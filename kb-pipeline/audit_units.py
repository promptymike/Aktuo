"""
Krok 4: Auditor answer units.
Wspiera checkpoint/resume per batch. Przy błędzie kredytów zapisuje postęp
i kończy się czysto, aby kolejny run mógł kontynuować od miejsca przerwania.
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
BATCH_SIZE = 15
CHECKPOINT_VERSION = 1

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


def is_credit_balance_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "credit balance too low" in message or "insufficient credit" in message


def get_article_text(articles: list[dict], article_numbers: list[str]) -> str:
    texts = []
    for number in article_numbers:
        for article in articles:
            if article["article_number"] == number:
                texts.append(f"--- {article['full_id']} ---\n{article['raw_text']}")
                break
    return "\n\n".join(texts)


def make_group_key(article_numbers: list[str]) -> str:
    return "|".join(sorted(set(article_numbers))) or "unknown"


def make_batch_key(group_key: str, batch_index: int) -> str:
    return f"{group_key}::batch::{batch_index}"


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


def build_groups(units: list[dict]) -> dict[str, dict]:
    groups: dict[str, dict] = {}
    for unit in units:
        source_articles = list(unit.get("_source_articles", []))
        if not source_articles and unit.get("legal_basis"):
            for legal_basis in unit["legal_basis"]:
                article_ref = legal_basis.get("article", "")
                match = re.search(r"art\.\s*(\d+[a-z]*)", article_ref, re.IGNORECASE)
                if match:
                    source_articles.append(match.group(1))
        group_key = make_group_key(source_articles)
        if group_key not in groups:
            groups[group_key] = {"articles": list(set(source_articles)), "units": []}
        groups[group_key]["units"].append(unit)
    return groups


def build_output_payload(
    units: list[dict],
    audits_by_unit_id: dict[str, dict],
    *,
    total_cost: float,
    api_calls: int,
    completed_batch_keys: set[str],
) -> dict:
    verified_units = []
    needs_fix_units = []
    rejected_units = []

    for unit in units:
        unit_id = unit.get("id", "")
        audit = normalize_audit(audits_by_unit_id.get(unit_id, {"unit_id": unit_id, "verdict": "NO_AUDIT", "relevance": "FAIL"}))
        enriched_unit = dict(unit)
        enriched_unit["_audit"] = audit
        verdict = audit.get("verdict", "NO_AUDIT")

        if verdict == "VERIFIED":
            verified_units.append(enriched_unit)
        elif verdict == "NEEDS_FIX":
            needs_fix_units.append(enriched_unit)
        else:
            rejected_units.append(enriched_unit)

    return {
        "metadata": {
            "checkpoint_version": CHECKPOINT_VERSION,
            "checkpoint_saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "batch_size": BATCH_SIZE,
            "completed_batches_count": len(completed_batch_keys),
            "completed_batch_keys": sorted(completed_batch_keys),
            "total_units": len(units),
            "verified": len(verified_units),
            "needs_fix": len(needs_fix_units),
            "rejected": len(rejected_units),
            "total_cost_usd": round(total_cost, 4),
            "api_calls": api_calls,
        },
        "verified_units": verified_units,
        "needs_fix_units": needs_fix_units,
        "rejected_units": rejected_units,
    }


def save_checkpoint(
    output_file: Path,
    *,
    units: list[dict],
    audits_by_unit_id: dict[str, dict],
    total_cost: float,
    api_calls: int,
    completed_batch_keys: set[str],
    articles_metadata: dict,
    exited_due_to_credit_error: bool = False,
) -> dict:
    payload = build_output_payload(
        units,
        audits_by_unit_id,
        total_cost=total_cost,
        api_calls=api_calls,
        completed_batch_keys=completed_batch_keys,
    )
    payload["metadata"]["exited_due_to_credit_error"] = exited_due_to_credit_error
    output_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    clean_kb_path = output_file.with_name(output_file.stem + "_kb.json")
    clean_kb = []
    for unit in payload["verified_units"]:
        clean = {key: value for key, value in unit.items() if not key.startswith("_")}
        clean["verified"] = True
        clean["verified_date"] = articles_metadata.get("consolidated_id", "")
        clean_kb.append(clean)
    clean_kb_path.write_text(json.dumps(clean_kb, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_checkpoint(output_file: Path) -> tuple[dict[str, dict], set[str], float, int]:
    if not output_file.exists():
        return {}, set(), 0.0, 0

    payload = json.loads(output_file.read_text(encoding="utf-8"))
    metadata = payload.get("metadata", {})
    completed_batch_keys = {str(key) for key in metadata.get("completed_batch_keys", [])}
    total_cost = float(metadata.get("total_cost_usd", 0.0) or 0.0)
    api_calls = int(metadata.get("api_calls", 0) or 0)

    audits_by_unit_id: dict[str, dict] = {}
    for collection_name in ("verified_units", "needs_fix_units", "rejected_units"):
        for unit in payload.get(collection_name, []):
            audit = unit.get("_audit")
            if isinstance(audit, dict):
                audits_by_unit_id[str(unit.get("id", ""))] = normalize_audit(audit)

    return audits_by_unit_id, completed_batch_keys, total_cost, api_calls


def main() -> None:
    if len(sys.argv) < 3:
        print("Użycie: python audit_units.py articles.json draft_units.json [--output verified_units.json]")
        sys.exit(1)

    articles_path = sys.argv[1]
    draft_path = sys.argv[2]
    output_path = "verified_units.json"
    if "--output" in sys.argv:
        output_path = sys.argv[sys.argv.index("--output") + 1]
    output_file = Path(output_path)

    api_key = get_env_value("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Ustaw ANTHROPIC_API_KEY")
        sys.exit(1)

    articles_data = json.loads(Path(articles_path).read_text(encoding="utf-8"))
    draft_data = json.loads(Path(draft_path).read_text(encoding="utf-8"))
    articles = articles_data["articles"]
    units = draft_data["units"]
    print(f"Unitów do audytu: {len(units)}")
    print(f"Batch size: {BATCH_SIZE}")

    client = anthropic.Anthropic(api_key=api_key)
    groups = build_groups(units)
    total_batches = sum(max(1, (len(group["units"]) + BATCH_SIZE - 1) // BATCH_SIZE) for group in groups.values())

    audits_by_unit_id, completed_batch_keys, total_cost, api_calls = load_checkpoint(output_file)
    if completed_batch_keys:
        print(f"Resume z checkpointu: {len(completed_batch_keys)}/{total_batches} batchy, koszt ${total_cost:.4f}")
    else:
        print("Start od zera — brak checkpointu.")

    for group_key, group in groups.items():
        article_numbers = group["articles"]
        group_units = group["units"]
        article_text = get_article_text(articles, article_numbers) if article_numbers else "BRAK TEKSTU ARTYKUŁU"

        for batch_index, start in enumerate(range(0, len(group_units), BATCH_SIZE), start=1):
            batch_key = make_batch_key(group_key, batch_index)
            if batch_key in completed_batch_keys:
                print(f"\n[Call {len(completed_batch_keys) + 1}] art. {', '.join(article_numbers)} — SKIP (checkpoint)")
                continue

            batch = group_units[start:start + BATCH_SIZE]
            api_calls += 1
            print(f"\n[Call {api_calls}] art. {', '.join(article_numbers)} — {len(batch)} unitów...")
            clean_units = [{key: value for key, value in unit.items() if not key.startswith('_')} for unit in batch]

            try:
                audits, cache_info = audit_batch(client, clean_units, article_text)
                for audit in audits:
                    normalized_audit = normalize_audit(audit)
                    audits_by_unit_id[normalized_audit.get("unit_id", "")] = normalized_audit

                cost = (
                    cache_info["input_tokens"] * 3 / 1_000_000
                    + cache_info["cache_read"] * 0.3 / 1_000_000
                    + cache_info["output_tokens"] * 15 / 1_000_000
                )
                total_cost += cost
                completed_batch_keys.add(batch_key)
                save_checkpoint(
                    output_file,
                    units=units,
                    audits_by_unit_id=audits_by_unit_id,
                    total_cost=total_cost,
                    api_calls=api_calls,
                    completed_batch_keys=completed_batch_keys,
                    articles_metadata=articles_data["metadata"],
                )
                verdicts = [audit.get("verdict", "?") for audit in audits]
                print(f"  {', '.join(verdicts)} | ${cost:.4f}")

            except Exception as exc:
                print(f"  ERROR: {exc}")
                save_checkpoint(
                    output_file,
                    units=units,
                    audits_by_unit_id=audits_by_unit_id,
                    total_cost=total_cost,
                    api_calls=api_calls,
                    completed_batch_keys=completed_batch_keys,
                    articles_metadata=articles_data["metadata"],
                    exited_due_to_credit_error=is_credit_balance_error(exc),
                )
                if is_credit_balance_error(exc):
                    print("Zapisano checkpoint po błędzie kredytów. Możesz wznowić od tego miejsca.")
                    return
                for unit in batch:
                    audits_by_unit_id[unit.get("id", "")] = {
                        "unit_id": unit.get("id", ""),
                        "verdict": "REJECTED",
                        "grounding": "FAIL",
                        "legal_basis_check": "FAIL",
                        "completeness": "NEEDS_FIX",
                        "accuracy": "FAIL",
                        "relevance": "FAIL",
                        "issues": [str(exc)[:200]],
                    }
                completed_batch_keys.add(batch_key)
                save_checkpoint(
                    output_file,
                    units=units,
                    audits_by_unit_id=audits_by_unit_id,
                    total_cost=total_cost,
                    api_calls=api_calls,
                    completed_batch_keys=completed_batch_keys,
                    articles_metadata=articles_data["metadata"],
                )

            time.sleep(0.5)

    payload = save_checkpoint(
        output_file,
        units=units,
        audits_by_unit_id=audits_by_unit_id,
        total_cost=total_cost,
        api_calls=api_calls,
        completed_batch_keys=completed_batch_keys,
        articles_metadata=articles_data["metadata"],
    )

    print(f"\n{'=' * 50}")
    print(f"VERIFIED:  {payload['metadata']['verified']}")
    print(f"NEEDS_FIX: {payload['metadata']['needs_fix']}")
    print(f"REJECTED:  {payload['metadata']['rejected']}")
    print(f"Koszt:     ${payload['metadata']['total_cost_usd']:.4f}")
    print(f"Zapisano:  {output_file}")
    print(f"Czysta KB: {output_file.with_name(output_file.stem + '_kb.json')}")


if __name__ == "__main__":
    main()
