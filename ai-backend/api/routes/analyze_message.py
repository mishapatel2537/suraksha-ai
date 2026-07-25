"""
POST /analyze-message

The rules -> model -> fallback ensemble decision lives in model/ensemble.py
(shared with model/evaluate.py so both use the exact same logic) -- this
route calls it, decides whether a Family Guardian alert should fire
(explanation/alert_generator.py), logs the classification for demo/debug
purposes, and wraps everything into the API response shape.
"""

from fastapi import APIRouter

from api.db.logging import log_flagged_message
from api.schemas.request_models import AnalyzeMessageRequest
from api.schemas.response_models import AnalyzeResponse, ScamCategory
from explanation.alert_generator import compute_trigger_alert, generate_alert_message
from explanation.claude_explainer import generate_explanation
from model.ensemble import classify

router = APIRouter()


@router.post("/analyze-message", response_model=AnalyzeResponse)
def analyze_message(request: AnalyzeMessageRequest) -> AnalyzeResponse:
    category_str, risk_percent = classify(request.text, request.language.value)
    category = ScamCategory(category_str)

    explanation = generate_explanation(
        category=category, risk_percent=risk_percent, language=request.language
    )

    trigger_alert = compute_trigger_alert(risk_percent)
    alert_message = generate_alert_message(category_str, request.language) if trigger_alert else ""

    log_flagged_message(
        text=request.text, category=category_str, risk_percent=risk_percent,
        language=request.language.value,
    )

    return AnalyzeResponse(
        category=category,
        risk_percent=risk_percent,
        explanation=explanation,
        language=request.language,
        trigger_alert=trigger_alert,
        alert_message=alert_message,
    )