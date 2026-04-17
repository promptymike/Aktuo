# FB corpus clustering report

Generated at: 2026-04-17T19:12:40+00:00

## 1. Executive summary

Z 24892 postów w korpusie (Zadanie 1.5d), UMAP (50D, n_neighbors=15, metric=cosine, seed=42) + HDBSCAN(min_cluster_size=35, min_samples=10, metric=euclidean) wyodrębnił **144** klastrów tematycznych. W szumie (cluster=-1) zostało **7897** postów (31.7%). Średnia wielkość klastra: **118.0**.

Klastry wysokiego priorytetu (size ≥ 30 AND avg_comments ≥ 1.5): **42**. To jest wyjściowa pula kandydatów na workflow rekordy w Zadaniu 3.

Embedding: `voyage-3-large` (dim=1024).

## 2. Distribution by topic area

| Topic area | Clusters | Total posts | Avg cluster size | % of corpus |
|---|---:|---:|---:|---:|
| VAT | 12 | 1394 | 116.2 | 5.6% |
| PIT | 15 | 1566 | 104.4 | 6.3% |
| CIT | 4 | 279 | 69.8 | 1.1% |
| ZUS | 20 | 1867 | 93.3 | 7.5% |
| kadry | 55 | 6692 | 121.7 | 26.9% |
| KSeF | 9 | 1610 | 178.9 | 6.5% |
| JPK | 5 | 480 | 96.0 | 1.9% |
| KPiR | 4 | 574 | 143.5 | 2.3% |
| rachunkowość | 5 | 622 | 124.4 | 2.5% |
| software | 5 | 651 | 130.2 | 2.6% |
| inne | 10 | 1260 | 126.0 | 5.1% |

## 3. Top 30 largest clusters

| # | Size | Label | Avg comments | Topic area |
|---:|---:|---|---:|---|
| 1 | 797 | Zaliczanie umów zlecenie i DG do stażu pracy od 2026 | 1.22 | kadry |
| 2 | 493 | Wymiar urlopu wypoczynkowego przy niepełnym etacie i zmianie wymiaru | 1.91 | kadry |
| 3 | 492 | KSeF: data wystawienia a rozliczenie VAT i KPiR | 1.49 | KSeF |
| 4 | 427 | Księgowanie faktur zagranicznych: WNT, import usług i towarów | 1.21 | VAT |
| 5 | 409 | Ewidencja i rozliczanie czasu pracy przy różnych systemach i wymiarach etatu | 1.16 | kadry |
| 6 | 394 | Poszukiwanie księgowych, biur rachunkowych i współpracy B2B | 0.91 | inne |
| 7 | 359 | Leasing samochodu osobowego: limity KUP i odliczenie VAT | 1.44 | PIT |
| 8 | 346 | Korekty faktur w KSeF: ujęcie w JPK i VAT | 1.32 | KSeF |
| 9 | 337 | KSeF: nadawanie uprawnień podmiotom i certyfikaty dla biur rachunkowych | 1.52 | KSeF |
| 10 | 306 | Mały ZUS Plus: ponowne skorzystanie po przerwie i nowe zasady od 2026 | 1.39 | ZUS |
| 11 | 288 | Środki trwałe: jednorazowa amortyzacja vs koszty bezpośrednie | 1.03 | KPiR |
| 12 | 287 | Badania lekarskie po długim L4: kontrolne vs okresowe | 1.56 | kadry |
| 13 | 281 | Urlop macierzyński i rodzicielski: wnioski i 9 tygodni dla ojca | 1.42 | kadry |
| 14 | 271 | Sprawozdania finansowe do KRS/KAS: schematy i składanie | 1.06 | rachunkowość |
| 15 | 266 | Kursy księgowości na start: SKwP, KIK i wybór ścieżki | 1.33 | inne |
| 16 | 248 | Nagroda jubileuszowa po doniesieniu dokumentów do stażu pracy | 1.17 | kadry |
| 17 | 241 | Składka zdrowotna przy zmianie formy opodatkowania i odliczenia ZUS | 1.28 | ZUS |
| 18 | 230 | Wybór programu księgowego: KPiR, pełna księgowość, JDG i spółki | 1.27 | software |
| 19 | 212 | Potrącenia komornicze niealimentacyjne z wynagrodzeń i zleceń | 1.30 | kadry |
| 20 | 198 | Kursy i szkolenia kadrowo-płacowe dla początkujących | 0.85 | kadry |
| 21 | 179 | VAT przy wykupie, sprzedaży i darowiźnie samochodu z firmy | 1.18 | VAT |
| 22 | 179 | Nowe oznaczenia JPK_VAT: BFK vs DI dla faktur WNT, importu i poza KSeF | 1.43 | JPK |
| 23 | 175 | Wycena usług księgowych dla JDG i sp. z o.o. | 1.66 | inne |
| 24 | 172 | Zasiłek opiekuńczy ZUS: wypełnianie Z-15A i prawo do zasiłku | 1.83 | ZUS |
| 25 | 170 | Akta osobowe: archiwizacja, układ i przechowywanie dokumentów | 1.64 | kadry |
| 26 | 168 | Rozliczenie roczne zaliczek PIT-4R/CIT-8: nadpłaty, niedopłaty, odsetki | 1.42 | PIT |
| 27 | 160 | Odbiór dnia wolnego za święto 1 listopada w sobotę | 1.52 | kadry |
| 28 | 159 | Korekty list płac: ZUS, PIT-11 i PPK | 1.22 | kadry |
| 29 | 156 | Benefity pracownicze: oskładkowanie, opodatkowanie i księgowanie na liście płac | 0.95 | kadry |
| 30 | 154 | Opinie i pomoc w obsłudze programów kadrowo-płacowych i ERP | 0.54 | software |

