# Streamlit Readiness Report

Data: 2026-04-18
Środowisko: Windows 11 Home, Python 3.12, streamlit 1.56.0
Cel: sanity check Streamlita i retrievera przed dopuszczeniem 42 draftów do testerów.

## TL;DR

- ✅ **Streamlit startuje bez błędów** (app/main.py) — `http://localhost:8599` odpowiada w ~10 s od `streamlit run`.
- ⚠️ **Retriever widzi tylko 10 legacy units**, a nie 42 nowe drafty.
- 🔎 Powód: `core/workflow_retriever.py::load_workflow_documents()` czyta `WORKFLOW_SEED_PATH = data/workflow/workflow_seed.json` (10 units w starym schemacie: `workflow_area` + `steps` jako plain strings, bez `id`, bez `answer_steps`, bez `legal_anchors`).
- 📁 42 nowe drafty są w `data/workflow_drafts/wf_*.json` (nowy schemat: `id`, `answer_steps`, `legal_anchors`, `self_critique`, `corrections_applied`), ale ŻADEN moduł w `core/` ich nie ładuje — są referenced wyłącznie przez skrypty w `analysis/`.
- 🛠️ Żeby retriever obsłużył 42 drafty, trzeba albo (a) zmerżować `wf_*.json` do `workflow_seed.json` z mapowaniem schematu, albo (b) rozszerzyć `load_workflow_documents()` o drugie źródło (np. `WORKFLOW_DRAFTS_DIR`). To osobne zadanie poza zakresem tego checku.

## Krok 1 — Streamlit startup

```
$ python -m streamlit run app/main.py --server.headless=true --server.port=8599 ...

  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8599
  Network URL: http://192.168.34.3:8599
```

- Brak ImportError / AttributeError / syntax error.
- `config.settings` wczytuje się (wymaga `AKTUO_ANTHROPIC_API_KEY` w env — ustawiony).
- `app.main` importuje `app.chat`, `app.sidebar`, `config.settings`, `core.generator`, `core.logger` — wszystkie bez problemu.

## Krok 2 — Retriever: ile draftów widzi

```python
from core.workflow_retriever import load_workflow_documents
docs = load_workflow_documents()
print(len(docs))  # -> 10
```

Seed path: `C:\Users\pawel\Downloads\Aktuo-main\Aktuo-main\data\workflow\workflow_seed.json`
Loaded: **10 / 42 (24 %)** — brakuje 32 draftów.

Fizycznie na dysku w `data/workflow_drafts/`:

- 42 plików `wf_*.json` (w tym `wf_10`, `wf_139`, `wf_merge_120_121`, `wf_merge_33_86_95`).
- Dodatkowo batch logi: `batch1_drafts.jsonl`, `batch1_run_log.json`, `batch2_drafts.jsonl`, `batch2_run_log.json`.

10 legacy seed units pochodzi ze wcześniejszej iteracji (source_type = `workflow_seed_v1`, bez `legal_anchors`, bez `self_critique`). Szczegółowy cross-ref w `analysis/workflow_seed_vs_drafts_comparison.md`.

## Krok 3 — 2 testowe zapytania

### Q1: "Jak wystawić fakturę korygującą w KSeF?"

Oczekiwane: `wf_merge_120_121` (KSeF moment podatkowy + korekty) albo `wf_139` (KSeF obieg).

| # | score | title | hit? |
|---|-------|-------|------|
| 1 | 17.50 | Obieg faktur, statusów i korekt w KSeF (legacy S3) | ⚠️ CZĘŚCIOWY |
| 2 | 14.00 | Nadawanie uprawnień i dostępów w KSeF (legacy S8) | — |
| 3 |  3.00 | Ujęcie dokumentów w okresie i ewidencji (legacy S1) | — |

- `confident = True`, top_score = 17.50.
- Top wynik to LEGACY S3 (ogólny "obieg + korekty"), który jest najbliższym approximation `wf_merge_120_121` / `wf_139`. Ale nie dostaje testera do nowego draftu z `answer_steps` i `legal_anchors`.

### Q2: "Jaka jest kwota wolna przy zajęciu komorniczym w 2026?"

Oczekiwane: `wf_10_potracenia_komornicze_niealimentacyjne`.

| # | score | title | hit? |
|---|-------|-------|------|
| 1 | 5.50 | Obieg faktur, statusów i korekt w KSeF | ❌ FAŁSZYWY |
| 2 | 2.00 | Obsługa zgłoszeń, wyrejestrowań ZUS | ❌ |
| 3 | 2.00 | Leasing, wykup samochodu | ❌ |

- `confident = False`, top_score = 5.50 (< threshold 6.0).
- **Brak trafienia.** `wf_10` jest w `data/workflow_drafts/` ale niewidoczny dla retrievera. To konsekwencja ustaleń z Kroku 2.

## Krok 4 — Jak uruchomić aplikację lokalnie

```bash
# w repo root
python -m streamlit run app/main.py
# albo: streamlit run app/main.py

# wymagane env:
export AKTUO_ANTHROPIC_API_KEY=sk-ant-...
# opcjonalnie (workflow tuning):
export AKTUO_WORKFLOW_SEED_PATH=data/workflow/workflow_seed.json
export AKTUO_WORKFLOW_CONFIDENCE_THRESHOLD=6.0
```

Domyślny port: 8501. Headless mode: `--server.headless=true`.

## Wnioski

1. **App boots cleanly** — nie ma pluginów do podpięcia, env var `AKTUO_ANTHROPIC_API_KEY` musi być set. Nic w main/sidebar/chat nie blokuje startu.
2. **Retriever nie widzi nowych draftów** — potwierdzone zarówno wprost (10 vs 42), jak i behawioralnie (Q2 retrieval miss). To nie jest problem manual fixes ani korekt v3 — to pre-existing gap w integracji warstwy workflow_drafts z core retrieverem.
3. **Pytest status:** 260 passed (ostatni run po Stage 8). Manual fixes w tej sesji dotykają wyłącznie content draftów, nie retrievera, więc testy pozostają green.
4. **Nie przekazywać 42 draftów testerom**, dopóki nie zostanie podjęta decyzja (merge do seed vs drugie źródło w `load_workflow_documents()`). Sam fakt że fizycznie istnieją w `data/workflow_drafts/` nie sprawia, że Streamlit je serwuje.

## Zalecane follow-upy (poza scope tego zadania)

- Dodać `AKTUO_WORKFLOW_DRAFTS_DIR` + loader w `core/workflow_retriever.py` mapujący nowy schemat (`answer_steps`→`steps`, `common_mistakes`→`common_pitfalls`, `legal_anchors` exposed osobno) na `WorkflowDocument`.
- Alternatywnie: jednorazowy skrypt `analysis/merge_drafts_into_seed.py` produkujący `workflow_seed.json` z 42 records + backward-compatible polami dla starych 10 units.
- Dopisać test integracyjny `tests/test_workflow_retriever.py::test_retrieves_batch2_drafts` sprawdzający że Q2 o komorniczej zwraca `wf_10`.
