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


def rules_risk_percent(matches_found: int) -> int:
    """Rough confidence mapping until Step 5/6 give a real model probability."""
    if matches_found >= 2:
        return 90
    if matches_found == 1:
        return 70
    return 5
