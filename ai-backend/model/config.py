"""
Step 5 config: base model choice + hyperparameters for fine-tuning.

Nothing trains against this yet — fill in once you get to Step 5.
Candidates to evaluate (all handle English/Hindi/Gujarati to varying
degrees — check coverage before committing):
  - "distilbert-base-multilingual-cased" — smallest/fastest, decent baseline
  - "bert-base-multilingual-cased" — better accuracy, still small enough for CPU inference
  - "ai4bharat/indic-bert" — trained specifically on Indian languages, worth
    benchmarking against the multilingual-BERT options for Hindi/Gujarati
"""

BASE_MODEL = "distilbert-base-multilingual-cased"  # placeholder — benchmark before locking in

NUM_LABELS = 6  # kyc_scam, loan_scam, lottery_scam, upi_scam, phishing, not_scam

TRAINING_ARGS = {
    "learning_rate": 2e-5,
    "per_device_train_batch_size": 16,
    "per_device_eval_batch_size": 16,
    "num_train_epochs": 4,
    "weight_decay": 0.01,
}

MAX_SEQUENCE_LENGTH = 128  # scam messages are short; raise if you see truncation issues
