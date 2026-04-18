"""Smoke test: verify retrieval-first gating on the 8 failing test questions.

Runs a lightweight dry-run of ``answer_query`` logic without LLM calls: we call
``analyze_query_requirements`` + ``_retrieve_context`` directly and report the
bypass decision per question.
"""

from __future__ import annotations

import io
import logging
import os
import sys

# Ensure an API key is set before importing config (settings loads env lazily).
os.environ.setdefault("AKTUO_APP_NAME", "Aktuo smoke test")
os.environ.setdefault("AKTUO_LAW_KNOWLEDGE_PATH", "data/seeds/law_knowledge.json")
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-smoke-test-placeholder-not-real")

from config.settings import WORKFLOW_SEED_PATH
from core.anonymizer import anonymize_text
from core.categorizer import categorize_query
from core.rag import WORKFLOW_V2_SOURCE_TYPE, _retrieve_context
from core.retriever import analyze_query_requirements


QUESTIONS = [
    "Umowy o pracę za styczeń wypłacone 15 lutego, ZUS zapłacony do 15 marca w terminie - w którym miesiącu zaliczymy składki ZUS do KUP?",
    "W 2025 miałem 3 umowy: umowa o pracę na pełen etat, umowa o pracę na pół etatu oraz umowa zlecenie. Czy mogę zastosować koszty w wysokości 4 500 zł?",
    "Podatnik ma jedno dziecko i dochody powyżej limitu (ponad 112 tys. zł). Dziecko otrzymuje orzeczenie o niepełnosprawności 30.07.2025.",
    "Samochód osobowy w leasingu. Wykorzystywany na wynajem więc odliczam 100% VAT, proporcje liczę od Netto a nie od netto+vat prawda?",
    "Podatnik ma kasę fiskalną - w pewnym roku przekroczył 20 000 zł. Twierdzi, że korzysta ze zwolnienia podmiotowego. Czy może?",
    "Czy nowopowstała spółka z o.o. może korzystać z podmiotowego zwolnienia z VAT do limitu 240 000 zł?",
    "Przez pomyłkę program do JPK ujął mi przychód za luty do stycznia. Czy pisać czynny żal?",
    "Nowo założona JDG nie ma konta bankowego, chce kupić samochód dostawczy z konta prywatnego. VAT-R złożony ale nie zarejestrowany. Czy odliczymy VAT?",
]


def _safe(text: str) -> str:
    """Encode non-ASCII as question marks for Windows cp1250 consoles."""
    return text.encode("ascii", errors="replace").decode("ascii")


def main() -> None:
    # Capture rag logger output so we can show slot_bypass / slot_fill events.
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    rag_logger = logging.getLogger("core.rag")
    rag_logger.setLevel(logging.INFO)
    rag_logger.addHandler(handler)

    bypass_count = 0
    clarif_count = 0
    legal_count = 0

    for idx, question in enumerate(QUESTIONS, start=1):
        print(f"\n=== Q{idx}: {_safe(question[:90])}... ===")
        redacted = anonymize_text(question)
        category = categorize_query(redacted)
        analysis = analyze_query_requirements(redacted)

        chunks, path, workflow_confident = _retrieve_context(
            query=redacted,
            knowledge_path=os.environ["AKTUO_LAW_KNOWLEDGE_PATH"],
            category=category,
            intent=analysis.intent,
            limit=5,
        )

        top = chunks[0] if chunks else None
        top_id = top.article_number if top else "(none)"
        top_score = top.score if top else 0.0
        top_src = top.source_type if top else "(none)"

        needs_clar = analysis.needs_clarification
        would_clarify = needs_clar and not workflow_confident

        print(f"  intent={analysis.intent} missing={analysis.missing_slots}")
        print(f"  retrieval_path={path} top={_safe(top_id)} score={top_score:.2f} src={top_src}")
        print(f"  workflow_confident={workflow_confident} needs_clar={needs_clar} -> decision: {'CLARIFY' if would_clarify else 'ANSWER'}")

        if would_clarify:
            clarif_count += 1
            rag_logger.info(
                "slot_fill_triggered: intent=%s missing=%s query=%s",
                analysis.intent,
                analysis.missing_slots,
                redacted[:100],
            )
        elif workflow_confident and needs_clar:
            bypass_count += 1
            rag_logger.info(
                "slot_bypass: draft_id=%s score=%.2f query=%s",
                top_id,
                top_score,
                redacted[:100],
            )
        else:
            # Not clarify, not bypass — either no missing slots, or non-workflow path.
            if path in {"workflow"}:
                bypass_count += 1
            else:
                legal_count += 1

    print("\n=== Summary ===")
    print(f"  Bypass/answer: {bypass_count} / {len(QUESTIONS)}")
    print(f"  Clarification: {clarif_count} / {len(QUESTIONS)}")
    print(f"  Legal (no slot issue): {legal_count} / {len(QUESTIONS)}")

    print("\n=== Log output ===")
    log_text = log_stream.getvalue()
    sys.stdout.buffer.write(_safe(log_text).encode("ascii") + b"\n")


if __name__ == "__main__":
    main()
