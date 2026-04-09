from __future__ import annotations

import json

import core.retriever as retriever


def test_load_chunks_uses_cache_and_invalidates_on_file_change(tmp_path, monkeypatch) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106e",
                    "category": "fakturowanie",
                    "verified_date": "",
                    "question_intent": "Co powinna zawierać faktura?",
                    "content": "Faktura zawiera dane podstawowe.",
                }
            ]
        ),
        encoding="utf-8",
    )

    call_count = {"count": 0}
    original_load_seed_laws = retriever.load_seed_laws

    def counting_load_seed_laws(path):
        call_count["count"] += 1
        return original_load_seed_laws(path)

    monkeypatch.setattr(retriever, "load_seed_laws", counting_load_seed_laws)

    retriever.load_chunks(seed_file)
    retriever.load_chunks(seed_file)
    assert call_count["count"] == 1

    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106j",
                    "category": "faktury_korygujące",
                    "verified_date": "",
                    "question_intent": "Kiedy wystawia się fakturę korygującą?",
                    "content": "Faktura korygująca poprawia błąd.",
                }
            ]
        ),
        encoding="utf-8",
    )

    retriever.load_chunks(seed_file)
    assert call_count["count"] == 2
