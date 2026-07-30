"""
Loads the fine-tuned classifier (Step 5) and exposes a simple predict()
function for the API layer to call.

Designed to fail gracefully: if model/artifacts/suraksha-classifier/ doesn't
exist yet (e.g. a teammate hasn't run training locally), predict() returns
None instead of crashing -- callers should fall back to rules-only in that
case. This matters because Person B (or anyone pulling the repo fresh)
shouldn't have the API break just because they haven't run model/train.py.
"""

import logging
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger("suraksha.model")

MODEL_DIR = Path(__file__).parent / "artifacts" / "suraksha-classifier"


@lru_cache(maxsize=1)
def _load_model():
    """
    Loads model + tokenizer once and caches them (lru_cache with maxsize=1
    means this only actually runs on the first call, subsequent calls
    reuse the cached model -- loading a transformer from disk on every
    request would make /analyze-message unusably slow).

    Returns (model, tokenizer, id2label) or None if artifacts aren't present.
    """
    model_file = MODEL_DIR / "model.safetensors"
    if not model_file.exists():
        logger.warning(f"Model artifacts NOT FOUND at {model_file} -- falling back to rules-only.")
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
        return model, tokenizer, id2label
    except Exception:
        # Loading can fail for real reasons (OOM, corrupted file, version
        # mismatch) -- log it clearly rather than letting it crash the
        # request, and fall back to rules-only same as a missing file.
        logger.exception("Model file exists but failed to load -- falling back to rules-only.")
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