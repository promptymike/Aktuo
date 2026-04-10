# Retest 7 pytań księgowych

- Wcześniej dobry match: `1/7`
- Teraz dobry match: `7/7`
- Teraz dobry lub częściowy match: `7/7`
- `good`: `7`
- `partial`: `0`
- `gap`: `0`

## 1. Termin złożenia JPK_V7?

- Kategoria: `jpk`
- Ocena: `good`
- Komentarz: Top wynik trafia w termin składania JPK_V7 z ustawy o VAT.
- Kontekst: Powinno trafić w terminy JPK_V7 z ustawy o VAT lub rozporządzenia JPK_V7.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o VAT` | `art. 99 ust. 1-3` | `jpk` | `47.5167` | JPK_V7 składa się do 25. dnia miesiąca następującego po okresie rozliczeniowym. Przy rozliczeniu miesięcznym podatnik przesyła JPK_V7M za każdy miesiąc, a pr... |
| `2` | `Rozporządzenie JPK_V7` | `§ 5` | `jpk` | `33.5803` | Część deklaracyjna zawiera także oznaczenia i pola techniczne wymagane dla poprawnego złożenia rozliczenia za okres miesięczny albo kwartalny. Podatnik wykaz... |
| `3` | `Rozporządzenie JPK_V7` | `Â§ 12` | `jpk` | `32.039` | Korektę JPK_V7 składa się za okres, którego dotyczą korygowane dane. Skorygowany plik musi być zgodny z opublikowaną strukturą logiczną i zawierać prawidłowe... |

## 2. Jak księgujecie faktury z Bioestry po zmianie w KSeF

- Kategoria: `ksef`
- Ocena: `good`
- Komentarz: Top wynik trafia w moment wystawienia i otrzymania faktury w KSeF.
- Kontekst: Powinno trafić w KSeF i moment uznania faktury za wystawioną/otrzymaną.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o VAT` | `art. 106na ust. 1 i 3` | `ksef` | `104.5638` | 1. Fakturę ustrukturyzowaną uznaje się za wystawioną w dniu jej przesłania do Krajowego Systemu e-Faktur. 2. (uchylony) 3. Faktura ustrukturyzowana jest uzna... |
| `2` | `Ustawa o VAT - KSeF zwolnienia` | `art. 106ga ust. 2` | `ksef` | `91.3402` | Z obowiązku wystawiania faktur ustrukturyzowanych w KSeF zwolnieni są: podatnicy bez siedziby w Polsce, podatnicy korzystający z procedur szczególnych OSS/IO... |
| `3` | `Ustawa o VAT - KSeF uproszczenia 2026` | `art. 145l` | `ksef` | `81.7942` | Do końca 2026 r. obowiązują uproszczenia: podatnicy mogą wystawiać faktury papierowe lub elektroniczne jeśli łączna sprzedaż w miesiącu nie przekracza 10 000... |

## 3. Ulga dla seniora — czy przysługuje, proporcjonalnie czy za cały rok

- Kategoria: `pit`
- Ocena: `good`
- Komentarz: Top wynik trafia bezpośrednio w ulgę dla seniora.
- Kontekst: Powinno trafić w PIT art. 21 ust. 1 pkt 154.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 21 ust. 1 pkt 154` | `pit` | `88.4801` | 154) przychody ze stosunku służbowego, stosunku pracy, pracy nakładczej, spółdzielczego stosunku pracy, z umów zlecenia, o których mowa w art. 13 pkt 8, z za... |
| `2` | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 30l` | `pit` | `24.8412` | 1. Ryczałt wynosi 200 000 zł za rok podatkowy niezależnie od wysokości uzyskanych w tym roku przychodów zagranicznych. 2. Podatnik jest obowiązany wpłacić ry... |
| `3` | `Ustawa o podatku dochodowym od os?b fizycznych` | `art. 26 ust. 7a pkt 12` | `pit` | `14.5542` | W ramach ulgi rehabilitacyjnej można odliczyć wydatki na leki w wysokości stanowiącej różnicę pomiędzy faktycznie poniesionym wydatkiem w danym miesiącu a kw... |

## 4. Usługa budowlana ryczałt 5.5% czy 8.5%