## 4. Top 30 most engaging clusters (size ≥ 20)

| # | Avg comments | Label | Size | Topic area |
|---:|---:|---|---:|---|
| 1 | 2.30 | Widełki wynagrodzeń księgowych wg zakresu obowiązków i lokalizacji | 46 | inne |
| 2 | 2.24 | Praca w biurze rachunkowym vs księgowość wewnętrzna — wypalenie i zmiana | 84 | inne |
| 3 | 2.20 | KSeF: panika klientów i przygotowanie biur rachunkowych | 59 | KSeF |
| 4 | 2.14 | Podwyżki cen w biurach rachunkowych a KSeF i koszty | 71 | inne |
| 5 | 2.00 | Kontrola ZUS i PIP: przygotowanie dokumentów i zakres sprawdzania | 35 | ZUS |
| 6 | 1.91 | Wymiar urlopu wypoczynkowego przy niepełnym etacie i zmianie wymiaru | 493 | kadry |
| 7 | 1.89 | KSeF: obieg, archiwizacja i weryfikacja faktur w biurze | 109 | KSeF |
| 8 | 1.87 | Zwolnienia lekarskie L4: nietypowe sytuacje i brak e-ZLA | 62 | kadry |
| 9 | 1.84 | Urlop wypoczynkowy przy kończącej się umowie i 14 dni ciągłych | 71 | kadry |
| 10 | 1.83 | Zasiłek opiekuńczy ZUS: wypełnianie Z-15A i prawo do zasiłku | 172 | ZUS |
| 11 | 1.81 | Umowa zlecenie ze studentem/uczniem do 26 r.ż. - składki ZUS | 100 | ZUS |
| 12 | 1.79 | Przejście roku: wynagrodzenie chorobowe vs zasiłek i okres zasiłkowy | 121 | kadry |
| 13 | 1.78 | Umowa o pracę: data zawarcia a dzień rozpoczęcia pracy w dzień wolny | 65 | kadry |
| 14 | 1.78 | Rozwiązanie umowy z art. 53 KP po 182 dniach zasiłku i świadczeniu rehabilitacyjnym | 59 | kadry |
| 15 | 1.73 | Świadectwo pracy: duplikaty, kopie i sprostowania | 40 | kadry |
| 16 | 1.71 | KUP przy wypłacie po ustaniu zatrudnienia i korekta PIT-11 | 56 | PIT |
| 17 | 1.70 | Rozliczanie sprzedaży Allegro: powiązanie wpłat z fakturami | 74 | rachunkowość |
| 18 | 1.70 | KSeF: duplikaty faktur zakupowych i numer KSeF | 79 | KSeF |
| 19 | 1.69 | Opieka nad dzieckiem art. 188 i przerwa na karmienie | 36 | kadry |
| 20 | 1.66 | Wycena usług księgowych dla JDG i sp. z o.o. | 175 | inne |
| 21 | 1.65 | Czynny żal przy spóźnionych deklaracjach (PIT-11, PIT-4R, JPK) | 75 | inne |
| 22 | 1.65 | KSeF: obowiązek dla nievatowców, zwolnionych z VAT i limitu 10 tys. | 83 | KSeF |
| 23 | 1.64 | Akta osobowe: archiwizacja, układ i przechowywanie dokumentów | 170 | kadry |
| 24 | 1.63 | Wypadki przy pracy i w drodze: zasiłek 100% i dokumentacja | 57 | ZUS |
| 25 | 1.62 | ZUS IWA: ustalanie liczby ubezpieczonych i stopy wypadkowej | 37 | ZUS |
| 26 | 1.61 | Urlop wypoczynkowy a urlop wychowawczy i rodzicielski - wymiar proporcjonalny | 57 | kadry |
| 27 | 1.60 | Umowa na zastępstwo: zawieranie, przedłużanie i rozwiązywanie | 38 | kadry |
| 28 | 1.57 | Ustalanie okresu wypowiedzenia umowy o pracę wg stażu | 73 | kadry |
| 29 | 1.57 | Awarie e-Deklaracji i bramki JPK: problemy z wysyłką i UPO | 77 | software |
| 30 | 1.57 | Rozwiązanie umowy: likwidacja stanowiska, porozumienie stron a zasiłek | 90 | kadry |

