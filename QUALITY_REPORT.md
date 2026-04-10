# QUALITY REPORT

Stan po wykonanych naprawach na podstawie:

- [tests/output/top100_coverage.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/top100_coverage.json)
- [tests/output/question_usage_audit.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/question_usage_audit.json)
- [tests/output/top30_units_to_fix.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/top30_units_to_fix.json)
- [tests/output/slang_analysis.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/slang_analysis.json)
- [tests/output/chunk_accuracy_audit.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/chunk_accuracy_audit.json)
- [tests/output/showcase_retrieval_audit.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/showcase_retrieval_audit.json)
- [MISSING_LAWS.md](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/MISSING_LAWS.md)

## 1. Pokrycie top 100 pytań FB

Top 100 pytań po `freq` z [fb_pipeline/dedup_questions_output_v3.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/fb_pipeline/dedup_questions_output_v3.json):

| Status | Liczba | Udział |
| --- | ---: | ---: |
| COVERED | 54 | 54.0% |
| WEAK | 0 | 0.0% |
| GAP | 46 | 46.0% |

Najważniejszy wniosek:

- obecna KB dobrze radzi sobie z twardym VAT, JPK, KSeF, PIT i częścią CIT,
- największe odpady nie wynikają z jednej luki, tylko z miksu:
  - pytań poza zakresem,
  - brakujących aktów pomocniczych,
  - oraz zbyt płytkich lub zbyt interpretacyjnych unitów w już istniejących ustawach.

## 2. Wykonane naprawy

W tym kroku zostały wykonane realne poprawki, a nie tylko opis problemu:

1. Usunięto `30` najbardziej ryzykownych unitów z [data/seeds/law_knowledge.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/data/seeds/law_knowledge.json).
2. Lista usuniętych rekordów wraz z powodami została zapisana do [tests/output/top30_units_to_fix.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/top30_units_to_fix.json).
3. Rozszerzono [core/retriever.py](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/core/retriever.py) o synonym map v1 dla języka księgowych.
4. Rozszerzono [core/categorizer.py](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/core/categorizer.py) o brakujące skróty i potoczne formy pytań.
5. Dodano testy regresyjne dla nowych skrótów i synonym mapy.

Wpływ cleanupu KB:

| Miara | Wartość |
| --- | ---: |
| Rekordy przed cleanupem | 2111 |
| Rekordy usunięte | 30 |
| Rekordy po cleanupie | 2081 |

Rozbicie usuniętych rekordów:

| Typ naprawy | Rekordy |
| --- | ---: |
| Placeholder / odpowiedzi poza zakresem ustawy | 19 |
| Unity oznaczone jako `INACCURATE` lub wysokiego ryzyka w audycie źródłowym | 11 |

Rozbicie po ustawach:

| Ustawa | Usunięte unity |
| --- | ---: |
| Kodeks pracy | 17 |
| Ustawa o VAT | 6 |
| Ustawa o podatku dochodowym od osób fizycznych | 5 |
| Rozporządzenie JPK_V7 | 1 |
| Rozporządzenie KSeF | 1 |

Wniosek:

- usunięte zostały przede wszystkim odpowiedzi typu "ten artykuł tego nie reguluje", które zaśmiecały retrieval i zwiększały ryzyko złych dopasowań,
- wycięto też kilka unitów z konkretnymi błędami merytorycznymi wykrytymi przez porównanie do sparsowanych artykułów ustaw.

## 3. Top 30 unitów do poprawy

Top 30 zostało potraktowane jako pakiet naprawczy:

- `19` rekordów to placeholdery lub odpowiedzi poza zakresem ustawy,
- `11` rekordów to unity wykryte jako `INACCURATE` lub wysokiego ryzyka w audycie źródłowym,
- pełna lista jest w [tests/output/top30_units_to_fix.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/top30_units_to_fix.json).

Najczęstsze wzorce błędów w tej trzydziestce:

1. Odpowiedzi w stylu "ten artykuł tego nie reguluje", które nie pomagają użytkownikowi i potrafią wciągać retriever na zły tor.
2. Doklejone informacje proceduralne lub formularze niewynikające z przepisu.
3. Odpowiedzi z liczbami lub warunkami, których nie ma w źródłowym artykule.
4. Jednostki mieszające prawo materialne z praktyką systemową, np. KSeF, JPK albo kadry.

## 4. Top 5 brakujących ustaw

To jest priorytetowy backlog ustaw i aktów, które najbardziej zwiększą pokrycie realnych pytań:

