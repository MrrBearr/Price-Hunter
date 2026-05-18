from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://pricehunter:pricehunter_secret_2024@db:5432/pricehunter"

    # Redis (optional for Vercel deployment)
    redis_url: Optional[str] = ""

    # Auth
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # App
    app_name: str = "PriceHunter"
    debug: bool = False

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
