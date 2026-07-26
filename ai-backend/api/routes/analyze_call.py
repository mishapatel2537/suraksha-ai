"""
POST /analyze-call

Transcribes uploaded call audio with Whisper, then reuses the exact same
rules -> model -> fallback ensemble (model/ensemble.py), Family Guardian
alert logic, and logging that /analyze-message uses -- a scam is a scam
whether it arrived as text or a transcribed call, so none of that logic
should differ by input type.

Edge cases handled here:
  - Oversized audio uploads rejected before transcription (avoids hanging
    the demo on a huge/long file -- Whisper on CPU is slow)
  - Unrecognized file extensions rejected with a clear message instead of
    a confusing ffmpeg failure deep in the stack
  - Transcription failures return a clean message, not a raw exception
    string (avoids leaking internal details to the client)
  - Unsupported-language fallback is now logged server-side instead of
    silently swapping to English
"""

import logging
import os
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile

from api.db.logging import log_flagged_message
from api.schemas.response_models import AnalyzeResponse, ScamCategory, Language
from explanation.alert_generator import compute_trigger_alert, generate_alert_message
from explanation.claude_explainer import generate_explanation
from model.ensemble import classify
from speech.transcribe import transcribe_audio

logger = logging.getLogger("suraksha.analyze_call")

router = APIRouter()

# Language to assume if Whisper detects something outside english/hindi/gujarati,
# or if it fails to detect a language at all -- still better to return a
# usable response than fail the request entirely, but this is a rough
# stopgap (see the logged warning below), not a real fix for other languages.
FALLBACK_LANGUAGE = "english"

MAX_AUDIO_SIZE_MB = 15  # generous for a scam-call clip; caps worst-case Whisper-on-CPU processing time
MAX_AUDIO_SIZE_BYTES = MAX_AUDIO_SIZE_MB * 1024 * 1024

# Extensions Whisper/ffmpeg can actually decode, that a phone recorder or
# WhatsApp voice note would realistically produce.
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".mp4", ".ogg", ".opus", ".webm", ".flac", ".aac"}


@router.post("/analyze-call", response_model=AnalyzeResponse)
async def analyze_call(audio: UploadFile):
    suffix = os.path.splitext(audio.filename or "")[1].lower()
    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix or 'unknown'}'. "
            f"Accepted formats: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}",
        )

    content = await audio.read()
    if len(content) > MAX_AUDIO_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large ({len(content) / 1024 / 1024:.1f}MB). "
            f"Max size is {MAX_AUDIO_SIZE_MB}MB.",
        )
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = transcribe_audio(tmp_path)
    except Exception as e:
        # Log the real exception server-side for debugging, but don't hand
        # the client raw internals (file paths, library stack traces).
        logger.exception(f"Transcription failed for uploaded file {audio.filename}")
        raise HTTPException(
            status_code=500,
            detail="Could not process this audio file. Try a different format or a clearer recording.",
        )
    finally:
        os.unlink(tmp_path)  # clean up the temp file regardless of outcome

    transcript = result["text"]
    detected_language = result["language"]

    if not transcript:
        # No speech detected -- silence, non-speech audio, or a language
        # Whisper couldn't transcribe at all. Better to say so plainly
        # than force a category guess on empty text.
        raise HTTPException(
            status_code=400,
            detail="No speech could be transcribed from this audio. Try a clearer recording.",
        )

    if detected_language is None:
        logger.warning(
            f"Whisper detected an unsupported language (code: {result.get('whisper_language_code')}) "
            f"for file {audio.filename}; falling back to {FALLBACK_LANGUAGE}. "
            f"Classification quality on this response may be degraded."
        )
        language = FALLBACK_LANGUAGE
    else:
        language = detected_language

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