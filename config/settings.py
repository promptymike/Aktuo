from __future__ import annotations

import os
from dataclasses import dataclass


class MissingEnvironmentError(ValueError):
    pass


@dataclass(slots=True)
class Settings:
    app_name: str
    system_prompt: str
    law_knowledge_path: str
    anthropic_api_key: str


def get_settings() -> Settings:
    required = {
        "AKTUO_APP_NAME": os.getenv("AKTUO_APP_NAME"),
        "AKTUO_SYSTEM_PROMPT": os.getenv("AKTUO_SYSTEM_PROMPT"),
        "AKTUO_LAW_KNOWLEDGE_PATH": os.getenv("AKTUO_LAW_KNOWLEDGE_PATH"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
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
