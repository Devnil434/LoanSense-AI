from __future__ import annotations

from pathlib import Path
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

from app.core.config import get_settings

settings = get_settings()

FEATURE_LABELS = {
    "Gender": "Gender",
    "Married": "Marital status",
    "Dependents": "Number of dependents",
    "Education": "Education level",
    "Self_Employed": "Self-employment status",
    "Property_Area": "Property area",
    "ApplicantIncome": "Applicant income",
    "CoapplicantIncome": "Co-applicant income",
    "LoanAmount": "Loan amount requested",
    "Loan_Amount_Term": "Loan repayment term",
    "Credit_History": "Credit history",
    "Age": "Applicant age",
    "ExistingDebt": "Existing debt",
    "Savings": "Savings balance",
    "TotalIncome": "Total household income",
    "IncomeToLoanRatio": "Income-to-loan ratio",
    "DebtToIncomeRatio": "Debt-to-income ratio",
}


class LoanModel:
    def __init__(self, model_path: str):
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Trained model artifact not found at {path.resolve()}. "
                f"Run `python ml/train.py` first to generate it."
            )
        artifact = joblib.load(path)
        self.model = artifact["model"]
        self.model_name = artifact["model_name"]
        self.scaler = artifact["scaler"]
        self.uses_scaler = artifact["uses_scaler"]
        self.feature_cols = artifact["feature_cols"]
        self.category_maps = artifact["category_maps"]
        self.explainer = artifact["explainer"]
        self.metrics = artifact["metrics"]

    def _build_row(self, data: dict) -> pd.DataFrame:
        row = {
            "Gender": self.category_maps["Gender"].get(data["gender"], 0),
            "Married": self.category_maps["Married"].get(data["married"], 0),
            "Dependents": self.category_maps["Dependents"].get(data["dependents"], 0),
            "Education": self.category_maps["Education"].get(data["education"], 0),
            "Self_Employed": self.category_maps["Self_Employed"].get(data["self_employed"], 0),
            "Property_Area": self.category_maps["Property_Area"].get(data["property_area"], 0),
            "ApplicantIncome": data["applicant_income"],
            "CoapplicantIncome": data["coapplicant_income"],
            "LoanAmount": data["loan_amount"],
            "Loan_Amount_Term": data["loan_amount_term"],
            "Credit_History": data["credit_history"],
            "Age": data["age"],
            "ExistingDebt": data["existing_debt"],
            "Savings": data["savings"],
        }
        total_income = row["ApplicantIncome"] + row["CoapplicantIncome"]
        row["TotalIncome"] = total_income
        row["IncomeToLoanRatio"] = total_income / (row["LoanAmount"] * 1000 + 1)
        row["DebtToIncomeRatio"] = row["ExistingDebt"] / (total_income + 1)

        df = pd.DataFrame([row])[self.feature_cols]
        return df

    def predict(self, data: dict) -> dict:
        df = self._build_row(data)
        X = self.scaler.transform(df) if self.uses_scaler else df

        proba = float(self.model.predict_proba(X)[0][1])
        decision = "Approved" if proba >= 0.5 else "Rejected"
        confidence = proba if decision == "Approved" else 1 - proba

        shap_values = self.explainer.shap_values(X)
        if isinstance(shap_values, list):
            shap_row = np.array(shap_values[1][0])
        else:
            sv = np.array(shap_values)
            shap_row = sv[0, :, 1] if sv.ndim == 3 else sv[0]

        contributions = list(zip(self.feature_cols, shap_row, df.iloc[0].to_list()))
        contributions.sort(key=lambda t: abs(t[1]), reverse=True)

        positives = [c for c in contributions if c[1] > 0][:3]
        negatives = [c for c in contributions if c[1] < 0][:3]

        def fmt(items, direction):
            out = []
            for feat, impact, _val in items:
                out.append(
                    {
                        "feature": feat,
                        "impact": round(float(impact), 4),
                        "direction": direction,
                        "human_readable": FEATURE_LABELS.get(feat, feat),
                    }
                )
            return out

        top_positive = fmt(positives, "positive")
        top_negative = fmt(negatives, "negative")

        summary = self._build_summary(decision, top_positive, top_negative)

        return {
            "decision": decision,
            "approval_probability": round(proba, 4),
            "confidence": round(confidence, 4),
            "model_used": self.model_name,
            "top_positive_factors": top_positive,
            "top_negative_factors": top_negative,
            "explanation_summary": summary,
        }

    @staticmethod
    def _build_summary(decision: str, positives: list[dict], negatives: list[dict]) -> str:
        if decision == "Approved":
            reasons = ", ".join(p["human_readable"].lower() for p in positives) or "overall applicant profile"
            return f"The applicant has a strong approval probability, primarily driven by {reasons}."
        reasons = ", ".join(n["human_readable"].lower() for n in negatives) or "overall applicant profile"
        return f"The application shows elevated rejection risk, primarily driven by {reasons}."


@lru_cache
def get_loan_model() -> LoanModel:
    return LoanModel(settings.ML_MODEL_PATH)
