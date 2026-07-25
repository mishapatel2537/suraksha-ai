"""
POST /analyze-call

Transcribes uploaded call audio with Whisper, then reuses the exact same
rules -> model -> fallback ensemble (model/ensemble.py), Family Guardian
alert logic, and logging that /analyze-message uses -- a scam is a scam
whether it arrived as text or a transcribed call, so none of that logic
should differ by input type.
"""

import os
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile

from api.db.logging import log_flagged_message
from api.schemas.response_models import AnalyzeResponse, ScamCategory, Language
from explanation.alert_generator import compute_trigger_alert, generate_alert_message
from explanation.claude_explainer import generate_explanation
from model.ensemble import classify
from speech.transcribe import transcribe_audio

router = APIRouter()

# Language to assume if Whisper detects something outside english/hindi/gujarati,
# or if it fails to detect a language at all. This is a rough stopgap --
# proper handling of unsupported languages is Step 14 (error handling / edge cases).
FALLBACK_LANGUAGE = "english"


@router.post("/analyze-call", response_model=AnalyzeResponse)
async def analyze_call(audio: UploadFile):
    suffix = os.path.splitext(audio.filename or "")[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        result = transcribe_audio(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
    finally:
        os.unlink(tmp_path)  # clean up the temp file regardless of outcome

    transcript = result["text"]
    language = result["language"] or FALLBACK_LANGUAGE

    if not transcript:
        # No speech detected -- silence, non-speech audio, or a language
        # Whisper couldn't transcribe at all. Better to say so plainly
        # than force a category guess on empty text.
        raise HTTPException(
            status_code=400,
            detail="No speech could be transcribed from this audio. Try a clearer recording.",
        )

    category_str, risk_percent = classify(transcript, language)
    category = ScamCategory(category_str)
    language_enum = Language(language)

    explanation = generate_explanation(
        category=category, risk_percent=risk_percent, language=language_enum
    )

    trigger_alert = compute_trigger_alert(risk_percent)
    alert_message = generate_alert_message(category_str, language_enum) if trigger_alert else ""

    log_flagged_message(
        text=transcript, category=category_str, risk_percent=risk_percent, language=language,
    )

    return AnalyzeResponse(
        category=category,
        risk_percent=risk_percent,
        explanation=explanation,
        language=language_enum,
        trigger_alert=trigger_alert,
        alert_message=alert_message,
    )