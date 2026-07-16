"""
Step 8: turn a classification result into a plain-language explanation
via the Claude API, in the user's chosen language.

Kept separate from api/ so it's testable without spinning up FastAPI, and
swappable for the fixed-template fallback (see below) if the API
integration stalls under time pressure.
"""

import os

from anthropic import Anthropic

from api.schemas.request_models import Language
from api.schemas.response_models import ScamCategory

_client: Anthropic | None = None

# Fallback: fixed template per category, used if ANTHROPIC_API_KEY isn't
# set yet or the API call fails — keeps the endpoint working during dev.
_FALLBACK_TEMPLATES = {
    ScamCategory.KYC_SCAM: {
        Language.ENGLISH: "This looks like a fake KYC update request. Banks never ask you to update KYC through a text link — do not click it.",
        Language.HINDI: "यह एक फर्जी केवाईसी अपडेट अनुरोध लगता है। बैंक कभी भी टेक्स्ट लिंक से केवाईसी अपडेट करने को नहीं कहते।",
        Language.GUJARATI: "આ નકલી કેવાયસી અપડેટ વિનંતી લાગે છે. બેંક ક્યારેય ટેક્સ્ટ લિંક દ્વારા કેવાયસી અપડેટ કરવાનું કહેતી નથી.",
    },
    ScamCategory.NOT_SCAM: {
        Language.ENGLISH: "This message doesn't match any known scam pattern.",
        Language.HINDI: "यह संदेश किसी ज्ञात धोखाधड़ी पैटर्न से मेल नहीं खाता।",
        Language.GUJARATI: "આ સંદેશ કોઈ જાણીતા છેતરપિંડી પેટર્ન સાથે મેળ ખાતો નથી.",
    },
}
_GENERIC_FALLBACK = {
    Language.ENGLISH: "This message shows signs of a scam. Be cautious and don't share personal or payment details.",
    Language.HINDI: "इस संदेश में धोखाधड़ी के संकेत हैं। सावधान रहें और व्यक्तिगत या भुगतान विवरण साझा न करें।",
    Language.GUJARATI: "આ સંદેશમાં છેતરપિંડીના સંકેતો છે. સાવચેત રહો અને વ્યક્તિગત અથવા ચુકવણી વિગતો શેર કરશો નહીં.",
}


def _get_client() -> Anthropic | None:
    global _client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    if _client is None:
        _client = Anthropic(api_key=api_key)
    return _client


def generate_explanation(category: ScamCategory, risk_percent: int, language: Language) -> str:
    client = _get_client()
    if client is not None:
        try:
            return _call_claude(client, category, risk_percent, language)
        except Exception:
            pass  # fall through to template fallback below

    return _FALLBACK_TEMPLATES.get(category, {}).get(language) or _GENERIC_FALLBACK[language]


def _call_claude(client: Anthropic, category: ScamCategory, risk_percent: int, language: Language) -> str:
    prompt = (
        f"A message-scanning tool classified a message as category='{category.value}' "
        f"with risk_percent={risk_percent}. Write a single short (1-2 sentence) plain-language "
        f"explanation for a first-time digital banking user in rural India, in {language.value}. "
        "Be direct and reassuring, avoid jargon, and if it's a scam say clearly what NOT to do "
        "(e.g. don't click the link, don't share OTP)."
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # fast/cheap — fine for a 1-2 sentence explanation
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
