# Repo State Audit — 2026-04-18

Audyt stanu repozytorium po sesji Codex + Claude z 2026-04-16 → 2026-04-17 (tag `audit-ready-2026-04-17` + 17 commitów wprzód).

## 1. Current state

### Git log (ostatnie 20 commitów)

```
752b00e  data(workflow_drafts): batch 1 — 10 drafts for Pawel's validation          2026-04-17 22:12
744e492  feat(workflow): add workflow draft generation pipeline                     2026-04-17 22:12
646626b  data(fb_corpus): cluster 24892 posts into 144 thematic clusters            2026-04-17 21:13
a1fa260  feat(fb_pipeline): add clustering pipeline (voyage-3-large+UMAP+HDBSCAN)   2026-04-17 21:13
f831cd3  refactor(fb_pipeline): remove probably_comment flag (v1.5d)                2026-04-17 16:58
2c10c3c  fix(fb_pipeline): narrow probably_comment to explicit patterns (v1.5c)     2026-04-17 16:52
3f3d260  feat(fb_pipeline): fix cutoff markers, expand filters (v1.5b)              2026-04-17 16:49
97a6efe  chore: note follow-ups from fb corpus ingest                               2026-04-17 16:16
5924eac  data(fb_corpus): generate deduplicated corpus report from 3 scrape files   2026-04-17 16:15
cece440  feat(fb_pipeline): add corpus ingest script with dedup and quality filters 2026-04-17 16:15
460b734  feat(workflow): skip draft records in workflow retrieval                   2026-04-17 15:28
e1d0bd0  schema(law_chunk): add versioning fields                                   2026-04-17 15:21
6754ea8  dedupe(kb): remove 72 true-duplicate records from Kodeks pracy             2026-04-17 15:14
3826984  analysis: classify 361 duplicate groups in law_knowledge post-utf8-fix     2026-04-17 10:53
164c241  fix(kb): repair UTF-8 corrupted records in law_knowledge                   2026-04-17 10:35
3938786  fix: tighten workflow answer formatting to primary unit                    2026-04-17 09:50
cb73d3a  feat: allow safe partial workflow answers before full clarification        2026-04-17 09:47
167669d  chore: ignore local reprocess artifacts and shell history  ← audit-ready   2026-04-17 09:35
e14e67e  docs: add intent confusion report for audit                                2026-04-17 09:35
ad39477  data: enrich high-impact workflow units to reduce clarification rate       2026-04-17 09:34
```

### HEAD

- **Hash:** `752b00e0527a99c0a92d55095d402f91fe900e5d`
- **Message:** `data(workflow_drafts): batch 1 — 10 drafts for Pawel's validation`
- **Data:** 2026-04-17 22:12:25 +0200

### Tag

- **Aktualny describe:** `audit-ready-2026-04-17-17-g752b00e` (17 commitów za tagiem)
- **Tag commit:** `167669d chore: ignore local reprocess artifacts and shell history`

### Git status (NIE clean)

```
On branch main
Your branch is ahead of 'origin/main' by 17 commits.

Changes not staged for commit:
  modified:   kb-pipeline/README.md

Untracked files:
  analysis/build_top60_review.py
  analysis/build_top60_review_v2.py
  analysis/top60_clusters_for_review.md
  analysis/top60_clusters_for_review_v2.md
  check_env.py
```

**Uwaga:** 5 plików nieśledzonych + 1 modyfikacja. Artefakty z sesji z 17. kwietnia (build skryptów top60 + check_env). Nie blokuje audytu, ale warto je albo commitnąć, albo dodać do `.gitignore`, albo usunąć przed dalszą pracą. 17 commitów do wypchnięcia na origin/main.

---

## 2. Workflow seed

- **Ścieżka:** `data/workflow/workflow_seed.json`
- **Liczba jednostek:** **10**
- **Wszystkie RICH** (≥3 steps AND ≥2 required_inputs AND ≥1 common_pitfall) — 10/10

