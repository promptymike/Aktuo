from __future__ import annotations

import json
import re
from pathlib import Path


def load_synonym_map(slang_file: str) -> dict[str, list[str]]:
    """Load a slang-to-expansions mapping from a JSON file.

    The input file must contain a JSON list of objects with the keys
    ``slang`` (str), ``expanded`` (str), and ``freq`` (int).

    Args:
        slang_file: Path to the JSON file with slang definitions.

    Returns:
        A dictionary mapping each slang term to a list of unique expanded forms.
        Keys are stored case-insensitively using ``str.casefold()``.

    Raises:
        ValueError: If the file is missing, cannot be read, cannot be parsed as
            JSON, or does not match the expected structure.
    """

    path = Path(slang_file)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Slang file not found: {slang_file}") from exc
    except OSError as exc:
        raise ValueError(f"Could not read slang file '{slang_file}': {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Malformed slang file '{slang_file}': invalid JSON ({exc.msg})."
        ) from exc

    if not isinstance(payload, list):
        raise ValueError(
            f"Malformed slang file '{slang_file}': expected a JSON list of entries."
        )

    grouped: dict[str, list[tuple[int, str]]] = {}

    for index, entry in enumerate(payload):
        if not isinstance(entry, dict):
            raise ValueError(
                f"Malformed slang file '{slang_file}': entry {index} is not an object."
            )

        slang = entry.get("slang")
        expanded = entry.get("expanded")
        freq = entry.get("freq")

        if not isinstance(slang, str) or not slang.strip():
            raise ValueError(
                f"Malformed slang file '{slang_file}': entry {index} has an invalid 'slang' value."
            )
        if not isinstance(expanded, str) or not expanded.strip():
            raise ValueError(
                f"Malformed slang file '{slang_file}': entry {index} has an invalid 'expanded' value."
            )
        if not isinstance(freq, int):
            raise ValueError(
                f"Malformed slang file '{slang_file}': entry {index} has an invalid 'freq' value."
            )

        key = slang.strip().casefold()
        grouped.setdefault(key, []).append((freq, expanded.strip()))

    synonym_map: dict[str, list[str]] = {}

    for slang, expansions_with_freq in grouped.items():
        # Prefer the most common expansions first and drop duplicates.
        ordered = sorted(
            expansions_with_freq,
            key=lambda item: (-item[0], item[1].casefold()),
        )
        unique_expansions: list[str] = []
        seen: set[str] = set()

        for _, expanded in ordered:
            marker = expanded.casefold()
            if marker in seen:
                continue
            seen.add(marker)
            unique_expansions.append(expanded)

        synonym_map[slang] = unique_expansions

    return synonym_map


def expand_query(query: str, synonym_map: dict[str, list[str]]) -> str:
    """Expand slang terms found in a user query.

    Each matched slang term is replaced with its expanded forms enclosed in
    parentheses. Matching is case-insensitive, while all non-matching parts of
    the original query are preserved unchanged.

    Args:
        query: The original user query.
        synonym_map: Mapping of slang terms to one or more expanded forms.

    Returns:
        The expanded query. If no slang terms are found, the original query is
        returned unchanged.
    """

    if not query or not synonym_map:
        return query

    normalized_map: dict[str, list[str]] = {}
    patterns: list[str] = []

    for slang, expansions in synonym_map.items():
        if not isinstance(slang, str) or not slang.strip():
            continue

        clean_expansions = [
            expanded.strip()
            for expanded in expansions
            if isinstance(expanded, str) and expanded.strip()
        ]
        if not clean_expansions:
            continue

        key = slang.strip().casefold()
        normalized_map[key] = clean_expansions
        patterns.append(re.escape(slang.strip()))

    if not patterns:
        return query

    pattern = re.compile(
        rf"(?<!\w)({'|'.join(sorted(patterns, key=len, reverse=True))})(?!\w)",
        flags=re.IGNORECASE,
    )

    if not pattern.search(query):
        return query

    def replace(match: re.Match[str]) -> str:
        slang = match.group(0).casefold()
        expansions = normalized_map[slang]
        return f"({' '.join(expansions)})"

    return pattern.sub(replace, query)
