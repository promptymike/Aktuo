# QUALITY REPORT

Stan repo i audytu na podstawie:

- [tests/output/top100_coverage.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/top100_coverage.json)
- [MISSING_LAWS.md](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/MISSING_LAWS.md)
- [tests/output/slang_analysis.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/slang_analysis.json)
- [tests/output/chunk_accuracy_audit.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/chunk_accuracy_audit.json)
- [tests/output/showcase_retrieval_audit.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/tests/output/showcase_retrieval_audit.json)

## 1. Pokrycie top 100 pytań FB

Top 100 pytań po `freq` z [dedup_questions_output_v3.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/fb_pipeline/dedup_questions_output_v3.json):

| Status | Liczba | Udział |
| --- | ---: | ---: |
| COVERED | 54 | 54.0% |
| WEAK | 0 | 0.0% |
| GAP | 46 | 46.0% |

Najważniejszy wniosek:

- obecna KB dobrze radzi sobie z twardym VAT, KSeF, JPK, PIT i częścią CIT,
- największe odpady nie wynikają z jednej luki, tylko z miksu:
  - pytań poza zakresem,
  - brakujących ustaw pomocniczych,
  - oraz zbyt płytkich unitów na styku kilku ustaw.

## 2. Brakujące ustawy i ich wpływ

Z GAP-ów top 100 wynika, że brakujące akty prawne odpowiadają za około `4` pytań z top 100.

| Brakujący akt | Szacowany wpływ w top 100 |
| --- | ---: |
| Ustawa o zryczałtowanym podatku dochodowym | 1 |
| Prawo przedsiębiorców / CEIDG / ZAW-FA | 1 |
| Kodeks spółek handlowych | 1 |
| Ustawa o rehabilitacji / PFRON | 1 |

Poza tym:

- `23` pytania odpadają nie dlatego, że brakuje całej ustawy, tylko dlatego, że brakuje konkretnych praktycznych unitów w już obecnych aktach,
- `19` pytań to pytania poza zakresem produktu albo stricte operacyjne (`szukam biura`, `jaki kurs`, `wdrożenie programu`, `czy działa system`).

## 3. Top 20 skrótów księgowych do mapy synonimów

Poniżej jest praktyczna lista skrótów do rozbudowy synonym mapy retrievera. Liczby oznaczają wystąpienia w całym datasetcie `11 601` pytań.

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

Wniosek:

- najwięcej wartości da dodanie synonym mapy nie dla „potocznych żartów”, tylko dla bardzo technicznych skrótów księgowych,
- szczególnie ważne są: `kpir`, `kup`, `dra`, `pue`, `bfk`, `di`, `sf`, `wdt`, `wnt`.

## 4. Dokładność merytoryczna chunków

Losowa próba `50` unitów z [law_knowledge.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/data/seeds/law_knowledge.json) porównana do sparsowanych aktów z `kb-pipeline/output/articles_*.json`:

| Ocena | Liczba | Udział |
| --- | ---: | ---: |
| ACCURATE | 40 | 80.0% |
| INACCURATE | 8 | 16.0% |
| UNVERIFIABLE | 2 | 4.0% |

Najważniejszy wniosek:

- KB nie jest „pełna bzdur” — większość losowej próby zgadza się ze źródłem,
- ale `16%` podejrzanych unitów to za dużo jak na produkt, który ma aspirację być single source of truth,
- największe ryzyko pochodzi z:
  - unitów zbyt interpretacyjnych,
  - unitów z doklejonymi liczbami lub warunkami niewidocznymi w źródle,
  - oraz unitów z błędnie dobranym artykułem.

## 5. Showcase questions

Trzy pytania z homepage’u mają obecnie dobry retrieval:

1. `Termin złożenia JPK_V7?`
   - top 1: `Ustawa o VAT | art. 99 ust. 1-3`
2. `Estoński CIT — kto może?`
   - top 1: `Ustawa o podatku dochodowym od osób prawnych | art. 28j ust. 1 oraz art. 28k ust. 1`
3. `Okres wypowiedzenia umowy`
   - top 1: `Kodeks pracy | art. 34`

To jest wystarczająco dobre na warstwę showcase.

## 6. Stan KB

Aktualna liczba unitów w [law_knowledge.json](C:/Users/pawel/Downloads/Aktuo-main/Aktuo-main/data/seeds/law_knowledge.json): `2111`

| Ustawa | Unity |
| --- | ---: |
| Ustawa o VAT | 1256 |
| Ustawa o podatku dochodowym od osób fizycznych | 522 |
| Ustawa o rachunkowości | 93 |
| Kodeks pracy | 60 |
| Ustawa o podatku dochodowym od osób prawnych | 59 |
| Ustawa o systemie ubezpieczeń społecznych | 43 |
| Ordynacja podatkowa | 39 |
| Rozporządzenie KSeF | 29 |
| Rozporządzenie JPK_V7 | 7 |
| Ustawa o VAT - KSeF terminy wdrożenia | 1 |
| Ustawa o VAT - KSeF uproszczenia 2026 | 1 |
| Ustawa o VAT - KSeF zwolnienia | 1 |

## 7. Rekomendacje priorytetowe

Posortowane po wpływie na jakość produktu:

1. Dodać synonym mapę dla skrótów księgowych.
   - Największy szybki zysk dla retrievera bez kosztu API.

2. Rozbudować rachunkowość / KPiR / rozliczenia okresowe.
   - To największa luka tematyczna wewnątrz już istniejących ustaw.

3. Dodać ustawę o ryczałcie.
   - To najtańszy nowy akt z dobrym stosunkiem koszt/impact.

4. Dodać Prawo przedsiębiorców / CEIDG i podstawowe workflow ZAW-FA.
   - W top 100 regularnie pojawiają się pytania operacyjne wokół JDG.

5. Dodać KSH w podstawowym zakresie dla spółek z o.o.
   - Nawet niewielki pakiet poprawi wiarygodność dla pytań o spółki.

6. Przejrzeć i poprawić `INACCURATE` unity z audytu losowej próby.
   - To najważniejszy krok, jeśli Aktuo ma być źródłem referencyjnym, a nie tylko „użytecznym pomocnikiem”.

7. Osobno potraktować pytania poza zakresem.
   - Dla `praktyka`, `erp`, części `inne` warto dodać świadome odpowiedzi typu:
     - „to pytanie dotyczy narzędzia / wdrożenia / rynku pracy, a nie przepisu”.

## Konkluzja

Aktuo ma już sensowne pokrycie najtwardszego jądra prawa księgowego, ale nie jest jeszcze single source of truth.

Największe ryzyko nie leży dziś w braku jednego wielkiego aktu, tylko w:

- lukach na styku ustaw,
- zbyt praktycznych pytaniach, których nie da się pokryć samym tekstem ustawy,
- oraz w części unitów, które są zbyt interpretacyjne względem źródła.

Największy product win na kolejny sprint:

1. synonym map dla języka księgowych,
2. domknięcie rachunkowości / KPiR / ryczałtu,
3. cleanup `INACCURATE` unitów z audytu źródłowego.
