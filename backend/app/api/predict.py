import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.ml.inference import get_loan_model
from app.ml.recommendations import generate_recommendations
from app.models.models import LoanApplication, PredictionRecord
from app.schemas.schemas import LoanApplicationInput, PredictionResponse, RiskFactorOut

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[3] / "ml"))
from risk_score import compute_risk_score  # noqa: E402

router = APIRouter(tags=["Prediction"])
logger = logging.getLogger("loansense.predict")


@router.post("/predict", response_model=PredictionResponse)
def predict_loan(
    payload: LoanApplicationInput,
    db: Session = Depends(get_db),
    user_id: str | None = Depends(get_current_user_optional),
):
    try:
        model = get_loan_model()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    data = payload.model_dump()

    try:
        ml_result = model.predict(data)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Model inference failed: {exc}")

    employment_status = "unemployed" if False else ("self_employed" if data["self_employed"] == "Yes" else "salaried")

    risk_result = compute_risk_score(
        annual_income=data["applicant_income"],
        coapplicant_income=data["coapplicant_income"],
        loan_amount=data["loan_amount"],
        loan_term_months=data["loan_amount_term"],
        credit_history=data["credit_history"],
        employment_status=employment_status,
        existing_debt=data["existing_debt"],
        savings=data["savings"],
        age=data["age"],
    )

    recommendations = generate_recommendations(
        data=data, decision=ml_result["decision"], risk_score=risk_result.score
    )

    application = LoanApplication(user_id=user_id, **data)
    db.add(application)
    db.commit()
    db.refresh(application)

    record = PredictionRecord(
        application_id=application.id,
        decision=ml_result["decision"],
        confidence=ml_result["confidence"],
        approval_probability=ml_result["approval_probability"],
        model_name=ml_result["model_used"],
        risk_score=risk_result.score,
        risk_category=risk_result.category,
        shap_explanation={
            "top_positive_factors": ml_result["top_positive_factors"],
            "top_negative_factors": ml_result["top_negative_factors"],
        },
        recommendations={"items": recommendations},
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return PredictionResponse(
        application_id=application.id,
        decision=ml_result["decision"],
        confidence=ml_result["confidence"],
        approval_probability=ml_result["approval_probability"],
        model_used=ml_result["model_used"],
        risk_score=risk_result.score,
        risk_category=risk_result.category,
        risk_factors=[RiskFactorOut(**f.__dict__) for f in risk_result.factors],
        top_positive_factors=ml_result["top_positive_factors"],
        top_negative_factors=ml_result["top_negative_factors"],
        explanation_summary=ml_result["explanation_summary"],
        recommendations=recommendations,
        created_at=record.created_at,
    )
