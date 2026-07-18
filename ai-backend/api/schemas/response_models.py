"""
Response schemas for the Suraksha API.

THIS IS THE LOCKED CONTRACT (Step 2). Field names here must exactly match
what Person B expects in AnalyzeResponse.kt: category, risk_percent,
explanation, language. Do not rename/restructure these without telling her
first — her screens are built directly against this shape.
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
    # Exactly the 4 locked fields — category, risk_percent, explanation, language.
    # If probabilities turn out unreliable (plan's fallback note), bucket
    # risk_percent into ~10/50/90 bands rather than adding a new field —
    # changing the shape means Person B has to touch her Kotlin models.
    category: ScamCategory
    risk_percent: int = Field(..., ge=0, le=100, description="Model confidence as a percentage")
    explanation: str = Field(..., description="Plain-language explanation, in the requested language")
    language: Language = Field(..., description="Language the explanation was generated in")


class GuardianAlertResponse(BaseModel):
    sent: bool
    message: str
