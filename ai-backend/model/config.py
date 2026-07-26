"""
Config: base model choice + hyperparameters for fine-tuning.

"""

BASE_MODEL = "distilbert-base-multilingual-cased"  # placeholder — benchmark before locking in

NUM_LABELS = 8  # kyc_scam, loan_scam, lottery_scam, upi_scam, phishing,
                # impersonation_digital_arrest, impersonation_blackmail, not_scam

TRAINING_ARGS = {
    "learning_rate": 2e-5,
    "per_device_train_batch_size": 16,
    "per_device_eval_batch_size": 16,
    "num_train_epochs": 8,  # bumped from 4 -- loss was still dropping, not plateaued
    "weight_decay": 0.01,
}

MAX_SEQUENCE_LENGTH = 128  # scam messages are short; raise if you see truncation issues
