from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.curate_kb_and_synonyms import (
    build_curation_report,
    canonicalize_law_name,
    curate_kb_units,
    curate_synonyms,
    has_legal_reference,
    kb_duplicate_key,
    merge_kb_additions,
    merge_synonym_additions,
    review_kb_units_interactively,
    review_synonyms_interactively,
    run_curation,
)


def make_unit(
    *,
    law_name: str = "Ustawa o VAT",
    article_number: str = "art. 86",
    category: str = "vat",
    content: str = (
        "Podatnik ma prawo do odliczenia VAT, jeżeli nabyte towary i usługi służą "
        "czynnościom opodatkowanym. Przepis wskazuje warunek związku z działalnością "
        "opodatkowaną oraz regułę rozliczenia podatku naliczonego."
    ),
    source_questions: list[str] | None = None,
    reason: str = "proposed from coverage gap",
) -> dict[str, object]:
    return {
        "law_name": law_name,
        "article_number": article_number,
        "category": category,
        "content": content,
        "source_questions": source_questions or ["Czy można odliczyć VAT od zakupu?"],
        "reason": reason,
    }


def make_synonym(
    *,
    slang: str = "IFT2R",
    expanded: str = "formularz IFT-2R",
    total_freq: int = 12,
    source_questions: list[str] | None = None,
) -> dict[str, object]:
    return {
        "slang": slang,
        "expanded": expanded,
        "total_freq": total_freq,
        "source_questions": source_questions
        or ["Czy trzeba składać IFT2R do subskrypcji zagranicznych?"],
    }


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_duplicate_rejection() -> None:
    existing = [make_unit()]
    accepted, rejected = curate_kb_units([make_unit()], existing)
    assert accepted == []
    assert rejected[0]["reason"] == "duplicate kb unit"


def test_placeholder_weak_kb_unit_rejection() -> None:
    weak = make_unit(
        content="Brak danych i nie wynika z przepisu, jak należy postąpić w tej sytuacji." * 4
    )
    accepted, rejected = curate_kb_units([weak], [])
    assert accepted == []
    assert rejected[0]["reason"] == "weak placeholder content"


def test_missing_field_rejection() -> None:
    broken = make_unit(category="")
    accepted, rejected = curate_kb_units([broken], [])
    assert accepted == []
    assert rejected[0]["reason"].startswith("missing fields:")


def test_valid_kb_unit_acceptance() -> None:
    accepted, rejected = curate_kb_units([make_unit()], [])
    assert len(accepted) == 1
    assert rejected == []
    assert accepted[0]["question_intent"] == "Czy można odliczyć VAT od zakupu?"


def test_rejects_missing_legal_reference() -> None:
    accepted, rejected = curate_kb_units([make_unit(article_number="poz. 12")], [])
    assert accepted == []
    assert rejected[0]["reason"] == "invalid article reference"


def test_rejects_missing_legal_grounding() -> None:
    bland = make_unit(
        content=(
            "Ten tekst opisuje temat bardzo ogólnie i bez żadnych warunków merytorycznych. "
            "To luźny komentarz redakcyjny, który nie wskazuje obowiązków, terminów ani reguł."
        )
    )
    accepted, rejected = curate_kb_units([bland], [])
    assert accepted == []
    assert rejected[0]["reason"] == "missing concrete legal grounding"


def test_canonicalizes_noisy_law_name_from_category() -> None:
    noisy = make_unit(
        law_name="Ustawa , 894, 896, 1203. DZIAL I Przepisy ogólne",
        category="vat",
    )
    accepted, _ = curate_kb_units([noisy], [])
    assert accepted[0]["law_name"] == "Ustawa o VAT"


def test_noisy_synonym_rejection() -> None:
    accepted, rejected = curate_synonyms([make_synonym(slang="COMARCH", expanded="system Comarch")], [])
    assert accepted == []
    assert rejected[0]["reason"] == "noise or brand synonym"


def test_valid_synonym_acceptance() -> None:
    accepted, rejected = curate_synonyms([make_synonym()], [])
    assert len(accepted) == 1
    assert rejected == []
    assert accepted[0]["short"] == "IFT2R"
    assert accepted[0]["source_questions_count"] == 1


