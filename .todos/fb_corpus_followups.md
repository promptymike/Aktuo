# FB corpus ingest — follow-ups

Obserwacje poboczne złapane podczas Zadania 1 (ingest FB corpus). Żadna z nich
nie blokuje Zadania 2, ale każda nadaje się na osobne, małe zadanie.

## 1. README drift

`README.md` wciąż opisuje tylko wcześniejszy "stateless scaffold" —
brakuje wzmianki o warstwach dodanych w 2026 Q1:

- workflow retrieval (`core/workflow_retriever.py`)
- intent router + taksonomia 19 intentów
- clarification gate (`data/prompts/clarification_slots.json`)
- partial workflow answer path
- schema wersjonowania chunków (`effective_from/to`, `source_url`, `source_hash`)

Akcja: osobny PR dokumentacyjny, nie ruszać w ramach ingestu FB.

## 2. Legacy `posts_tagged.json` w fb_pipeline/

`fb_pipeline/posts_tagged.json` (10700 rekordów, 5.7 MB) to post-processed
wariant `posts_output_backup.json` z dodanymi polami `tag`, `char_count`,
`has_comments`, `comment_count`. Nie jest używany w nowym pipeline, ale
nadal tracked w git.

Akcja: zdecydować czy gitignorować i `git rm --cached`, czy archiwizować
pod `fb_pipeline/legacy/` razem z `01_tag_and_batch.py` / `02_chatgpt_prompts.md`
/ `03_merge_outputs.py`. Osobne zadanie, bo dotyka retencji starego pipeline'u.

## 3. Scraper zostawia "... Wyświetl więcej"

W top-20 keywords znormalizowanego korpusu zajmują wysokie pozycje tokeny
`wyświetl` (#8) i `więcej` (#2). To artefakt scrapera — FB ucina długie
posty dodając UI label "... Wyświetl więcej", który został zachowany
w tekście surowym.

Akcja: albo poprawić scraper (docelowe), albo dodać drugi krok normalizacji
usuwający tę frazę przed Zadaniem 2, żeby nie zniekształcała embeddingów.

## 4. Długie komentarze udające posty

Top-1 najbardziej angażujący post (10 komentarzy) to fragment wyglądający
na długi komentarz, nie post — scraper najwyraźniej przy niektórych wątkach
zaciąga dalej idące odpowiedzi.

Akcja: w Zadaniu 2 dodać heurystyczny filtr (długi tekst bez pytajnika i bez
"czy/jak/kiedy" jako pierwszych 20 tokenów → flaga `probably_comment`).
Albo sanity-check scrapera: czy dla losowych 20 top-engaging postów "post"
faktycznie jest korzeniem wątku, a nie najwyżej głosowaną odpowiedzią.
