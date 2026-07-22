"""
Shared label constants -- the single source of truth for category<->id
mapping. Deliberately has zero heavy dependencies (no torch/transformers)
so anything that just needs the category list (rules-only evaluation,
quick scripts, tests) doesn't need PyTorch installed to import it.

Must match api/schemas/response_models.py's ScamCategory values exactly.
"""

from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "processed" / "labeled_dataset.csv"

LABELS = [
    "kyc_scam",
    "loan_scam",
    "lottery_scam",
    "upi_scam",
    "phishing",
    "impersonation_digital_arrest",
    "impersonation_blackmail",
    "not_scam",
]
LABEL2ID = {label: i for i, label in enumerate(LABELS)}
ID2LABEL = {i: label for i, label in enumerate(LABELS)}