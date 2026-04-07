"""
Krok 3: Generator answer units.
Bierze dopasowane pary (pytanie + artykuły) i generuje structured answer units.

Użycie:
    python generate_units.py articles.json matched.json --output draft_units.json

Wymaga: ANTHROPIC_API_KEY w env
"""

import json
import os
import sys
import time
from pathlib import Path

import anthropic
from env_utils import get_env_value

MODEL = "claude-haiku-4-5-20251001"
REQUEST_TIMEOUT_SECONDS = 180.0
TIMEOUT_RETRIES = 3
CHECKPOINT_VERSION = 2


def validate_generated_units(
    units: list[dict],
    *,
    group_key: str,
    article_nums: list[str],
    source_questions: list[str],
) -> tuple[list[dict], list[dict]]:
    valid_units: list[dict] = []
    rejected_units: list[dict] = []
    for idx, unit in enumerate(units, start=1):
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
                    "articles": article_nums,
                    "group_key": group_key,
                    "sub_batch_index": None,
                    "questions": source_questions,
                    "error": f"Invalid generated unit #{idx}: {', '.join(issues)}",
                }
            )
            continue

        valid_units.append(unit)

    return valid_units, rejected_units

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
      "id": "law-{{numer_artykulu}}-{{krótki-slug}}",
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
}}

taxpayer_type — wybierz TYLKO te, do których odnosi się przepis:
- "osoba_fizyczna_dg" — osoba fizyczna prowadząca działalność gospodarczą
- "osoba_prawna" — spółki, fundacje etc.
- "ryczalt" — ryczałt od przychodów ewidencjonowanych
- "vat_czynny" — czynny podatnik VAT
- "vat_zwolniony" — podatnik zwolniony z VAT
- "all" — przepis dotyczy wszystkich podatników"""


def get_article_text(articles: list[dict], article_numbers: list[str]) -> str:
    """Pobiera pełny tekst wskazanych artykułów."""
    texts = []
    for num in article_numbers:
        for a in articles:
            if a["article_number"] == num:
                texts.append(f"--- {a['full_id']} ({a['division']}) ---\n{a['raw_text']}")
                break
    return "\n\n".join(texts)


def make_group_key(article_numbers: list[str]) -> str:
    return "|".join(sorted(str(num) for num in article_numbers if num))


def generate_units_for_group(
    client: anthropic.Anthropic,
    questions: list[dict],
    article_text: str,
    law_name: str,
) -> tuple[list[dict], dict]:
    """Generuje answer units dla grupy pytań z tym samym zestawem artykułów."""
    questions_formatted = "\n".join(
        f"- {q['question']}" for q in questions
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        system=[{
            "type": "text",
            "text": build_system_prompt(law_name),
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{
            "role": "user",
            "content": f"""TEKST ARTYKUŁÓW USTAWY: {law_name}

{article_text}

PYTANIA UŻYTKOWNIKÓW (wygeneruj answer unit dla KAŻDEGO pytania):

{questions_formatted}

