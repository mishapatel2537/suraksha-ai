"""
Family Guardian alert logic (Section 4 of the backend roadmap).

Two responsibilities, both backend-only:
  1. Decide WHETHER an alert should fire (compute_trigger_alert)
  2. Draft WHAT it should say (generate_alert_message)

The backend never stores guardian contacts and never sends SMS -- that's
entirely Person B's app (SmsManager, local storage). This module just
hands her a ready-to-send string and a boolean.

alert_message uses FIXED TEMPLATES, not a live Claude API call:
  - Reliability: an alert to a worried family member during an active
    scam shouldn't depend on an external API being reachable at that
    moment.
  - Cost: zero extra API spend per alert.
  - Length safety: Unicode SMS (Hindi/Gujarati) splits into ~70-char
    segments vs ~160 for English GSM-7 -- an AI-generated message could
    unpredictably blow past that and split into multiple texts. Fixed
    templates guarantee we stay well under the limit every time.
"""

from api.schemas.request_models import Language

ALERT_THRESHOLD = 70  # risk_percent >= this triggers an alert; tune after real eval data


def compute_trigger_alert(risk_percent: int) -> bool:
    return risk_percent >= ALERT_THRESHOLD


# {category} gets the human-readable category name substituted in.
# Kept deliberately short -- well under SMS single-segment limits in all
# 3 languages even after substitution.
_ALERT_TEMPLATES = {
    Language.ENGLISH: "Suraksha alert: a high-risk {category} was flagged on this phone. Please check in.",
    Language.HINDI: "सुरक्षा अलर्ट: इस फोन पर एक हाई-रिस्क {category} मिला है। कृपया संपर्क करें।",
    Language.GUJARATI: "સુરક્ષા એલર્ટ: આ ફોન પર એક હાઈ-રિસ્ક {category} મળ્યો છે. કૃપા કરી સંપર્ક કરો.",
}

# Human-readable category names for the template, per language -- reading
# "kyc_scam" in the middle of an SMS looks unpolished; a family member
# should see something they can actually parse at a glance.
_CATEGORY_NAMES = {
    "kyc_scam": {"english": "KYC scam", "hindi": "केवाईसी घोटाला", "gujarati": "કેવાયસી કૌભાંડ"},
    "loan_scam": {"english": "loan scam", "hindi": "लोन घोटाला", "gujarati": "લોન કૌભાંડ"},
    "lottery_scam": {"english": "lottery scam", "hindi": "लॉटरी घोटाला", "gujarati": "લોટરી કૌભાંડ"},
    "upi_scam": {"english": "UPI scam", "hindi": "यूपीआई घोटाला", "gujarati": "યુપીઆઈ કૌભાંડ"},
    "phishing": {"english": "phishing message", "hindi": "फिशिंग संदेश", "gujarati": "ફિશિંગ સંદેશ"},
    "impersonation_digital_arrest": {
        "english": "fake police call", "hindi": "फर्जी पुलिस कॉल", "gujarati": "નકલી પોલીસ કૉલ",
    },
    "impersonation_blackmail": {
        "english": "blackmail scam", "hindi": "ब्लैकमेल धमकी", "gujarati": "બ્લેકમેલ ધમકી",
    },
}


def generate_alert_message(category: str, language: Language) -> str:
    """
    category: the raw category string (e.g. "kyc_scam"), not the not_scam
    case -- callers should only invoke this when trigger_alert is True,
    which by construction means a real scam category.
    """
    category_name = _CATEGORY_NAMES.get(category, {}).get(language.value, category)
    template = _ALERT_TEMPLATES[language]
    return template.format(category=category_name)