from __future__ import annotations

DEFAULT_SYSTEM_PROMPT = (
    "You are Aktuo, a cautious legal information assistant that stays grounded in retrieved context."
)


def get_default_system_prompt() -> str:
    return DEFAULT_SYSTEM_PROMPT
