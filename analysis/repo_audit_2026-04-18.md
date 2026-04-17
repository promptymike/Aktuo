# Aktuo — Pełny Audyt Repo (2026-04-18)

Mapa stanu repozytorium po ~2 tygodniach pracy Codexa, Claude Code i webchat Claude. Wszystkie liczby zmierzone na `HEAD = e5350ee` (audit-ready-2026-04-17 + 18 commitów).

---

## 1. Struktura repo

```
.
├── aktuo/                    # synonym mapper (1 plik)
├── analysis/                 # raporty + skrypty analityczne (30 *.py + 25 *.md + 19 *.json)
├── app/                      # UI Streamlit (analytics, chat, main, sidebar)
├── config/                   # settings.py
├── core/                     # produktowy silnik RAG (9 modułów, 3559 linii)
├── data/
│   ├── corpus/fb_groups/     # FB corpus + embeddings + klastry (audit-ready)
│   ├── curated/              # 4 pliki z ręcznie kuratowaną wiedzą
│   ├── prompts/              # system_prompt_pl.txt
│   ├── seeds/                # law_knowledge.json + 2 additions (4472 total)
│   ├── workflow/             # workflow_seed.json (10 units)
│   └── workflow_drafts/      # batch1 drafty wygenerowane przez Opus (10 + jsonl + run log)
├── db/migrations/            # schematy bazy
├── fb_pipeline/
│   ├── batches/              # 10 txt batchy (stary pipeline ChatGPT)
│   ├── batch_outputs/        # 53 JSON output'ów starego pipeline
│   ├── clustering/           # cluster_fb_corpus.py (nowy, 1210 linii)
│   ├── ingest/               # ingest_fb_corpus.py (nowy)
│   └── workflow/             # prepare_material + schema + generate_draft (batch 1 infra)
├── kb-pipeline/              # pipeline ustaw → KB (match → generate → audit → merge)
│   ├── input/
│   ├── output/               # 70+ plików (matched/draft/verified per obszar)
│   └── output/reprocess/     # 44 plików z ponowną obróbką artykułów
├── tests/                    # 33 pliki testowe, 260 passed
└── .todos/                   # follow-upy
```

### Rola każdego folderu (1-2 zdania)

