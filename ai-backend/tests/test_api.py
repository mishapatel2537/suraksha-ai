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
