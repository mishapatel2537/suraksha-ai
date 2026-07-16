# Suraksha — AI + Backend (Person A's branch)

Scam detection backend for **Suraksha**, an Android app helping first-time
digital banking users in rural India detect scam calls, fake UPI requests,
phishing, and loan scams. Built for the Maverick Effect AI Challenge 2026,
Season 3 — "Financial Safety for Rural India" track.

## Status

This is the Step 1 + Step 2 scaffold: environment, folder structure, and
the **locked API contract** (`category`, `risk_percent`, `explanation`,
`language`). `/analyze-message` and `/guardian-alert` are live and running
on the rules-based fallback layer only — no ML model yet, that's Step 5+.
`/analyze-call` is stubbed (501) pending Step 9.

## Setup

```bash
cd ai-backend
python3 -m venv .venv
source .venv/bin/activate        # .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env             # fill in ANTHROPIC_API_KEY
```

## Run

```bash
uvicorn api.main:app --reload --port 8000
```

Then open http://127.0.0.1:8000/docs for interactive Swagger UI — useful
for Person B to see exact request/response shapes without reading code.

## Test

```bash
pytest tests/ -v
```

## What's next (per the step-by-step plan)

- **Step 3** — collect & label the multilingual dataset (biggest bottleneck, start ASAP)
- **Step 4** — rules layer is scaffolded in `rules/`, but pattern lists are
  just a handful of seed examples — expand them as you collect real data
- **Step 5** — fine-tune the classifier (`model/config.py` has placeholder
  hyperparameters and 3 base-model candidates to benchmark)
- **Step 6-7** — risk % + evaluation
- **Step 8** — explanation generation is wired up in `explanation/claude_explainer.py`
  with a template fallback if the API key isn't set or the call fails
- **Step 9** — speech-to-text (`speech/transcribe.py` doesn't exist yet)
- **Step 10-14** — logging (`api/db/logging.py` has the schema but isn't
  wired into the routes yet), deploy, integration testing, error handling

## Folder structure

See the top-level docstrings in each module — the shape follows the
reference structure doc exactly (`data/`, `rules/`, `model/`,
`explanation/`, `speech/`, `api/`, `tests/`).

## API contract (locked — do not change without telling Person B)

```json
{
  "category": "kyc_scam | loan_scam | lottery_scam | upi_scam | phishing | not_scam | unknown",
  "risk_percent": 0-100,
  "explanation": "string, in the requested language",
  "language": "english | hindi | gujarati"
}
```
