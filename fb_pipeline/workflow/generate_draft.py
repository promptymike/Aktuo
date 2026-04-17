"""Prompt building + Opus 4.7 call with 1x retry for workflow drafts.

Kept small and side-effect-isolated — the LLM call is a single function
parameterised on a ``client_factory`` so tests can drop in fakes.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Callable

from fb_pipeline.workflow.prepare_material import (
    ClusterMaterial,
    truncate,
)
from fb_pipeline.workflow.schema import validate_draft


SYSTEM_PROMPT = (
    "Jesteś senior księgowym, doradcą podatkowym i kadrowym dla polskich biur "
    "rachunkowych. Tworzysz workflow rekord dla systemu Aktuo."
)

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _format_centroid_block(material: ClusterMaterial) -> str:
    lines: list[str] = []
    for i, p in enumerate(material.centroid_posts, start=1):
        lines.append(
            f"[{i}] post_id={p.post_id} · {p.comments_count} kom. · "
            f"cos={p.cosine_to_centroid:.3f}"
        )
        lines.append(f"    {truncate(p.text, 600)}")
        for j, cm in enumerate(p.longest_comments, start=1):
            lines.append(f"    komentarz #{j}: {truncate(cm, 250)}")
        lines.append("")
    return "\n".join(lines).strip()


def _format_high_engagement_block(material: ClusterMaterial) -> str:
    lines: list[str] = []
    for i, p in enumerate(material.high_engagement_posts, start=1):
        lines.append(
            f"[HE{i}] post_id={p.post_id} · {p.comments_count} kom. · "
            f"text_len={p.text_length}"
        )
        lines.append(f"    PYTANIE: {truncate(p.text, 800)}")
        lines.append(f"    KOMENTARZE ({len(p.all_comments)}):")
        for j, cm in enumerate(p.all_comments, start=1):
            lines.append(f"      [{j}] {truncate(cm, 300)}")
        lines.append("")
    return "\n".join(lines).strip()


def _format_legal_candidates_block(material: ClusterMaterial) -> str:
    lines: list[str] = []
    for i, cand in enumerate(material.legal_candidates, start=1):
        lines.append(
            f"[{i}] {cand.law_name} · {cand.article_number} · "
            f"kategoria={cand.category} · score={cand.score:.3f}"
        )
        lines.append(f"    {cand.content_preview}")
    return "\n".join(lines).strip()


def build_prompt(material: ClusterMaterial, today_iso: str) -> str:
    spec = material.spec
    keywords_line = ", ".join(material.top_keywords) or "(brak)"
    bigrams_line = ", ".join(material.top_bigrams) or "(brak)"
    centroid = _format_centroid_block(material) or "(brak)"
    high = _format_high_engagement_block(material) or "(brak)"
    legal = _format_legal_candidates_block(material) or "(brak)"

    prompt = f"""KONTEKST KLASTRA:
Label: {spec.label}
Topic area: {spec.topic_area}
Size: {material.size} postów w klastrze
Keywords: {keywords_line}
Bigramy: {bigrams_line}

10 PRZYKŁADOWYCH PYTAŃ Z KLASTRA (centroid):
{centroid}

5 PYTAŃ Z BOGATĄ DYSKUSJĄ (high engagement + komentarze):
{high}

KANDYDACI NA KOTWICE PRAWNE Z KB AKTUO:
{legal}
(Wybierz 1-3 które SĄ naprawdę relevantne. Jeśli żaden nie jest relevantny, zostaw pustą listę i ustaw requires_manual_legal_anchor=true.)

ZADANIE:
Stwórz workflow rekord w formacie JSON zgodnym z poniższym schematem. Zasady:

- question_examples: dokładnie 5 pytań. Użyj PRAWDZIWYCH pytań z klastra (parafrazuj lekko dla zwięzłości, ale nie wymyślaj).
- answer_steps: 3-7 konkretnych kroków. Każdy krok:
  * Zaczyna się od czasownika ("Sprawdź...", "Ustal...", "Wystaw...", "Zgłoś...").
  * Konkret operacyjny (nie "sprawdź dokumenty", tylko "sprawdź czy Z-3 ma kod ZUS 331 lub 350").
  * Bazuje na komentarzach społeczności PLUS Twojej wiedzy merytorycznej.
  * Jeśli krok zależy od warunku — użyj pola "condition" (np. "if pracownik ma orzeczenie niepełnosprawności").
  * Jeśli krok wymaga programu księgowego, wymień 1-2 popularne (Comarch Optima, Symfonia, Enova, WFirma).
