"""
Krok 3: Generator answer units.
Wspiera checkpoint/resume per sub-batch. Przy błędzie kredytów zapisuje postęp
i kończy się czysto, aby kolejny run mógł kontynuować od miejsca przerwania.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import anthropic
from env_utils import get_env_value

MODEL = "claude-haiku-4-5-20251001"
REQUEST_TIMEOUT_SECONDS = 180.0
TIMEOUT_RETRIES = 3
CHECKPOINT_VERSION = 3
SUB_BATCH_SIZE = 10


def is_credit_balance_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "credit balance too low" in message or "insufficient credit" in message


def build_system_prompt(law_name: str) -> str:
    return f"""Jesteś ekspertem od polskiego prawa podatkowego. Generujesz ANSWER UNITS dla systemu RAG.

Pracujesz na ustawie: {law_name}.
Answer unit to strukturalna jednostka wiedzy, która odpowiada na JEDNO konkretne pytanie księgowego/podatkowca.

TWARDE ZASADY:
1. Odpowiedź musi wynikać WYŁĄCZNIE z podanego tekstu artykułu. NIGDY nie dodawaj wiedzy spoza tekstu.
2. Cytuj DOKŁADNY artykuł, ustęp i punkt (np. "art. 86a ust. 1 pkt 2 lit. a").
3. Jeśli tekst artykułu nie wystarcza do pełnej odpowiedzi, ustaw "requires_verification": true.
4. Odpowiedź ma być PRAKTYCZNA — napisana językiem zrozumiałym dla księgowego, nie prawniczym.
5. Odpowiedź powinna mieć 2-5 zdań. Konkret, nie esej.
6. Warunki i wyjątki MUSZĄ wynikać z tekstu, nie z Twojej wiedzy.

FORMAT ODPOWIEDZI — WYŁĄCZNIE JSON, bez markdown:
{{
  "units": [
    {{
      "id": "law-{{numer_artykulu}}-{{krotki-slug}}",
      "question_intent": "Pytanie w formie naturalnej",
      "question_patterns": ["wariant 1", "wariant 2", "wariant 3"],
      "answer": "Odpowiedź 2-5 zdań. Praktyczna, konkretna.",
      "legal_basis": [
        {{
          "law": "{law_name}",
          "article": "art. 86a ust. 1",
          "quote": "kluczowy fragment z tekstu artykułu (max 1 zdanie)"
        }}
      ],
      "conditions": ["warunek 1 z tekstu", "warunek 2"],
      "exceptions": ["wyjątek 1 z tekstu"],
      "taxpayer_type": ["osoba_fizyczna_dg", "osoba_prawna", "ryczalt", "vat_czynny", "vat_zwolniony"],
      "topic": "kategoria tematu",
      "difficulty": "easy|medium|hard",
      "requires_verification": false
    }}
  ]
}}"""


def get_article_text(articles: list[dict], article_numbers: list[str]) -> str:
    texts = []
    for number in article_numbers:
        for article in articles:
            if article["article_number"] == number:
                texts.append(f"--- {article['full_id']} ({article['division']}) ---\n{article['raw_text']}")
                break
    return "\n\n".join(texts)


def make_group_key(article_numbers: list[str]) -> str:
    return "|".join(sorted(str(number) for number in article_numbers if number))


def make_subbatch_key(group_key: str, subbatch_index: int) -> str:
    return f"{group_key}::subbatch::{subbatch_index}"


def generate_units_for_group(
    client: anthropic.Anthropic,
    questions: list[dict],
    article_text: str,
    law_name: str,
) -> tuple[list[dict], dict]:
    questions_formatted = "\n".join(f"- {question['question']}" for question in questions)

    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=[
            {
                "type": "text",
                "text": build_system_prompt(law_name),
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"""TEKST ARTYKUŁÓW USTAWY: {law_name}

{article_text}

PYTANIA UŻYTKOWNIKÓW (wygeneruj answer unit dla KAŻDEGO pytania):

{questions_formatted}

