"""Ingest FB community scrapes into a deduplicated, quality-filtered corpus.

Reads three raw scrapes produced by Playwright, normalizes text, assigns a
stable 12-char SHA-256 id over the first 200 normalized characters, resolves
cross-file duplicates by newest ``scraped_at`` (merging comment lists), applies
REJECT/FLAG quality heuristics, and emits:

* ``data/corpus/fb_groups/fb_corpus.jsonl``        (gitignored)
* ``analysis/fb_corpus_ingest_report.md``          (tracked)
* ``analysis/fb_corpus_ingest_report.json``        (tracked)

The script is dry-run by default; pass ``--apply`` to write outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import random
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger("ingest_fb_corpus")

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES: tuple[tuple[str, str, str], ...] = (
    ("fb_pipeline/posts_15k_ksiegowosc_moja_pasja.json", "360545881004410", "ksiegowosc_moja_pasja"),
    ("fb_pipeline/posts_output.json", "507801603233194", "grupa_2_507801603233194"),
    ("fb_pipeline/posts_output_backup.json", "360545881004410", "ksiegowosc_moja_pasja"),
)
DEFAULT_OUTPUT_JSONL = "data/corpus/fb_groups/fb_corpus.jsonl"
DEFAULT_REPORT_MD = "analysis/fb_corpus_ingest_report.md"
DEFAULT_REPORT_JSON = "analysis/fb_corpus_ingest_report.json"

HASH_PREFIX_CHARS = 200
HASH_ID_LENGTH = 12
COMMENT_DEDUP_PREFIX = 80

TEXT_MIN_LENGTH = 20
TEXT_FLAG_LONG = 800
LINKS_FLAG_THRESHOLD = 5

# v1.5b quality fixes
HEAD_MATCH_CHARS = 50
MARKETING_BOLD_HEAD_CHARS = 100
MARKETING_BOLD_THRESHOLD = 0.40

# Baseline numbers from the v1 run (Zadanie 1, commit 97a6efe) — frozen for the
# before/after table in the regenerated report. Do not change without also
# bumping the corpus version.
BASELINE_V1: dict[str, int] = {
    "raw_total": 40537,
    "final_total": 24954,
    "rejected_too_short": 15,
    "rejected_no_question_pattern": 3807,
    "rejected_job_ad": 82,
    "rejected_community_only": 0,
    "flagged_too_long": 0,
    "flagged_no_comments": 7422,
    "flagged_many_links": 0,
    "cross_file_duplicates": 10026,
    "duplicates_within_files": 1629,
}

QUESTION_KEYWORD_RE = re.compile(
    r"(?:^|[^\w])(jak|czy|co|kiedy|gdzie|ile|pomocy?|problem|prosz[eę]|potrzebuj|nie wiem|nie rozumiem)(?:[^\w]|$)",
    flags=re.IGNORECASE,
)

JOB_AD_PREFIXES: tuple[str, ...] = (
    "szukam księgowej",
    "szukam księgowego",
    "szukam pracy",
    "szukam doświadczonego",
    "oferuj",
    "zatrudnię",
    "polecam mojego",
    "polecam moją",
    "oferta pracy",
    "poszukuję pracy",
    "poszukujemy",
    "rekrutacja",
    "ogłoszenie o prac",
    "ogloszenie o prac",
    "do działu",
    "starsza specjalistka",
    "starszy specjalista",
)

SALES_SPAM_PREFIXES: tuple[str, ...] = (
    "sprzedam",
    "oddam",
    "kupię",
    "kupie",
    "wynajmę",
)

COMMUNITY_ONLY_MARKERS: tuple[str, ...] = (
    "link w komentarzu",
    "pisz na pw",
    "pm dla zainteresowanych",
)

# Scraper truncation markers — FB injects "... Wyświetl więcej" at the UI cut-off.
CUTOFF_SUFFIXES: tuple[str, ...] = (
    "wyświetl więcej",
    "zobacz więcej",
)
TRAILING_ELLIPSIS_RE = re.compile(r"(?:…+|\.{3,})\s*$")

# Mathematical Alphanumeric Symbols — used by marketing posts for fancy bold text.
MATH_BOLD_RE = re.compile(r"[\U0001D400-\U0001D7FF]")

# Opener patterns suggesting the "post" is actually a reply/commentary.
COMMENT_OPENER_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pat)
    for pat in (
        r"^(Nie\s+(wiem|ma|w)\s)",
        r"^(Jeżeli|Jesli|Jeśli)\s+(rozliczasz|chcesz|to|jest|z)",
        r"^Zgłosić\s+do\s",
        r"^Tak\s+jak\s+pisali\s",
        r"^A\s+(nie|u\s+mnie|czym)\s",
        r"^Dlaczego\s+(czekać|nie)\s",
        r"^Mam\s+podobny\s+problem",
        r"^Obecnie\s+od\s+\d",
        r"^Samo\s+zaświadczenie",
        r"^Zależy\s+(czy|od)",
        r"^Mówi\s+Pani\s+o",
        r"^Pytanie\s+co\s+masz",
        r"^OC\s+zwraca",
        r"^kogoś\s+to\s+jeszcze",
        r"^liczysz\s+każdy",
        r"^Uznać\s+za\s+(chorobę|wypadek)",
        r"^Problemem\s+w\s+(takich|tym)",
        r"^Sporo\s+z\s+nich",
        r"^Ja\s+po\s+(poronieniu|latach)",
        r"^Przez\s+całe\s+lata",
        r"^to\s+chyba",
        r"^Nasze\s+BR",
        r"^Nic\s+nie\s+wysyłaj",
        r"^Skoro\s+jest\s",
        r"^Pit\s+2\s+sekcja",
    )
)

URL_RE = re.compile(r"https?://\S+", flags=re.IGNORECASE)

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\u200d\u2640-\u2642\u2600-\u2B55\u23cf\u23e9\u231a\ufe0f\u3030"
    "]+",
    flags=re.UNICODE,
)

WHITESPACE_RE = re.compile(r"\s+")

# Lightweight Polish stopword list used only for the "top 20 keywords" summary.
POLISH_STOP_WORDS = {
    "a", "aby", "ale", "bo", "by", "być", "był", "była", "było", "były", "bym",
    "byś", "co", "czy", "da", "do", "dla", "go", "i", "ich", "ile", "im", "inny",
    "ja", "jak", "jakie", "jako", "je", "jego", "jej", "jest", "jeszcze",
    "już", "ju", "kiedy", "kto", "która", "które", "którego", "której", "który",
    "którzy", "lub", "ma", "mam", "mi", "mnie", "mu", "my", "na", "nad", "nam",
    "nas", "nawet", "nic", "nie", "niego", "niej", "nim", "no", "o", "od",
    "oraz", "po", "pod", "prze", "przez", "przy", "się", "sie", "są", "ta",
    "tak", "tam", "te", "tego", "tej", "temu", "ten", "to", "tu", "tylko",
    "tym", "u", "w", "we", "wie", "więc", "wy", "z", "ze", "za", "że", "zeby",
    "żeby", "który", "jakie", "jakim", "może", "mozna", "można",
}


# --- v1.5b quality-fix helpers ---

def strip_cutoff_suffixes(text: str) -> tuple[str, bool]:
    """Strip FB scraper truncation markers from the tail of a post.

    Removes trailing ``"Wyświetl więcej"`` / ``"Zobacz więcej"`` labels and
    unicode/ascii ellipses. Iterates until stable so stacked markers
    (``"... Wyświetl więcej"``) collapse in one call.

    Returns ``(cleaned_text, was_modified)``.
    """

    if not isinstance(text, str):
        return "", False
    original = text
    cleaned = text
    while True:
        candidate = cleaned.rstrip()
        lower = candidate.lower()
        matched = False
        for suffix in CUTOFF_SUFFIXES:
            if lower.endswith(suffix):
                candidate = candidate[: -len(suffix)].rstrip()
                matched = True
                break
        if not matched:
            m = TRAILING_ELLIPSIS_RE.search(candidate)
            if m:
                candidate = candidate[: m.start()].rstrip()
                matched = True
        if not matched or candidate == cleaned:
            cleaned = candidate
            break
        cleaned = candidate
    return cleaned, cleaned != original


def is_marketing_bold(text: str) -> bool:
    """True when the first ~100 chars are dominated by Mathematical Bold glyphs.

    Marketing/crypto spam posts use U+1D400–U+1D7FF characters to render fake
    bold text. Legit posts with a stray bold character are well below the 40%
    threshold.
    """

    if not isinstance(text, str) or not text:
        return False
    head = text[:MARKETING_BOLD_HEAD_CHARS]
    if not head:
        return False
    bold_count = len(MATH_BOLD_RE.findall(head))
    return (bold_count / len(head)) >= MARKETING_BOLD_THRESHOLD


def detect_probably_comment(text: str) -> bool:
    """Heuristic: does this "post" actually look like a reply comment?

    v1.5c: matches only the 25 explicit comment-opener regexes. The earlier
    "starts with a lowercase letter" rule had a >60% false-positive rate in
    Polish posts (legit openers like "witam", "e-commerce", URL pastes).
    """

    if not isinstance(text, str):
        return False
    stripped = text.strip()
    if not stripped:
        return False
    for pattern in COMMENT_OPENER_PATTERNS:
        if pattern.match(stripped):
            return True
    return False


@dataclass(slots=True)
class RawSource:
    path: Path
    group_id: str
    group_name: str
    scraped_at: str
    posts: list[dict]


@dataclass(slots=True)
class CandidateRecord:
    id: str
    group_id: str
    group_name: str
    text: str
    normalized_text: str
    text_length: int
    comments: list[str]
    scraped_at: str
    source_file: str
    num_links: int


@dataclass(slots=True)
class FinalRecord:
    id: str
    group_id: str
    group_name: str
    text: str
    normalized_text: str
    text_length: int
    comments: list[str]
    comments_count: int
    scraped_at: str
    source_file: str
    quality_flags: list[str]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "text": self.text,
            "normalized_text": self.normalized_text,
            "text_length": self.text_length,
            "comments": list(self.comments),
            "comments_count": self.comments_count,
            "scraped_at": self.scraped_at,
            "source_file": self.source_file,
            "quality_flags": list(self.quality_flags),
        }


@dataclass(slots=True)
class Stats:
    per_source_raw: dict[str, int] = field(default_factory=dict)
    per_source_after_dedupe: dict[str, int] = field(default_factory=lambda: Counter())
    per_source_final: dict[str, int] = field(default_factory=lambda: Counter())
    duplicates_within_files: int = 0
    cross_file_duplicates: int = 0
    rejected_too_short: int = 0
    rejected_no_question: int = 0
    rejected_job_ad: int = 0
    rejected_community_only: int = 0
    rejected_marketing_bold: int = 0
    rejected_sales_spam: int = 0
    flagged_too_long: int = 0
    flagged_no_comments: int = 0
    flagged_many_links: int = 0
    flagged_probably_comment: int = 0
    cutoff_stripped: int = 0
    backup_with_dup_in_newer_same_group: int = 0
    backup_total: int = 0
    group1_with_dup_in_group2: int = 0
    group1_total: int = 0


def normalize_text(text: str) -> str:
    """Lowercase, strip emoji and URLs, collapse whitespace.

    Polish diacritics and punctuation are preserved because both carry signal
    (diacritics mark legal terms; ``?`` marks question intent).
    """

    if not isinstance(text, str):
        return ""
    cleaned, _ = strip_cutoff_suffixes(text)
    stripped = URL_RE.sub(" ", cleaned)
    stripped = EMOJI_RE.sub(" ", stripped)
    stripped = unicodedata.normalize("NFC", stripped)
    lowered = stripped.lower()
    collapsed = WHITESPACE_RE.sub(" ", lowered).strip()
    return collapsed


def compute_record_id(normalized_text: str) -> str:
    prefix = normalized_text[:HASH_PREFIX_CHARS]
    digest = hashlib.sha256(prefix.encode("utf-8")).hexdigest()
    return digest[:HASH_ID_LENGTH]


def count_urls(text: str) -> int:
    if not isinstance(text, str):
        return 0
    return len(URL_RE.findall(text))


def _parse_scraped_at(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return datetime.min.replace(tzinfo=timezone.utc)


def load_source(source_path: Path, group_id: str, group_name: str) -> RawSource:
    data = json.loads(source_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "posts" not in data:
        raise ValueError(f"{source_path}: unexpected scrape structure (missing 'posts' key)")

    posts = data.get("posts") or []
    if not isinstance(posts, list):
        raise ValueError(f"{source_path}: 'posts' is not a list")

    scraped_at = str(data.get("scraped_at", "")).strip()
    return RawSource(
        path=source_path,
        group_id=group_id,
        group_name=group_name,
        scraped_at=scraped_at,
        posts=posts,
    )


def _coerce_comments(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def build_candidates(source: RawSource) -> tuple[list[CandidateRecord], int, int]:
    """Turn raw posts into :class:`CandidateRecord`, collapsing in-file duplicates.

    Returns ``(candidates, in_file_duplicates, cutoff_stripped)``. The stripped
    count is incremented once per post whose raw text contained a scraper
    truncation marker (``"Wyświetl więcej"`` / ellipsis) — those are cleaned
    before hashing so the marker no longer splits what is the same post
    content.
    """

    by_id: dict[str, CandidateRecord] = {}
    in_file_dupes = 0
    cutoff_stripped = 0
    source_file_name = source.path.name
    for post in source.posts:
        raw_text = str(post.get("text", "") or "").strip()
        if not raw_text:
            continue
        cleaned_text, was_stripped = strip_cutoff_suffixes(raw_text)
        if was_stripped:
            cutoff_stripped += 1
        if not cleaned_text:
            continue
        normalized = normalize_text(cleaned_text)
        if not normalized:
            continue
        record_id = compute_record_id(normalized)
        comments = _coerce_comments(post.get("comments"))
        num_links = count_urls(cleaned_text)
        if record_id in by_id:
            in_file_dupes += 1
            existing = by_id[record_id]
            existing.comments = _merge_comments(existing.comments, comments)
            continue
        by_id[record_id] = CandidateRecord(
            id=record_id,
            group_id=source.group_id,
            group_name=source.group_name,
            text=cleaned_text,
            normalized_text=normalized,
            text_length=len(cleaned_text),
            comments=comments,
            scraped_at=source.scraped_at,
            source_file=source_file_name,
            num_links=num_links,
        )
    return list(by_id.values()), in_file_dupes, cutoff_stripped


def _merge_comments(*lists: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for lst in lists:
        for comment in lst:
            key = normalize_text(comment)[:COMMENT_DEDUP_PREFIX]
            if not key:
                continue
            if key in seen:
                continue
            seen.add(key)
            merged.append(comment)
    return merged


def resolve_cross_file_duplicates(
    per_source_candidates: dict[str, list[CandidateRecord]],
) -> tuple[list[CandidateRecord], int, dict[str, int], dict[str, set[str]]]:
    """Keep the newest record per id and merge comments from older duplicates.

    Returns ``(winners, cross_file_duplicate_count, winners_per_source,
    ids_per_source)``. ``ids_per_source`` is used later to compute
    verification counts (backup vs newer same-group; group1 vs group2).
    """

    ids_per_source: dict[str, set[str]] = {
        source: {record.id for record in records}
        for source, records in per_source_candidates.items()
    }

    merged: dict[str, CandidateRecord] = {}
    cross_file_dupes = 0
    for source, records in per_source_candidates.items():
        for record in records:
            existing = merged.get(record.id)
            if existing is None:
                merged[record.id] = record
                continue
            cross_file_dupes += 1
            existing_ts = _parse_scraped_at(existing.scraped_at)
            candidate_ts = _parse_scraped_at(record.scraped_at)
            if candidate_ts > existing_ts:
                record.comments = _merge_comments(record.comments, existing.comments)
                merged[record.id] = record
            else:
                existing.comments = _merge_comments(existing.comments, record.comments)

    winners_per_source: dict[str, int] = Counter()
    for record in merged.values():
        winners_per_source[record.source_file] += 1

    return list(merged.values()), cross_file_dupes, dict(winners_per_source), ids_per_source


def classify_record(record: CandidateRecord) -> tuple[bool, str | None, list[str]]:
    """Apply REJECT / FLAG heuristics. Returns ``(keep, reject_reason, flags)``.

    Reject order (v1.5b): ``too_short`` → ``marketing_bold`` → ``sales_spam`` →
    ``job_ad`` → ``community_only`` → ``no_question_pattern``. Flags (kept) add
    ``probably_comment`` to the v1 set.
    """

    if record.text_length < TEXT_MIN_LENGTH:
        return False, "too_short", []

    if is_marketing_bold(record.text):
        return False, "marketing_bold", []

    normalized = record.normalized_text
    head = normalized[:HEAD_MATCH_CHARS]

    for prefix in SALES_SPAM_PREFIXES:
        if head.startswith(prefix):
            return False, "sales_spam", []

    # Job-ad prefixes are matched as substrings in the first HEAD_MATCH_CHARS so
    # that openers like "Witam, rekrutacja..." are caught without bespoke
    # greeting handling.
    for prefix in JOB_AD_PREFIXES:
        if prefix in head:
            return False, "job_ad", []

    for marker in COMMUNITY_ONLY_MARKERS:
        if marker in normalized:
            return False, "community_only", []

    has_question_mark = "?" in normalized
    has_keyword = QUESTION_KEYWORD_RE.search(normalized) is not None
    if not (has_question_mark or has_keyword):
        return False, "no_question_pattern", []

    flags: list[str] = []
    if record.text_length > TEXT_FLAG_LONG:
        flags.append("too_long")
    if not record.comments:
        flags.append("no_comments")
    if record.num_links > LINKS_FLAG_THRESHOLD:
        flags.append("many_links")
    if detect_probably_comment(record.text):
        flags.append("probably_comment")
    return True, None, flags


def finalize(records: Iterable[CandidateRecord], stats: Stats) -> list[FinalRecord]:
    finalized: list[FinalRecord] = []
    for record in records:
        keep, reason, flags = classify_record(record)
        if not keep:
            if reason == "too_short":
                stats.rejected_too_short += 1
            elif reason == "no_question_pattern":
                stats.rejected_no_question += 1
            elif reason == "job_ad":
                stats.rejected_job_ad += 1
            elif reason == "community_only":
                stats.rejected_community_only += 1
            elif reason == "marketing_bold":
                stats.rejected_marketing_bold += 1
            elif reason == "sales_spam":
                stats.rejected_sales_spam += 1
            continue
        if "too_long" in flags:
            stats.flagged_too_long += 1
        if "no_comments" in flags:
            stats.flagged_no_comments += 1
        if "many_links" in flags:
            stats.flagged_many_links += 1
        if "probably_comment" in flags:
            stats.flagged_probably_comment += 1
        finalized.append(
            FinalRecord(
                id=record.id,
                group_id=record.group_id,
                group_name=record.group_name,
                text=record.text,
                normalized_text=record.normalized_text,
                text_length=record.text_length,
                comments=record.comments,
                comments_count=len(record.comments),
                scraped_at=record.scraped_at,
                source_file=record.source_file,
                quality_flags=flags,
            )
        )
        stats.per_source_final[record.source_file] += 1
    return finalized


def _top_keywords(records: list[FinalRecord], limit: int = 20) -> list[tuple[str, int]]:
    token_re = re.compile(r"[a-zA-Ząćęłńóśżź0-9]{3,}")
    counts: Counter[str] = Counter()
    for record in records:
        for token in token_re.findall(record.normalized_text):
            if token in POLISH_STOP_WORDS:
                continue
            if token.isdigit():
                continue
            counts[token] += 1
    return counts.most_common(limit)


def _random_sample(records: list[FinalRecord], size: int = 10, seed: int = 42) -> list[FinalRecord]:
    if not records:
        return []
    rng = random.Random(seed)
    count = min(size, len(records))
    return rng.sample(records, count)


def _top_engaging(records: list[FinalRecord], limit: int = 20) -> list[FinalRecord]:
    return sorted(records, key=lambda r: (r.comments_count, r.text_length), reverse=True)[:limit]


def _heuristic_cluster_estimate(corpus_size: int) -> str:
    if corpus_size <= 0:
        return "n/a"
    low = max(1, corpus_size // 150)
    high = max(low, corpus_size // 100)
    return f"~{low}-{high}"


def build_reports(
    stats: Stats,
    per_source_raw: dict[str, int],
    per_source_after_dedupe: dict[str, int],
    final_records: list[FinalRecord],
    sources: list[tuple[str, str, str]],
    unrelated_observations: list[str],
) -> tuple[str, dict]:
    total_raw = sum(per_source_raw.values())
    total_after_dedupe = sum(per_source_after_dedupe.values())
    total_final = len(final_records)
    cluster_estimate = _heuristic_cluster_estimate(total_final)

    rejections = {
        "too_short": stats.rejected_too_short,
        "marketing_bold": stats.rejected_marketing_bold,
        "sales_spam": stats.rejected_sales_spam,
        "job_ad": stats.rejected_job_ad,
        "community_only": stats.rejected_community_only,
        "no_question_pattern": stats.rejected_no_question,
    }
    flags = {
        "too_long": stats.flagged_too_long,
        "no_comments": stats.flagged_no_comments,
        "many_links": stats.flagged_many_links,
        "probably_comment": stats.flagged_probably_comment,
    }

    top_keywords = _top_keywords(final_records)
    random_sample = _random_sample(final_records)
    top_engaging = _top_engaging(final_records)
    probably_comment_records = [
        r for r in final_records if "probably_comment" in r.quality_flags
    ]
    probably_comment_sample = _random_sample(probably_comment_records, size=10, seed=42)

    def _fmt_pct(part: int, total: int) -> str:
        if total == 0:
            return "0.0%"
        return f"{part / total * 100:.1f}%"

    volume_rows = []
    for path_rel, group_id, group_name in sources:
        source_name = Path(path_rel).name
        raw = per_source_raw.get(source_name, 0)
        after_dedupe = per_source_after_dedupe.get(source_name, 0)
        after_quality = stats.per_source_final.get(source_name, 0)
        survival = _fmt_pct(after_quality, raw) if raw else "—"
        volume_rows.append(
            f"| {source_name} | {group_name} | {raw} | {after_dedupe} | {after_quality} | {survival} |"
        )

    lines: list[str] = []
    lines.append("# FB corpus ingest report")
    lines.append("")
    lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("## 1. Executive summary")
    lines.append("")
    lines.append(
        f"Trzy scrape'y FB (2 grupy) zsumowane: **{total_raw}** surowych postów. "
        f"Po deduplikacji na SHA-256 pierwszych 200 znaków znormalizowanego tekstu "
        f"i po filtrach jakości (question pattern, job ads, community-only markers) "
        f"zostaje **{total_final}** postów unikalnych."
    )
    lines.append("")
    lines.append(
        f"Przy heurystyce ~100-150 postów na jeden klaster tematyczny, z tego korpusu "
        f"realistycznie wyjdzie **{cluster_estimate}** klastrów (Zadanie 2)."
    )
    lines.append("")
    lines.append("## 2. Volume table")
    lines.append("")
    lines.append("| Source file | Group | Raw | After dedupe | After quality | Survival |")
    lines.append("|---|---|---|---|---|---|")
    lines.extend(volume_rows)
    lines.append("")
    lines.append(
        f"Cross-file duplicates removed (resolved by newest scraped_at): "
        f"**{stats.cross_file_duplicates}**. Duplicates collapsed within a single file: "
        f"**{stats.duplicates_within_files}**."
    )
    lines.append("")
    lines.append("## 3. Quality breakdown")
    lines.append("")
    lines.append("### Rejected")
    lines.append("")
    lines.append("| Reason | Count |")
    lines.append("|---|---:|")
    for reason, count in rejections.items():
        lines.append(f"| {reason} | {count} |")
    lines.append("")
    lines.append("### Flagged (kept)")
    lines.append("")
    lines.append("| Flag | Count |")
    lines.append("|---|---:|")
    for flag, count in flags.items():
        lines.append(f"| {flag} | {count} |")
    lines.append("")
    lines.append("### Top 20 keywords in final corpus")
    lines.append("")
    lines.append("| Rank | Token | Frequency |")
    lines.append("|---:|---|---:|")
    for rank, (token, count) in enumerate(top_keywords, start=1):
        lines.append(f"| {rank} | {token} | {count} |")
    lines.append("")
    lines.append("## 4. Random sample (seed=42, n=10)")
    lines.append("")
    for entry in random_sample:
        excerpt = entry.text.replace("\n", " ").strip()
        if len(excerpt) > 300:
            excerpt = excerpt[:300].rstrip() + "…"
        lines.append(
            f"- **{entry.id}** · {entry.group_name} · comments: {entry.comments_count}\n"
            f"  > {excerpt}"
        )
    lines.append("")
    lines.append("## 5. Cross-file dedupe verification")
    lines.append("")
    lines.append(
        f"- Posty z backupu (2026-04-06, ta sama grupa 1), które miały duplikat w nowszym scrape grupy 1: "
        f"**{stats.backup_with_dup_in_newer_same_group} / {stats.backup_total}**. "
        f"Oczekiwanie: większość. Starszy snapshot jest nadzbiorem domeny czasowej nowszego."
    )
    lines.append(
        f"- Posty z grupy 1 (nowszy scrape), które miały duplikat w grupie 2 (hash match): "
        f"**{stats.group1_with_dup_in_group2} / {stats.group1_total}**. "
        f"Oczekiwanie: 0 albo bardzo mało — różne grupy, hash nie chwyta parafraz."
    )
    lines.append("")
    lines.append("## 6. Top 20 most engaging (by comments_count)")
    lines.append("")
    lines.append("| Rank | id | group | comments | text (first 200 chars) |")
    lines.append("|---:|---|---|---:|---|")
    for rank, record in enumerate(top_engaging, start=1):
        excerpt = record.text.replace("\n", " ").replace("|", "/").strip()
        if len(excerpt) > 200:
            excerpt = excerpt[:200].rstrip() + "…"
        lines.append(
            f"| {rank} | {record.id} | {record.group_name} | {record.comments_count} | {excerpt} |"
        )
    lines.append("")
    lines.append("## 7. Wpływ 1.5b fixes (Before / After)")
    lines.append("")
    lines.append(
        "Porównanie ilościowe v1 (commit 97a6efe, Zadanie 1) vs v1.5b (obecny run). "
        "v1.5b wprowadza strip cutoff markerów (`Wyświetl więcej`, ellipsis) przed "
        "hashem, rozszerzone prefiksy `job_ad`, nowe kategorie `sales_spam` i "
        "`marketing_bold`, oraz flagę `probably_comment`."
    )
    lines.append("")
    lines.append("| Metric | v1 | v1.5b | Δ |")
    lines.append("|---|---:|---:|---:|")

    def _delta_row(label: str, v1_key: str, current: int) -> str:
        baseline = BASELINE_V1.get(v1_key, 0)
        delta = current - baseline
        sign = "+" if delta > 0 else ""
        return f"| {label} | {baseline} | {current} | {sign}{delta} |"

    lines.append(_delta_row("Raw total", "raw_total", total_raw))
    lines.append(_delta_row("Final total", "final_total", total_final))
    lines.append(
        _delta_row(
            "Duplicates within files", "duplicates_within_files", stats.duplicates_within_files
        )
    )
    lines.append(
        _delta_row("Cross-file duplicates", "cross_file_duplicates", stats.cross_file_duplicates)
    )
    lines.append(_delta_row("Rejected: too_short", "rejected_too_short", stats.rejected_too_short))
    lines.append(
        _delta_row(
            "Rejected: no_question_pattern",
            "rejected_no_question_pattern",
            stats.rejected_no_question,
        )
    )
    lines.append(_delta_row("Rejected: job_ad", "rejected_job_ad", stats.rejected_job_ad))
    lines.append(
        _delta_row("Rejected: community_only", "rejected_community_only", stats.rejected_community_only)
    )
    lines.append(f"| Rejected: marketing_bold (new) | — | {stats.rejected_marketing_bold} | n/a |")
    lines.append(f"| Rejected: sales_spam (new) | — | {stats.rejected_sales_spam} | n/a |")
    lines.append(_delta_row("Flagged: too_long", "flagged_too_long", stats.flagged_too_long))
    lines.append(_delta_row("Flagged: no_comments", "flagged_no_comments", stats.flagged_no_comments))
    lines.append(_delta_row("Flagged: many_links", "flagged_many_links", stats.flagged_many_links))
    lines.append(f"| Flagged: probably_comment (new) | — | {stats.flagged_probably_comment} | n/a |")
    lines.append(f"| Cutoff markers stripped (new) | — | {stats.cutoff_stripped} | n/a |")
    lines.append("")
    lines.append(
        "Uwaga: spadek `final_total` między v1 i v1.5b to suma odrzuceń z trzech nowych "
        "reguł (`marketing_bold`, `sales_spam`, rozszerzone `job_ad`). Flagi nie "
        "usuwają postów z korpusu."
    )
    lines.append("")
    lines.append("## 8. Sample of `probably_comment` flag (10 random, seed=42)")
    lines.append("")
    lines.append(
        "Posty oznaczone flagą `probably_comment` nadal są w korpusie — to sygnał "
        "dla Zadania 2 (klasteryzacja), że prawdopodobnie są to wklejki komentarzy. "
        "Próbka losowa (seed=42)."
    )
    lines.append("")
    if probably_comment_sample:
        for entry in probably_comment_sample:
            excerpt = entry.text.replace("\n", " ").strip()
            if len(excerpt) > 300:
                excerpt = excerpt[:300].rstrip() + "…"
            lines.append(
                f"- **{entry.id}** · {entry.group_name} · comments: {entry.comments_count}\n"
                f"  > {excerpt}"
            )
    else:
        lines.append("- (brak rekordów z flagą `probably_comment`)")
    lines.append("")
    lines.append("## 9. Unrelated observations")
    lines.append("")
    if unrelated_observations:
        for note in unrelated_observations:
            lines.append(f"- {note}")
    else:
        lines.append("- (brak)")
    lines.append("")

    report_md = "\n".join(lines)

    report_json = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [
            {
                "file": Path(path_rel).name,
                "group_id": group_id,
                "group_name": group_name,
                "raw": per_source_raw.get(Path(path_rel).name, 0),
                "after_dedupe": per_source_after_dedupe.get(Path(path_rel).name, 0),
                "after_quality": stats.per_source_final.get(Path(path_rel).name, 0),
            }
            for path_rel, group_id, group_name in sources
        ],
        "totals": {
            "raw": total_raw,
            "after_dedupe": total_after_dedupe,
            "final": total_final,
            "duplicates_within_files": stats.duplicates_within_files,
            "cross_file_duplicates": stats.cross_file_duplicates,
            "cutoff_markers_stripped": stats.cutoff_stripped,
        },
        "baseline_v1": dict(BASELINE_V1),
        "probably_comment_sample": [
            {
                "id": r.id,
                "group_name": r.group_name,
                "comments_count": r.comments_count,
                "text_excerpt": (r.text[:300] + "…") if len(r.text) > 300 else r.text,
            }
            for r in probably_comment_sample
        ],
        "rejections": rejections,
        "flags": flags,
        "cluster_estimate": cluster_estimate,
        "cross_file_verification": {
            "backup_group1_with_dup_in_newer": stats.backup_with_dup_in_newer_same_group,
            "backup_group1_total": stats.backup_total,
            "group1_newer_with_dup_in_group2": stats.group1_with_dup_in_group2,
            "group1_newer_total": stats.group1_total,
        },
        "top_keywords": [{"token": t, "count": c} for t, c in top_keywords],
        "random_sample_seed": 42,
        "random_sample": [
            {
                "id": r.id,
                "group_name": r.group_name,
                "text_excerpt": (r.text[:300] + "…") if len(r.text) > 300 else r.text,
                "comments_count": r.comments_count,
            }
            for r in random_sample
        ],
        "top_engaging": [
            {
                "id": r.id,
                "group_name": r.group_name,
                "comments_count": r.comments_count,
                "text_excerpt": (r.text[:200] + "…") if len(r.text) > 200 else r.text,
            }
            for r in top_engaging
        ],
        "unrelated_observations": list(unrelated_observations),
    }

    return report_md, report_json


def _compute_cross_file_verification(
    ids_per_source: dict[str, set[str]],
    sources: list[tuple[str, str, str]],
) -> tuple[int, int, int, int]:
    """Return ``(backup_with_dup_in_newer, backup_total, g1_with_dup_in_g2, g1_total)``.

    The verification is purely informational — it runs against the raw per-source
    id sets so the counts describe the scrapes, not the deduplicated result.
    """

    newer_group1_file: str | None = None
    backup_group1_file: str | None = None
    group2_file: str | None = None
    for path_rel, group_id, _ in sources:
        name = Path(path_rel).name
        if group_id == "360545881004410":
            if "backup" in name:
                backup_group1_file = name
            else:
                newer_group1_file = name
        elif group_id == "507801603233194":
            group2_file = name

    backup_ids = ids_per_source.get(backup_group1_file or "", set())
    newer_ids = ids_per_source.get(newer_group1_file or "", set())
    group2_ids = ids_per_source.get(group2_file or "", set())

    backup_total = len(backup_ids)
    backup_hits = len(backup_ids & newer_ids) if backup_ids and newer_ids else 0
    g1_total = len(newer_ids)
    g1_hits = len(newer_ids & group2_ids) if newer_ids and group2_ids else 0
    return backup_hits, backup_total, g1_hits, g1_total


def run(
    sources: list[tuple[str, str, str]],
    output_jsonl: Path,
    report_md_path: Path,
    report_json_path: Path,
    apply: bool,
    repo_root: Path = REPO_ROOT,
) -> tuple[Stats, list[FinalRecord], dict]:
    stats = Stats()
    per_source_candidates: dict[str, list[CandidateRecord]] = {}
    per_source_raw: dict[str, int] = {}

    for index, (path_rel, group_id, group_name) in enumerate(sources, start=1):
        full_path = (repo_root / path_rel).resolve()
        LOGGER.info("[%d/%d] Loading %s", index, len(sources), path_rel)
        source = load_source(full_path, group_id, group_name)
        source_name = Path(path_rel).name
        per_source_raw[source_name] = len(source.posts)
        LOGGER.info(
            "  scraped_at=%s group=%s raw=%d",
            source.scraped_at,
            group_name,
            len(source.posts),
        )
        candidates, in_file_dupes, cutoff_stripped = build_candidates(source)
        stats.duplicates_within_files += in_file_dupes
        stats.cutoff_stripped += cutoff_stripped
        per_source_candidates[source_name] = candidates

    total_raw = sum(per_source_raw.values())
    LOGGER.info("Total raw: %d", total_raw)

    winners, cross_file_dupes, winners_per_source, ids_per_source = resolve_cross_file_duplicates(
        per_source_candidates
    )
    stats.cross_file_duplicates = cross_file_dupes
    stats.per_source_after_dedupe = dict(winners_per_source)
    total_unique = len(winners)
    LOGGER.info(
        "Deduplication: unique=%d  within_file=%d  cross_file=%d",
        total_unique,
        stats.duplicates_within_files,
        stats.cross_file_duplicates,
    )

    (
        stats.backup_with_dup_in_newer_same_group,
        stats.backup_total,
        stats.group1_with_dup_in_group2,
        stats.group1_total,
    ) = _compute_cross_file_verification(ids_per_source, sources)

    final_records = finalize(winners, stats)
    LOGGER.info(
        "Quality: rejected short=%d no_q=%d job=%d community=%d marketing=%d sales=%d | "
        "flagged long=%d no_comm=%d many_links=%d prob_comment=%d | cutoff_stripped=%d",
        stats.rejected_too_short,
        stats.rejected_no_question,
        stats.rejected_job_ad,
        stats.rejected_community_only,
        stats.rejected_marketing_bold,
        stats.rejected_sales_spam,
        stats.flagged_too_long,
        stats.flagged_no_comments,
        stats.flagged_many_links,
        stats.flagged_probably_comment,
        stats.cutoff_stripped,
    )
    LOGGER.info("Final corpus: %d posts", len(final_records))

    unrelated_observations = [
        (
            "README.md opisuje tylko wcześniejszy stateless scaffold — brak wzmianki o workflow "
            "layer, intent routing i clarification gate, które są już w repo. Dokumentacyjny dług, "
            "do naprawy osobno."
        ),
        (
            "fb_pipeline/posts_tagged.json (10700 rekordów) to post-processed wariant "
            "posts_output_backup.json z dodanymi polami tag/char_count. Nie jest używany w tym "
            "ingestie, ale nadal jest tracked w git i nie w .gitignore — można rozważyć "
            "osobne uprzątnięcie legacy pipeline'u."
        ),
        (
            "v1.5b: usunięto scraperowe cutoff markery (`Wyświetl więcej`, ellipsis) przed "
            "obliczeniem hasha. Efekt: mniej fałszywych duplikatów i czysty top-N keywords "
            "bez tokenów UI."
        ),
        (
            "v1.5b: flaga `probably_comment` nie usuwa postów, tylko oznacza prawdopodobne "
            "wklejki komentarzy. Klasteryzacja w Zadaniu 2 może ich używać z niższą wagą, "
            "albo zrobić osobny klaster \"opinie/komentarze\"."
        ),
    ]

    report_md, report_json = build_reports(
        stats=stats,
        per_source_raw=per_source_raw,
        per_source_after_dedupe=stats.per_source_after_dedupe,
        final_records=final_records,
        sources=sources,
        unrelated_observations=unrelated_observations,
    )

    if apply:
        output_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with output_jsonl.open("w", encoding="utf-8") as handle:
            for record in final_records:
                handle.write(json.dumps(record.to_dict(), ensure_ascii=False))
                handle.write("\n")
        LOGGER.info("Wrote corpus -> %s", output_jsonl)

        report_md_path.parent.mkdir(parents=True, exist_ok=True)
        report_md_path.write_text(report_md, encoding="utf-8")
        report_json_path.write_text(
            json.dumps(report_json, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        LOGGER.info("Wrote report -> %s (+ .json)", report_md_path)
    else:
        LOGGER.info("Dry-run: no files written. Re-run with --apply to persist corpus + report.")

    return stats, final_records, report_json


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write corpus JSONL and analysis report. Without this flag the run is read-only.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit dry-run (default behaviour when --apply is absent).",
    )
    parser.add_argument(
        "--output-jsonl",
        type=Path,
        default=None,
        help=f"Override output corpus path (default: {DEFAULT_OUTPUT_JSONL}).",
    )
    parser.add_argument(
        "--report-md",
        type=Path,
        default=None,
        help=f"Override report MD path (default: {DEFAULT_REPORT_MD}).",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=None,
        help=f"Override report JSON path (default: {DEFAULT_REPORT_JSON}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run are mutually exclusive")

    apply = bool(args.apply)

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        stream=sys.stdout,
    )

    sources = [(path_rel, group_id, group_name) for path_rel, group_id, group_name in DEFAULT_SOURCES]
    output_jsonl = (REPO_ROOT / (args.output_jsonl or DEFAULT_OUTPUT_JSONL)).resolve()
    report_md_path = (REPO_ROOT / (args.report_md or DEFAULT_REPORT_MD)).resolve()
    report_json_path = (REPO_ROOT / (args.report_json or DEFAULT_REPORT_JSON)).resolve()

    run(
        sources=sources,
        output_jsonl=output_jsonl,
        report_md_path=report_md_path,
        report_json_path=report_json_path,
        apply=apply,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
