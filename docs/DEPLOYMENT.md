# Deployment Guide

Target stack: **Vercel** (frontend) + **Render** (backend) + **Neon
PostgreSQL** (database). All three have usable free tiers.

## 1. Database — Neon PostgreSQL

1. Create an account at [neon.tech](https://neon.tech) and a new project.
2. Copy the pooled connection string (starts with `postgresql://...`).
3. Keep it handy for step 2.

Supabase or Aiven Postgres work as drop-in replacements — just swap the
connection string; no code changes needed.

## 2. Backend — Render

1. Push this repository to GitHub.
2. In Render, create a **New Web Service** pointed at the repo.
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Environment variables:
   - `DATABASE_URL` — the Neon connection string from step 1
   - `JWT_SECRET_KEY` — a long random string
   - `CORS_ORIGINS` — `["https://your-frontend.vercel.app"]`
   - `ML_MODEL_PATH` — `../ml/models/loan_model.joblib`
7. **Important:** the `ml/` directory (including the trained
   `loan_model.joblib`) must be included in the deployed repo — Render
   builds from the repo root, and the backend's relative `ML_MODEL_PATH`
   expects `ml/` to be a sibling of `backend/`. Either commit the trained
   artifact, or add a Render build step that runs
   `python ml/train.py` before starting the service.
8. Once deployed, verify `https://your-backend.onrender.com/api/v1/health`
   returns `{"status": "ok", ...}`.

Alternatively, deploy via the included `backend/Dockerfile` — Render, Fly.io,
and Railway all support "deploy from Dockerfile" directly.

## 3. Frontend — Vercel

1. Import the same GitHub repo into Vercel.
2. Root directory: `frontend`
3. Framework preset: Next.js (auto-detected)
4. Environment variable:
   - `NEXT_PUBLIC_API_BASE_URL` — `https://your-backend.onrender.com/api/v1`
5. Deploy. Vercel builds and serves the Next.js App Router project
   automatically — no further configuration needed.

## 4. Local development (Docker Compose)

For a fully local stack (Postgres + backend + frontend) without any cloud
accounts:

```bash
cp .env.example backend/.env      # then edit values as needed
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- Postgres: localhost:5432 (user/pass/db: `loansense`)

## 5. Seeding demo data

After the backend is up (locally or on Render), seed sample applications
so the dashboard isn't empty:

```bash
cd backend
python -m app.seed
```

## Free-tier notes

- **Neon** free tier: 0.5 GB storage, auto-suspends when idle — perfectly
  fine for a portfolio project; the first request after idle may be slow
  ("cold start").
- **Render** free web services also spin down after inactivity; the first
  request after a cold start can take 30–60 seconds.
- **Vercel** hobby tier has no meaningful limits for a project this size.
