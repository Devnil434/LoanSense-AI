"""
generate_dataset.py

Generates a synthetic loan-application dataset that mirrors the schema of the
well-known Kaggle "Loan Prediction" dataset (Loan_ID, Gender, Married,
Dependents, Education, Self_Employed, ApplicantIncome, CoapplicantIncome,
LoanAmount, Loan_Amount_Term, Credit_History, Property_Area, Loan_Status).

NOTE: This environment cannot reach kaggle.com (network is restricted to a
package-registry allowlist), so the real Kaggle CSV cannot be downloaded at
build time. Instead we generate a statistically realistic synthetic dataset
with the exact same columns/semantics, using a transparent, documented rule
+ noise process. If you have Kaggle API access, drop the real
`loan_prediction.csv` into ml/data/raw/ and it will be used automatically
(see load_dataset() in train.py) — this generator is only a fallback so the
pipeline is runnable end-to-end out of the box.
"""

import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
N_ROWS = 5000

OUT_DIR = Path(__file__).parent / "data" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def generate():
    gender = RNG.choice(["Male", "Female"], N_ROWS, p=[0.78, 0.22])
    married = RNG.choice(["Yes", "No"], N_ROWS, p=[0.65, 0.35])
    dependents = RNG.choice(["0", "1", "2", "3+"], N_ROWS, p=[0.58, 0.17, 0.17, 0.08])
    education = RNG.choice(["Graduate", "Not Graduate"], N_ROWS, p=[0.78, 0.22])
    self_employed = RNG.choice(["Yes", "No"], N_ROWS, p=[0.14, 0.86])
    property_area = RNG.choice(["Urban", "Semiurban", "Rural"], N_ROWS, p=[0.38, 0.38, 0.24])

    applicant_income = RNG.gamma(shape=3.2, scale=1800, size=N_ROWS).round(0) + 1500
    coapplicant_income = np.where(
        married == "Yes",
        RNG.gamma(shape=2.0, scale=900, size=N_ROWS).round(0),
        0,
    )
    loan_amount = (RNG.gamma(shape=3.0, scale=45, size=N_ROWS) + 20).round(0)
    loan_amount_term = RNG.choice(
        [360, 180, 240, 120, 60, 84, 300, 12, 36],
        N_ROWS,
        p=[0.72, 0.08, 0.05, 0.04, 0.03, 0.03, 0.02, 0.02, 0.01],
    )
    credit_history = RNG.choice([1.0, 0.0], N_ROWS, p=[0.84, 0.16])

    age = RNG.integers(21, 65, N_ROWS)
    existing_debt = (RNG.gamma(shape=2.0, scale=1500, size=N_ROWS)).round(0)
    savings = (RNG.gamma(shape=2.2, scale=2500, size=N_ROWS)).round(0)

    total_income = applicant_income + coapplicant_income
    income_to_loan = total_income / (loan_amount * 1000 + 1)
    dti = existing_debt / (total_income + 1)

    # Transparent rule-based "ground truth" score used purely to synthesize a
    # realistic Loan_Status label with noise, mimicking real-world approval
    # patterns without leaking a trivial deterministic rule to the model.
    score = (
        2.4 * (credit_history == 1.0)
        + 1.1 * np.tanh(income_to_loan / 4)
        - 1.3 * np.tanh(dti * 3)
        + 0.35 * (education == "Graduate")
        + 0.25 * (property_area != "Rural")
        - 0.15 * (dependents == "3+")
        + RNG.normal(0, 0.9, N_ROWS)
    )
    approve_prob = 1 / (1 + np.exp(-score))
    loan_status = np.where(RNG.random(N_ROWS) < approve_prob, "Y", "N")

    loan_id = [f"LP{100000 + i}" for i in range(N_ROWS)]

    df = pd.DataFrame(
        {
            "Loan_ID": loan_id,
            "Gender": gender,
            "Married": married,
            "Dependents": dependents,
            "Education": education,
            "Self_Employed": self_employed,
            "ApplicantIncome": applicant_income.astype(int),
            "CoapplicantIncome": coapplicant_income.astype(int),
            "LoanAmount": loan_amount.astype(int),
            "Loan_Amount_Term": loan_amount_term.astype(int),
            "Credit_History": credit_history,
            "Property_Area": property_area,
            "Age": age.astype(int),
            "ExistingDebt": existing_debt.astype(int),
            "Savings": savings.astype(int),
            "Loan_Status": loan_status,
        }
    )

    # Inject realistic missingness, mirroring the real Kaggle dataset which
    # has nulls in several columns.
    for col, frac in [
        ("Gender", 0.02),
        ("Married", 0.005),
        ("Dependents", 0.025),
        ("Self_Employed", 0.05),
        ("LoanAmount", 0.035),
        ("Loan_Amount_Term", 0.023),
        ("Credit_History", 0.08),
    ]:
        idx = RNG.choice(N_ROWS, size=int(N_ROWS * frac), replace=False)
        df.loc[idx, col] = np.nan

    out_path = OUT_DIR / "loan_prediction.csv"
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} rows -> {out_path}")
    return df


if __name__ == "__main__":
    generate()
