"""
Krok 2: Matcher pytań do artykułów.
Wysyła pytania w batchach do Claude, który wskazuje trafne artykuły.

Użycie:
    python match_questions.py articles.json questions.json --output matched.json

Wymaga: ANTHROPIC_API_KEY w env
"""

import json
import sys
import time
from pathlib import Path

import anthropic
from env_utils import get_env_value

MODEL = "claude-haiku-4-5-20251001"
BATCH_SIZE = 20  # pytań na jedno wywołanie
PREVIEW_LENGTH = 70
RATE_LIMIT_RETRIES = 4
INPUT_TOKEN_COST_PER_M = 0.25
OUTPUT_TOKEN_COST_PER_M = 1.25
CACHE_HIT_COST_PER_M = 0.03


def build_article_index(articles: list[dict]) -> str:
    """Buduje skrócony indeks artykułów do promptu."""
    lines = []
    for article in articles:
        if article["is_repealed"]:
            continue
        preview = " ".join(article["raw_text"].split())
        preview = preview[:PREVIEW_LENGTH]
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
    """Wysyła batch pytań do Claude i zwraca dopasowania."""
    questions_text = "\n".join(
        f"{i + 1}. [{question.get('topic', question.get('cat', 'fb'))}] {question['question']}"
        for i, question in enumerate(questions)
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


def main() -> None:
    if len(sys.argv) < 3:
        print("Użycie: python match_questions.py articles.json questions.json [--output matched.json]")
        sys.exit(1)

    articles_path = sys.argv[1]
    questions_path = sys.argv[2]
    output_path = "matched.json"
    if "--output" in sys.argv:
        output_path = sys.argv[sys.argv.index("--output") + 1]

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
    print(f"Indeks artykułów: {len(article_index)} znaków ({active_articles} aktywnych)")
    print(f"Pytania do dopasowania: {len(questions)}")

    client = anthropic.Anthropic(api_key=api_key)

    all_matches = []
    total_cost = 0.0

    for i in range(0, len(questions), BATCH_SIZE):
        batch = questions[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(questions) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n[Batch {batch_num}/{total_batches}] {len(batch)} pytań...")

        try:
            matches, cache_info = match_batch_with_retry(client, batch, article_index, law_name)
            all_matches.extend(matches)

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

        except Exception as exc:
            print(f"  ERROR: {exc}")
            for question in batch:
                all_matches.append(
                    {
                        "question": question["question"],
                        "matched_articles": [],
                        "primary_article": None,
                        "reasoning": f"ERROR: {str(exc)[:100]}",
                    }
                )

        if i + BATCH_SIZE < len(questions):
            time.sleep(1)

    output = {
        "metadata": {
            "total_questions": len(questions),
            "matched": sum(1 for match in all_matches if match.get("matched_articles")),
            "unmatched": sum(1 for match in all_matches if not match.get("matched_articles")),
            "total_cost_usd": round(total_cost, 4),
        },
        "matches": all_matches,
    }

    Path(output_path).write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n{'=' * 50}")
    print(f"Gotowe! {output['metadata']['matched']}/{len(questions)} pytań dopasowanych")
    print(f"Koszt całkowity: ${total_cost:.4f}")
    print(f"Zapisano: {output_path}")


if __name__ == "__main__":
    main()
