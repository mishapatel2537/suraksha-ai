from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_message_flags_known_kyc_pattern():
    response = client.post(
        "/analyze-message",
        json={"text": "Your KYC update is pending, verify your KYC immediately", "language": "english"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "kyc_scam"
    assert body["risk_percent"] > 50
    assert body["language"] == "english"
    assert len(body["explanation"]) > 0
    # high risk_percent (rules layer gives 90 for 2+ matches) -- should trigger
    assert body["trigger_alert"] is True
    assert len(body["alert_message"]) > 0


def test_analyze_message_no_alert_when_not_scam():
    response = client.post(
        "/analyze-message",
        json={"text": "Hey, are we still on for dinner tonight?", "language": "english"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "not_scam"
    assert body["trigger_alert"] is False
    assert body["alert_message"] == ""


def test_analyze_message_clean_text_not_flagged():
    response = client.post(
        "/analyze-message",
        json={"text": "Hey, are we still on for dinner tonight?", "language": "english"},
    )
    assert response.status_code == 200
    assert response.json()["category"] == "not_scam"


def test_guardian_alert_mock_response():
    response = client.post(
        "/guardian-alert",
        json={
            "message_id": "abc123",
            "category": "kyc_scam",
            "risk_percent": 90,
            "guardian_contact": "+911234567890",
        },
    )
    assert response.status_code == 200
    assert response.json()["sent"] is True


def test_analyze_call_no_speech_detected(monkeypatch):
    """Empty transcript (silence/non-speech audio) should be a clear 400, not a wrong classification."""
    def fake_transcribe(path):
        return {"text": "", "whisper_language_code": "en", "language": "english"}

    monkeypatch.setattr("api.routes.analyze_call.transcribe_audio", fake_transcribe)
    response = client.post(
        "/analyze-call",
        files={"audio": ("test.wav", b"fake audio bytes", "audio/wav")},
    )
    assert response.status_code == 400


def test_analyze_call_routes_transcript_through_ensemble(monkeypatch):
    """A transcribed KYC scam call should classify the same way the equivalent text message would."""
    def fake_transcribe(path):
        return {
            "text": "Your KYC is pending, account will be blocked, share your OTP immediately",
            "whisper_language_code": "en",
            "language": "english",
        }

    monkeypatch.setattr("api.routes.analyze_call.transcribe_audio", fake_transcribe)
    response = client.post(
        "/analyze-call",
        files={"audio": ("test.wav", b"fake audio bytes", "audio/wav")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "kyc_scam"
    assert body["language"] == "english"


def test_analyze_call_unsupported_language_falls_back(monkeypatch):
    """If Whisper detects a language outside english/hindi/gujarati, fall back rather than crash."""
    def fake_transcribe(path):
        return {"text": "some transcribed text", "whisper_language_code": "ta", "language": None}

    monkeypatch.setattr("api.routes.analyze_call.transcribe_audio", fake_transcribe)
    response = client.post(
        "/analyze-call",
        files={"audio": ("test.wav", b"fake audio bytes", "audio/wav")},
    )
    assert response.status_code == 200
    assert response.json()["language"] == "english"  # FALLBACK_LANGUAGE
