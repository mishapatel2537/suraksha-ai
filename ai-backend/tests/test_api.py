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


def test_analyze_call_rejects_unsupported_file_type():
    response = client.post(
        "/analyze-call",
        files={"audio": ("test.pdf", b"not actually audio", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_analyze_call_rejects_oversized_file():
    oversized = b"x" * (16 * 1024 * 1024)  # 16MB, over the 15MB cap
    response = client.post(
        "/analyze-call",
        files={"audio": ("test.wav", oversized, "audio/wav")},
    )
    assert response.status_code == 413
    assert "too large" in response.json()["detail"]


def test_analyze_call_rejects_empty_file():
    response = client.post(
        "/analyze-call",
        files={"audio": ("test.wav", b"", "audio/wav")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_analyze_call_transcription_crash_returns_clean_message(monkeypatch):
    """A raw exception from Whisper/ffmpeg should never leak to the client."""
    def broken_transcribe(path):
        raise RuntimeError("some internal ffmpeg path detail that shouldn't leak: /tmp/xyz123")

    monkeypatch.setattr("api.routes.analyze_call.transcribe_audio", broken_transcribe)
    response = client.post(
        "/analyze-call",
        files={"audio": ("test.wav", b"fake audio bytes", "audio/wav")},
    )
    assert response.status_code == 500
    assert "xyz123" not in response.json()["detail"]  # internal detail didn't leak
    assert "ffmpeg" not in response.json()["detail"].lower()


def test_guardian_alert_accepts_valid_phone():
    response = client.post(
        "/guardian-alert",
        json={"message_id": "abc", "category": "kyc_scam", "risk_percent": 90,
              "guardian_contact": "+919876543210"},
    )
    assert response.status_code == 200


def test_guardian_alert_accepts_valid_email():
    response = client.post(
        "/guardian-alert",
        json={"message_id": "abc", "category": "kyc_scam", "risk_percent": 90,
              "guardian_contact": "family@example.com"},
    )
    assert response.status_code == 200


def test_guardian_alert_rejects_garbage_contact():
    response = client.post(
        "/guardian-alert",
        json={"message_id": "abc", "category": "kyc_scam", "risk_percent": 90,
              "guardian_contact": "not a real contact!!"},
    )
    assert response.status_code == 422  # Pydantic validation error


def test_unhandled_exception_returns_clean_response(monkeypatch):
    """The global exception handler should catch anything unexpected and
    never leak a raw traceback to the client."""
    from fastapi.testclient import TestClient as TC
    # raise_server_exceptions=False is needed here specifically -- TestClient
    # re-raises unhandled exceptions by default (for easier debugging of
    # genuine test failures), which bypasses the exception-handler
    # middleware a real running server actually goes through.
    no_raise_client = TC(app, raise_server_exceptions=False)

    def broken_classify(text, language):
        raise RuntimeError("unexpected internal failure with a fake /etc/secret path")

    monkeypatch.setattr("api.routes.analyze_message.classify", broken_classify)
    response = no_raise_client.post(
        "/analyze-message",
        json={"text": "some message", "language": "english"},
    )
    assert response.status_code == 500
    assert "secret" not in response.json()["detail"]
    assert "Traceback" not in response.text


def test_analyze_message_output_language_differs_from_input_language():
    """
    Gujarati message, but the app wants the explanation in English --
    classification must still run against Gujarati patterns for accuracy,
    while the returned explanation/alert_message come back in English.
    """
    response = client.post(
        "/analyze-message",
        json={
            "text": "તમારું કેવાયસી અપડેટ નથી. તાત્કાલિક તમારો ઓટીપી જણાવો.",
            "language": "gujarati",
            "output_language": "english",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "kyc_scam"  # classification worked correctly on the Gujarati text
    assert body["language"] == "english"   # but response language reflects output_language
    assert body["risk_percent"] > 50


def test_analyze_message_output_language_defaults_to_language_when_omitted():
    """Old callers who never send output_language should see identical behavior to before."""
    response = client.post(
        "/analyze-message",
        json={"text": "Your KYC is pending, verify your KYC immediately", "language": "english"},
    )
    assert response.status_code == 200
    assert response.json()["language"] == "english"


def test_analyze_call_output_language_differs_from_detected(monkeypatch):
    """Hindi call, but output_language=english should return the explanation in English."""
    def fake_transcribe(path):
        return {
            "text": "Your KYC is pending, account will be blocked, share your OTP immediately",
            "whisper_language_code": "hi",
            "language": "hindi",
        }

    monkeypatch.setattr("api.routes.analyze_call.transcribe_audio", fake_transcribe)
    response = client.post(
        "/analyze-call",
        files={"audio": ("test.wav", b"fake audio bytes", "audio/wav")},
        data={"output_language": "english"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "kyc_scam"
    assert body["language"] == "english"


def test_analyze_call_rejects_invalid_output_language():
    response = client.post(
        "/analyze-call",
        files={"audio": ("test.wav", b"fake audio bytes", "audio/wav")},
        data={"output_language": "french"},
    )
    assert response.status_code == 400