Wygeneruj answer units. WYŁĄCZNIE JSON.""",
            }
        ],
    )

    raw = response.content[0].text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(raw[start:end])
        else:
            raise

    units = result.get("units", [result] if "id" in result else [])
    usage = response.usage
    cache_info = {
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "cache_read": getattr(usage, "cache_read_input_tokens", 0),
    }
    return units, cache_info


def validate_generated_units(
    units: list[dict],
    *,
    group_key: str,
    subbatch_key: str,
    article_numbers: list[str],
    source_questions: list[str],
) -> tuple[list[dict], list[dict]]:
    valid_units: list[dict] = []
    rejected_units: list[dict] = []

    for index, unit in enumerate(units, start=1):
        issues: list[str] = []
        unit_id = str(unit.get("id", "")).strip()
        question_intent = str(unit.get("question_intent", "")).strip()
        answer = str(unit.get("answer", "")).strip()
        legal_basis = unit.get("legal_basis")

        if not unit_id:
            issues.append("missing id")
        if not question_intent:
            issues.append("missing question_intent")
        if len(answer) < 20:
            issues.append("answer too short")
        if not isinstance(legal_basis, list) or not legal_basis:
            issues.append("missing legal_basis")

        if issues:
            rejected_units.append(
                {
                    "articles": article_numbers,
                    "group_key": group_key,
                    "subbatch_key": subbatch_key,
                    "questions": source_questions,
                    "error": f"Invalid generated unit #{index}: {', '.join(issues)}",
                }
            )
            continue

        valid_units.append(unit)

    return valid_units, rejected_units


def group_by_articles(matches: list[dict]) -> dict[str, dict]:
    groups: dict[str, dict] = {}
    for match in matches:
        article_numbers = match.get("matched_articles", [])
        if not article_numbers:
            continue
        group_key = make_group_key(article_numbers)
        if group_key not in groups:
            groups[group_key] = {"articles": article_numbers, "questions": []}
        groups[group_key]["questions"].append(
            {
                "question": match["question"],
                "topic": match.get("topic", ""),
                "primary_article": match.get("primary_article", article_numbers[0]),
            }
        )
    return groups


def deduplicate_units(units: list[dict]) -> list[dict]:
    seen_ids: set[str] = set()
    unique_units: list[dict] = []
    for unit in units:
        normalized = dict(unit)
        unit_id = str(normalized.get("id", "") or "")
        if unit_id:
            original_id = unit_id
            suffix = 1
            while unit_id in seen_ids:
                suffix += 1
                unit_id = f"{original_id}-{suffix}"
            normalized["id"] = unit_id
            seen_ids.add(unit_id)
        unique_units.append(normalized)
    return unique_units


def unit_subbatch_key(unit: dict) -> str:
    return str(unit.get("_source_subbatch_key", "")).strip()


def load_checkpoint(output_file: Path) -> tuple[list[dict], list[dict], float, set[str], int]:
    if not output_file.exists():
        return [], [], 0.0, set(), 0

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    units = payload.get("units", [])
    errors = payload.get("errors", [])
    metadata = payload.get("metadata", {})
    if not isinstance(units, list) or not isinstance(errors, list) or not isinstance(metadata, dict):
        raise ValueError(f"Nieprawidłowy checkpoint: {output_file}")

    completed_subbatch_keys = {str(key) for key in metadata.get("completed_subbatch_keys", [])}
    total_cost = float(metadata.get("total_cost_usd", 0.0) or 0.0)
    invalid_units_rejected = int(metadata.get("invalid_units_rejected", 0) or 0)

    retry_subbatch_keys = {
        str(error.get("subbatch_key", "")).strip()
        for error in errors
        if str(error.get("subbatch_key", "")).strip()
    }

    if retry_subbatch_keys:
        units = [unit for unit in units if unit_subbatch_key(unit) not in retry_subbatch_keys]
        errors = [error for error in errors if str(error.get("subbatch_key", "")).strip() not in retry_subbatch_keys]
        completed_subbatch_keys -= retry_subbatch_keys

    return units, errors, total_cost, completed_subbatch_keys, invalid_units_rejected


def save_checkpoint(
    output_file: Path,
    *,
    units: list[dict],
    errors: list[dict],
    total_cost: float,
    invalid_units_rejected: int,
    completed_subbatch_keys: set[str],
    total_groups: int,
    total_subbatches: int,
    articles_metadata: dict,
    exited_due_to_credit_error: bool = False,
) -> int:
    unique_units = deduplicate_units(units)
    completed_groups = len({key.split("::subbatch::", 1)[0] for key in completed_subbatch_keys})
    payload = {
        "metadata": {
            "checkpoint_version": CHECKPOINT_VERSION,
            "checkpoint_saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_groups": completed_groups,
            "total_groups": total_groups,
            "completed_subbatches": len(completed_subbatch_keys),
            "total_subbatches": total_subbatches,
            "completed_subbatch_keys": sorted(completed_subbatch_keys),
            "total_units": len(unique_units),
            "errors": len(errors),
            "invalid_units_rejected": invalid_units_rejected,
            "total_cost_usd": round(total_cost, 4),
            "exited_due_to_credit_error": exited_due_to_credit_error,
            "law": articles_metadata,
        },
        "units": unique_units,
        "errors": errors,
    }
    output_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(unique_units)


def format_elapsed(started_at: float) -> str:
    elapsed = int(time.time() - started_at)
    minutes, seconds = divmod(elapsed, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"
    return f"{minutes}m {seconds:02d}s"


def generate_units_with_retry(
    client: anthropic.Anthropic,
    questions: list[dict],
    article_text: str,
    law_name: str,
) -> tuple[list[dict], dict]:
    last_error: Exception | None = None
    for attempt in range(1, TIMEOUT_RETRIES + 1):
        try:
            return generate_units_for_group(client, questions, article_text, law_name)
        except anthropic.APITimeoutError as exc:
            last_error = exc
            print(f"  TIMEOUT {attempt}/{TIMEOUT_RETRIES}: Claude nie odpowiedział w {REQUEST_TIMEOUT_SECONDS:.0f}s")
            if attempt < TIMEOUT_RETRIES:
                time.sleep(attempt)
    assert last_error is not None
    raise last_error


def main() -> None:
    if len(sys.argv) < 3:
        print("Użycie: python generate_units.py articles.json matched.json [--output draft_units.json]")
        sys.exit(1)

    articles_path = sys.argv[1]
    matched_path = sys.argv[2]
    output_path = "draft_units.json"
    if "--output" in sys.argv:
        output_path = sys.argv[sys.argv.index("--output") + 1]
    output_file = Path(output_path)

    api_key = get_env_value("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Ustaw ANTHROPIC_API_KEY")
        sys.exit(1)

    articles_data = json.loads(Path(articles_path).read_text(encoding="utf-8"))
    matched_data = json.loads(Path(matched_path).read_text(encoding="utf-8"))

    articles = articles_data["articles"]
    law_name = articles_data.get("metadata", {}).get("short_name") or articles_data.get("metadata", {}).get("law_name", "ustawa")
    matches = matched_data["matches"]
    groups = group_by_articles(matches)
    total_questions = sum(len(group["questions"]) for group in groups.values())
    total_groups = len(groups)
    total_subbatches = sum(max(1, (len(group["questions"]) + SUB_BATCH_SIZE - 1) // SUB_BATCH_SIZE) for group in groups.values())

    print(f"Pytań z dopasowaniem: {total_questions}")
    print(f"Grup artykułów: {total_groups}")
    print(f"Szacowana liczba wywołań API (sub-batche): {total_subbatches}")

    client = anthropic.Anthropic(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS)

    try:
        all_units, errors, total_cost, completed_subbatch_keys, invalid_units_rejected = load_checkpoint(output_file)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    if completed_subbatch_keys:
        print(
            f"Resume z checkpointu: {len(completed_subbatch_keys)}/{total_subbatches} sub-batchy, "
            f"{len(all_units)} unitów, koszt ${total_cost:.4f}"
        )
    else:
        print("Start od zera — brak checkpointu.")

    started_at = time.time()

    for group_index, (group_key, group) in enumerate(groups.items(), start=1):
        article_numbers = group["articles"]
        questions = group["questions"]
        article_text = get_article_text(articles, article_numbers)
        sub_batches = [questions[index:index + SUB_BATCH_SIZE] for index in range(0, len(questions), SUB_BATCH_SIZE)] or [questions]

        print(
            f"\n[{group_index}/{total_groups}] art. {', '.join(article_numbers)} | "
            f"pytania: {len(questions)} | sub-batche: {len(sub_batches)} | "
            f"tekst: {len(article_text)} znaków | elapsed {format_elapsed(started_at)}"
        )

        for subbatch_index, sub_batch in enumerate(sub_batches, start=1):
            subbatch_key = make_subbatch_key(group_key, subbatch_index)
            if subbatch_key in completed_subbatch_keys:
                print(f"  -> Sub-batch {subbatch_index}/{len(sub_batches)} SKIP (checkpoint)")
                continue

            try:
                print(
                    f"  -> Sub-batch {subbatch_index}/{len(sub_batches)} "
                    f"(globalnie {len(completed_subbatch_keys) + 1}/{total_subbatches}) | {len(sub_batch)} pytań"
                )
                units, cache_info = generate_units_with_retry(client, sub_batch, article_text, law_name)
                units, rejected_units = validate_generated_units(
                    units,
                    group_key=group_key,
                    subbatch_key=subbatch_key,
                    article_numbers=article_numbers,
                    source_questions=[question["question"] for question in sub_batch],
                )
                errors.extend(rejected_units)
                invalid_units_rejected += len(rejected_units)

                for unit in units:
                    unit["_source_articles"] = article_numbers
                    unit["_generated_from"] = [question["question"] for question in sub_batch]
                    unit["_source_subbatch_key"] = subbatch_key

                all_units.extend(units)
                completed_subbatch_keys.add(subbatch_key)

                input_cost = cache_info["input_tokens"] * 3 / 1_000_000
                cached_cost = cache_info["cache_read"] * 0.3 / 1_000_000
                output_cost = cache_info["output_tokens"] * 15 / 1_000_000
                batch_cost = input_cost + cached_cost + output_cost
                total_cost += batch_cost

                total_units = save_checkpoint(
                    output_file,
                    units=all_units,
                    errors=errors,
                    total_cost=total_cost,
                    invalid_units_rejected=invalid_units_rejected,
                    completed_subbatch_keys=completed_subbatch_keys,
                    total_groups=total_groups,
                    total_subbatches=total_subbatches,
                    articles_metadata=articles_data["metadata"],
                )
                print(
                    f"     OK: {len(units)} unitów | odrzucone: {len(rejected_units)} | koszt ${batch_cost:.4f} | "
                    f"razem ${total_cost:.4f} | checkpoint: {total_units} unitów"
                )

            except Exception as exc:
                print(f"     ERROR: {exc}")
                errors.append(
                    {
                        "articles": article_numbers,
                        "group_key": group_key,
                        "subbatch_key": subbatch_key,
                        "questions": [question["question"] for question in sub_batch],
                        "error": str(exc)[:200],
                    }
                )
                save_checkpoint(
                    output_file,
                    units=all_units,
                    errors=errors,
                    total_cost=total_cost,
                    invalid_units_rejected=invalid_units_rejected,
                    completed_subbatch_keys=completed_subbatch_keys,
                    total_groups=total_groups,
                    total_subbatches=total_subbatches,
                    articles_metadata=articles_data["metadata"],
                    exited_due_to_credit_error=is_credit_balance_error(exc),
                )
                if is_credit_balance_error(exc):
                    print("Zapisano checkpoint po błędzie kredytów. Możesz wznowić od tego miejsca.")
                    return

            time.sleep(0.5)

    unique_units_count = save_checkpoint(
        output_file,
        units=all_units,
        errors=errors,
        total_cost=total_cost,
        invalid_units_rejected=invalid_units_rejected,
        completed_subbatch_keys=completed_subbatch_keys,
        total_groups=total_groups,
        total_subbatches=total_subbatches,
        articles_metadata=articles_data["metadata"],
    )

    print(f"\n{'=' * 50}")
    print(f"Wygenerowano {unique_units_count} draft answer units")
    print(f"Błędy: {len(errors)}")
    print(f"Odrzucone unity po walidacji: {invalid_units_rejected}")
    print(f"Koszt: ${total_cost:.4f}")
    print(f"Czas:  {format_elapsed(started_at)}")
    print(f"Zapisano: {output_file}")


if __name__ == "__main__":
    main()
