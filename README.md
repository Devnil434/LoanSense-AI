# LoanSense AI

**AI-powered Loan Approval & Credit Risk Assessment Platform**

A full-stack FinTech MVP: applicants submit a loan application and get an
instant, explainable decision — an ML-driven approve/reject call, a
transparent 0–100 credit risk score, a SHAP-powered breakdown of *why*,
and concrete recommendations to improve their odds.

Built as a portfolio-grade demonstration of ML engineering, explainable
AI, REST API design, and modern full-stack development.

---

## Features

- **Loan approval prediction** — Logistic Regression, Random Forest, and
  XGBoost are trained and benchmarked; the best-performing model (by
  ROC-AUC) is automatically selected and served.
- **0–100 Credit Risk Score** — a transparent, rule-based score
  (independent of the ML model) built from income, debt, savings, credit
  history, employment, and loan terms, with a full points breakdown.
- **Explainable AI** — SHAP values surface the top positive and negative
  factors behind every decision, in plain language.
- **Smart recommendations** — rule-based, actionable suggestions when an
  application is rejected or high-risk.
- **Analytics dashboard** — approval trends, risk distribution, average
  loan size, and live model performance metrics.
- **Production-shaped backend** — JWT auth, input validation, structured
  logging, Swagger docs, and a cloud-Postgres-ready data layer.

## Tech stack

| Layer      | Technology |
|------------|------------|
| Frontend   | Next.js 15 (App Router), TypeScript, Tailwind CSS, React Hook Form, Zod, Recharts, Framer Motion |
| Backend    | FastAPI, Python 3.12, Pydantic, SQLAlchemy |
| ML         | Scikit-learn, XGBoost, Pandas, NumPy, SHAP, Joblib |
| Database   | PostgreSQL (Neon / Supabase / Aiven), SQLite fallback for local dev |
| Deployment | Vercel (frontend), Render (backend), Neon (database), Docker Compose (local) |

## Quickstart

```bash
# 1. Train the model (one-time)
cd ml && pip install -r ../backend/requirements.txt
python generate_dataset.py && python train.py

# 2. Backend
cd ../backend && pip install -r requirements.txt
uvicorn app.main:app --reload
# → http://localhost:8000/docs

# 3. Frontend (new terminal)
cd ../frontend && npm install && npm run dev
# → http://localhost:3000

# 4. (Optional) seed demo data for the dashboard
cd ../backend && python -m app.seed
```

Or, with Docker:

```bash
docker compose up --build
```

Full setup details: [`docs/ENVIRONMENT_SETUP.md`](docs/ENVIRONMENT_SETUP.md)

## Running the backend

```bash
cd backend
uvicorn app.main:app --reload
```

Swagger UI at `/docs`, ReDoc at `/redoc`.

## Running the frontend

```bash
cd frontend
npm run dev
```

## Model training

```bash
cd ml
python generate_dataset.py   # synthetic Kaggle-schema dataset (see docs/ML_PIPELINE.md)
python train.py              # trains + evaluates LR/RF/XGBoost, saves the winner
```

See [`docs/ML_PIPELINE.md`](docs/ML_PIPELINE.md) for the full pipeline
explanation, including how to plug in the real Kaggle dataset.

## Deployment

Deployable to **Vercel + Render + Neon PostgreSQL** with no code changes —
see [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for step-by-step instructions.

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design and key decisions
- [`docs/API.md`](docs/API.md) — full endpoint reference with examples
- [`docs/ML_PIPELINE.md`](docs/ML_PIPELINE.md) — training pipeline explained
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — Vercel/Render/Neon deployment guide
- [`docs/ENVIRONMENT_SETUP.md`](docs/ENVIRONMENT_SETUP.md) — local dev setup
- [`docs/FOLDER_STRUCTURE.md`](docs/FOLDER_STRUCTURE.md) — full repo layout
- [`database/SCHEMA.md`](database/SCHEMA.md) — table definitions and relationships

## Testing

```bash
cd backend
pytest app/tests/ -v
```

Covers the prediction API (success + validation failures) and the risk
score engine (low-risk and high-risk profile assertions, score bounds).

## Screenshots

_Add screenshots of the landing page, application form, prediction result,
and dashboard here once deployed — e.g. `docs/screenshots/landing.png`._

## Security

- JWT-based authentication (`/auth/register`, `/auth/login`) — optional on
  `/predict` so the demo stays frictionless, but ties applications to a
  user account when a token is supplied.
- Passwords hashed with bcrypt (via the `bcrypt` library directly).
- All request bodies validated with Pydantic (type, range, and enum
  constraints — see `backend/app/schemas/schemas.py`).
- CORS restricted via `CORS_ORIGINS` environment variable.
- Credentials and secrets loaded exclusively from environment variables —
  never hardcoded.
- SQLAlchemy's parameterized queries prevent SQL injection by construction.

## Honest notes on scope

This environment couldn't reach `kaggle.com` to download the real Loan
Prediction dataset (only package registries are network-accessible here),
so `ml/generate_dataset.py` produces a schema-identical synthetic dataset
as a documented fallback — see [`docs/ML_PIPELINE.md`](docs/ML_PIPELINE.md)
for exactly how to swap in the real CSV. Every other piece (backend API,
risk engine, SHAP explanations, frontend, tests) has been run and verified
end-to-end in this repository, not just written.

## Future improvements

- What-if loan simulator (live sliders re-querying `/predict`)
- Downloadable PDF prediction reports
- Per-user recent application history view (backend already stores the
  `user_id` link; a `GET /applications` endpoint would surface it)
- Alembic migrations for schema evolution in production
- Model retraining pipeline triggered by drift monitoring

## License

MIT — free to use for portfolio, learning, or as a starting point for a
real project.
