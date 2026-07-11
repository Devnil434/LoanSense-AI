"""
seed.py — Populate the database with sample loan applications + predictions
so the Analytics Dashboard has data to display immediately after setup.

Run from backend/:
    python -m app.seed
"""

import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "ml"))

from app.core.database import Base, SessionLocal, engine
from app.ml.inference import get_loan_model
from app.ml.recommendations import generate_recommendations
from app.models.models import LoanApplication, PredictionRecord
from risk_score import compute_risk_score  # noqa: E402

random.seed(7)

SAMPLE_NAMES = [
    "Aditi Sharma", "Rohan Mehta", "Priya Nair", "Vikram Rao", "Sneha Kapoor",
    "Arjun Verma", "Isha Gupta", "Karan Malhotra", "Ananya Iyer", "Nikhil Joshi",
    "Meera Pillai", "Siddharth Desai", "Kavya Reddy", "Rahul Chatterjee", "Divya Menon",
]


def random_application():
    gender = random.choice(["Male", "Female"])
    married = random.choice(["Yes", "No"])
    return {
        "applicant_name": random.choice(SAMPLE_NAMES),
        "age": random.randint(22, 60),
        "gender": gender,
        "married": married,
        "dependents": random.choice(["0", "1", "2", "3+"]),
        "education": random.choice(["Graduate", "Not Graduate"]),
        "self_employed": random.choice(["Yes", "No"]),
        "applicant_income": round(random.uniform(18000, 150000), 2),
        "coapplicant_income": round(random.uniform(0, 40000), 2) if married == "Yes" else 0,
        "loan_amount": round(random.uniform(50, 500), 2),
        "loan_amount_term": random.choice([360, 180, 240, 120, 84]),
        "credit_history": random.choice([1, 1, 1, 0]),
        "property_area": random.choice(["Urban", "Semiurban", "Rural"]),
        "existing_debt": round(random.uniform(0, 20000), 2),
        "savings": round(random.uniform(0, 60000), 2),
    }


def main(n: int = 40):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    model = get_loan_model()

    created = 0
    for _ in range(n):
        data = random_application()
        ml_result = model.predict(data)

        employment_status = "self_employed" if data["self_employed"] == "Yes" else "salaried"
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

        application = LoanApplication(**data)
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
        created += 1

    db.close()
    print(f"Seeded {created} sample loan applications + predictions.")


if __name__ == "__main__":
    main()
