"""
Recovery script: your training run finished successfully (checkpoint-264
has the trained model), but crashed during the optimizer-state write, so
train.py never reached its final steps — saving the tokenizer, saving
labels.json, and printing the per-category metrics table.

This script does just those 3 things from the already-trained checkpoint,
without retraining anything.

Usage: python model/finish_after_crash.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from model.config import BASE_MODEL, MAX_SEQUENCE_LENGTH
from model.train import DATA_PATH, ID2LABEL, LABEL2ID, LABELS, ScamDataset

CHECKPOINT_DIR = Path(__file__).parent / "checkpoints" / "checkpoint-264"
OUTPUT_DIR = Path(__file__).parent / "artifacts" / "suraksha-classifier"

print(f"Loading trained model from {CHECKPOINT_DIR}")
model = AutoModelForSequenceClassification.from_pretrained(str(CHECKPOINT_DIR))
model.eval()

print(f"Downloading tokenizer for {BASE_MODEL} (small, no retraining)")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
model.save_pretrained(str(OUTPUT_DIR))
tokenizer.save_pretrained(str(OUTPUT_DIR))

with open(OUTPUT_DIR / "labels.json", "w") as f:
    json.dump({"labels": LABELS, "label2id": LABEL2ID, "id2label": ID2LABEL}, f, indent=2)

print(f"Saved complete model + tokenizer to {OUTPUT_DIR}")

# --- reproduce the same val split train.py used (same random_state=42) to print metrics ---
df = pd.read_csv(DATA_PATH)
df = df[df["category"].isin(LABELS)].reset_index(drop=True)
df["label_id"] = df["category"].map(LABEL2ID)
_, val_df = train_test_split(df, test_size=0.15, random_state=42, stratify=df["label_id"])

val_encodings = tokenizer(
    list(val_df["text"]), truncation=True, padding="max_length", max_length=MAX_SEQUENCE_LENGTH
)
val_dataset = ScamDataset(val_encodings, val_df["label_id"].tolist())

print("\nRunning inference on validation set...")
all_preds = []
with torch.no_grad():
    for i in range(len(val_dataset)):
        item = val_dataset[i]
        inputs = {k: v.unsqueeze(0) for k, v in item.items() if k != "labels"}
        logits = model(**inputs).logits
        all_preds.append(int(torch.argmax(logits, dim=1)))

precision, recall, f1, support = precision_recall_fscore_support(
    val_df["label_id"], all_preds, labels=list(range(len(LABELS))), zero_division=0
)
print("\nPer-category precision/recall/F1 on validation set:")
for i, label in ID2LABEL.items():
    print(f"  {label}: precision={precision[i]:.2f} recall={recall[i]:.2f} "
          f"f1={f1[i]:.2f} (n={support[i]})")