## 5. Noise analysis

Postów w szumie: **7897** (31.7% korpusu). Poniżej 10 losowych (seed=42) — dla oceny czy tracimy sygnał czy to legitny szum.

- **07f9ab4bfbdc** · grupa_2_507801603233194 · comments: 0
  > Dzień dobry, pracownik sprzątający ma umowę zlecenie. Czy może podpisać drugą umowę zlecenia z tym samym pracodawcą również na utrzymanie czystości i porządku ale zadania te wykonywane będą w innym miejscu? Dziękuję
- **42599e789649** · ksiegowosc_moja_pasja · comments: 2
  > Dzień dobry, ma pytanie. Dochód z mężem ponad 120 tys.  Mamy 1 dziecko. Jak  się rozliczam razem z mężem w epitach przechodzi ulga na dziecko.  Czy program epity powinien zauważyć że jest przekroczony dochód? Jak myślicie czy urząd mimo przekroczenia dochodu nie będzie się czepia…
- **96419dacca44** · ksiegowosc_moja_pasja · comments: 0
  > UEPiK a Optima; czy ktoś z Państwa proawdzi UEPiK w Optimie? JEśli tak to na jakim module KPiR czy robi to w KSIĘGI HANDLOWE?
- **fb43f56a193b** · grupa_2_507801603233194 · comments: 0
  > Witam. Pierwszy raz robię sprawozdanie do PFR odnośnie PPE.Czy do liczby zatrudnionych wliczamy UoP + UZ? I co z osobami na macierzyńskim/wychowawczym?Witam. Pierwszy raz robię sprawozdanie do PFR odnośnie PPE.Czy do liczby zatrudnionych wliczamy UoP + UZ? I co z osobami na macie…
- **f1693056caf6** · ksiegowosc_moja_pasja · comments: 2
  > #KSEF  czy jest możliwe od 1 kwietnia wystawić faktury tak jak do tej pory.  A później zebrać i wrzucić w KSEF żeby zdążyć do północy? Jest faktur niewiele
- **d57cdac79532** · ksiegowosc_moja_pasja · comments: 0
  > Mam fakturę krajową w euro z vatem. System przelicza mi zobowiązanie na złotówki licząc sumę pozycji: Netto po kursie CIT plus VAT po kursie VAT. Czy ja źle mysle, że wycena zobowiązania w księgach powinna być po jednym kursie (netto plus VAT) razy kurs CIT?
- **8f30887c53c7** · ksiegowosc_moja_pasja · comments: 2
  > Edit: Dziękuję życzliwym za pomoc, już wiem jak robić to poprawnie i legalnie. Pozdrawiam i życzę jak najwięcej życzliwości  Jak przychodzi do was obca osoba żeby rozliczyc jej pit to jak to robicie? (Pytam księgowych, biur rachunkowych)  Bo chyba nie składa ta osoba pełnomocnict…
- **6d291bfdf4a7** · ksiegowosc_moja_pasja · comments: 2
  > Czy mozna wystąpić o zwrot Vat jesli faktury są nieopłacone?
- **0e6cc4122273** · grupa_2_507801603233194 · comments: 0
  > Czy jezeli pracodawca chce pokryc czesc kosztow za okulary pracownika to pracownik musi miec zaświadczenie ze musi pracowac w okularach ??  I czym kwote dofinansowania za okulary wprowadzic jakims regulaminem np. Ze bede zwracane koszty za okulary w kwocie np 100 zl raz na 3 lata…
