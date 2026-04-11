"""Tests for the KB and synonym expansion script.

Verifies classification logic, slang detection, article candidate search,
and the end-to-end ``run()`` function with synthetic data.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.expand_kb_and_synonyms import (
    build_known_abbreviations,
    classify_question,
    detect_slang,
    find_candidate_articles,
    load_articles,
    load_questions,
    load_slang,
    merge_kb_units,
    merge_synonyms,
    run,
    suggest_expansion,
)
from core.retriever import LawChunk


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def synthetic_dataset(tmp_path: Path) -> Path:
    data = {
        "summary": {"total_unique": 3},
        "questions": [
            {
                "id": 1,
                "q": "Czy faktura WDT wymaga oznaczenia BFK w JPK?",
                "cat": "vat",
                "freq": 20,
            },
            {
                "id": 2,
                "q": "Jak rozliczyć IFT-2R za subskrypcje Adobe?",
                "cat": "cit",
                "freq": 15,
            },
            {
                "id": 3,
                "q": "Ulga rehabilitacyjna PIT odliczenie leków",
                "cat": "pit",
                "freq": 10,
            },
        ],
    }
    path = tmp_path / "questions.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture()
def synthetic_kb(tmp_path: Path) -> Path:
    kb = [
        {
            "law_name": "Ustawa o VAT",
            "article_number": "art. 86",
            "category": "vat",
            "verified_date": "",
            "question_intent": "Odliczenie VAT",
            "content": "Podatnik ma prawo do odliczenia VAT naliczonego...",
            "source": "test",
        },
    ]
    path = tmp_path / "law_knowledge.json"
    path.write_text(json.dumps(kb, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture()
def synthetic_slang(tmp_path: Path) -> Path:
    slang = [
        {"slang": "ksef", "expanded": "Krajowy System e-Faktur", "freq": 5},
        {"slang": "jpk", "expanded": "jednolity plik kontrolny", "freq": 3},
    ]
    path = tmp_path / "slang.json"
    path.write_text(json.dumps(slang, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture()
def synthetic_articles(tmp_path: Path) -> Path:
    articles_dir = tmp_path / "articles"
    articles_dir.mkdir()

    vat_articles = {
        "metadata": {"law_name": "Ustawa o VAT", "date": "2004-03-11"},
        "articles": [
            {
                "article_number": "106b",
                "full_id": "art. 106b",
                "raw_text": (
                    "Art. 106b. Obowiązek wystawienia faktury WDT "
                    "wewnątrzwspólnotowa dostawa towarów fakturowanie."
                ),
                "is_repealed": False,
                "char_count": 100,
            },
            {
                "article_number": "86",
                "full_id": "art. 86",
                "raw_text": (
                    "Art. 86 Prawo do odliczenia VAT naliczonego od zakupów."
                ),
                "is_repealed": False,
                "char_count": 50,
            },
        ],
    }
    (articles_dir / "articles_vat.json").write_text(
        json.dumps(vat_articles, ensure_ascii=False), encoding="utf-8"
    )

    cit_articles = {
        "metadata": {"law_name": "Ustawa o CIT", "date": "2024-01-01"},
        "articles": [
            {
                "article_number": "26",
                "full_id": "art. 26",
                "raw_text": (
                    "Art. 26. Obowiązek poboru podatku u źródła "
                    "WHT IFT-2R subskrypcja rozliczenie certyfikat "
                    "rezydencji podatkowej."
                ),
                "is_repealed": False,
                "char_count": 130,
            },
        ],
    }
    (articles_dir / "articles_cit.json").write_text(
        json.dumps(cit_articles, ensure_ascii=False), encoding="utf-8"
    )

    return articles_dir


# ---------------------------------------------------------------------------
# TestLoadQuestions
# ---------------------------------------------------------------------------

class TestLoadQuestions:
    def test_loads_valid_dataset(self, synthetic_dataset: Path) -> None:
        questions = load_questions(synthetic_dataset)
        assert len(questions) == 3
        assert questions[0]["q"] == "Czy faktura WDT wymaga oznaczenia BFK w JPK?"

    def test_raises_on_missing_questions_key(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text('{"not_questions": []}', encoding="utf-8")
        with pytest.raises(ValueError, match="questions"):
            load_questions(bad)

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not found"):
            load_questions(tmp_path / "nonexistent.json")

    def test_raises_on_malformed_json(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json}", encoding="utf-8")
        with pytest.raises(ValueError, match="invalid JSON"):
            load_questions(bad)


# ---------------------------------------------------------------------------
# TestLoadSlang
# ---------------------------------------------------------------------------

class TestLoadSlang:
    def test_loads_list_format(self, synthetic_slang: Path) -> None:
        entries = load_slang(synthetic_slang)
        assert len(entries) == 2
        assert entries[0]["slang"] == "ksef"

    def test_loads_analysis_format(self, tmp_path: Path) -> None:
        analysis = {
            "meta": {},
            "top_slang_terms": [
                {"short": "wdt", "full_phrase": "wewnątrzwspólnotowa dostawa towarów"},
            ],
        }
        path = tmp_path / "analysis.json"
        path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")
        entries = load_slang(path)
        assert len(entries) == 1
        assert entries[0]["short"] == "wdt"

    def test_returns_empty_for_missing(self, tmp_path: Path) -> None:
        entries = load_slang(tmp_path / "nonexistent.json")
        assert entries == []

    def test_raises_on_malformed_format(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text('{"unexpected": "format"}', encoding="utf-8")
        with pytest.raises(ValueError, match="Unrecognised"):
            load_slang(bad)


# ---------------------------------------------------------------------------
# TestDetectSlang
# ---------------------------------------------------------------------------

class TestDetectSlang:
    def test_finds_unknown_abbreviation(self) -> None:
        known = {"vat", "pit", "cit", "jpk", "ksef"}
        detected = detect_slang("Czy IFT-2R dla Adobe jest konieczny?", known)
        lower_detected = [d.lower() for d in detected]
        assert "ift-2r" in lower_detected

    def test_ignores_known_abbreviations(self) -> None:
        known = {"vat", "pit", "jpk", "bfk"}
        detected = detect_slang("Oznaczenie BFK w JPK za luty", known)
        lower_detected = [d.lower() for d in detected]
        assert "bfk" not in lower_detected
        assert "jpk" not in lower_detected

    def test_catches_pfron(self) -> None:
        known = {"vat", "pit"}
        detected = detect_slang("Czy PFRON dotyczy tego przypadku?", known)
        assert any(d.lower() == "pfron" for d in detected)

    def test_returns_empty_for_no_abbreviations(self) -> None:
        known: set[str] = set()
        detected = detect_slang("jakie są koszty uzyskania?", known)
        assert detected == []


# ---------------------------------------------------------------------------
# TestSuggestExpansion
# ---------------------------------------------------------------------------

class TestSuggestExpansion:
    def test_known_hint(self) -> None:
        assert "źródła" in suggest_expansion("IFT-2R")

    def test_form_number_pattern(self) -> None:
        result = suggest_expansion("PIT36L")
        assert "PIT-36L" in result

    def test_returns_empty_for_unknown(self) -> None:
        assert suggest_expansion("XYZQ") == ""


# ---------------------------------------------------------------------------
# TestFindCandidateArticles
# ---------------------------------------------------------------------------

class TestFindCandidateArticles:
    def test_finds_vat_article_by_keyword(
        self, synthetic_articles: Path
    ) -> None:
        articles_db = load_articles(synthetic_articles)
        candidates = find_candidate_articles(
            "Obowiązek wystawienia faktury WDT",
            "vat",
            articles_db,
            limit=3,
        )
        assert len(candidates) >= 1
        assert any("106b" in c["article_number"] for c in candidates)

    def test_finds_cit_article_by_keyword(
        self, synthetic_articles: Path
    ) -> None:
        articles_db = load_articles(synthetic_articles)
        candidates = find_candidate_articles(
            "Jak rozliczyć IFT-2R za subskrypcje?",
            "cit",
            articles_db,
            limit=3,
        )
        assert len(candidates) >= 1
        assert any("26" in c["article_number"] for c in candidates)

    def test_returns_empty_for_no_match(
        self, synthetic_articles: Path
    ) -> None:
        articles_db = load_articles(synthetic_articles)
        candidates = find_candidate_articles(
            "Zupełnie inny temat",
            "zus",
            articles_db,
            limit=3,
        )
        assert candidates == []

    def test_skips_repealed_articles(self, tmp_path: Path) -> None:
        articles_dir = tmp_path / "arts"
        articles_dir.mkdir()
        data = {
            "metadata": {"law_name": "Testowa ustawa"},
            "articles": [
                {
                    "article_number": "99",
                    "full_id": "art. 99",
                    "raw_text": "Uchylony artykuł o fakturach.",
                    "is_repealed": True,
                    "char_count": 30,
                },
            ],
        }
        (articles_dir / "articles_vat.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
        articles_db = load_articles(articles_dir)
        candidates = find_candidate_articles(
            "Faktury", "vat", articles_db, limit=3
        )
        assert candidates == []


# ---------------------------------------------------------------------------
# TestClassifyQuestion
# ---------------------------------------------------------------------------

class TestClassifyQuestion:
    def test_covered_when_law_matches_and_score_high(self) -> None:
        chunks = [
            LawChunk(
                content="Podatnik ma prawo...",
                law_name="Ustawa o VAT",
                article_number="art. 86",
                category="vat",
                verified_date="",
                score=0.032,
            ),
        ]
        verdict, _ = classify_question("vat", chunks)
        assert verdict == "COVERED"

    def test_weak_when_law_in_top3_but_not_top1(self) -> None:
        chunks = [
            LawChunk(
                content="Kodeks pracy...",
                law_name="Kodeks pracy",
                article_number="art. 1",
                category="kadry",
                verified_date="",
                score=0.031,
            ),
            LawChunk(
                content="VAT...",
                law_name="Ustawa o VAT",
                article_number="art. 86",
                category="vat",
                verified_date="",
                score=0.029,
            ),
        ]
        verdict, _ = classify_question("vat", chunks)
        assert verdict == "WEAK"

    def test_gap_when_wrong_law(self) -> None:
        chunks = [
            LawChunk(
                content="Kodeks pracy...",
                law_name="Kodeks pracy",
                article_number="art. 1",
                category="kadry",
                verified_date="",
                score=0.032,
            ),
        ]
        verdict, _ = classify_question("cit", chunks)
        assert verdict == "GAP"

    def test_gap_when_no_chunks(self) -> None:
        verdict, _ = classify_question("vat", [])
        assert verdict == "GAP"

    def test_weak_for_unmapped_category_with_good_score(self) -> None:
        chunks = [
            LawChunk(
                content="...",
                law_name="Ustawa o VAT",
                article_number="art. 1",
                category="vat",
                verified_date="",
                score=0.031,
            ),
        ]
        verdict, _ = classify_question("praktyka", chunks)
        assert verdict == "WEAK"


# ---------------------------------------------------------------------------
# TestBuildKnownAbbreviations
# ---------------------------------------------------------------------------

class TestBuildKnownAbbreviations:
    def test_includes_category_synonym_map_keys(self) -> None:
        known = build_known_abbreviations([])
        assert "wdt" in known
        assert "wnt" in known
        assert "mpp" in known

    def test_includes_slang_entries(self) -> None:
        entries = [{"slang": "myterm", "expanded": "my full term", "freq": 1}]
        known = build_known_abbreviations(entries)
        assert "myterm" in known

    def test_includes_analysis_format(self) -> None:
        entries = [{"short": "aterm", "full_phrase": "a full phrase"}]
        known = build_known_abbreviations(entries)
        assert "aterm" in known


# ---------------------------------------------------------------------------
# TestMerge
# ---------------------------------------------------------------------------

class TestMerge:
    def test_merge_kb_units_appends(self, tmp_path: Path) -> None:
        kb_path = tmp_path / "kb.json"
        kb_path.write_text('[{"law_name": "existing"}]', encoding="utf-8")

        new_units = [
            {
                "law_name": "Ustawa X",
                "article_number": "art. 1",
                "category": "vat",
                "content": "Treść artykułu.",
            },
        ]
        count = merge_kb_units(kb_path, new_units)
        assert count == 1

        merged = json.loads(kb_path.read_text(encoding="utf-8"))
        assert len(merged) == 2
        assert merged[1]["law_name"] == "Ustawa X"
        assert merged[1]["source"] == "expand_kb_and_synonyms"

    def test_merge_synonyms_skips_empty_expanded(self, tmp_path: Path) -> None:
        slang_path = tmp_path / "slang.json"
        slang_path.write_text("[]", encoding="utf-8")

        new_synonyms = [
            {"slang": "ABC", "expanded": "", "total_freq": 5},
            {"slang": "DEF", "expanded": "defined fully", "total_freq": 3},
        ]
        count = merge_synonyms(slang_path, new_synonyms)
        assert count == 1

        merged = json.loads(slang_path.read_text(encoding="utf-8"))
        assert len(merged) == 1
        assert merged[0]["slang"] == "DEF"

    def test_merge_kb_creates_file_if_missing(self, tmp_path: Path) -> None:
        kb_path = tmp_path / "new_kb.json"
        count = merge_kb_units(kb_path, [
            {"law_name": "X", "article_number": "a1", "category": "c", "content": "t"},
        ])
        assert count == 1
        assert kb_path.exists()


# ---------------------------------------------------------------------------
# TestRun (integration with mocked retriever)
# ---------------------------------------------------------------------------

class TestRun:
    def _make_chunks(self, law_name: str, score: float) -> list[LawChunk]:
        return [
            LawChunk(
                content="Treść...",
                law_name=law_name,
                article_number="art. 1",
                category="vat",
                verified_date="",
                score=score,
            ),
        ]

    def test_produces_proposals_for_gap_questions(
        self,
        synthetic_dataset: Path,
        synthetic_kb: Path,
        synthetic_slang: Path,
        synthetic_articles: Path,
    ) -> None:
        # Mock the retriever to return chunks that will cause GAP for CIT
        # question and COVERED for VAT question
        call_index = {"n": 0}

        def mock_retrieve(query: str, kb_path: str, limit: int = 5) -> list[LawChunk]:
            call_index["n"] += 1
            # Q1 (vat, freq=20): return VAT law -> COVERED
            if "WDT" in query:
                return self._make_chunks("Ustawa o VAT", 0.032)
            # Q2 (cit, freq=15): return wrong law -> GAP
            if "IFT-2R" in query:
                return self._make_chunks("Kodeks pracy", 0.032)
            # Q3 (pit, freq=10): return PIT law -> COVERED
            return self._make_chunks(
                "Ustawa o podatku dochodowym od osób fizycznych", 0.032
            )

        with patch(
            "analysis.expand_kb_and_synonyms.retrieve_chunks",
            side_effect=mock_retrieve,
        ):
            proposed_units, proposed_synonyms = run(
                dataset_path=synthetic_dataset,
                law_units_path=synthetic_kb,
                slang_path=synthetic_slang,
                articles_dir=synthetic_articles,
                top_n=10,
            )

        assert isinstance(proposed_units, list)
        assert isinstance(proposed_synonyms, list)

        # The CIT question is a GAP, so it should produce candidates from
        # articles_cit.json (which has art. 26 about IFT-2R).
        if proposed_units:
            assert any(
                "26" in u.get("article_number", "") for u in proposed_units
            )

    def test_detects_unknown_slang_in_gap_questions(
        self,
        synthetic_dataset: Path,
        synthetic_kb: Path,
        synthetic_slang: Path,
        synthetic_articles: Path,
    ) -> None:
        def mock_retrieve(query: str, kb_path: str, limit: int = 5) -> list[LawChunk]:
            # Everything returns wrong law -> all GAP
            return self._make_chunks("Kodeks pracy", 0.032)

        with patch(
            "analysis.expand_kb_and_synonyms.retrieve_chunks",
            side_effect=mock_retrieve,
        ):
            _, proposed_synonyms = run(
                dataset_path=synthetic_dataset,
                law_units_path=synthetic_kb,
                slang_path=synthetic_slang,
                articles_dir=synthetic_articles,
                top_n=10,
            )

        # IFT-2R should be detected as unknown slang
        slang_tokens = [s["slang"].lower() for s in proposed_synonyms]
        assert any("ift" in t for t in slang_tokens)

    def test_skips_covered_questions(
        self,
        synthetic_dataset: Path,
        synthetic_kb: Path,
        synthetic_slang: Path,
        synthetic_articles: Path,
    ) -> None:
        def mock_retrieve(query: str, kb_path: str, limit: int = 5) -> list[LawChunk]:
            # Return matching law for every category -> all COVERED
            if "WDT" in query:
                return self._make_chunks("Ustawa o VAT", 0.032)
            if "IFT" in query:
                return self._make_chunks(
                    "Ustawa o podatku dochodowym od osób prawnych", 0.032
                )
            return self._make_chunks(
                "Ustawa o podatku dochodowym od osób fizycznych", 0.032
            )

        with patch(
            "analysis.expand_kb_and_synonyms.retrieve_chunks",
            side_effect=mock_retrieve,
        ):
            proposed_units, proposed_synonyms = run(
                dataset_path=synthetic_dataset,
                law_units_path=synthetic_kb,
                slang_path=synthetic_slang,
                articles_dir=synthetic_articles,
                top_n=10,
            )

        # All questions are COVERED -> no proposals
        assert proposed_units == []
        assert proposed_synonyms == []
