import sys
from pathlib import Path

from fastapi import APIRouter

from app.schemas.schemas import LoanApplicationInput, RiskFactorOut, RiskScoreResponse

sys.path.append(str(Path(__file__).resolve().parents[3] / "ml"))
from risk_score import compute_risk_score  # noqa: E402

router = APIRouter(tags=["Risk Score"])


@router.post("/risk-score", response_model=RiskScoreResponse)
def risk_score(payload: LoanApplicationInput):
    data = payload.model_dump()
    employment_status = "self_employed" if data["self_employed"] == "Yes" else "salaried"

    result = compute_risk_score(
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

    return RiskScoreResponse(
        score=result.score,
        category=result.category,
        factors=[RiskFactorOut(**f.__dict__) for f in result.factors],
    )