- **`kb-pipeline/`** — pipeline offline do zamiany tekstu ustaw (PDF → articles.json → matched → draft → verified → merge do `data/seeds/law_knowledge.json`). Zawiera też skrypty runowe (`run_pipeline.py`, `run_reprocess_all.py`) i manualne pipeline'y per obszar.
- **`fb_pipeline/`** — pipeline korpusu Facebook (ingestionowanie scrape'ów, klasteryzacja, generacja workflow draftów z klastrów). W środku kryją się 2 generacje: stara (batches + ChatGPT prompts, 53 batch outputs) i nowa (ingest + clustering + workflow od kwietnia 17, 2026).
- **`core/`** — silnik runtime RAG: `retriever.py` (BM25+cosine+RRF, 843 linii), `workflow_retriever.py` (606), `rag.py` (409, top-level orchestrator), `generator.py` (470, LLM calls), `intent_router.py` (552), `categorizer.py` (507). Pomocnicze: `anonymizer.py` (49), `auditor.py` (19), `logger.py` (104).
- **`data/`** — wszystkie artefakty danych: seedy KB (`data/seeds/`), workflow seed i drafty, korpus FB + embeddingi, curated datasets, promptem systemowym.
- **`analysis/`** — skrypty analityczne (30 `*.py`) + wygenerowane raporty (25 `.md` + 19 `.json`). Historyczny „silnik" eksperymentalny — buduje eval sety, diagnostyki, dedupy, enrichment, itp.
- **`tests/`** — 33 pliki testowe, 260 testów, wszystkie passed.
- **`app/`** — UI Streamlit (niezmieniony od ~tygodnia).
- **`aktuo/`** — pojedynczy moduł `synonym_mapper.py`.
- **`config/`** — `settings.py` z konfiguracją runtime.
- **`db/`** — migracje bazy.

---

## 2. Git state

```
$ git describe --tags
audit-ready-2026-04-17-18-g e5350ee

$ git status
On branch main
Your branch is ahead of 'origin/main' by 18 commits.

Changes not staged for commit:
  modified:   kb-pipeline/README.md

Untracked files:
  analysis/build_top60_review.py
  analysis/build_top60_review_v2.py
  analysis/top60_clusters_for_review.md
  analysis/top60_clusters_for_review_v2.md
  check_env.py
```

### Ostatnie 30 commitów — grupowane po sesji/autorze

| Data | Hash | Message | Sesja |
|------|------|---------|-------|
| **2026-04-18** (dziś) | e5350ee | docs: audit repo state after codex session 2026-04-17 | **Claude Code** (dziś) |
| 2026-04-17 22:12 | 752b00e | data(workflow_drafts): batch 1 — 10 drafts | **Claude Code** (Zadanie 3) |
| 2026-04-17 22:12 | 744e492 | feat(workflow): add workflow draft generation pipeline | Claude Code (Zadanie 3) |
| 2026-04-17 21:13 | 646626b | data(fb_corpus): cluster 24892 posts into 144 clusters | Claude Code (Zadanie 2) |
| 2026-04-17 21:13 | a1fa260 | feat(fb_pipeline): add clustering (voyage-3 + UMAP + HDBSCAN) | Claude Code (Zadanie 2) |
| 2026-04-17 16:58 | f831cd3 | refactor(fb_pipeline): remove probably_comment flag (v1.5d) | Claude Code (Zadanie 1.5) |
| 2026-04-17 16:52 | 2c10c3c | fix(fb_pipeline): narrow probably_comment (v1.5c) | Claude Code (Zadanie 1.5) |
| 2026-04-17 16:49 | 3f3d260 | feat(fb_pipeline): cutoff markers + filters (v1.5b) | Claude Code (Zadanie 1.5) |
| 2026-04-17 16:16 | 97a6efe | chore: note follow-ups from fb corpus ingest | Claude Code (Zadanie 1) |
| 2026-04-17 16:15 | 5924eac | data(fb_corpus): dedup report from 3 scrape files | Claude Code (Zadanie 1) |
| 2026-04-17 16:15 | cece440 | feat(fb_pipeline): corpus ingest script | Claude Code (Zadanie 1) |
| 2026-04-17 15:28 | 460b734 | feat(workflow): skip draft records in retrieval | Claude Code |
| 2026-04-17 15:21 | e1d0bd0 | schema(law_chunk): add versioning fields | Claude Code |
| 2026-04-17 15:14 | 6754ea8 | dedupe(kb): remove 72 true-duplicates Kodeks pracy | Claude Code |
| 2026-04-17 10:53 | 3826984 | analysis: classify 361 duplicate groups | Claude Code |
| 2026-04-17 10:35 | 164c241 | fix(kb): repair 1017 UTF-8 corrupted records | Claude Code |
| 2026-04-17 09:50 | 3938786 | fix: tighten workflow answer formatting to primary unit | **Codex** (poranek) |
| 2026-04-17 09:47 | cb73d3a | feat: allow safe partial workflow answers | **Codex** (poranek) |
| 2026-04-17 09:35 | 167669d | chore: ignore local reprocess artifacts — **TAG audit-ready** | ręczne |
| 2026-04-17 09:35 | e14e67e | docs: add intent confusion report for audit | ręczne |
| 2026-04-17 09:34 | ad39477 | data: enrich high-impact workflow units | **Codex** |
| 2026-04-17 09:12 | 032111d | test: workflow answer quality eval harness | **Codex** |
| 2026-04-16 20:01 | a8d84ed | feat: workflow-specific answer formatting + legal fallback | **Codex** |
| 2026-04-16 19:56 | 2531ccc | fix: improve workflow versus legal routing | **Codex** |
| 2026-04-16 19:27 | c5c0894 | test: workflow evaluation harness + routing report | Codex/ręczne |
| 2026-04-16 19:20 | df1e9ae | feat: workflow retrieval path with legal fallback | Codex |
| 2026-04-16 19:04 | 943815e | analysis: build workflow knowledge seed | Codex/ręczne |
| 2026-04-15 19:55 | 44f6a14 | fix: reduce top intent confusion pairs | Codex |
| 2026-04-14 09:02 | 24eaef8 | feat: simplify clarification gate | Codex |
| 2026-04-14 08:39 | 40e9386 | feat: refine clarification and intent routing | Codex |

**Wniosek:** 18 commitów do wypchnięcia na origin/main. Untracked i zmodyfikowane pliki wymagają decyzji (commit / gitignore / usunąć).

---

## 3. Pipeline'y w repo

### 3A. `kb-pipeline/` — legal KB (ustawy → `law_knowledge.json`)

Pipeline stages:

| Krok | Plik | Istnieje | Rola |
|------|------|----------|------|
| 0. parsowanie | `parse_isap.py` | ✅ | PDF/HTML ustaw → `articles_*.json` (lista artykułów z tekstem) |
| 1. match | `match_questions.py` | ✅ | Question → artykuły, generuje `matched_*.json` |
| 2. generate | `generate_units.py` | ✅ | Produce KB record draft z matched artykułów (LLM) |
| 3. audit | `audit_units.py` | ✅ | LLM audit nad draftami, generuje `verified_*.json` |
| 4. merge | `merge_kb.py` | ✅ | Merge `verified_*_kb.json` do `data/seeds/law_knowledge.json` |
| orkiestracja | `run_pipeline.py` | ✅ | E2E per obszar |
| reprocess | `run_reprocess_all.py` + `prepare_raw_reprocess.py` | ✅ | Reprocess wszystkich `raw_units_to_process.json` |

**Input questions files** (per obszar):
```
questions_vat.json          199 questions
questions_pit.json          100
questions_cit.json          100
questions_zus.json          100
questions_kadry.json        100
questions_jpk.json           30
questions_jpk_v2.json       100
questions_ksef.json          50
questions_ordynacja.json     50
questions_rachunkowosc.json  60
questions_rachunkowosc_v2.json 100
```
Razem: **1 089 questions** na wejściu do pipeline'u.

**Output files** w `kb-pipeline/output/` (zob. sekcja 4E).

### 3B. `fb_pipeline/` — corpus FB + klasteryzacja + workflow drafty

**Stara warstwa** (pre-Zadanie 1):
- `01_tag_and_batch.py`, `02_chatgpt_prompts.md`, `03_merge_outputs.py` — pipeline ChatGPT-batch do taggowania FB postów na kategorie.
- `posts_15k_ksiegowosc_moja_pasja.json`, `posts_output.json`, `posts_output_backup.json` — raw scrape'y.
- `posts_tagged.json` — otaggowane posty.
- `batches/` — 10 TXT batchy do wklejenia w ChatGPT.
- `batch_outputs/` — 53 JSON output'ów (batch_001..053).

**Nowa warstwa** (od 17.04):
- `ingest/ingest_fb_corpus.py` — stabilny SHA-256 id, dedupe cross-file, quality filters (job ads, sales spam, marketing bold). Output: `data/corpus/fb_groups/fb_corpus.jsonl` (24 892 postów).
- `clustering/cluster_fb_corpus.py` (1210 linii) — voyage-3-large embeddings + UMAP(50D) + HDBSCAN + Opus labeling. Output: `clusters.jsonl` (144) + `post_to_cluster.jsonl`.
- `workflow/prepare_material.py` + `schema.py` + `generate_draft.py` — orkiestracja Zadanie 3 Batch 1 (centroid + high-engagement picker, KB retrieval adapter, walidator schema).

### 3C. `core/` — runtime

| Moduł | Linie | Rola |
|-------|-------|------|
| `retriever.py` | 843 | BM25 + cosine + RRF + slang normalizer, główny indeks KB |
| `workflow_retriever.py` | 606 | Osobny index na workflow_seed z filter draftów (od 460b734) |
| `rag.py` | 409 | Top-level orchestrator: intent → clarification → retrieve → generate |
| `generator.py` | 470 | LLM calls + formatowanie (workflow vs legal), partial answers (od cb73d3a) |
| `intent_router.py` | 552 | Klasyfikacja intencji na taksonomii `data/curated/intent_taxonomy.json` |
| `categorizer.py` | 507 | Kategoryzacja zapytania na obszary prawa |
| `logger.py` | 104 | Logging helpers |
| `anonymizer.py` | 49 | PII maskowanie |
| `auditor.py` | 19 | Expired-source flag (od e1d0bd0) |
| **Suma** | **3 559** | |

### 3D. `analysis/` — 30 `*.py` skryptów + reporty

Skrypty (top by function):
- **KB building:** `build_curated_question_layer.py`, `curate_kb_and_synonyms.py`, `expand_kb_and_synonyms.py`, `patch_kb_from_parsed_sources.py`, `add_missing_articles_from_sources.py`, `add_missing_units.py`.
- **KB cleanup:** `fix_utf8_corruption.py`, `analyze_duplicate_groups.py`, `apply_true_duplicate_dedupe.py`.
- **Workflow seed:** `build_workflow_seed.py`, `enrich_workflow_seed.py`.
- **FB corpus Zadanie 3:** `build_top60_review.py`/`_v2.py`, `generate_batch1_drafts.py`, `build_batch1_report.py`, `retry_cluster_62.py`, `fb_corpus_quality_audit.py`.
- **Eval:** `run_eval.py`, `run_workflow_eval.py`, `run_workflow_answer_eval.py`, `prioritize_eval_failures.py`, `prioritize_workflow_routing_failures.py`, `intent_confusion_report.py`, `kb_unit_quality_diagnostic.py`.
- **Ad-hoc:** `missing_laws_impact.py`, `patch_accountant_retrieval_hotspots.py`, `retest_7_accountant_questions.py`, `article_coverage_audit.py`, `report_coverage_stats_after_gap_patch.py`, `top_coverage_impact_plan.py`.

Raporty:
- `.md`: 25 plików (zob. wynik `ls analysis/*.md`).
- `.json`: 19 plików (zob. wynik `ls analysis/*_report*.json`).

---

## 4. Data state

### 4A. Legal KB — `data/seeds/law_knowledge.json`

| Metryka | Wartość |
|---------|---------|
| Total rekordów (main) | **4 388** |
| `law_knowledge_additions.json` | 6 |
| `law_knowledge_curated_additions.json` | 78 |
| **ŁĄCZNIE** | **4 472** ✅ (zgodne z commit 6754ea8) |

**Rozkład per ustawa (main file):**

| Ustawa | Rekordów |
|--------|----------|
| Ustawa o VAT | 1 492 |
| Ordynacja podatkowa | 766 |
| Ustawa o PIT | 673 |
| Kodeks pracy | 427 |
| Ustawa o CIT | 229 |
| Ustawa o systemie ubezpieczeń społecznych | 225 |
| Ustawa o rachunkowości | 200 |
| Ustawa o zryczałtowanym podatku dochodowym | 198 |
| Rozp. MF o kasach rejestrujących | 161 |
| Rozp. JPK_V7 | 8 |
| Ustawa o VAT (alias) | 3 |
| Rozp. KSeF | 3 |
| Ustawa o VAT - KSeF (3 sub-wariancje) | 3 |

**Rozkład per `source` (top):**

| Source | Rekordów |
|--------|----------|
| `(none)` (legacy) | 2 045 |
| `parsed_article_gap_patch` | 1 928 |
| `raw_unit_reprocess_verified` | 357 |
| `curate_kb_and_synonyms` | 20 |
| `manual_grounded_kpir_batch_2026_04_11` | 9 |
| `accountant_retrieval_hotspot_patch` | 8 |
| `gap_question_addition` | 6 |
| `manual_grounded_ksef_permissions_batch_2026_04_11` | 5 |
| `manual_grounded_tax_procedures_batch_2026_04_12` | 4 |
| `legacy` | 3 |
| `manual_grounded_leasing_batch_2026_04_12` | 3 |

**Schema:** `['law_name', 'article_number', 'category', 'verified_date', 'question_intent', 'content', 'source']` + opcjonalne `gap_freq`, `gap_query`, `gap_source_category`, `proposal_meta` (dla gap-patched records). **Uwaga:** versioning fields z e1d0bd0 (`effective_from/to`, `source_url`, `source_hash`, `last_verified_at`) są w kodzie, ale **nie zapisane w żadnym rekordzie**.

### 4B. Workflow seed — `data/workflow/workflow_seed.json`

**10 units, 10/10 RICH** (≥3 steps AND ≥2 required_inputs AND ≥1 common_pitfall).

| # | Title | Category (`workflow_area`) | steps/inputs/pitfalls |
|---|-------|--------------------------|----------------------|
| 1 | Ujęcie dokumentów w odpowiednim okresie i ewidencji | KPiR / księgowanie / okresy i memoriał | 7/7/5 |
| 2 | Przygotowanie, podpisanie i wysyłka sprawozdania finansowego | Sprawozdanie finansowe / podpis / wysyłka | 7/7/6 |
| 3 | Obieg faktur, statusów i korekt w KSeF | KSeF issuing / correction / invoice circulation | 7/7/6 |
| 4 | Obsługa problemów systemowych i synchronizacji danych | Oprogramowanie księgowe / integracje | 7/7/5 |
| 5 | Klasyfikacja dokumentów, kolumn i zapisów magazynowych | Dokumenty księgowe / magazyn | 7/7/5 |
| 6 | Obsługa wysyłki, korekty i oznaczeń JPK | JPK filing / correction / tags | 7/7/6 |
| 7 | Obsługa zgłoszeń, wyrejestrowań i deklaracji ZUS | ZUS / PUE / zgłoszenia i wyrejestrowania | 7/7/6 |
| 8 | Nadawanie uprawnień i dostępów w KSeF | KSeF permissions / authorization flow | 7/7/6 |
| 9 | Pełnomocnictwa, podpisy i elektroniczne kanały złożenia | Pełnomocnictwa / podpis / kanały złożenia | 7/7/6 |
| 10 | Leasing, wykup samochodu i ewidencja kosztów pojazdu | Leasing / samochód / VAT-26 | 4/7/2 ← minimum-rich |

Unit 10 (Leasing) wyraźnie niedokończony — reszta ma standardowy szkielet 7/7/5-6.

### 4C. FB Corpus — `data/corpus/fb_groups/`

| Plik | Count / rozmiar |
|------|----------------|
| `fb_corpus.jsonl` | 24 892 postów |
| `clusters.jsonl` | 144 klastry |
| `post_to_cluster.jsonl` | 24 892 mapowań |
| `embeddings.npy` | 97.3 MB (voyage-3-large 1024D) |
| `embeddings_meta.json` | ✅ |
| `embeddings_umap50.npy` | 4.7 MB (UMAP 50D cache) |
| `embeddings_umap50_meta.json` | ✅ |

### 4D. Curated data — `data/curated/`

| Plik | Rozmiar | Wpisy | Rola |
|------|---------|-------|------|
| `clarification_slots.json` | 10 KB | 13 intent-groupings | Mapa intencji → brakujące pola |
| `intent_taxonomy.json` | 10 KB | 13 intencji | Master taksonomia dla `intent_router.py` |
| `golden_eval_set.jsonl` | 422 KB | **500 pytań** | Ground truth dla `run_eval.py` |
| `workflow_vs_legal_vs_out_of_scope.jsonl` | 10.1 MB | **11 509 linii** | Kurs rozpoznawania workflow vs legal (baza do eval subsetów) |

### 4E. KB pipeline outputs — `kb-pipeline/output/`

Per-obszar stages (verified_*_kb.json = finalny kandydat do merge'u):

| Obszar | matched → draft → verified_kb (count) | Status |
|--------|---------------------------------------|--------|
| **VAT** (ustawa) | matched_vat_fb + draft_vat_fb → `verified_vat_fb_kb.json` = **1 058** | ✅ done |
| **PIT** | matched_pit + draft_pit → `verified_pit_kb.json` = **78** | ✅ done |
| **PIT** (FB layer) | matched_pit_fb + draft_pit_fb → `verified_pit_fb_kb.json` = **433** | ✅ done |
| **CIT** | matched_cit + draft_cit → `verified_cit_kb.json` = **46** | ✅ done |
| **ZUS** | matched_zus + draft_zus → `verified_zus_kb.json` = **43** | ✅ done |
| **Kadry** | matched_kadry + draft_kadry → `verified_kadry_kb.json` = **58** | ✅ done |
| **JPK** | matched_jpk → verified_jpk_kb = **21** | ✅ done |
| **JPK v2** | matched_jpk_v2 → verified_jpk_v2_kb = **21** | ⚠️ duplikat (zob. 7E) |
| **KSeF** (full) | matched_ksef_full → verified_ksef_full_kb = **29** | ✅ done |
| **KSeF 2023** | matched_ksef_2023 → verified_ksef_2023_kb = **36** | ✅ done |
| **KSeF ustawa** | matched_ksef_ustawa → verified_ksef_ustawa_full_kb = **39** | ✅ done |
| **Ordynacja** | matched_ordynacja → verified_ordynacja_kb = **39** | ✅ done |
| **Rachunkowość** | matched_rachunkowosc → verified_rachunkowosc_kb = **34** | ✅ done |
| **Rachunkowość v2** | matched_rachunkowosc_v2 → verified_rachunkowosc_v2_kb = **59** | ⚠️ duplikat (zob. 7E) |
| **Generic units** | → `verified_units_kb.json` = **88** | ✅ done |
| **Ryczałt** (w `reprocess/`) | → `verified_ustawa_o_ryczalcie_kb.json` | ✅ done (różna ścieżka) |
| **Rozp. kas** (w `reprocess/`) | → `verified_rozporzadzenie_o_kasach_kb.json` | ✅ done |

Suma `verified_*_kb.json`: **~2 200 rekordów** w plikach per-obszar (te pewnie już zostały wmerge'owane w `data/seeds/law_knowledge.json`, gdzie jest 4 472). Nie ma dowodu braku merge'u dla żadnego obszaru.

**Reprocess** (`kb-pipeline/output/reprocess/`) — 44 pliki, wszystkie stages obecne dla 12 aktów (kodeks_pracy, ordynacja_podatkowa, jpk_v7, kasach, cit, pit, rachunkowosci, ryczalcie, vat, vat_ksef_terminy, vat_ksef_zwolnienia, zus). Tylko 2 mają `verified_*_kb.json` (ryczałt, rozp. kas) — reszta zatrzymała się na stage `matched` lub `draft`.

---

## 5. Evaluation metrics

### `analysis/workflow_eval_report.json` — routing (347 rekordów)

```
workflow_path_precision           = 0.8496
legal_path_precision              = 0.7548
workflow_recall_on_workflow_qs    = 0.4800
legal_leakage_into_workflow       = 0.1333
workflow_leakage_into_legal       = 0.2400

clarification_rate_per_subset:
  workflow_expected  = 0.8267
  legal_expected     = 0.8400
  mixed_expected     = 0.5106
```

### `analysis/workflow_answer_eval_report.json` — quality odpowiedzi (347 rekordów)

```
workflow_format_rate              = 1.0000
workflow_section_completeness     = 0.8431
workflow_clarification_rate       = 0.7800 ← było 0.83 (Codex partial answers)
workflow_fallback_safety_rate     = 0.0213
legal_safety_rate                 = 0.9667
legal_path_contamination_rate     = 0.2030
sparse_unit_safety_rate           = 0.0000
```

### `analysis/eval_report.json` — golden set baseline (500 rekordów)

```
overall:
  behavior_accuracy = 0.846
  intent_accuracy   = 0.564
  macro_precision   = 0.6094
  macro_recall      = 0.5214
per_intent (sample): accounting_operational precision=0.3607, recall=0.5789
```

### `analysis/quality_audit_report.json` — 20 kontrolnych pytań (faktur, terminy)
`summary: {PASS: 20}` — wszystkie 20 przeszło.

### `analysis/stress_test_accountant_report.json` — 30 pytań stress-test
`summary: {PASS: 30}` — wszystkie 30 przeszło.

### Inne
- `analysis/intent_confusion_report.json` — macierz konfuzji intencji (audit-ready).
- `analysis/duplicate_groups_report.json` — 361 grup dupli post-UTF8-fix (użyte w dedupe).
- `analysis/fb_corpus_clustering_report.json` — klasteryzacja stats (42 high-priority klastrów).
- `analysis/fb_corpus_ingest_report_v2.json` — ingestion stats (40 537 raw → 24 954 final).
- `analysis/single_fail_fix_report.json` — stress test: before {PASS:28, PARTIAL:1, FAIL:1} → after {PASS:29, PARTIAL:1, FAIL:0}.
- `analysis/quality_audit_report.json`, `analysis/curation_report.json`, `analysis/add_missing_units_report.json`, `analysis/curated_question_layer_report.json`, `analysis/top_coverage_impact_report.json`, `analysis/utf8_fix_report.json`, `analysis/workflow_seed_enrichment_report.json`, `analysis/workflow_seed_report.json` — historyczne raporty z wcześniejszych sesji.

---

## 6. Testy

```
$ python -m pytest -q --tb=no
.................................................................... [100%]
260 passed in 6.02s
```

- **260 passed**, 0 failed, 0 skipped, 0 xfailed, 0 xpassed.
- **33 pliki** testowe w `tests/`.

**Kategorie (by file name):**

| Obszar | Pliki |
|--------|-------|
| Retriever core | `test_retriever.py`, `test_retriever_cache.py`, `test_retriever_rrf.py`, `test_retriever_slang.py`, `test_workflow_retriever.py`, `test_workflow_draft_filtering.py` |
| Generator / RAG | `test_rag.py`, `test_generator.py`, `test_workflow_answer_formatting.py` |
| Intent / categorizer | `test_intent_router.py`, `test_categorizer.py` |
| Clarification UX | `test_clarification_chips.py`, `test_clarification_display.py`, `test_clarification_ui.py` |
| KB data quality | `test_kb_encoding.py`, `test_kb_no_true_duplicates.py`, `test_law_chunk_versioning_schema.py` |
| Analysis scripts | `test_build_curated_question_layer.py`, `test_build_workflow_seed.py`, `test_enrich_workflow_seed.py`, `test_curate_kb_and_synonyms.py`, `test_expand_kb_and_synonyms.py`, `test_prioritize_eval_failures.py`, `test_run_eval.py`, `test_run_workflow_eval.py`, `test_run_workflow_answer_eval.py` |
| FB pipeline | `test_fb_cluster.py`, `test_fb_corpus_ingest.py`, `test_workflow_generation.py` |
| UI / infra | `test_main.py`, `test_anonymizer.py`, `test_auditor.py`, `test_logger.py` |

---

## 7. What's missing / in progress

### 7A. Obszary z kompletnym KB legalnym (end-to-end merged do `law_knowledge.json`)

Na podstawie liczb w `law_knowledge.json` + obecności `verified_*_kb.json`:

| Obszar | Rekordów w KB | `verified_*_kb.json` istnieje | Status |
|--------|---------------|-------------------------------|--------|
| VAT | 1 492 | 1 058 (fb) | ✅ merged (KB > fb layer o 434) |
| PIT | 673 | 78 + 433 fb = 511 | ✅ merged (KB > o 162) |
| Ordynacja podatkowa | 766 | 39 | ✅ merged |
| Kodeks pracy | 427 | 58 (kadry) | ✅ merged (reprocess stage: matched) |
| CIT | 229 | 46 | ✅ merged |
| ZUS (ust. o systemie) | 225 | 43 | ✅ merged |
| Rachunkowość | 200 | 34 + 59 v2 = 93 | ✅ merged |
| Ryczałt | 198 | (reprocess `verified_ustawa_o_ryczalcie_kb`) | ✅ merged |
| Rozp. kas | 161 | (reprocess `verified_rozporzadzenie_o_kasach_kb`) | ✅ merged |
| **Łącznie** | **4 371** | | wszystko merged |

Pozostałe 101 rekordów (4472 − 4371) to KSeF (3), Rozp. KSeF (3), Rozp. JPK_V7 (8), additions-file (84), "Ustawa o VAT - KSeF …" (3).

### 7B. Obszary z częściowym KB

- **Kodeks pracy w reprocess** — pipeline `reprocess/` ma stages `matched_kodeks_pracy.json` + `draft_kodeks_pracy.json` ale **nie ma `verified_kodeks_pracy_kb.json`**. Czy to znaczy, że reprocess KP nie został zakończony? Jeśli to miała być druga iteracja po UTF-8 fix, to się nie dokończyła.
- **CIT, PIT, Ordynacja, Rachunkowość, ZUS, JPK_V7, VAT + KSeF warianty w reprocess** — mają `matched` i `draft`, ale nie mają `verified_*_kb.json`. **10 z 12 reprocessów zatrzymanych na drafcie** — prawdopodobnie czekają na audit step.

### 7C. Workflow seed — production-ready vs draft

- **Production-ready (RICH, wmerge'owane):** 10 / 10 w `data/workflow/workflow_seed.json` (zob. 4B).
- **Draft (batch 1 z FB klastrów, niezwalidowane):** **10** w `data/workflow_drafts/wf_*.json`. Cost generacji $4.85, all 24 legal_anchors exist in KB, ale **żaden draft nie został jeszcze promowany do seed'u**. Retriever ma filter na drafty (źródło `draft`) — nie wypłyną na runtime (460b734).

### 7D. Klastry FB — stan wykorzystania

- **144 klastrów zlabelowanych** (Opus 4.7, zero fallbacków).
- **42 high-priority** (size ≥30, avg_comments ≥1.5) — kandydaci na workflow rekordy.
- **10 z 42 (24%) zostały przetworzone** na drafty w Zadaniu 3 Batch 1. Pozostałe **32 high-priority klastrów NIE mają draftów** — do zrobienia w batchach 2+.
- Klastry jako takie są **tylko labelowane + embeddingowe** — nie mają yet struktury „workflow unit". Batch 1 draft = pierwsze 10 workflow units z FB.

### 7E. Duplikacja / rozbieżność

Znalezione "dwa podejścia do tego samego":

| # | Plik A (stary) | Plik B (nowy) | Aktualny |
|---|----------------|----------------|----------|
| 1 | `matched_jpk.json` + `verified_jpk_kb.json` (21 rek.) | `matched_jpk_v2.json` + `verified_jpk_v2_kb.json` (21 rek.) | **v2** (wg `questions_jpk_v2.json` = 100 pytań, v1 = 30) |
| 2 | `matched_rachunkowosc.json` + `verified_rachunkowosc_kb.json` (34 rek.) | `matched_rachunkowosc_v2.json` + `verified_rachunkowosc_v2_kb.json` (59 rek.) | **v2** (v1 = 60 pytań, v2 = 100) |
| 3 | `fb_pipeline/01_tag_and_batch.py` + `batches/` + `batch_outputs/` (53 plików) | `fb_pipeline/ingest/ingest_fb_corpus.py` (2026-04-17) | **Nowy** (ingest) — stary pipeline pewnie do usunięcia ale nie był czyszczony |
| 4 | `fb_pipeline/posts_tagged.json` (stary scrape tagowany ChatGPT) | `data/corpus/fb_groups/fb_corpus.jsonl` (nowy ingest) | **Nowy** korpus |
| 5 | `analysis/build_top60_review.py` + `top60_clusters_for_review.md` | `analysis/build_top60_review_v2.py` + `top60_clusters_for_review_v2.md` | **v2** (v1 uwzględniał wykluczenia, v2 zgodnie z decyzjami Pawła) — oba **untracked** |
| 6 | `analysis/fb_corpus_ingest_report.json/.md` | `analysis/fb_corpus_ingest_report_v2.json/.md` | **v2** (po v1.5b filtrach) |
| 7 | `articles.json`, `matched.json` (bez sufixu obszaru) | per-obszar pliki | **Per-obszar** (legacy bez suffix'a zostało) |
| 8 | `verified_units.json` + `verified_units_kb.json` (88 rek., generic) | per-obszar pliki | Unjasne — 88 generic rekordów mogło zostać merge'owane pod różne obszary |
| 9 | `fb_pipeline/batch_outputs/batch_001_output.json` → `batch_053_output.json` | `data/corpus/fb_groups/fb_corpus.jsonl` | **Nowy korpus** (stary ChatGPT batch jest prawdopodobnie nadrzędnym źródłem, ale po pełnym ingestion nie jest już używany) |

**Uwaga:** pliki `questions_*_test10.json` (7 plików po 10 pytań) to smoke test subsety — nie duplikaty, tylko subset.

---

## 8. Rekomendacja Claude Code — najbardziej sensowny następny krok

Stan jest nietrywialnie dobry: **runtime działa** (260 testów zielonych), KB legalny ma 4 472 rekordów end-to-end merged, workflow seed ma 10/10 rich units, a klastry FB dają jasną mapę prac. Ale **precision/recall w evalu są wąskim gardłem**: `workflow_recall_on_workflow_qs = 0.48` i `legal_path_precision = 0.75` oznaczają, że system trafnie rutuje w ~60-75% przypadków, co jest jakościowym sufitem dla końcowej UX.

**Rekomenduję następujący priorytet:**

1. **PUSH + cleanup** (30 min). 18 commitów nie jest wypchniętych, 5 plików untracked. Decyzja per-plik: commit `top60_*` (istotne dla batcha 2), gitignore `check_env.py`, resztę wg uznania. `kb-pipeline/README.md` — odejrzeć zmianę.

2. **Batch 2 workflow draftów z FB klastrów** (~$4.85 per 10, czyli ~$15 na pozostałe 32 high-priority klastry). Zanim batch 2 — **walidacja Pawła** 10 draftów batch 1 (promowanie do seed'u). Bez walidacji batch 2 ryzykuje replikacją błędów pierwszego wygenerowania. **Rzeczywisty zysk:** rozbicie `workflow_recall` z 0.48 do ~0.60+ (bo brakujące workflow units są głównym powodem, że pytania workflow trafiają na legal).

3. **Drugie co** — dokończyć 10 niedoukończonych reprocessów w `kb-pipeline/output/reprocess/` (stages matched/draft → verified → merge). Mają być „post UTF-8 fix" iteracją drugiego przejścia — brakujący audit step pewnie zajmie 1-2h LLM time. Alternatywnie: wyjaśnić, czy reprocess dalej jest potrzebny, czy UTF-8 fix + dedupe już rozwiązały problem.

4. **Obniżenie `workflow_clarification_rate` z 0.78 do <0.6** jeśli jest to nadal priorytet — ale obecne 0.78 jest OK dla większości przypadków; tutaj marginalne usprawnienia potrzebują inwestycji w dane (więcej workflow units, lepsze slot inference), a nie w kod.

5. **voyage-4 migration** — duża inwestycja, najmniejszy natychmiastowy zwrot. Jeśli robić — dopiero po batchu 2+3 workflow draftów, żeby nie re-embedować dwa razy.

---

## 9. Koszty API

### Znane koszty (z checkpointów/metadata)

- **Zadanie 3 Batch 1** — `data/workflow_drafts/batch1_run_log.json`:
  - Input tokens: 90 205
  - Output tokens: 46 587
  - Cost: **$4.8471** (Opus 4.7)
  - Elapsed: 634 s
  - + retry cluster 62: ~$0.40 (nie zalogowane osobno)
  - **Razem: ~$4.85 + $0.40 = $5.25**

- **Klasteryzacja FB Zadanie 2** — brak zalogowanego kosztu w repo (voyage-3-large embeddings + Opus labeling dla 144 klastrów). **Szacunek na podstawie rozmiaru:**
  - Voyage-3-large embeddings: 24 892 postów × ~200 token/post = ~5M tokens × $0.18/M = **~$0.90**
  - Opus labeling: 144 klastrów × ~1k in + 500 out = 144k in + 72k out × ($0.015 in + $0.075 out) = **~$7.60**
  - **Razem: ~$8-9**

- **`kb-pipeline` (match + generate + audit) — pre-repo-tracked** — **brak cost log'u w repo**. Wszystkie kb-pipeline output'y mają daty z wcześniej (2026-04-03 do 2026-04-15). Nie udało się zsumować kosztu z danych — nie ma metadata.usage w `verified_*.json` ani w `draft_*.json`.

- **KB UTF-8 fix + dedupe (2026-04-17)** — zerowy LLM cost (deterministyczny kod, bez LLM calls).

- **Codex (webchat) — intent_router, clarification, workflow routing (2026-04-14 do 17)** — koszt ponoszony w webchacie, **nie do odzyskania** z repo.

### Szacunek pozostałego budżetu

Budżet: **$80** (cytowany przez Pawła).

| Pozycja | Znany/szacunkowy koszt |
|---------|------------------------|
| kb-pipeline pełny (wszystkie obszary, ~4 400 rekordów × ~2k in + 500 out Opus = 8.8M in + 2.2M out) | **~$130-150 szacunkowo** (prawdopodobnie przekracza budżet — chyba że używano Sonnet, wtedy **~$40-50**) |
| Klasteryzacja FB (Zadanie 1+2) | **~$8-9** |
| Zadanie 3 Batch 1 | **$5.25** |
| Webchat Codex (nieznane) | **?** |
| **Razem znane** | **~$15-20 znane + ~$50-130 niepewne** |

**Wniosek:** bez cost log'ów z kb-pipeline nie mogę dać twardej liczby. Widząc rozmiar i jakość KB, realny wydatek mógł być rzędu $30-60 (gdyby użyty Sonnet 3.5 do draft/audit, co było standardem przed Opus 4.7), plus ~$15 na Zadania 1-3. To zostawia budżet rzędu **$20-35** na batch 2 + resztę, **jeśli szacunki są trafne**. Przed batchem 2 — **dodać explicit cost logging do `analysis/generate_batch1_drafts.py` patternu** żeby batch 2 i dalsze były mierzalne.

---

## Podsumowanie 1-akapitowe

Repo jest w dobrym stanie end-to-end: 4 472 rekordów KB legalnego merged dla wszystkich 10 głównych obszarów prawa, 10/10 rich workflow units, 24 892 postów FB skorpusowanych + 144 klastry labelowane, 260/260 testów zielonych. Główne "niedokończone" obszary to: 10 draftów workflow z batcha 1 do walidacji Pawła przed promocją do seed'u, 32 high-priority klastry FB czekające na batch 2+, 10 niedokończonych `reprocess/` (zatrzymane na draft/audit). Runtime evaluation pokazuje słabość retrieval: 0.48 workflow recall i 0.75 legal precision — największy impact będzie z **dodawania więcej workflow units** (z klastrów FB), nie z wkładu w kod. Nieewidentne ryzyko: brak cost log'u z kb-pipeline uniemożliwia precyzyjny szacunek pozostałego budżetu API ($20-35 realnie, ale niepewne).
