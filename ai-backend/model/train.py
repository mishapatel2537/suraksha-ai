"""
Fine-tune the multilingual scam classifier.

Usage on Colab:
    1. Upload data/processed/labeled_dataset.csv to the Colab session
       (or mount Google Drive and point DATA_PATH at it).
    2. pip install transformers torch scikit-learn pandas accelerate
    3. Upload this file (or paste its contents into a cell) along with
       model/config.py, then run:
           python train.py
    4. Download the resulting model/artifacts/suraksha-classifier/ folder
       and place it in your local repo at that same path.

Usage locally (only if you have a decent GPU):
    cd ai-backend
    python model/train.py
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

sys.path.insert(0, str(Path(__file__).parent.parent))
from model.config import BASE_MODEL, MAX_SEQUENCE_LENGTH, NUM_LABELS, TRAINING_ARGS
from model.labels import DATA_PATH, ID2LABEL, LABEL2ID, LABELS

OUTPUT_DIR = Path(__file__).parent / "artifacts" / "suraksha-classifier"


class ScamDataset(torch.utils.data.Dataset):
    """Wraps tokenizer output + labels in the dict-of-tensors shape Trainer expects."""

    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def compute_metrics(eval_pred):
    """
    Weighted F1 matters more than raw accuracy here — your classes aren't
    balanced (phishing has 262 rows, impersonation_blackmail has 54), so a
    model that just always predicts the majority class would still score
    ~20% accuracy without being useful. Weighted F1 accounts for that.
    Per-category recall (printed separately) is what actually tells you
    whether the model learned the rare categories or not.
    """
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    acc = accuracy_score(labels, preds)
    f1_weighted = f1_score(labels, preds, average="weighted")
    return {"accuracy": acc, "f1_weighted": f1_weighted}


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run this from the ai-backend/ directory "
            f"with data/processed/labeled_dataset.csv in place."
        )

    print(f"Loading dataset from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)

    # drop any rows with a category outside the 8 trained labels (e.g. stray
    # "unknown" rows shouldn't exist in training data, but guard anyway)
    before = len(df)
    df = df[df["category"].isin(LABELS)].reset_index(drop=True)
    if len(df) < before:
        print(f"Dropped {before - len(df)} rows with unrecognized categories.")

    df["label_id"] = df["category"].map(LABEL2ID)
    print(f"\nTotal rows: {len(df)}")
    print(df["category"].value_counts())

    # stratified split keeps the same class balance in train and val --
    # important given how uneven your categories are (54 to 262 rows)
    train_df, val_df = train_test_split(
        df, test_size=0.15, random_state=42, stratify=df["label_id"]
    )
    print(f"\nTrain: {len(train_df)} | Val: {len(val_df)}")

    print(f"\nLoading tokenizer + model: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )

    def tokenize(texts):
        return tokenizer(
            list(texts),
            truncation=True,
            padding="max_length",
            max_length=MAX_SEQUENCE_LENGTH,
        )

    print("\nTokenizing...")
    train_encodings = tokenize(train_df["text"])
    val_encodings = tokenize(val_df["text"])

    train_dataset = ScamDataset(train_encodings, train_df["label_id"].tolist())
    val_dataset = ScamDataset(val_encodings, val_df["label_id"].tolist())

    training_args = TrainingArguments(
        output_dir=str(Path(__file__).parent / "checkpoints"),
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=1,  # keep only the latest checkpoint -- avoids the disk-space crash from last run
        load_best_model_at_end=True,
        metric_for_best_model="f1_weighted",
        logging_steps=20,
        **TRAINING_ARGS,  # learning_rate, batch sizes, epochs, weight_decay from config.py
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    print("\nTraining...")
    trainer.train()

    print("\nFinal validation metrics:")
    eval_results = trainer.evaluate()
    print(eval_results)

    # per-category breakdown -- the number that actually matters for your
    # rarer classes (impersonation_blackmail, upi_scam) that weighted F1 can hide
    print("\nPer-category precision/recall/F1 on validation set:")
    preds = trainer.predict(val_dataset)
    pred_labels = np.argmax(preds.predictions, axis=1)
    precision, recall, f1, support = precision_recall_fscore_support(
        val_df["label_id"], pred_labels, labels=list(range(NUM_LABELS)), zero_division=0
    )
    for i, label in ID2LABEL.items():
        print(f"  {label}: precision={precision[i]:.2f} recall={recall[i]:.2f} "
              f"f1={f1[i]:.2f} (n={support[i]})")

    print(f"\nSaving model to {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))

    # id2label/label2id are already baked into the saved config.json by
    # save_pretrained above, but a standalone file is convenient for the
    # API layer or any script that just wants the label list without
    # loading the full model config.
    with open(OUTPUT_DIR / "labels.json", "w") as f:
        json.dump({"labels": LABELS, "label2id": LABEL2ID, "id2label": ID2LABEL}, f, indent=2)

    print("\nDone. Copy the artifacts/suraksha-classifier/ folder to your local repo if trained on Colab.")


if __name__ == "__main__":
    main()