Wygeneruj answer units. WYŁĄCZNIE JSON.""",
        }],
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
        "cache_creation": getattr(usage, "cache_creation_input_tokens", 0),
    }

    return units, cache_info


def group_by_articles(matches: list[dict]) -> dict[str, dict]:
    """Grupuje pytania po zestawie artykułów — minimalizuje wywołania API."""
    groups = {}
    for m in matches:
        arts = m.get("matched_articles", [])
        if not arts:
            continue
        key = make_group_key(arts)
        if key not in groups:
            groups[key] = {"articles": arts, "questions": []}
        groups[key]["questions"].append({
            "question": m["question"],
            "topic": m.get("topic", ""),
            "primary_article": m.get("primary_article", arts[0]),
        })
    return groups


def deduplicate_units(units: list[dict]) -> list[dict]:
    """Deduplikuje unity po ID zachowując stabilne, unikalne identyfikatory."""
    seen_ids: set[str] = set()
    unique_units = []
    for unit in units:
        normalized = dict(unit)
        uid = str(normalized.get("id", "") or "")
        if uid:
            original_uid = uid
            suffix = 1
            while uid in seen_ids:
                suffix += 1
                uid = f"{original_uid}-{suffix}"
            normalized["id"] = uid
            seen_ids.add(uid)
        unique_units.append(normalized)
    return unique_units


def unit_group_key(unit: dict) -> str:
    source_articles = unit.get("_source_articles", [])
    if isinstance(source_articles, list):
        return make_group_key(source_articles)
    return ""


def load_checkpoint(output_path: Path) -> tuple[list[dict], list[dict], float, set[str], set[str]]:
    """Ładuje checkpoint, jeśli istnieje."""
    if not output_path.exists():
        return [], [], 0.0, set(), set()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    units = payload.get("units", [])
    errors = payload.get("errors", [])
    metadata = payload.get("metadata", {})

    if not isinstance(units, list) or not isinstance(errors, list) or not isinstance(metadata, dict):
        raise ValueError(f"Nieprawidłowy checkpoint: {output_path}")

    completed_groups = set(metadata.get("completed_group_keys", []))
    total_cost = float(metadata.get("total_cost_usd", 0.0) or 0.0)
    retry_group_keys = {
        str(error.get("group_key", "")).strip()
        for error in errors
        if str(error.get("group_key", "")).strip()
    }

    if retry_group_keys:
        units = [unit for unit in units if unit_group_key(unit) not in retry_group_keys]
        errors = [error for error in errors if str(error.get("group_key", "")).strip() not in retry_group_keys]
        completed_groups -= retry_group_keys

    return units, errors, total_cost, completed_groups, retry_group_keys


def save_checkpoint(
    output_path: Path,
    *,
    units: list[dict],
    errors: list[dict],
    invalid_units_rejected: int,
    total_cost: float,
    completed_group_keys: set[str],
    total_groups: int,
    processed_subbatches: int,
    total_subbatches: int,
    articles_metadata: dict,
) -> int:
    """Zapisuje checkpoint po każdej ukończonej grupie."""
    unique_units = deduplicate_units(units)
    payload = {
        "metadata": {
            "checkpoint_version": CHECKPOINT_VERSION,
            "checkpoint_saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "completed_groups": len(completed_group_keys),
            "total_groups": total_groups,
            "processed_subbatches": processed_subbatches,
            "total_subbatches": total_subbatches,
            "total_units": len(unique_units),
            "total_cost_usd": round(total_cost, 4),
            "errors": len(errors),
            "invalid_units_rejected": invalid_units_rejected,
            "completed_group_keys": sorted(completed_group_keys),
            "law": articles_metadata,
        },
        "units": unique_units,
        "errors": errors,
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
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
            print(
                f"  TIMEOUT {attempt}/{TIMEOUT_RETRIES}: Claude nie odpowiedział w {REQUEST_TIMEOUT_SECONDS:.0f}s"
            )
            if attempt < TIMEOUT_RETRIES:
                time.sleep(attempt)
    assert last_error is not None
    raise last_error


def main():
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

    # Grupuj pytania po artykułach
    groups = group_by_articles(matches)
    total_questions = sum(len(group["questions"]) for group in groups.values())
    total_groups = len(groups)
    total_subbatches = sum(max(1, (len(group["questions"]) + 9) // 10) for group in groups.values())
    print(f"Pytań z dopasowaniem: {total_questions}")
    print(f"Grup artykułów: {total_groups}")
    print(f"Szacowana liczba wywołań API (sub-batche): {total_subbatches}")

    client = anthropic.Anthropic(api_key=api_key, timeout=REQUEST_TIMEOUT_SECONDS)

    try:
        all_units, errors, total_cost, completed_group_keys, retry_group_keys = load_checkpoint(output_file)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    if retry_group_keys:
        print(
            f"Resume z checkpointu: ponawiam {len(retry_group_keys)} grup z błędami, "
            f"zachowano {len(completed_group_keys)} ukończonych grup i {len(all_units)} unitów."
        )
    elif completed_group_keys:
        print(
            f"Resume z checkpointu: {len(completed_group_keys)}/{total_groups} grup, "
            f"{len(all_units)} unitów, koszt ${total_cost:.4f}"
        )
    else:
        print("Start od zera — brak checkpointu.")

    processed_subbatches = sum(
        max(1, (len(groups[group_key]["questions"]) + 9) // 10)
        for group_key in completed_group_keys
        if group_key in groups
    )
    invalid_units_rejected = sum(
        1 for error in errors if str(error.get("error", "")).startswith("Invalid generated unit #")
    )
    started_at = time.time()

    for i, (key, group) in enumerate(groups.items(), start=1):
        if key in completed_group_keys:
            print(
                f"[{i}/{total_groups}] SKIP art. {', '.join(group['articles'])} "
                f"(checkpoint, elapsed {format_elapsed(started_at)})"
            )
            continue

        article_nums = group["articles"]
        questions = group["questions"]
        article_text = get_article_text(articles, article_nums)
        sub_batches = [questions[j:j + 10] for j in range(0, len(questions), 10)] or [questions]

        print(
            f"\n[{i}/{total_groups}] art. {', '.join(article_nums)} | "
            f"pytania: {len(questions)} | sub-batche: {len(sub_batches)} | "
            f"tekst: {len(article_text)} znaków | elapsed {format_elapsed(started_at)}"
        )

        for sb_idx, sub_batch in enumerate(sub_batches):
            try:
                print(
                    f"  -> Sub-batch {sb_idx + 1}/{len(sub_batches)} "
                    f"(globalnie {processed_subbatches + 1}/{total_subbatches}) "
                    f"| {len(sub_batch)} pytań"
                )
                units, cache_info = generate_units_with_retry(client, sub_batch, article_text, law_name)
                units, rejected_units = validate_generated_units(
                    units,
                    group_key=key,
                    article_nums=article_nums,
                    source_questions=[q["question"] for q in sub_batch],
                )
                errors.extend(rejected_units)
                invalid_units_rejected += len(rejected_units)

                # Dodaj source metadata do każdego unitu
                for u in units:
                    u["_source_articles"] = article_nums
                    u["_generated_from"] = [q["question"] for q in sub_batch]

                all_units.extend(units)

                input_cost = cache_info["input_tokens"] * 3 / 1_000_000
                cached_cost = cache_info["cache_read"] * 0.3 / 1_000_000
                output_cost = cache_info["output_tokens"] * 15 / 1_000_000
                batch_cost = input_cost + cached_cost + output_cost
                total_cost += batch_cost

                print(
                    f"     OK: {len(units)} unitów | odrzucone: {len(rejected_units)} | koszt ${batch_cost:.4f} | "
                    f"cache: {cache_info['cache_read']} | razem ${total_cost:.4f}"
                )

            except Exception as e:
                print(f"     ERROR: {e}")
                errors.append(
                    {
                        "articles": article_nums,
                        "group_key": key,
                        "sub_batch_index": sb_idx + 1,
                        "questions": [q["question"] for q in sub_batch],
                        "error": str(e)[:200],
                    }
                )

            processed_subbatches += 1
            time.sleep(0.5)  # rate limiting

        completed_group_keys.add(key)
        total_units = save_checkpoint(
            output_file,
            units=all_units,
            errors=errors,
            invalid_units_rejected=invalid_units_rejected,
            total_cost=total_cost,
            completed_group_keys=completed_group_keys,
            total_groups=total_groups,
            processed_subbatches=processed_subbatches,
            total_subbatches=total_subbatches,
            articles_metadata=articles_data["metadata"],
        )
        print(
            f"  CHECKPOINT: grupy {len(completed_group_keys)}/{total_groups} | "
            f"unity {total_units} | błędy {len(errors)} | odrzucone unity {invalid_units_rejected} | "
            f"elapsed {format_elapsed(started_at)} | zapisano {output_file}"
        )

    unique_units_count = save_checkpoint(
        output_file,
        units=all_units,
        errors=errors,
        invalid_units_rejected=invalid_units_rejected,
        total_cost=total_cost,
        completed_group_keys=completed_group_keys,
        total_groups=total_groups,
        processed_subbatches=processed_subbatches,
        total_subbatches=total_subbatches,
        articles_metadata=articles_data["metadata"],
    )

    print(f"\n{'='*50}")
    print(f"Wygenerowano {unique_units_count} draft answer units")
    print(f"Błędy: {len(errors)}")
    print(f"Odrzucone unity po walidacji: {invalid_units_rejected}")
    print(f"Koszt: ${total_cost:.4f}")
    print(f"Czas:  {format_elapsed(started_at)}")
    print(f"Zapisano: {output_file}")


if __name__ == "__main__":
    main()
