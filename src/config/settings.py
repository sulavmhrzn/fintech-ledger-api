from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/fintech_ledger"
    )
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "fallback_secret_key_for_dev"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1
    OTP_EXPIRATION_MINUTES: int = 15

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    SMTP_HOST: str
    SMTP_PORT: int
    SENDER_EMAIL: str = "noreply@fintechledger.com"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
