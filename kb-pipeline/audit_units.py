"""
Krok 4: Auditor answer units.
Weryfikuje każdy unit względem tekstu artykułu:
- Czy answer wynika z tekstu?
- Czy legal_basis jest poprawny?
- Czy nie dodano wiedzy spoza źródła?
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import anthropic
from env_utils import get_env_value

MODEL = "claude-haiku-4-5-20251001"
BATCH_SIZE = 5

SYSTEM_PROMPT = """Jesteś audytorem prawnym. Weryfikujesz answer units dla systemu AI dla księgowych.

Dostajesz:
1. TEKST ARTYKUŁU USTAWY (źródło prawdy)
2. ANSWER UNIT do zweryfikowania

Sprawdź KAŻDY unit według tych kryteriów:

A) GROUNDING — Czy KAŻDE twierdzenie w "answer" wynika z tekstu artykułu?
   - Jeśli answer dodaje informacje spoza tekstu -> REJECTED
   - Jeśli answer upraszcza tekst, ale sens jest poprawny -> PASS

B) LEGAL_BASIS — Czy cytowany artykuł/ustęp/punkt jest poprawny?
   - Sprawdź czy podany "art. X ust. Y" faktycznie istnieje w tekście
   - Sprawdź czy quote jest wierny (nie musi być identyczny, ale sens musi się zgadzać)

C) COMPLETENESS — Czy answer nie pomija kluczowych warunków lub wyjątków z tekstu?
   - Drobne pominięcia -> PASS z komentarzem
   - Pominięcie istotnego warunku -> NEEDS_FIX

D) ACCURACY — Czy kwoty, procenty, terminy są poprawne?
   - "50%" gdy tekst mówi "50 %" -> PASS
   - "100%" gdy tekst mówi "50 %" -> FAIL

E) RELEVANCE — Czy pytanie użytkownika faktycznie dotyczy tego artykułu?
   - Jeśli pytanie dotyczy zupełnie innego tematu niż artykuł -> FAIL i REJECTED
   - Jeśli pytanie jest powiązane, ale artykuł nie odpowiada bezpośrednio -> NEEDS_FIX

Odpowiedz WYŁĄCZNIE JSON:
{
  "audits": [
    {
      "unit_id": "id unitu",
      "verdict": "VERIFIED | NEEDS_FIX | REJECTED",
      "grounding": "PASS | FAIL",
      "legal_basis_check": "PASS | FAIL",
      "completeness": "PASS | NEEDS_FIX",
      "accuracy": "PASS | FAIL",
      "relevance": "PASS | FAIL",
      "issues": ["opis problemu 1", "opis problemu 2"],
      "suggested_fix": "sugerowana poprawka (jeśli NEEDS_FIX)",
      "confidence": 0.95
    }
  ]
}

Bądź SUROWY. Lepiej odrzucić dobry unit niż przepuścić zły.
W domenie podatkowej błędna informacja jest gorsza niż brak informacji."""


def get_article_text(articles: list[dict], article_numbers: list[str]) -> str:
    texts = []
    for num in article_numbers:
        for article in articles:
            if article["article_number"] == num:
                texts.append(f"--- {article['full_id']} ---\n{article['raw_text']}")
                break
    return "\n\n".join(texts)


def audit_batch(
    client: anthropic.Anthropic,
    units: list[dict],
    article_text: str,
) -> tuple[list[dict], dict]:
    units_formatted = json.dumps(units, ensure_ascii=False, indent=2)

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"""TEKST ARTYKUŁÓW USTAWY (ŹRÓDŁO PRAWDY):

{article_text}

ANSWER UNITS DO AUDYTU:

{units_formatted}

