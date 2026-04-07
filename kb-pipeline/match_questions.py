"""
Krok 2: Matcher pytań do artykułów.
Wysyła pytania w batchach do Claude, który wskazuje trafne artykuły.

Wspiera checkpoint/resume per batch. Przy błędzie kredytów zapisuje postęp
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
BATCH_SIZE = 20
PREVIEW_LENGTH = 70
RATE_LIMIT_RETRIES = 4
CHECKPOINT_VERSION = 1
INPUT_TOKEN_COST_PER_M = 0.25
OUTPUT_TOKEN_COST_PER_M = 1.25
CACHE_HIT_COST_PER_M = 0.03


def is_credit_balance_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "credit balance too low" in message or "insufficient credit" in message


def build_article_index(articles: list[dict]) -> str:
    lines = []
    for article in articles:
        if article["is_repealed"]:
            continue
        preview = " ".join(article["raw_text"].split())[:PREVIEW_LENGTH]
        context = " | ".join(part for part in (article["division"], article["chapter"]) if part)
        if context:
            lines.append(f"[{article['full_id']}] {context} | {preview}")
        else:
            lines.append(f"[{article['full_id']}] {preview}")
    return "\n".join(lines)


def build_system_prompt(law_name: str) -> str:
    return f"""Jesteś ekspertem od polskiego prawa podatkowego.
Dostajesz listę pytań użytkowników i indeks artykułów ustawy: {law_name}.
Dla KAŻDEGO pytania wskaż od 1 do 5 artykułów, które są potrzebne do odpowiedzi.

ZASADY:
- Wskaż TYLKO artykuły, które bezpośrednio odpowiadają na pytanie
- Jeśli pytanie wymaga kilku artykułów (np. warunek + wyjątek), wskaż wszystkie
- Jeśli nie jesteś pewien, dodaj artykuł z flagą "uncertain": true
- Odpowiedz WYŁĄCZNIE w JSON, bez markdown, bez komentarzy

Format odpowiedzi (JSON array):
[
  {{
    "question": "treść pytania",
    "matched_articles": ["86a", "86"],
    "primary_article": "86a",
    "reasoning": "krótkie uzasadnienie po polsku"
  }}
]"""


def match_batch(
    client: anthropic.Anthropic,
    questions: list[dict],
    article_index: str,
    law_name: str,
) -> tuple[list[dict], dict]:
    questions_text = "\n".join(
        f"{index + 1}. [{question.get('topic', question.get('cat', 'fb'))}] {question['question']}"
        for index, question in enumerate(questions)
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
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
                "content": f"""INDEKS ARTYKUŁÓW USTAWY: {law_name}
{article_index}

PYTANIA DO DOPASOWANIA:
{questions_text}

