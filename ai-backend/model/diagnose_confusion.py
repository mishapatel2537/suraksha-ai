"""
Diagnostic: kyc_scam scored 0.00 precision/recall in the validation report.
This prints a confusion matrix so we can see exactly what the model is
predicting instead, rather than guessing.

Usage: python -m model.diagnose_confusion
"""

import sys
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from model.config import MAX_SEQUENCE_LENGTH
from model.train import DATA_PATH, ID2LABEL, LABEL2ID, LABELS, ScamDataset

MODEL_DIR = Path(__file__).parent / "artifacts" / "suraksha-classifier"

print(f"Loading model from {MODEL_DIR}")
model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
model.eval()

df = pd.read_csv(DATA_PATH)
df = df[df["category"].isin(LABELS)].reset_index(drop=True)
df["label_id"] = df["category"].map(LABEL2ID)
_, val_df = train_test_split(df, test_size=0.15, random_state=42, stratify=df["label_id"])

val_encodings = tokenizer(
    list(val_df["text"]), truncation=True, padding="max_length", max_length=MAX_SEQUENCE_LENGTH
)
val_dataset = ScamDataset(val_encodings, val_df["label_id"].tolist())

all_preds = []
with torch.no_grad():
    for i in range(len(val_dataset)):
        item = val_dataset[i]
        inputs = {k: v.unsqueeze(0) for k, v in item.items() if k != "labels"}
        logits = model(**inputs).logits
        all_preds.append(int(torch.argmax(logits, dim=1)))

cm = confusion_matrix(val_df["label_id"], all_preds, labels=list(range(len(LABELS))))

print("\nConfusion matrix (rows = true category, columns = predicted category)")
print(f"{'':30s}", end="")
for label in LABELS:
    print(f"{label[:8]:>9s}", end="")
print()
for i, true_label in enumerate(LABELS):
    print(f"{true_label:30s}", end="")
    for j in range(len(LABELS)):
        print(f"{cm[i][j]:>9d}", end="")
    print()

print("\n--- kyc_scam validation examples: true label vs what the model predicted ---")
kyc_val = val_df[val_df["category"] == "kyc_scam"]
kyc_indices = [i for i, (_, row) in enumerate(val_df.iterrows()) if row["category"] == "kyc_scam"]
for idx, (_, row) in zip(kyc_indices, kyc_val.iterrows()):
    pred_label = ID2LABEL[all_preds[idx]]
    print(f"  [{row['language']}] predicted={pred_label} | text: {row['text'][:80]}")