- Kategoria: `pit`
- Ocena: `good`
- Komentarz: Top wynik trafia w ustawę o ryczałcie — stawki ryczałtu.
- Kontekst: Brakuje całej ustawy o zryczałtowanym podatku dochodowym, więc dziś to nadal GAP.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o zryczałtowanym podatku dochodowym` | `art. 5` | `pit` | `45.9125` | Art. 5. Podatnicy opodatkowani na zasadach okrelonych w ustawie nie maj obowizku prowadzenia ksig, chyba e przepisy ustawy stanowi inaczej. Rozdzial 2 Ryczal... |
| `2` | `Ustawa o zryczałtowanym podatku dochodowym` | `art. 45` | `pit` | `41.829` | Art. 45. 1. Wikariusze lub inni duchowni pelnicy czasowo funkcje proboszczów oplacaj ryczalt wedlug stawek okrelonych w zalczniku nr 5. 2. Osoby duchowne kie... |
| `3` | `Ustawa o zryczałtowanym podatku dochodowym` | `art. 20` | `pit` | `26.8892` | Art. 20. 1. (uchylony) 2. (uchylony) 3. (uchylony) 4. (uchylony) 5. (uchylony) 6. W przypadku likwidacji dzialalnoci gospodarczej, w tym take w formie spólki... |

## 5. Obowiązek podatkowy PIT i VAT — data wykonania vs data faktury

- Kategoria: `ogólne`
- Ocena: `good`
- Komentarz: Retriever zwraca oba kluczowe przepisy: VAT art. 19a i PIT art. 14 ust. 1c.
- Kontekst: Powinno zwrócić równolegle VAT art. 19a i PIT art. 14 ust. 1c.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o VAT` | `art. 19a ust. 1` | `vat` | `50.5252` | 1. Obowiązek podatkowy powstaje z chwilą dokonania dostawy towarów lub wykonania usługi, z zastrzeżeniem ust. 1a, 1b, 5 i 7–11, art. 14 ust. 6, art. 20, art.... |
| `2` | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 14 ust. 1c` | `pit` | `40.5207` | 1c. Za datę powstania przychodu, o którym mowa w ust. 1, uważa się, z zastrzeżeniem ust. 1e, 1h–1j i 1n–1p, dzień wydania rzeczy, zbycia prawa majątkowego lu... |
| `3` | `Ustawa o VAT` | `art. 19a ust. 1` | `Moment powstania obowiązku podatkowego` | `33.1554` | VAT ujmujesz w miesiącu kwietnia (data wykonania usługi/dostawy - 30 kwietnia), ponieważ obowiązek podatkowy powstaje z chwilą dokonania dostawy lub wykonani... |

## 6. Przeliczenie wynagrodzenia w euro na PLN — jaki kurs

- Kategoria: `ogólne`
- Ocena: `good`
- Komentarz: Top wynik trafia w przeliczanie przychodów w walucie obcej według kursu NBP.
- Kontekst: Powinno trafić w PIT art. 11a.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 11a ust. 1` | `pit` | `34.6318` | 1. Przychody w walutach obcych przelicza się na złote według kursu średniego walut obcych ogłaszanego przez Narodowy Bank Polski z ostatniego dnia roboczego ... |
| `2` | `Ustawa o VAT` | `art. 31a ust. 1` | `przeliczanie_walut_VAT` | `20.7819` | Do rozliczenia VAT (również w VIU-DO) kwoty z faktury wyrażone w walucie obcej (np. CZK) przelicza się na PLN, a nie na EUR. Stosuje się kurs średni NBP dane... |
| `3` | `Ustawa o VAT` | `art. 31a ust. 1` | `przeliczanie_waluty_obcej_vat` | `19.8323` | Podatnik VAT przelicza kwoty w walucie obcej na złote według kursu średniego danej waluty ogłoszonego przez NBP na ostatni dzień roboczy poprzedzający dzień ... |

## 7. Sprzedaż bezpośrednia rolnik — zwolnienie z kasy fiskalnej

- Kategoria: `vat`
- Ocena: `good`
- Komentarz: Top wynik trafia w obowiązek ewidencji (art. 111) + rozporządzenie o kasach.
- Kontekst: VAT art. 111 daje część odpowiedzi, ale pełne zwolnienia wymagają rozporządzenia o kasach rejestrujących.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o VAT` | `art. 111 ust. 1` | `vat` | `82.9593` | 1. 1. Podatnicy dokonujący sprzedaży na rzecz osób fizycznych nieprowadzących działalności gospodarczej oraz rolników ryczałtowych są obowiązani prowadzić ew... |
| `2` | `Ustawa o VAT` | `art. 111 ust. 1` | `obowiązek_kasy_rejestrującej` | `46.9367` | Artykuł 111 nie dotyczy limitów zwolnienia od VAT — limit 240 tys. zł znajduje się w art. 113. Obowiązek kasy fiskalnej w art. 111 ust. 1 dotyczy sprzedaży n... |
| `3` | `Rozporządzenie MF o kasach rejestrujących` | `§ 19` | `vat` | `46.935` | § 19. W przypadku zmiany miejsca uywania kasy on-line podatnik zapewnia zapisanie w pamici fiskalnej i pamici chronionej oraz w ksice kasy aktualnych, po dok... |
