"""
Step 9: Whisper integration for call-recording transcription.

Uses local open-source Whisper (not the paid OpenAI API) -- free, and your
RTX 4060 handles it fine. Requires ffmpeg to be installed and on PATH
(Whisper shells out to it for audio decoding) -- if you don't have it:
    Windows: winget install ffmpeg   (or download from ffmpeg.org and add to PATH)

Model size: "small" by default -- good multilingual accuracy/speed balance.
"tiny"/"base" are faster but noticeably worse on Hindi/Gujarati; "medium"/
"large" are better but slower and use more VRAM. Change WHISPER_MODEL_SIZE
below if you want to trade off differently.
"""

from functools import lru_cache

# Whisper's own language codes -> the language strings the rest of the
# app uses (matches Language enum in api/schemas/request_models.py)
WHISPER_LANG_TO_APP_LANG = {
    "en": "english",
    "hi": "hindi",
    "gu": "gujarati",
}

WHISPER_MODEL_SIZE = "small"


@lru_cache(maxsize=1)
def _load_whisper_model():
    """
    Loads the Whisper model once and caches it -- loading from disk on
    every call would make /analyze-call unusably slow. First call
    downloads the model (~500MB for "small"), subsequent calls reuse it.
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

    whisper_lang = result.get("language", "")
    app_lang = WHISPER_LANG_TO_APP_LANG.get(whisper_lang)

    return {
        "text": result.get("text", "").strip(),
        "whisper_language_code": whisper_lang,
        "language": app_lang,
    }