| Priorytet | Brakujący akt | Dlaczego jest ważny |
| --- | --- | --- |
| 1 | Ustawa o zryczałtowanym podatku dochodowym | Regularnie wracają pytania o stawki ryczałtu, wybór formy i branżowe wyjątki. |
| 2 | Prawo przedsiębiorców | Brakuje odpowiedzi o JDG, obowiązkach przedsiębiorcy i podstawowych procedurach działalności. |
| 3 | Kodeks spółek handlowych | Padają pytania o spółkę z o.o., odpowiedzialność wspólników, zarząd i formalności korporacyjne. |
| 4 | Ustawa o rehabilitacji zawodowej i społecznej oraz zatrudnianiu osób niepełnosprawnych | Pytania o PFRON i obowiązki pracodawcy są obecnie praktycznie poza KB. |
| 5 | Ustawa zasiłkowa | Potrzebna do domknięcia chorobowego i macierzyńskiego, bo same przepisy ZUS i Kodeksu pracy nie wystarczają. |

Wniosek:

- największa luka to nie "jedna wielka brakująca ustawa", tylko kilka mniejszych, ale stale wracających obszarów praktycznych,
- najszybszy wzrost pokrycia dają dziś: ryczałt, Prawo przedsiębiorców i ustawa zasiłkowa.

## 5. Synonym map v1

Naprawa została wdrożona w:

- [core/retriever.py](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/core/retriever.py)
- [core/categorizer.py](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/core/categorizer.py)

Dodane i obsłużone skróty oraz potoczne formy:

| Obszar | Przykłady skrótów / wariantów |
| --- | --- |
| VAT / JPK | `vat`, `jpk`, `jpk_v7`, `gtu`, `wdt`, `wnt`, `mpp`, `tp`, `sw`, `ee`, `bfk`, `di`, `fp`, `wew`, `ro` |
| PIT / CIT | `pit`, `pit11`, `pit-11`, `pit4r`, `pit-4r`, `cit`, `cit8`, `cit-8`, `wht`, `estończyk` |
| ZUS / kadry | `zus`, `zusik`, `dra`, `rca`, `rsa`, `pue`, `bhp` |
| Księgowość | `kpir`, `sf`, `kup`, `krs`, `jdg` |
| KSeF | `ksef`, `krajowy system e-faktur` |

Najważniejszy efekt:

- retriever przestał polegać wyłącznie na formalnych nazwach z ustawy,
- większa część języka używanego przez księgowych trafia teraz do właściwej kategorii i właściwych chunków.

## 6. Ile pytań z FB trafiło do pipeline KB

Dokładny audyt został zapisany do [tests/output/question_usage_audit.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/question_usage_audit.json).

Najważniejsze liczby:

| Miara | Wartość |
| --- | ---: |
| Wszystkie pytania w FB dataset (raw) | 11601 |
| Wszystkie pytania unikalne po normalizacji | 11509 |
| Unikalne pytania z FB użyte w rootowych `questions_*.json` pipeline'u | 500 |
| Pytania z FB, które nigdy nie trafiły do rootowego pipeline'u | 11098 |
| Niewykorzystane pytania z `freq >= 3` | 240 |

Ważna uwaga metodologiczna:

- liczenie "użyte w pipeline" dotyczy wyłącznie rootowych plików `kb-pipeline/questions_*.json`, zgodnie z Twoją prośbą,
- stagingowe banki w `kb-pipeline/input/questions_*_fb.json` nie są liczone jako "użyte", dopóki nie zostały przeniesione do właściwego pipeline'u,
- suma kategorii może być minimalnie wyższa niż globalne `500`, bo część znormalizowanych pytań trafia do więcej niż jednego banku albo do banku z inną kategorią niż w surowym datasetcie.

Rozbicie per kategoria:

| Kategoria | Total w FB | Użyte w pipeline | Niewykorzystane | Niewykorzystane `freq >= 3` |
| --- | ---: | ---: | ---: | ---: |
| rachunkowosc | 2177 | 100 | 2077 | 39 |
| vat | 2102 | 0 | 2102 | 61 |
| ksef | 1566 | 1 | 1565 | 31 |
| kadry | 1074 | 102 | 972 | 10 |
| pit | 894 | 0 | 894 | 17 |
| zus | 883 | 100 | 783 | 0 |
| praktyka | 787 | 0 | 787 | 48 |
| inne | 566 | 0 | 566 | 7 |
| jpk | 520 | 100 | 420 | 4 |
| erp | 340 | 0 | 340 | 12 |
| cit | 259 | 100 | 159 | 0 |
| ordynacja | 189 | 0 | 189 | 3 |
| spolki | 123 | 0 | 123 | 3 |
| ceidg | 121 | 0 | 121 | 5 |

Wniosek:

- dziś wykorzystaliśmy tylko `500` unikalnych pytań z `11 509` unikalnych pytań FB po normalizacji,
- największe niewykorzystane zbiory o wysokim potencjale to: `vat`, `rachunkowosc`, `ksef`, `pit`, `praktyka`,
- sam VAT ma `2102` niewykorzystane pytania, z czego `61` było zadawanych co najmniej 3 razy.

## 7. Top 20 skrótów księgowych do dalszej mapy synonimów

Na podstawie [tests/output/slang_analysis.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/slang_analysis.json):

