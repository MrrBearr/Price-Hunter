from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://pricehunter:pricehunter_secret_2024@db:5432/pricehunter"

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Auth
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # App
    app_name: str = "PriceHunter"
    debug: bool = True

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
