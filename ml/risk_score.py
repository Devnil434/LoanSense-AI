"""
risk_score.py — Transparent, rule-based 0-100 Credit Risk Score.

This score is DELIBERATELY independent of the ML approval model. It exists
to give applicants and reviewers a transparent, auditable number that is not
a black box — every point is explainable by a named factor. Lower score =
lower risk (0-20 Excellent ... 81-100 Very High Risk), matching the product
spec.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RiskFactor:
    name: str
    points: float
    reason: str


@dataclass
class RiskScoreResult:
    score: int
    category: str
    factors: list[RiskFactor] = field(default_factory=list)

    def to_dict(self):
        return {
            "score": self.score,
            "category": self.category,
            "factors": [f.__dict__ for f in self.factors],
        }


def _category(score: int) -> str:
    if score <= 20:
        return "Excellent"
    if score <= 40:
        return "Low Risk"
    if score <= 60:
        return "Moderate Risk"
    if score <= 80:
        return "High Risk"
    return "Very High Risk"


def compute_risk_score(
    *,
    annual_income: float,
    coapplicant_income: float,
    loan_amount: float,
    loan_term_months: int,
    credit_history: int,  # 1 = good, 0 = no/poor history
    employment_status: str,  # "salaried" | "self_employed" | "unemployed"
    existing_debt: float,
    savings: float,
    age: int,
) -> RiskScoreResult:
    factors: list[RiskFactor] = []
    total_income = annual_income + coapplicant_income

    # 1. Income-to-loan ratio (0-25 risk points, lower ratio = more points)
    loan_amount_full = loan_amount * 1000  # dataset stores LoanAmount in thousands
    ratio = total_income / (loan_amount_full + 1)
    if ratio >= 0.5:
        pts = 0
    elif ratio >= 0.3:
        pts = 6
    elif ratio >= 0.15:
        pts = 14
    else:
        pts = 25
    factors.append(RiskFactor("Income-to-Loan Ratio", pts, f"Total income covers {ratio:.1%} of the requested loan amount"))

    # 2. Credit history (0-25 points)
    pts = 0 if credit_history == 1 else 25
    factors.append(RiskFactor("Credit History", pts, "Good repayment history" if credit_history == 1 else "No or poor prior credit history"))

    # 3. Employment stability (0-15 points)
    emp_points = {"salaried": 0, "self_employed": 7, "unemployed": 15}
    pts = emp_points.get(employment_status, 10)
    factors.append(RiskFactor("Employment Stability", pts, f"Employment status: {employment_status.replace('_', ' ')}"))

    # 4. Debt-to-income ratio (0-15 points)
    dti = existing_debt / (total_income + 1)
    if dti < 0.1:
        pts = 0
    elif dti < 0.25:
        pts = 6
    elif dti < 0.4:
        pts = 11
    else:
        pts = 15
    factors.append(RiskFactor("Debt-to-Income Ratio", pts, f"Existing debt is {dti:.1%} of total income"))

    # 5. Savings buffer relative to loan (0-10 points)
    savings_ratio = savings / (loan_amount_full + 1)
    if savings_ratio >= 0.2:
        pts = 0
    elif savings_ratio >= 0.08:
        pts = 4
    elif savings_ratio >= 0.02:
        pts = 7
    else:
        pts = 10
    factors.append(RiskFactor("Savings Buffer", pts, f"Savings represent {savings_ratio:.1%} of the loan amount"))

    # 6. Loan term (0-5 points; very long terms carry slightly more risk)
    pts = 5 if loan_term_months >= 360 else (2 if loan_term_months >= 180 else 0)
    factors.append(RiskFactor("Loan Term Length", pts, f"{loan_term_months}-month repayment term"))

    # 7. Age band (0-5 points; very young or near-retirement applicants score
    #    marginally higher, reflecting income-stability variance)
    if 28 <= age <= 55:
        pts = 0
    elif 22 <= age <= 60:
        pts = 2
    else:
        pts = 5
    factors.append(RiskFactor("Applicant Age Band", pts, f"Applicant age: {age}"))

    raw_score = sum(f.points for f in factors)
    score = int(round(min(100, max(0, raw_score))))

    return RiskScoreResult(score=score, category=_category(score), factors=factors)
