"""
Krok 4: Auditor answer units.
Weryfikuje każdy unit względem tekstu artykułu:
- Czy answer wynika z tekstu?
- Czy legal_basis jest poprawny?
- Czy nie dodano wiedzy spoza źródła?

Użycie:
    python audit_units.py articles.json draft_units.json --output verified_units.json

Wymaga: ANTHROPIC_API_KEY w env
"""

import json
import os
import sys
import time
from pathlib import Path

import anthropic
from env_utils import get_env_value

MODEL = "claude-haiku-3-5-20251001"
BATCH_SIZE = 5  # unitów na wywołanie — mniejsze batche = lepsza jakość audytu

SYSTEM_PROMPT = """Jesteś audytorem prawnym. Weryfikujesz answer units dla systemu AI dla księgowych.

Dostajesz:
1. TEKST ARTYKUŁU USTAWY (źródło prawdy)
2. ANSWER UNIT do zweryfikowania

Sprawdź KAŻDY unit według tych kryteriów:

A) GROUNDING — Czy KAŻDE twierdzenie w "answer" wynika z tekstu artykułu?
   - Jeśli answer dodaje informacje spoza tekstu → REJECT
   - Jeśli answer upraszcza tekst, ale sens jest poprawny → PASS

B) LEGAL_BASIS — Czy cytowany artykuł/ustęp/punkt jest poprawny?
   - Sprawdź czy podany "art. X ust. Y" faktycznie istnieje w tekście
   - Sprawdź czy quote jest wierny (nie musi być identyczny, ale sens musi się zgadzać)

C) COMPLETENESS — Czy answer nie pomija KLUCZOWYCH warunków lub wyjątków z tekstu?
   - Drobne pominięcia → PASS z komentarzem
   - Pominięcie istotnego warunku → NEEDS_FIX

D) ACCURACY — Czy kwoty, procenty, terminy są poprawne?
   - "50%" gdy tekst mówi "50 %" → PASS
   - "100%" gdy tekst mówi "50 %" → REJECT

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
      "issues": ["opis problemu 1", "opis problemu 2"],
      "suggested_fix": "sugerowana poprawka (jeśli NEEDS_FIX)",
      "confidence": 0.95
    }
  ]
}

Bądź SUROWY. Lepiej odrzucić dobry unit niż przepuścić zły.
W domenie podatkowej błędna informacja jest gorsza niż brak informacji."""


def get_article_text(articles: list[dict], article_numbers: list[str]) -> str:
    """Pobiera tekst artykułów."""
    texts = []
    for num in article_numbers:
        for a in articles:
            if a["article_number"] == num:
                texts.append(f"--- {a['full_id']} ---\n{a['raw_text']}")
                break
    return "\n\n".join(texts)


def audit_batch(
    client: anthropic.Anthropic,
    units: list[dict],
    article_text: str,
) -> tuple[list[dict], dict]:
    """Audytuje batch unitów."""

    units_formatted = json.dumps(units, ensure_ascii=False, indent=2)

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
            "content": f"""TEKST ARTYKUŁÓW USTAWY (ŹRÓDŁO PRAWDY):

{article_text}

ANSWER UNITS DO AUDYTU:

{units_formatted}

Zaudytuj KAŻDY unit. WYŁĄCZNIE JSON.""",
        }],
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


def main():
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

    # Grupuj unity po artykułach źródłowych (żeby oszczędzić tokeny na tekst artykułu)
    groups = {}
    for u in units:
        source_arts = u.get("_source_articles", [])
        # Fallback: wyciągnij numer artykułu z legal_basis
        if not source_arts and u.get("legal_basis"):
            for lb in u["legal_basis"]:
                art = lb.get("article", "")
                # Wyciągnij numer: "art. 86a ust. 1" → "86a"
                import re
                m = re.search(r"art\.\s*(\d+[a-z]*)", art)
                if m:
                    source_arts.append(m.group(1))
        key = "|".join(sorted(set(source_arts))) or "unknown"
        if key not in groups:
            groups[key] = {"articles": list(set(source_arts)), "units": []}
        groups[key]["units"].append(u)

    all_audits = {}  # unit_id → audit result
    total_cost = 0
    call_count = 0

    for group_key, group in groups.items():
        art_nums = group["articles"]
        group_units = group["units"]
        article_text = get_article_text(articles, art_nums) if art_nums else "BRAK TEKSTU ARTYKUŁU"

        # Przetwarzaj w batchach po BATCH_SIZE
        for i in range(0, len(group_units), BATCH_SIZE):
            batch = group_units[i:i + BATCH_SIZE]
            call_count += 1
            print(f"\n[Call {call_count}] art. {', '.join(art_nums)} — {len(batch)} unitów...")

            # Przygotuj unity bez wewnętrznych metadanych
            clean_units = []
            for u in batch:
                cu = {k: v for k, v in u.items() if not k.startswith("_")}
                clean_units.append(cu)

            try:
                audits, cache_info = audit_batch(client, clean_units, article_text)

                for audit in audits:
                    uid = audit.get("unit_id", "")
                    all_audits[uid] = audit

                cost = (
                    cache_info["input_tokens"] * 3 / 1_000_000
                    + cache_info["cache_read"] * 0.3 / 1_000_000
                    + cache_info["output_tokens"] * 15 / 1_000_000
                )
                total_cost += cost
                verdicts = [a.get("verdict", "?") for a in audits]
                print(f"  {', '.join(verdicts)} | ${cost:.4f}")

            except Exception as e:
                print(f"  ERROR: {e}")
                for u in batch:
                    all_audits[u.get("id", "")] = {
                        "unit_id": u.get("id", ""),
                        "verdict": "ERROR",
                        "issues": [str(e)[:200]],
                    }

            time.sleep(0.5)

    # Rozdziel unity na verified / needs_fix / rejected
    verified = []
    needs_fix = []
    rejected = []

    for u in units:
        uid = u.get("id", "")
        audit = all_audits.get(uid, {"verdict": "NO_AUDIT"})
        u["_audit"] = audit
        verdict = audit.get("verdict", "NO_AUDIT")

        if verdict == "VERIFIED":
            verified.append(u)
        elif verdict == "NEEDS_FIX":
            needs_fix.append(u)
        else:
            rejected.append(u)

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

    Path(output_path).write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # Zapisz też czystą bazę (tylko verified, bez metadanych wewnętrznych)
    clean_kb_path = output_path.replace(".json", "_kb.json")
    clean_kb = []
    for u in verified:
        clean = {k: v for k, v in u.items() if not k.startswith("_")}
        clean["verified"] = True
        clean["verified_date"] = articles_data["metadata"].get("consolidated_id", "")
        clean_kb.append(clean)

    Path(clean_kb_path).write_text(
        json.dumps(clean_kb, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"\n{'='*50}")
    print(f"VERIFIED:  {len(verified)}")
    print(f"NEEDS_FIX: {len(needs_fix)}")
    print(f"REJECTED:  {len(rejected)}")
    print(f"Koszt:     ${total_cost:.4f}")
    print(f"Zapisano:  {output_path}")
    print(f"Czysta KB: {clean_kb_path}")


if __name__ == "__main__":
    main()
