"""
Whisper integration for call-recording transcription.

Uses local open-source Whisper (not the paid OpenAI API) -- free, and your
RTX 4060 handles it fine. Requires ffmpeg to be installed and on PATH
(Whisper shells out to it for audio decoding) -- if you don't have it:
    Windows: winget install ffmpeg   (or download from ffmpeg.org and add to PATH)

Model size: "tiny" -- smallest available, chosen to minimize memory
footprint on Render's 512MB free tier.

Whisper runs in a SEPARATE PROCESS (not just a thread), started fresh for
each call and torn down immediately after. A del + gc.collect() approach
was tried first but wasn't reliable: Python's garbage collector frees the
*objects*, but the underlying memory allocator (PyTorch's, and glibc's
malloc beneath it) does not reliably return that memory to the OS -- it's
often kept reserved for reuse within the same process. Render's memory
limit is measured at the OS level (RSS), so "the Python object is gone"
doesn't guarantee "the OS sees the memory as free."

A subprocess sidesteps this entirely: when the subprocess exits, the OS
reclaims 100% of its memory, no matter what the allocator inside it was
doing. This is slower (a fresh Python interpreter + fresh imports of
torch/whisper on every single call, instead of reusing a warm process)
but on a 512MB instance, correctness has to come before speed here.
"""

import logging
import multiprocessing as mp

logger = logging.getLogger("suraksha.speech")

# Whisper's own language codes -> the language strings the rest of the
# app uses (matches Language enum in api/schemas/request_models.py)
WHISPER_LANG_TO_APP_LANG = {
    "en": "english",
    "hi": "hindi",
    "gu": "gujarati",
}

WHISPER_MODEL_SIZE = "tiny"

# Generous but bounded -- Whisper on a slow free-tier CPU shouldn't take
# this long for a call-length clip, but a hang (bad audio, stuck ffmpeg)
# shouldn't be able to block the request forever.
TRANSCRIBE_TIMEOUT_SECONDS = 120


def _whisper_worker(audio_path: str, result_queue: mp.Queue) -> None:
    """
    Runs entirely inside the child process. Imports whisper, loads the
    model, transcribes, and puts the raw result on the queue -- then the
    process exits (multiprocessing.Process handles that once this function
    returns), which is what actually releases the memory.
    """
    try:
        import whisper
        model = whisper.load_model(WHISPER_MODEL_SIZE)
        result = model.transcribe(audio_path)
        result_queue.put({
            "ok": True,
            "text": result.get("text", "").strip(),
            "language": result.get("language", ""),
        })
    except Exception as e:
        # Errors inside the child process don't propagate to the parent
        # automatically -- send them back explicitly so the caller can
        # raise a clean HTTPException instead of hanging or dying silently.
        logger.exception("Whisper subprocess failed")
        result_queue.put({"ok": False, "error": str(e)})


def transcribe_audio(audio_path: str) -> dict:
    """
    Transcribes an audio file and detects its language, running Whisper in
    an isolated subprocess so its memory is fully released afterward.

    Returns:
        {
            "text": str,                      # transcribed text (empty string if no speech detected)
            "whisper_language_code": str,      # Whisper's raw detected code, e.g. "hi"
            "language": str | None,            # mapped to "english"/"hindi"/"gujarati", or None if
                                                # Whisper detected a language outside those 3
        }

    Raises:
        RuntimeError if the subprocess times out or crashes.

    Note: Whisper sometimes confuses Hindi and Gujarati on short or noisy
    clips, since they're related languages -- if you see misclassified
    calls in testing, that's a known Whisper limitation, not a bug here.
    """
    # "spawn" (not "fork") starts a genuinely fresh Python interpreter with
    # nothing inherited from the parent -- this matters here specifically
    # because fork on Linux can share memory pages with the parent via
    # copy-on-write, which would undercut the whole point of isolating
    # Whisper's memory. spawn is slower to start but is the one that
    # actually guarantees isolation.
    ctx = mp.get_context("spawn")
    result_queue = ctx.Queue()
    process = ctx.Process(target=_whisper_worker, args=(audio_path, result_queue))
    process.start()
    process.join(timeout=TRANSCRIBE_TIMEOUT_SECONDS)

    if process.is_alive():
        # Timed out -- kill it rather than leaving an orphaned process
        # holding memory indefinitely.
        process.terminate()
        process.join()
        raise RuntimeError(f"Transcription timed out after {TRANSCRIBE_TIMEOUT_SECONDS}s")

    if result_queue.empty():
        # Process exited but never put anything on the queue -- most
        # likely it was OOM-killed by the OS mid-transcription, which
        # doesn't raise a catchable Python exception, it just dies.
        raise RuntimeError("Transcription subprocess exited unexpectedly (possible out-of-memory)")

    raw = result_queue.get()
    if not raw["ok"]:
        raise RuntimeError(f"Transcription failed: {raw['error']}")

    whisper_lang = raw["language"]
    app_lang = WHISPER_LANG_TO_APP_LANG.get(whisper_lang)

    logger.debug(f"Whisper transcript: {raw['text']}")

    return {
        "text": raw["text"],
        "whisper_language_code": whisper_lang,
        "language": app_lang,
    }