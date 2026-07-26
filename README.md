# Suraksha — AI + Backend

Scam detection backend for **Suraksha**, an Android app helping first-time
digital banking users in rural India detect scam calls, texts, and UPI
fraud in English, Hindi, and Gujarati. Built for the Maverick Effect AI
Challenge 2026, Season 3 — "Financial Safety for Rural India" track.

## Status: core pipeline complete and live

All three endpoints are built and working, backed by a trained classifier,
a rules-based fallback layer, live Claude-generated explanations, and
Family Guardian alert logic. Remaining work is deployment and integration
testing with the Android app (see "What's next" below).

## Setup

```bash
cd ai-backend
python -m venv .venv
source .venv/bin/activate        # .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env             # fill in ANTHROPIC_API_KEY
```

**System dependency:** `ffmpeg` must be installed and on PATH (Whisper
shells out to it for audio decoding). `winget install ffmpeg` on Windows,
then add its `bin` folder to PATH manually if it isn't picked up
automatically — this has been a recurring gotcha across machines.

## Run

```bash
python -m uvicorn api.main:app --reload --port 8000
```

Then open http://127.0.0.1:8000/docs for interactive Swagger UI — useful
for Person B to see exact request/response shapes without reading code.

## Test

```bash
pytest tests/ -v
```

28 tests across `test_api.py` (endpoint behavior + edge cases),
`test_alerts.py` (Family Guardian threshold logic), and `test_rules.py`
(rules layer precision/recall against the real labeled dataset).

## Endpoints

- **`POST /analyze-message`** — text in, classification out. Runs the
  rules → model → fallback ensemble (see `model/ensemble.py`).
- **`POST /analyze-call`** — audio file in, transcribes via Whisper then
  runs the exact same classification pipeline as `/analyze-message`.
- **`POST /guardian-alert`** — mocked SMS-send confirmation (real sending
  happens entirely on Person B's Android side via `SmsManager`).

## API contract (locked - do not change without discussing)

```json
{
  "category": "kyc_scam | loan_scam | lottery_scam | upi_scam | phishing | impersonation_digital_arrest | impersonation_blackmail | not_scam | unknown",
  "risk_percent": 0-100,
  "explanation": "string, in the requested language",
  "language": "english | hindi | gujarati",
  "trigger_alert": true,
  "alert_message": "string, empty if trigger_alert is false"
}
```

`trigger_alert` fires when `risk_percent >= 70` (see
`explanation/alert_generator.py`). `alert_message` uses a fixed template
(not a live Claude call) for reliability and SMS-length safety.

## Model performance (held-out validation set, 186 examples)

Ensemble (rules + fine-tuned `distilbert-base-multilingual-cased`):
**~90% accuracy, 1.4% missed-scam rate, 5.1% false-alarm rate.**

Weakest category: `upi_scam` (~57% recall, mostly confused with
`phishing` — genuine content overlap). Everything else scores 0.7+ F1,
with `impersonation_digital_arrest` and `impersonation_blackmail`
performing strongest.

Run `python -m model.evaluate` to reproduce this report (rules-only vs
model-only vs ensemble, side by side, plus a full confusion matrix).

## Known limitations, worth mentioning if asked

- **Whisper can confuse Hindi and Gujarati** on short or noisy audio
  clips, since they're related languages — a known Whisper limitation,
  not a bug in this codebase.
- **`upi_scam` recall is the weakest category** — more training data
  here would help most if there's time before the deadline.
- **`impersonation_blackmail` has the least training data** (54 rows) of
  any category — strong validation-set scores here should be read with
  that small sample size in mind.
- Rules-layer patterns were tuned for high precision over recall by
  design (a fallback shouldn't cry wolf) — it's meant to catch what the
  model misses, not replace it.

## Folder structure

```
ai-backend/
├── data/           # raw, processed, and synthetic training data
├── rules/          # keyword-based fallback layer + pattern lists
├── model/          # training, evaluation, inference, ensemble logic
├── explanation/    # Claude-based explanation + alert message generation
├── speech/         # Whisper transcription
├── api/            # FastAPI app, routes, schemas, SQLite logging
└── tests/          # pytest suite
```

## What's next

- **Deploy** — not yet done. Plan is Render (free tier), watching this
  branch directly rather than `main`, so merging into `main` doesn't
  trigger unrelated redeploys.
- **Integration testing with Person B's app** — real end-to-end test
  with her actual Android code, not just Swagger UI (contract shape,
  audio format from a real device, HTTPS, SMS trigger all need
  verifying together).
- **Merge into `main`** once the above are stable.