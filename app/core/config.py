from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FaaS Billing"
    debug: bool = False
    database_url: str = "postgresql+psycopg://faas:faas@localhost:5432/faas_billing"
    max_batch_size: int = 1000


@lru_cache
def get_settings() -> Settings:
    return Settings()
