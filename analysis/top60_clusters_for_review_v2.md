# Top klastrów do review — v2 (po decyzjach Pawła)

**Zmiany względem v1:** przywrócono **16** klastrów (operacyjne kadrowo-płacowe, v1 wycięła je zbyt agresywnym keywordem 'wynagrodz'), utrzymano wykluczenie **10** (faktycznie społeczne/niszowe), oraz zmergowano **3** grupy klastrów w jeden workflow każda.

Z **144** oryginalnych klastrów: **10** wykluczono (filtr + decyzje), **7** połączono w **3** merge'y, finalnie **130** klastrów w rankingu — pokazano top **60**:

```
score = size * 0.4 + avg_comments * 50 * 0.4 + bonus * 0.2
bonus = 100 dla topic_area ∈ {KSeF, KPiR, VAT, ZUS, PIT, CIT, JPK, kadry, rachunkowość}
dla merge'ów: size = suma; avg_comments = średnia ważona size
```

**Rekomendacje heurystyczne (do weryfikacji przez Pawła):**
- RECOMMENDED WORKFLOW: **21** klastrów
- CONSIDER: **39** klastrów
- LOW PRIORITY: **0** klastrów

**Jak używać:** przejrzyj każdą sekcję, przeczytaj 3 przykładowe posty, i wypełnij `decyzja Pawła` jedną z:
- `WORKFLOW` — klaster wchodzi jako kandydat workflow rekordu w Zadaniu 3
- `SKIP` — odpada
- `MERGE_WITH_#X` — powinien być połączony z klastrem #X

## Zastosowane merge'y

| Merge | Cluster_ids | Nowy label | Topic | Size (suma) | AvgComm (ważona) |
|---|---|---|---|---:|---:|
| M1 | `120 + 121` | KSeF: moment podatkowy, data wystawienia, korekty | KSeF | 838 | 1.42 |
| M2 | `101 + 102` | Macierzyństwo: wnioski urlopowe, zasiłki, składki ZUS | kadry | 379 | 1.40 |
| M3 | `33 + 86 + 95` | Roczne rozliczenia PIT: PIT-4R, PIT-11, korekty i przekazanie | PIT | 329 | 1.46 |

## Tabela zbiorcza (top 60)

| # | Score | Size | AvgComm | Topic | Rekomendacja | Label | cluster_id | Decyzja |
|---:|---:|---:|---:|---|---|---|---|---|
| 1 ⟵M | 383.6 | 838 | 1.42 | KSeF | CONSIDER | KSeF: moment podatkowy, data wystawienia, korekty | `merge[120+121]` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 2 | 363.2 | 797 | 1.22 | kadry | CONSIDER | Zaliczanie umów zlecenie i DG do stażu pracy od 2026 | `7` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 3 | 255.4 | 493 | 1.91 | kadry | RECOMMENDED WORKFLOW | Wymiar urlopu wypoczynkowego przy niepełnym etacie i zmianie wymiaru | `45` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 4 | 215.1 | 427 | 1.21 | VAT | CONSIDER | Księgowanie faktur zagranicznych: WNT, import usług i towarów | `66` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 5 | 206.8 | 409 | 1.16 | kadry | CONSIDER | Ewidencja i rozliczanie czasu pracy przy różnych systemach i wymiarach etatu | `35` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 6 ⟵M | 199.7 | 379 | 1.40 | kadry | CONSIDER | Macierzyństwo: wnioski urlopowe, zasiłki, składki ZUS | `merge[101+102]` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 7 | 192.4 | 359 | 1.44 | PIT | CONSIDER | Leasing samochodu osobowego: limity KUP i odliczenie VAT | `63` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 8 | 185.2 | 337 | 1.52 | KSeF | RECOMMENDED WORKFLOW | KSeF: nadawanie uprawnień podmiotom i certyfikaty dla biur rachunkowych | `99` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 9 ⟵M | 180.7 | 329 | 1.46 | PIT | CONSIDER | Roczne rozliczenia PIT: PIT-4R, PIT-11, korekty i przekazanie | `merge[33+86+95]` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 10 | 170.2 | 306 | 1.39 | ZUS | CONSIDER | Mały ZUS Plus: ponowne skorzystanie po przerwie i nowe zasady od 2026 | `79` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 11 | 166.1 | 287 | 1.56 | kadry | RECOMMENDED WORKFLOW | Badania lekarskie po długim L4: kontrolne vs okresowe | `125` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 12 | 155.8 | 288 | 1.03 | KPiR | CONSIDER | Środki trwałe: jednorazowa amortyzacja vs koszty bezpośrednie | `49` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 13 | 149.6 | 271 | 1.06 | rachunkowość | CONSIDER | Sprawozdania finansowe do KRS/KAS: schematy i składanie | `21` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 14 | 142.7 | 248 | 1.17 | kadry | CONSIDER | Nagroda jubileuszowa po doniesieniu dokumentów do stażu pracy | `8` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 15 | 142.0 | 241 | 1.28 | ZUS | CONSIDER | Składka zdrowotna przy zmianie formy opodatkowania i odliczenia ZUS | `82` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 16 | 130.8 | 212 | 1.30 | kadry | CONSIDER | Potrącenia komornicze niealimentacyjne z wynagrodzeń i zleceń | `10` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 17 | 125.3 | 172 | 1.83 | ZUS | RECOMMENDED WORKFLOW | Zasiłek opiekuńczy ZUS: wypełnianie Z-15A i prawo do zasiłku | `98` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 18 | 120.7 | 170 | 1.64 | kadry | RECOMMENDED WORKFLOW | Akta osobowe: archiwizacja, układ i przechowywanie dokumentów | `15` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 19 | 120.1 | 179 | 1.43 | JPK | CONSIDER | Nowe oznaczenia JPK_VAT: BFK vs DI dla faktur WNT, importu i poza KSeF | `107` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 20 | 117.4 | 230 | 1.27 | software | CONSIDER | Wybór programu księgowego: KPiR, pełna księgowość, JDG i spółki | `143` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 21 | 116.2 | 198 | 0.85 | kadry | CONSIDER | Kursy i szkolenia kadrowo-płacowe dla początkujących | `138` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 22 | 115.2 | 179 | 1.18 | VAT | CONSIDER | VAT przy wykupie, sprzedaży i darowiźnie samochodu z firmy | `62` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 23 | 114.4 | 160 | 1.52 | kadry | RECOMMENDED WORKFLOW | Odbiór dnia wolnego za święto 1 listopada w sobotę | `34` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 24 | 108.0 | 159 | 1.22 | kadry | CONSIDER | Korekty list płac: ZUS, PIT-11 i PPK | `90` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 25 | 107.2 | 150 | 1.36 | PIT | CONSIDER | PIT: ulga na dziecko i rozliczenie samotnego rodzica - limity dochodów | `87` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 26 | 104.9 | 140 | 1.44 | kadry | CONSIDER | Zatrudnianie obywateli Ukrainy: formalności i dokumenty | `4` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 27 | 104.3 | 121 | 1.79 | kadry | RECOMMENDED WORKFLOW | Przejście roku: wynagrodzenie chorobowe vs zasiłek i okres zasiłkowy | `135` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 28 | 103.2 | 134 | 1.48 | rachunkowość | CONSIDER | Przejęcie księgowości: korekta błędnych sald rozrachunków z BO | `51` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 29 | 103.0 | 148 | 1.19 | JPK | CONSIDER | JPK_CIT: znaczniki kont i moment ich nadania | `30` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 30 | 101.5 | 156 | 0.95 | kadry | CONSIDER | Benefity pracownicze: oskładkowanie, opodatkowanie i księgowanie na liście płac | `24` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 31 | 101.4 | 109 | 1.89 | KSeF | RECOMMENDED WORKFLOW | KSeF: obieg, archiwizacja i weryfikacja faktur w biurze | `139` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 32 | 101.1 | 143 | 1.20 | VAT | CONSIDER | Najem prywatny a VAT, KSeF i JDG | `53` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 33 | 98.4 | 144 | 1.04 | PIT | CONSIDER | Ryczałt: dobór stawki wg rodzaju usługi (IT, hydraulik, catering, BHP, księgowość) | `48` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 34 | 97.5 | 123 | 1.42 | KPiR | CONSIDER | KPiR 2026: księgowanie faktur do paragonu i sprzedaży detalicznej | `110` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 35 | 96.2 | 100 | 1.81 | ZUS | RECOMMENDED WORKFLOW | Umowa zlecenie ze studentem/uczniem do 26 r.ż. - składki ZUS | `69` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 36 | 94.9 | 123 | 1.28 | VAT | CONSIDER | Powrót do zwolnienia VAT po podniesieniu limitu do 240 tys. | `94` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 37 | 94.7 | 137 | 0.99 | kadry | CONSIDER | Minimalne wynagrodzenie 2026: regulamin i składniki płacy | `71` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 38 | 92.3 | 153 | 0.56 | kadry | CONSIDER | Delegowanie i podróże służbowe pracowników za granicę: ZUS, podatek, A1 | `19` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 39 | 91.9 | 108 | 1.44 | ZUS | CONSIDER | ZUS Z-3: wynagrodzenie i zasiłek chorobowy przy firmach <20 pracowników | `134` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 40 | 90.8 | 102 | 1.50 | kadry | RECOMMENDED WORKFLOW | Rozliczanie wynagrodzeń wypłacanych w następnym miesiącu: koszty, ZUS, PIT | `74` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 41 | 90.2 | 105 | 1.41 | kadry | CONSIDER | Ustalanie podstawy wynagrodzenia chorobowego przy zmianach etatu i płacy | `130` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 42 | 89.4 | 98 | 1.51 | kadry | RECOMMENDED WORKFLOW | Limity umów na czas określony: 33 miesiące i 3 umowy | `113` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 43 | 88.8 | 102 | 1.40 | kadry | CONSIDER | Śmierć pracownika: wypłata wynagrodzenia, ekwiwalentu i odprawy pośmiertnej | `1` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 44 | 87.9 | 97 | 1.45 | ZUS | CONSIDER | ZUS Płatnik/PUE: błędy krytyczne przy wysyłce deklaracji i korekt DRA/RCA | `85` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 45 | 87.7 | 59 | 2.20 | KSeF | RECOMMENDED WORKFLOW | KSeF: panika klientów i przygotowanie biur rachunkowych | `109` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 46 | 87.3 | 90 | 1.57 | kadry | RECOMMENDED WORKFLOW | Rozwiązanie umowy: likwidacja stanowiska, porozumienie stron a zasiłek | `117` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 47 | 87.3 | 107 | 1.22 | PIT | CONSIDER | Ulga dla pracującego seniora: PIT-11 i rozliczenie | `75` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 48 | 86.3 | 91 | 1.50 | ZUS | CONSIDER | Zbieg tytułów ubezpieczeń przy umowach zlecenie | `83` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 49 | 86.2 | 83 | 1.65 | KSeF | RECOMMENDED WORKFLOW | KSeF: obowiązek dla nievatowców, zwolnionych z VAT i limitu 10 tys. | `111` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 50 | 85.7 | 89 | 1.51 | PIT | RECOMMENDED WORKFLOW | KUP i kwota zmniejszająca przy dwóch umowach o pracę | `92` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 51 | 85.5 | 79 | 1.70 | KSeF | RECOMMENDED WORKFLOW | KSeF: duplikaty faktur zakupowych i numer KSeF | `132` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 52 | 85.3 | 71 | 1.84 | kadry | RECOMMENDED WORKFLOW | Urlop wypoczynkowy przy kończącej się umowie i 14 dni ciągłych | `44` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 53 | 84.1 | 102 | 1.17 | KPiR | CONSIDER | Kaucje za butelki w KPiR i VAT (system kaucyjny) | `6` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 54 | 83.7 | 74 | 1.70 | rachunkowość | RECOMMENDED WORKFLOW | Rozliczanie sprzedaży Allegro: powiązanie wpłat z fakturami | `40` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 55 | 82.2 | 62 | 1.87 | kadry | RECOMMENDED WORKFLOW | Zwolnienia lekarskie L4: nietypowe sytuacje i brak e-ZLA | `124` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 56 | 81.7 | 65 | 1.78 | kadry | RECOMMENDED WORKFLOW | Umowa o pracę: data zawarcia a dzień rozpoczęcia pracy w dzień wolny | `59` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 57 | 81.2 | 116 | 0.74 | kadry | CONSIDER | Premie w podstawie wynagrodzenia chorobowego i urlopowego | `127` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 58 | 80.7 | 73 | 1.57 | kadry | RECOMMENDED WORKFLOW | Ustalanie okresu wypowiedzenia umowy o pracę wg stażu | `118` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 59 | 80.4 | 90 | 1.22 | ZUS | CONSIDER | ZUS: zaświadczenie o przychodach emerytów i rencistów do końca lutego | `84` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |
| 60 | 80.2 | 93 | 1.15 | VAT | CONSIDER | Odliczenie VAT i księgowanie posiłków oraz cateringu dla pracowników | `47` | `[WORKFLOW / SKIP / MERGE_WITH_#X]` |

---

## Szczegółowe karty klastrów (top 60)

## 1. KSeF: moment podatkowy, data wystawienia, korekty · MERGED (120, 121)

- **rank**: 1  **score**: 383.6  **cluster_id**: `merge[120+121]`
- **topic_area**: `KSeF`
- **size**: 838 postów
- **avg_comments**: 1.42
- **has_many_comments_ratio**: 0.52
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> (120) Pytania dotyczą prawidłowego ujęcia faktur korygujących wystawionych w KSeF w innym okresie niż faktura pierwotna - zwłaszcza korekt danych formalnych (NIP, nazwa, data sprzedaży) oraz korekt do zera. Księgowi mają wątpliwości, w którym miesiącu wykazać korektę w rejestrze VAT i JPK. 

(121) Pytania dotyczą tego, którą datę (wystawienia faktury, przesłania do KSeF, sprzedaży/wykonania usługi) należy przyjąć do rozliczenia VAT i ujęcia kosztu w KPiR, zwłaszcza gdy daty te przypadają na różne miesiące. Księgowi zastanawiają się nad prawidłowym momentem odliczenia VAT i zaksięgowania faktur kosztowych w kontekście KSeF.

**Keywords**: faktury, vat, fakturę, faktura, korekta, korektę, ksef, korekty, jpk, wystawiona  **Bigramy**: data wystawienia, jpk vat, faktura wystawiona, zrobić korektę, fakturę korygującą

**Przykładowe posty (z centroidu):**

