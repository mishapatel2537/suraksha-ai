"""
Evaluate.py -- precision/recall/confusion matrix per category.

Evaluates three things side by side, on the same held-out validation split
train.py used (same random_state=42, so this is genuinely held-out data
the model never trained on):

  1. Rules-only (fallback layer alone)
  2. Model-only (the raw classifier, ignoring rules)
  3. Ensemble (model/ensemble.py -- what the live API actually returns)

Comparing all three matters: it's the only way to know whether the
ensemble is actually earning its complexity over either piece alone.

Special attention to missed scams (false negatives on any real scam
category): per the project plan, a missed scam is the costly failure
mode -- a false alarm on a real not_scam message is annoying, but a
missed real scam could directly cost someone money.

Usage: python -m model.evaluate
"""

import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).parent.parent))

from model.ensemble import classify
from model.predict import predict as model_predict
from model.labels import DATA_PATH, LABEL2ID, LABELS
from rules.scam_patterns import check_rules

SCAM_CATEGORIES = [l for l in LABELS if l != "not_scam"]


def load_val_split():
    df = pd.read_csv(DATA_PATH)
    df = df[df["category"].isin(LABELS)].reset_index(drop=True)
    df["label_id"] = df["category"].map(LABEL2ID)
    _, val_df = train_test_split(df, test_size=0.15, random_state=42, stratify=df["label_id"])
    return val_df


def rules_only_predict(text, language):
    category, matches = check_rules(text, language)
    return category if category else "not_scam"


def model_only_predict(text):
    result = model_predict(text)
    if result is None:
        return None  # caller should skip / report model unavailable
    category, _confidence = result
    return category


def ensemble_predict(text, language):
    category, _risk_percent = classify(text, language)
    return category


def print_report(name, val_df, preds):
    print(f"\n{'='*60}\n{name}\n{'='*60}")

    true_labels = val_df["category"].tolist()
    label_order = LABELS
    precision, recall, f1, support = precision_recall_fscore_support(
        true_labels, preds, labels=label_order, zero_division=0
    )
    overall_acc = sum(1 for t, p in zip(true_labels, preds) if t == p) / len(true_labels)
    print(f"Overall accuracy: {overall_acc:.1%}\n")
    print(f"{'category':32s}{'precision':>10s}{'recall':>10s}{'f1':>10s}{'n':>6s}")
    for i, label in enumerate(label_order):
        print(f"{label:32s}{precision[i]:>10.2f}{recall[i]:>10.2f}{f1[i]:>10.2f}{support[i]:>6d}")

    # missed scams: true category is a real scam, predicted not_scam
    missed = sum(
        1 for t, p in zip(true_labels, preds)
        if t in SCAM_CATEGORIES and p == "not_scam"
    )
    total_scams = sum(1 for t in true_labels if t in SCAM_CATEGORIES)
    print(f"\nMissed scams (real scam predicted as not_scam): {missed}/{total_scams} "
          f"({missed/total_scams:.1%}) -- the costly failure mode")

    # false alarms: true not_scam, predicted as any scam category
    false_alarms = sum(
        1 for t, p in zip(true_labels, preds)
        if t == "not_scam" and p != "not_scam"
    )
    total_notscam = sum(1 for t in true_labels if t == "not_scam")
    print(f"False alarms (real not_scam flagged as a scam): {false_alarms}/{total_notscam} "
          f"({false_alarms/total_notscam:.1%})")

    return {"accuracy": overall_acc, "missed_scam_rate": missed / total_scams,
            "false_alarm_rate": false_alarms / total_notscam}


def print_confusion_matrix(name, val_df, preds):
    print(f"\n--- {name}: confusion matrix (rows=true, cols=predicted) ---")
    cm = confusion_matrix(val_df["category"], preds, labels=LABELS)
    print(f"{'':30s}", end="")
    for label in LABELS:
        print(f"{label[:8]:>9s}", end="")
    print()
    for i, true_label in enumerate(LABELS):
        print(f"{true_label:30s}", end="")
        for j in range(len(LABELS)):
            print(f"{cm[i][j]:>9d}", end="")
        print()


def main():
    val_df = load_val_split()
    print(f"Evaluating on {len(val_df)} held-out validation examples "
          f"(same split train.py used, random_state=42)")

    texts = val_df["text"].tolist()
    languages = val_df["language"].tolist()

    print("\nRunning rules-only predictions...")
    rules_preds = [rules_only_predict(t, l) for t, l in zip(texts, languages)]

    print("Running model-only predictions...")
    model_preds_raw = [model_only_predict(t) for t in texts]
    if any(p is None for p in model_preds_raw):
        print("\nWARNING: model/artifacts/suraksha-classifier not found -- "
              "skipping model-only and ensemble evaluation. Run model/train.py first.")
        print_report("RULES-ONLY", val_df, rules_preds)
        print_confusion_matrix("RULES-ONLY", val_df, rules_preds)
        return
    model_preds = model_preds_raw

    print("Running ensemble predictions...")
    ensemble_preds = [ensemble_predict(t, l) for t, l in zip(texts, languages)]

    results = {}
    results["rules_only"] = print_report("RULES-ONLY", val_df, rules_preds)
    results["model_only"] = print_report("MODEL-ONLY", val_df, model_preds)
    results["ensemble"] = print_report("ENSEMBLE (what the live API returns)", val_df, ensemble_preds)

    print(f"\n{'='*60}\nSUMMARY\n{'='*60}")
    print(f"{'method':20s}{'accuracy':>12s}{'missed scams':>16s}{'false alarms':>16s}")
    for method, r in results.items():
        print(f"{method:20s}{r['accuracy']:>12.1%}{r['missed_scam_rate']:>16.1%}{r['false_alarm_rate']:>16.1%}")

    print_confusion_matrix("ENSEMBLE", val_df, ensemble_preds)


if __name__ == "__main__":
    main()