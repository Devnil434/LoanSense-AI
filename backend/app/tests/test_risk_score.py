import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


BASE = {
    "applicant_name": "John Smith",
    "age": 45,
    "gender": "Male",
    "married": "Yes",
    "dependents": "2",
    "education": "Graduate",
    "self_employed": "No",
    "applicant_income": 90000,
    "coapplicant_income": 20000,
    "loan_amount": 100,
    "loan_amount_term": 180,
    "credit_history": 1,
    "property_area": "Urban",
    "existing_debt": 1000,
    "savings": 40000,
}


def test_low_risk_profile_scores_low(client):
    r = client.post("/api/v1/risk-score", json=BASE)
    assert r.status_code == 200
    body = r.json()
    assert body["score"] <= 40
    assert body["category"] in ("Excellent", "Low Risk")
    assert len(body["factors"]) == 7


def test_high_risk_profile_scores_high(client):
    risky = dict(BASE)
    risky.update(
        {
            "applicant_income": 15000,
            "coapplicant_income": 0,
            "loan_amount": 500,
            "credit_history": 0,
            "existing_debt": 12000,
            "savings": 500,
            "self_employed": "Yes",
        }
    )
    r = client.post("/api/v1/risk-score", json=risky)
    assert r.status_code == 200
    body = r.json()
    assert body["score"] >= 60
    assert body["category"] in ("High Risk", "Very High Risk")


def test_score_is_bounded(client):
    r = client.post("/api/v1/risk-score", json=BASE)
    body = r.json()
    assert 0 <= body["score"] <= 100