- **a0fe00a8c09f** · ksiegowosc_moja_pasja · comments: 0
  > Złożyłem wniosek USP na stronie ZUS aby działalność doliczyć do stażu pracy. Czekam już prawie tydzień i nie ma w skrzynce odbiorczej odpowiedzi. Ile to może trwać?

## 6. Coverage check by topic area

- **VAT**: 12 klastrów. Przykłady: `Księgowanie faktur zagranicznych: WNT, import usług i towarów` (427); `VAT przy wykupie, sprzedaży i darowiźnie samochodu z firmy` (179); `Najem prywatny a VAT, KSeF i JDG` (143)
- **PIT**: 15 klastrów. Przykłady: `Leasing samochodu osobowego: limity KUP i odliczenie VAT` (359); `Rozliczenie roczne zaliczek PIT-4R/CIT-8: nadpłaty, niedopłaty, odsetki` (168); `PIT: ulga na dziecko i rozliczenie samotnego rodzica - limity dochodów` (150)
- **CIT**: 4 klastrów. Przykłady: `Certyfikaty rezydencji podatkowej zagranicznych dostawców usług cyfrowych` (95); `Dotacje i darowizny: rozliczenie przychodów i kosztów w CIT/PIT` (76); `IFT-2R i WHT od subskrypcji zagranicznych (Adobe, Canva, Google, Meta, OpenAI)` (57)
- **ZUS**: 20 klastrów. Przykłady: `Mały ZUS Plus: ponowne skorzystanie po przerwie i nowe zasady od 2026` (306); `Składka zdrowotna przy zmianie formy opodatkowania i odliczenia ZUS` (241); `Zasiłek opiekuńczy ZUS: wypełnianie Z-15A i prawo do zasiłku` (172)
- **kadry**: 55 klastrów. Przykłady: `Zaliczanie umów zlecenie i DG do stażu pracy od 2026` (797); `Wymiar urlopu wypoczynkowego przy niepełnym etacie i zmianie wymiaru` (493); `Ewidencja i rozliczanie czasu pracy przy różnych systemach i wymiarach etatu` (409)
- **KSeF**: 9 klastrów. Przykłady: `KSeF: data wystawienia a rozliczenie VAT i KPiR` (492); `Korekty faktur w KSeF: ujęcie w JPK i VAT` (346); `KSeF: nadawanie uprawnień podmiotom i certyfikaty dla biur rachunkowych` (337)
- **JPK**: 5 klastrów. Przykłady: `Nowe oznaczenia JPK_VAT: BFK vs DI dla faktur WNT, importu i poza KSeF` (179); `JPK_CIT: znaczniki kont i moment ich nadania` (148); `JPK_VAT i JPK_KPiR 2026: prefiks PL i dane kontrahenta` (76)
- **KPiR**: 4 klastrów. Przykłady: `Środki trwałe: jednorazowa amortyzacja vs koszty bezpośrednie` (288); `KPiR 2026: księgowanie faktur do paragonu i sprzedaży detalicznej` (123); `Kaucje za butelki w KPiR i VAT (system kaucyjny)` (102)
- **rachunkowość**: 5 klastrów. Przykłady: `Sprawozdania finansowe do KRS/KAS: schematy i składanie` (271); `Przejęcie księgowości: korekta błędnych sald rozrachunków z BO` (134); `Różnice kursowe: faktury walutowe i przewalutowania` (75)
- **software**: 5 klastrów. Przykłady: `Wybór programu księgowego: KPiR, pełna księgowość, JDG i spółki` (230); `Opinie i pomoc w obsłudze programów kadrowo-płacowych i ERP` (154); `Awarie PUE ZUS, Płatnika i e-deklaracji: problemy z logowaniem` (119)
- **inne**: 10 klastrów. Przykłady: `Poszukiwanie księgowych, biur rachunkowych i współpracy B2B` (394); `Kursy księgowości na start: SKwP, KIK i wybór ścieżki` (266); `Wycena usług księgowych dla JDG i sp. z o.o.` (175)

## 7. Recommended top 50 clusters for workflow (Zadanie 3)

Ranking score: `size * 0.4 + avg_comments * 10 * 0.4 + topic_boost * 100 * 0.2` (boost dla ['KPiR', 'KSeF', 'VAT', 'ZUS']).

