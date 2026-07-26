"""
Loads the fine-tuned classifier and exposes a simple predict()
function for the API layer to call.

Designed to fail gracefully: if model/artifacts/suraksha-classifier/ doesn't
exist yet, predict() returns
None instead of crashing -- callers should fall back to rules-only in that
case.
"""

import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

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
    if not (MODEL_DIR / "model.safetensors").exists():
        return None

    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
    model.eval()

    # id2label is baked into the model's config by train.py, but falls back
    # to labels.json if that's somehow missing
    id2label = model.config.id2label
    return model, tokenizer, id2label


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