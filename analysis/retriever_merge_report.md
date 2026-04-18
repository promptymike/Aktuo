# Retriever Merge Report — 42 workflow drafts wired into pipeline

Data: 2026-04-18
Branch: main
Cel: Streamlit ma widzieć wszystkie 42 drafty z `data/workflow_drafts/`, nie tylko 10 legacy seed units z `data/workflow/workflow_seed.json`.

## TL;DR

- ✅ Retriever ładuje **52 units** (42 workflow_draft_v2 + 10 workflow_seed_v1).
- ✅ 5/5 test pytań trafia oczekiwany draft na #1 (wszystkie `confident=True`).
- ✅ pytest 260 passed — brak regresji.
- ✅ Streamlit boots cleanly na `app/main.py`.
- 🔑 Zero LLM calls, czysty refactor (~180 LOC).

## Co zmienione

### `config/settings.py`
Nowa zmienna `WORKFLOW_DRAFTS_DIR` (env `AKTUO_WORKFLOW_DRAFTS_DIR`, domyślnie `data/workflow_drafts`).

### `core/workflow_retriever.py`
Trzy rzeczy:

1. **Dual-source loader.** `load_workflow_documents()` przy wywołaniu z domyślnym `WORKFLOW_SEED_PATH` automatycznie dołącza drafty z `WORKFLOW_DRAFTS_DIR` (sorted alfabetycznie, skip plików bez `title` lub z nieznanym schematem). Testy przekazujące `workflow_path=tmp_path/...` nadal dostają wyłącznie seed (drafts dir pomijany — izolacja fixtures).
2. **V2 schema mapping.**
   - `id` → `LawChunk.article_number`
   - `title` → `LawChunk.title`
   - `topic_area` → `category`, `workflow_area`, `category_tokens`
   - `question_examples` + `answer_steps` details + `edge_cases` + `common_mistakes` → `example_tokens` (rich body, fixes Polish morphology miss)
   - `legal_anchors` (obsługuje oba warianty — `{law_name, article_number, reason}` i `{short_name, full_name, description}`) → renderowane do `content` + `form_tokens`
   - `common_mistakes` + `edge_cases` → `workflow_common_pitfalls` (dla downstream UI)
   - `last_verified_at` zachowane
   - `source_type = "workflow_draft_v2"` (distinct od legacy `workflow_seed_v1`)
3. **Lightweight Polish stemmer.** Nowa funkcja `_stem()` + stem-expansion w `_tokenize()`. Strippuje pojedynczy suffix deklinacyjny (ego/emu/ych/ymi/ach/ami/ej/ie/ia/iu/ym/em/om/y/i/a/e/u/o itd.) zachowując min 4-char stem. Token set = `{oryginalny_token, stem}`. Dzięki temu `komorniczym` ≡ `komornicze` ≡ `komorniczych` (wszystkie → stem `komornicz`), `stawki` ≡ `stawka`, `diety` ≡ `diet`, etc. Bez zewnętrznych deps, deterministyczny, O(n) na token.

### Zachowany backward compat
- Legacy `workflow_seed.json` (10 units) działa dalej, po prostu ładuje się AFTER drafts (niższa pozycja przy ties, bo drafts sorted first).
- Istniejący `_build_workflow_content()` nietknięty.
- Tests używają `workflow_path=tmp_path/*.json` → drafts dir niedotknięty → 260 passed.

### Niedotknięte
- UI / app/main.py / sidebar — backend-only refactor.
- `self_critique`, `corrections_applied`, `community_feedback_summary` — zachowane w plikach JSON, nie wpychane do `LawChunk` (jeśli w przyszłości UI chce disclaimery, można dodać dedykowane pole do `LawChunk`).
- Batch logi (`batch1_drafts.jsonl`, `batch2_run_log.json`) — ignorowane przez `_load_drafts_dir` bo glob `wf_*.json`.
- Pliki bez `title` albo bez `answer_steps`/`steps` — skip.

## 5 test pytań

```
confident threshold: 6.0 (z AKTUO_WORKFLOW_CONFIDENCE_THRESHOLD)
limit: 3
```

### Q1. "Jak wystawić fakturę korygującą w KSeF?"
Oczekiwane: `wf_merge_120_121` lub `wf_139`.

| # | score | source_type | id | hit |
|---|-------|-------------|-----|-----|
| 1 | 39.50 | workflow_draft_v2 | wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze | ✅ |
| 2 | 38.50 | workflow_draft_v2 | wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty | ✅ |
| 3 | 34.50 | workflow_draft_v2 | wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt | — |

`confident=True, top=39.50`.

### Q2. "Jaka jest kwota wolna przy zajęciu komorniczym w 2026?"
Oczekiwane: `wf_10`.

| # | score | source_type | id | hit |
|---|-------|-------------|-----|-----|
| 1 | 34.50 | workflow_draft_v2 | wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlecen | ✅ |
| 2 | 21.50 | workflow_draft_v2 | wf_82_skladka_zdrowotna_przy_zmianie_formy_opodatkowania | — |
| 3 | 21.50 | workflow_draft_v2 | wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica | — |

