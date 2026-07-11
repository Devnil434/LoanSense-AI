"""
train.py — LoanSense AI model training pipeline.

Pipeline:
  1. Load dataset (real Kaggle CSV if present, else synthetic fallback)
  2. Clean missing values
  3. Encode categorical features
  4. Scale numeric features
  5. Train/test split (stratified)
  6. Train Logistic Regression, Random Forest, XGBoost
  7. Evaluate on held-out test set, select best model by ROC-AUC
  8. Persist model + preprocessing pipeline + metadata + SHAP explainer with joblib

Run:
    python train.py
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODEL_DIR = BASE_DIR / "models"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

CATEGORICAL_COLS = ["Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area"]
NUMERIC_COLS = [
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_History",
    "Age",
    "ExistingDebt",
    "Savings",
]
TARGET_COL = "Loan_Status"

CATEGORY_MAPS = {
    "Gender": {"Male": 1, "Female": 0},
    "Married": {"Yes": 1, "No": 0},
    "Dependents": {"0": 0, "1": 1, "2": 2, "3+": 3},
    "Education": {"Graduate": 1, "Not Graduate": 0},
    "Self_Employed": {"Yes": 1, "No": 0},
    "Property_Area": {"Rural": 0, "Semiurban": 1, "Urban": 2},
}


def load_dataset() -> pd.DataFrame:
    real_csv = RAW_DIR / "loan_prediction_real.csv"
    synth_csv = RAW_DIR / "loan_prediction.csv"
    if real_csv.exists():
        print("Loading real Kaggle dataset from data/raw/loan_prediction_real.csv")
        return pd.read_csv(real_csv)
    if not synth_csv.exists():
        from generate_dataset import generate

        generate()
    print("Loading synthetic fallback dataset from data/raw/loan_prediction.csv")
    return pd.read_csv(synth_csv)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.drop(columns=[c for c in ["Loan_ID"] if c in df.columns], inplace=True)

    for col in CATEGORICAL_COLS:
        mode = df[col].mode(dropna=True)
        df[col] = df[col].fillna(mode.iloc[0] if len(mode) else "Unknown")

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    df = df[df[TARGET_COL].notna()]
    return df


def encode(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col, mapping in CATEGORY_MAPS.items():
        df[col] = df[col].map(mapping).fillna(0).astype(int)
    df[TARGET_COL] = df[TARGET_COL].map({"Y": 1, "N": 0})
    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["TotalIncome"] = df["ApplicantIncome"] + df["CoapplicantIncome"]
    df["IncomeToLoanRatio"] = df["TotalIncome"] / (df["LoanAmount"] * 1000 + 1)
    df["DebtToIncomeRatio"] = df["ExistingDebt"] / (df["TotalIncome"] + 1)
    return df

FEATURE_COLS = CATEGORICAL_COLS + NUMERIC_COLS + [
    "TotalIncome",
    "IncomeToLoanRatio",
    "DebtToIncomeRatio",
]


def evaluate(model, X_test, y_test) -> dict:
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]
    return {
        "accuracy": round(accuracy_score(y_test, preds), 4),
        "precision": round(precision_score(y_test, preds), 4),
        "recall": round(recall_score(y_test, preds), 4),
        "f1_score": round(f1_score(y_test, preds), 4),
        "roc_auc": round(roc_auc_score(y_test, probs), 4),
    }


def main():
    raw = load_dataset()
    cleaned = clean(raw)
    encoded = encode(cleaned)
    featured = build_features(encoded)

    X = featured[FEATURE_COLS]
    y = featured[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=8, min_samples_leaf=5, random_state=42, n_jobs=-1
        ),
        "xgboost": XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        ),
    }

    results = {}
    fitted = {}
    for name, model in candidates.items():
        if name == "logistic_regression":
            model.fit(X_train_scaled, y_train)
            metrics = evaluate(model, X_test_scaled, y_test)
        else:
            model.fit(X_train, y_train)
            metrics = evaluate(model, X_test, y_test)
        results[name] = metrics
        fitted[name] = model
        print(f"{name}: {metrics}")

    best_name = max(results, key=lambda n: results[n]["roc_auc"])
    best_model = fitted[best_name]
    print(f"\nBest model selected: {best_name} (ROC-AUC={results[best_name]['roc_auc']})")

    # Build a SHAP explainer for the winning model (tree explainer for tree
    # models, linear explainer for logistic regression).
    if best_name == "logistic_regression":
        explainer = shap.LinearExplainer(best_model, X_train_scaled, feature_names=FEATURE_COLS)
        uses_scaler = True
    else:
        explainer = shap.TreeExplainer(best_model)
        uses_scaler = False

    artifact = {
        "model": best_model,
        "model_name": best_name,
        "scaler": scaler,
        "uses_scaler": uses_scaler,
        "feature_cols": FEATURE_COLS,
        "category_maps": CATEGORY_MAPS,
        "explainer": explainer,
        "metrics": results,
    }
    joblib.dump(artifact, MODEL_DIR / "loan_model.joblib")

    with open(MODEL_DIR / "metrics.json", "w") as f:
        json.dump(
            {"best_model": best_name, "all_results": results, "n_train": len(X_train), "n_test": len(X_test)},
            f,
            indent=2,
        )

    featured.to_csv(PROCESSED_DIR / "featured_dataset.csv", index=False)
    print(f"\nSaved model artifact -> {MODEL_DIR / 'loan_model.joblib'}")
    print(f"Saved metrics -> {MODEL_DIR / 'metrics.json'}")


if __name__ == "__main__":
    main()
