import json
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.ml.inference import get_loan_model
from app.models.models import LoanApplication, PredictionRecord
from app.schemas.schemas import DashboardMetrics, HealthResponse, ModelMetrics

router = APIRouter(tags=["Analytics"])
settings = get_settings()


@router.get("/metrics", response_model=DashboardMetrics)
def get_metrics(db: Session = Depends(get_db)):
    total = db.query(func.count(PredictionRecord.id)).scalar() or 0
    approved = (
        db.query(func.count(PredictionRecord.id)).filter(PredictionRecord.decision == "Approved").scalar() or 0
    )
    rejected = total - approved
    avg_loan = db.query(func.avg(LoanApplication.loan_amount)).scalar() or 0.0
    avg_risk = db.query(func.avg(PredictionRecord.risk_score)).scalar() or 0.0

    risk_distribution: dict[str, int] = {}
    rows = (
        db.query(PredictionRecord.risk_category, func.count(PredictionRecord.id))
        .group_by(PredictionRecord.risk_category)
        .all()
    )
    for category, count in rows:
        risk_distribution[category] = count

    model_path = Path(settings.ML_MODEL_PATH).parent / "metrics.json"
    if model_path.exists():
        with open(model_path) as f:
            model_metrics_raw = json.load(f)
    else:
        model_metrics_raw = {"best_model": "unknown", "all_results": {}, "n_train": 0, "n_test": 0}

    return DashboardMetrics(
        total_applications=total,
        approved_count=approved,
        rejected_count=rejected,
        approval_rate=round((approved / total) * 100, 2) if total else 0.0,
        average_loan_amount=round(float(avg_loan), 2),
        average_risk_score=round(float(avg_risk), 2),
        risk_distribution=risk_distribution,
        model_metrics=ModelMetrics(**model_metrics_raw),
    )


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    model_loaded = True
    model_name = None
    try:
        model = get_loan_model()
        model_name = model.model_name
    except FileNotFoundError:
        model_loaded = False

    db_status = "connected"
    try:
        db.execute(func.now() if not settings.DATABASE_URL.startswith("sqlite") else func.datetime("now"))
    except Exception:  # noqa: BLE001
        db_status = "disconnected"

    return HealthResponse(
        status="ok" if model_loaded and db_status == "connected" else "degraded",
        model_loaded=model_loaded,
        model_name=model_name,
        database=db_status,
    )
