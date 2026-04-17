"""Tests for ``fb_pipeline.ingest.ingest_fb_corpus``.

Covers normalization, hashing, in-file / cross-file deduplication, and the
quality filter. Uses synthetic fixtures in ``tests/fixtures/fb_sample/``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from fb_pipeline.ingest import ingest_fb_corpus as ingest


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "fb_sample"
FILE1 = FIXTURE_DIR / "file1.json"
FILE2 = FIXTURE_DIR / "file2.json"
FILE3 = FIXTURE_DIR / "file3.json"


def _candidate(
    text: str,
    *,
    comments: list[str] | None = None,
    scraped_at: str = "2026-04-11T10:00:00.000Z",
    source_file: str = "file1.json",
    group_id: str = "group_a",
    group_name: str = "group_a_name",
) -> ingest.CandidateRecord:
    normalized = ingest.normalize_text(text)
    return ingest.CandidateRecord(
        id=ingest.compute_record_id(normalized),
        group_id=group_id,
        group_name=group_name,
        text=text,
        normalized_text=normalized,
        text_length=len(text),
        comments=list(comments or []),
        scraped_at=scraped_at,
        source_file=source_file,
        num_links=ingest.count_urls(text),
    )


def test_normalize_text_preserves_polish():
    source = "Jak księgować fakturę?"
    normalized = ingest.normalize_text(source)
    assert normalized == "jak księgować fakturę?"
    # Diacritics and question mark survive normalization — both are load-bearing.
    assert "ę" in normalized and "ć" in normalized and "?" in normalized


def test_normalize_text_strips_emoji_and_urls():
    source = "Jak zaksięgować fakturę 😊 z linku https://example.com/faktura? Dzięki 🙏"
    normalized = ingest.normalize_text(source)
    assert "😊" not in normalized
    assert "🙏" not in normalized
    assert "http" not in normalized
    assert "example.com" not in normalized
    # Content words and diacritics stay.
    assert "zaksięgować" in normalized
    assert normalized.endswith("dzięki") or "dzięki" in normalized


def test_dedup_same_prefix():
    long_prefix = "Jak rozliczyć " + ("VAT i JPK " * 25)
    text_a = long_prefix + "wariant A"
    text_b = long_prefix + "inny zupełnie wariant B"
    id_a = ingest.compute_record_id(ingest.normalize_text(text_a))
    id_b = ingest.compute_record_id(ingest.normalize_text(text_b))
    # Both exceed 200 chars and share the same first 200 chars after normalization.
    assert len(ingest.normalize_text(text_a)) > ingest.HASH_PREFIX_CHARS
    assert id_a == id_b


def test_dedup_different_prefix():
    id_a = ingest.compute_record_id(ingest.normalize_text("Jak rozliczyć VAT przy WDT?"))
    id_b = ingest.compute_record_id(ingest.normalize_text("Jak rozliczyć CIT za rok 2025?"))
    assert id_a != id_b


def test_quality_filter_rejects_short():
    record = _candidate("xyz?")
    keep, reason, _ = ingest.classify_record(record)
    assert not keep
    assert reason == "too_short"


def test_quality_filter_rejects_no_question():
    record = _candidate("Dzisiaj jest bardzo ładna pogoda i słoneczko świeci nad Warszawą.")
    keep, reason, _ = ingest.classify_record(record)
    assert not keep
    assert reason == "no_question_pattern"


def test_quality_filter_accepts_real_question():
    record = _candidate(
        "Faktura z kodem QR offline ale nie widać jej w KSeF. Czy mogę odliczyć VAT i "
        "jakie oznaczenie dać w JPK – BFK czy DI?",
        comments=["BFK po synchronizacji."],
    )
    keep, reason, flags = ingest.classify_record(record)
    assert keep, reason
    assert reason is None
    assert "no_comments" not in flags


def test_quality_filter_rejects_job_ad():
    record = _candidate("Szukam księgowej do biura w Warszawie, praca od zaraz, pisz na pw.")
    keep, reason, _ = ingest.classify_record(record)
    assert not keep
    assert reason == "job_ad"


def test_cross_file_merge_keeps_newer(tmp_path: Path):
    sources = [
        (str(FILE1.relative_to(Path(__file__).resolve().parents[1])), "group_a", "group_a_name"),
        (str(FILE3.relative_to(Path(__file__).resolve().parents[1])), "group_a", "group_a_name"),
    ]
    stats, finals, report = ingest.run(
        sources=sources,
        output_jsonl=tmp_path / "out.jsonl",
        report_md_path=tmp_path / "report.md",
        report_json_path=tmp_path / "report.json",
        apply=False,
        repo_root=Path(__file__).resolve().parents[1],
    )

    # The shared post (file1 new vs file3 backup) must resolve to file1.json
    # because file1's scraped_at is newer than file3's.
    shared_candidates = [r for r in finals if "wdt jeśli faktura" in r.normalized_text]
    assert len(shared_candidates) == 1
    winner = shared_candidates[0]
    assert winner.source_file == "file1.json"
    assert winner.scraped_at.startswith("2026-04-11")
    assert stats.cross_file_duplicates >= 1


def test_cross_file_merges_comments(tmp_path: Path):
    sources = [
        (str(FILE1.relative_to(Path(__file__).resolve().parents[1])), "group_a", "group_a_name"),
        (str(FILE3.relative_to(Path(__file__).resolve().parents[1])), "group_a", "group_a_name"),
    ]
    _, finals, _ = ingest.run(
        sources=sources,
        output_jsonl=tmp_path / "out.jsonl",
        report_md_path=tmp_path / "report.md",
        report_json_path=tmp_path / "report.json",
        apply=False,
        repo_root=Path(__file__).resolve().parents[1],
    )

    shared_candidates = [r for r in finals if "wdt jeśli faktura" in r.normalized_text]
    assert len(shared_candidates) == 1
    winner = shared_candidates[0]
    comments = winner.comments

    # Unique comment from backup survives; comment duplicated across files appears once.
    assert any("starszy komentarz z backupu" in c.lower() for c in comments)
    rozlicz_hits = sum(1 for c in comments if "rozlicz za miesiąc wysyłki" in c.lower())
    assert rozlicz_hits == 1, comments
    # Comment edited-into-the-duplicate from file1 (post6) is also kept.
    assert any("komentarz dodany do duplikatu" in c.lower() for c in comments)


def test_in_file_duplicate_collapses(tmp_path: Path):
    sources = [
        (str(FILE1.relative_to(Path(__file__).resolve().parents[1])), "group_a", "group_a_name"),
    ]
    stats, finals, _ = ingest.run(
        sources=sources,
        output_jsonl=tmp_path / "out.jsonl",
        report_md_path=tmp_path / "report.md",
        report_json_path=tmp_path / "report.json",
        apply=False,
        repo_root=Path(__file__).resolve().parents[1],
    )

    # post1 and post6 share the same first 200 normalized chars — one survivor only.
    shared = [r for r in finals if "wdt jeśli faktura" in r.normalized_text]
    assert len(shared) == 1
    assert stats.duplicates_within_files >= 1


def test_rejects_community_only_marker():
    record = _candidate(
        "Mam ciekawą ofertę dla księgowych, link w komentarzu proszę kliknąć jeśli ktoś zainteresowany?"
    )
    keep, reason, _ = ingest.classify_record(record)
    assert not keep
    assert reason == "community_only"


def test_flag_no_comments_and_too_long():
    long_text = "Czy mogę zapytać o jedną rzecz? " + ("Dłuższy akapit analizy. " * 50)
    assert len(long_text) > ingest.TEXT_FLAG_LONG
    record = _candidate(long_text, comments=[])
    keep, reason, flags = ingest.classify_record(record)
    assert keep, reason
    assert "too_long" in flags
    assert "no_comments" in flags


# --- v1.5b: cutoff stripping, expanded filters, probably_comment flag ---


def test_strip_cutoff_suffixes_basic_cases():
    samples = [
        ("Witam, mam pytanie... Wyświetl więcej", "Witam, mam pytanie"),
        ("Długi tekst posta Zobacz więcej", "Długi tekst posta"),
        ("Tekst z unicode ellipsą …", "Tekst z unicode ellipsą"),
        ("Tekst z asci elipsą...", "Tekst z asci elipsą"),
        ("Bez ucinania, pełny tekst?", "Bez ucinania, pełny tekst?"),
    ]
    for source, expected in samples:
        cleaned, was_stripped = ingest.strip_cutoff_suffixes(source)
        assert cleaned == expected, (source, cleaned)
        assert was_stripped == (cleaned != source)


def test_strip_cutoff_suffixes_is_idempotent():
    source = "Pytanie księgowe... Wyświetl więcej"
    once, was_stripped = ingest.strip_cutoff_suffixes(source)
    twice, was_stripped_again = ingest.strip_cutoff_suffixes(once)
    assert was_stripped is True
    assert was_stripped_again is False
    assert once == twice == "Pytanie księgowe"


def test_normalize_strips_cutoff_markers():
    lhs = ingest.normalize_text("Jak rozliczyć VAT przy WDT? Wyświetl więcej")
    rhs = ingest.normalize_text("Jak rozliczyć VAT przy WDT?")
    assert lhs == rhs, (lhs, rhs)
    assert "wyświetl" not in lhs
    assert "więcej" not in lhs


def test_build_candidates_counts_cutoff_stripped(tmp_path: Path):
    # Two posts, one has a cutoff marker. cutoff_stripped should count 1.
    source = ingest.RawSource(
        path=Path("synthetic.json"),
        group_id="group_a",
        group_name="group_a_name",
        scraped_at="2026-04-16T10:00:00.000Z",
        posts=[
            {"text": "Pierwszy pełny post, wszystko widać. Czy mogę odliczyć VAT?", "comments": []},
            {"text": "Drugi post ma ucięte zakończenie... Wyświetl więcej", "comments": []},
        ],
    )
    _, _, cutoff_stripped = ingest.build_candidates(source)
    assert cutoff_stripped == 1


def test_quality_filter_rejects_rekrutacja_substring():
    # "rekrutacja" after a greeting should be caught (substring in first 50 chars).
    record = _candidate(
        "Witam, rekrutacja do biura rachunkowego w Krakowie, oferujemy stabilną umowę."
    )
    keep, reason, _ = ingest.classify_record(record)
    assert not keep
    assert reason == "job_ad"


def test_quality_filter_rejects_poszukujemy():
    record = _candidate(
        "Poszukujemy księgowej z doświadczeniem na umowę o pracę, Warszawa centrum."
    )
    keep, reason, _ = ingest.classify_record(record)
    assert not keep
    assert reason == "job_ad"


def test_quality_filter_rejects_sales_spam_sprzedam():
    record = _candidate(
        "Sprzedam biuro rachunkowe w centrum Poznania z kompletem klientów, "
        "cena do negocjacji po pw."
    )
    keep, reason, _ = ingest.classify_record(record)
    assert not keep
    assert reason == "sales_spam"


def test_quality_filter_rejects_marketing_bold():
    # Head must have >=40% mathematical bold glyphs. 50 bold chars in the first
    # 100 is a comfortable margin.
    bold_head = "𝗧𝗼𝗷𝗲𝘀𝘁𝗻𝗮𝗷𝗹𝗲𝗽𝘀𝘇𝗮𝗼𝗸𝗮𝘇𝗷𝗮𝗶𝗻𝘄𝗲𝘀𝘁𝘆𝗰𝘆𝗷𝗻𝗮𝘁𝘆𝗹𝗸𝗼𝗱𝘇𝗶𝘀𝗶𝗮𝗷𝗭𝗮𝗿𝗮𝗯𝗶𝗮𝗷"
    rest = " Kup teraz krypto i zarabiaj, gwarantowany zwrot 20% miesięcznie."
    record = _candidate(bold_head + rest)
    keep, reason, _ = ingest.classify_record(record)
    assert not keep
    assert reason == "marketing_bold"


def test_quality_filter_accepts_low_bold():
    # A legit question with a single stray bold char is not marketing.
    record = _candidate(
        "Czy mogę odliczyć VAT przy sprzedaży 𝗪𝗗𝗧? Potrzebuję potwierdzenia.",
        comments=["tak, możesz"],
    )
    keep, reason, _ = ingest.classify_record(record)
    assert keep, reason
    assert reason is None


def test_probably_comment_regex_opener():
    # Matches a known comment opener regex.
    assert ingest.detect_probably_comment(
        "Tak jak pisali poprzednicy, u mnie również tak to wygląda?"
    )
    assert ingest.detect_probably_comment("Mam podobny problem z tym samym klientem?")
    assert ingest.detect_probably_comment("Nie wiem skąd taka kwota, sprawdź rachunek.")


def test_probably_comment_lowercase_opener():
    # Lowercase first letter also trips the heuristic.
    assert ingest.detect_probably_comment("to chyba zależy od rodzaju umowy?")


def test_probably_comment_false_for_normal_post():
    # A normal post starting with an uppercase greeting is not flagged.
    assert not ingest.detect_probably_comment(
        "Witam, mam pytanie o rozliczenie VAT przy imporcie usług z UE. Czy mogę odliczyć?"
    )
    assert not ingest.detect_probably_comment(
        "Jak rozliczyć fakturę korygującą w JPK_V7M za zeszły miesiąc?"
    )


def test_flagged_probably_comment_kept_not_rejected():
    # probably_comment is a FLAG, not a reject — record must survive.
    record = _candidate(
        "Tak jak pisali poprzednicy, u mnie w biurze stosujemy tę samą metodę. "
        "Czy Wy też tak macie?",
        comments=["zgadzam się"],
    )
    keep, reason, flags = ingest.classify_record(record)
    assert keep, reason
    assert reason is None
    assert "probably_comment" in flags


def test_marketing_bold_rejects_before_no_question():
    # Marketing bold check fires even when the post has no "?" or question keywords.
    bold_head = "𝗜𝗡𝗪𝗘𝗦𝗧𝗨𝗝𝗧𝗘𝗥𝗔𝗭𝗶𝗽𝗼𝗺𝗻𝗼𝘇𝗸𝗮𝗽𝗶𝘁𝗮𝗹𝘇𝗱𝘂𝘇𝘆𝗺𝘇𝘄𝗿𝗼𝘁𝗲𝗺𝗽𝗼𝗹𝗲𝗰𝗮𝗺"
    record = _candidate(bold_head + " kontakt na priv i dostajesz dostęp do grupy.")
    keep, reason, _ = ingest.classify_record(record)
    assert not keep
    assert reason == "marketing_bold"


def test_end_to_end_report_shape(tmp_path: Path):
    sources = [
        (str(FILE1.relative_to(Path(__file__).resolve().parents[1])), "group_a", "group_a_name"),
        (str(FILE2.relative_to(Path(__file__).resolve().parents[1])), "group_b", "group_b_name"),
        (str(FILE3.relative_to(Path(__file__).resolve().parents[1])), "group_a", "group_a_name"),
    ]
    stats, finals, report = ingest.run(
        sources=sources,
        output_jsonl=tmp_path / "out.jsonl",
        report_md_path=tmp_path / "report.md",
        report_json_path=tmp_path / "report.json",
        apply=True,
        repo_root=Path(__file__).resolve().parents[1],
    )

    assert (tmp_path / "out.jsonl").exists()
    assert (tmp_path / "report.md").exists()
    assert (tmp_path / "report.json").exists()
    assert report["totals"]["final"] == len(finals)
    assert report["totals"]["raw"] == 6 + 5 + 3
    assert stats.rejected_job_ad >= 1
    assert stats.rejected_too_short >= 1
    assert stats.rejected_no_question >= 1
    assert stats.rejected_community_only >= 1
