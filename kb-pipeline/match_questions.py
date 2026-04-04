"""
Krok 2: Matcher pytań do artykułów.
Wysyła pytania w batchach do Claude, który wskazuje relevantne artykuły.

Użycie:
    python match_questions.py articles.json questions.json --output matched.json

Wymaga: ANTHROPIC_API_KEY w env
"""

import json
import os
import sys
import time
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-4-20250514"
BATCH_SIZE = 20  # pytań na jedno wywołanie


def build_article_index(articles: list[dict]) -> str:
    """Buduje skrócony indeks artykułów do promptu."""
    lines = []
    for a in articles:
        if a["is_repealed"]:
            continue
        # Pierwsze 200 znaków raw_text jako podgląd
        preview = a["raw_text"][:200].replace("\n", " ")
        lines.append(f"[{a['full_id']}] {a['division']} | {preview}")
    return "\n".join(lines)


SYSTEM_PROMPT = """Jesteś ekspertem od polskiej ustawy o VAT.
Dostajesz listę pytań użytkowników i indeks artykułów ustawy.
Dla KAŻDEGO pytania wskaż od 1 do 5 artykułów, które są potrzebne do odpowiedzi.

ZASADY:
- Wskaż TYLKO artykuły które BEZPOŚREDNIO odpowiadają na pytanie
- Jeśli pytanie wymaga kilku artykułów (np. warunek + wyjątek), wskaż wszystkie
- Jeśli nie jesteś pewien, dodaj artykuł z flagą "uncertain": true
- Odpowiedz WYŁĄCZNIE w JSON, bez markdown, bez komentarzy

Format odpowiedzi (JSON array):
[
  {
    "question": "treść pytania",
    "matched_articles": ["86a", "86"],
    "primary_article": "86a",
    "reasoning": "krótkie uzasadnienie po polsku"
  }
]"""


def match_batch(
    client: anthropic.Anthropic,
    questions: list[dict],
    article_index: str,
) -> list[dict]:
    """Wysyła batch pytań do Claude i zwraca dopasowania."""
    questions_text = "\n".join(
        f"{i+1}. [{q['topic']}] {q['question']}"
        for i, q in enumerate(questions)
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=[{
            "type": "text",
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{
            "role": "user",
            "content": f"""INDEKS ARTYKUŁÓW USTAWY O VAT:
{article_index}

PYTANIA DO DOPASOWANIA:
{questions_text}

Odpowiedz JSON array z dopasowaniami dla KAŻDEGO pytania.""",
        }],
    )

    raw = response.content[0].text.strip()
    # Wyczyść ewentualne markdown backticki
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        matches = json.loads(raw)
    except json.JSONDecodeError:
        print(f"  WARN: nie udało się sparsować JSON, próbuję naprawić...")
        # Spróbuj wyciąć JSON array
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            matches = json.loads(raw[start:end])
        else:
            raise

    # Dodaj metadata z cache
    usage = response.usage
    cache_info = {
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "cache_read": getattr(usage, "cache_read_input_tokens", 0),
        "cache_creation": getattr(usage, "cache_creation_input_tokens", 0),
    }

    return matches, cache_info


def main():
    if len(sys.argv) < 3:
        print("Użycie: python match_questions.py articles.json questions.json [--output matched.json]")
        sys.exit(1)

    articles_path = sys.argv[1]
    questions_path = sys.argv[2]
    output_path = "matched.json"
    if "--output" in sys.argv:
        output_path = sys.argv[sys.argv.index("--output") + 1]

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Ustaw ANTHROPIC_API_KEY")
        sys.exit(1)

    # Załaduj dane
    articles_data = json.loads(Path(articles_path).read_text(encoding="utf-8"))
    questions = json.loads(Path(questions_path).read_text(encoding="utf-8"))

    articles = articles_data["articles"]
    article_index = build_article_index(articles)
    print(f"Indeks artykułów: {len(article_index)} znaków ({len([a for a in articles if not a['is_repealed']])} aktywnych)")
    print(f"Pytań do dopasowania: {len(questions)}")

    client = anthropic.Anthropic(api_key=api_key)

    # Przetwarzaj w batchach
    all_matches = []
    total_cost = 0

    for i in range(0, len(questions), BATCH_SIZE):
        batch = questions[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(questions) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n[Batch {batch_num}/{total_batches}] {len(batch)} pytań...")

        try:
            matches, cache_info = match_batch(client, batch, article_index)
            all_matches.extend(matches)

            # Kalkulacja kosztu
            input_cost = cache_info["input_tokens"] * 3 / 1_000_000
            cached_cost = cache_info["cache_read"] * 0.3 / 1_000_000
            output_cost = cache_info["output_tokens"] * 15 / 1_000_000
            batch_cost = input_cost + cached_cost + output_cost
            total_cost += batch_cost

            print(f"  OK: {len(matches)} dopasowań")
            print(f"  Tokeny: {cache_info['input_tokens']} in, {cache_info['output_tokens']} out, cache read: {cache_info['cache_read']}")
            print(f"  Koszt: ${batch_cost:.4f}")

        except Exception as e:
            print(f"  ERROR: {e}")
            # Dodaj pytania z tego batcha jako unmatched
            for q in batch:
                all_matches.append({
                    "question": q["question"],
                    "matched_articles": [],
                    "primary_article": None,
                    "reasoning": f"ERROR: {str(e)[:100]}",
                })

        # Rate limiting
        if i + BATCH_SIZE < len(questions):
            time.sleep(1)

    # Zapisz wyniki
    output = {
        "metadata": {
            "total_questions": len(questions),
            "matched": sum(1 for m in all_matches if m.get("matched_articles")),
            "unmatched": sum(1 for m in all_matches if not m.get("matched_articles")),
            "total_cost_usd": round(total_cost, 4),
        },
        "matches": all_matches,
    }

    Path(output_path).write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n{'='*50}")
    print(f"Gotowe! {output['metadata']['matched']}/{len(questions)} pytań dopasowanych")
    print(f"Koszt całkowity: ${total_cost:.4f}")
    print(f"Zapisano: {output_path}")


if __name__ == "__main__":
    main()
