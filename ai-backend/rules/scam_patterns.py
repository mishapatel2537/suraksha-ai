"""
Rules-based fallback layer.

This is a permanent safety net under the ML model.
Detection is deliberately simple: case-insensitive substring match against
per-category phrase lists in pattern_lists/*.json.
"""

import json
from pathlib import Path

PATTERN_DIR = Path(__file__).parent / "pattern_lists"


def _load_pattern_files() -> dict[str, dict]:
    """Load every *.json file in pattern_lists/ keyed by category name."""
    patterns = {}
    for file in PATTERN_DIR.glob("*.json"):
        with open(file, encoding="utf-8") as f:
            data = json.load(f)
            patterns[data["category"]] = data["patterns"]
    return patterns


_PATTERNS = _load_pattern_files()


def check_rules(text: str, language: str) -> tuple[str | None, int]:
    """
    Check text against known scam patterns for the given language.

    Returns (category, matches_found) — category is None if nothing matched.
    matches_found lets the caller turn a raw hit count into a risk_percent
    (e.g. 1 match -> 70%, 2+ matches -> 90%) until the real model exists.
    """
    text_lower = text.lower()
    best_category = None
    best_matches = 0

    for category, lang_patterns in _PATTERNS.items():
        phrases = lang_patterns.get(language, [])
        matches = sum(1 for phrase in phrases if phrase.lower() in text_lower)
        if matches > best_matches:
            best_matches = matches
            best_category = category

    return best_category, best_matches


def check_rules_any_language(text: str, declared_language: str) -> tuple[str | None, int]:
    """
    For call transcripts specifically: Whisper's declared spoken-language
    detection and the actual language of its transcribed text can diverge
    -- especially with the smaller "tiny" model, which sometimes detects
    Hindi/Gujarati audio correctly but transcribes it into rough English
    words anyway. check_rules() alone would then check that English-ish
    text against Hindi/Gujarati pattern lists and find nothing.

    This checks the declared language first (the common, correct case),
    then falls back to checking the other two languages' patterns if that
    finds nothing -- catching the mismatch case without changing behavior
    for the normal case. Not used for /analyze-message, where the language
    is explicitly and reliably provided by the user.
    """
    category, matches = check_rules(text, declared_language)
    if matches > 0:
        return category, matches

    other_languages = [l for l in ("english", "hindi", "gujarati") if l != declared_language]
    for lang in other_languages:
        category, matches = check_rules(text, lang)
        if matches > 0:
            return category, matches

    return None, 0


def rules_risk_percent(matches_found: int) -> int:
    """Rough confidence mapping until Step 5/6 give a real model probability."""
    if matches_found >= 2:
        return 90
    if matches_found == 1:
        return 70
    return 5
