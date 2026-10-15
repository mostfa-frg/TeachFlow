"""Environment-backed application settings."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./data/teachflow.db"
    )
    data_dir: Path = Path(os.getenv("TEACHFLOW_DATA_DIR", "./data"))
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    llm_api_key: str | None = os.getenv("LLM_API_KEY")
    llm_base_url: str = os.getenv(
        "LLM_BASE_URL", "https://api.groq.com/openai/v1"
    ).rstrip("/")
    llm_model: str = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
    llm_api_style: str = os.getenv(
        "LLM_API_STYLE", "chat_completions"
    ).strip().lower()
    llm_timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "60"))


settings = Settings()
