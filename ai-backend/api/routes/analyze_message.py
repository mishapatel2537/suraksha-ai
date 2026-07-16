"""
POST /analyze-message

Right now this runs rules-only (RULES_ONLY_MODE in .env). Once Step 5's
classifier is trained and exported, swap the TODO block below for a real
model call — the response shape doesn't need to change either way, which
is the whole point of having the contract locked first.
"""

from fastapi import APIRouter

from api.schemas.request_models import AnalyzeMessageRequest
from api.schemas.response_models import AnalyzeResponse, ScamCategory
from explanation.claude_explainer import generate_explanation
from rules.scam_patterns import check_rules, rules_risk_percent

router = APIRouter()


@router.post("/analyze-message", response_model=AnalyzeResponse)
def analyze_message(request: AnalyzeMessageRequest) -> AnalyzeResponse:
    category_str, matches = check_rules(request.text, request.language.value)

    # TODO (Step 5+): once model/artifacts/suraksha-classifier exists, run
    # the ML classifier here and combine with the rules result instead of
    # relying on rules alone. Suggested approach: if rules fire with high
    # confidence, trust rules (they're precise even if not exhaustive);
    # otherwise defer to the model. RULES_ONLY_MODE in .env can gate this
    # once both paths exist.
    category = ScamCategory(category_str) if category_str else ScamCategory.NOT_SCAM
    risk_percent = rules_risk_percent(matches)

    explanation = generate_explanation(
        category=category, risk_percent=risk_percent, language=request.language
    )

    return AnalyzeResponse(
        category=category,
        risk_percent=risk_percent,
        explanation=explanation,
        language=request.language,
    )