| Skrót | Pełna fraza | Wystąpienia |
| --- | --- | ---: |
| `vat` | podatek od towarów i usług | 1097 |
| `ksef` | Krajowy System e-Faktur | 829 |
| `pit` | podatek dochodowy od osób fizycznych | 406 |
| `zus` | Zakład Ubezpieczeń Społecznych | 384 |
| `jpk` | jednolity plik kontrolny | 376 |
| `kpir` | księga przychodów i rozchodów | 308 |
| `cit` | podatek dochodowy od osób prawnych | 220 |
| `jdg` | jednoosobowa działalność gospodarcza | 204 |
| `nip` | numer identyfikacji podatkowej | 157 |
| `kup` | koszty uzyskania przychodu | 117 |
| `dra` | deklaracja ZUS DRA | 70 |
| `krs` | Krajowy Rejestr Sądowy | 53 |
| `bfk` | oznaczenie BFK | 52 |
| `di` | oznaczenie DI | 48 |
| `pue` | Platforma Usług Elektronicznych ZUS | 41 |
| `wnt` | wewnątrzwspólnotowe nabycie towarów | 40 |
| `skwp` | Stowarzyszenie Księgowych w Polsce | 38 |
| `fp` | oznaczenie FP w JPK | 29 |
| `sf` | sprawozdanie finansowe | 22 |
| `wdt` | wewnątrzwspólnotowa dostawa towarów | 18 |

## 8. Dokładność merytoryczna chunków

Losowa próba `50` unitów z KB porównana do sparsowanych artykułów ustaw:

| Ocena | Liczba | Udział |
| --- | ---: | ---: |
| ACCURATE | 40 | 80.0% |
| INACCURATE | 8 | 16.0% |
| UNVERIFIABLE | 2 | 4.0% |

Najważniejszy wniosek:

- KB nie jest "pełna bzdur", ale `16%` błędnych unitów w losowej próbie to nadal za dużo na produkt referencyjny,
- wykonany cleanup usunął część najbardziej ryzykownych rekordów z tej grupy, ale to nadal temat do dalszego systematycznego czyszczenia.

## 9. Showcase questions

Trzy pytania z homepage'u mają obecnie sensowny retrieval:

1. `Termin złożenia JPK_V7?`
   - top 1: `Ustawa o VAT | art. 99 ust. 1-3`
2. `Estoński CIT — kto może?`
   - top 1: `Ustawa o podatku dochodowym od osób prawnych | art. 28j ust. 1 oraz art. 28k ust. 1`
3. `Okres wypowiedzenia umowy`
   - top 1: `Kodeks pracy | art. 34`

## 10. Stan KB po naprawach

Aktualna liczba unitów w [data/seeds/law_knowledge.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/data/seeds/law_knowledge.json): `2081`

| Ustawa | Unity |
| --- | ---: |
| Ustawa o VAT | 1250 |
| Ustawa o podatku dochodowym od osób fizycznych | 517 |
| Ustawa o rachunkowości | 93 |
| Ustawa o podatku dochodowym od osób prawnych | 59 |
| Kodeks pracy | 43 |
| Ustawa o systemie ubezpieczeń społecznych | 43 |
| Ordynacja podatkowa | 39 |
| Rozporządzenie KSeF | 28 |
| Rozporządzenie JPK_V7 | 6 |
| Ustawa o VAT - KSeF terminy wdrożenia | 1 |
| Ustawa o VAT - KSeF uproszczenia 2026 | 1 |
| Ustawa o VAT - KSeF zwolnienia | 1 |

## 11. Rekomendacje priorytetowe

Posortowane po wpływie:

1. Przepchnąć do pełnego pipeline'u największe niewykorzystane banki FB: `VAT`, `rachunkowosc`, `KSeF`, `PIT`.
2. Dodać ustawę o ryczałcie i ustawę zasiłkową.
3. Rozbudować pytania i unity o język operacyjny księgowych, zwłaszcza dla ZUS, JPK i praktyki JDG.
4. Kontynuować cleanup unitów `INACCURATE` na podstawie porównania z `articles_*.json`.
5. Utrzymać i rozwijać synonym mapę, bo to najtańsza poprawa jakości retrievalu bez kosztu API.

## Konkluzja

Aktuo ma już sensowne pokrycie najtwardszego jądra pytań prawno-podatkowych, ale nadal nie jest single source of truth.

Największy problem nie leży dziś w samym braku danych, tylko w trzech rzeczach naraz:

1. za mała część pytań FB została faktycznie przepchnięta przez pipeline,
2. w KB nadal były rekordy placeholderowe i zbyt interpretacyjne,
3. język użytkowników jest bardziej skrótowy i operacyjny niż język ustaw.

W tym kroku zostały wykonane dwie realne naprawy o najlepszym stosunku koszt/efekt:

- cleanup `30` najbardziej ryzykownych unitów,
- oraz wdrożenie `synonym map v1` w retrievalu i kategoryzacji.