| # | id/title | topic_area | steps | inputs | pitfalls | forms | systems | rich? |
|---|----------|-----------|-------|--------|----------|-------|---------|-------|
| 1 | Ujęcie dokumentów w odpowiednim okresie i ewidencji | KPiR / księgowanie / okresy i memoriał | 7 | 7 | 5 | 0 | 5 | ✅ |
| 2 | Przygotowanie, podpisanie i wysyłka sprawozdania finansowego | Sprawozdanie finansowe / podpis / wysyłka | 7 | 7 | 6 | 2 | 4 | ✅ |
| 3 | Obieg faktur, statusów i korekt w KSeF | KSeF issuing / correction / invoice circulation | 7 | 7 | 6 | 1 | 7 | ✅ |
| 4 | Obsługa problemów systemowych i synchronizacji danych | Oprogramowanie księgowe / integracje | 7 | 7 | 5 | 1 | 8 | ✅ |
| 5 | Klasyfikacja dokumentów, kolumn i zapisów magazynowych | Dokumenty księgowe / magazyn / kolumny | 7 | 7 | 5 | 1 | 4 | ✅ |
| 6 | Obsługa wysyłki, korekty i oznaczeń JPK | JPK filing / correction / tags | 7 | 7 | 6 | 3 | 6 | ✅ |
| 7 | Obsługa zgłoszeń, wyrejestrowań i deklaracji ZUS | ZUS / PUE / zgłoszenia i wyrejestrowania | 7 | 7 | 6 | 5 | 3 | ✅ |
| 8 | Nadawanie uprawnień i dostępów w KSeF | KSeF permissions / authorization flow | 7 | 7 | 6 | 3 | 3 | ✅ |
| 9 | Pełnomocnictwa, podpisy i elektroniczne kanały złożenia | Pełnomocnictwa / podpis / kanały złożenia | 7 | 7 | 6 | 3 | 3 | ✅ |
| 10 | Leasing, wykup samochodu i ewidencja kosztów pojazdu | Leasing / samochód / VAT-26 / koszty | 4 | 7 | 2 | 1 | 5 | ✅ |

**Uwaga:** Schemat workflow_seed używa `workflow_area` (nie `topic_area`) + `category` + `user_intent` + `cluster_impact`. Unit 10 (Leasing) jest tu wyraźnie "minimum-rich" (4 kroki, 2 pitfalls) — prawdopodobnie świeżo dodany i niedowzbogacony, w odróżnieniu od 1–9 które mają standardowy szkielet 7/7/5-6.

**Osobny layer:** `data/workflow_drafts/*.json` = 10 **świeżych draftów** z batcha 1 (z klastrów FB), schemat inny (id, question_examples, answer_steps, legal_anchors, edge_cases, common_mistakes, related_questions, requires_manual_legal_anchor, generation_metadata). To **nie są** jednostki z workflow_seed — to kandydaci do walidacji Pawła przed ewentualnym promowaniem do seed.

---

## 3. FB corpus i klastry

| Plik | Istnieje | Rozmiar |
|------|----------|---------|
| `data/corpus/fb_groups/fb_corpus.jsonl` | ✅ | 24 892 postów |
| `data/corpus/fb_groups/clusters.jsonl` | ✅ | 144 klastry |
| `data/corpus/fb_groups/post_to_cluster.jsonl` | ✅ | 24 892 mapowań |
| `data/corpus/fb_groups/embeddings.npy` | ✅ | 1024D voyage-3-large, ~97 MB |
| `data/corpus/fb_groups/embeddings_meta.json` | ✅ | — |
| `data/corpus/fb_groups/embeddings_umap50.npy` | ✅ | 50D UMAP cache, ~4.7 MB |
| `data/corpus/fb_groups/embeddings_umap50_meta.json` | ✅ | — |

Cache embeddingów + UMAP siedzi lokalnie (ignorowane w git per `.gitignore`). Re-clustering z innymi parametrami HDBSCAN jest "free" — nie trzeba odpytywać Voyage ponownie.

---

## 4. Eval metrics (latest)

### `analysis/workflow_eval_report.json` (routing workflow vs legal, 347 rekordów)

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

Subset: 150 workflow + 150 legal + 47 mixed.

### `analysis/workflow_answer_eval_report.json` (jakość odpowiedzi, 347 rekordów)

```
workflow_format_rate              = 1.0000
workflow_section_completeness     = 0.8431
workflow_clarification_rate       = 0.7800  ← było 0.83
workflow_fallback_safety_rate     = 0.0213
legal_safety_rate                 = 0.9667
legal_path_contamination_rate     = 0.2030
sparse_unit_safety_rate           = 0.0000
```

