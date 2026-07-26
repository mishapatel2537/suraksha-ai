"""
Turn a classification result into a plain-language explanation
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
    ScamCategory.IMPERSONATION_DIGITAL_ARREST: {
        Language.ENGLISH: "This looks like a fake police/CBI call. Real police never arrest you over a phone or video call, or ask for money to close a case — hang up and verify at your nearest police station.",
        Language.HINDI: "यह एक फर्जी पुलिस/सीबीआई कॉल लगता है। असली पुलिस कभी फोन या वीडियो कॉल पर गिरफ्तार नहीं करती, न ही केस बंद करने के लिए पैसे मांगती है — कॉल काटें और नजदीकी थाने में पुष्टि करें।",
        Language.GUJARATI: "આ નકલી પોલીસ/સીબીઆઈ કૉલ લાગે છે. સાચી પોલીસ ક્યારેય ફોન કે વિડિયો કૉલ પર ધરપકડ કરતી નથી, કે કેસ બંધ કરવા પૈસા માંગતી નથી — કૉલ કાપો અને નજીકના પોલીસ સ્ટેશને ચકાસો.",
    },
    ScamCategory.IMPERSONATION_BLACKMAIL: {
        Language.ENGLISH: "This looks like a fake blackmail threat. Do not send money or share more information — block the number and report it to cybercrime.gov.in.",
        Language.HINDI: "यह एक फर्जी ब्लैकमेल धमकी लगती है। पैसे न भेजें और कोई जानकारी साझा न करें — नंबर ब्लॉक करें और cybercrime.gov.in पर रिपोर्ट करें।",
        Language.GUJARATI: "આ નકલી બ્લેકમેલ ધમકી લાગે છે. પૈસા ન મોકલો અને વધુ માહિતી શેર ન કરો — નંબર બ્લોક કરો અને cybercrime.gov.in પર જાણ કરો.",
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
    script_instruction = {
        Language.HINDI: "Write in Hindi using Devanagari script (देवनागरी) -- NOT romanized Hinglish in Latin letters.",
        Language.GUJARATI: "Write in Gujarati using Gujarati script (ગુજરાતી) -- NOT romanized text in Latin letters.",
        Language.ENGLISH: "Write in English.",
    }[language]

    prompt = (
        f"A message-scanning tool classified a message as category='{category.value}' "
        f"with risk_percent={risk_percent}. Write a single short (1-2 sentence) plain-language "
        f"explanation for a first-time digital banking user in rural India, in {language.value}. "
        f"{script_instruction} "
        "Be direct and reassuring, avoid jargon, and if it's a scam say clearly what NOT to do "
        "(e.g. don't click the link, don't share OTP). "
        "IMPORTANT: reply with plain text only -- no markdown, no headers, no bold/asterisks, "
        "no bullet points, no title. Just 1-2 plain sentences, nothing else, since this goes "
        "directly into a mobile app's UI where markdown symbols would show up as literal characters."
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",  # fast/cheap — fine for a 1-2 sentence explanation
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()