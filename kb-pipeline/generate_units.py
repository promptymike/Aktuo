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

MODEL = "claude-sonnet-4-20250514"

# System prompt — cachowany, identyczny dla każdego wywołania
SYSTEM_PROMPT = """Jesteś ekspertem od polskiego prawa podatkowego. Generujesz ANSWER UNITS dla systemu RAG.

Answer unit to strukturalna jednostka wiedzy, która odpowiada na JEDNO konkretne pytanie księgowego/podatkowca.

TWARDE ZASADY:
1. Odpowiedź musi wynikać WYŁĄCZNIE z podanego tekstu artykułu. NIGDY nie dodawaj wiedzy spoza tekstu.
2. Cytuj DOKŁADNY artykuł, ustęp i punkt (np. "art. 86a ust. 1 pkt 2 lit. a").
3. Jeśli tekst artykułu nie wystarcza do pełnej odpowiedzi, ustaw "requires_verification": true.
4. Odpowiedź ma być PRAKTYCZNA — napisana językiem zrozumiałym dla księgowego, nie prawniczym.
5. Odpowiedź powinna mieć 2-5 zdań. Konkret, nie esej.
6. Warunki i wyjątki MUSZĄ wynikać z tekstu, nie z Twojej wiedzy.

FORMAT ODPOWIEDZI — WYŁĄCZNIE JSON, bez markdown:
{
  "units": [
    {
      "id": "vat-{numer_artykulu}-{krótki-slug}",
      "question_intent": "Pytanie w formie naturalnej",
      "question_patterns": ["wariant 1", "wariant 2", "wariant 3"],
      "answer": "Odpowiedź 2-5 zdań. Praktyczna, konkretna.",
      "legal_basis": [
        {
          "law": "Ustawa o VAT",
          "article": "art. 86a ust. 1",
          "quote": "kluczowy fragment z tekstu artykułu (max 1 zdanie)"
        }
      ],
      "conditions": ["warunek 1 z tekstu", "warunek 2"],
      "exceptions": ["wyjątek 1 z tekstu"],
      "taxpayer_type": ["osoba_fizyczna_dg", "osoba_prawna", "ryczalt", "vat_czynny", "vat_zwolniony"],
      "topic": "kategoria tematu",
      "difficulty": "easy|medium|hard",
      "requires_verification": false
    }
  ]
}

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


def generate_units_for_group(
    client: anthropic.Anthropic,
    questions: list[dict],
    article_text: str,
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
            "text": SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{
            "role": "user",
            "content": f"""TEKST ARTYKUŁÓW USTAWY O VAT:

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


def group_by_articles(matches: list[dict]) -> dict:
    """Grupuje pytania po zestawie artykułów — minimalizuje wywołania API."""
    groups = {}
    for m in matches:
        arts = m.get("matched_articles", [])
        if not arts:
            continue
        key = "|".join(sorted(arts))
        if key not in groups:
            groups[key] = {"articles": arts, "questions": []}
        groups[key]["questions"].append({
            "question": m["question"],
            "topic": m.get("topic", ""),
            "primary_article": m.get("primary_article", arts[0]),
        })
    return groups


def main():
    if len(sys.argv) < 3:
        print("Użycie: python generate_units.py articles.json matched.json [--output draft_units.json]")
        sys.exit(1)

    articles_path = sys.argv[1]
    matched_path = sys.argv[2]
    output_path = "draft_units.json"
    if "--output" in sys.argv:
        output_path = sys.argv[sys.argv.index("--output") + 1]

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Ustaw ANTHROPIC_API_KEY")
        sys.exit(1)

    articles_data = json.loads(Path(articles_path).read_text(encoding="utf-8"))
    matched_data = json.loads(Path(matched_path).read_text(encoding="utf-8"))

    articles = articles_data["articles"]
    matches = matched_data["matches"]

    # Grupuj pytania po artykułach
    groups = group_by_articles(matches)
    print(f"Pytań z dopasowaniem: {sum(len(g['questions']) for g in groups.values())}")
    print(f"Grup artykułów: {len(groups)} (= tyle wywołań API)")

    client = anthropic.Anthropic(api_key=api_key)

    all_units = []
    total_cost = 0
    errors = []

    for i, (key, group) in enumerate(groups.items()):
        article_nums = group["articles"]
        questions = group["questions"]
        article_text = get_article_text(articles, article_nums)

        print(f"\n[{i+1}/{len(groups)}] art. {', '.join(article_nums)} — {len(questions)} pytań ({len(article_text)} znaków)...")

        # Jeśli tekst artykułu za długi, split na sub-batche pytań
        if len(questions) > 10:
            sub_batches = [questions[j:j+10] for j in range(0, len(questions), 10)]
        else:
            sub_batches = [questions]

        for sb_idx, sub_batch in enumerate(sub_batches):
            try:
                units, cache_info = generate_units_for_group(client, sub_batch, article_text)

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

                print(f"  {'Sub-batch '+str(sb_idx+1)+': ' if len(sub_batches)>1 else ''}{len(units)} units | ${batch_cost:.4f} | cache: {cache_info['cache_read']} tokens")

            except Exception as e:
                print(f"  ERROR: {e}")
                errors.append({"articles": article_nums, "error": str(e)[:200]})

            time.sleep(0.5)  # rate limiting

    # Deduplikacja po ID
    seen_ids = set()
    unique_units = []
    for u in all_units:
        uid = u.get("id", "")
        if uid and uid in seen_ids:
            uid = uid + f"-{len(seen_ids)}"
            u["id"] = uid
        seen_ids.add(uid)
        unique_units.append(u)

    output = {
        "metadata": {
            "total_units": len(unique_units),
            "total_cost_usd": round(total_cost, 4),
            "errors": len(errors),
            "law": articles_data["metadata"],
        },
        "units": unique_units,
        "errors": errors,
    }

    Path(output_path).write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n{'='*50}")
    print(f"Wygenerowano {len(unique_units)} draft answer units")
    print(f"Błędy: {len(errors)}")
    print(f"Koszt: ${total_cost:.4f}")
    print(f"Zapisano: {output_path}")


if __name__ == "__main__":
    main()
