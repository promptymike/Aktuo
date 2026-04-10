# Aktuo — Plan Poprawy Jakości

Data: 2026-04-10
Wersja: 1.0

## 1. Stan obecny — wyniki audytów

### Gap Analysis (989 pytań z KB-pipeline)
| Metryka | Wartość |
|---------|---------|
| COVERED (score ≥ 2.0) | 981 / 989 (99.2%) |
| WEAK (0.5–2.0) | 1 (0.1%) |
| GAP (< 0.5) | 7 (0.7%) |

### Accountant Audit (50 losowych pytań FB, język potoczny)
| Metryka | Wartość |
|---------|---------|
| GOOD | 44 / 50 (88.0%) |
| WEAK | 6 / 50 (12.0%) |
| MISS | 0 / 50 (0.0%) |

### Quality Audit (20 pytań eksperckich)
| Metryka | Wartość |
|---------|---------|
| PASS | 17 / 20 (85%) |
| PARTIAL | 3 / 20 (15%) |
| FAIL | 0 / 20 (0%) |

### Baza wiedzy
- 1 808 jednostek wiedzy
- 12 aktów prawnych
- 1 247 unikalnych kategorii w danych (vs. 15 kategorii w categorizerze)

---

## 2. Top 20 brakujących tematów

Na podstawie gap analysis, accountant audit i przeglądu pytań FB:

| # | Temat | Źródło | Problem |
|---|-------|--------|---------|
| 1 | JPK_V7M vs JPK_V7K — różnice strukturalne | GAP | Brak KB unit wyjaśniającego różnicę miesięczny/kwartalny |
| 2 | Urlop macierzyński + B2B jednocześnie | GAP | Brak KB unit o zbiegu tytułów macierzyński/B2B |
| 3 | Prewspółczynnik VAT | WEAK | Jedyny WEAK w gap analysis, brak dedykowanego unitu |
| 4 | PUE ZUS — obsługa, błędy, problemy techniczne | FB | Częste pytania (freq 4–14), ale Aktuo to nie helpdesk ZUS |
| 5 | Różnice kursowe — księgowanie faktur w walutach | Audit | Pytanie o kursy walut na fakturach — category mismatch |
| 6 | L4 vs urlop — optymalizacja, czas pracy na L4 | Audit | KADRY→PIT mismatch, brak unitu o wyborze L4/urlop |
| 7 | Zaliczki PIT od umów zleceń — terminy i korekty | Audit | KADRY→PIT mismatch, cross-category pytanie |
| 8 | Rozliczenia międzyokresowe kosztów (RMK) | Audit | RACHUNKOWO??→terminy mismatch |
| 9 | FP i FGŚP — kiedy opłacać, jak odliczać | FB | Częste pytanie ZUS, skróty |
| 10 | DRA — wypełnianie, korekty, kopiowanie | FB | Najczęstszy temat ZUS (freq=14) |
| 11 | Certyfikaty rezydencji podatkowej (WHT) | FB | Bardzo częste w CIT (freq=10+) |
| 12 | IFT-2R — kiedy składać, za jakie podmioty | FB | Częste pytanie CIT |
| 13 | Środki trwałe — stawki amortyzacji, wykup leasingu | FB | Pytania rachunkowość |
| 14 | NIP kontrahenta w JPK — kiedy z PL, kiedy bez | Audit | JPK→CIT mismatch |
| 15 | Sprawozdanie finansowe — e-Sprawozdanie, XML, KRS | FB | Częste w rachunkowości |
| 16 | Wynagrodzenie minimalne 2026 — składki, koszty | FB | Brak aktualnych kwot |
| 17 | Split payment — obligatoryjny vs dobrowolny | Quality | PARTIAL w quality audit |
| 18 | Samochód w firmie — 50%/100% VAT, ewidencja | Quality | PARTIAL w quality audit |
| 19 | Korekta JPK_V7 — procedura, czynny żal | Quality | PARTIAL w quality audit |
| 20 | Karta podatkowa 2026 — czy nadal dostępna | FB | Zmiany legislacyjne |

---

## 3. Problemy retrievera

### 3.1 Fragmentacja kategorii
**Problem**: 1 247 unikalnych kategorii w KB vs. 15 w categorizerze.
- Categorizer mapuje pytanie na jedną z 15 kategorii
- BM25 boosting (`CATEGORY_BOOST = 3.0`) wymaga dopasowania category chunk → category pytania
- `_category_matches()` w retriever.py używa `broad_law_aliases` i `subcategory_aliases`, ale pokrywa tylko ~30% wariantów

**Rozwiązanie**: Normalizować kategorie w KB do 15 kanonicznych wartości. Jeden skrypt mapujący 1 247 → 15.

### 3.2 Cross-category pytania
**Problem**: Pytania typu "zaliczka PIT od umowy zlecenie" dotyczą zarówno PIT jak i KADRY.
- Categorizer zwraca JEDNĄ kategorię (first match wins)
- 6/50 category mismatches w accountant audit — wszystkie WEAK (nie MISS)

**Rozwiązanie**: Multi-category support — categorizer zwraca listę kategorii, retriever boost'uje chunki z DOWOLNEJ z nich.

### 3.3 Pytania bez treści merytorycznej
**Problem**: 4 z 7 GAP-ów to pytania bez treści ("Co potrzeba?", "Co byście zrobili?", "Co ze znacznikami?").
- BM25 nie może zmatchować pytania bez słów kluczowych
- To nie jest błąd systemu — te pytania nie mają odpowiedzi prawnej

**Rozwiązanie**: Dodać detekcję pytań "bez kontekstu" w RAG pipeline, zwracając prośbę o doprecyzowanie.

