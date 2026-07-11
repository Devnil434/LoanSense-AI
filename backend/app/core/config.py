from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "LoanSense AI"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # Falls back to a local SQLite file if DATABASE_URL is not provided, so
    # the project runs out-of-the-box without a cloud DB. In production, set
    # DATABASE_URL to a Neon/Supabase/Aiven Postgres connection string.
    DATABASE_URL: str = "sqlite:///./loansense.db"

    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_super_secret_key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://localhost:3000"]

    ML_MODEL_PATH: str = "../ml/models/loan_model.joblib"


@lru_cache
def get_settings() -> Settings:
    return Settings()
