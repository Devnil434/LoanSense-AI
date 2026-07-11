# Folder Structure

```text
LoanSense-AI/
├── frontend/                      # Next.js 15 App Router + TypeScript
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Landing page (hero, features, workflow, CTA)
│   │   │   ├── layout.tsx         # Root layout (fonts, navbar, footer, toasts)
│   │   │   ├── globals.css        # Design tokens, glassmorphism utilities
│   │   │   ├── application/
│   │   │   │   └── page.tsx       # Loan application form
│   │   │   ├── predict/
│   │   │   │   └── page.tsx       # Prediction result + SHAP explanation
│   │   │   └── dashboard/
│   │   │       └── page.tsx       # Analytics dashboard (Recharts)
│   │   ├── components/
│   │   │   ├── navbar.tsx, footer.tsx
│   │   │   └── ui/                # Button, Card, RiskGauge, Field, Skeleton, Toast
│   │   ├── lib/                   # api.ts, utils.ts, validation.ts (Zod schemas)
│   │   └── types/                 # Shared TypeScript interfaces
│   ├── package.json
│   ├── tailwind.config.ts
│   └── Dockerfile
│
├── backend/                       # FastAPI + Python 3.12
│   ├── app/
│   │   ├── main.py                # App entrypoint, CORS, routers, lifespan
│   │   ├── api/                   # auth.py, predict.py, risk.py, metrics.py
│   │   ├── core/                  # config.py, database.py, security.py
│   │   ├── models/                # SQLAlchemy models (User, LoanApplication, PredictionRecord)
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── ml/                    # inference.py, recommendations.py
│   │   ├── tests/                 # pytest suite
│   │   └── seed.py                # Sample data seeding script
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── ml/                             # Model training pipeline (standalone, reusable)
│   ├── generate_dataset.py        # Synthetic Kaggle-schema dataset generator
│   ├── train.py                   # Cleaning, encoding, scaling, training, evaluation
│   ├── risk_score.py              # Rule-based 0-100 credit risk score engine
│   ├── data/
│   │   ├── raw/                   # loan_prediction.csv (generated or real Kaggle CSV)
│   │   └── processed/             # featured_dataset.csv
│   └── models/
│       ├── loan_model.joblib      # Trained model + scaler + SHAP explainer bundle
│       └── metrics.json           # Offline evaluation metrics
│
├── database/
│   └── SCHEMA.md                  # Entity-relationship notes for the SQLAlchemy models
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── ML_PIPELINE.md
│   ├── DEPLOYMENT.md
│   ├── ENVIRONMENT_SETUP.md
│   └── FOLDER_STRUCTURE.md        # (this file)
│
├── docker-compose.yml              # Full local stack: Postgres + backend + frontend
├── .env.example                    # Root reference for all environment variables
└── README.md
```