### 3.4 BM25 vs semantyczne wyszukiwanie
**Problem**: BM25 wymaga leksykalnego dopasowania tokenów.
- Synonimy ("chorobowe" ≠ "L4") wymagają ręcznego dodawania keywords
- Potoczny język FB ("mały zus", "preferencyjny") vs formalne KB ("art. 18a ustawy o sus")
- NFKD normalizacja + ł→l translacja łagodzi problem, ale nie eliminuje

**Rozwiązanie**: Hybrid retrieval — BM25 + embedding-based (np. `text-embedding-3-small` na polskich danych). BM25 jako fast pre-filter, embeddingi jako re-ranker.

### 3.5 Duplikacja semantyczna w KB
**Problem**: Wiele unitów opisuje ten sam temat z minimalnie inną treścią.
- 1 119 unitów VAT, ale wiele to warianty tego samego artykułu
- BM25 zwraca 5 wariantów tego samego, zamiast 5 różnych tematów

**Rozwiązanie**: Deduplikacja semantyczna (cosine similarity > 0.9 → merge). Albo MMR (Maximal Marginal Relevance) w retrieverze.

---

## 4. Propozycja wykorzystania 989 pytań pipeline'owych

### 4.1 Obecne zasoby
- 989 pytań w `kb-pipeline/questions_*.json` (10 kategorii)
- 500 z nich to pytania z FB (`source_freq > 0`) — prawdziwy język użytkowników
- Format: `{question, category, topic, source_id?, source_freq?}`

### 4.2 Plan wykorzystania

#### Faza 1: Benchmark automatyczny (gotowe)
- `tests/gap_analysis.py` — uruchamiany na każdym PR jako CI check
- `tests/accountant_audit.py` — regresja na prawdziwym języku FB
- Target: 95%+ COVERED, 90%+ GOOD

#### Faza 2: Generowanie nowych KB units (1–2 dni pracy)
1. Wziąć pytania z `source_freq ≥ 3` (najczęściej zadawane, ~150 pytań)
2. Pogrupować po `topic` — każdy topic = potencjalny nowy KB unit
3. Dla każdego topic:
   - Sprawdzić czy istniejący KB unit odpowiada (gap analysis score)
   - Jeśli nie → wygenerować nowy unit z `match_questions.py` + weryfikacja
4. Dodać wygenerowane units do `law_knowledge.json`

#### Faza 3: Question-intent enrichment (2–3 dni)
1. Dla każdego KB unit dodać pole `question_intent` z 3–5 typowymi pytaniami
2. Retriever już indeksuje `question_intent` w BM25 corpus
3. Źródło: 989 pytań pipeline'owych zmapowanych na artykuły przez `match_questions.py`
4. Efekt: BM25 dopasowuje potoczny język pytań do formalnej treści KB

#### Faza 4: Expansion do pełnego korpusu FB (3–5 dni)
1. Zebrać pełny zbiór pytań FB (11 601 z oryginalnego pliku `dedup_questions_output_v3.json`)
2. Uruchomić gap analysis na pełnym zbiorze
3. Zidentyfikować top 50 gap-topics po `source_freq`
4. Wygenerować KB units dla każdego gap-topic
5. Re-benchmark: target 98%+ COVERED na pełnym zbiorze

---

## 5. Benchmarki — cele i metryki

| Metryka | Obecna | Cel (faza 2) | Cel (faza 4) |
|---------|--------|-------------|-------------|
| Gap Analysis COVERED | 99.2% | 99.5% | 99.8% |
| Accountant Audit GOOD | 88.0% | 92.0% | 95.0% |
| Quality Audit PASS | 85.0% | 90.0% | 95.0% |
| Category mismatches | 12.0% | 6.0% | 3.0% |
| KB units | 1 808 | ~1 850 | ~2 000 |
| Unique KB categories | 1 247 | 15 | 15 |

---

## 6. Priorytety implementacji

### Wysoki priorytet (największy wpływ)
1. **Normalizacja kategorii KB** — zmapować 1 247 → 15 kanonicznych. Natychmiastowy wzrost trafności category boost.
2. **Question-intent enrichment** — dodać potoczne formy pytań do KB units. Bezpośrednio poprawia BM25 matching.
3. **Multi-category categorizer** — zwracać top 2–3 kategorie zamiast jednej. Eliminuje cross-category mismatches.

### Średni priorytet (solidna poprawa)
4. **Deduplikacja semantyczna** — usunąć warianty tego samego artykułu, zachować najlepszy.
5. **MMR w retrieverze** — Maximal Marginal Relevance zamiast top-K, żeby chunki były zróżnicowane.
6. **Detekcja pytań bez kontekstu** — "Co potrzeba?", "Co byście zrobili?" → prośba o doprecyzowanie.

### Niski priorytet (long-term)
7. **Hybrid retrieval (BM25 + embeddings)** — znacząco lepsze dopasowanie semantyczne, ale wymaga API costs.
8. **Fine-tuning Claude na polskich danych** — specjalizacja odpowiedzi na polski kontekst prawny.
9. **Feedback loop** — zbieranie ocen użytkowników, automatyczna identyfikacja słabych odpowiedzi.

---

## 7. Bezpieczeństwo (z SECURITY_AUDIT.md)

Niezależnie od poprawy jakości, następujące problemy bezpieczeństwa wymagają natychmiastowej naprawy:

1. **CRITICAL**: Hardcoded password w `app/analytics.py:16`
2. **CRITICAL**: Brak sanitizacji query w `core/generator.py` (prompt injection)
3. **CRITICAL**: Logowanie PII w `core/logger.py` (RODO)
4. **HIGH**: Brak walidacji PESEL/NIP/IBAN w anonymizerze

Pełna lista: `SECURITY_AUDIT.md`
