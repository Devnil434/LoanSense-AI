# Database Schema

Defined via SQLAlchemy models in `backend/app/models/models.py`. Tables are
created automatically on backend startup via `Base.metadata.create_all()`
— no separate migration step is required for a fresh database. For schema
changes on an existing production database, use
[Alembic](https://alembic.sqlalchemy.org/) (not included by default, to
keep the MVP dependency footprint small).

## `users`

| Column          | Type      | Notes                        |
|-----------------|-----------|-------------------------------|
| id              | String (UUID) | Primary key               |
| email           | String    | Unique, indexed               |
| hashed_password | String    | bcrypt hash                   |
| full_name       | String    | Nullable                      |
| created_at      | DateTime  |                                |

## `loan_applications`

| Column              | Type    | Notes                                   |
|---------------------|---------|-------------------------------------------|
| id                  | String (UUID) | Primary key                        |
| user_id             | String  | FK → `users.id`, nullable (anonymous demo use) |
| applicant_name      | String  |                                            |
| age                 | Integer |                                            |
| gender              | String  | `Male` \| `Female`                        |
| married             | String  | `Yes` \| `No`                             |
| dependents          | String  | `0` \| `1` \| `2` \| `3+`                 |
| education           | String  | `Graduate` \| `Not Graduate`              |
| self_employed       | String  | `Yes` \| `No`                             |
| applicant_income    | Float   |                                            |
| coapplicant_income  | Float   | Default 0                                 |
| loan_amount         | Float   | In thousands, matching Kaggle convention  |
| loan_amount_term    | Integer | Months                                    |
| credit_history      | Integer | 0 or 1                                    |
| property_area       | String  | `Urban` \| `Semiurban` \| `Rural`         |
| existing_debt       | Float   | Default 0                                 |
| savings             | Float   | Default 0                                 |
| created_at          | DateTime|                                            |

## `prediction_history`

| Column               | Type    | Notes                                        |
|----------------------|---------|-----------------------------------------------|
| id                   | String (UUID) | Primary key                              |
| application_id       | String  | FK → `loan_applications.id`                    |
| decision             | String  | `Approved` \| `Rejected`                       |
| confidence           | Float   |                                                 |
| approval_probability | Float   |                                                 |
| model_name           | String  | Which of LR/RF/XGB served this prediction      |
| risk_score           | Integer | 0–100                                          |
| risk_category        | String  | Excellent / Low / Moderate / High / Very High  |
| shap_explanation     | JSON    | `{ top_positive_factors, top_negative_factors }` |
| recommendations      | JSON    | `{ items: string[] }`                          |
| created_at           | DateTime|                                                 |

## Relationships

```
users (1) ───< loan_applications (many)
loan_applications (1) ───< prediction_history (many)
```

An application can, in principle, have multiple prediction records if
re-scored (e.g. after a model retrain) — the schema doesn't assume 1:1.

## Sample seed data

Run `python -m app.seed` from `backend/` to populate 40 realistic
applications + predictions, useful for immediately populating the
Analytics Dashboard on a fresh deployment.