Subset: 150 workflow_answer + 150 legal_answer + 47 legal_fallback.

### Inne reporty w `analysis/`

- `intent_confusion_report.json/.md` (e14e67e)
- `fb_corpus_clustering_report.json/.md` (646626b)
- `fb_corpus_ingest_report_v2.json/.md` (5924eac)
- `duplicate_groups_report.json/.md` (3826984) — 361 grup
- `dedupe_true_duplicate_plan.json` + `dedupe_true_duplicate_applied.json` (6754ea8)
- `zadanie3_batch1_report.md` + `batch1_run_log.json` (752b00e)

---

## 5. KB Aktuo

### Law knowledge records

| Plik | Count |
|------|-------|
| `data/seeds/law_knowledge.json` | **4 388** |
| `data/seeds/law_knowledge_additions.json` | 6 |
| `data/seeds/law_knowledge_curated_additions.json` | 78 |
| **SUMA** | **4 472** ✅ |

Oczekiwana wartość **4472 zgodnie z commitem dedupe (6754ea8)**. Dopasowanie idealne. Jednostkowy plik `law_knowledge.json` ma 4388, a różnica 84 to sumy pozostałych dwóch plików — baseline 4472 liczy się po złożeniu wszystkich trzech.

### Schema

Obecny schema głównego pliku (klucze widoczne w rekordach):
```
['law_name', 'article_number', 'category', 'verified_date',
 'question_intent', 'content', 'source',
 'gap_freq', 'gap_query', 'gap_source_category', 'proposal_meta']
```

**Pola versioning dodane w commicie e1d0bd0** (`effective_from`, `effective_to`, `source_url`, `source_hash`, `last_verified_at`):
- ✅ Obecne w kodzie jako opcjonalne LawChunk fields z defaultami pustego stringa (`core/retriever.py`, `core/workflow_retriever.py`, `core/rag.py`, `core/auditor.py`).
- ❌ **NIE zapisane do danych** — żaden z 4388 rekordów nie ma tych pól w JSON. Schema jest więc rozszerzona prospektywnie (backward-compat: pola traktowane jako puste przy deserializacji).

---

## 6. Testy

```
python -m pytest -q
260 passed in 15.81s
```

- **260 passed** — zero failed, zero skipped, zero xfailed, zero xpassed.
- Baseline przed tagiem audit-ready: 241 (brief Zadania 3 cytuje tę liczbę).
- Delta +19 testów od tagu (głównie: +6 test_fb_cluster, +13 test_workflow_generation oraz dodatki z cb73d3a: test_rag +26/-0 linii, test_run_workflow_answer_eval +59, test_workflow_answer_formatting +85 linii).

---

## 7. Co się działo od audit-ready (17 commitów)

> Klasyfikacja orientacyjna: Codex = praca z sesji webchat Pawła z 16-17 kwietnia. Claude Code = praca lokalna (dzisiaj, wszystkie commity z Co-Authored-By). Autor gitowy wszędzie jest `Pawel Tokarski` — klasyfikacja na podstawie daty/treści/trailera.

### A. Codex — partial workflow answers (2 commity, 17.04 poranek)

**`cb73d3a` — feat: allow safe partial workflow answers before full clarification** (09:47)
- Zmodyfikowane: `config/settings.py` (+20), `core/generator.py` (+63), `core/rag.py` (+157), `tests/test_rag.py` (+26), `tests/test_workflow_answer_formatting.py` (+85), `tests/test_run_workflow_answer_eval.py` (+59), eval report +903 linii.
- Sens: pozwolić zwracać bezpieczną częściową odpowiedź workflow zanim wszystkie slots będą wypełnione (zamiast twardego "potrzebuję doprecyzowania"). Próg bezpieczeństwa ustawiany w settings.

**`3938786` — fix: tighten workflow answer formatting to primary unit** (09:50)
- `core/generator.py` (+12), eval report +74 linii.
- Dokrętka: generator miał mieszać sekcje z wielu workflow units — teraz tylko primary unit.

### B. Claude Code — KB cleanup (3 commity, 17.04 rano)

**`164c241` — fix(kb): repair UTF-8 corrupted records in law_knowledge** (10:35)
- Naprawa 1017 rekordów z zepsutym UTF-8 (564 w PIT, 103 w Kodeksie pracy, reszta rozproszona). Backup `.backup_pre_utf8_fix` w 3 plikach.

