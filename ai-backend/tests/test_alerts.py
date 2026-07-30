"""
Tests for the Family Guardian alert logic (explanation/alert_generator.py).
"""

from api.schemas.request_models import Language
from explanation.alert_generator import (
    ALERT_THRESHOLD,
    compute_trigger_alert,
    generate_alert_message,
)
from rules.scam_patterns import check_rules, check_rules_any_language


def test_threshold_constant_is_70():
    # Not load-bearing on its own, but if someone changes ALERT_THRESHOLD
    # without meaning to, this test name makes the diff obvious in review.
    assert ALERT_THRESHOLD == 70


def test_just_below_threshold_does_not_trigger():
    assert compute_trigger_alert(69) is False


def test_at_threshold_triggers():
    assert compute_trigger_alert(70) is True


def test_just_above_threshold_triggers():
    assert compute_trigger_alert(71) is True


def test_zero_does_not_trigger():
    assert compute_trigger_alert(0) is False


def test_hundred_triggers():
    assert compute_trigger_alert(100) is True


def test_alert_message_all_languages_nonempty_and_short():
    # SMS length safety check -- Unicode (Hindi/Gujarati) segments are much
    # shorter than English GSM-7 ones, so this is worth actually asserting,
    # not just assuming the templates are short enough.
    for lang in [Language.ENGLISH, Language.HINDI, Language.GUJARATI]:
        msg = generate_alert_message("kyc_scam", lang)
        assert len(msg) > 0
        assert len(msg) < 140, f"{lang.value} alert message too long for a single SMS segment: {len(msg)} chars"


def test_alert_message_substitutes_category_name():
    msg_en = generate_alert_message("impersonation_digital_arrest", Language.ENGLISH)
    assert "fake police call" in msg_en
    assert "impersonation_digital_arrest" not in msg_en  # raw category id shouldn't leak into user-facing text


def test_alert_message_unknown_category_falls_back_gracefully():
    # Shouldn't crash if called with a category not in _CATEGORY_NAMES --
    # falls back to the raw string rather than raising.
    msg = generate_alert_message("some_future_category", Language.ENGLISH)
    assert "some_future_category" in msg


def test_check_rules_any_language_catches_whisper_language_mismatch():
    """
    Regression test for a real bug found in production: Whisper's 'tiny'
    model detected Hindi audio correctly but transcribed it into rough
    English words. check_rules() alone (checking only against the
    declared 'hindi' patterns) found nothing, since the text was actually
    English. check_rules_any_language() should catch this by falling
    back to checking the other languages' patterns.
    """
    garbled_transcript = (
        "Namaste, I am Delhi Police Cyber Crime Department saying that you are "
        "a mani-londering case. Sir, your name is a criminal complaint. If you "
        "dont operate, then digital arrest can be done. Investigation officer, "
        "talk about this."
    )

    # the bug: declared-language-only check finds nothing
    category, matches = check_rules(garbled_transcript, "hindi")
    assert matches == 0

    # the fix: any-language check finds it
    category, matches = check_rules_any_language(garbled_transcript, "hindi")
    assert category == "impersonation_digital_arrest"
    assert matches >= 2