"""
Request schemas for the Suraksha API.

Must stay in sync with the frontend's AnalyzeRequest.kt (Person B's branch).
Agree on any field changes with Person B before merging — her screens are
built directly against this shape.
"""

from enum import Enum

from pydantic import BaseModel, Field


class Language(str, Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    GUJARATI = "gujarati"


class AnalyzeMessageRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The message content to analyze")
    language: Language = Field(..., description="Language the message is written in")


class AnalyzeCallRequest(BaseModel):
    # Audio arrives as multipart/form-data in the actual endpoint (see
    # api/routes/analyze_call.py) rather than as JSON body fields — this
    # model documents the accompanying metadata sent alongside the file.
    language: Language = Field(..., description="Expected language of the call audio")


class GuardianAlertRequest(BaseModel):
    message_id: str = Field(..., description="ID of the flagged message/call that triggered this alert")
    category: str = Field(..., description="Scam category that triggered the alert")
    risk_percent: int = Field(..., ge=0, le=100)
    guardian_contact: str = Field(..., description="Phone number or email of the trusted family member")
