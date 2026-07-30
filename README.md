# Suraksha AI

**Your shield against scams.**

An AI-powered Android app that detects scam texts, calls, and UPI fraud for first-time digital banking users in rural India — in **English, Hindi, and Gujarati**.

Built for the **Maverick Effect AI Challenge 2026, Season 3** — *Financial Safety for Rural India* track.

- 🎥 Demo video: https://youtu.be/0aYcP0VeDFY

| | |
|---|---|
| **AI / Backend** | Misha Patel — model training, Whisper, FastAPI, Claude explanations |
| **Android Frontend** | Palak Parmar — Kotlin, Jetpack Compose, full UI/UX |

---

## The Problem

Rural India's digital banking boom has outrun its scam awareness. First-time UPI and mobile-banking users are the fastest-growing target for fraud — and the least equipped to spot it:

- **Language barrier** — most scam-detection tools exist only in English
- **Multi-channel fraud** — scams arrive as SMS, WhatsApp forwards, and phone calls impersonating banks, KYC officers, or police
- **No safety net** — elderly or first-time users often have no one nearby to double-check a suspicious message

## The Solution

One app, three ways to check, three languages. A user can paste a message, scan their whole SMS inbox, or upload a call recording, and get a plain-language risk verdict in the language they already read in.

- **Check a Message** — paste, type, or Share-Intent a suspicious text; classified with risk %, category, and explanation
- **Scan SMS Inbox** — reads the real device inbox and auto-analyzes every message in place
- **Check a Call Recording** — upload audio; Whisper transcribes it, then the same pipeline classifies it
- **Family Guardian** — high-risk hits automatically alert a trusted contact by real SMS, no app needed on their end

**What sets it apart:** not just an LLM wrapper — a measured, fine-tuned ensemble model (rules + distilBERT) with a fallback layer, wired into real device SMS/call access, across three languages.

---

## Architecture

```
Android App  →  FastAPI (Render)  →  Rules → Model → Fallback  →  Claude API
  text/SMS/audio    /analyze-message      ensemble classifier      plain-language
                     /analyze-call                                 explanation
                                                                          ↓
                                                                  Guardian Alert
                                                                  (SMS via SmsManager)
```

Deployed on Render · SQLite logging · 28-test pytest suite · single ensemble module shared by the live API and offline evaluation.

## Tech Stack

**Frontend (Android)**
- Kotlin, Jetpack Compose, Material 3
- Retrofit + OkHttp (networking), Jetpack Navigation Compose
- SharedPreferences (local persistence), Android SmsManager / ContentResolver / Telephony provider
- Runtime permissions, Share Intent (`ACTION_SEND`), string-resource localization (`values`, `values-hi`, `values-gu`)

**Backend / AI**
- FastAPI on Render, SQLite logging
- Fine-tuned `distilbert-base-multilingual-cased` + rules-based fallback layer (ensemble)
- Whisper (speech-to-text for call recordings)
- Claude API (plain-language explanation generation)
- pytest (28 tests: API behavior, alert threshold logic, rules precision/recall)

---

## API Contract

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

- `trigger_alert` fires when `risk_percent >= 70`
- `alert_message` uses a fixed template (not a live Claude call) for reliability and SMS-length safety
- Actual SMS delivery to guardians happens entirely client-side via Android's `SmsManager` — the backend only decides and drafts

### Endpoints

| Endpoint | Description |
|---|---|
| `POST /analyze-message` | Text in, classification out (rules → model → fallback ensemble) |
| `POST /analyze-call` | Audio file in, transcribed via Whisper, then run through the same pipeline as `/analyze-message` |
| `POST /guardian-alert` | Mocked SMS-send confirmation (real sending happens on the Android side) |

---

## Model Performance

Held-out validation set, 186 examples. Ensemble (rules + fine-tuned distilBERT):

**~90% accuracy · 1.4% missed-scam rate · 5.1% false-alarm rate**

Weakest category: `upi_scam` (~57% recall, mostly confused with `phishing` due to genuine content overlap). Everything else scores 0.7+ F1, with `impersonation_digital_arrest` and `impersonation_blackmail` performing strongest.

---

## Screens

| Screen | Description |
|---|---|
| Splash | Custom Compose splash with shield icon + wordmark |
| Login | Local-only name + phone capture (no backend auth) |
| Home | 2×2 grid for the four core actions |
| Check a Message | Paste/type or Share Intent a message for analysis |
| Result | Risk score, category, and explanation, color-coded by risk |
| Scan SMS Inbox | Reads and auto-analyzes real device SMS |
| Check a Call Recording | Pick an audio file and submit for analysis |
| Family Guardian | Add/remove trusted contacts; real test SMS alert |
| Profile | Name, member-since date, activity counters, recent activity log |
| Settings | Language toggle (EN/hi/gu), Guardian Alerts toggle, Dark Mode, Clear Activity Data, About, Log Out |

---

## Getting Started

### Backend

```bash
cd ai-backend
python -m venv .venv
source .venv/bin/activate        # .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env             # fill in ANTHROPIC_API_KEY
```

**System dependency:** `ffmpeg` must be installed and on PATH (Whisper needs it for audio decoding).

```bash
python -m uvicorn api.main:app --reload --port 8000
```

Open http://127.0.0.1:8000/docs for the interactive Swagger UI. Run tests with:

```bash
pytest tests/ -v
```

### Frontend

1. Clone this repository
2. Open in Android Studio
3. Let Gradle sync
4. Run on an emulator or a physical Android device

---

## Project Structure

```
suraksha-ai/
├── app/                        # Android frontend (Kotlin, Jetpack Compose)
│   └── src/main/java/com/suraksha/ai/
│       ├── components/
│       ├── navigation/
│       ├── network/
│       ├── screens/
│       │   ├── callupload/
│       │   ├── guardian/
│       │   ├── home/
│       │   ├── login/
│       │   ├── messagecheck/
│       │   ├── profile/
│       │   ├── result/
│       │   ├── settings/
│       │   ├── sms/
│       │   └── splash/
│       ├── ui/
│       └── MainActivity.kt
├── ai-backend/                 # FastAPI backend + AI pipeline
│   ├── data/                   # raw, processed, and synthetic training data
│   ├── rules/                  # keyword-based fallback layer
│   ├── model/                  # training, evaluation, inference, ensemble
│   ├── explanation/             # Claude-based explanation + alert generation
│   ├── speech/                  # Whisper transcription
│   ├── api/                     # FastAPI app, routes, schemas, SQLite logging
│   └── tests/                   # pytest suite
└── README.md
```

---

## Known Limitations

- **SMS Inbox scanning is not live** — scans on screen-open and via manual refresh, not on new incoming messages in the background
- **Call recording check can fail on the deployed instance** — the free-tier Render instance (512MB RAM) can run out of memory loading the classifier and Whisper together
- **`upi_scam` recall is weak (~57%)**, mostly confused with `phishing`
- **Whisper can confuse Hindi and Gujarati** on short or noisy audio, since the languages are related
- **Login is not real authentication** — local name/phone entry only, no backend account system
- **No automated frontend tests** — testing was manual across all screens

## Future Scope

- Live background SMS/call screening, not just user-initiated checks
- Offline-first rules fallback for poor-connectivity areas
- Expanded UPI-scam training data + broader language support
- Cross-device Guardian sync (Firebase Auth + cloud storage)
