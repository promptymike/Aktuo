from __future__ import annotations

import os
from pathlib import Path

PLACEHOLDER_VALUES = {
    "",
    "your_anthropic_api_key",
    "sk-ant-...",
    "sk-ant-TwojKlucz",
    "sk-ant-TwójKlucz",
}


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _read_dotenv(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        values[key.strip()] = _strip_quotes(raw_value.strip())
    return values


def _is_usable(value: str | None) -> bool:
    return bool(value and value.strip() and value.strip() not in PLACEHOLDER_VALUES)


def get_env_value(name: str) -> str | None:
    process_value = os.getenv(name)
    if _is_usable(process_value):
        return process_value

    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / ".env",
        script_dir.parent / ".env",
    ]

    for candidate in candidates:
        dotenv_values = _read_dotenv(candidate)
        dotenv_value = dotenv_values.get(name)
        if _is_usable(dotenv_value):
            os.environ[name] = dotenv_value
            return dotenv_value

    return process_value