def test_deduplicates_synonyms_with_and_without_hyphen() -> None:
    accepted, rejected = curate_synonyms(
        [
            make_synonym(slang="IFT2R"),
            make_synonym(slang="IFT-2R", expanded="informacja IFT-2R"),
        ],
        [],
    )
    assert len(accepted) == 1
    assert len(rejected) == 1
    assert rejected[0]["reason"] == "duplicate proposed synonym"


def test_rejects_ambiguous_short_token() -> None:
    accepted, rejected = curate_synonyms([make_synonym(slang="US", expanded="urząd skarbowy")], [])
    assert accepted == []
    assert rejected[0]["reason"] == "ambiguous short token"


def test_merge_without_duplicates(tmp_path: Path) -> None:
    kb_path = tmp_path / "law_knowledge.json"
    slang_path = tmp_path / "slang_analysis.json"
    existing_kb = [
        {
            "law_name": "Ustawa o VAT",
            "article_number": "art. 86",
            "category": "vat",
            "verified_date": "",
            "question_intent": "seed",
            "content": make_unit()["content"],
            "source": "seed",
        }
    ]
    existing_slang = [{"short": "IFT2R", "full_phrase": "formularz IFT-2R", "freq": 1}]
    write_json(kb_path, existing_kb)
    write_json(slang_path, existing_slang)

    kb_added = merge_kb_additions(kb_path, curate_kb_units([make_unit()], existing_kb)[0])
    synonym_added = merge_synonym_additions(slang_path, curate_synonyms([make_synonym()], existing_slang)[0])

    assert kb_added == 0
    assert synonym_added == 0
    assert len(json.loads(kb_path.read_text(encoding="utf-8"))) == 1
    assert len(json.loads(slang_path.read_text(encoding="utf-8"))) == 1


def test_deterministic_sorting(tmp_path: Path) -> None:
    kb_path = tmp_path / "law_knowledge.json"
    slang_path = tmp_path / "slang_analysis.json"
    write_json(kb_path, [])
    write_json(slang_path, [])

    kb_additions = [
        {
            "law_name": "Z ustawa",
            "article_number": "art. 2",
            "category": "vat",
            "verified_date": "",
            "question_intent": "z",
            "content": "Podatnik ma obowiązek złożyć deklarację do końca miesiąca i spełnić warunki ustawowe dla rozliczenia podatku.",
            "source": "test",
        },
        {
            "law_name": "A ustawa",
            "article_number": "art. 1",
            "category": "vat",
            "verified_date": "",
            "question_intent": "a",
            "content": "Podatnik może zastosować stawkę preferencyjną, jeżeli spełni warunki i dochowa terminu określonego w ustawie.",
            "source": "test",
        },
    ]
    synonym_additions = [
        {
            "short": "ZUS",
            "full_phrase": "Zakład Ubezpieczeń Społecznych",
            "freq": 1,
            "examples": [],
            "source_questions_count": 0,
            "slang": "ZUS",
            "expanded": "Zakład Ubezpieczeń Społecznych",
        },
        {
            "short": "IFT2R",
            "full_phrase": "formularz IFT-2R",
            "freq": 20,
            "examples": [],
            "source_questions_count": 0,
            "slang": "IFT2R",
            "expanded": "formularz IFT-2R",
        },
    ]

    merge_kb_additions(kb_path, kb_additions)
    merge_synonym_additions(slang_path, synonym_additions)

    kb_result = json.loads(kb_path.read_text(encoding="utf-8"))
    slang_result = json.loads(slang_path.read_text(encoding="utf-8"))

    assert kb_result[0]["law_name"] == "A ustawa"
    assert kb_result[1]["law_name"] == "Z ustawa"
    assert slang_result[0]["short"] == "IFT2R"
    assert slang_result[1]["short"] == "ZUS"


def test_interactive_mode_with_monkeypatched_input_for_kb() -> None:
    answers = iter(["e", "cit", "Nowa treść z obowiązkiem, terminem i warunkiem ustawowym przekraczająca minimalny próg długości.", "a"])
    result = review_kb_units_interactively(
        [
            {
                **make_unit(),
                "verified_date": "",
                "question_intent": "pytanie",
                "source": "test",
            }
        ],
        input_func=lambda _: next(answers),
    )
    assert len(result) == 1
    assert result[0]["category"] == "cit"
    assert result[0]["content"].startswith("Nowa treść")


