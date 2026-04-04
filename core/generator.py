from __future__ import annotations

import json
from collections.abc import Sequence
from urllib import error, request

from core.retriever import LawChunk

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
ANTHROPIC_MODEL = "claude-sonnet-4-6"


class AnthropicAPIError(RuntimeError):
    pass


def _build_user_prompt(query: str, chunks: Sequence[LawChunk]) -> str:
    context = "\n".join(
        (
            f"- Law: {chunk.law_name} | Article: {chunk.article_number} | "
            f"Category: {chunk.category} | Verified: {chunk.verified_date} | "
            f"Content: {chunk.content}"
        )
        for chunk in chunks
    )
    return (
        "Answer the user's question using only the provided legal context. "
        "If the context is not enough, say 'insufficient data'.\n\n"
        f"Question:\n{query}\n\n"
        f"Legal context:\n{context}"
    )


def _extract_text(payload: dict[str, object]) -> str:
    content = payload.get("content", [])
    if not isinstance(content, list):
        raise AnthropicAPIError("Anthropic API returned an unexpected response format.")

    parts: list[str] = []
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            text = item.get("text", "")
            if isinstance(text, str):
                parts.append(text)

    answer = "".join(parts).strip()
    if not answer:
        raise AnthropicAPIError("Anthropic API returned an empty response.")
    return answer


def generate_answer(
    query: str,
    chunks: Sequence[LawChunk],
    system_prompt: str,
    api_key: str,
) -> str:
    if not chunks:
        return "insufficient data"
    if not api_key:
        raise AnthropicAPIError("Missing ANTHROPIC_API_KEY.")

    payload = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 400,
        "system": [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": _build_user_prompt(query=query, chunks=chunks)}],
            }
        ],
    }
    body = json.dumps(payload).encode("utf-8")
    api_request = request.Request(
        ANTHROPIC_API_URL,
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_API_VERSION,
        },
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=30) as response:
            raw_response = response.read().decode("utf-8")
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="ignore").strip()
        raise AnthropicAPIError(f"Anthropic API request failed: {details or exc.reason}") from exc
    except error.URLError as exc:
        raise AnthropicAPIError(f"Could not reach Anthropic API: {exc.reason}") from exc

    return _extract_text(json.loads(raw_response))
