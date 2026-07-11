# Environment Setup

## Prerequisites

- Python 3.12+
- Node.js 20+
- npm 10+
- (Optional) Docker + Docker Compose for one-command local stack

## 1. Clone and configure

```bash
git clone <your-fork-url> LoanSense-AI
cd LoanSense-AI
cp .env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Edit `backend/.env`:
- Leave `DATABASE_URL` unset (or delete the line) to use local SQLite —
  the project runs immediately with zero external services.
- Set it to a Neon/Supabase/Aiven Postgres URL for a "real" cloud setup.

## 2. Train the ML model (required once)

```bash
cd ml
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r ../backend/requirements.txt
python generate_dataset.py   # generates a synthetic Kaggle-schema dataset
python train.py              # trains LR/RF/XGBoost, saves the best one
```

This produces `ml/models/loan_model.joblib`, which the backend loads at
startup. **The backend will return `503` on `/predict` until this file
exists.**

## 3. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # if not already active
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive Swagger UI.

Optional — seed sample data for the dashboard:

```bash
python -m app.seed
```

## 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`.

## 5. Running tests

```bash
cd backend
pytest app/tests/ -v
```

## Troubleshooting

- **`FileNotFoundError: Trained model artifact not found`** — run
  `python ml/train.py` from step 2.
- **CORS errors in the browser console** — check `CORS_ORIGINS` in
  `backend/.env` includes your frontend's origin.
- **`no such table` SQLite errors when calling the API directly via
  scripts** — make sure you're going through the FastAPI app (which runs
  `Base.metadata.create_all` on startup) rather than importing models in
  isolation.
