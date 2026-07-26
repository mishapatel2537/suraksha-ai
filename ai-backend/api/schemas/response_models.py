"""
Response schemas for the Suraksha API.

THIS IS THE LOCKED CONTRACT. Field names here must exactly match in
AnalyzeResponse.kt: category, risk_percent, explanation, language,
trigger_alert, alert_message.
"""

from enum import Enum

from pydantic import BaseModel, Field

from api.schemas.request_models import Language


class ScamCategory(str, Enum):
    KYC_SCAM = "kyc_scam"
    LOAN_SCAM = "loan_scam"
    LOTTERY_SCAM = "lottery_scam"
    UPI_SCAM = "upi_scam"
    PHISHING = "phishing"
    IMPERSONATION_DIGITAL_ARREST = "impersonation_digital_arrest"  # added: fake police/CBI/cyber-cell calls
    IMPERSONATION_BLACKMAIL = "impersonation_blackmail"  # added: fake obscene-content/morphed-photo threats
    NOT_SCAM = "not_scam"
    UNKNOWN = "unknown"  # low-confidence / couldn't classify


class AnalyzeResponse(BaseModel):
    # Locked contract fields: category, risk_percent, explanation, language,
    # trigger_alert, alert_message. Last two added for Family Guardian --
    # tell Person B before changing any of these further.
    category: ScamCategory
    risk_percent: int = Field(..., ge=0, le=100, description="Model confidence as a percentage")
    explanation: str = Field(..., description="Plain-language explanation, in the requested language")
    language: Language = Field(..., description="Language the explanation was generated in")
    trigger_alert: bool = Field(..., description="True if risk_percent crosses the alert threshold")
    alert_message: str = Field(
        default="",
        description="Pre-written SMS-ready alert text, in the requested language. "
        "Empty string when trigger_alert is False.",
    )


class GuardianAlertResponse(BaseModel):
    sent: bool
    message: str