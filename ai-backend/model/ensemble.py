"""
The ensemble decision logic (rules -> model -> fallback), extracted out of
api/routes/analyze_message.py so both the live API and model/evaluate.py
call the exact same code path. Evaluating a re-implementation of the
ensemble logic instead of the real thing would risk the two silently
drifting apart -- this module is the single source of truth for it.

Policy: rules are precise but not exhaustive (Validation: ~99.6%
precision, ~30-80% recall depending on category). The model is more
exhaustive but occasionally wrong in different ways. So:

  1. If rules fire with >=2 keyword matches (high confidence per
     rules_risk_percent's own scale), trust rules directly.
  2. Otherwise, defer to the model if it's available.
  3. If the model isn't available, fall back to rules-only.
"""

from model.predict import predict as model_predict
from rules.scam_patterns import check_rules, rules_risk_percent

RULES_HIGH_CONFIDENCE_THRESHOLD = 2  # matches rules_risk_percent's own 90%-at-2-matches scale


def classify(text: str, language: str) -> tuple[str, int]:
    """
    Returns (category: str, risk_percent: int), using the same rules -> model
    -> fallback policy the live API uses.
    """
    rules_category_str, matches = check_rules(text, language)

    if matches >= RULES_HIGH_CONFIDENCE_THRESHOLD:
        category = rules_category_str if rules_category_str else "not_scam"
        risk_percent = rules_risk_percent(matches)
        return category, risk_percent

    model_result = model_predict(text)
    if model_result is not None:
        model_category_str, confidence = model_result
        return model_category_str, round(confidence * 100)

    if matches == 1:
        return rules_category_str, rules_risk_percent(matches)

    return "not_scam", rules_risk_percent(0)