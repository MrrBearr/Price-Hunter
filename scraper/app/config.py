from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://pricehunter:pricehunter_secret_2024@db:5432/pricehunter"
    redis_url: str = "redis://redis:6379/0"
    scraping_headless: bool = True
    scraping_timeout: int = 30000
    max_concurrent_scrapers: int = 3

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
