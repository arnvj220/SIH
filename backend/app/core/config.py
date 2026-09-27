from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _parse_origins(raw: str) -> list[str]:
    """Split a comma-separated origin list; strip whitespace and empties."""
    return [o.strip() for o in raw.split(",") if o.strip()]


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Qureka API")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "qureka")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    
    CORS_ORIGINS: list[str] = _parse_origins(
        os.getenv("CORS_ORIGINS", "http://localhost:5173")
    )

    DEBUG: bool = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"}


settings = Settings()