from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from rank_bm25 import BM25Okapi

from core.categorizer import categorize_query
from data.ingest import load_seed_laws


POLISH_STOP_WORDS = {
    "i",
    "w",
    "na",
    "do",
    "z",
    "o",
    "od",
    "dla",
    "jest",
    "nie",
    "sie",
    "to",
    "ze",
    "jak",
    "po",
    "za",
    "co",
    "czy",
    "ale",
    "lub",
    "oraz",
    "przez",
    "przy",
    "bez",
    "pod",
    "nad",
    "przed",
    "miedzy",
    "jako",
    "tylko",
    "tez",
    "juz",
    "ten",
    "ta",
    "te",
    "tego",
    "tej",
    "tym",
    "tych",
    "temu",
    "ich",
    "jego",
    "jej",
}


@dataclass(slots=True)
class LawChunk:
    content: str
    law_name: str
    article_number: str
    category: str
    verified_date: str
    question_intent: str = ""
    score: float = 0.0


_CACHE_LOCK = Lock()
_KNOWLEDGE_CACHE: dict[str, tuple[int, tuple[LawChunk, ...], BM25Okapi, tuple[tuple[str, ...], ...]]] = {}


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def _tokenize(text: str) -> list[str]:
    normalized = _normalize(text)
    tokens = re.findall(r"[a-z0-9_]+", normalized)
    return [token for token in tokens if token not in POLISH_STOP_WORDS]


def _category_matches(query_category: str, chunk: LawChunk) -> bool:
    if chunk.category == query_category:
        return True

    haystack = _normalize(" ".join([chunk.category, chunk.law_name, chunk.content, chunk.question_intent]))

    category_aliases = {
        "ksef": (
            "ksef",
            "krajowy system e-faktur",
            "e-faktura",
            "ustrukturyz",
        ),
        "fakturowanie": (
            "fakturowanie",
            "faktura",
            "faktury",
            "paragon",
            "duplikat",
        ),
        "faktury_korygujące": (
            "faktury_korygujace",
            "korekta_faktury",
            "faktura korygujaca",
            "koryguj",
            "nip",
        ),
        "korekty": (
            "korekta",
            "korekty_vat",
            "ulga_na_zle_dlugi",
        ),
        "terminy": (
            "termin",
            "terminy",
            "jpk",
            "deklaracja",
            "deklaracje",
        ),
        "podatek_naliczony": (
            "podatek_naliczony",
            "odliczenie_vat",
            "naliczony",
        ),
        "podatek_należny": (
            "podatek_nalezny",
            "obowiazek_podatkowy",
            "nalezny",
        ),
        "vat": (
            "vat",
            "zwrot_vat",
            "zwolnienie_z_vat",
            "rejestracja_vat",
        ),
        "pit": (
            "pit",
            "podatek dochodowy",
            "pit-36",
            "pit-37",
            "pit-11",
            "kwota wolna",
            "skala podatkowa",
            "podatek liniowy",
        ),
        "cit": (
            "cit",
            "podatek dochodowy od osob prawnych",
            "estonski cit",
            "ryczalt od dochodow spolek",
            "wht",
            "podatek u zrodla",
            "ceny transferowe",
            "tpr",
            "cit-8",
            "maly podatnik cit",
            "ift-2r",
        ),
        "zus": (
            "zus",
            "skladka",
            "skladki",
            "skladka zdrowotna",
            "skladka spoleczna",
            "maly zus",
            "preferencyjny zus",
            "ulga na start",
            "dra",
            "rca",
            "zasilek",
            "chorobowe",
            "macierzynski",
            "zbieg tytulow",
            "podstawa wymiaru",
        ),
        "kadry": (
            "kodeks pracy",
            "umowa o prace",
            "urlop",
            "wynagrodzenie minimalne",
            "nadgodziny",
            "wypowiedzenie",
            "swiadectwo pracy",
            "l4",
            "zasilek chorobowy",
            "czas pracy",
            "okres probny",
            "praca zdalna",
            "bhp",
            "badania lekarskie",
            "macierzynski",
            "rodzicielski",
            "ekwiwalent",
        ),
        "ordynacja": (
            "ordynacja podatkowa",
            "przedawnienie",
            "kontrola podatkowa",
            "interpretacja indywidualna",
            "nadplata",
            "zaleglosc podatkowa",
            "odsetki za zwloke",
            "pelnomocnictwo",
        ),
        "jpk": (
            "jpk",
            "jpk_v7",
            "jpk_vat",
            "gtu",
            "oznaczenia jpk",
        ),
        "rachunkowosc": (
            "bilans",
            "rachunek zyskow i strat",
            "sprawozdanie finansowe",
            "ksiegi rachunkowe",
            "kpir",
            "srodki trwale",
            "amortyzacja",
            "inwentaryzacja",
            "rezerwa",
            "rmk",
            "odpis aktualizujacy",
        ),
    }

    return any(alias in haystack for alias in category_aliases.get(query_category, ()))


