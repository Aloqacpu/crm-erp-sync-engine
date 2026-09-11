from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "crm-erp-sync-engine"
    database_url: str = "sqlite+aiosqlite:///./sync.db"
    erp_base_url: str = "http://erp:8080"
    erp_api_token: str = ""
    erp_timeout_seconds: float = 10.0
    erp_max_retries: int = 3
    retry_base_delay: float = 0.2


@lru_cache
def get_settings() -> Settings:
    return Settings()