**`3826984` — analysis: classify 361 duplicate groups** (10:53)
- Skrypt klasyfikacji + raport. 25 450 insertions — ogromny raport JSON/MD z kategoryzacją dupli (true vs curated variants).

**`6754ea8` — dedupe(kb): remove 72 true-duplicate records from Kodeks pracy triple-ingest pattern** (15:14)
- Aplikacja wyników 3826984. Zdjęto 72 true-duplikaty (0 priority_1_verified, 58 priority_2_curated, 2 tiebreak_lowest_index + 12 innych kategorii). Nowy total KB: 4 472.

### C. Claude Code — schema + workflow draft filtering (2 commity, 17.04 popołudnie)

**`e1d0bd0` — schema(law_chunk): add versioning fields** (15:21)
- Dodano opcjonalne pola `effective_from/effective_to/source_url/source_hash/last_verified_at` do LawChunk w `core/retriever.py`, `core/rag.py`, `core/workflow_retriever.py`. Auditor zyskał flagę expired-source. Testy regresyjne.

**`460b734` — feat(workflow): skip draft records in workflow retrieval** (15:28)
- `core/workflow_retriever.py` (+2/-1), `tests/test_workflow_draft_filtering.py` (+50). Drafty (source_type zawierający `draft`) są odfiltrowywane z retrieval — żeby nieuwierzytelnione batch1 drafty nie wypływały do odpowiedzi na produkcji.

### D. Claude Code — FB corpus ingest (4 commity, 17.04 popołudnie)

**`cece440` — feat(fb_pipeline): add corpus ingest script with dedup and quality filters** (16:15)
- `fb_pipeline/ingest/ingest_fb_corpus.py` — stabilne 12-char SHA-256 id, normalizacja polskich znaków, cross-file dedupe po newest scraped_at.

**`5924eac` — data(fb_corpus): generate deduplicated corpus report from 3 scrape files** (16:15)
- Report na 3 scrape'ach: 40 537 raw → 28 858 unique → 24 954 final. Backup scrape pokrywał ~96% nowych.

**`97a6efe` — chore: note follow-ups from fb corpus ingest** (16:16)
- `.todos/fb_corpus_followups.md` — 4 obserwacje (README drift, posts_tagged.json, "Wyświetl więcej" w top keywords, komentarze jako posty).

**`3f3d260` / `2c10c3c` / `f831cd3` — iteracje v1.5b→c→d** (16:49 / 16:52 / 16:58)
- v1.5b: strip scraper cutoff markers ("Wyswietl wiecej"), expand JOB_AD_PREFIXES 9→17, add SALES_SPAM + MARKETING_BOLD filters, add probably_comment flag.
- v1.5c: zawężenie probably_comment — usunięto Rule 2 (lowercase opener, 60%+ FP), zostały 25 explicit regexes. 557→91 flagów.
- v1.5d: **usunięcie** flagi probably_comment w ogóle — decyzja strategiczna: klasteryzacja naturalnie rozwarstwi komentarze od postów. Po 3 iteracjach FP rate ciągle 40-60%.

### E. Claude Code — klasteryzacja (2 commity, 17.04 wieczór)

**`a1fa260` — feat(fb_pipeline): add clustering pipeline (voyage-3-large + UMAP + HDBSCAN + Opus labeling)** (21:13)
- `fb_pipeline/clustering/cluster_fb_corpus.py` (+1210), `tests/test_fb_cluster.py` (+271). Pipeline: embeddings via voyage-3-large (1024D), redukcja UMAP (50D, n_neighbors=15, cosine, seed=42), HDBSCAN sklearn (min_cluster=35, min_samples=10, euclidean, eom), labelowanie Opus 4.7 per klaster. Cache'uje obie wersje embeddingów na dysku.

**`646626b` — data(fb_corpus): cluster 24892 posts into 144 thematic clusters** (21:13)
- Raport: 144 klastrów, 17 002 przypisanych, 7 897 noise (31.7% — plateau). Avg size 118, 42 high-priority. Topic coverage: kadry 55, ZUS 20, PIT 15, VAT 12, inne 10, KSeF 9, rach. 5, software 5, JPK 5, KPiR 4, CIT 4. Zero fallbacków w labelowaniu.

