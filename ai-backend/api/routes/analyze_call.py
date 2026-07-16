"""
POST /analyze-call — Step 9 (Important, drop 2nd if time is short).

Transcribes uploaded call audio with Whisper, then reuses the exact same
rules/model/explanation pipeline as /analyze-message. Not implemented yet
— stubbed so the route exists and Person B can build against it, but it
currently returns 501 until speech/transcribe.py is written.
"""

from fastapi import APIRouter, HTTPException, UploadFile

from api.schemas.response_models import AnalyzeResponse

router = APIRouter()


@router.post("/analyze-call", response_model=AnalyzeResponse)
async def analyze_call(audio: UploadFile):
    # TODO (Step 9): transcribe via speech/transcribe.py, then call the
    # same logic as analyze_message.analyze_message() on the transcript.
    raise HTTPException(status_code=501, detail="Call analysis not implemented yet — coming in Step 9.")
