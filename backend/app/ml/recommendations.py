from __future__ import annotations


def generate_recommendations(*, data: dict, decision: str, risk_score: int) -> list[str]:
    """Generate rule-based, actionable suggestions for the applicant."""
    recs: list[str] = []

    total_income = data["applicant_income"] + data["coapplicant_income"]
    loan_amount_full = data["loan_amount"] * 1000
    income_to_loan = total_income / (loan_amount_full + 1)
    dti = data["existing_debt"] / (total_income + 1)

    if decision == "Rejected" or risk_score > 40:
        if income_to_loan < 0.3:
            recs.append("Consider reducing the requested loan amount to better match your income level.")
        if data["credit_history"] == 0:
            recs.append("Build or improve your credit history before reapplying — this is one of the strongest approval factors.")
        if dti > 0.25:
            recs.append("Pay down existing debt to lower your debt-to-income ratio.")
        if total_income < 40000:
            recs.append("Increasing verifiable annual income (or adding a co-applicant) would improve approval odds.")
        if data["loan_amount_term"] >= 300:
            recs.append("Choosing a shorter repayment period can reduce perceived long-term risk.")
        if data["savings"] < loan_amount_full * 0.05:
            recs.append("Building a larger savings buffer improves your risk profile as a financial safety net.")

    if not recs:
        recs.append("Your application profile is strong — maintaining your current credit history and income stability will keep future applications competitive.")

    return recs[:5]
