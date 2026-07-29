# Suraksha — Frontend

Android frontend for **Suraksha**, built for the Maverick Effect AI Challenge 2026 Season 3 ("Financial Safety for Rural India" track). Suraksha helps first-time digital banking users detect scam calls, fake UPI requests, phishing, and loan scams — in English, Hindi, and Gujarati.

This README documents the frontend work completed for this project.

## Tech Stack

- **Language:** Kotlin
- **UI:** Jetpack Compose
- **Networking:** Retrofit + OkHttp
- **Navigation:** Jetpack Navigation Compose
- **Package:** `com.suraksha.ai`

## Screens Built

| Screen | Description |
|---|---|
| **Splash** | Custom Compose splash screen with shield icon + "सुर"+"ksha" logo, auto-navigates after ~1.2s |
| **Login** | First-run welcome screen — collects name + phone, saved locally (no backend auth) |
| **Home** | Central hub with a 2x2 icon grid for navigating to core actions |
| **Message Input** | Paste/type or Share Intent a suspicious message for analysis |
| **Result** | Shows risk score, category, and plain-language explanation, color-coded by risk level |
| **SMS Permission** | Explains and requests `READ_SMS` access |
| **SMS Inbox** | Reads and lists real device SMS messages via `ContentResolver` |
| **Family Guardian** | Add/remove trusted contacts; test alert via real `SmsManager` |
| **Call Upload** | Pick an audio file and submit it for scam analysis |
| **Profile** | Editable name, member-since date, message/call check counters, recent activity log |
| **Settings** | Language toggle (EN/hi/gu), Guardian Alerts toggle, Dark Mode toggle, Clear Activity Data, About Suraksha, Log Out |

## Key Features

- **Share Intent support** — analyze a message shared directly from other apps
- **Real SMS inbox scanning** — reads on-device messages via the Telephony content provider
- **Family Guardian alerts** — real SMS alerts sent client-side via `SmsManager` when a high-risk scam is detected
- **Multi-language support** — English, Hindi, Gujarati (in progress — see Known Issues)
- **Persistent local login** — simple name/phone login gate, backed by SharedPreferences, with logout
- **Activity tracking** — message/call checks and risk levels logged to Profile via a shared `ProfileViewModel`
- **Real backend integration** — `analyze-message` and `analyze-call` endpoints wired via Retrofit to Person A's deployed backend, matching the locked API contract (category, risk_percent, explanation, language, trigger_alert, alert_message)

## Architecture Notes

- Shared state (`MessageInputViewModel`, `GuardianViewModel`, `ProfileViewModel`) is passed through `AppNavigation` rather than serialized through nav route arguments
- `ApiService.kt` defines the real network contract; a `MockApiService` was used during early development and has since been replaced by real calls in message and call flows
- `AppThemeState` holds the dark mode flag; screen backgrounds are being migrated to a shared theme-aware helper so Dark Mode actually changes appearance app-wide

## Known Issues / In Progress

- **Dark Mode** — toggle exists and updates state correctly, but most screens still hardcode their background colors rather than reading from the shared theme; visual dark mode is not yet fully wired across all screens
- **Language coverage** — some screens (e.g. Settings, Call Upload) still use hardcoded English strings instead of `stringResource()`, so the language toggle doesn't affect them yet; string resources for Hindi/Gujarati need to be completed and applied consistently across every screen
- **Guardian list persistence** — currently held in memory; not yet backed by durable local storage, so the list resets on app restart

## Git Workflow

- `main` — demo-ready, no direct commits
- `ai-backend` — backend/AI work
- `frontend` — this branch, frontend work
- Small, frequent commits; PRs into `main` every couple of days
