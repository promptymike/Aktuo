# Brakujące ustawy i luki tematyczne

Analiza oparta na pliku [tests/output/top100_coverage.json](tests/output/top100_coverage.json) dla top 100 pytań z [fb_pipeline/dedup_questions_output_v3.json](fb_pipeline/dedup_questions_output_v3.json).

## Podsumowanie

- Przeanalizowane pytania: `100`
- `COVERED`: `54`
- `GAP`: `46`
- `WEAK`: `0`

Wśród `46` pytań oznaczonych jako `GAP` są trzy różne grupy problemów:

| Typ problemu | Liczba pytań | Co to oznacza |
| --- | ---: | --- |
| Brakuje całej ustawy / rozporządzenia | 4 | KB nie ma właściwego aktu prawnego dla pytania |
| Brakuje konkretnego tematu w istniejącej ustawie | 23 | Właściwa ustawa jest w KB, ale pokrycie jest zbyt płytkie lub zbyt ogólne |
| Pytanie poza zakresem produktu / operacyjne | 19 | To nie jest problem braku przepisu, tylko pytanie o wdrożenie, szkolenie, pracę albo narzędzie |

## 1. Brakujące ustawy / rozporządzenia

To są luki, które realnie obniżają pokrycie i wymagają dodania nowych źródeł.

| Brakujący akt | Liczba pytań w top 100 | Typowe pytania |
| --- | ---: | --- |
| Ustawa o zryczałtowanym podatku dochodowym | 1 | stawka ryczałtu dla budowy i montażu drewnianej konstrukcji szkieletowej |
| Prawo przedsiębiorców / procedury CEIDG i ZAW-FA | 1 | podpis, profil zaufany, CEIDG / JDG / ZAW-FA |
| Kodeks spółek handlowych | 1 | pytania o spółkę z o.o. jako formę prowadzenia działalności |
| Ustawa o rehabilitacji zawodowej i społecznej oraz zatrudnianiu osób niepełnosprawnych (PFRON) | 1 | rejestracja pełnomocnictwa i składanie wniosków PFRON |

### Wniosek

Największa luka ustawowa w top 100 nie dotyczy jednej ogromnej brakującej ustawy, tylko kilku wąskich, ale regularnie pojawiających się domen praktycznych:

1. ryczałt,
2. CEIDG / Prawo przedsiębiorców,
3. KSH,
4. PFRON.

## 2. Luki tematyczne w już istniejących ustawach

Tutaj baza ma właściwy akt prawny, ale brakuje odpowiednio precyzyjnych unitów albo retriever zbyt łatwo wpada w złą gałąź prawa.

### Rachunkowość / KPiR / rozliczenia okresowe

Szacowany wpływ: `12` pytań z top 100.

Najczęstsze braki:

- ujęcie kosztów dotyczących poprzedniego roku,
- zaliczki i przeksięgowania po dodaniu faktury kosztowej,
- KPiR: data przychodu vs data wydatku,
- koszty bilansowe vs KUP przy leasingu,
- wywóz nieczystości, koszty pośrednie, moment ujęcia,
- rozliczenia na przełomie miesięcy przy KSeF i KPiR.

To nie wygląda na brak całej ustawy, tylko na zbyt płytką warstwę praktycznych unitów na styku:

- ustawa o rachunkowości,
- PIT/CIT,
- KPiR,
- moment ujęcia kosztu / przychodu.

### VAT + JPK: moment wykazania, transakcje zagraniczne, oznaczenia

Szacowany wpływ: `5` pytań z top 100.

Najczęstsze braki:

- WDT: faktura w jednym miesiącu, wysyłka w kolejnym,
- VAT-UE i JPK przy rozjechaniu dokumentu i dostawy,
- usługa naprawy pojazdu dla kontrahenta spoza UE na terytorium Polski,
- relacja stawek VAT do oznaczeń JPK,
- data sprzedaży vs ujęcie w VAT i KPiR.

Wniosek: sama ustawa o VAT jest obecna, ale potrzeba więcej unitów:

- miejsce świadczenia usług,
- moment wykazania w JPK/VAT-UE,
- case’y transgraniczne,
- praktyka księgowania na przełomie okresów.

### ZUS: operacyjne pytania deklaracyjne

Szacowany wpływ: `3` pytania z top 100.

Najczęstsze braki:

- DRA dla JDG bez pracowników,
- PUE / e-Płatnik,
- aktualne łączne składki przy preferencyjnym ZUS / małym ZUS.

Tu częściowo problemem nie jest brak ustawy, tylko to, że użytkownicy pytają językiem operacyjnym:

- "gdzie to kliknąć",
- "czy działa e-Płatnik",
- "ile teraz wynoszą składki".

Do pełnego pokrycia potrzeba nie tylko przepisów, ale też warstwy praktycznej / proceduralnej.

### Kodeks pracy / kadry

Szacowany wpływ: `3` pytania z top 100, ale wszystkie wyglądają na szum kategorii lub pytania niejednoznaczne.

To nie jest dziś główna luka ustawowa. Problemem jest raczej:

- błędne przypisanie kategorii w datasetcie,
- zbyt skrótowy język użytkownika,
- pytania mieszające kadry z leasingiem albo zerowym zarobkiem.

## 3. Pytania poza zakresem produktu

Łącznie: `19` pytań z top 100.

To głównie:

- szukanie pracy,
- rekomendacje kursów i szkoleń,
- wdrożenie do programu,
- prośby o kontakt do specjalisty,
- pytania o konkretne systemy ERP (`Symfonia`, `Subiekt`),
- bardzo ogólne "bardzo proszę o pomoc?" bez kontekstu.

Takie pytania nie powinny być traktowane jako luka merytoryczna KB. To raczej:

1. pytania poza zakresem Aktuo,
2. pytania sprzedażowe / networkingowe,
3. pytania o software i wdrożenia.

## Priorytet produktowy

Największy wpływ na realne pokrycie top 100 dają kolejno:

1. Dodanie ustawy o ryczałcie.
2. Rozbudowa unitów rachunkowości / KPiR / rozliczeń okresowych.
3. Rozbudowa VAT + JPK o moment wykazania i case’y zagraniczne.
4. Dodanie podstawowego pakietu CEIDG / Prawo przedsiębiorców.
5. Dodanie wąskiego pakietu PFRON.
6. Dodanie KSH dla najczęstszych pytań o spółki.

## Konkluzja

Największa luka nie polega dziś na tym, że "brakuje jednej wielkiej ustawy". Z top 100 częściej odpadają:

- pytania praktyczne spoza zakresu,
- pytania na styku kilku ustaw,
- pytania operacyjne i proceduralne,
- oraz pytania, dla których KB ma ustawę, ale nie ma wystarczająco konkretnego, praktycznego unitu.
