"""
Loads the fine-tuned classifier and exposes a simple predict()
function for the API layer to call.

Designed to fail gracefully: if model/artifacts/suraksha-classifier/ doesn't
exist yet (e.g. a teammate hasn't run training locally), predict() returns
None instead of crashing -- callers should fall back to rules-only in that
case. This matters because Person B (or anyone pulling the repo fresh)
shouldn't have the API break just because they haven't run model/train.py.
"""

import logging
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger("suraksha.model")

MODEL_DIR = Path(__file__).parent / "artifacts" / "suraksha-classifier"

# Manual cache + lock instead of @lru_cache(maxsize=1). lru_cache's internal
# lock only protects the cache dict itself -- it does NOT serialize calls to
# the wrapped function. Two concurrent requests can both see a cache miss
# and both start loading the model at once, which is exactly what happened
# right after a cold start: two simultaneous `transformers` imports collided
# and one raised a spurious ImportError, silently falling back to rules-only
# for that request. This lock makes loading itself mutually exclusive.
_model_cache = None
_model_cache_set = False  # distinguishes "not loaded yet" from "loaded, and the result was None"
_model_load_lock = threading.Lock()


def _load_model():
    """
    Loads model + tokenizer once and caches them. Double-checked locking:
    the first check (no lock) makes the common case -- already warm --
    cheap. The second check (inside the lock) ensures that if two threads
    both passed the first check, only one of them actually performs the
    load; the other sees the now-populated cache and returns immediately.

    Returns (model, tokenizer, id2label) or None if artifacts aren't present
    or loading failed. None is cached too, so a missing-artifacts state
    doesn't retry the (expensive) load on every single request.
    """
    global _model_cache, _model_cache_set

    if _model_cache_set:
        return _model_cache

    with _model_load_lock:
        if _model_cache_set:
            return _model_cache

        model_file = MODEL_DIR / "model.safetensors"
        if not model_file.exists():
            logger.warning(f"Model artifacts NOT FOUND at {model_file} -- falling back to rules-only.")
            _model_cache = None
            _model_cache_set = True
            return None

        file_size_mb = model_file.stat().st_size / 1024 / 1024
        logger.info(f"Found model.safetensors ({file_size_mb:.1f}MB) at {model_file}, loading...")

        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
            tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
            model.eval()

            # id2label is baked into the model's config by train.py, but falls back
            # to labels.json if that's somehow missing
            id2label = model.config.id2label
            logger.info("Model loaded successfully.")
            _model_cache = (model, tokenizer, id2label)
            _model_cache_set = True
            return _model_cache
        except Exception:
            # Loading can fail for real reasons (OOM, corrupted file, version
            # mismatch) -- log it clearly rather than letting it crash the
            # request, and fall back to rules-only same as a missing file.
            logger.exception("Model file exists but failed to load -- falling back to rules-only.")
            _model_cache = None
            _model_cache_set = True
            return None


def predict(text: str, max_length: int = 128):
    """
    Returns (category: str, confidence: float 0-1) or None if the model
    isn't available (artifacts missing). Confidence is the softmax
    probability of the top predicted class -- use it as the basis for
    risk_percent, not as a guarantee of correctness.
    """
    loaded = _load_model()
    if loaded is None:
        return None
    model, tokenizer, id2label = loaded

    import torch

    inputs = tokenizer(text, truncation=True, padding="max_length", max_length=max_length, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)[0]
        top_id = int(torch.argmax(probs))
        confidence = float(probs[top_id])

    # HF's id2label dict sometimes has int keys, sometimes str keys depending
    # on how it was serialized -- handle both rather than guessing
    category = id2label.get(top_id, id2label.get(str(top_id)))
    return category, confidence