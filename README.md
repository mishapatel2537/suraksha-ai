# Suraksha — Frontend

Android frontend for **Suraksha**, built for the Maverick Effect AI Challenge 2026 Season 3 ("Financial Safety for Rural India" track). Suraksha helps first-time digital banking users detect scam calls, fake UPI requests, phishing, and loan scams — in English, Hindi, and Gujarati.

This README documents the frontend work completed for this project.

## Tech Stack

- **Language:** Kotlin
- **UI:** Jetpack Compose
- **Networking:** Retrofit + OkHttp
- **Navigation:** Jetpack Navigation Compose
- **Package:** `com.suraksha.ai`

  ### Steps
1. Clone this repository.
2. Open the project in Android Studio.
3. Allow Gradle to sync automatically.
4. Run the application on an emulator or a physical Android device.

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

- Shared application state is managed using `MessageInputViewModel`, `GuardianViewModel`, and `ProfileViewModel`, which are provided through `AppNavigation` instead of being passed as navigation route arguments.
- Networking is implemented using Retrofit through `ApiService.kt`, which communicates with the FastAPI backend.
- A `MockApiService` was used during the initial development phase for frontend testing before being replaced with the production API integration for SMS and call analysis.
- The UI is built entirely with Jetpack Compose and follows a screen-based navigation architecture.
- User preferences (such as guardians and app settings) are persisted locally using `SharedPreferences`.

## Consuming the API contract

{
  "category": "kyc_scam | loan_scam | lottery_scam | upi_scam | phishing | impersonation_digital_arrest | impersonation_blackmail | not_scam | unknown",
  "risk_percent": 0-100,
  "explanation": "string, in the requested language",
  "language": "english | hindi | gujarati",
  "trigger_alert": true,
  "alert_message": "string, empty if trigger_alert is false"
}

## 📂 Project Structure

```text
SURAKSHA-AI/
├── app/
│   ├── src/
│   │   ├── androidTest/
│   │   ├── main/
│   │   │   ├── java/com/suraksha/ai/
│   │   │   │   ├── components/
│   │   │   │   ├── navigation/
│   │   │   │   ├── network/
│   │   │   │   ├── screens/
│   │   │   │   ├── ui/
│   │   │   │   └── MainActivity.kt
│   │   │   ├── res/
│   │   │   └── AndroidManifest.xml
│   │   └── test/
│   ├── build.gradle.kts
│   └── .gitignore
├── gradle/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── gradlew
├── gradlew.bat
└── README.md
```

## screens folder structure

```text
screens/
├── callupload/
│   └── CallUploadScreen.kt
├── guardian/
│   ├── GuardianScreen.kt
│   └── GuardianViewModel.kt
├── home/
│   └── HomeScreen.kt
├── login/
│   └── LoginScreen.kt
├── messagecheck/
│   ├── MessageInputScreen.kt
│   └── MessageInputViewModel.kt
├── profile/
│   ├── ProfileScreen.kt
│   └── ProfileViewModel.kt
├── result/
│   └── ResultScreen.kt
├── settings/
│   └── SettingsScreen.kt
├── sms/
│   ├── SmsInboxScreen.kt
│   └── SmsPermissionScreen.kt
└── splash/
    └── SplashScreen.kt
```