### F. Claude Code — Zadanie 3 Batch 1 (2 commity, 17.04 późny wieczór)

**`744e492` — feat(workflow): add workflow draft generation pipeline** (22:12)
- `fb_pipeline/workflow/prepare_material.py` + `schema.py` + `generate_draft.py`, `analysis/generate_batch1_drafts.py` + `retry_cluster_62.py` + `build_batch1_report.py`, `tests/test_workflow_generation.py` (+1956 linii razem). Centroid + high-engagement picker, walidator JSON, runner z BATCH1_RESUME=1.

**`752b00e` — data(workflow_drafts): batch 1 — 10 drafts for Pawel's validation** (22:12)
- 10 draftów `wf_{cluster_id}_{slug}.json` + `batch1_drafts.jsonl` + `batch1_run_log.json` + `zadanie3_batch1_report.md` (381 linii). Koszt $4.85, 24/24 legal_anchors verified, 2 flags `requires_manual_legal_anchor=true`.

---

## 8. Differences vs plan (Pawel + Claude webchat)

| Plan | Status | Evidence |
|------|--------|----------|
| **Zadanie 3 batch 1:** wygenerować 10 workflow rekordów z klastrów FB przez Opus | ✅ **DONE** | commits 744e492 + 752b00e (22:12, 17.04). 10/10 schema-valid, $4.85, raport `analysis/zadanie3_batch1_report.md`, 24/24 anchors w KB |
| **Blok 2 (clarification rate fix):** było 83% | ⚠️ **CZĘŚCIOWO** | Codex commits cb73d3a+3938786 obniżyły `workflow_clarification_rate` z 0.83 → **0.78** (raport `workflow_answer_eval_report.json`). Poprawa 5 pp. — nie jest to "fix" tylko iteracja. Warto sprawdzić czy dociąć dalej. |
| **Blok 2 (embeddingi produkcyjne voyage-4):** | ❌ **NIE ZROBIONE** | Obecnie klastry używają **voyage-3-large** (a1fa260). Nie ma voyage-4 w repo. `fb_corpus` embeddings wymagałyby re-embedu; retriever `core/retriever.py` używa swojej ścieżki i niezależnie od fb_corpus. |

### Dodatkowe osiągnięcia Codex/Claude poza planem

- Codex: partial answers (cb73d3a) + tighten formatting (3938786).
- Claude: KB dedupe + UTF-8 fix (164c241, 3826984, 6754ea8) — -72 prawdziwych dupli, -1017 UTF-8.
- Claude: LawChunk versioning schema prospektywnie (e1d0bd0) — gotowe pod zewnętrzne źródła.
- Claude: draft filtering in workflow retrieval (460b734) — bezpieczeństwo przed wypłynięciem nieuwierzytelnionych draftów.
- Claude: FB corpus ingest + klasteryzacja (cece440→646626b) — 24 892 postów → 144 klastry, fundament pod Zadanie 3.

### Co dalej (rekomendacja z audytu)

1. **Decyzja o 5 nieśledzonych plikach** (`build_top60_review.py`, `build_top60_review_v2.py`, `top60_clusters_*.md`, `check_env.py`) + modyfikacji `kb-pipeline/README.md`: commit / gitignore / remove.
2. **Walidacja 10 draftów batch 1** przez Pawła (ręczny review + decyzja co promować do `workflow_seed.json`).
3. **Dalsze zbicie clarification rate** (0.78 → <0.60) — jeśli to nadal top priority Bloku 2. Obecne dane: `analysis/workflow_answer_eval_report.json` zawiera 347 rekordów z diagnozą, w tym sekcje `top_weak_workflow_answers` i `workflow_units_to_enrich_first`.
4. **voyage-4 migration** — osobne zadanie, osobny koszt. Pytanie: czy migrować cały pipeline retrievera (legal+workflow KB) czy tylko FB corpus (gdzie voyage-3-large już cachowane).
5. **Push na origin/main** — 17 commitów nie jest wysłanych; przed dłuższą pauzą wypchnąć lub stagować jako branch.
6. **Wypełnienie versioning fields** w istniejących rekordach KB (schema jest, dane nie) — jeśli planowana integracja z zewnętrznymi źródłami prawnymi.