def test_interactive_mode_with_monkeypatched_input_for_synonyms() -> None:
    answers = iter(["e", "informacja IFT-2R", "a"])
    result = review_synonyms_interactively(
        [
            {
                "short": "IFT2R",
                "full_phrase": "formularz IFT-2R",
                "freq": 3,
                "examples": [],
                "source_questions_count": 1,
                "slang": "IFT2R",
                "expanded": "formularz IFT-2R",
            }
        ],
        input_func=lambda _: next(answers),
    )
    assert len(result) == 1
    assert result[0]["full_phrase"] == "informacja IFT-2R"


def test_run_curation_and_merge_creates_outputs(tmp_path: Path) -> None:
    kb_path = tmp_path / "law_knowledge.json"
    slang_path = tmp_path / "slang_analysis.json"
    proposed_kb_path = tmp_path / "proposed_kb_units.json"
    proposed_synonyms_path = tmp_path / "proposed_synonyms.json"
    curated_kb_path = tmp_path / "law_knowledge_curated_additions.json"
    curated_slang_path = tmp_path / "slang_curated_additions.json"
    report_path = tmp_path / "curation_report.json"

    write_json(kb_path, [])
    write_json(slang_path, [])
    write_json(proposed_kb_path, [make_unit()])
    write_json(proposed_synonyms_path, [make_synonym()])

    report = run_curation(
        kb_path=kb_path,
        slang_path=slang_path,
        proposed_kb_path=proposed_kb_path,
        proposed_synonyms_path=proposed_synonyms_path,
        curated_kb_path=curated_kb_path,
        curated_slang_path=curated_slang_path,
        report_path=report_path,
        merge=True,
    )

    assert report["proposed_kb_units_accepted"] == 1
    assert report["proposed_synonyms_accepted"] == 1
    assert report["merge"]["kb_added"] == 1
    assert report["merge"]["synonyms_added"] == 1
    assert curated_kb_path.exists()
    assert curated_slang_path.exists()
    assert report_path.exists()
    assert len(json.loads(kb_path.read_text(encoding="utf-8"))) == 1
    assert len(json.loads(slang_path.read_text(encoding="utf-8"))) == 1


def test_build_report_shape() -> None:
    report = build_curation_report(
        proposed_kb_units=[make_unit(), make_unit(article_number="art. 87")],
        accepted_kb_units=[to_curated_kb_like(make_unit())],
        rejected_kb_units=[{"item": "x", "reason": "duplicate kb unit"}],
        proposed_synonyms=[make_synonym()],
        accepted_synonyms=[to_curated_synonym_like(make_synonym())],
        rejected_synonyms=[],
    )
    assert report["proposed_kb_units_total"] == 2
    assert report["proposed_kb_units_accepted"] == 1
    assert report["proposed_synonyms_total"] == 1
    assert report["top_accepted_laws_by_count"]["Ustawa o VAT"] == 1


def to_curated_kb_like(unit: dict[str, object]) -> dict[str, object]:
    return {
        "law_name": unit["law_name"],
        "article_number": unit["article_number"],
        "category": unit["category"],
        "verified_date": "",
        "question_intent": "test",
        "content": unit["content"],
        "source": "test",
    }


def to_curated_synonym_like(synonym: dict[str, object]) -> dict[str, object]:
    return {
        "short": synonym["slang"],
        "full_phrase": synonym["expanded"],
        "freq": synonym["total_freq"],
        "examples": synonym["source_questions"],
        "source_questions_count": len(synonym["source_questions"]),
        "slang": synonym["slang"],
        "expanded": synonym["expanded"],
    }


def test_helper_has_legal_reference() -> None:
    assert has_legal_reference("art. 86")
    assert has_legal_reference("§ 4 ust. 1")
    assert not has_legal_reference("poz. 12")


def test_helper_kb_duplicate_key_is_normalized() -> None:
    left = kb_duplicate_key(
        {
            "law_name": "Ustawa o VAT",
            "article_number": "art. 86",
            "content": "Prawo do odliczenia VAT przy czynnościach opodatkowanych.",
        }
    )
    right = kb_duplicate_key(
        {
            "law_name": "ustawa o vat",
            "article_number": "ART. 86",
            "content": "Prawo do odliczenia VAT przy czynnościach opodatkowanych.  ",
        }
    )
    assert left == right


def test_helper_canonicalize_law_name() -> None:
    assert canonicalize_law_name("Kodeks pracy1) Preambuła i dalszy tekst") == "Kodeks pracy"