Odpowiedz JSON array z dopasowaniami dla KAŻDEGO pytania.""",
            }
        ],
    )

    raw = response.content[0].text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        matches = json.loads(raw)
    except json.JSONDecodeError:
        print("  WARN: nie udało się sparsować JSON, próbuję naprawić...")
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            matches = json.loads(raw[start:end])
        else:
            raise

    usage = response.usage
    cache_info = {
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "cache_read": getattr(usage, "cache_read_input_tokens", 0),
        "cache_creation": getattr(usage, "cache_creation_input_tokens", 0),
    }
    return matches, cache_info


def match_batch_with_retry(
    client: anthropic.Anthropic,
    questions: list[dict],
    article_index: str,
    law_name: str,
) -> tuple[list[dict], dict]:
    for attempt in range(1, RATE_LIMIT_RETRIES + 1):
        try:
            return match_batch(client, questions, article_index, law_name)
        except anthropic.RateLimitError:
            if attempt == RATE_LIMIT_RETRIES:
                raise
            wait_seconds = attempt * 20
            print(f"  RATE LIMIT {attempt}/{RATE_LIMIT_RETRIES}: czekam {wait_seconds}s")
            time.sleep(wait_seconds)
    raise RuntimeError("Nie udało się dopasować pytań po ponownych próbach.")


def load_checkpoint(output_file: Path) -> tuple[dict[int, list[dict]], set[int], float]:
    if not output_file.exists():
        return {}, set(), 0.0

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    metadata = payload.get("metadata", {})
    raw_batch_results = payload.get("batch_results", {})

    batch_results = {
        int(batch_index): matches
        for batch_index, matches in raw_batch_results.items()
        if isinstance(matches, list)
    }
    completed_batches = {int(index) for index in metadata.get("completed_batches", list(batch_results.keys()))}
    total_cost = float(metadata.get("total_cost_usd", 0.0) or 0.0)
    return batch_results, completed_batches, total_cost


def save_checkpoint(
    output_file: Path,
    *,
    batch_results: dict[int, list[dict]],
    completed_batches: set[int],
    total_cost: float,
    total_questions: int,
    total_batches: int,
) -> None:
    flattened_matches: list[dict] = []
    for batch_index in sorted(batch_results):
        flattened_matches.extend(batch_results[batch_index])

    payload = {
        "metadata": {
            "checkpoint_version": CHECKPOINT_VERSION,
            "checkpoint_saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_questions": total_questions,
            "completed_batches_count": len(completed_batches),
            "total_batches": total_batches,
            "completed_batches": sorted(completed_batches),
            "matched": sum(1 for match in flattened_matches if match.get("matched_articles")),
            "unmatched": sum(1 for match in flattened_matches if not match.get("matched_articles")),
            "total_cost_usd": round(total_cost, 4),
        },
        "batch_results": {str(index): matches for index, matches in sorted(batch_results.items())},
        "matches": flattened_matches,
    }
    output_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    if len(sys.argv) < 3:
        print("Użycie: python match_questions.py articles.json questions.json [--output matched.json]")
        sys.exit(1)

    articles_path = sys.argv[1]
    questions_path = sys.argv[2]
    output_path = "matched.json"
    if "--output" in sys.argv:
        output_path = sys.argv[sys.argv.index("--output") + 1]
    output_file = Path(output_path)

    api_key = get_env_value("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Ustaw ANTHROPIC_API_KEY")
        sys.exit(1)

    articles_data = json.loads(Path(articles_path).read_text(encoding="utf-8"))
    questions = json.loads(Path(questions_path).read_text(encoding="utf-8"))

    articles = articles_data["articles"]
    law_name = articles_data.get("metadata", {}).get("short_name") or articles_data.get("metadata", {}).get("law_name", "ustawa")
    article_index = build_article_index(articles)
    active_articles = len([article for article in articles if not article["is_repealed"]])
    total_batches = (len(questions) + BATCH_SIZE - 1) // BATCH_SIZE

    print(f"Indeks artykułów: {len(article_index)} znaków ({active_articles} aktywnych)")
    print(f"Pytania do dopasowania: {len(questions)}")
    print(f"Batch size: {BATCH_SIZE}, liczba batchy: {total_batches}")

    client = anthropic.Anthropic(api_key=api_key)
    batch_results, completed_batches, total_cost = load_checkpoint(output_file)
    if completed_batches:
        print(f"Resume z checkpointu: {len(completed_batches)}/{total_batches} batchy, koszt ${total_cost:.4f}")
    else:
        print("Start od zera — brak checkpointu.")

    for batch_index, start in enumerate(range(0, len(questions), BATCH_SIZE)):
        batch_number = batch_index + 1
        batch = questions[start:start + BATCH_SIZE]

        if batch_index in completed_batches:
            print(f"\n[Batch {batch_number}/{total_batches}] SKIP (checkpoint)")
            continue

        print(f"\n[Batch {batch_number}/{total_batches}] {len(batch)} pytań...")

        try:
            matches, cache_info = match_batch_with_retry(client, batch, article_index, law_name)
            batch_results[batch_index] = matches
            completed_batches.add(batch_index)

            input_cost = cache_info["input_tokens"] * INPUT_TOKEN_COST_PER_M / 1_000_000
            cached_cost = cache_info["cache_read"] * CACHE_HIT_COST_PER_M / 1_000_000
            output_cost = cache_info["output_tokens"] * OUTPUT_TOKEN_COST_PER_M / 1_000_000
            batch_cost = input_cost + cached_cost + output_cost
            total_cost += batch_cost

            print(f"  OK: {len(matches)} dopasowań")
            print(
                f"  Tokeny: {cache_info['input_tokens']} in, "
                f"{cache_info['output_tokens']} out, cache read: {cache_info['cache_read']}"
            )
            print(f"  Koszt: ${batch_cost:.4f}")
            save_checkpoint(
                output_file,
                batch_results=batch_results,
                completed_batches=completed_batches,
                total_cost=total_cost,
                total_questions=len(questions),
                total_batches=total_batches,
            )

        except Exception as exc:
            if is_credit_balance_error(exc):
                print(f"  CREDIT ERROR: {exc}")
                save_checkpoint(
                    output_file,
                    batch_results=batch_results,
                    completed_batches=completed_batches,
                    total_cost=total_cost,
                    total_questions=len(questions),
                    total_batches=total_batches,
                )
                print("Zapisano checkpoint po błędzie kredytów. Możesz wznowić od tego miejsca.")
                return

            print(f"  ERROR: {exc}")
            batch_results[batch_index] = [
                {
                    "question": question["question"],
                    "matched_articles": [],
                    "primary_article": None,
                    "reasoning": f"ERROR: {str(exc)[:100]}",
                }
                for question in batch
            ]
            completed_batches.add(batch_index)
            save_checkpoint(
                output_file,
                batch_results=batch_results,
                completed_batches=completed_batches,
                total_cost=total_cost,
                total_questions=len(questions),
                total_batches=total_batches,
            )

        if batch_number < total_batches:
            time.sleep(1)

    flattened_matches = []
    for index in sorted(batch_results):
        flattened_matches.extend(batch_results[index])

    print(f"\n{'=' * 50}")
    print(f"Gotowe! {sum(1 for match in flattened_matches if match.get('matched_articles'))}/{len(questions)} pytań dopasowanych")
    print(f"Koszt całkowity: ${total_cost:.4f}")
    print(f"Zapisano: {output_file}")


if __name__ == "__main__":
    main()