1. `a49652cbee16` · ksiegowosc_moja_pasja · 2 komentarzy
   > Proszę o pomoc czy dobrze rozumiem. Faktura w ksef wystawiona w lutym, data nadania numeru ksef też luty. Ale faktura ta miała zostać skorygowana do zera. Korekta z datą wystawienia już marcową (data…

2. `ee1aeb71b3b3` · ksiegowosc_moja_pasja · 1 komentarzy
   > Cześć. Mam fakturę kosztową z grudnia ale były złe dane nabywcy(nazwa, nip, adres). Kontrahent zrobił korektę danych ale w styczniu. Jak to zaksięgować bo już się zgubiłam? Tą Pierwotną błędną w grudn…

3. `f49eb551594c` · ksiegowosc_moja_pasja · 0 komentarzy
   > Witam, Mam fakturę sprzedaży w styczniu ze złym NIP-em nabywcy. Czy w lutym mogę dokonać korekty danych formalnych czy muszę wyzerować już fakturę pierwotną do zera i wstawić nową?

---

## 2. Zaliczanie umów zlecenie i DG do stażu pracy od 2026

- **rank**: 2  **score**: 363.2  **cluster_id**: `7`
- **topic_area**: `kadry`
- **size**: 797 postów
- **avg_comments**: 1.22
- **has_many_comments_ratio**: 0.42
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą nowych zasad wliczania do stażu pracy okresów umów zlecenia (także studenckich) oraz prowadzenia działalności gospodarczej, a także wymaganych dokumentów (zaświadczenia z ZUS, US-7) potwierdzających te okresy.

**Keywords**: pracy, stażu, pracownik, lat, zlecenie, zaświadczenie, zus, okres, umowy, staż  **Bigramy**: stażu pracy, staż pracy, umowę zlecenie, umowy zlecenia, zaświadczenie zus

**Przykładowe posty (z centroidu):**

1. `5524fe102d29` · grupa_2_507801603233194 · 1 komentarzy
   > Chciałabym się dowiedzieć, czy okres pracy na umowie zlecenia wlicza się do stażu pracy. Obecnie pracuję na zleceniu i wcześniej też pracowałam w ten sposób, również w trakcie studiów licencjat i magi…

2. `075e641c91f8` · grupa_2_507801603233194 · 1 komentarzy
   > Czy do stażu pracy mogę doliczyć umowy zlecenie w czasie studiów z zaświadczeniem z 2008 r. że osoba była zatrudniona w danej firmie? Na umowach są rachunki.

3. `ecb07ec14ab2` · grupa_2_507801603233194 · 1 komentarzy
   > Zaliczenie umów do stażu pracy, czy samo zaświadczenie z ZUS wystarczy? Chodzi o pracownika który miał 30 lat kiedy pracował na umowie zlecenie

---

## 3. Wymiar urlopu wypoczynkowego przy niepełnym etacie i zmianie wymiaru

- **rank**: 3  **score**: 255.4  **cluster_id**: `45`
- **topic_area**: `kadry`
- **size**: 493 postów
- **avg_comments**: 1.91
- **has_many_comments_ratio**: 0.72
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą proporcjonalnego naliczania urlopu wypoczynkowego dla pracowników zatrudnionych na część etatu (1/2, 3/4, 5/8) oraz przeliczania dni i godzin urlopu przy zmianie wymiaru etatu w trakcie roku.

**Keywords**: dni, urlopu, urlop, pracownik, pracy, etatu, roku, zatrudniony, godzin, wymiar  **Bigramy**: dni urlopu, pracownik zatrudniony, urlopu wypoczynkowego, wymiar urlopu, urlopu dni

**Przykładowe posty (z centroidu):**

1. `452562129f68` · grupa_2_507801603233194 · 1 komentarzy
   > Pracownik w dniu 17.04.2026 nabywa prawo do 26 dni urlopu wypoczynkowego .Do końca grudnia 2025 zatrudniony był na pół etatu i z końca roku 2025 zostało mu do wykorzystania pół dnia to jest 4 godzin y…

2. `294da0fbc478` · grupa_2_507801603233194 · 2 komentarzy
   > Witam, Chciałam się dopytać, pracownikowi przysługuje urlop 26 dni na rok, jest zatrudniony na pół etatu więc proporcjonalnie 13 dni, ale pracuje od poniedziałku do piątku po 4 godziny dziennie. Jak r…

3. `2e4842adb815` · grupa_2_507801603233194 · 2 komentarzy
   > Dzień dobry, czy poniższe wyliczenie urlopu dla osoby zatrudnionej na 0.75 etatu od dnia 3 lutego 2025 do 31 grudnia 2025 jest prawidłowe? 26 dni x 0.75 etatu  = 19.5 ~ 20 dni 20 dni : 12 m-cy = 1,66…

---

## 4. Księgowanie faktur zagranicznych: WNT, import usług i towarów

- **rank**: 4  **score**: 215.1  **cluster_id**: `66`
- **topic_area**: `VAT`
- **size**: 427 postów
- **avg_comments**: 1.21
- **has_many_comments_ratio**: 0.37
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą prawidłowego rozliczenia VAT od faktur zakupowych od kontrahentów z UE i spoza UE, w tym klasyfikacji jako WNT, import usług lub import towarów w zależności od statusu VAT stron i miejsca dostawy.

**Keywords**: vat, fakturę, faktura, usług, import, nip, towar, kontrahenta, faktury, polski  **Bigramy**: import usług, stawka vat, taką fakturę, zakup towaru, odwrotne obciążenie

**Przykładowe posty (z centroidu):**

1. `1f86f654be0f` · ksiegowosc_moja_pasja · 2 komentarzy
   > Jak zaksięgować taką fakturę? Kupującym jest podatnik VAT.

2. `cd8d52f0b2b3` · ksiegowosc_moja_pasja · 1 komentarzy
   > Proszę o pomoc. Mam fakturę od media Markt. Sprzedawca - niemiecki numer vat id. Kupujacy polska firma czynny podatnik vat zarejestrowany do vat UE. Faktura po angielsku kwoty w złotówkach netto vat b…

3. `e41385475e6c` · ksiegowosc_moja_pasja · 1 komentarzy
   > Dzień dobry, proszę podpowiedzieć czy dobrze myślę   Faktura zakupu towaru od kontrahenta Niemieckiego z PL NIP. Towar dostarczony z Niemiec, stawka VAT na frze 0%. Traktuję to jako WNT, należny, nali…

---

## 5. Ewidencja i rozliczanie czasu pracy przy różnych systemach i wymiarach etatu

- **rank**: 5  **score**: 206.8  **cluster_id**: `35`
- **topic_area**: `kadry`
- **size**: 409 postów
- **avg_comments**: 1.16
- **has_many_comments_ratio**: 0.38
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rozliczania czasu pracy pracowników w systemach równoważnym i zadaniowym, ustalania grafików przy niepełnych etatach oraz identyfikacji i wypłaty nadgodzin wynikających z przekroczeń norm dobowych i tygodniowych.

**Keywords**: pracy, pracownik, godzin, czasu, etatu, nadgodziny, pracuje, pracę, dni, godziny  **Bigramy**: czasu pracy, czas pracy, system czasu, okres rozliczeniowy, poniedziałku piątku

**Przykładowe posty (z centroidu):**

1. `97809c5b23fd` · grupa_2_507801603233194 · 2 komentarzy
   > Jak ewidencjonujecie czas pracy pracowników którzy pracują 5dni w tyg. Pn-pt 9-17, sobota 8-14. Dzień wolny z tyt. 5dniowego tyg pracy ustalany na podstawie planu pracy. Jeśli pracownik przyjdzie w so…

2. `11d13afe2453` · grupa_2_507801603233194 · 5 komentarzy
   > Czy pracownik na 1/4 etatu może mieć ustalony grafik że pracuje 1 dzień w tygodniu np po 8-9 h? W zależności od miesiąca jaka liczba godzin do przepracowania wypada. I wyrabiając normalną liczbę h prz…

3. `c058063f53e0` · grupa_2_507801603233194 · 1 komentarzy
   > Jaki jest okres rozliczeniowe jaki w umowie jest zapis o limicie powyżej którego praca jest traktowana jako praca w godzinach nadliczbowych ?￼

---

## 6. Macierzyństwo: wnioski urlopowe, zasiłki, składki ZUS · MERGED (101, 102)

- **rank**: 6  **score**: 199.7  **cluster_id**: `merge[101+102]`
- **topic_area**: `kadry`
- **size**: 379 postów
- **avg_comments**: 1.40
- **has_many_comments_ratio**: 0.50
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> (101) Pytania dotyczą obsługi ZUS w trakcie i po zasiłku macierzyńskim — kodów zgłoszeniowych (ZZA/ZWUA), wykazywania pracownika na RCA/RSA, przerejestrowań oraz uprawnień do zasiłku przy umowie zleceniu, działalności gospodarczej i urlopie wychowawczym. 

(102) Pytania dotyczą zasad wnioskowania o urlop macierzyński i rodzicielski, w tym nieprzenoszalnej części 9 tygodni dla ojca, sytuacji gdy matka nie ma prawa do zasiłku oraz wymaganych dokumentów.

**Keywords**: zus, zasiłku, macierzyńskim, składki, macierzyński, urlopie, zasiłek, pracę, rca, macierzyńskiego  **Bigramy**: zasiłek macierzyński, urlopie macierzyńskim, zasiłku macierzyńskiego, urlopie wychowawczym, umowę zlecenie

**Przykładowe posty (z centroidu):**

1. `e2e4c21b97c0` · grupa_2_507801603233194 · 0 komentarzy
   > Jak wygląda sytuacja z zasiłkiem macierzyńskim osoby wykonującej zlecenie. Pani zgloszna do ub. chorobowego jakie dokumenty, czy w trakcie zasiłku macierzyńskiego dokonuje przerejestrowania w ZUS do s…

2. `b405f9c70a30` · ksiegowosc_moja_pasja · 2 komentarzy
   > Hej prowadzę działalność gospodarczą, urodziłam dziecko i złożyłam do ZUS - ZUS ZAM zawnioskował tam łącznie o macierzyński i rodzicielski 52 tyg. chciałam 81,5% czy muszę dodatkowo składać ZUS ZUR?

3. `7951e5a13cb1` · ksiegowosc_moja_pasja · 2 komentarzy
   > Hej prowadzę działalność gospodarczą, urodziłam dziecko i złożyłam do ZUS - ZUS ZAM zawnioskował tam łącznie o macierzyński i rodzicielski 52 tyg. chciałam 81,5%czy muszę dodatkowo składać ZUS ZUR?

---

## 7. Leasing samochodu osobowego: limity KUP i odliczenie VAT

- **rank**: 7  **score**: 192.4  **cluster_id**: `63`
- **topic_area**: `PIT`
- **size**: 359 postów
- **avg_comments**: 1.44
- **has_many_comments_ratio**: 0.52
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rozliczania rat leasingu operacyjnego samochodów osobowych — stosowania limitu 150/100 tys. zł w kosztach, proporcji 75%/100% oraz odliczenia VAT (50%/100%) przy użytku mieszanym lub zgłoszeniu VAT-26.

**Keywords**: leasingu, vat, leasing, samochód, wartość, tys, samochodu, koszty, kup, netto  **Bigramy**: samochód osobowy, leasing operacyjny, samochodu osobowego, wartość samochodu, celów mieszanych

**Przykładowe posty (z centroidu):**

1. `30ae43f4a41f` · ksiegowosc_moja_pasja · 2 komentarzy
   > Mam samochód osobowy który używam też prywatnie. Opłacam ratę leasingu operacyjnegoNie jestem na VAT Czy kwotę z faktury leasingowej można księgować w 100% czy 75% Są różne informacje na stronach gofi…

2. `12186b408679` · ksiegowosc_moja_pasja · 1 komentarzy
   > Samochód osobowy z leasingiem operacyjnym Wartość powyżej 100 tys brutto Zgłoszony do Vat-26 Czy leasing odliczam proporcje ? Czy jak?

3. `3552fcdae025` · ksiegowosc_moja_pasja · 2 komentarzy
   > Mam samochód osobowy który używam też prywatnie.  Opłacam ratę leasingu operacyjnego Nie jestem na VAT  Czy kwotę z faktury leasingowej można księgować w 100% czy 75%  Są różne informacje na stronach…

---

## 8. KSeF: nadawanie uprawnień podmiotom i certyfikaty dla biur rachunkowych

- **rank**: 8  **score**: 185.2  **cluster_id**: `99`
- **topic_area**: `KSeF`
- **size**: 337 postów
- **avg_comments**: 1.52
- **has_many_comments_ratio**: 0.59
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą problemów z nadawaniem i weryfikacją uprawnień w KSeF — zwłaszcza dla biur rachunkowych będących spółkami, logowania przez ZAW-FA/Profil Zaufany, generowania certyfikatów w MCU oraz braku widoczności faktur klientów po zalogowaniu.

**Keywords**: ksef, uprawnienia, faktur, uprawnień, certyfikat, certyfikaty, nip, zaw-fa, spółki, mcu  **Bigramy**: przeglądania faktur, nadać uprawnienia, biuro rachunkowe, profilem zaufanym, uprawnienia ksef

**Przykładowe posty (z centroidu):**

1. `e610a37393bf` · ksiegowosc_moja_pasja · 2 komentarzy
   > Spolka z o.o. Złożyliśmy ZAW-FA, po zalogowaniu sie do KSEF nie widzimy wystawionych na nas faktur. Czy musimy jeszcze cos zrobic?

2. `c23b89fa3f30` · ksiegowosc_moja_pasja · 0 komentarzy
   > Hej, szybkie pytanie. Biuro rachunkowe, ktore jest spółką ma nadane przez klientow uprawnienia dla podmiotu do przeglądania i wystawiania faktur. Prezes biura loguje sie do KSEF na NIP biura i uwierzy…

3. `b17dbe8eb5b8` · ksiegowosc_moja_pasja · 2 komentarzy
   > Dzień dobry, czy ktoś pomoże mi zrozumieć jak to ustrojstwo KSEF działa   pracuje w spółce, wysłałam ZAW-FA z danymi prezesa. Wczoraj Prezes się zalogował do ksef i nadał uprawnienia mi, jak mam spraw…

---

## 9. Roczne rozliczenia PIT: PIT-4R, PIT-11, korekty i przekazanie · MERGED (33, 86, 95)

- **rank**: 9  **score**: 180.7  **cluster_id**: `merge[33+86+95]`
- **topic_area**: `PIT`
- **size**: 329 postów
- **avg_comments**: 1.46
- **has_many_comments_ratio**: 0.53
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> (33) Pytania dotyczą rozbieżności między zaliczkami miesięcznymi wpłaconymi do US a kwotami wykazanymi w deklaracjach rocznych (PIT-4R, PIT-8AR, CIT-8, PIT-36), w tym nadpłat, niedopłat, odsetek za nieterminową wpłatę oraz ujęcia remanentu w zaliczce za grudzień. 

(86) Pytania dotyczą sytuacji, gdy w wysłanym PIT-11 znalazł się nieprawidłowy adres zamieszkania/zameldowania pracownika lub został on przekazany do niewłaściwego urzędu skarbowego, oraz czy w takich przypadkach konieczna jest korekta deklaracji. 

(95) Pytania dotyczą sposobu doręczania PIT-11 pracownikom (mail, poczta, e-Doręczenia, osobiście), konieczności podpisu (ręcznego lub kwalifikowanego) oraz potwierdzania odbioru formularza.

**Keywords**: zaliczki, podatek, roku, pit, podatku, opodatkowania, cit, odsetki, zmienić, grudzień  **Bigramy**: formę opodatkowania, zmienić formę, podatek dochodowy, formy opodatkowania, urzędu skarbowego

**Przykładowe posty (z centroidu):**

1. `06292268f946` · ksiegowosc_moja_pasja · 1 komentarzy
   > Cześć, potrzebuję podpowiedzi, bo już wszystko mi się miesza. Czy może być sytuacja taka w CIT-8, że należne zaliczki miesięczne są mniejsze od rocznej kwoty podatku?

2. `029555712a35` · ksiegowosc_moja_pasja · 1 komentarzy
   > Dzień dobry, jak wykazać w pit 4r nadpłaconą zaliczkę na podatek za grudzień? Czy zostanie zwrócona?

3. `2284d4842b6a` · grupa_2_507801603233194 · 0 komentarzy
   > W jednostce samorządowej przelewam podatek do US parę dni wcześniej i po zakończeniu roku mam nadpłatę w  pit4r.  Jak obliczać wysokość tej nadpłaty przed dokonaniem przelewu?

---

## 10. Mały ZUS Plus: ponowne skorzystanie po przerwie i nowe zasady od 2026

- **rank**: 10  **score**: 170.2  **cluster_id**: `79`
- **topic_area**: `ZUS`
- **size**: 306 postów
- **avg_comments**: 1.39
- **has_many_comments_ratio**: 0.46
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą warunków powrotu do ulgi Mały ZUS Plus po wykorzystaniu limitu 36/48 miesięcy, wpływu zawieszenia działalności oraz nowych zasad naliczania opartych o limit przychodu 120 tys. zł.

**Keywords**: zus, plus, mały, roku, działalność, małego, ulgi, stycznia, teraz, miesięcy  **Bigramy**: zus plus, mały zus, małego zus, małego zusu, ulgi start

**Przykładowe posty (z centroidu):**

1. `41ca3a49bde1` · ksiegowosc_moja_pasja · 1 komentarzy
   > Witam , mam taka zagwostke , przedsiębiorca od 2022 prowadzi działalność wykorzystał 6 miesięcy ulgi na start później 2 lata składek preferencyjnych i w 2025 opłacał duży ZUS przez 4 miesiące pozostał…

2. `e3c79fc941c6` · ksiegowosc_moja_pasja · 1 komentarzy
   > Mały zus plus Czy podatnik, który w poprzednim roku wykorzystał 12 mies małego ZUS plus może w 2026 roku nadal korzystać ? Termin styczniowy został przegapiony, dochodów w firmie nie ma już od kilku m…

3. `5a0807305ab1` · ksiegowosc_moja_pasja · 1 komentarzy
   > Mały zus plusCzy podatnik, który w poprzednim roku wykorzystał 12 mies małego ZUS plus może w 2026 roku nadal korzystać ? Termin styczniowy został przegapiony, dochodów w firmie nie ma już od kilku mi…

---

## 11. Badania lekarskie po długim L4: kontrolne vs okresowe

- **rank**: 11  **score**: 166.1  **cluster_id**: `125`
- **topic_area**: `kadry`
- **size**: 287 postów
- **avg_comments**: 1.56
- **has_many_comments_ratio**: 0.56
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą kierowania pracowników na badania profilaktyczne (kontrolne, okresowe, wstępne) po zwolnieniu lekarskim, utraty ważności badań w trakcie L4 oraz konsekwencji ich braku.

**Keywords**: badania, pracy, pracownik, kontrolne, lekarskie, okresowe, dni, skierowanie, pracownika, wstępne  **Bigramy**: badania kontrolne, badania lekarskie, badania okresowe, medycyny pracy, skierowanie badania

**Przykładowe posty (z centroidu):**

1. `561c829ae276` · grupa_2_507801603233194 · 2 komentarzy
   > Pracownica była na długim zwolnieniu lekarskim, w trakcie którego skończyła się ważność badań okresowych. Została skierowana tylko na badania kontrolne i wróciła do pracy. Czy to orzeczenie lekarskie…

2. `92b9e849018c` · grupa_2_507801603233194 · 1 komentarzy
   > Witam, Pracownik jest na zwolnieniu L4 po zabiegu równe 30 dni, czy powinniśmy skierować na badania lekarskie przed powrotem do pracy?

3. `41c5d40ccdef` · grupa_2_507801603233194 · 2 komentarzy
   > Hej, zatrudniłam zleceniobiorcę, w dniu zatrudnienia zrobił badania lekarskie wstępne. Następnego dnia odbył instruktaż stanowiskowy BHP. W kolejnym dniu poszedł na zwolnienie lekarskie. Czy w takim r…

---

## 12. Środki trwałe: jednorazowa amortyzacja vs koszty bezpośrednie

- **rank**: 12  **score**: 155.8  **cluster_id**: `49`
- **topic_area**: `KPiR`
- **size**: 288 postów
- **avg_comments**: 1.03
- **has_many_comments_ratio**: 0.33
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą kwalifikacji zakupów do środków trwałych, wyboru między jednorazową amortyzacją a ujęciem bezpośrednio w kosztach, ulepszeń oraz rozliczenia sprzedaży ŚT. Pojawiają się też wątki KŚT i amortyzacji mieszkania jako lokalu firmy.

**Keywords**: amortyzacji, środków, koszty, trwałych, środka, trwałego, tys, środek, wartość, zakup  **Bigramy**: środka trwałego, środków trwałych, środek trwały, środki trwałe, jednorazowej amortyzacji

**Przykładowe posty (z centroidu):**

1. `d28558e44602` · ksiegowosc_moja_pasja · 2 komentarzy
   > Czy musze ująć zakup jako jednorazowa amortyzacja czy moge wrzucić to bezpośrednio w koszty bez wykazu w ewid.środków trwałych?

2. `03f11e507249` · ksiegowosc_moja_pasja · 2 komentarzy
   > Co powinnam wpisać wypełniając pit-36L zal.B w kosztach ze sprzedaży środków trwałych: wartość niezamortyzowaną czy wartość początkową ?

3. `a75c246c7484` · ksiegowosc_moja_pasja · 1 komentarzy
   > Spółka cywilna przychód za rok 2025 około 8 milionów czy w 2026 mogę zamortyzować jednorazowo środek trwały o wartości 110 tysięcy netto?

---

## 13. Sprawozdania finansowe do KRS/KAS: schematy i składanie

- **rank**: 13  **score**: 149.6  **cluster_id**: `21`
- **topic_area**: `rachunkowość`
- **size**: 271 postów
- **avg_comments**: 1.06
- **has_many_comments_ratio**: 0.39
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą sporządzania i wysyłki sprawozdań finansowych za 2025 rok - wyboru wersji schematu (1.3 vs 2.1), sposobu składania do KRS/KAS oraz dołączania uchwał i dokumentów towarzyszących.

**Keywords**: sprawozdanie, krs, sprawozdania, finansowe, spółka, roku, spółki, rok, zrobić, uchwały  **Bigramy**: sprawozdanie finansowe, sprawozdania finansowego, rok obrotowy, pierwszy raz, trakcie roku

**Przykładowe posty (z centroidu):**

1. `c7ad127f9296` · ksiegowosc_moja_pasja · 0 komentarzy
   > Witam,Czy w przypadku spolki z o.o. za 2025 mozna sporządzić sprawozdanie w wersji 1.3 czy trzeba poczekać aż KRS umożliwi wysyłkę wersji 2.1?

2. `0eb0e6142629` · ksiegowosc_moja_pasja · 0 komentarzy
   > Witam, Czy w przypadku spolki z o.o. za 2025 mozna sporządzić sprawozdanie w wersji 1.3 czy trzeba poczekać aż KRS umożliwi wysyłkę wersji 2.1?

3. `214f7d8d83d7` · ksiegowosc_moja_pasja · 0 komentarzy
   > Czy sprawozdania do KRS w tym roku skladaliscie normalnie przez S24? Bo mam jakiś dziwny komunikat że przeniesiono do jakiś e- formularzy.

---

## 14. Nagroda jubileuszowa po doniesieniu dokumentów do stażu pracy

- **rank**: 14  **score**: 142.7  **cluster_id**: `8`
- **topic_area**: `kadry`
- **size**: 248 postów
- **avg_comments**: 1.17
- **has_many_comments_ratio**: 0.43
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą wypłaty nagrody jubileuszowej dla pracowników samorządowych, którzy w trakcie zatrudnienia dostarczyli zaświadczenia z ZUS (umowy zlecenia, działalność gospodarcza) zwiększające ich staż pracy wstecz. Księgowi pytają, czy należy wypłacić jubileuszówkę za wyższy próg stażowy i czy nie minął termin.

**Keywords**: lat, pracy, pracownik, nagrodę, nagrody, wypłacić, nagroda, stażu, zus, staż  **Bigramy**: lat pracy, nagrodę jubileuszową, stażu pracy, nagrody jubileuszowej, nagroda jubileuszowa

**Przykładowe posty (z centroidu):**

1. `0523754dde22` · grupa_2_507801603233194 · 2 komentarzy
   > Witam, Potrzebuję pomocy. Pracownik samorządowy mając 19 lat i 5 miesięcy stażu pracy dostarczył dokumenty z ZUS potwierdzające opłacenia składek na umowie zlecenie. Po przeliczeniu stażu wyszło 23 la…

2. `23d9b6e78aaf` · grupa_2_507801603233194 · 0 komentarzy
   > Dzień dobry, pytanko pracownik zatrudniony  1.11.2023 r., posiada na starcie staż pracy wynoszący 25 lat i 4 miesiące (pracownik samorządowy ). W styczniu tego roku dostarcza zaświadczenia z ZUS o pro…

3. `667a7375cf31` · grupa_2_507801603233194 · 0 komentarzy
   > Dzień dobry, mam pytanie: Pracownik został zatrudniony 1.12.2025r.   w jednostce samorządowej wtedy jego staż pracy wynosił 15 lat i 3 miesiące.  2.04.2026 r.   doniósł zaświadczenie z zus z umów zlec…

---

## 15. Składka zdrowotna przy zmianie formy opodatkowania i odliczenia ZUS

- **rank**: 15  **score**: 142.0  **cluster_id**: `82`
- **topic_area**: `ZUS`
- **size**: 241 postów
- **avg_comments**: 1.28
- **has_many_comments_ratio**: 0.39
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą ustalania podstawy i wysokości składki zdrowotnej (głównie na ryczałcie i po zmianie formy opodatkowania) oraz zasad odliczania zapłaconych składek społecznych i zdrowotnych w DRA, KPiR i rozliczeniu rocznym.

**Keywords**: składki, zdrowotnej, zus, zdrowotna, roku, składka, dra, ryczałcie, składkę, przychód  **Bigramy**: składki zdrowotnej, składka zdrowotna, składki społeczne, formy opodatkowania, składkę zdrowotną

**Przykładowe posty (z centroidu):**

1. `0b01e4223296` · ksiegowosc_moja_pasja · 1 komentarzy
   > Przychód do składki zdrowotnej na ryczałcie. Czy można co miesiąc w DRA wykazywać “surowy” przychód, a dopiero w rocznym rozliczeniu składki zdrowotnej odjąć zapłacone składki społeczne za cały rok?

2. `0056919e3bcb` · ksiegowosc_moja_pasja · 1 komentarzy
   > Przychód do składki zdrowotnej na ryczałcie.Czy można co miesiąc w DRA wykazywać “surowy” przychód, a dopiero w rocznym rozliczeniu składki zdrowotnej odjąć zapłacone składki społeczne za cały rok?

3. `c0ba34d89e7d` · ksiegowosc_moja_pasja · 2 komentarzy
   > Witam. przy zmianie formy  z zasad na ryczałt obliczajac podatek za styczeń można odjąć składki społeczne oraz 50% zdrowotnej zapłaconej w styczniu za grudzień  na skali?

---

## 16. Potrącenia komornicze niealimentacyjne z wynagrodzeń i zleceń

- **rank**: 16  **score**: 130.8  **cluster_id**: `10`
- **topic_area**: `kadry`
- **size**: 212 postów
- **avg_comments**: 1.30
- **has_many_comments_ratio**: 0.49
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą zasad dokonywania zajęć komorniczych niealimentacyjnych: obliczania kwot potrąceń, stosowania kwoty wolnej, traktowania umów zlecenia, zasiłków, 13-stek oraz świadczeń z ZFŚS.

**Keywords**: pracownik, wynagrodzenia, zajęcie, komornika, wynagrodzenie, komornicze, pracownika, pracę, kwota, kwotę  **Bigramy**: zajęcie komornicze, kwota wolna, zajęcie wynagrodzenia, najniższą krajową, komornicze niealimentacyjne

**Przykładowe posty (z centroidu):**

1. `415cc82e63d3` · grupa_2_507801603233194 · 0 komentarzy
   > Dzień dobry, pomóżcie proszę. Mamy pracownika z zajęciem niealimentacyjnym. W grudniu wypłacamy świadczenie z ZFŚS, nagrodę i wynagrodzenie. Czy z każdej wypłacanej kwoty muszę odliczyć osobno potrące…

2. `8ad9d2380b5b` · grupa_2_507801603233194 · 3 komentarzy
   > Proszę o poradę.Dziś przyszło pismo od komornika. Pracownik ma umowę zlecenie.  Zarabia Ok 1700 z brutto. To moje pierwsze zajęcie komornicze od strony płacowej . Wyczytałam, że przy umowie zleceniu m…

3. `f73ebf4734cf` · grupa_2_507801603233194 · 3 komentarzy
   > Proszę o poradę. Dziś przyszło pismo od komornika. Pracownik ma umowę zlecenie. Zarabia Ok 1700 z brutto. To moje pierwsze zajęcie komornicze od strony płacowej . Wyczytałam, że przy umowie zleceniu m…

---

## 17. Zasiłek opiekuńczy ZUS: wypełnianie Z-15A i prawo do zasiłku

- **rank**: 17  **score**: 125.3  **cluster_id**: `98`
- **topic_area**: `ZUS`
- **size**: 172 postów
- **avg_comments**: 1.83
- **has_many_comments_ratio**: 0.71
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą ustalania prawa do zasiłku opiekuńczego na chore lub zdrowe dziecko oraz sposobu wypełniania wniosku Z-15A w sytuacjach takich jak obecność drugiego rodzica w domu, urlop macierzyński współmałżonka, ferie czy weekendy w okresie zwolnienia.

**Keywords**: dziecko, dni, pracownik, opiekę, zasiłek, opieki, dzieckiem, zwolnienie, opiekuńczy, opieka  **Bigramy**: zasiłek opiekuńczy, dni opieki, opiekę dziecko, drugi rodzic, opieki dziecko

**Przykładowe posty (z centroidu):**

1. `36c28597c058` · grupa_2_507801603233194 · 4 komentarzy
   > Pracownik zlozyl z15 na chore dziecko, ktore nie ma dwoch lat. Zaznaczyl w nim, ze drugi rodzic dziecka nie pracuje. Czy w takim wypadku nalezy sie zasilek? Czy to bedzie nieobecnosc usprawiedliwona n…

2. `381844d9c99f` · grupa_2_507801603233194 · 2 komentarzy
   > Witajcie, pracownik otrzymał zwolnienie lekarskie z tytułu choroby dziecka na 3 dni. Jego żona przebywa aktualnie na zasiłku macierzyńskim na ich drugie młodsze dziecko. Czy w Z15A wpisują że żona pra…

3. `8f5bd5a7865b` · grupa_2_507801603233194 · 2 komentarzy
   > Dzień dobry, czy pracownik może dostać zasiłek opiekuńczy na dziecko 7 letnie, jeśli zwolnienie od lekarza przypada na okres ferii zimowych?

---

## 18. Akta osobowe: archiwizacja, układ i przechowywanie dokumentów

- **rank**: 18  **score**: 120.7  **cluster_id**: `15`
- **topic_area**: `kadry`
- **size**: 170 postów
- **avg_comments**: 1.64
- **has_many_comments_ratio**: 0.65
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą prowadzenia akt osobowych pracowników - gdzie wpinać poszczególne dokumenty (ZUS, listy płac, badania lekarskie), jak je archiwizować, numerować oraz postępować przy ponownym zatrudnieniu.

**Keywords**: akt, osobowych, pracy, dokumenty, aktach, pracownik, części, pracownika, akta, lat  **Bigramy**: akt osobowych, aktach osobowych, części akt, czasu pracy, akta osobowe

**Przykładowe posty (z centroidu):**

1. `82ca2d6b9331` · grupa_2_507801603233194 · 0 komentarzy
   > Dzień dobry, mam pytanie czy jeśli w aktach pracowników zatrudnionionych wiele lat temu znajdują się kserokopie dowodów osobistych to usuwacie je i na spisie dodajecie adnotację ' usunięto w akt '? Cz…

2. `793836ed614b` · grupa_2_507801603233194 · 2 komentarzy
   > Cześć, jestem początkującą kadrową, zostałam sama w pracy i czeka mnie wiele wyzwań.Jednym z nich jest archiwizacja dokumentów. Czy listy obecności oraz karty wynagrodzeniem z całego okresu zatrudnien…

3. `ef7d56d7c537` · grupa_2_507801603233194 · 2 komentarzy
   > Cześć, jestem początkującą kadrową, zostałam sama w pracy i czeka mnie wiele wyzwań. Jednym z nich jest archiwizacja dokumentów. Czy listy obecności oraz karty wynagrodzeniem z całego okresu zatrudnie…

---

## 19. Nowe oznaczenia JPK_VAT: BFK vs DI dla faktur WNT, importu i poza KSeF

- **rank**: 19  **score**: 120.1  **cluster_id**: `107`
- **topic_area**: `JPK`
- **size**: 179 postów
- **avg_comments**: 1.43
- **has_many_comments_ratio**: 0.51
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą prawidłowego stosowania nowych znaczników BFK i DI w ewidencji JPK_VAT od lutego 2026 dla faktur WNT, importu usług, faktur wystawianych poza KSeF oraz paragonów z NIP. Użytkownicy mają sprzeczne informacje co do tego, które dokumenty oznaczać którym kodem i od kiedy.

**Keywords**: bfk, ksef, jpk, faktury, vat, faktura, oznaczenie, oznaczenia, usług, sprzedaży  **Bigramy**: jpk vat, import usług, poza ksef, oznaczenie bfk, jpk bfk

**Przykładowe posty (z centroidu):**

1. `8df09435d3e5` · ksiegowosc_moja_pasja · 3 komentarzy
   > Jakie oznaczenie w Ewidencji zakupu i sprzedaży dla faktury WNT? BFK czy DI - mamy sprzeczne informacj

2. `253ca9d7afea` · ksiegowosc_moja_pasja · 1 komentarzy
   > Dzień dobry. Proszę bo się zgubiłem. Faktury unijne i eksportowe sprzedaż i zakup oznaczany DI, faktury,  które wchodzą do ksef od kwietnia zakup i sprzedaż oznaczamy BFK?

3. `b6ee496c7a6a` · ksiegowosc_moja_pasja · 1 komentarzy
   > Faktury sprzedaży dla osób fizycznych wystawione do paragonu fiskalnego ( w jpk oznaczenie FP) nie wysyłane do KSEF.  Jaki kod od lutego w JPK-VAT?  Pasuje mi tu DI.

---

## 20. Wybór programu księgowego: KPiR, pełna księgowość, JDG i spółki

- **rank**: 20  **score**: 117.4  **cluster_id**: `143`
- **topic_area**: `software`
- **size**: 230 postów
- **avg_comments**: 1.27
- **has_many_comments_ratio**: 0.44
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Użytkownicy proszą o rekomendacje programów do prowadzenia księgowości (JDG, spółek, pełnej księgowości, ryczałtu) z uwzględnieniem ceny, funkcjonalności, obsługi JPK/KSeF oraz pracy stacjonarnej lub w chmurze.

**Keywords**: program, programu, jaki, ksef, faktur, polecacie, dziękuję, prowadzenia, kpir, jdg  **Bigramy**: jaki program, program księgowy, góry dziękuję, program polecacie, możecie polecić

**Przykładowe posty (z centroidu):**

1. `9484dbacac32` · ksiegowosc_moja_pasja · 0 komentarzy
   > Dzień dobry, Czy  poleci ktoś w miarę tani i przyjemny program do prowadzenia księgowości dwóch firm, jedna z nich jest Vatowcem, więc z możliwością wysyłki JPK.  Z góry dziękuję za wszelkie polecenia…

2. `7cf2a48d6244` · ksiegowosc_moja_pasja · 0 komentarzy
   > Dzień dobry,Czy  poleci ktoś w miarę tani i przyjemny program do prowadzenia księgowości dwóch firm, jedna z nich jest Vatowcem, więc z możliwością wysyłki JPK. Z góry dziękuję za wszelkie polecenia.

3. `1d21ee1e6385` · ksiegowosc_moja_pasja · 2 komentarzy
   > Możecie polecić jakiś prosty w obsłudze i czytelny program do pełnej księgowości? Chodzi mi o to, żeby działał stacjonarnie a nie w chmurze . Z góry dziękuję

---

## 21. Kursy i szkolenia kadrowo-płacowe dla początkujących

- **rank**: 21  **score**: 116.2  **cluster_id**: `138`
- **topic_area**: `kadry`
- **size**: 198 postów
- **avg_comments**: 0.85
- **has_many_comments_ratio**: 0.31
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rekomendacji kursów i szkoleń z zakresu kadr i płac – stacjonarnych, online, weekendowych, w tym szkoleń z Płatnika oraz dla konkretnych lokalizacji i branż (np. sfera budżetowa).

**Keywords**: kurs, szkolenie, szkolenia, kadr, polecacie, online, płac, ksef, szukam, kadry  **Bigramy**: kadr płac, kadry płace, zrobić kurs, szukam kursu, najlepiej online

**Przykładowe posty (z centroidu):**

1. `3228711a33d8` · ksiegowosc_moja_pasja · 1 komentarzy
   > Dzień dobry. Czy możecie zaproponować jakiś kurs / szkolenie dla początkującej osoby w zakresie kadr i płac? Polecacie kogoś szczególnie ?

2. `0487e237dac3` · ksiegowosc_moja_pasja · 0 komentarzy
   > Witam, gdzie polecacie kurs/ szkolenie kadry i płace (kompletne) we Wrocławiu, najlepiej stacjonarnie?  Z góry dziękuję za konkretne i sprawdzone sugestie

3. `b9857a4d6159` · grupa_2_507801603233194 · 0 komentarzy
   > Witam. Gdzie warto  zrobić Kurs  kadry i płace dla początkujących ? Najlepiej online z certyfikatem

---

## 22. VAT przy wykupie, sprzedaży i darowiźnie samochodu z firmy

- **rank**: 22  **score**: 115.2  **cluster_id**: `62`
- **topic_area**: `VAT`
- **size**: 179 postów
- **avg_comments**: 1.18
- **has_many_comments_ratio**: 0.35
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą skutków VAT przy wykupie samochodu z leasingu, przekazaniu na cele prywatne, darowiźnie oraz sprzedaży auta firmowego, w tym sprzedaży w procedurze VAT marża.

**Keywords**: vat, samochód, auto, leasingu, samochodu, sprzedaży, auta, sprzedać, jdg, roku  **Bigramy**: vat marża, środków trwałych, samochodu osobowego, fakturę vat, środki trwałe

**Przykładowe posty (z centroidu):**

1. `d43a1bec6705` · ksiegowosc_moja_pasja · 2 komentarzy
   > Potwierdźcie proszę ze dobrze mysle bo czytam i czytam i się zakręciłam już  Przy wykupie samochodu osobowego z leasingu  operacyjnego (faktura na firmę, bo bank nie wystawi na osobe prywatną)jeżeli n…

2. `a1e8ceb1e6f3` · ksiegowosc_moja_pasja · 2 komentarzy
   > Potwierdźcie proszę ze dobrze myslebo czytam i czytam i się zakręciłam już Przy wykupie samochodu osobowego z leasingu  operacyjnego (faktura na firmę, bo bank nie wystawi na osobe prywatną)jeżeli nie…

3. `6664543ff8bd` · ksiegowosc_moja_pasja · 1 komentarzy
   > witam, klient wykupił samochód z leasingu na firmę ale nie odliczył VATu tylko wprowadził do środków trwałych. Czy może go darować ojcu bez odprowadzenia od tej czynności VATu? Skoro przy zakupie nie…

---

## 23. Odbiór dnia wolnego za święto 1 listopada w sobotę

- **rank**: 23  **score**: 114.4  **cluster_id**: `34`
- **topic_area**: `kadry`
- **size**: 160 postów
- **avg_comments**: 1.52
- **has_many_comments_ratio**: 0.57
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą zasad udzielania i odbioru dnia wolnego za święto przypadające w sobotę (głównie 1 listopada) w różnych sytuacjach pracowniczych: powrót z urlopu, zwolnienie lekarskie, nowe zatrudnienie, niepełny etat czy zmiana okresu rozliczeniowego.

**Keywords**: wolny, pracownik, listopada, pracy, dnia, święto, wolnego, należy, wolne, sobotę  **Bigramy**: dnia wolnego, odbiór dnia, czasu pracy, okres rozliczeniowy, wolnego święto

**Przykładowe posty (z centroidu):**

1. `e3d63dee2474` · grupa_2_507801603233194 · 2 komentarzy
   > Witam. Czy za Święto Wszystkich Świętych, które przypada w sobotę można odebrać dzień wolny w inny dzień. Czyli jako dodatkowy dzien wolny który nie wpływa na wypłatę?

2. `d33ca1dcb346` · grupa_2_507801603233194 · 2 komentarzy
   > Witam, powrót w grudniu z urlopu rodzicielskiego, trzymiesięczny okres rozliczeniowy październik-grudzień. Czy należy udzielić wolnego za 01.11?

3. `c7df6857a89e` · grupa_2_507801603233194 · 2 komentarzy
   > Pracownica wraca z urlopu wychowawczego 6 listopada. 10 listopada jest ustalonym dniem wolnym za święto przypadające w sobotę (1 listopada). Czy pracownicy również przysługuje ten dzień wolny? Może po…

---

## 24. Korekty list płac: ZUS, PIT-11 i PPK

- **rank**: 24  **score**: 108.0  **cluster_id**: `90`
- **topic_area**: `kadry`
- **size**: 159 postów
- **avg_comments**: 1.22
- **has_many_comments_ratio**: 0.41
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą sposobu przeprowadzania korekt wynagrodzeń pracowników (nadpłaty, niedopłaty, błędne zasiłki, przekroczenie 30-krotności) oraz wpływu tych korekt na deklaracje ZUS, PIT-11 i składki PPK.

**Keywords**: pracownik, zus, płac, wynagrodzenie, korektę, teraz, zrobić, pit, wynagrodzenia, pracownika  **Bigramy**: listy płac, zrobić korektę, liście płac, pracownik miał, korekta listy

**Przykładowe posty (z centroidu):**

1. `d9766c664d17` · grupa_2_507801603233194 · 1 komentarzy
   > Dzień dobry. Taka sytuacja, kadrowa wprowadziła ppk i naliczało za dwa miesiące poprzednie  i okey ale coś się w systemie przestawiło i na poprzednią wypłatę zostało to usunięte mimo że jest cały czas…

2. `dce1f3c18fbd` · grupa_2_507801603233194 · 0 komentarzy
   > Mam pracownika któremu w 2025 robiłam korektę za grudzień 2024 z powodu przekroczenia 30 krotności ZUS, zrobiłam korekty w platniku. Pracownik z tego tytułu miał zwrot . Generuje mu pit 11 i kwotę któ…

3. `10e13c9cb919` · grupa_2_507801603233194 · 0 komentarzy
   > Czy jeśli zauważyłam błędnie zaliczone wynagrodzenie (za dużo) to robić korektę. Bym musiała robić korektę wypłaty, składek ZUS, pitu, naliczenia zwolnienia lekarskiego które było w następnych miesiąc…

---

## 25. PIT: ulga na dziecko i rozliczenie samotnego rodzica - limity dochodów

- **rank**: 25  **score**: 107.2  **cluster_id**: `87`
- **topic_area**: `PIT`
- **size**: 150 postów
- **avg_comments**: 1.36
- **has_many_comments_ratio**: 0.48
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą warunków skorzystania z ulgi prorodzinnej na jedno dziecko oraz rozliczenia jako samotnie wychowujący rodzic, w kontekście limitów dochodów rodziców (56/112 tys.) i dochodów pełnoletniego uczącego się dziecka.

**Keywords**: dziecko, dzieci, ulgę, ulgi, rozliczyć, pit, jedno, dochód, odliczyć, tys  **Bigramy**: jedno dziecko, ulgę dziecko, ulgi dziecko, samotnie wychowująca, odliczyć ulgę

**Przykładowe posty (z centroidu):**

1. `94192d8158d7` · ksiegowosc_moja_pasja · 1 komentarzy
   > mam pytanie odnośnie ulgi na dziecko. Czy w przypadku gdy dziecko przekroczyło dochody, to matka może się mimo to rozliczyć jako "samotnie wychowujący " rodzic czy te zarobki dziecka dyskwalifikują za…

2. `000cc56a2819` · ksiegowosc_moja_pasja · 2 komentarzy
   > Czy mogę rozliczyć się jako rodzic samotnie wychowujący dziecko i nie stosować ulgi na dziecko gdy:- jestem panną- nie przekroczyłam dochodu 112 tyś.- dziecko przekroczyło dochód 22.546,92- dziecko ma…

3. `366ba8fe9540` · ksiegowosc_moja_pasja · 2 komentarzy
   > Witam, jak to jest z limitem na jedno dziecko:- tata ryczałt przychód 35 tys. - mama etat dochód 64 tys.Czy mama może w pit-37 rozliczyć całą ulgę na dziecko czy jednak nie?

---

## 26. Zatrudnianie obywateli Ukrainy: formalności i dokumenty

- **rank**: 26  **score**: 104.9  **cluster_id**: `4`
- **topic_area**: `kadry`
- **size**: 140 postów
- **avg_comments**: 1.44
- **has_many_comments_ratio**: 0.52
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą obowiązków pracodawcy przy zatrudnianiu obywateli Ukrainy — wymaganych dokumentów (paszport, karta pobytu, PESEL UKR), powiadomienia urzędu pracy oraz legalizacji zatrudnienia na umowę o pracę i zlecenie.

**Keywords**: ukrainy, pracy, pobytu, pobyt, zatrudnić, pracę, obywatela, umowę, pesel, pracownik  **Bigramy**: obywatela ukrainy, kartę pobytu, pobyt czasowy, powierzeniu pracy, obywatel ukrainy

**Przykładowe posty (z centroidu):**

1. `36461de6eb85` · grupa_2_507801603233194 · 1 komentarzy
   > Chcemy zatrudnić Ukraińca. Posiada kartę pobytu. Przyjechał do Polski przed wybuchem wojny. W tym przypadku wystarczy powiadomienie o powierzeniu pracy do urzędu pracy?

2. `b120abcc50bb` · grupa_2_507801603233194 · 0 komentarzy
   > Witam, mam pytanie zatrudniajac obywatela Ukrainy na umowę o pracę na czas określony czy oprócz wysłania powiadomienia o powierzeniu pracy do urzędu pracy jeszcze jakieś formalności są?

3. `26a76ed00a81` · grupa_2_507801603233194 · 1 komentarzy
   > Kochani mam pytanie, jakie obowiązki spoczywają na pracodawcy zatrudniającym Ukraincow? Pracownik został zgłoszony o podjęciu pracy, mamy skan paszportu-czy coś jeszcze należy posiadać, na dowód , że…

---

## 27. Przejście roku: wynagrodzenie chorobowe vs zasiłek i okres zasiłkowy

- **rank**: 27  **score**: 104.3  **cluster_id**: `135`
- **topic_area**: `kadry`
- **size**: 121 postów
- **avg_comments**: 1.79
- **has_many_comments_ratio**: 0.65
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rozliczania chorobowego na przełomie roku — czy pracownikowi po 1 stycznia naliczać ponownie 33 dni wynagrodzenia chorobowego czy kontynuować zasiłek z ZUS, oraz jak liczyć okres zasiłkowy przy przerwach w zwolnieniach.

**Keywords**: dni, pracownik, chorobowe, zwolnienie, wynagrodzenie, zasiłek, okres, chorobowego, pracy, stycznia  **Bigramy**: wynagrodzenie chorobowe, okres zasiłkowy, zwolnienie lekarskie, pracownik zatrudniony, wynagrodzenia chorobowego

**Przykładowe posty (z centroidu):**

1. `2a4600d92b3c` · grupa_2_507801603233194 · 1 komentarzy
   > Hej, proszę o pomoc, czy dobrze rozumiem.  Pracownik w 2024 roku miał wypłacony zasiłek chorobowy od 28-31 grudnia. W 2025 roku zachorował od 10-25 lutego. Będzie wypłacony zasiłek czy wynagrodzenie c…

2. `e339fb47a3f9` · grupa_2_507801603233194 · 1 komentarzy
   > Witam, proszę o podpowiedź:pracownik od 21.12.2025r. do 13.01.2026r na zasiłku chorobowym ( płatne z ZUS). Jeśli przedłuży zwolnienie od 14.01.2026 to będzie mial wynagrodzenie chorobowe ( nowe 33 dni…

3. `8e561a1c6609` · grupa_2_507801603233194 · 3 komentarzy
   > Dzień dobry,Proszę o pomoc. Jak liczyć okres zasiłkowy jeśli pracownik był na zasiłku do 19.12.2025 (krótka przerwa) a od 5 stycznia 2026 znowu poszedł na zwolnienie? W styczniu wypłacam wynagrodzenie…

---

## 28. Przejęcie księgowości: korekta błędnych sald rozrachunków z BO

- **rank**: 28  **score**: 103.2  **cluster_id**: `51`
- **topic_area**: `rachunkowość`
- **size**: 134 postów
- **avg_comments**: 1.48
- **has_many_comments_ratio**: 0.59
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą sposobu wyjaśnienia i wyksięgowania nieprawidłowych sald kont rozrachunkowych (z dostawcami, US, kontrahentami UE, kasą) przejętych po poprzednim biurze rachunkowym. Księgowi pytają, czy zostawić stare salda, zaksięgować w przychody/wynik finansowy, czy robić PK korygujące bilans otwarcia.

**Keywords**: roku, saldo, salda, konta, kasy, spółki, faktury, zrobić, lat, mogę  **Bigramy**: koniec roku, poprzednia księgowa, góry dziękuję, błędne saldo, konta firmowego

**Przykładowe posty (z centroidu):**

1. `a969b859ea15` · ksiegowosc_moja_pasja · 1 komentarzy
   > Witam, przejęłam klienta sp. z o. o. i mam pytanie. Co robicie z saldami zobowiązań z dostawcami wiszącymi z poprzednich lat typu paliwo, czy inne zakupy, które wiadomo, że zostały zapłacone. Zostawia…

2. `240cb8020895` · ksiegowosc_moja_pasja · 1 komentarzy
   > Witam,przejęłam klienta sp. z o. o. i mam pytanie.Co robicie z saldami zobowiązań z dostawcami wiszącymi z poprzednich lat typu paliwo, czy inne zakupy, które wiadomo, że zostały zapłacone.Zostawiacie…

3. `243ab8694a0e` · ksiegowosc_moja_pasja · 2 komentarzy
   > Witam,Nasze biuro Przejęło Księgowość spółki od tego roku. Weryfikując rozrachunki znalazłam, ze brakuje sporo dostarczonych faktur do płatności oraz mniej pozycji ale jednak brakuje płatności do zaks…

---

## 29. JPK_CIT: znaczniki kont i moment ich nadania

- **rank**: 29  **score**: 103.0  **cluster_id**: `30`
- **topic_area**: `JPK`
- **size**: 148 postów
- **avg_comments**: 1.19
- **has_many_comments_ratio**: 0.41
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą oznaczania kont (znaczników podatkowych, KUP/NKUP, kont pozabilansowych) na potrzeby JPK_KR_PD/JPK_CIT — kiedy je nadać, jak działają w programach (Optima, Rewizor) oraz jak łączyć analitykę bilansową z ewidencją podatkową.

**Keywords**: jpk, znaczniki, kont, konta, cit, nkup, znaczników, konto, znacznik, kontach  **Bigramy**: jpk cit, plan kont, planu kont, znaczniki kont, kup nkup

**Przykładowe posty (z centroidu):**

1. `3dc4a416a54c` · ksiegowosc_moja_pasja · 2 komentarzy
   > Znaczniki kont do JPK-KR-PDCzy znaczniki kont na potrzeby JPK-KR-PD trzeba mieć już faktycznie przypisane PRZED dokonaniem księgowań dot. 2026?Czy nie można zrobić później? Przecież JPK-KR-PD będzie s…

2. `2b710f6a5899` · ksiegowosc_moja_pasja · 2 komentarzy
   > Znaczniki kont do JPK-KR-PD Czy znaczniki kont na potrzeby JPK-KR-PD trzeba mieć już faktycznie przypisane PRZED dokonaniem księgowań dot. 2026? Czy nie można zrobić później? Przecież JPK-KR-PD będzie…

3. `8448b8c35671` · ksiegowosc_moja_pasja · 0 komentarzy
   > Jpk KR PD Optima Hej, proszę dajcie znać  1. Czy jeśli w trakcie roku 2026 dopiero nadam znaczniki to czy Optima poprawnie wygeneruje JPK ? 2. Jeśli nie to możecie mi prosto wyjaśnić jak działają znac…

---

## 30. Benefity pracownicze: oskładkowanie, opodatkowanie i księgowanie na liście płac

- **rank**: 30  **score**: 101.5  **cluster_id**: `24`
- **topic_area**: `kadry`
- **size**: 156 postów
- **avg_comments**: 0.95
- **has_many_comments_ratio**: 0.29
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rozliczania pakietów medycznych, kart sportowych (Multisport, Pluxee) oraz ubezpieczeń grupowych finansowanych lub współfinansowanych przez pracodawcę — kwestii naliczania ZUS, podatku, PPK oraz ujęcia na liście płac i w księgach, w tym finansowania z ZFŚS.

**Keywords**: pracownika, pracownik, pracodawca, multisport, pracowników, składki, ppk, netto, zus, karty  **Bigramy**: liście płac, karty multisport, pakiet medyczny, składki ppk, zus podatek

**Przykładowe posty (z centroidu):**

1. `314b22834802` · grupa_2_507801603233194 · 0 komentarzy
   > Cześć, pracodawca w całości finansuje pakiet medyczny dla pracowników. Jak powinno być to zaksięgowane na liście płac?  Na liście płac jest wykazana ta kwota, żeby naliczył się ZUS i podatek, ale tera…

2. `311b4e1959c4` · grupa_2_507801603233194 · 2 komentarzy
   > Cześć  Mam pytanko: czy od dofinansowanej części przez pracodawcę do kart Multisporta nalicza się tylko podatek ? Czy składki ZUS również ?

3. `72c8cc97f4c6` · grupa_2_507801603233194 · 0 komentarzy
   > Dzień dobry, czy jeśli pracownik dostał kartę Pluxee zasiloną np na 300 zł, to muszę tę kwotę ubruttowić? Doliczyć podatek i zus? Czyli 300 zł plus skladki?

---

## 31. KSeF: obieg, archiwizacja i weryfikacja faktur w biurze

- **rank**: 31  **score**: 101.4  **cluster_id**: `139`
- **topic_area**: `KSeF`
- **size**: 109 postów
- **avg_comments**: 1.89
- **has_many_comments_ratio**: 0.75
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą praktycznej organizacji pracy z KSeF w biurach rachunkowych i firmach: jak weryfikować i archiwizować faktury, czy je drukować, jak klient ma oznaczać faktury kosztowe oraz jak ułożyć elektroniczny obieg dokumentów.

**Keywords**: ksef, faktury, faktur, będą, klienta, wszystkie, lutego, pytanie, teraz, dokumentów  **Bigramy**: faktury ksef, wszystkie faktury, faktury kosztowe, elektroniczny obieg, obieg dokumentów

**Przykładowe posty (z centroidu):**

1. `cc5cc333f5c2` · ksiegowosc_moja_pasja · 1 komentarzy
   > Hej, pytanie o KSEF Jak planujecie pracę z KSEF w praktyce? Czy klienci nadal będą dostarczać faktury czy bazujecie tylko na tym, co jest w KSEF? I jak klient ma oznaczać, które faktury są KUP, a któr…

2. `7d3402451576` · ksiegowosc_moja_pasja · 1 komentarzy
   > Hej, pytanie o KSEFJak planujecie pracę z KSEF w praktyce?Czy klienci nadal będą dostarczać faktury czy bazujecie tylko na tym, co jest w KSEF? I jak klient ma oznaczać, które faktury są KUP, a które…

3. `150ba10bb077` · ksiegowosc_moja_pasja · 2 komentarzy
   > Ściągnąłem faktury z ksef widze je w programie ale jak radzicie sobie z weryfikacja skoro fizycznie nie macie tej faktury czy moze je drukujecie jak to ogarniacie technicznie ?

---

## 32. Najem prywatny a VAT, KSeF i JDG

- **rank**: 32  **score**: 101.1  **cluster_id**: `53`
- **topic_area**: `VAT`
- **size**: 143 postów
- **avg_comments**: 1.20
- **has_many_comments_ratio**: 0.37
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rozliczania najmu prywatnego w kontekście VAT, obowiązku wysyłki faktur do KSeF oraz relacji między najmem prywatnym a prowadzoną działalnością gospodarczą (JDG, ryczałt, kasa fiskalna).

**Keywords**: vat, najem, faktury, prywatny, ksef, jdg, wynajmuje, działalność, najmu, działalności  **Bigramy**: najem prywatny, osoba fizyczna, kasę fiskalną, działalności gospodarczej, działalność gospodarczą

**Przykładowe posty (z centroidu):**

1. `8a0d409bd299` · ksiegowosc_moja_pasja · 2 komentarzy
   > A najem prywatny wystawiony na firmę ale u podatnika zwolnionego z VAT? ( przedsiębiorca prowadzi inną działalność i nie przekroczył limitu do VAT)

2. `542fa1f69e76` · ksiegowosc_moja_pasja · 1 komentarzy
   > Osoba fizyczna najmuje lokale firmom. Czy musi od 1 kwietnia wysyłać faktury za najem przez ksef ?

3. `dccb417eabec` · ksiegowosc_moja_pasja · 2 komentarzy
   > Czy faktura z vat za najem prywatny  wystawiona na firmę musi być przesłana do ksef ?Czy faktura z vat za najem prywatny  wystawiona na firmę musi być przesłana do ksef ?

---

## 33. Ryczałt: dobór stawki wg rodzaju usługi (IT, hydraulik, catering, BHP, księgowość)

- **rank**: 33  **score**: 98.4  **cluster_id**: `48`
- **topic_area**: `PIT`
- **size**: 144 postów
- **avg_comments**: 1.04
- **has_many_comments_ratio**: 0.32
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą ustalenia właściwej stawki ryczałtu ewidencjonowanego (3%, 5,5%, 8,5%, 12%, 17%) dla konkretnych usług oraz dopasowania jej do PKD/PKWiU. Pojawia się też wątek stawki VAT 8% przy usłudze montażowej.

**Keywords**: stawka, ryczałtu, usługi, vat, jaka, pkd, stawkę, zastosować, usługa, usług  **Bigramy**: jaka stawka, stawka ryczałtu, zastosować stawkę, kod pkd, stawkę ryczałtu

**Przykładowe posty (z centroidu):**

1. `fdcdcedd226d` · ksiegowosc_moja_pasja · 0 komentarzy
   > Cześć jaka stawka ryczałtu dla usług hydraulicznych? Czy stosujecie obie stawki 5,5% oraz 8,5%? Nie potrafię zrozumieć, która stawka kiedy.. Jakie np opisy usług macie pod którą stawka u klienta np?

2. `f4ede36351ac` · ksiegowosc_moja_pasja · 2 komentarzy
   > Kiedy mogę zastosować stawkę 12% ryczałtu przy usługach IT żeby kontrola nie miała pytań….

3. `db109870bfc4` · ksiegowosc_moja_pasja · 2 komentarzy
   > Słuchajcie mam klienta który rozwozi catering. Wpisał w PKD kod 56.21z ale Fv jest wystawiona pt usługa transportowa a to kwalifikuje się do 8.5% już. Ktoś ma takiego klienta?

---

## 34. KPiR 2026: księgowanie faktur do paragonu i sprzedaży detalicznej

- **rank**: 34  **score**: 97.5  **cluster_id**: `110`
- **topic_area**: `KPiR`
- **size**: 123 postów
- **avg_comments**: 1.42
- **has_many_comments_ratio**: 0.50
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą nowych zasad ewidencjonowania w KPiR od 2026 r. faktur wystawianych do paragonów (w tym dla osób fizycznych) oraz sprzedaży detalicznej z kasy fiskalnej — czy ujmować każdą fakturę osobno, czy zbiorczo na podstawie raportu miesięcznego.

**Keywords**: sprzedaży, kpir, faktury, sprzedaż, kasy, fiskalnej, fakturę, paragonu, zbiorczo, jpk  **Bigramy**: kasy fiskalnej, osób fizycznych, koniec miesiąca, raport fiskalny, jednym zapisem

**Przykładowe posty (z centroidu):**

1. `9693e56dd286` · ksiegowosc_moja_pasja · 1 komentarzy
   > Podpowiedzcie, jak to jest ze zmianą przepisów z elektroniczną ewidencją sprzedaży. Klient wprowadza na swoim profilu klienta -dowody sprzedaży z podsumowaniem z całego dnia (klient bez kasy fiskalnej…

2. `9d48e1a84c90` · ksiegowosc_moja_pasja · 1 komentarzy
   > Jak wygląda w 2026 księgowanie faktur pod paragon? Do tej pory księgowałam fakturę do JPK Vat z oznaczeniem FP, a do książki w kolumne Inne, zeby nie zdublowac sprzedaży z raportem fiskalnym. Ewentual…

3. `c5485cbadc87` · ksiegowosc_moja_pasja · 0 komentarzy
   > Faktury do paragonu dla osób fizycznychRozumiem, że od 2026 roku w rejestrze każda faktura wykazywana osobno z FP, a w KPiR pod raportem miesięcznym? Bez księgowania każdej pozycji osobno?

---

## 35. Umowa zlecenie ze studentem/uczniem do 26 r.ż. - składki ZUS

- **rank**: 35  **score**: 96.2  **cluster_id**: `69`
- **topic_area**: `ZUS`
- **size**: 100 postów
- **avg_comments**: 1.81
- **has_many_comments_ratio**: 0.62
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą zwolnienia ze składek ZUS przy umowach zlecenia zawieranych ze studentami i uczniami do 26 roku życia, w tym wymaganej dokumentacji (oświadczenie, zaświadczenie, legitymacja) oraz zbiegów tytułów ubezpieczeń (UoP, działalność, szkoła policealna).

**Keywords**: zus, zlecenie, składek, studenta, zaświadczenie, umowie, szkoły, roku, umowę, umowa  **Bigramy**: umowę zlecenie, umowa zlecenie, status studenta, umowie zlecenie, szkoły policealnej

**Przykładowe posty (z centroidu):**

1. `74b9defea0f8` · grupa_2_507801603233194 · 1 komentarzy
   > Zleceniobiorca, którego chcę zatrudnić jest uczniem szkoły policealnej. Czy muszę umowę zgłaszać do ZUS, czy jest zwolniony ze składek?

2. `3c22d7aedb91` · grupa_2_507801603233194 · 2 komentarzy
   > Czy pomoże ktoś w Umowie zlecenie? Mam pracownika który w innej firmie jest zatrudniony na UOP a u mnie będzie miał zlecenie. Jest to student 24 lata czy ja mogę nie naliczać mu ZUS a tylko podatek ??…

3. `511ffe5b3b4e` · grupa_2_507801603233194 · 2 komentarzy
   > Witam, czy osoba która pracuje na umowie o pracę i umowie zlecenie poniżej 26 r życia. Donosi zaświadczenie o uczęszczaniu do szkoły policealnej . Czy na umowie zlecenie jest zwolniona ze składek ZUS…

---

## 36. Powrót do zwolnienia VAT po podniesieniu limitu do 240 tys.

- **rank**: 36  **score**: 94.9  **cluster_id**: `94`
- **topic_area**: `VAT`
- **size**: 123 postów
- **avg_comments**: 1.28
- **has_many_comments_ratio**: 0.44
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą podatników, którzy przekroczyli limit 200 tys. zł pod koniec 2025 r. i zarejestrowali się do VAT, a chcą skorzystać z przepisów przejściowych i powrócić do zwolnienia podmiotowego od stycznia 2026 r. w związku z podniesieniem limitu do 240 tys. zł, w tym terminów i sposobu złożenia aktualizacji VAT-R.

**Keywords**: vat, roku, zwolnienia, limit, limitu, podatnik, tys, vat-r, działalność, grudniu  **Bigramy**: zwolnienia vat, limit vat, przekroczył limit, przekroczenie limitu, limitu vat

**Przykładowe posty (z centroidu):**

1. `e41d99c07dd9` · ksiegowosc_moja_pasja · 1 komentarzy
   > Mam pytanie odnośnie zwolnienia limitu podmiotowego VAT.Ostatnio były posty na grupie, ale nie mogę ich odnaleźć. Podatnik przekroczył końcem roku limit 200 tyś zł więc musi rejestrować się do VAT; na…

2. `e496b2ae1cfb` · ksiegowosc_moja_pasja · 1 komentarzy
   > Mam pytanie odnośnie zwolnienia limitu podmiotowego VAT. Ostatnio były posty na grupie, ale nie mogę ich odnaleźć. Podatnik przekroczył końcem roku limit 200 tyś zł więc musi rejestrować się do VAT; n…

3. `9ce5e0150234` · ksiegowosc_moja_pasja · 1 komentarzy
   > Powrót do zwolnienia z vat. Jak to jest podatnik przekroczył limit do zwolnienia w grudniu. Odbyła się rejestracja do vat. W styczniu chce powrócić do zwolnienia bo nie przekroczył 240 000. Czy w styc…

---

## 37. Minimalne wynagrodzenie 2026: regulamin i składniki płacy

- **rank**: 37  **score**: 94.7  **cluster_id**: `71`
- **topic_area**: `kadry`
- **size**: 137 postów
- **avg_comments**: 0.99
- **has_many_comments_ratio**: 0.36
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą zmian minimalnego wynagrodzenia od 1 stycznia 2026, konieczności aktualizacji regulaminu wynagradzania i tabel zaszeregowania oraz tego, jakie składniki (dodatek funkcyjny, premia) wchodzą w skład płacy minimalnej.

**Keywords**: wynagrodzenia, wynagrodzenie, stycznia, pracowników, pracy, dodatek, pracę, pytanie, wynagradzania, pomoc  **Bigramy**: najniższej krajowej, minimalnego wynagrodzenia, wynagrodzenie zasadnicze, regulamin pracy, płacy minimalnej

**Przykładowe posty (z centroidu):**

1. `38d75eae24f6` · grupa_2_507801603233194 · 0 komentarzy
   > Witam czy ma ktoś utworzony nowy regulamin wynagradzania pracowników jednostki budzetowej od dn. 01.01.2026

2. `e02ca17b206c` · grupa_2_507801603233194 · 2 komentarzy
   > Czy od stycznia 2026 wynagrodzenie zasadnicze musi byc = wynagrodzeniu minimalnemu, czy nadal może byc niższe i uzupełnione premią?

3. `5d424215ecaf` · grupa_2_507801603233194 · 2 komentarzy
   > Witam czy jest juz obowiazujaca nowa stawka dotycząca minimalnego wynagrodzenia od stycznia 2026?

---

## 38. Delegowanie i podróże służbowe pracowników za granicę: ZUS, podatek, A1

- **rank**: 38  **score**: 92.3  **cluster_id**: `19`
- **topic_area**: `kadry`
- **size**: 153 postów
- **avg_comments**: 0.56
- **has_many_comments_ratio**: 0.18
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rozliczania pracowników i zleceniobiorców wysyłanych do pracy za granicę (Holandia, Niemcy, Czechy, Szwecja, Norwegia) — procedury delegowania, formularz A1, naliczanie ZUS, podatku i diet.

**Keywords**: pracy, zus, polsce, pracownik, pracownika, pomoc, pracowników, rozliczyć, dni, niemczech  **Bigramy**: pierwszy raz, pracy niemczech, powinien mieć, taką sytuację, taki przypadek

**Przykładowe posty (z centroidu):**

1. `c7f08f3412ad` · grupa_2_507801603233194 · 0 komentarzy
   > Dzień dobry. Czy ktoś byłby w stanie udzielić pomocy dotyczącej delegowania pracowników do Holandii z Polskiej firmy? Procedury + najważniejsze rozliczenie wynagrodzeń (Zus i podatek) Będę wdzięczna z…

2. `9f78b83ad5b7` · grupa_2_507801603233194 · 0 komentarzy
   > Dzień dobry. Czy ktoś byłby w stanie udzielić pomocy dotyczącej delegowania pracowników do Holandii z Polskiej firmy?Procedury + najważniejsze rozliczenie wynagrodzeń (Zus i podatek)Będę wdzięczna za…

3. `a003ebba8e83` · grupa_2_507801603233194 · 0 komentarzy
   > Mam pytanie,  jak rozliczyć delegacje osobie, atrudnionej na UOP w firmie działającej w Polsce ale osoba mieszka w innym kraju np na Litwie i ma delegacje na łotwe. Jaka stawkę za godzinę delegacji li…

---

## 39. ZUS Z-3: wynagrodzenie i zasiłek chorobowy przy firmach <20 pracowników

- **rank**: 39  **score**: 91.9  **cluster_id**: `134`
- **topic_area**: `ZUS`
- **size**: 108 postów
- **avg_comments**: 1.44
- **has_many_comments_ratio**: 0.53
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rozliczania zwolnień lekarskich w firmach zatrudniających poniżej 20 osób – kiedy pracodawca wypłaca wynagrodzenie chorobowe, kiedy ZUS przejmuje zasiłek (m.in. po 33 dniach lub po ustaniu zatrudnienia) oraz jak i kiedy składać druk Z-3.

**Keywords**: zus, zwolnienie, zasiłek, pracownik, z-3, pracodawca, chorobowego, zatrudnienia, chorobowe, dni  **Bigramy**: zwolnienie lekarskie, zasiłek chorobowy, ustaniu zatrudnienia, zwolnieniu lekarskim, zwolnienie chorobowe

**Przykładowe posty (z centroidu):**

1. `a19d1d056f19` · grupa_2_507801603233194 · 0 komentarzy
   > Witam, mam pytanie o zwolnienie lekarskie, podczas którego kończy się umowa o pracę. W tej sytuacji wynagrodzenie chorobowe wypłaca pracodawca, a za dni gdy już umowa jest zakończona, ZUS wypłaca zasi…

2. `9af03890ff02` · grupa_2_507801603233194 · 2 komentarzy
   > Jeśli mam mniej niż 20 pracowników i wpłynęło zwolnienie lekarskie to powinnam złożyć druk z3 do zusu? A mu wypłacić pomniejszone wynagrodzenie? A wynagrodzenie za czas chorobowy powinien wypłacić ZUS…

3. `aa8d6b663ddb` · grupa_2_507801603233194 · 0 komentarzy
   > Zus z-3 Pracownik zatrudniony na umowe o prace, dostał w listopadzie zwolnienie lekarskie do kónca roku. Płatnikiem jest spółka zatrudniająca poniżej 20 pracowników. Spółka wypłaci wynagrodzenie choro…

---

## 40. Rozliczanie wynagrodzeń wypłacanych w następnym miesiącu: koszty, ZUS, PIT

- **rank**: 40  **score**: 90.8  **cluster_id**: `74`
- **topic_area**: `kadry`
- **size**: 102 postów
- **avg_comments**: 1.50
- **has_many_comments_ratio**: 0.52
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą momentu ujmowania w kosztach (KPiR/bilans) wynagrodzeń i składek ZUS, gdy wypłata następuje w kolejnym miesiącu lub roku, oraz prawidłowego przypisania ich do okresu na listach płac, deklaracjach (RPA, PIT-4R, PIT-11).

**Keywords**: wynagrodzenie, zus, wynagrodzenia, miesiąca, styczniu, wypłacone, płac, grudniu, grudzień, ppk  **Bigramy**: lista płac, następnego miesiąca, dnia miesiąca, liście płac, dnia następnego

**Przykładowe posty (z centroidu):**

1. `56282a69e462` · grupa_2_507801603233194 · 2 komentarzy
   > Hej, pracuję od niedawna w płacach.  Mam pytanie o przelanie wynagrodzenia z umowy zlecenie. Czy można za listopad przelać wynagrodzenie w grudniu? Jeśli tak, to jak naliczyć listę płac? Data sporządz…

2. `5eb4bd9ad45a` · grupa_2_507801603233194 · 2 komentarzy
   > Podpowiedzcie proszę, bo się zakręciłam. 9go stycznia wypłacę składnik wynagrodzenia za grudzień. Czy tą wypłatę wykazuję na RPA teraz w styczniu, czy w lutym?

3. `5beacd4cab3a` · ksiegowosc_moja_pasja · 2 komentarzy
   > hejka, mam pytanie, co do księgowania list płac w kpir, jak mam listę płac za styczeń wypłaconą w lutym, to wynagrodzenie plus ZUS jest kosztem lutego i wtedy patrze na dra ze stycznia, a jak mam list…

---

## 41. Ustalanie podstawy wynagrodzenia chorobowego przy zmianach etatu i płacy

- **rank**: 41  **score**: 90.2  **cluster_id**: `130`
- **topic_area**: `kadry`
- **size**: 105 postów
- **avg_comments**: 1.41
- **has_many_comments_ratio**: 0.48
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą sposobu wyliczania podstawy wynagrodzenia i zasiłku chorobowego w sytuacjach zmiany wynagrodzenia, etatu, wzrostu płacy minimalnej oraz uzupełniania wynagrodzenia przy nieobecnościach. Księgowi pytają, jakie kwoty i z jakich okresów przyjmować do podstawy.

**Keywords**: wynagrodzenie, chorobowego, pracownik, podstawy, wynagrodzenia, podstawę, zasiłku, chorobowe, etatu, podstawa  **Bigramy**: wynagrodzenia chorobowego, wynagrodzenie chorobowe, pracownik zatrudniony, zasiłku chorobowego, podstawy zasiłku

**Przykładowe posty (z centroidu):**

1. `42143d89f28d` · grupa_2_507801603233194 · 1 komentarzy
   > Proszę o pomoc Jak wyliczyć podstawę do wynagrodzenia chorobowego?pracownik na zwolnieniu w marcu, czyli biorę podstawę od marca 2025 do lutego 2026. W marcu zmienia się wynagrodzenie dla pracowników…

2. `5fcf4806b659` · grupa_2_507801603233194 · 1 komentarzy
   > Proszę o pomocJak wyliczyć podstawę do wynagrodzenia chorobowego?pracownik na zwolnieniu w marcu, czyli biorę podstawę od marca 2025 do lutego 2026. W marcu zmienia się wynagrodzenie dla pracowników s…

3. `6d30a7a7c05d` · grupa_2_507801603233194 · 2 komentarzy
   > Pracownikowi 15.09 zmieniła się kwota wynagrodzenia. W październiku zachorował. Jaką kwotę wziąć do podstawy chorobowego za wrzesień? Przed czy po zmianie a może policzone brutto za wrzesień?

---

## 42. Limity umów na czas określony: 33 miesiące i 3 umowy

- **rank**: 42  **score**: 89.4  **cluster_id**: `113`
- **topic_area**: `kadry`
- **size**: 98 postów
- **avg_comments**: 1.51
- **has_many_comments_ratio**: 0.54
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą zasad zawierania kolejnych umów o pracę na czas określony, wliczania umowy na okres próbny do limitu 33 miesięcy i 3 umów oraz wpływu przerw w zatrudnieniu na ponowne liczenie limitów.

**Keywords**: czas, umowa, określony, umowę, okres, pracownik, próbny, umowy, miesiące, nieokreślony  **Bigramy**: czas określony, okres próbny, umowę czas, czas nieokreślony, umowa czas

**Przykładowe posty (z centroidu):**

1. `ab632709d15a` · grupa_2_507801603233194 · 2 komentarzy
   > Pracownik miał umowę na okres próbny 3 miesiące później umowę na czas określony rok czy kolejną umowę na czas określony możemy dać na 3 miesiące?

2. `1c6afde3f870` · grupa_2_507801603233194 · 2 komentarzy
   > Mam pytanie o czas umów jeżeli pierwsza umowa jest na okres  próbny na 3 miesiące to ile może być potem oprócz tej na okres próbny umów na czas określony ? Z góry bardzo dziękuję za odpowiedź

3. `8844a55ff2ff` · grupa_2_507801603233194 · 2 komentarzy
   > Pracownik miał umowę na okres próbny 3 miesiące później umowę na czas określony rok czy kolejną umowę na czas określony możemy dać na 3 miesiące?Pracownik miał umowę na okres próbny 3 miesiące później…

---

## 43. Śmierć pracownika: wypłata wynagrodzenia, ekwiwalentu i odprawy pośmiertnej

- **rank**: 43  **score**: 88.8  **cluster_id**: `1`
- **topic_area**: `kadry`
- **size**: 102 postów
- **avg_comments**: 1.40
- **has_many_comments_ratio**: 0.50
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rozliczenia świadczeń po zmarłym pracowniku — komu i w jakich proporcjach wypłacić wynagrodzenie, ekwiwalent za urlop i odprawę pośmiertną oraz jak poprawnie wystawić PIT-11 i listę płac.

**Keywords**: pracownika, zmarł, pracownik, wynagrodzenie, pracy, zmarłego, odprawę, śmierci, wynagrodzenia, śmierć  **Bigramy**: pracownik zmarł, śmierć pracownika, odprawy pośmiertnej, zmarłego pracownika, renty rodzinnej

**Przykładowe posty (z centroidu):**

1. `5698cbe4551e` · grupa_2_507801603233194 · 1 komentarzy
   > W połowie miesiąca zmarł pracownik. Pozostawił żonę oraz córkę (21 lat, studentka – spełnia warunki do renty rodzinnej). Czy zaległe wynagrodzenie, ekwiwalent za urlop oraz odprawę pośmiertną wypłacam…

2. `b901d9a94e21` · grupa_2_507801603233194 · 1 komentarzy
   > Witam, śmierć pracownika, jeśli chodzi o wynagrodzenie   i ekwiwalent urlopowy o pit11 na co zwrócić szczególną uwagę, żeby wszystko było dobrze wypłacone, jak           w takim przypadku przeliczyć w…

3. `166849f5e0ec` · grupa_2_507801603233194 · 0 komentarzy
   > Witam, śmierć pracownika,   wynagrodzenie , ekwiwalent urlopowy i odprawę posmiertna przelewam na konto żony?, jeśli jest uprawniona do renty, bo dzieci nie są uprawnione, są to osoby pracujące po 30…

---

## 44. ZUS Płatnik/PUE: błędy krytyczne przy wysyłce deklaracji i korekt DRA/RCA

- **rank**: 44  **score**: 87.9  **cluster_id**: `85`
- **topic_area**: `ZUS`
- **size**: 97 postów
- **avg_comments**: 1.45
- **has_many_comments_ratio**: 0.62
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Księgowi zgłaszają problemy techniczne z wysyłką deklaracji ZUS (DRA, RCA, ZWUA, zgłoszenia) – błędy krytyczne o niepotwierdzonych danych płatnika oraz trudności z korektami dokumentów rozliczeniowych w Płatniku i PUE ZUS.

**Keywords**: zus, dra, błąd, deklaracji, zrobić, krytyczny, problem, pue, rca, danych  **Bigramy**: błąd krytyczny, dra rca, wyskakuje błąd, zrobić korektę, pue zus

**Przykładowe posty (z centroidu):**

1. `e8375531f120` · ksiegowosc_moja_pasja · 0 komentarzy
   > Dzień dobry, Czy spotkali się Państwo z komunikatem przy wysyłce deklaracji do ZUS „dokument ma niepotwierdzone dane płatnika w ZUS”? ZPA złożone.

2. `7a7b67a8cc2a` · ksiegowosc_moja_pasja · 0 komentarzy
   > Jak wysłać zus dra2 za styczeń.  Zus pue nie działa więc ciągle jest błąd krytyczny bo nie widzi kodu ubezpieczenia.  Czy mam to wysłać papierowo żeby było w terminie?

3. `077161926230` · ksiegowosc_moja_pasja · 0 komentarzy
   > Dzień dobry,Czy spotkali się Państwo z komunikatem przy wysyłce deklaracji do ZUS „dokument ma niepotwierdzone dane płatnika w ZUS”?ZPA złożone.

---

## 45. KSeF: panika klientów i przygotowanie biur rachunkowych

- **rank**: 45  **score**: 87.7  **cluster_id**: `109`
- **topic_area**: `KSeF`
- **size**: 59 postów
- **avg_comments**: 2.20
- **has_many_comments_ratio**: 0.95
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą reakcji klientów biur rachunkowych na wdrożenie KSeF — obaw o bezpieczeństwo systemu, oporu wobec zmian oraz roli księgowych w przygotowaniu, wystawianiu faktur i obsłudze klientów.

**Keywords**: ksef, faktury, klientów, wszystko, faktur, odnośnie, pytanie, rachunkowych, biur, firmy  **Bigramy**: biur rachunkowych, wasi klienci, odnośnie ksef, pytanie osób, non stop

**Przykładowe posty (z centroidu):**

1. `9a9a05644bf9` · ksiegowosc_moja_pasja · 2 komentarzy
   > Pytanie odnośnie ksef Czy wasi klienci też panikują przed wejściem ksef i co im mówicie? U mnie telefony non stop odnośnie tego ,iż czytali o nieszczelności systemu albo ktoś dowie się ile transakcji…

2. `80eee1aebe94` · ksiegowosc_moja_pasja · 2 komentarzy
   > Pytanie odnośnie ksefCzy wasi klienci też panikują przed wejściem ksef i co im mówicie?U mnie telefony non stop odnośnie tego ,iż czytali o nieszczelności systemu albo ktoś dowie się ile transakcji or…

3. `29844e510312` · ksiegowosc_moja_pasja · 2 komentarzy
   > Ksef. Nie rozumiem troche tej paniki biur rachunkowych. Niestety dopiero siadam do szkolenia. Czy naprawdę jest się z czym spieszyć jeśli mam samych małych klientów? Od 1.02. będzie trzeba pobierać fv…

---

## 46. Rozwiązanie umowy: likwidacja stanowiska, porozumienie stron a zasiłek

- **rank**: 46  **score**: 87.3  **cluster_id**: `117`
- **topic_area**: `kadry`
- **size**: 90 postów
- **avg_comments**: 1.57
- **has_many_comments_ratio**: 0.56
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą prawidłowego sformułowania wypowiedzenia i świadectwa pracy przy rozwiązaniu umowy z przyczyn leżących po stronie pracodawcy (likwidacja stanowiska, zamknięcie firmy, porozumienie stron), tak aby pracownik zachował prawo do zasiłku dla bezrobotnych.

**Keywords**: wypowiedzenie, umowy, pracy, stron, wypowiedzenia, pracodawca, pracownik, stanowiska, likwidacja, zlecenie  **Bigramy**: rozwiązanie umowy, porozumieniem stron, umowy pracę, likwidacja stanowiska, porozumienie stron

**Przykładowe posty (z centroidu):**

1. `324a3837cee3` · grupa_2_507801603233194 · 2 komentarzy
   > Nie ma czegoś takiego jak wypowiedzenie za porozumieniem stron. Albo pracodawca daje wypowiedzenie z zachowaniem okresu wypowiedzenia, albo dogadujecie się razem i dochodzi do ROZWIĄZANIA umowy za por…

2. `bec9c77ba78a` · grupa_2_507801603233194 · 2 komentarzy
   > Witam chciałam się upewnić jak prawidłowo wpisać podstawę prawną do świadectwa pracy ,likwidacja stanowiska pracy problemy finansowe spółki wypowiedzenie że strony pracodawcy który zatrudnia do 20 osó…

3. `fce5b81108ff` · grupa_2_507801603233194 · 2 komentarzy
   > Mam pytanie. Szef chce zwolnić 3 pracowników za porozumieniem. Co wpisać na wypowiedzeniu i na ewentualnym świadectwie pracy tak żeby mieli prawo od razu do zasiłku. Zwolnienie jest między innymi ze z…

---

## 47. Ulga dla pracującego seniora: PIT-11 i rozliczenie

- **rank**: 47  **score**: 87.3  **cluster_id**: `75`
- **topic_area**: `PIT`
- **size**: 107 postów
- **avg_comments**: 1.22
- **has_many_comments_ratio**: 0.43
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą stosowania ulgi dla pracującego seniora oraz sposobu wykazywania przychodów emerytów i osób w wieku emerytalnym w PIT-11, w tym momentu nabycia prawa do ulgi i rozliczenia kosztów uzyskania przychodu.

**Keywords**: pit, ulgi, seniora, emeryturę, pracownik, podatek, emeryt, ulgę, ulga, pit-11  **Bigramy**: wiek emerytalny, ulgi seniora, osiągnął wiek, ulga seniora, zastosować ulgę

**Przykładowe posty (z centroidu):**

1. `457ab05617f9` · grupa_2_507801603233194 · 0 komentarzy
   > Witam, pytanie dot. PIT11: w której rubryce powinnam wykazać przychód  pracownika UOP, który pobiera emeryturę i nie korzysta z ulgi dla seniora? Czy w rubrykach 43 do 49 wiersz trzeci będzie ok? Bard…

2. `0983839f3968` · grupa_2_507801603233194 · 1 komentarzy
   > Dzień dobry, pracownik 14 kwietnia 2025 ukończył 65 rż. Wypłatę za marzec dostał 10 kwietnia. Czy tę wypłatę którą otrzymał w kwietniu można zaliczyć do kwoty z ulgą dla pracującego seniora i uwzględn…

3. `7107023889f5` · grupa_2_507801603233194 · 0 komentarzy
   > Witam, Pracujący emeryt, nie korzystający z ulgi dla seniora w trakcie roku, nie pobierający emerytury czy jego przychód z umowy o pracę powinien być wykazany w rubryce 43, w PIT 11 ?

---

## 48. Zbieg tytułów ubezpieczeń przy umowach zlecenie

- **rank**: 48  **score**: 86.3  **cluster_id**: `83`
- **topic_area**: `ZUS`
- **size**: 91 postów
- **avg_comments**: 1.50
- **has_many_comments_ratio**: 0.49
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą ustalania, jakie składki ZUS (społeczne, chorobowe, zdrowotna) należy odprowadzać od zleceniobiorców w przypadku zbiegu tytułów ubezpieczeń – z inną umową zlecenie, umową o pracę, działalnością gospodarczą lub emeryturą.

**Keywords**: zlecenie, umowę, umowy, pracę, składki, zlecenia, wynagrodzenie, umowa, zus, minimalne  **Bigramy**: umowę zlecenie, umowy zlecenia, umowę pracę, umowy zlecenie, minimalne wynagrodzenie

**Przykładowe posty (z centroidu):**

1. `10bc98ef85ae` · grupa_2_507801603233194 · 1 komentarzy
   > Jakie składki pobierać od zleceniobiorcy Zleceniobiorca zawarł z nami umowę zlecenie 3 w kolejności aby prawidłowo rozliczać składki w każdym miesiącu należy brać oświadczenie czy podstawa składek z i…

2. `a138948c2ff7` · grupa_2_507801603233194 · 5 komentarzy
   > Umowa o pracę z wyższym niż minimalne wynagrodzenie, następnie chce zawrzeć umowę zlecenie z innym pracodawcą- czy mogę płacisz wszystkie składki społeczne plus chorobowa ? Czy jest to zbieg umów i ni…

3. `7c217c519ee4` · grupa_2_507801603233194 · 1 komentarzy
   > Witam, firma chce zatrudnić pracownika na umowę zlecenie. Osoba zaznaczyła na oświadczeniu że jest emerytem a dodatkowo jest jeszcze zatrudniona na umowę o pracę i zarabia minimalne wynagrodzenie. Pyt…

---

## 49. KSeF: obowiązek dla nievatowców, zwolnionych z VAT i limitu 10 tys.

- **rank**: 49  **score**: 86.2  **cluster_id**: `111`
- **topic_area**: `KSeF`
- **size**: 83 postów
- **avg_comments**: 1.65
- **has_many_comments_ratio**: 0.58
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą tego, kto i w jakich sytuacjach musi korzystać z KSeF — w szczególności podatników zwolnionych z VAT, nievatowców wystawiających rachunki, przedsiębiorców poniżej limitu 10 tys. zł, organizacji pozarządowych oraz sprzedaży zagranicznej.

**Keywords**: ksef, faktury, vat, muszę, faktur, tys, roku, będą, wystawiać, obowiązek  **Bigramy**: faktury ksef, wysyłać ksef, wysyłać faktury, wystawia faktury, końca roku

**Przykładowe posty (z centroidu):**

1. `7c886850999b` · ksiegowosc_moja_pasja · 2 komentarzy
   > #ksef Czy dobrze rozumiem ze jak ktoś jest zwolniony z VAT to nie musi w przyszłym roku przesyłać faktur do ksef i Ci którzy są zarejestrowani do VAT ale nie przekroczą limitu 10000 zł brutto też nie…

2. `1f52e74604ca` · ksiegowosc_moja_pasja · 2 komentarzy
   > Dobry wieczór, jestem vatowcem i miesięcznie nie przekroczę obrotu 10tys. Czy muszę wysłać faktury do KSeF?

3. `07b668284201` · ksiegowosc_moja_pasja · 1 komentarzy
   > Prowadzę działalność gospodarczą - ale nie jestem zarejestrowany do VAT. Wystawiam rachunki. Czy dobrze rozumiem, że też muszę się zarejestrować do KSEF, żeby np. pobierać faktury za leasing, telefon…

---

## 50. KUP i kwota zmniejszająca przy dwóch umowach o pracę

- **rank**: 50  **score**: 85.7  **cluster_id**: `92`
- **topic_area**: `PIT`
- **size**: 89 postów
- **avg_comments**: 1.51
- **has_many_comments_ratio**: 0.58
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą stosowania kosztów uzyskania przychodu (podstawowych/podwyższonych) oraz kwoty zmniejszającej podatek i PIT-2 przy zatrudnieniu u dwóch pracodawców lub na dwóch umowach, a także limitów rocznych KUP w zeznaniu PIT.

**Keywords**: pracy, koszty, kup, uzyskania, pracę, pit, pracownik, umowy, przychodu, podwyższone  **Bigramy**: koszty uzyskania, uzyskania przychodu, podwyższone koszty, umowy pracę, dwie umowy

**Przykładowe posty (z centroidu):**

1. `0151b5243f5a` · grupa_2_507801603233194 · 1 komentarzy
   > Dzień dobry, mam prośbę o potwierdzenie czy dobrze rozumiem prawo: pracownik jest zatrudniony u jednego pracodawcy na dwie umowy o pracę, wykonuje dwie inne czynności, czy koszty uzyskania przychodu p…

2. `630f3db85442` · grupa_2_507801603233194 · 1 komentarzy
   > Czy w rozliczeniu rocznym Pit-36 z działalności i umów o pracę można zastosować KUP w wysokości 4500zł ze stosunku pracy (miejscowe) i dodatkowo koszty z działalności? Oczywiście oddzielnie w odpowied…

3. `bb70d624fda3` · grupa_2_507801603233194 · 2 komentarzy
   > Pracownik pracuje na  1/2 etatu w innym zakładzie pracu.U nas podjął pracę na dodatkowo 1/2 etatu. Wiem że nie można stosować w dwóch miejsc pracy ulgi podatkowej . A co z kosztami uzyskania przychodó…

---

## 51. KSeF: duplikaty faktur zakupowych i numer KSeF

- **rank**: 51  **score**: 85.5  **cluster_id**: `132`
- **topic_area**: `KSeF`
- **size**: 79 postów
- **avg_comments**: 1.70
- **has_many_comments_ratio**: 0.68
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą sytuacji, gdy ta sama faktura pojawia się równolegle w formie papierowej/PDF i w KSeF, oraz wątpliwości co do numeru KSeF, kodu QR i sposobu księgowania takich dokumentów.

**Keywords**: ksef, faktury, faktur, numer, faktura, kpir, fakturę, teraz, nip, związku  **Bigramy**: faktury ksef, numer ksef, faktur ksef, fakturę ksef, numer faktury

**Przykładowe posty (z centroidu):**

1. `06130227193d` · ksiegowosc_moja_pasja · 2 komentarzy
   > Kupilam towar i otrzymałam starą zwykłą papierową fakturę. Dzisiaj wchodzę do Ksef a tam jest również ta faktura tylko już z numerem Ksef, kodem Qr. sprzedawca nie ma obowiązku wystawiania faktur w Ks…

2. `324a75fa7004` · ksiegowosc_moja_pasja · 1 komentarzy
   > Jak to teraz bedzie z numeracja faktur, jdg obowiązek od kwietnia 2026, co gdy do 10.02 wystawiano kilka ręcznie a 11.02 wystawiono w Ksew i ten numer  od jedynki leci, no jest niezgodnosc w numeracji…

3. `b2a82f465b86` · ksiegowosc_moja_pasja · 0 komentarzy
   > Czy za rok przy raportowaniu - JPK_KR będzie wymagany numer KSEF?  Mam nietypowa sytuację, przejmuje ksiegowosc i w programie faktury zakupowe księgowane są przez tzw. BUFOR przez samo PK a nie przez…

---

## 52. Urlop wypoczynkowy przy kończącej się umowie i 14 dni ciągłych

- **rank**: 52  **score**: 85.3  **cluster_id**: `44`
- **topic_area**: `kadry`
- **size**: 71 postów
- **avg_comments**: 1.84
- **has_many_comments_ratio**: 0.70
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą udzielania zaległego i bieżącego urlopu wypoczynkowego w sytuacji wygasającej lub wypowiadanej umowy o pracę oraz obowiązku wykorzystania 14 dni kalendarzowych urlopu, w tym czy pracodawca może narzucić termin i czy potrzebny jest wniosek urlopowy.

**Keywords**: urlopu, urlop, pracownik, dni, pracownika, pracy, pracodawca, umowa, roku, umowę  **Bigramy**: urlopu wypoczynkowego, dni urlopu, porozumienie stron, świadczenia pracy, pracownik wykorzystał

**Przykładowe posty (z centroidu):**

1. `02cb6e6bcea2` · grupa_2_507801603233194 · 2 komentarzy
   > Dzień dobry, pracownik nie wykorzystał dlugiego 14 dniowego urlopu wypoczynkowego, zostało mu 5 dni do końca roku, jakie są konsekwencje nie udzielenia tego urlopu? Dodam, że pracownikowi było mówione…

2. `657f66beedef` · grupa_2_507801603233194 · 2 komentarzy
   > Czy jeżeli umowa kończy się przez upływ czasu na jaki została zawarta to pracodawca może nakazać pracownikowi skorzystać z urlopu w konkretnym terminie ?

3. `6832fe44a703` · grupa_2_507801603233194 · 2 komentarzy
   > Czy jeśli kończy mi się umowa za jakiś czas i firma nie przedłuża to mogą mi nie udzielić urlopu, który pozostał? Jak to jest? Czy pracownik ma prawo wybrać ten urlop czy mogą zawetować?

---

## 53. Kaucje za butelki w KPiR i VAT (system kaucyjny)

- **rank**: 53  **score**: 84.1  **cluster_id**: `6`
- **topic_area**: `KPiR`
- **size**: 102 postów
- **avg_comments**: 1.17
- **has_many_comments_ratio**: 0.45
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą księgowania kaucji za opakowania (butelki szklane i plastikowe) w KPiR oraz ujęcia ich w rejestrach VAT, szczególnie w kontekście nowego systemu kaucyjnego i sklepów nieprzyjmujących zwrotów.

**Keywords**: vat, butelki, kpir, noty, kaucji, kaucja, opakowania, faktury, opakowań, kaucję  **Bigramy**: kaucja butelki, kwotę kaucji, kaucje butelki, jpk vat, system kaucyjny

**Przykładowe posty (z centroidu):**

1. `4642bd40bb4b` · ksiegowosc_moja_pasja · 0 komentarzy
   > Witam. Jak należy zaksięgować w KPIR kaucje? Jedne są ze stawką np ale w drugiej są z doliczonym VAT. Czy mogą być  kosztem ? Czy mam prawo odliczyć ten VAT ?  Dodam że sklep nie przyjmuje zwrotów but…

2. `4aaef6bbd186` · ksiegowosc_moja_pasja · 1 komentarzy
   > Witam, prowadzę mały sklep spożywczy, rozliczam się na kpir. Chciałem zapytać jak ksiegujecie Państwo kaucję - zarówno szklane butelki po piwie jak i plastikowe: z Eurocash mam wydanie opakowań kaucyj…

3. `8bee27e363ed` · ksiegowosc_moja_pasja · 1 komentarzy
   > NOWY SYSTEM KAUCYJNY Cześć, mam pytanie do osób prowadzących księgowość dla małych sklepów (PKPiR). Jak rozwiązujecie temat nowych kaucji za opakowania w sklepach, które nie przyjmują zwrotów opakowań…

---

## 54. Rozliczanie sprzedaży Allegro: powiązanie wpłat z fakturami

- **rank**: 54  **score**: 83.7  **cluster_id**: `40`
- **topic_area**: `rachunkowość`
- **size**: 74 postów
- **avg_comments**: 1.70
- **has_many_comments_ratio**: 0.65
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą księgowania zbiorczych wypłat z Allegro (oraz PayPal, Etsy) i dopasowywania ich do pojedynczych faktur/paragonów, w tym rozliczania prowizji, różnic kursowych i sprzedaży w OSS.

**Keywords**: allegro, sprzedaż, klient, płatności, wyciągu, sprzedaży, konto, klienta, faktury, rozliczacie  **Bigramy**: sprzedaż allegro, rozlicza sprzedaż, wyciągu bankowym, sprzedaży allegro, macie jakieś

**Przykładowe posty (z centroidu):**

1. `dc42a0651d04` · ksiegowosc_moja_pasja · 2 komentarzy
   > Cześć,  jak rozliczacie sprzedaż przez allegro? Mam pierwszego takiego klienta,  dostaje przelewy z allegro za dany okres,  oprócz tego zwroty z pobrań inpost, poczta polska, dpd.. jak dojść za które…

2. `833d074cb0fb` · ksiegowosc_moja_pasja · 3 komentarzy
   > Dzień dobry jak zaksięgować wpływ na konto wypłaty środków z  konta Allegro  (wpłyneły na konto firmowe ) w pełnej księgowosci z vat ? F-ra wewnętrzna ? Wystawić f-re dla Allegro?? Wszystkie f-ry sprz…

3. `6a1c0c402a94` · ksiegowosc_moja_pasja · 1 komentarzy
   > Jak rozwiązujecie problem z powiązywaniem zbiorczych wypłat przy sprzedaży na Allegro z zamówieniami i ich FV/paragonami? Jeśli łączycie je ręcznie to polecam narzędzie

---

## 55. Zwolnienia lekarskie L4: nietypowe sytuacje i brak e-ZLA

- **rank**: 55  **score**: 82.2  **cluster_id**: `124`
- **topic_area**: `kadry`
- **size**: 62 postów
- **avg_comments**: 1.87
- **has_many_comments_ratio**: 0.76
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą problematycznych przypadków obsługi zwolnień lekarskich pracowników – brakujących lub spóźnionych e-ZLA, nakładających się L4, przerw między zwolnieniami, hospitalizacji bez dokumentu oraz podejrzeń o nadużywanie chorobowego.

**Keywords**: pracownik, pracy, zwolnienie, badania, pracownika, dni, zwolnienia, nieobecność, zrobić, lekarz  **Bigramy**: zwolnienie lekarskie, zwolnieniu lekarskim, medycyny pracy, badania kontrolne, nieobecność usprawiedliwiona

**Przykładowe posty (z centroidu):**

1. `c470e557a595` · grupa_2_507801603233194 · 2 komentarzy
   > Proszę o pomoc  Pracownik trafił do szpitala, jest tam od 20.01 nie wiadomo kiedy wyjdzie, bo z jego zdrowiem jest bardzo źle. Czy za styczeń mogę wpisać zwolnienie chorobowe mimo że nie dostałam jesz…

2. `e446d272f949` · grupa_2_507801603233194 · 1 komentarzy
   > Wpłynęły dwa zwolnienia lekarskie na te sam okres, dosłownie jedno po drugim. Co robicie z tym drugim zwolnieniem? Olać czy trzeba gdzieś zgłosić?

3. `477accd5b8c2` · grupa_2_507801603233194 · 2 komentarzy
   > Cześć   czy jeśli pracownik przebywa w sanatorium to będzie wystawione zwolnienie lekarskie ? Póki co nie ma żadnego zwolnienia lekarskiego. Powinnam zaznaczyć to jakoś nieobecność usprawiedliwiona ?

---

## 56. Umowa o pracę: data zawarcia a dzień rozpoczęcia pracy w dzień wolny

- **rank**: 56  **score**: 81.7  **cluster_id**: `59`
- **topic_area**: `kadry`
- **size**: 65 postów
- **avg_comments**: 1.78
- **has_many_comments_ratio**: 0.60
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą rozbieżności między datą podpisania/zawarcia umowy o pracę a dniem rozpoczęcia pracy, zwłaszcza gdy pierwszy dzień zatrudnienia przypada na sobotę, niedzielę lub inny dzień wolny.

**Keywords**: pracy, data, umowa, umowę, rozpoczęcia, umowy, datą, pracownik, zawarcia, pracę  **Bigramy**: rozpoczęcia pracy, data zawarcia, czas określony, będę wdzięczna, zawarcia umowy

**Przykładowe posty (z centroidu):**

1. `8d980816c900` · grupa_2_507801603233194 · 2 komentarzy
   > Witam czy umowa może być zawarta 01.01.2026 i dzień rozpoczęcia pracy 01.01.2026 mimo tego że dla pracownika jest to dzień wolny?

2. `4956423830fd` · grupa_2_507801603233194 · 2 komentarzy
   > Witam wszystkich grupowiczów. Bardzo proszę o pomoc. Firma będzie zatrudniała nowego pracownika. Dzień podpisania umowy będzie 2 lutego, pierwszy dzień pracy również, bo wtedy będzie miał szkolenie BH…

3. `f63de52fc1b0` · grupa_2_507801603233194 · 2 komentarzy
   > Proszę o potwierdzenie czy dobrze myślę, bo jestem na chwilowym zastępstwie za kadrową i akurat przypadło mi podpisać umowę z nowym pracownikiem od 01.02.2026 r. Pytanie: 1. Jeśli ma być zatrudniony o…

---

## 57. Premie w podstawie wynagrodzenia chorobowego i urlopowego

- **rank**: 57  **score**: 81.2  **cluster_id**: `127`
- **topic_area**: `kadry`
- **size**: 116 postów
- **avg_comments**: 0.74
- **has_many_comments_ratio**: 0.28
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą tego, czy różne rodzaje premii (regulaminowe, uznaniowe, kwartalne, roczne, za brak absencji, specjalne) należy wliczać do podstawy wynagrodzenia chorobowego oraz urlopowego, w zależności od tego, czy są pomniejszane za czas nieobecności.

**Keywords**: podstawy, chorobowego, dodatek, pracownik, premia, wynagrodzenia, czas, choroby, premie, dni  **Bigramy**: podstawy chorobowego, czas choroby, dodatek specjalny, wchodzi podstawy, wynagrodzenia urlopowego

**Przykładowe posty (z centroidu):**

1. `4a6f1ffec586` · grupa_2_507801603233194 · 1 komentarzy
   > Czy do wyliczenia podstawy wynagrodzenia chorobowego, nieobecność w styczniu 2026,  przyjąć premie które były wypłacana do grudnia co miesiąc 3% wynagrodzenia zasadniczego, które od stycznia w związku…

2. `b721d2ab6d6b` · grupa_2_507801603233194 · 0 komentarzy
   > Cześć, czy premie regulaminowe np. za usuwanie awarii w kwocie 50 zł za 1 godzinę. Wliczalibyście do podstawy chorobowego ? Wygląda to tak, w styczniu wypłaciliśmy np. 150 zł takiej premii. Czy dolicz…

3. `b799d2a2d7cd` · grupa_2_507801603233194 · 2 komentarzy
   > Jakie macie rodzaj premii na listach plac/ kartkach z wypłaty? Chodzi mi o nazewnictwo. Premia, 5s, wydajnościowa, motywacyjna ? Czy wszystkiego tego typu rodzaje premii powinny wchodzi do podstawy ch…

---

## 58. Ustalanie okresu wypowiedzenia umowy o pracę wg stażu

- **rank**: 58  **score**: 80.7  **cluster_id**: `118`
- **topic_area**: `kadry`
- **size**: 73 postów
- **avg_comments**: 1.57
- **has_many_comments_ratio**: 0.57
- **rekomendacja heurystyczna**: **RECOMMENDED WORKFLOW**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą prawidłowego ustalenia długości okresu wypowiedzenia umowy o pracę (2 tygodnie, 1 miesiąc, 3 miesiące) w zależności od stażu pracy pracownika oraz momentu złożenia wypowiedzenia, szczególnie gdy data wypowiedzenia jest bliska progom stażowym.

**Keywords**: wypowiedzenia, okres, wypowiedzenie, pracownik, pracy, miesięczny, miesiące, umowy, umowa, zatrudniony  **Bigramy**: okres wypowiedzenia, miesięczny okres, złożyć wypowiedzenie, pracownik zatrudniony, okresu wypowiedzenia

**Przykładowe posty (z centroidu):**

1. `ea20e88f623a` · ksiegowosc_moja_pasja · 2 komentarzy
   > Witam, zostało złożone wypowiedzenie umowy o pracę. Umowa zawarta 16.07.2025. Wypowiedzenie złożono 31.12.2025. Jaki jest prawidłowy okres wypowiedzenia?

2. `34afcac8fbf2` · grupa_2_507801603233194 · 0 komentarzy
   > Hej. Czy jak pracownik wypowie sie dzis, a umowe zawarl 1 kwietnia 2023, jaki ma okres wypowiedzenia? 1 miesiac czy 3? Jezeli zrobi to w kolejnym miesiacu np na poczatku marca to wtedy 3 miesiace wypo…

3. `7a9292abf0c0` · grupa_2_507801603233194 · 3 komentarzy
   > Proszę o potwierdzenie, zatrudnienie od 01.01.2023, dziś wręczymy wypowiedzenie, czy okresy wypowiedzenia jest 3 miesięczny czy 1 miesięczny?

---

## 59. ZUS: zaświadczenie o przychodach emerytów i rencistów do końca lutego

- **rank**: 59  **score**: 80.4  **cluster_id**: `84`
- **topic_area**: `ZUS`
- **size**: 90 postów
- **avg_comments**: 1.22
- **has_many_comments_ratio**: 0.43
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą obowiązku płatnika składania do ZUS rocznego zaświadczenia o przychodach zatrudnionych emerytów i rencistów – kogo obejmuje (wiek emerytalny, emeryci mundurowi, umowy zlecenia), na jakim druku i w jakiej formie.

**Keywords**: zus, emeryta, zaświadczenie, przychodach, emerytów, emeryturę, rok, pracownik, emeryt, końca  **Bigramy**: końca lutego, zaświadczenie zus, zaświadczenie przychodach, emerytów rencistów, wieku emerytalnego

**Przykładowe posty (z centroidu):**

1. `1f0e22d4746d` · grupa_2_507801603233194 · 0 komentarzy
   > Proszę o podpowiedź:1.  zatrudniamy emeryta, który nie na osiągniętego wieku emerytalnego. My jako płatnik wysylamy tylko zaświadczenie do ZUS o osiągniętych przychodach? na jakimś konkretnym druku?

2. `85a45706c101` · grupa_2_507801603233194 · 0 komentarzy
   > Proszę o podpowiedź: 1.  zatrudniamy emeryta, który nie na osiągniętego wieku emerytalnego. My jako płatnik wysylamy tylko zaświadczenie do ZUS o osiągniętych przychodach? na jakimś konkretnym druku?

3. `2560355c8da7` · grupa_2_507801603233194 · 4 komentarzy
   > Cześć! Chciałam zapytać o to czy pracodawca ma obowiązek wysłać informacje o przychodach zatrudnionych emerytów i rencistów? Jeśli tak to jak to zrobić? Jest do tego jakiś druk?

---

## 60. Odliczenie VAT i księgowanie posiłków oraz cateringu dla pracowników

- **rank**: 60  **score**: 80.2  **cluster_id**: `47`
- **topic_area**: `VAT`
- **size**: 93 postów
- **avg_comments**: 1.15
- **has_many_comments_ratio**: 0.41
- **rekomendacja heurystyczna**: **CONSIDER**
- **decyzja Pawła**: `[WORKFLOW / SKIP / MERGE_WITH_#X]`

> Pytania dotyczą prawa do odliczenia VAT oraz sposobu księgowania wydatków na potrawy, catering, usługi gastronomiczne i artykuły spożywcze (kawa, herbata, pączki) dla pracowników, w tym na spotkania firmowe i wigilijne.

**Keywords**: vat, zakup, koszty, mogę, pracowników, kup, odliczyć, usługa, logo, firmy  **Bigramy**: odliczyć vat, usługa gastronomiczna, odliczyc vat, logo firmy, mogę odliczyć

**Przykładowe posty (z centroidu):**

1. `2fa4bc6ba96a` · ksiegowosc_moja_pasja · 0 komentarzy
   > Witam, zakup potraw na spotkanie z pracownikami. Czy mogę odliczyc VAT? Na jakie konto zaksięgować koszt?

2. `bf5a09c567f2` · ksiegowosc_moja_pasja · 0 komentarzy
   > Witam, zakup potraw na spotkanie z pracownikami. Czy mogę odliczyc VAT? Na jakie konto zaksięgować koszt?Witam, zakup potraw na spotkanie z pracownikami. Czy mogę odliczyc VAT? Na jakie konto zaksięgo…

3. `e84ae58aa7aa` · ksiegowosc_moja_pasja · 2 komentarzy
   > Witam..w spółce zoo zakupiono potrawy na spotkanie wigilijne dla pracowników. Na jakim koncie ująć taki wydatek i co z odliczeniem VAT? Z góry dzięki za odp.

---

## Klastry wykluczone (v2)

Pełna lista **10** klastrów odrzuconych — dla audytu.

| cluster_id | Topic | Size | AvgComm | Label | Powód wykluczenia |
|---:|---|---:|---:|---|---|
| `133` | inne | 394 | 0.91 | Poszukiwanie księgowych, biur rachunkowych i współpracy B2B | decyzja Pawła: out (przegląd v1) |
| `137` | inne | 266 | 1.33 | Kursy księgowości na start: SKwP, KIK i wybór ścieżki | decyzja Pawła: out (przegląd v1) |
| `116` | inne | 175 | 1.66 | Wycena usług księgowych dla JDG i sp. z o.o. | decyzja Pawła: out (przegląd v1) |
| `136` | inne | 84 | 2.24 | Praca w biurze rachunkowym vs księgowość wewnętrzna — wypalenie i zmiana | decyzja Pawła: out (przegląd v1) |
| `115` | inne | 71 | 2.14 | Podwyżki cen w biurach rachunkowych a KSeF i koszty | decyzja Pawła: out (przegląd v1) |
| `0` | inne | 52 | 0.12 | Prośby studentów o wypełnienie ankiet do prac dyplomowych | decyzja Pawła: out (przegląd v1) |
| `28` | inne | 51 | 1.55 | Ubezpieczenie OC księgowych i biur rachunkowych | decyzja Pawła: out (przegląd v1) |
| `11` | inne | 46 | 0.56 | Prośby o udostępnienie płatnych artykułów (Infor, Lex, Gofin) | decyzja Pawła: out (przegląd v1) |
| `129` | inne | 46 | 2.30 | Widełki wynagrodzeń księgowych wg zakresu obowiązków i lokalizacji | decyzja Pawła: out (przegląd v1) |
| `72` | kadry | 44 | 1.41 | Jawność wynagrodzeń i wartościowanie stanowisk: wdrożenie dyrektywy UE | decyzja Pawła: out (przegląd v1) |
