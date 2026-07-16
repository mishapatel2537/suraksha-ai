"""
POST /guardian-alert — Important, drop 1st if time is short.

Per the plan's fallback, this can stay mocked (no real SMS/email send) and
the frontend can simulate the alert UI without a real trigger. Wired up
here as a mock so Person B has a real endpoint + response shape to build
against immediately.
"""

from fastapi import APIRouter

from api.schemas.request_models import GuardianAlertRequest
from api.schemas.response_models import GuardianAlertResponse

router = APIRouter()


@router.post("/guardian-alert", response_model=GuardianAlertResponse)
def guardian_alert(request: GuardianAlertRequest) -> GuardianAlertResponse:
    # TODO (optional, if time allows): wire up a real SMS/email API
    # (e.g. Twilio free tier, or a transactional email API) here instead
    # of the mock response below.
    return GuardianAlertResponse(
        sent=True,
        message=f"[MOCK] Alert would be sent to {request.guardian_contact} "
        f"about a {request.category} risk ({request.risk_percent}% confidence).",
    )
