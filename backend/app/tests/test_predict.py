import pytest
from fastapi.testclient import TestClient

from app.main import app

VALID_PAYLOAD = {
    "applicant_name": "Jane Doe",
    "age": 30,
    "gender": "Female",
    "married": "No",
    "dependents": "0",
    "education": "Graduate",
    "self_employed": "No",
    "applicant_income": 72000,
    "coapplicant_income": 0,
    "loan_amount": 120,
    "loan_amount_term": 360,
    "credit_history": 1,
    "property_area": "Semiurban",
    "existing_debt": 3000,
    "savings": 25000,
}


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("ok", "degraded")
    assert "model_loaded" in body


def test_predict_success(client):
    r = client.post("/api/v1/predict", json=VALID_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["decision"] in ("Approved", "Rejected")
    assert 0 <= body["risk_score"] <= 100
    assert body["risk_category"] in (
        "Excellent",
        "Low Risk",
        "Moderate Risk",
        "High Risk",
        "Very High Risk",
    )
    assert 0 <= body["approval_probability"] <= 1
    assert len(body["recommendations"]) >= 1


def test_predict_rejects_invalid_input(client):
    bad_payload = dict(VALID_PAYLOAD)
    bad_payload["age"] = 5  # below allowed minimum
    r = client.post("/api/v1/predict", json=bad_payload)
    assert r.status_code == 422


def test_predict_rejects_negative_income(client):
    bad_payload = dict(VALID_PAYLOAD)
    bad_payload["applicant_income"] = -100
    r = client.post("/api/v1/predict", json=bad_payload)
    assert r.status_code == 422
