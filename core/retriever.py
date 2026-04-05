from __future__ import annotations

import re
from threading import Lock
from dataclasses import dataclass
from pathlib import Path

from core.categorizer import categorize_query
from data.ingest import ingest_seed_chunks


@dataclass(slots=True)
class LawChunk:
    content: str
    law_name: str
    article_number: str
    category: str
    verified_date: str


_CACHE_LOCK = Lock()
_CHUNK_CACHE: dict[str, tuple[int, tuple[LawChunk, ...]]] = {}


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _normalize(text: str) -> str:
    translation = str.maketrans(
        {
            "ą": "a",
            "ć": "c",
            "ę": "e",
            "ł": "l",
            "ń": "n",
            "ó": "o",
            "ś": "s",
            "ż": "z",
            "ź": "z",
        }
    )
    return text.lower().translate(translation)


def _category_matches(query_category: str, chunk: LawChunk) -> bool:
    if chunk.category == query_category:
        return True

    haystack = _normalize(" ".join([chunk.category, chunk.law_name, chunk.content]))

    category_aliases = {
        "ksef": (
            "ksef",
            "krajowy system e-faktur",
            "e-faktur",
            "e-faktura",
            "ustrukturyz",
            "uprawnienia_ksef",
            "terminy_ksef",
            "autoryzacja_ksef",
        ),
        "fakturowanie": (
            "fakturowanie",
            "faktury",
            "wystawianie_faktur",
            "dokumentowanie_sprzedazy",
            "faktury_elektroniczne",
            "kasy_fiskalne",
            "duplikat",
        ),
        "faktury_korygujące": (
            "faktury_korygujace",
            "korekta_faktury",
            "korekty_faktur",
            "faktura korygujaca",
            "koryguj",
        ),
        "korekty": (
            "korekty_vat",
            "korekta_vat_naliczony",
            "ulga_na_zle_dlugi",
            "korekta",
        ),
        "terminy": (
            "terminy",
            "deklaracje vat",
            "obowiazki_deklaracyjne",
            "okresy_rozliczeniowe",
            "ewidencja_jpk",
            "jpk",
            "termin",
        ),
        "podatek_naliczony": (
            "podatek_naliczony",
            "odliczenie_vat",
            "odliczenia_vat",
            "odliczenia_vat_pojazdy",
            "korekta_vat_naliczony",
            "naliczony",
        ),
        "podatek_należny": (
            "podatek_nalezny",
            "obowiazek_podatkowy",
            "obowiazek podatkowy",
            "stawki_vat",
            "zakres_opodatkowania_vat",
            "dostawa_towarow",
            "import_towarow",
            "import uslug",
            "nalezny",
        ),
        "vat": (
            "vat",
            "rejestracja_vat",
            "rejestracja_vat_ue",
            "zwolnienie_z_vat",
            "zwrot_vat",
            "sankcje_podatkowe_vat",
            "stawki_vat",
        ),
    }

    return any(alias in haystack for alias in category_aliases.get(query_category, ()))


def load_chunks(knowledge_path: str | Path) -> list[LawChunk]:
    path = Path(knowledge_path).resolve()
    mtime_ns = path.stat().st_mtime_ns
    cache_key = str(path)

    with _CACHE_LOCK:
        cached = _CHUNK_CACHE.get(cache_key)
        if cached and cached[0] == mtime_ns:
            return list(cached[1])

    chunks = tuple(
        LawChunk(
            content=chunk.content,
            law_name=chunk.law_name,
            article_number=chunk.article_number,
            category=chunk.category,
            verified_date=chunk.verified_date,
        )
        for chunk in ingest_seed_chunks(path)
    )

    with _CACHE_LOCK:
        _CHUNK_CACHE[cache_key] = (mtime_ns, chunks)

    return list(chunks)


def retrieve_chunks(query: str, knowledge_path: str | Path, limit: int = 3) -> list[LawChunk]:
    query_tokens = _tokenize(query)
    query_category = categorize_query(query)
    scored: list[tuple[int, LawChunk]] = []

    for chunk in load_chunks(knowledge_path):
        searchable_text = " ".join(
            [chunk.content, chunk.law_name, chunk.article_number, chunk.category]
        )
        chunk_tokens = _tokenize(searchable_text)
        score = len(query_tokens & chunk_tokens)
        if _category_matches(query_category, chunk):
            score += 2
        if score > 0:
            scored.append((score, chunk))

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