`confident=True, top=34.50`. **Kluczowy hit — bez stemmera trafiało `wf_71` (minimalne wynagrodzenie 2026) bo tam `2026` występuje w tytule; po stemmerze `komorniczym→komornicz` matchuje `komornicze` i wf_10 dominuje.**

### Q3. "Jak rozliczyć leasing samochodu osobowego?"
Oczekiwane: `wf_63`.

| # | score | source_type | id | hit |
|---|-------|-------------|-----|-----|
| 1 | 64.50 | workflow_draft_v2 | wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat | ✅ |
| 2 | 53.50 | workflow_draft_v2 | wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu | — |
| 3 | 31.50 | workflow_seed_v1  | Leasing, wykup samochodu i ewidencja kosztów pojazdu | — |

`confident=True, top=64.50`. Legacy seed unit pojawia się jako #3 → backward compat OK.

### Q4. "Jakie są stawki diet zagranicznych w 2026?"
Oczekiwane: `wf_19`.

| # | score | source_type | id | hit |
|---|-------|-------------|-----|-----|
| 1 | 33.50 | workflow_draft_v2 | wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice | ✅ |
| 2 | 20.50 | workflow_draft_v2 | wf_48_ryczalt_dobor_stawki_wg_rodzaju_uslugi | — |
| 3 | 20.50 | workflow_draft_v2 | wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica | — |

`confident=True, top=33.50`.

### Q5. "Jak oznaczyć fakturę WNT w JPK od lutego 2026?"
Oczekiwane: `wf_107`.

| # | score | source_type | id | hit |
|---|-------|-------------|-----|-----|
| 1 | 66.50 | workflow_draft_v2 | wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_poza_ksef | ✅ |
| 2 | 34.50 | workflow_draft_v2 | wf_66_ksiegowanie_faktur_zagranicznych_wnt_import_uslug | — |
| 3 | 33.50 | workflow_draft_v2 | wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty | — |

`confident=True, top=66.50`.

## Pytest
```
260 passed in 5.71s
```

Testy nieruszone. Nowe test-case dla v2 loadera celowo NIE dodany w tym PRze (user request: "NIE twórz nowego schema, używaj tego co jest w draftach" + zakres "pure refactor $0"). Osobny follow-up w sekcji niżej.

## Streamlit startup
```
$ python -m streamlit run app/main.py --server.headless=true --server.port=8601 ...

  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8601
```

## Uwagi dla follow-upu

1. **Test coverage dla drafts loader** — dodać `tests/test_workflow_retriever.py::test_load_workflow_documents_merges_drafts_dir` używający `monkeypatch.setattr("core.workflow_retriever.WORKFLOW_DRAFTS_DIR", tmp_dir)` i weryfikujący że 42-rekordowy payload (mock) dociera do documents.
2. **UI disclaimer dla v2 drafts** — przy top hit `source_type == "workflow_draft_v2"` można w sidebar pokazać info "draft v2 — może zawierać corrections_applied z verifier pipeline". Obecnie UI tego nie rozróżnia.
3. **`self_critique` persistence** — nie jest obecnie wykorzystywane przez retriever/generator; rozważyć czy warto dodać `LawChunk.self_critique_flag_count` dla UI "tester warning".
4. **Legacy seed sunset** — 10 legacy units w `workflow_seed.json` duplikuje się częściowo z 42 draftami (szczegóły: [workflow_seed_vs_drafts_comparison.md](workflow_seed_vs_drafts_comparison.md)). Nie ma potrzeby go usuwać teraz, ale przy ewentualnej batch 3 generacji draftów wymigających pozostałe 5 legacy topics można plik zdeprekować.
5. **Polish stemmer skromny** — obecny `_stem()` strippuje jeden suffix; nie obsługuje palatalizacji (`-cki` → `-ckiego` → `-ckich`). Dla 5/5 Q's wystarczające; przy potrzebie rozważyć pystempel (dep pystempel MIT, ~50KB).

## Instrukcja dla Pawła

```bash
# 1. Upewnij się że masz env:
export AKTUO_ANTHROPIC_API_KEY=sk-ant-...

# 2. Odpal Streamlit:
cd C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main
python -m streamlit run app/main.py
# albo po prostu: streamlit run app/main.py

# 3. Przeglądarka otworzy http://localhost:8501

# 4. Testuj 30 pytań - teraz retriever widzi 42 drafty:
#    - kadry/ZUS (wf_4, wf_7, wf_8, wf_10, wf_19, wf_35, wf_45, wf_71, ...)
#    - KSeF/JPK (wf_99, wf_107, wf_139, wf_merge_120_121, ...)
#    - KPiR/rachunkowość (wf_21, wf_49, wf_51, wf_110, ...)
#    - VAT/PIT/ryczałt (wf_48, wf_53, wf_62, wf_63, wf_75, wf_82, wf_94, ...)
```

W razie wątpliwości czy konkretne pytanie trafia prawidłowy draft:
```bash
python -c "
from core.workflow_retriever import retrieve_workflow
r = retrieve_workflow('twoje pytanie tutaj', limit=3)
for c in r.chunks:
    print(c.score, c.source_type, c.article_number)
"
```
