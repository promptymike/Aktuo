from __future__ import annotations

from core.auditor import audit_answer
from core.retriever import LawChunk


def test_audit_answer_flags_expired_sources() -> None:
    expired_chunk = LawChunk(
        content="Wersja historyczna przepisu.",
        law_name="Ustawa o VAT",
        article_number="art. 86",
        category="vat",
        verified_date="2026-04-01",
        effective_to="2020-12-31",
    )
    current_chunk = LawChunk(
        content="Aktualna wersja przepisu.",
        law_name="Ustawa o VAT",
        article_number="art. 87",
        category="vat",
        verified_date="2026-04-01",
        effective_to="",
    )

    audit = audit_answer("Odpowiedź oparta na źródłach.", [expired_chunk, current_chunk])

    assert audit["grounded"] is True
    assert audit["context_count"] == 2
    assert audit["contains_expired_sources"] is True
    assert audit["sources"] == ["Ustawa o VAT art. 86", "Ustawa o VAT art. 87"]


def test_audit_answer_keeps_expired_flag_false_for_current_sources() -> None:
    chunk = LawChunk(
        content="Aktualny przepis.",
        law_name="Kodeks pracy",
        article_number="art. 94",
        category="kadry",
        verified_date="2026-04-01",
        effective_to="2099-12-31",
    )

    audit = audit_answer("Treść odpowiedzi.", [chunk])

    assert audit["contains_expired_sources"] is False