def load_chunks(knowledge_path: str | Path) -> list[LawChunk]:
    path = Path(knowledge_path).resolve()
    mtime_ns = path.stat().st_mtime_ns
    cache_key = str(path)

    with _CACHE_LOCK:
        cached = _KNOWLEDGE_CACHE.get(cache_key)
        if cached and cached[0] == mtime_ns:
            return list(cached[1])

    records = load_seed_laws(path)
    chunks = tuple(
        LawChunk(
            content=str(record.get("answer") or record.get("content") or "").strip(),
            law_name=str(record.get("law_name", "")).strip(),
            article_number=str(record.get("article_number", "")).strip(),
            category=str(record.get("category", "")).strip(),
            verified_date=str(record.get("verified_date", "")).strip(),
            question_intent=str(record.get("question_intent", "")).strip(),
        )
        for record in records
        if str(record.get("answer") or record.get("content") or "").strip()
    )

    tokenized_corpus = tuple(
        tuple(_tokenize(" ".join(part for part in (chunk.question_intent, chunk.content) if part)))
        for chunk in chunks
    )
    bm25 = BM25Okapi([list(tokens) if tokens else ["_empty_"] for tokens in tokenized_corpus])

    with _CACHE_LOCK:
        _KNOWLEDGE_CACHE[cache_key] = (mtime_ns, chunks, bm25, tokenized_corpus)

    return list(chunks)


def _load_bm25_cache(knowledge_path: str | Path) -> tuple[list[LawChunk], BM25Okapi, list[tuple[str, ...]]]:
    path = Path(knowledge_path).resolve()
    mtime_ns = path.stat().st_mtime_ns
    cache_key = str(path)

    with _CACHE_LOCK:
        cached = _KNOWLEDGE_CACHE.get(cache_key)
        if cached and cached[0] == mtime_ns:
            return list(cached[1]), cached[2], list(cached[3])

    load_chunks(path)
    with _CACHE_LOCK:
        cached = _KNOWLEDGE_CACHE[cache_key]
        return list(cached[1]), cached[2], list(cached[3])


def retrieve_chunks(query: str, knowledge_path: str | Path, limit: int = 5) -> list[LawChunk]:
    chunks, bm25, _ = _load_bm25_cache(knowledge_path)
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    query_category = categorize_query(query)
    scores = bm25.get_scores(query_tokens)
    scored: list[tuple[float, LawChunk]] = []

    for score, chunk in zip(scores, chunks, strict=False):
        boosted_score = float(score)
        if _category_matches(query_category, chunk):
            boosted_score *= 1.5
        scored.append(
            (
                boosted_score,
                LawChunk(
                    content=chunk.content,
                    law_name=chunk.law_name,
                    article_number=chunk.article_number,
                    category=chunk.category,
                    verified_date=chunk.verified_date,
                    question_intent=chunk.question_intent,
                    score=boosted_score,
                ),
            )
        )

    scored.sort(
        key=lambda item: (
            item[0],
            item[1].verified_date,
            item[1].law_name,
            item[1].article_number,
        ),
        reverse=True,
    )
    return [chunk for _, chunk in scored[:limit]]
