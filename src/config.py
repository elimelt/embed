from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path


class Settings(BaseSettings):
    DATABASE_URL: str = "document.db"
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    STATIC_DIR: Path = BASE_DIR / "static"
    CLEANUP_DAYS: int = 30

    class Config:
        DEBUG: bool = False


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
