# AKTUO — FB Posts → Knowledge Base Pipeline

## Co masz

- `posts_output.json` — 10 700 surowych postów z grup FB (120k+ księgowych)
- Posty + komentarze = realne pytania z rynku

## Pipeline

```
posts_output.json
       │
       ▼
[01_tag_and_batch.py]     ← taguje noise/content, NIE usuwa nic
       │
       ├── posts_tagged.json     (pełny backup z tagami)
       ├── batches/batch_001.txt (do ChatGPT)
       ├── batches/batch_002.txt
       └── stats.txt
       │
       ▼
[ChatGPT — batch processing]  ← prompty z 02_chatgpt_prompts.md
       │
       ├── batch_outputs/batch_001_output.json
       ├── batch_outputs/batch_002_output.json
       └── ...
       │
       ▼
[03_merge_outputs.py]     ← łączy outputy
       │
       └── all_questions_raw.json
       │
       ▼
[ChatGPT — deduplikacja]  ← prompt końcowy z 02_chatgpt_prompts.md
       │
       └── aktuo_questions_final.json  (posortowane po freq)
```

## Krok po kroku

### 1. Przygotowanie
```bash
# Skopiuj posts_output.json do tego folderu
cp /ścieżka/do/posts_output.json .

# Uruchom tagger
python 01_tag_and_batch.py
```

### 2. ChatGPT — przetwarzanie batchy
1. Otwórz ChatGPT (GPT-4o)
2. Wklej SYSTEM PROMPT z `02_chatgpt_prompts.md` (sekcja 1)
3. Dla każdego pliku z `batches/`:
   - Wklej BATCH PROMPT (sekcja 2) + zawartość pliku
   - Zapisz output jako `batch_outputs/batch_XXX_output.json`
4. Jak ChatGPT przytnie JSON — napisz "kontynuuj"

### 3. Merge
```bash
mkdir batch_outputs
# Skopiuj tu outputy z ChatGPT
python 03_merge_outputs.py
```

### 4. Deduplikacja (ChatGPT)
1. Nowy czat w ChatGPT
2. Wklej PROMPT KOŃCOWY (sekcja 3 z `02_chatgpt_prompts.md`)
3. Wklej zawartość `all_questions_raw.json`
4. Zapisz output jako `aktuo_questions_final.json`

### 5. Wrzutka do Aktuo KB
Top pytania z `aktuo_questions_final.json` → `questions_*.json` w ETL pipeline.

## Pliki

| Plik | Opis | Usuwać? |
|------|-------|---------|
| posts_output.json | Surowy scrape | NIGDY |
| posts_tagged.json | Backup z tagami | NIGDY |
| batches/*.txt | Batche do GPT | Po przetworzeniu |
| batch_outputs/*.json | Outputy GPT | Po merge |
| all_questions_raw.json | Surowe pytania | Po deduplikacji |
| aktuo_questions_final.json | **FINALNY OUTPUT** | NIGDY |

## Szacunki

- ~10 700 postów
- ~60-70% content, ~30-40% noise/short/empty
- ~6 000-7 000 postów do ChatGPT
- ~25-35 batchy po 200
- ~2 000-4 000 surowych pytań
- ~500-1 000 unikalnych po deduplikacji
- Koszt ChatGPT: ~$0 jeśli Plus, albo $5-10 na API
