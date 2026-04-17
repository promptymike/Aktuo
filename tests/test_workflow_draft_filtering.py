from __future__ import annotations

import json
from pathlib import Path

from core.workflow_retriever import load_workflow_documents


def test_load_workflow_documents_skips_draft_records(tmp_path: Path) -> None:
    workflow_path = tmp_path / "workflow_seed.json"
    workflow_path.write_text(
        json.dumps(
            [
                {
                    "workflow_area": "Sprawozdania",
                    "title": "Gotowy rekord bez pola draft",
                    "category": "rachunkowosc",
                    "question_examples": ["Jak wysłać sprawozdanie?"],
                    "steps": ["Przygotuj plik.", "Wyślij dokument."],
                },
                {
                    "workflow_area": "KSeF",
                    "title": "Gotowy rekord z draft false",
                    "category": "ksef",
                    "draft": False,
                    "question_examples": ["Jak nadać uprawnienia w KSeF?"],
                    "steps": ["Wybierz użytkownika.", "Nadaj uprawnienie."],
                },
                {
                    "workflow_area": "JPK",
                    "title": "Roboczy rekord draft true",
                    "category": "jpk",
                    "draft": True,
                    "question_examples": ["Jak wysłać korektę JPK?"],
                    "steps": ["Przygotuj korektę.", "Wyślij plik."],
                },
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    documents = load_workflow_documents(workflow_path)
    titles = {document.chunk.title for document in documents}

    assert len(documents) == 2
    assert "Gotowy rekord bez pola draft" in titles
    assert "Gotowy rekord z draft false" in titles
    assert "Roboczy rekord draft true" not in titles
