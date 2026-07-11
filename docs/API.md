# API Documentation

Base URL (local): `http://localhost:8000/api/v1`
Interactive Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`

All endpoints return JSON. Validation errors return HTTP 422 with a
Pydantic-style error body.

---

## `POST /predict`

Runs both the ML approval model and the risk-score engine, persists the
application + prediction, and returns a full explanation.

**Auth:** optional. If an `Authorization: Bearer <token>` header is
supplied, the application is linked to that user.

**Request body**

```json
{
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
  "savings": 25000
}
```

**Response `200`**

```json
{
  "application_id": "d956dc32-...",
  "decision": "Approved",
  "confidence": 0.9846,
  "approval_probability": 0.9846,
  "model_used": "logistic_regression",
  "risk_score": 9,
  "risk_category": "Excellent",
  "risk_factors": [ { "name": "Credit History", "points": 0, "reason": "Good repayment history" } ],
  "top_positive_factors": [ { "feature": "TotalIncome", "impact": 1.495, "direction": "positive", "human_readable": "Total household income" } ],
  "top_negative_factors": [ { "feature": "Savings", "impact": -0.26, "direction": "negative", "human_readable": "Savings balance" } ],
  "explanation_summary": "The applicant has a strong approval probability, primarily driven by total household income, applicant income, credit history.",
  "recommendations": ["Your application profile is strong — maintaining your current credit history and income stability will keep future applications competitive."],
  "created_at": "2026-07-11T04:04:56Z"
}
```

**Errors**
- `422` — invalid input (e.g. negative income, age outside 18–100)
- `503` — the trained model artifact is missing (run `python ml/train.py`)

---

## `POST /risk-score`

Runs only the rule-based 0–100 risk score engine, independent of the ML
model. Same request schema as `/predict`; no auth required; nothing is
persisted.

**Response `200`**

```json
{
  "score": 9,
  "category": "Excellent",
  "factors": [
    { "name": "Income-to-Loan Ratio", "points": 0, "reason": "Total income covers 53.3% of the requested loan amount" },
    { "name": "Credit History", "points": 0, "reason": "Good repayment history" },
    { "name": "Employment Stability", "points": 0, "reason": "Employment status: salaried" },
    { "name": "Debt-to-Income Ratio", "points": 0, "reason": "Existing debt is 6.2% of total income" },
    { "name": "Savings Buffer", "points": 4, "reason": "Savings represent 13.3% of the loan amount" },
    { "name": "Loan Term Length", "points": 5, "reason": "360-month repayment term" },
    { "name": "Applicant Age Band", "points": 0, "reason": "Applicant age: 34" }
  ]
}
```

---

## `GET /metrics`

Aggregated analytics across every application ever submitted, plus the
current model's offline evaluation metrics.

**Response `200`**

```json
{
  "total_applications": 40,
  "approved_count": 35,
  "rejected_count": 5,
  "approval_rate": 87.5,
  "average_loan_amount": 279.88,
  "average_risk_score": 33.12,
  "risk_distribution": { "Excellent": 14, "Low Risk": 16, "Moderate Risk": 5, "High Risk": 5 },
  "model_metrics": {
    "best_model": "logistic_regression",
    "all_results": {
      "logistic_regression": { "accuracy": 0.795, "precision": 0.8203, "recall": 0.9388, "f1_score": 0.8755, "roc_auc": 0.6845 },
      "random_forest": { "accuracy": 0.803, "precision": 0.8127, "recall": 0.9661, "f1_score": 0.8828, "roc_auc": 0.6731 },
      "xgboost": { "accuracy": 0.796, "precision": 0.814, "recall": 0.9518, "f1_score": 0.8776, "roc_auc": 0.6691 }
    },
    "n_train": 4000,
    "n_test": 1000
  }
}
```

---

## `GET /health`

Liveness/readiness probe for deployment platforms (Render, Docker, k8s).

```json
{ "status": "ok", "model_loaded": true, "model_name": "logistic_regression", "database": "connected" }
```

---

## `POST /auth/register`

```json
// Request
{ "email": "jane@example.com", "password": "at-least-8-chars", "full_name": "Jane Doe" }

// Response 201
{ "access_token": "eyJ...", "token_type": "bearer" }
```

## `POST /auth/login`

```json
// Request
{ "email": "jane@example.com", "password": "at-least-8-chars" }

// Response 200
{ "access_token": "eyJ...", "token_type": "bearer" }
```

Use the returned token as `Authorization: Bearer <access_token>` on
`/predict` to associate applications with the account.