- legal_anchors: 1-3 kotwice z KB. Każda: law_name + article_number + reason (1 zdanie). Jeśli żadna nie pasuje — pusta lista + requires_manual_legal_anchor=true.
- edge_cases: 2-4 warianty/wyjątki z dyskusji w komentarzach.
- common_mistakes: 2-3 typowe błędy widoczne w komentarzach lub z doświadczenia.
- related_questions: 2-3 pytania "zbliżone ale inne" (tylko pytania, bez odpowiedzi).
- last_verified_at: "{today_iso}"
- draft: true
- requires_manual_legal_anchor: bool
- generation_metadata: model="claude-opus-4-7", cluster_id="{spec.target_key}", cluster_label z label powyżej, generated_at=ISO timestamp UTC, source_post_ids=lista id postów które wpłynęły na treść.

SCHEMAT JSON (zwróć TYLKO JSON, bez markdown fence, bez tekstu przed/po; użyj polskich znaków diakrytycznych):
{{
  "id": "wf_{spec.target_key}_{{slug_from_label}}",
  "title": "...",
  "topic_area": "{spec.topic_area}",
  "question_examples": ["...", "...", "...", "...", "..."],
  "answer_steps": [
    {{"step": 1, "action": "...", "detail": "...", "condition": null}},
    {{"step": 2, "action": "...", "detail": "...", "condition": "if ..."}}
  ],
  "legal_anchors": [
    {{"law_name": "...", "article_number": "...", "reason": "..."}}
  ],
  "edge_cases": ["...", "..."],
  "common_mistakes": ["...", "..."],
  "related_questions": ["...", "..."],
  "last_verified_at": "{today_iso}",
  "draft": true,
  "requires_manual_legal_anchor": false,
  "generation_metadata": {{
    "model": "claude-opus-4-7",
    "cluster_id": "{spec.target_key}",
    "cluster_label": "{spec.label}",
    "generated_at": "<ISO UTC>",
    "source_post_ids": ["...", "..."]
  }}
}}
"""
    return prompt


def parse_json_response(text: str) -> dict[str, Any]:
    """Extract and parse a JSON object from an LLM response.

    Accepts either a raw JSON string or a markdown-fenced one. Raises
    ``ValueError`` on parse failure.
    """

    stripped = text.strip()
    if not stripped:
        raise ValueError("empty response")

    # Try fence first (defensive — prompt asks not to fence).
    m = _JSON_FENCE.search(stripped)
    if m:
        stripped = m.group(1).strip()

    # Trim any accidental prefix before the first '{'.
    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace == -1 or last_brace == -1 or last_brace < first_brace:
        raise ValueError("no JSON object found in response")
    candidate = stripped[first_brace : last_brace + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON parse failed: {exc}") from exc


def call_opus(
    client: Any,
    prompt: str,
    *,
    model: str = "claude-opus-4-7",
    max_tokens: int = 4096,
) -> tuple[str, dict[str, int]]:
    """Single Opus call. Returns (text, usage_dict)."""

    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in resp.content if block.type == "text")
    usage = {
        "input_tokens": int(getattr(resp.usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(resp.usage, "output_tokens", 0) or 0),
    }
    return text, usage


def generate_draft_with_retry(
    client: Any,
    prompt: str,
    *,
    max_retries: int = 1,
    model: str = "claude-opus-4-7",
    max_tokens: int = 4096,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Call Opus, parse+validate, retry once if malformed.

    Returns (draft or None, list of attempt telemetry dicts).
    """

    attempts: list[dict[str, Any]] = []
    current_prompt = prompt
    last_error: str | None = None

    for attempt_idx in range(max_retries + 1):
        text, usage = call_opus(
            client, current_prompt, model=model, max_tokens=max_tokens
        )
        attempt_rec: dict[str, Any] = {
            "attempt": attempt_idx + 1,
            "input_tokens": usage["input_tokens"],
            "output_tokens": usage["output_tokens"],
            "raw_text_len": len(text),
        }
        try:
            parsed = parse_json_response(text)
        except ValueError as exc:
            last_error = f"parse: {exc}"
            attempt_rec["status"] = "parse_fail"
            attempt_rec["error"] = last_error
            attempts.append(attempt_rec)
            current_prompt = (
                prompt
                + "\n\nPoprzednia próba zwróciła niepoprawny JSON: "
                + f"{last_error}. Zwróć TYLKO poprawny JSON."
            )
            continue

        ok, err = validate_draft(parsed)
        if not ok:
            last_error = f"schema: {err}"
            attempt_rec["status"] = "schema_fail"
            attempt_rec["error"] = last_error
            attempts.append(attempt_rec)
            current_prompt = (
                prompt
                + "\n\nPoprzednia próba miała niepoprawny JSON: "
                + f"{last_error}. Zwróć TYLKO poprawny JSON zgodny ze schematem."
            )
            continue

        attempt_rec["status"] = "ok"
        attempts.append(attempt_rec)
        return parsed, attempts

    return None, attempts


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
