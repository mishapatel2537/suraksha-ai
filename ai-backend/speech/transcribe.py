"""
Whisper integration for call-recording transcription.

Uses local open-source Whisper (not the paid OpenAI API) -- free, and your
RTX 4060 handles it fine. Requires ffmpeg to be installed and on PATH
(Whisper shells out to it for audio decoding) -- if you don't have it:
    Windows: winget install ffmpeg   (or download from ffmpeg.org and add to PATH)

Model size: "tiny" -- smallest available, chosen to minimize memory
footprint on Render's 512MB free tier. "small"/"medium"/"large" would be
more accurate on Hindi/Gujarati but are not viable at this memory budget
alongside the classifier.
"""

import gc
import logging

logger = logging.getLogger("suraksha.speech")

# Whisper's own language codes -> the language strings the rest of the
# app uses (matches Language enum in api/schemas/request_models.py)
WHISPER_LANG_TO_APP_LANG = {
    "en": "english",
    "hi": "hindi",
    "gu": "gujarati",
}

WHISPER_MODEL_SIZE = "tiny"


def _load_whisper_model():
    """
    Loads the Whisper model fresh -- deliberately NOT cached across calls
    (no @lru_cache here). Caching kept Whisper resident in memory
    indefinitely once warm, which meant it was sitting in RAM at the same
    time as the ~516MB classifier -- on Render's 512MB free tier, that
    combination is what caused the OOM 502s on /analyze-call. Loading
    fresh per call and releasing immediately after (see transcribe_audio
    below) keeps peak memory bounded to whichever one model is active.

    This does cost a reload on every call, but the *weights themselves*
    are still cached on disk by the whisper library after the first
    download (~/.cache/whisper by default) for the life of the running
    instance -- only the network download is a one-time cost, not the
    in-memory load.
    """
    import whisper
    return whisper.load_model(WHISPER_MODEL_SIZE)


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribes an audio file and detects its language.

    Returns:
        {
            "text": str,                      # transcribed text (empty string if no speech detected)
            "whisper_language_code": str,      # Whisper's raw detected code, e.g. "hi"
            "language": str | None,            # mapped to "english"/"hindi"/"gujarati", or None if
                                                # Whisper detected a language outside those 3
        }

    Note: Whisper sometimes confuses Hindi and Gujarati on short or noisy
    clips, since they're related languages -- if you see misclassified
    calls in testing, that's a known Whisper limitation, not a bug here.
    Worth a native speaker spot-checking a few real recordings before
    trusting this on stage.
    """
    model = _load_whisper_model()
    result = model.transcribe(audio_path)

    # Release Whisper's memory before returning, so the classifier (loaded
    # separately by model/predict.py, right after this function returns)
    # never has to share the 512MB ceiling with a resident Whisper model.
    # del drops the reference; gc.collect() forces reclamation now instead
    # of whenever the collector next runs on its own schedule -- on a
    # tightly memory-constrained instance, that timing gap is exactly what
    # was causing the OOM.
    del model
    gc.collect()

    whisper_lang = result.get("language", "")
    app_lang = WHISPER_LANG_TO_APP_LANG.get(whisper_lang)

    logger.debug(f"Whisper transcript: {result['text']}")

    return {
        "text": result.get("text", "").strip(),
        "whisper_language_code": whisper_lang,
        "language": app_lang,
    }