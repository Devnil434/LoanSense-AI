# Architecture Overview

## System diagram (textual)

```
┌─────────────────┐        HTTPS/JSON        ┌──────────────────┐
│   Next.js 15     │ ───────────────────────▶ │    FastAPI       │
│  (Vercel)        │ ◀─────────────────────── │   (Render)       │
│                   │                          │                  │
│  App Router pages │                          │  /predict        │
│  React Hook Form  │                          │  /risk-score     │
│  Recharts         │                          │  /metrics        │
│  Framer Motion    │                          │  /health         │
└─────────────────┘                          │  /auth/*         │
                                               └────────┬─────────┘
                                                        │
                                     ┌──────────────────┼──────────────────┐
                                     │                  │                  │
                             ┌───────▼───────┐  ┌───────▼───────┐  ┌───────▼───────┐
                             │  ML artifact   │  │  Risk engine  │  │  PostgreSQL   │
                             │ loan_model     │  │ (rule-based,  │  │  (Neon)       │
                             │ .joblib        │  │  0-100 score) │  │               │
                             │ (LR/RF/XGB +   │  └───────────────┘  │ users         │
                             │  SHAP)         │                     │ loan_apps     │
                             └────────────────┘                     │ predictions   │
                                                                     └───────────────┘
```

## Design decisions

**Two independent scoring systems.** The ML classifier (`/predict`) answers
"will this applicant likely repay, based on historical patterns?" The rule
engine (`/risk-score` and the `risk_score` field returned by `/predict`)
answers "how much objective, explainable risk does this specific applicant
profile carry?" Keeping these independent means the risk score is auditable
even when the underlying ML model changes, and a reviewer never has to
trust a black box for the number that matters most to compliance.

**Model selection is automatic and data-driven.** `ml/train.py` trains
Logistic Regression, Random Forest, and XGBoost on the same train/test
split and selects the highest ROC-AUC model. Whichever wins is the one
serialized into `loan_model.joblib` and used in production — there is no
hardcoded "always use XGBoost" assumption.

**SHAP runs against the actual winning model.** Rather than always using
`TreeExplainer`, `train.py` picks `LinearExplainer` for logistic regression
and `TreeExplainer` for tree-based models, so explanations are always
faithful to whichever model is actually serving predictions.

**Public-friendly auth.** `/predict` and `/risk-score` work without
authentication (so recruiters/reviewers can try the live demo instantly),
but if a bearer token *is* provided, the application is associated with
that user's account for history tracking. `/auth/register` and
`/auth/login` issue JWTs for this optional flow.

**Database is swappable with zero code changes.** `DATABASE_URL` defaults
to a local SQLite file so the project runs immediately after cloning. Point
it at any Postgres connection string (Neon, Supabase, Aiven) and the same
SQLAlchemy models and Alembic-style `Base.metadata.create_all` bootstrap
work unchanged.

## Request lifecycle for `POST /predict`

1. Pydantic validates the incoming `LoanApplicationInput` payload.
2. `LoanModel.predict()` builds the feature row, applies the same
   scaler/encoding used at training time, and returns a decision +
   probability + SHAP factors.
3. `risk_score.compute_risk_score()` independently computes the 0–100 score
   from seven weighted, named factors.
4. `generate_recommendations()` produces rule-based next steps if the
   application was rejected or scored above 40.
5. The application and prediction are persisted to Postgres/SQLite.
6. A single `PredictionResponse` combining all four outputs is returned.
