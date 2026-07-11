from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Loan Application ----------
class LoanApplicationInput(BaseModel):
    applicant_name: str = Field(min_length=2, max_length=120)
    age: int = Field(ge=18, le=100)
    gender: Literal["Male", "Female"]
    married: Literal["Yes", "No"]
    dependents: Literal["0", "1", "2", "3+"]
    education: Literal["Graduate", "Not Graduate"]
    self_employed: Literal["Yes", "No"]
    applicant_income: float = Field(gt=0, description="Annual income in currency units")
    coapplicant_income: float = Field(ge=0, default=0)
    loan_amount: float = Field(gt=0, description="Loan amount requested, in thousands")
    loan_amount_term: int = Field(gt=0, description="Loan term in months")
    credit_history: Literal[0, 1]
    property_area: Literal["Urban", "Semiurban", "Rural"]
    existing_debt: float = Field(ge=0, default=0)
    savings: float = Field(ge=0, default=0)

    @field_validator("applicant_name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


# ---------- Prediction ----------
class ShapFactor(BaseModel):
    feature: str
    impact: float
    direction: Literal["positive", "negative"]
    human_readable: str


class RiskFactorOut(BaseModel):
    name: str
    points: float
    reason: str


class PredictionResponse(BaseModel):
    application_id: str
    decision: Literal["Approved", "Rejected"]
    confidence: float
    approval_probability: float
    model_used: str

    risk_score: int
    risk_category: str
    risk_factors: list[RiskFactorOut]

    top_positive_factors: list[ShapFactor]
    top_negative_factors: list[ShapFactor]
    explanation_summary: str

    recommendations: list[str]
    created_at: datetime


class RiskScoreResponse(BaseModel):
    score: int
    category: str
    factors: list[RiskFactorOut]


# ---------- Metrics / Dashboard ----------
class ModelMetrics(BaseModel):
    best_model: str
    all_results: dict
    n_train: int
    n_test: int


class DashboardMetrics(BaseModel):
    total_applications: int
    approved_count: int
    rejected_count: int
    approval_rate: float
    average_loan_amount: float
    average_risk_score: float
    risk_distribution: dict[str, int]
    model_metrics: ModelMetrics


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str | None = None
    database: str
