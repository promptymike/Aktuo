from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False, encoding="utf-8")
DEFAULT_SYSTEM_PROMPT_PATH = PROJECT_ROOT / "data" / "prompts" / "system_prompt_pl.txt"
# After switching to RRF (Reciprocal Rank Fusion), scores are rank-based
# and fall in a narrow range (~0.025-0.033).  A top-1 result at rank 1
# in both BM25 and vector rankings scores ~0.0328.  Setting the
# low-confidence threshold to 0.020 means only results ranked very deep
# (rank 50+ in both rankings) are flagged.
BM25_MIN_SCORE = 0.020
RATE_LIMIT_PER_HOUR = 30
MAX_QUESTION_LENGTH = 5000
MAX_CONTEXT_TOKENS = int(os.getenv("AKTUO_MAX_CONTEXT_TOKENS", "1200"))
SLANG_FILE_PATH = os.getenv("AKTUO_SLANG_FILE_PATH", "").strip()
RRF_BM25_K = int(os.getenv("AKTUO_RRF_BM25_K", "60"))
RRF_VECTOR_K = int(os.getenv("AKTUO_RRF_VECTOR_K", "60"))
INTENT_TAXONOMY_PATH = os.getenv(
    "AKTUO_INTENT_TAXONOMY_PATH",
    str(PROJECT_ROOT / "data" / "curated" / "intent_taxonomy.json"),
).strip()
CLARIFICATION_SLOTS_PATH = os.getenv(
    "AKTUO_CLARIFICATION_SLOTS_PATH",
    str(PROJECT_ROOT / "data" / "curated" / "clarification_slots.json"),
).strip()
CLARIFICATION_PROMPTS_PATH = os.getenv(
    "AKTUO_CLARIFICATION_PROMPTS_PATH",
    CLARIFICATION_SLOTS_PATH,
).strip()

PLACEHOLDER_VALUES = {
    "",
    "your_anthropic_api_key",
    "sk-ant-...",
    "sk-ant-TwojKlucz",
    "sk-ant-TwójKlucz",
}


class MissingEnvironmentError(ValueError):
    pass


@dataclass(slots=True)
class Settings:
    app_name: str
    system_prompt: str
    law_knowledge_path: str
    anthropic_api_key: str


def _is_usable(value: str | None) -> bool:
    return bool(value and value.strip() and value.strip() not in PLACEHOLDER_VALUES)


def _get_env_value(name: str) -> str | None:
    value = os.getenv(name)
    if _is_usable(value):
        return value
    return value


def _load_default_system_prompt() -> str:
    return DEFAULT_SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").strip()


def get_settings() -> Settings:
    system_prompt = _get_env_value("AKTUO_SYSTEM_PROMPT") or _load_default_system_prompt()
    required = {
        "AKTUO_APP_NAME": _get_env_value("AKTUO_APP_NAME"),
        "AKTUO_SYSTEM_PROMPT": system_prompt,
        "AKTUO_LAW_KNOWLEDGE_PATH": _get_env_value("AKTUO_LAW_KNOWLEDGE_PATH"),
        "ANTHROPIC_API_KEY": _get_env_value("ANTHROPIC_API_KEY"),
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        joined = ", ".join(missing)
        raise MissingEnvironmentError(
            f"Missing required environment variables: {joined}. "
            "Populate them before starting the app."
        )

    return Settings(
        app_name=required["AKTUO_APP_NAME"] or "",
        system_prompt=required["AKTUO_SYSTEM_PROMPT"] or "",
        law_knowledge_path=required["AKTUO_LAW_KNOWLEDGE_PATH"] or "",
        anthropic_api_key=required["ANTHROPIC_API_KEY"] or "",
    )
