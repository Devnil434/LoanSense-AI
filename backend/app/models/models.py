import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    applications: Mapped[list["LoanApplication"]] = relationship(back_populates="user")


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=True)

    applicant_name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String)
    married: Mapped[str] = mapped_column(String)
    dependents: Mapped[str] = mapped_column(String)
    education: Mapped[str] = mapped_column(String)
    self_employed: Mapped[str] = mapped_column(String)
    applicant_income: Mapped[float] = mapped_column(Float)
    coapplicant_income: Mapped[float] = mapped_column(Float, default=0)
    loan_amount: Mapped[float] = mapped_column(Float)
    loan_amount_term: Mapped[int] = mapped_column(Integer)
    credit_history: Mapped[int] = mapped_column(Integer)
    property_area: Mapped[str] = mapped_column(String)
    existing_debt: Mapped[float] = mapped_column(Float, default=0)
    savings: Mapped[float] = mapped_column(Float, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    user: Mapped["User"] = relationship(back_populates="applications")
    predictions: Mapped[list["PredictionRecord"]] = relationship(back_populates="application")


class PredictionRecord(Base):
    __tablename__ = "prediction_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    application_id: Mapped[str] = mapped_column(String, ForeignKey("loan_applications.id"))

    decision: Mapped[str] = mapped_column(String)  # "Approved" | "Rejected"
    confidence: Mapped[float] = mapped_column(Float)
    approval_probability: Mapped[float] = mapped_column(Float)
    model_name: Mapped[str] = mapped_column(String)

    risk_score: Mapped[int] = mapped_column(Integer)
    risk_category: Mapped[str] = mapped_column(String)

    shap_explanation: Mapped[dict] = mapped_column(JSON)
    recommendations: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    application: Mapped["LoanApplication"] = relationship(back_populates="predictions")
