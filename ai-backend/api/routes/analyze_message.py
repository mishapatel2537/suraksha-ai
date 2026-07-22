"""
POST /analyze-message

The rules -> model -> fallback ensemble decision lives in model/ensemble.py
(shared with model/evaluate.py so both use the exact same logic) -- this
route just calls it and wraps the result into the API response shape.
"""

from fastapi import APIRouter

from api.schemas.request_models import AnalyzeMessageRequest
from api.schemas.response_models import AnalyzeResponse, ScamCategory
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

    return AnalyzeResponse(
        category=category,
        risk_percent=risk_percent,
        explanation=explanation,
        language=request.language,
    )