Zaudytuj KAŻDY unit. WYŁĄCZNIE JSON.""",
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
        result = json.loads(raw[start:end])

    audits = result.get("audits", [])
    usage = response.usage
    cache_info = {
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "cache_read": getattr(usage, "cache_read_input_tokens", 0),
    }
    return audits, cache_info


def normalize_audit(audit: dict) -> dict:
    normalized = dict(audit)
    relevance = str(normalized.get("relevance", "PASS")).strip().upper() or "PASS"
    verdict = str(normalized.get("verdict", "REJECTED")).strip().upper() or "REJECTED"
    if relevance == "FAIL":
        verdict = "REJECTED"
    normalized["relevance"] = relevance
    normalized["verdict"] = verdict
    return normalized


def main() -> None:
    if len(sys.argv) < 3:
        print("Użycie: python audit_units.py articles.json draft_units.json [--output verified_units.json]")
        sys.exit(1)

    articles_path = sys.argv[1]
    draft_path = sys.argv[2]
    output_path = "verified_units.json"
    if "--output" in sys.argv:
        output_path = sys.argv[sys.argv.index("--output") + 1]

    api_key = get_env_value("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Ustaw ANTHROPIC_API_KEY")
        sys.exit(1)

    articles_data = json.loads(Path(articles_path).read_text(encoding="utf-8"))
    draft_data = json.loads(Path(draft_path).read_text(encoding="utf-8"))

    articles = articles_data["articles"]
    units = draft_data["units"]
    print(f"Unitów do audytu: {len(units)}")

    client = anthropic.Anthropic(api_key=api_key)

    groups: dict[str, dict] = {}
    for unit in units:
        source_articles = list(unit.get("_source_articles", []))
        if not source_articles and unit.get("legal_basis"):
            for legal_basis in unit["legal_basis"]:
                article_ref = legal_basis.get("article", "")
                match = re.search(r"art\.\s*(\d+[a-z]*)", article_ref, re.IGNORECASE)
                if match:
                    source_articles.append(match.group(1))
        key = "|".join(sorted(set(source_articles))) or "unknown"
        if key not in groups:
            groups[key] = {"articles": list(set(source_articles)), "units": []}
        groups[key]["units"].append(unit)

    all_audits: dict[str, dict] = {}
    total_cost = 0.0
    call_count = 0

    for group in groups.values():
        article_numbers = group["articles"]
        group_units = group["units"]
        article_text = get_article_text(articles, article_numbers) if article_numbers else "BRAK TEKSTU ARTYKUŁU"

        for start in range(0, len(group_units), BATCH_SIZE):
            batch = group_units[start:start + BATCH_SIZE]
            call_count += 1
            print(f"\n[Call {call_count}] art. {', '.join(article_numbers)} — {len(batch)} unitów...")

            clean_units = [{key: value for key, value in unit.items() if not key.startswith("_")} for unit in batch]

            try:
                audits, cache_info = audit_batch(client, clean_units, article_text)

                for audit in audits:
                    normalized_audit = normalize_audit(audit)
                    all_audits[normalized_audit.get("unit_id", "")] = normalized_audit

                cost = (
                    cache_info["input_tokens"] * 3 / 1_000_000
                    + cache_info["cache_read"] * 0.3 / 1_000_000
                    + cache_info["output_tokens"] * 15 / 1_000_000
                )
                total_cost += cost
                verdicts = [audit.get("verdict", "?") for audit in audits]
                print(f"  {', '.join(verdicts)} | ${cost:.4f}")

            except Exception as exc:
                print(f"  ERROR: {exc}")
                for unit in batch:
                    all_audits[unit.get("id", "")] = {
                        "unit_id": unit.get("id", ""),
                        "verdict": "ERROR",
                        "grounding": "FAIL",
                        "legal_basis_check": "FAIL",
                        "completeness": "NEEDS_FIX",
                        "accuracy": "FAIL",
                        "relevance": "FAIL",
                        "issues": [str(exc)[:200]],
                    }

            time.sleep(0.5)

    verified = []
    needs_fix = []
    rejected = []

    for unit in units:
        unit_id = unit.get("id", "")
        audit = normalize_audit(all_audits.get(unit_id, {"unit_id": unit_id, "verdict": "NO_AUDIT", "relevance": "FAIL"}))
        unit["_audit"] = audit
        verdict = audit.get("verdict", "NO_AUDIT")

        if verdict == "VERIFIED":
            verified.append(unit)
        elif verdict == "NEEDS_FIX":
            needs_fix.append(unit)
        else:
            rejected.append(unit)

    output = {
        "metadata": {
            "total_units": len(units),
            "verified": len(verified),
            "needs_fix": len(needs_fix),
            "rejected": len(rejected),
            "total_cost_usd": round(total_cost, 4),
            "api_calls": call_count,
        },
        "verified_units": verified,
        "needs_fix_units": needs_fix,
        "rejected_units": rejected,
    }

    Path(output_path).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    clean_kb_path = output_path.replace(".json", "_kb.json")
    clean_kb = []
    for unit in verified:
        clean = {key: value for key, value in unit.items() if not key.startswith("_")}
        clean["verified"] = True
        clean["verified_date"] = articles_data["metadata"].get("consolidated_id", "")
        clean_kb.append(clean)

    Path(clean_kb_path).write_text(json.dumps(clean_kb, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'=' * 50}")
    print(f"VERIFIED:  {len(verified)}")
    print(f"NEEDS_FIX: {len(needs_fix)}")
    print(f"REJECTED:  {len(rejected)}")
    print(f"Koszt:     ${total_cost:.4f}")
    print(f"Zapisano:  {output_path}")
    print(f"Czysta KB: {clean_kb_path}")


if __name__ == "__main__":
    main()
