"""Configuration management"""

import json
from typing import List, Union

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_cors_origins(v: Union[str, List[str]]) -> List[str]:
    """Parse CORS_ORIGINS to list (comma-split + strip, or JSON array)."""
    if isinstance(v, str):
        s = v.strip()
        if s.startswith("["):
            try:
                parsed = json.loads(s)
                return [str(o).strip() for o in parsed if o] if isinstance(parsed, list) else [s]
            except (json.JSONDecodeError, TypeError):
                pass
        return [o.strip() for o in v.split(",") if o.strip()]
    return list(v) if v else []


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # Environment
    sgp_plus_env: str = "des"  # des|hml|prod

    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/sgp_plus_des"

    # Cookie Settings
    cookie_name: str = "sgp_plus_session"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cookie_domain: str | None = None
    cookie_path: str = "/"
    session_ttl_minutes: int = 720

    # CORS (list; no "*" when using cookie auth / allow_credentials=True)
    cors_origins: Union[str, List[str]] = "http://localhost:5173"

    # Bootstrap Admin (senha obrigatório trocar em .env)
    bootstrap_admin_email: str = "admin@sgp.local"
    bootstrap_admin_password: str = "CHANGE_ME"

    @model_validator(mode="after")
    def validate_cors_and_parse_origins(self) -> "Settings":
        self.cors_origins = _parse_cors_origins(self.cors_origins)
        if "*" in self.cors_origins or self.cors_origins == ["*"]:
            raise ValueError(
                "CORS_ORIGINS cannot contain '*' when allow_credentials=True (cookie auth)."
            )
        return self


settings = Settings()
