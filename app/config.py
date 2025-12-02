import os
from functools import lru_cache
from pathlib import Path
from typing import List

SECRET_KEY_ENV_NAME = "FREELATRACKER_SECRET_KEY"
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
DEFAULT_DATABASE_URL = "sqlite:///./freelatracker.db"
AUTO_CREATE_TABLES_ENV = "FREELATRACKER_AUTO_CREATE_TABLES"
DATABASE_URL_ENV_NAMES = ["FREELATRACKER_DATABASE_URL", "DATABASE_URL"]
ENV_NAME_ENV_VAR = "FREELATRACKER_ENV"
DEV_ENV_VALUES = {"dev", "development", "local"}
PROD_ENV_VALUES = {"prod", "production", "staging"}
ENV_FILE_PATH = Path(__file__).resolve().parent.parent / ".env"


def _current_env() -> str:
    return os.getenv(ENV_NAME_ENV_VAR, "dev").lower()


def _is_dev_env() -> bool:
    return _current_env() in DEV_ENV_VALUES


def _should_load_env_file() -> bool:
    """Only load .env automatically in local/dev environments."""
    override = os.getenv("FREELATRACKER_LOAD_ENV_FILE")
    if override is not None:
        return override.lower() in ("1", "true", "yes", "on")
    return _is_dev_env()


def _load_local_env() -> None:
    """Load a simple .env file so local runs work without exporting vars."""
    if not _should_load_env_file() or not ENV_FILE_PATH.exists():
        return

    try:
        for raw_line in ENV_FILE_PATH.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if key and value and key not in os.environ:
                os.environ[key] = value
    except OSError:
        # If the file cannot be read, fall back to existing environment vars.
        pass


_load_local_env()


@lru_cache()
def get_secret_key() -> str:
    secret = os.getenv(SECRET_KEY_ENV_NAME, "")
    if not secret:
        raise RuntimeError(
            f"Define un secreto fuerte en la variable de entorno {SECRET_KEY_ENV_NAME} "
            "antes de iniciar el servidor."
        )
    if len(secret) < 32:
        raise RuntimeError("FREELATRACKER_SECRET_KEY debe tener al menos 32 caracteres.")
    return secret


@lru_cache()
def get_database_url() -> str:
    for env_name in DATABASE_URL_ENV_NAMES:
        raw = os.getenv(env_name)
        if raw and raw.strip():
            return raw.strip()
    return DEFAULT_DATABASE_URL


@lru_cache()
def get_cors_origins() -> List[str]:
    raw = os.getenv("FREELATRACKER_CORS_ORIGINS", "")
    if not raw.strip():
        return DEFAULT_ALLOWED_ORIGINS
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache()
def get_access_token_exp_minutes() -> int:
    raw = os.getenv("FREELATRACKER_ACCESS_TOKEN_MINUTES", "60")
    try:
        value = int(raw)
    except ValueError:
        value = 60
    return max(value, 1)


@lru_cache()
def should_auto_create_tables() -> bool:
    default_raw = "false" if _current_env() in PROD_ENV_VALUES else "true"
    raw = os.getenv(AUTO_CREATE_TABLES_ENV, default_raw).lower()
    return raw in ("1", "true", "yes", "on")
