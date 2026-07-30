"""
Validates the rules-based fallback layer against the real labeled
dataset. This isn't the full model evaluation — it's a
regression check that pattern-list edits don't accidentally tank recall
or, more importantly, spike the false-alarm rate on real not_scam text.

Run with: pytest tests/test_rules.py -v -s
"""

import csv
from pathlib import Path

from rules.scam_patterns import check_rules

DATASET_PATH = Path(__file__).parent.parent / "data" / "processed" / "labeled_dataset.csv"


def _load_dataset():
    if not DATASET_PATH.exists():
        return []
    with open(DATASET_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_false_alarm_rate_stays_low():
    """
    The rules layer's main job is precision, not recall — a real (non-scam)
    message getting flagged erodes user trust fast. This should stay near-zero.
    """
    rows = _load_dataset()
    if not rows:
        return  # dataset not present in this environment, skip
    not_scam_rows = [r for r in rows if r["category"] == "not_scam"]
    false_alarms = sum(
        1 for r in not_scam_rows
        if (check_rules(r["text"], r["language"])[0] or "not_scam") != "not_scam"
    )
    false_alarm_rate = false_alarms / len(not_scam_rows)
    assert false_alarm_rate < 0.05, (
        f"False alarm rate {false_alarm_rate:.1%} is too high for a fallback layer "
        f"({false_alarms}/{len(not_scam_rows)}) — check recent pattern_lists edits."
    )


def test_kyc_scam_recall_baseline():
    """kyc_scam recall was tuned to ~81% — regression-check it doesn't silently drop."""
    rows = _load_dataset()
    if not rows:
        return
    kyc_rows = [r for r in rows if r["category"] == "kyc_scam"]
    correct = sum(
        1 for r in kyc_rows
        if (check_rules(r["text"], r["language"])[0] or "not_scam") == "kyc_scam"
    )
    recall = correct / len(kyc_rows)
    assert recall > 0.6, f"kyc_scam recall dropped to {recall:.1%}, expected >60%"


def test_print_full_report(capsys):
    """Not a real assertion — just prints the current per-category recall table
    when run with -s, so you can see the fallback layer's actual coverage."""
    rows = _load_dataset()
    if not rows:
        return
    categories = sorted(set(r["category"] for r in rows))
    print("\n\n=== Rules layer recall by category ===")
    for cat in categories:
        cat_rows = [r for r in rows if r["category"] == cat]
        correct = sum(
            1 for r in cat_rows
            if (check_rules(r["text"], r["language"])[0] or "not_scam") == cat
        )
        print(f"  {cat}: {correct}/{len(cat_rows)} = {correct/len(cat_rows)*100:.1f}%")