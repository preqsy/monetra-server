from pydantic_settings import BaseSettings
from pathlib import Path

env_path = str(Path.cwd()) + "/.env"


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    MONO_BASE_URL: str = "https://api.withmono.com/v2"
    MONO_SECRET_KEY: str = ""
    FIREBASE_ADMIN_SDK_JSON_PATH: str = ""
    FIREBASE_SERVICE_ACCOUNT_JSON: str = ""

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    PLAID_CLIENT_ID: str = ""
    PLAID_SECRET: str = ""
    PLAID_ENV: str = "sandbox"
    PLAID_BASE_URL_SANDBOX: str = "https://sandbox.plaid.com"
    PLAID_BASE_URL_DEVELOPMENT: str = "https://development.plaid.com"
    PLAID_BASE_URL_PRODUCTION: str = "https://production.plaid.com"

    EXCHANGE_API_KEY: str = ""
    EXCHANGE_RATE_BASE_URL: str = "https://v6.exchangerate-api.com/v6/"
    KAFKA_CA_PEM: str = ""
    KAFKA_SERVICE_CERT: str = ""
    KAFKA_SERVICE_KEY: str = ""
    KAFKA_URL: str = ""

    BACKEND_HEADER: str

    class Config:
        env_file = env_path
        # Allow extra fields for backward compatibility
        extra = "ignore"


settings = Settings()
