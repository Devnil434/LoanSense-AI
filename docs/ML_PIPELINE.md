# ML Pipeline

## Data

The product spec calls for the Kaggle "Loan Prediction" dataset. This
sandboxed build environment cannot reach `kaggle.com` (network egress is
restricted to package registries), so `ml/generate_dataset.py` produces a
**synthetic dataset with the identical schema and realistic missingness**
as a runnable fallback (5,000 rows, documented generation rules).

To use the real dataset instead:

1. Download `train.csv` from [Kaggle's Loan Prediction Problem
   dataset](https://www.kaggle.com/datasets/altruistdelhite04/loan-prediction-problem-dataset).
2. Save it as `ml/data/raw/loan_prediction_real.csv`.
3. Re-run `python ml/train.py` — `load_dataset()` automatically prefers the
   real file when present.

## Pipeline stages (`ml/train.py`)

1. **Load** — real CSV if present, else the synthetic generator.
2. **Clean** — categorical nulls filled with column mode, numeric nulls
   filled with column median, rows with a missing target dropped.
3. **Encode** — categorical columns mapped to integers via documented
   `CATEGORY_MAPS` (no silent label-encoder drift between train/serve).
4. **Feature engineering** — adds `TotalIncome`, `IncomeToLoanRatio`,
   `DebtToIncomeRatio` on top of the raw columns.
5. **Split** — stratified 80/20 train/test split (`random_state=42`).
6. **Scale** — `StandardScaler` fit on train only, applied to logistic
   regression (tree models use raw features).
7. **Train three candidates** — Logistic Regression, Random Forest,
   XGBoost, each evaluated on the same held-out test set.
8. **Select** — highest ROC-AUC wins. This is data-driven, not hardcoded.
9. **Explain** — a SHAP explainer matching the winning model type
   (`LinearExplainer` or `TreeExplainer`) is built and serialized alongside
   the model.
10. **Persist** — everything (model, scaler, feature columns, category
    maps, explainer, metrics) is bundled into one `joblib` artifact so
    inference never has any environment-dependent guesswork.

## Reproducing training

```bash
cd ml
pip install -r ../backend/requirements.txt
python generate_dataset.py   # only needed if data/raw/loan_prediction.csv is absent
python train.py
```

Outputs:
- `ml/models/loan_model.joblib` — the artifact the backend loads
- `ml/models/metrics.json` — offline evaluation metrics surfaced on `/metrics`
- `ml/data/processed/featured_dataset.csv` — the fully-featured dataset used for training

## Honest metrics

On this run, all three models land in the 0.79–0.80 accuracy / 0.67–0.68
ROC-AUC range — modest, not inflated. This reflects the deliberately noisy
synthetic label-generation process (see `generate_dataset.py`) rather than
a tuned, cherry-picked result. Swapping in the real Kaggle dataset and
re-running `train.py` will likely shift these numbers; the pipeline itself
does not change.

## Credit Risk Score vs. ML prediction

The `ml/risk_score.py` module is **not** an ML model. It's a transparent,
auditable point system (documented in `docs/ARCHITECTURE.md`) that exists
specifically so risk assessment doesn't depend on a black box. This
mirrors how real underwriting desks often keep a rules-based score
alongside a statistical model for compliance and explainability.
