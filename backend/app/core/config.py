"""
Application configuration.

Environment variables are loaded from .env when available.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv(
        "APP_NAME",
        "Quantum-Inspired Cyber Threat Detection",
    )

    APP_ENV: str = os.getenv(
        "APP_ENV",
        "development",
    )

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/qds_security",
    )

    API_PREFIX: str = os.getenv(
        "API_PREFIX",
        "/api",
    )

    DEBUG: bool = os.getenv(
        "DEBUG",
        "false",
    ).lower() in {"1", "true", "yes"}

    def __repr__(self) -> str:
        return (
            f"Settings("
            f"APP_NAME={self.APP_NAME!r}, "
            f"APP_ENV={self.APP_ENV!r}, "
            f"DATABASE_URL=<hidden>, "
            f"API_PREFIX={self.API_PREFIX!r}, "
            f"DEBUG={self.DEBUG!r}"
            f")"
        )


settings = Settings()