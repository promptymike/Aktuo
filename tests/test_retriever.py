from __future__ import annotations

import json

from core.retriever import retrieve_chunks


def test_retrieve_chunks_prefers_matching_polish_category(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106e",
                    "category": "fakturowanie",
                    "verified_date": "2026-04-01",
                    "question_intent": "Jakie elementy powinna zawierać faktura?",
                    "content": "Faktura powinna zawierać podstawowe dane sprzedawcy i nabywcy.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 99",
                    "category": "terminy",
                    "verified_date": "2026-04-01",
                    "question_intent": "Jaki jest termin złożenia deklaracji JPK_V7?",
                    "content": "Deklarację JPK_V7 składa się w ustawowym terminie za dany okres.",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("Jaki jest termin złożenia deklaracji JPK_V7?", seed_file, limit=1)

    assert len(chunks) == 1
    assert chunks[0].article_number == "art. 99"


def test_retrieve_chunks_returns_top_five_results_for_bm25_query(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106e",
                    "category": "fakturowanie",
                    "verified_date": "2026-04-01",
                    "question_intent": "Co musi zawierać faktura?",
                    "content": "Faktura powinna zawierać numer oraz datę wystawienia.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106h",
                    "category": "faktury",
                    "verified_date": "2026-04-02",
                    "question_intent": "Kiedy można wystawić fakturę do paragonu?",
                    "content": "Fakturę można wystawić do paragonu fiskalnego w określonych przypadkach.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 106i",
                    "category": "fakturowanie",
                    "verified_date": "2026-04-03",
                    "question_intent": "Jaki jest termin wystawienia faktury?",
                    "content": "Termin wystawienia faktury zależy od rodzaju transakcji.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 99",
                    "category": "terminy",
                    "verified_date": "2026-04-01",
                    "question_intent": "Kiedy składa się deklaracje VAT?",
                    "content": "Deklaracje podatkowe składa się miesięcznie albo kwartalnie.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 86",
                    "category": "podatek_naliczony",
                    "verified_date": "2026-04-04",
                    "question_intent": "Kiedy można odliczyć VAT naliczony?",
                    "content": "Podatek naliczony można odliczyć, jeśli zakup służy czynnościom opodatkowanym.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 19a",
                    "category": "podatek_należny",
                    "verified_date": "2026-04-05",
                    "question_intent": "Kiedy powstaje obowiązek podatkowy w VAT?",
                    "content": "Obowiązek podatkowy powstaje z chwilą dokonania dostawy towarów lub wykonania usługi.",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("Kiedy trzeba wystawić fakturę i co powinna zawierać?", seed_file)

    assert len(chunks) == 5
    top_three = {chunk.article_number for chunk in chunks[:3]}
    assert "art. 106h" in top_three
    assert {"art. 106e", "art. 106i"} & top_three


def test_retrieve_chunks_hard_filters_for_cit_category(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o podatku dochodowym od osób prawnych",
                    "article_number": "art. 28j",
                    "category": "cit",
                    "verified_date": "2026-04-01",
                    "question_intent": "Kto może wybrać estoński CIT?",
                    "content": "Estoński CIT mogą wybrać spółki spełniające warunki ustawowe.",
                },
                {
                    "law_name": "Ustawa o podatku dochodowym od osób prawnych",
                    "article_number": "art. 28k",
                    "category": "cit",
                    "verified_date": "2026-04-02",
                    "question_intent": "Jakie warunki trzeba spełnić dla estońskiego CIT?",
                    "content": "Warunki estońskiego CIT obejmują strukturę przychodów i zatrudnienia.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 89a",
                    "category": "vat",
                    "verified_date": "2026-04-03",
                    "question_intent": "Kto musi płacić VAT po korekcie podatku?",
                    "content": "VAT trzeba rozliczyć zgodnie z ustawą o VAT.",
                },
                {
                    "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
                    "article_number": "art. 30ca",
                    "category": "pit",
                    "verified_date": "2026-04-04",
                    "question_intent": "Kto musi płacić podatek dochodowy i kiedy składa PIT?",
                    "content": "Podatek dochodowy osób fizycznych rozlicza się w zeznaniu rocznym.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 31a",
                    "category": "vat",
                    "verified_date": "2026-04-05",
                    "question_intent": "Kto musi płacić podatek przy przeliczeniu faktury?",
                    "content": "Przeliczenie walut dla VAT reguluje ustawa o VAT.",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("Kto musi płacić estoński CIT?", seed_file)

    assert sum(
        1 for chunk in chunks if chunk.law_name == "Ustawa o podatku dochodowym od osób prawnych"
    ) >= 2


def test_retrieve_chunks_hard_filters_for_zus_category(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Ustawa o systemie ubezpieczeń społecznych",
                    "article_number": "art. 9",
                    "category": "zus",
                    "verified_date": "2026-04-01",
                    "question_intent": "Jak działa zbieg tytułów do ubezpieczeń przy działalności i zleceniu?",
                    "content": "Zbieg tytułów ZUS przy działalności i umowie zlecenia reguluje art. 9.",
                },
                {
                    "law_name": "Ustawa o systemie ubezpieczeń społecznych",
                    "article_number": "art. 6",
                    "category": "zus",
                    "verified_date": "2026-04-02",
                    "question_intent": "Kto podlega ubezpieczeniom społecznym przy umowie zlecenia?",
                    "content": "Obowiązek ubezpieczeń społecznych przy zleceniu wynika z art. 6.",
                },
                {
                    "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
                    "article_number": "art. 5b",
                    "category": "pit",
                    "verified_date": "2026-04-03",
                    "question_intent": "Czy działalność i zlecenie to działalność gospodarcza?",
                    "content": "Działalność gospodarcza jest definiowana w ustawie o PIT.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 15",
                    "category": "vat",
                    "verified_date": "2026-04-04",
                    "question_intent": "Kto jest podatnikiem VAT przy działalności i umowie?",
                    "content": "Podatnikiem VAT jest podmiot wykonujący działalność gospodarczą.",
                },
                {
                    "law_name": "Kodeks pracy",
                    "article_number": "art. 2",
                    "category": "kadry",
                    "verified_date": "2026-04-05",
                    "question_intent": "Czy umowa zlecenia jest umową o pracę?",
                    "content": "Kodeks pracy definiuje pracownika i umowę o pracę.",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("Zbieg tytułów ZUS umowa zlecenia i działalność", seed_file)

    assert sum(
        1 for chunk in chunks if chunk.law_name == "Ustawa o systemie ubezpieczeń społecznych"
    ) >= 2


def test_retrieve_chunks_hard_filters_for_kadry_category(tmp_path) -> None:
    seed_file = tmp_path / "law_knowledge.json"
    seed_file.write_text(
        json.dumps(
            [
                {
                    "law_name": "Kodeks pracy",
                    "article_number": "art. 36",
                    "category": "kadry",
                    "verified_date": "2026-04-01",
                    "question_intent": "Jakie są okresy wypowiedzenia umowy o pracę?",
                    "content": "Okresy wypowiedzenia umowy o pracę zależą od stażu pracy.",
                },
                {
                    "law_name": "Kodeks pracy",
                    "article_number": "art. 30",
                    "category": "kadry",
                    "verified_date": "2026-04-02",
                    "question_intent": "W jaki sposób rozwiązuje się umowę o pracę?",
                    "content": "Umowa o pracę może być rozwiązana za wypowiedzeniem albo bez wypowiedzenia.",
                },
                {
                    "law_name": "Ustawa o VAT",
                    "article_number": "art. 112",
                    "category": "vat",
                    "verified_date": "2026-04-03",
                    "question_intent": "Jak długo przechowywać dokumenty po rozwiązaniu umowy?",
                    "content": "VAT reguluje przechowywanie faktur i ewidencji.",
                },
                {
                    "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
                    "article_number": "art. 12",
                    "category": "pit",
                    "verified_date": "2026-04-04",
                    "question_intent": "Jak rozliczyć umowę o pracę i wynagrodzenie?",
                    "content": "Przychody ze stosunku pracy reguluje ustawa o PIT.",
                },
                {
                    "law_name": "Ustawa o systemie ubezpieczeń społecznych",
                    "article_number": "art. 6",
                    "category": "zus",
                    "verified_date": "2026-04-05",
                    "question_intent": "Jakie składki płaci pracownik na umowie o pracę?",
                    "content": "Ubezpieczenia społeczne pracownika reguluje ustawa o systemie ubezpieczeń społecznych.",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    chunks = retrieve_chunks("Jakie są okresy wypowiedzenia umowy o pracę?", seed_file)

    assert sum(1 for chunk in chunks if chunk.law_name == "Kodeks pracy") >= 2