| # | Score | Label | Description | Size | Avg comments | Topic |
|---:|---:|---|---|---:|---:|---|
| 1 | 323.7 | Zaliczanie umów zlecenie i DG do stażu pracy od 2026 | Pytania dotyczą nowych zasad wliczania do stażu pracy okresów umów zlecenia (także studenckich) oraz prowadzenia działalności gospodarczej,… | 797 | 1.22 | kadry |
| 2 | 222.8 | KSeF: data wystawienia a rozliczenie VAT i KPiR | Pytania dotyczą tego, którą datę (wystawienia faktury, przesłania do KSeF, sprzedaży/wykonania usługi) należy przyjąć do rozliczenia VAT i u… | 492 | 1.49 | KSeF |
| 3 | 204.8 | Wymiar urlopu wypoczynkowego przy niepełnym etacie i zmianie wymiaru | Pytania dotyczą proporcjonalnego naliczania urlopu wypoczynkowego dla pracowników zatrudnionych na część etatu (1/2, 3/4, 5/8) oraz przelicz… | 493 | 1.91 | kadry |
| 4 | 195.7 | Księgowanie faktur zagranicznych: WNT, import usług i towarów | Pytania dotyczą prawidłowego rozliczenia VAT od faktur zakupowych od kontrahentów z UE i spoza UE, w tym klasyfikacji jako WNT, import usług… | 427 | 1.21 | VAT |
| 5 | 168.2 | Ewidencja i rozliczanie czasu pracy przy różnych systemach i wymiarach etatu | Pytania dotyczą rozliczania czasu pracy pracowników w systemach równoważnym i zadaniowym, ustalania grafików przy niepełnych etatach oraz id… | 409 | 1.16 | kadry |
| 6 | 163.7 | Korekty faktur w KSeF: ujęcie w JPK i VAT | Pytania dotyczą prawidłowego ujęcia faktur korygujących wystawionych w KSeF w innym okresie niż faktura pierwotna - zwłaszcza korekt danych… | 346 | 1.32 | KSeF |
| 7 | 161.2 | Poszukiwanie księgowych, biur rachunkowych i współpracy B2B | Pytania dotyczą ogłoszeń o poszukiwaniu pracy w księgowości, zleceń dla biur rachunkowych oraz osób do pomocy przy rozliczeniach JDG, spółek… | 394 | 0.91 | inne |
| 8 | 160.9 | KSeF: nadawanie uprawnień podmiotom i certyfikaty dla biur rachunkowych | Pytania dotyczą problemów z nadawaniem i weryfikacją uprawnień w KSeF — zwłaszcza dla biur rachunkowych będących spółkami, logowania przez Z… | 337 | 1.52 | KSeF |
| 9 | 149.4 | Leasing samochodu osobowego: limity KUP i odliczenie VAT | Pytania dotyczą rozliczania rat leasingu operacyjnego samochodów osobowych — stosowania limitu 150/100 tys. zł w kosztach, proporcji 75%/100… | 359 | 1.44 | PIT |
| 10 | 148.0 | Mały ZUS Plus: ponowne skorzystanie po przerwie i nowe zasady od 2026 | Pytania dotyczą warunków powrotu do ulgi Mały ZUS Plus po wykorzystaniu limitu 36/48 miesięcy, wpływu zawieszenia działalności oraz nowych z… | 306 | 1.39 | ZUS |
| 11 | 139.3 | Środki trwałe: jednorazowa amortyzacja vs koszty bezpośrednie | Pytania dotyczą kwalifikacji zakupów do środków trwałych, wyboru między jednorazową amortyzacją a ujęciem bezpośrednio w kosztach, ulepszeń… | 288 | 1.03 | KPiR |
| 12 | 121.5 | Składka zdrowotna przy zmianie formy opodatkowania i odliczenia ZUS | Pytania dotyczą ustalania podstawy i wysokości składki zdrowotnej (głównie na ryczałcie i po zmianie formy opodatkowania) oraz zasad odlicza… | 241 | 1.28 | ZUS |
| 13 | 121.1 | Badania lekarskie po długim L4: kontrolne vs okresowe | Pytania dotyczą kierowania pracowników na badania profilaktyczne (kontrolne, okresowe, wstępne) po zwolnieniu lekarskim, utraty ważności bad… | 287 | 1.56 | kadry |
| 14 | 118.1 | Urlop macierzyński i rodzicielski: wnioski i 9 tygodni dla ojca | Pytania dotyczą zasad wnioskowania o urlop macierzyński i rodzicielski, w tym nieprzenoszalnej części 9 tygodni dla ojca, sytuacji gdy matka… | 281 | 1.42 | kadry |
| 15 | 112.6 | Sprawozdania finansowe do KRS/KAS: schematy i składanie | Pytania dotyczą sporządzania i wysyłki sprawozdań finansowych za 2025 rok - wyboru wersji schematu (1.3 vs 2.1), sposobu składania do KRS/KA… | 271 | 1.06 | rachunkowość |
| 16 | 111.7 | Kursy księgowości na start: SKwP, KIK i wybór ścieżki | Pytania początkujących i osób przebranżawiających się o wybór kursów księgowych (głównie SKwP i Krajowa Izba Księgowych), ich przydatność w… | 266 | 1.33 | inne |
| 17 | 103.9 | Nagroda jubileuszowa po doniesieniu dokumentów do stażu pracy | Pytania dotyczą wypłaty nagrody jubileuszowej dla pracowników samorządowych, którzy w trakcie zatrudnienia dostarczyli zaświadczenia z ZUS (… | 248 | 1.17 | kadry |
| 18 | 97.1 | Wybór programu księgowego: KPiR, pełna księgowość, JDG i spółki | Użytkownicy proszą o rekomendacje programów do prowadzenia księgowości (JDG, spółek, pełnej księgowości, ryczałtu) z uwzględnieniem ceny, fu… | 230 | 1.27 | software |
| 19 | 96.3 | VAT przy wykupie, sprzedaży i darowiźnie samochodu z firmy | Pytania dotyczą skutków VAT przy wykupie samochodu z leasingu, przekazaniu na cele prywatne, darowiźnie oraz sprzedaży auta firmowego, w tym… | 179 | 1.18 | VAT |
| 20 | 96.1 | Zasiłek opiekuńczy ZUS: wypełnianie Z-15A i prawo do zasiłku | Pytania dotyczą ustalania prawa do zasiłku opiekuńczego na chore lub zdrowe dziecko oraz sposobu wypełniania wniosku Z-15A w sytuacjach taki… | 172 | 1.83 | ZUS |
| 21 | 90.0 | Potrącenia komornicze niealimentacyjne z wynagrodzeń i zleceń | Pytania dotyczą zasad dokonywania zajęć komorniczych niealimentacyjnych: obliczania kwot potrąceń, stosowania kwoty wolnej, traktowania umów… | 212 | 1.30 | kadry |
| 22 | 82.6 | Kursy i szkolenia kadrowo-płacowe dla początkujących | Pytania dotyczą rekomendacji kursów i szkoleń z zakresu kadr i płac – stacjonarnych, online, weekendowych, w tym szkoleń z Płatnika oraz dla… | 198 | 0.85 | kadry |
| 23 | 82.0 | Najem prywatny a VAT, KSeF i JDG | Pytania dotyczą rozliczania najmu prywatnego w kontekście VAT, obowiązku wysyłki faktur do KSeF oraz relacji między najmem prywatnym a prowa… | 143 | 1.20 | VAT |
| 24 | 77.3 | Nowe oznaczenia JPK_VAT: BFK vs DI dla faktur WNT, importu i poza KSeF | Pytania dotyczą prawidłowego stosowania nowych znaczników BFK i DI w ewidencji JPK_VAT od lutego 2026 dla faktur WNT, importu usług, faktur… | 179 | 1.43 | JPK |
| 25 | 76.6 | Wycena usług księgowych dla JDG i sp. z o.o. | Pytania dotyczą ustalenia stawek za obsługę księgową różnych podmiotów (JDG, sp. z o.o., fundacje) w oparciu o liczbę dokumentów, pracownikó… | 175 | 1.66 | inne |
| 26 | 74.9 | KPiR 2026: księgowanie faktur do paragonu i sprzedaży detalicznej | Pytania dotyczą nowych zasad ewidencjonowania w KPiR od 2026 r. faktur wystawianych do paragonów (w tym dla osób fizycznych) oraz sprzedaży… | 123 | 1.42 | KPiR |
| 27 | 74.5 | Akta osobowe: archiwizacja, układ i przechowywanie dokumentów | Pytania dotyczą prowadzenia akt osobowych pracowników - gdzie wpinać poszczególne dokumenty (ZUS, listy płac, badania lekarskie), jak je arc… | 170 | 1.64 | kadry |
| 28 | 74.3 | Powrót do zwolnienia VAT po podniesieniu limitu do 240 tys. | Pytania dotyczą podatników, którzy przekroczyli limit 200 tys. zł pod koniec 2025 r. i zarejestrowali się do VAT, a chcą skorzystać z przepi… | 123 | 1.28 | VAT |
| 29 | 72.9 | Rozliczenie roczne zaliczek PIT-4R/CIT-8: nadpłaty, niedopłaty, odsetki | Pytania dotyczą rozbieżności między zaliczkami miesięcznymi wpłaconymi do US a kwotami wykazanymi w deklaracjach rocznych (PIT-4R, PIT-8AR,… | 168 | 1.42 | PIT |
| 30 | 71.2 | KSeF: obieg, archiwizacja i weryfikacja faktur w biurze | Pytania dotyczą praktycznej organizacji pracy z KSeF w biurach rachunkowych i firmach: jak weryfikować i archiwizować faktury, czy je drukow… | 109 | 1.89 | KSeF |
| 31 | 70.1 | Odbiór dnia wolnego za święto 1 listopada w sobotę | Pytania dotyczą zasad udzielania i odbioru dnia wolnego za święto przypadające w sobotę (głównie 1 listopada) w różnych sytuacjach pracownic… | 160 | 1.52 | kadry |
| 32 | 68.9 | ZUS Z-3: wynagrodzenie i zasiłek chorobowy przy firmach <20 pracowników | Pytania dotyczą rozliczania zwolnień lekarskich w firmach zatrudniających poniżej 20 osób – kiedy pracodawca wypłaca wynagrodzenie chorobowe… | 108 | 1.44 | ZUS |
| 33 | 68.5 | Korekty list płac: ZUS, PIT-11 i PPK | Pytania dotyczą sposobu przeprowadzania korekt wynagrodzeń pracowników (nadpłaty, niedopłaty, błędne zasiłki, przekroczenie 30-krotności) or… | 159 | 1.22 | kadry |
| 34 | 67.2 | Umowa zlecenie ze studentem/uczniem do 26 r.ż. - składki ZUS | Pytania dotyczą zwolnienia ze składek ZUS przy umowach zlecenia zawieranych ze studentami i uczniami do 26 roku życia, w tym wymaganej dokum… | 100 | 1.81 | ZUS |
| 35 | 66.2 | Benefity pracownicze: oskładkowanie, opodatkowanie i księgowanie na liście płac | Pytania dotyczą rozliczania pakietów medycznych, kart sportowych (Multisport, Pluxee) oraz ubezpieczeń grupowych finansowanych lub współfina… | 156 | 0.95 | kadry |
| 36 | 65.5 | Kaucje za butelki w KPiR i VAT (system kaucyjny) | Pytania dotyczą księgowania kaucji za opakowania (butelki szklane i plastikowe) w KPiR oraz ujęcia ich w rejestrach VAT, szczególnie w konte… | 102 | 1.17 | KPiR |
| 37 | 65.4 | PIT: ulga na dziecko i rozliczenie samotnego rodzica - limity dochodów | Pytania dotyczą warunków skorzystania z ulgi prorodzinnej na jedno dziecko oraz rozliczenia jako samotnie wychowujący rodzic, w kontekście l… | 150 | 1.36 | PIT |
| 38 | 64.7 | Zasiłek macierzyński a zgłoszenia ZUS: zlecenie, działalność, etat | Pytania dotyczą obsługi ZUS w trakcie i po zasiłku macierzyńskim — kodów zgłoszeniowych (ZZA/ZWUA), wykazywania pracownika na RCA/RSA, przer… | 98 | 1.37 | ZUS |
| 39 | 64.6 | ZUS Płatnik/PUE: błędy krytyczne przy wysyłce deklaracji i korekt DRA/RCA | Księgowi zgłaszają problemy techniczne z wysyłką deklaracji ZUS (DRA, RCA, ZWUA, zgłoszenia) – błędy krytyczne o niepotwierdzonych danych pł… | 97 | 1.45 | ZUS |
| 40 | 64.0 | JPK_CIT: znaczniki kont i moment ich nadania | Pytania dotyczą oznaczania kont (znaczników podatkowych, KUP/NKUP, kont pozabilansowych) na potrzeby JPK_KR_PD/JPK_CIT — kiedy je nadać, jak… | 148 | 1.19 | JPK |
| 41 | 63.8 | Opinie i pomoc w obsłudze programów kadrowo-płacowych i ERP | Użytkownicy pytają o doświadczenia i szukają pomocy w konkretnych programach do kadr, płac, księgowości i ewidencji czasu pracy (m.in. Bizne… | 154 | 0.54 | software |
| 42 | 63.4 | Delegowanie i podróże służbowe pracowników za granicę: ZUS, podatek, A1 | Pytania dotyczą rozliczania pracowników i zleceniobiorców wysyłanych do pracy za granicę (Holandia, Niemcy, Czechy, Szwecja, Norwegia) — pro… | 153 | 0.56 | kadry |
| 43 | 62.4 | Zbieg tytułów ubezpieczeń przy umowach zlecenie | Pytania dotyczą ustalania, jakie składki ZUS (społeczne, chorobowe, zdrowotna) należy odprowadzać od zleceniobiorców w przypadku zbiegu tytu… | 91 | 1.50 | ZUS |
| 44 | 61.8 | Odliczenie VAT i księgowanie posiłków oraz cateringu dla pracowników | Pytania dotyczą prawa do odliczenia VAT oraz sposobu księgowania wydatków na potrawy, catering, usługi gastronomiczne i artykuły spożywcze (… | 93 | 1.15 | VAT |
| 45 | 61.8 | Zatrudnianie obywateli Ukrainy: formalności i dokumenty | Pytania dotyczą obowiązków pracodawcy przy zatrudnianiu obywateli Ukrainy — wymaganych dokumentów (paszport, karta pobytu, PESEL UKR), powia… | 140 | 1.44 | kadry |
| 46 | 61.8 | Ryczałt: dobór stawki wg rodzaju usługi (IT, hydraulik, catering, BHP, księgowość) | Pytania dotyczą ustalenia właściwej stawki ryczałtu ewidencjonowanego (3%, 5,5%, 8,5%, 12%, 17%) dla konkretnych usług oraz dopasowania jej… | 144 | 1.04 | PIT |
| 47 | 60.9 | ZUS: zaświadczenie o przychodach emerytów i rencistów do końca lutego | Pytania dotyczą obowiązku płatnika składania do ZUS rocznego zaświadczenia o przychodach zatrudnionych emerytów i rencistów – kogo obejmuje… | 90 | 1.22 | ZUS |
| 48 | 59.8 | KSeF: obowiązek dla nievatowców, zwolnionych z VAT i limitu 10 tys. | Pytania dotyczą tego, kto i w jakich sytuacjach musi korzystać z KSeF — w szczególności podatników zwolnionych z VAT, nievatowców wystawiają… | 83 | 1.65 | KSeF |
| 49 | 59.5 | Przejęcie księgowości: korekta błędnych sald rozrachunków z BO | Pytania dotyczą sposobu wyjaśnienia i wyksięgowania nieprawidłowych sald kont rozrachunkowych (z dostawcami, US, kontrahentami UE, kasą) prz… | 134 | 1.48 | rachunkowość |
| 50 | 58.8 | Minimalne wynagrodzenie 2026: regulamin i składniki płacy | Pytania dotyczą zmian minimalnego wynagrodzenia od 1 stycznia 2026, konieczności aktualizacji regulaminu wynagradzania i tabel zaszeregowani… | 137 | 0.99 | kadry |

## 8. Unrelated observations

- **Pivot pipeline-u: HDBSCAN na raw 1024D voyage embeddingach cosine dawał 3-6 mega-klastrów (curse of dimensionality). Rozwiązanie: UMAP 1024D→50D (n_neighbors=15, min_dist=0.0, metric=cosine, seed=42) przed HDBSCAN (metric=euclidean). Po 6 iteracjach parametrów wybrano min_cluster_size=35, min_samples=10 jako najlepszy kompromis między liczbą klastrów (144, w targecie 80-150) a szumem (31.7%, plateau nie do obniżenia przez dalszy tuning).
- Dalsza kontrola jakości klastrów manualna: review top-30 largest i top-30 engaging, oznacz te które faktycznie łapią pojedynczy workflow vs. te które są za szerokie.
- Komentarze-jako-posty (problem z Zadania 1.5) mogą tworzyć osobne klastry — szukaj labeli typu 'komentarze/opinie' albo klastrów z nienaturalnie wysokim avg_comments_count.
- Klaster `inne` (10 klastrów, 1260 postów) jest dobrym kandydatem do dalszej inspekcji — może ukrywać tematy pominięte przez heurystyczny mapping topic_area.
