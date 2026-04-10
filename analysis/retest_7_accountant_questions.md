# Retest 7 pytań księgowych

- Wcześniej dobry match: `1/7`
- Teraz dobry match: `5/7`
- Teraz dobry lub częściowy match: `6/7`
- `good`: `5`
- `partial`: `1`
- `gap`: `1`

## 1. Termin złożenia JPK_V7?

- Kategoria: `jpk`
- Ocena: `good`
- Komentarz: Top wynik trafia w termin składania JPK_V7 z ustawy o VAT.
- Kontekst: Powinno trafić w terminy JPK_V7 z ustawy o VAT lub rozporządzenia JPK_V7.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o VAT` | `art. 99 ust. 1-3` | `jpk` | `47.124` | JPK_V7 składa się do 25. dnia miesiąca następującego po okresie rozliczeniowym. Przy rozliczeniu miesięcznym podatnik przesyła JPK_V7M za każdy miesiąc, a pr... |
| `2` | `Rozporządzenie JPK_V7` | `§ 5` | `jpk` | `33.188` | Część deklaracyjna zawiera także oznaczenia i pola techniczne wymagane dla poprawnego złożenia rozliczenia za okres miesięczny albo kwartalny. Podatnik wykaz... |
| `3` | `Rozporządzenie JPK_V7` | `Â§ 12` | `jpk` | `31.7967` | Korektę JPK_V7 składa się za okres, którego dotyczą korygowane dane. Skorygowany plik musi być zgodny z opublikowaną strukturą logiczną i zawierać prawidłowe... |

## 2. Jak księgujecie faktury z Bioestry po zmianie w KSeF

- Kategoria: `ksef`
- Ocena: `good`
- Komentarz: Top wynik trafia w moment wystawienia i otrzymania faktury w KSeF.
- Kontekst: Powinno trafić w KSeF i moment uznania faktury za wystawioną/otrzymaną.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o VAT` | `art. 106na ust. 1 i 3` | `ksef` | `104.0772` | 1. Fakturę ustrukturyzowaną uznaje się za wystawioną w dniu jej przesłania do Krajowego Systemu e-Faktur. 2. (uchylony) 3. Faktura ustrukturyzowana jest uzna... |
| `2` | `Ustawa o VAT - KSeF zwolnienia` | `art. 106ga ust. 2` | `ksef` | `90.7225` | Z obowiązku wystawiania faktur ustrukturyzowanych w KSeF zwolnieni są: podatnicy bez siedziby w Polsce, podatnicy korzystający z procedur szczególnych OSS/IO... |
| `3` | `Ustawa o VAT - KSeF uproszczenia 2026` | `art. 145l` | `ksef` | `81.1381` | Do końca 2026 r. obowiązują uproszczenia: podatnicy mogą wystawiać faktury papierowe lub elektroniczne jeśli łączna sprzedaż w miesiącu nie przekracza 10 000... |

## 3. Ulga dla seniora — czy przysługuje, proporcjonalnie czy za cały rok

- Kategoria: `pit`
- Ocena: `good`
- Komentarz: Top wynik trafia bezpośrednio w ulgę dla seniora.
- Kontekst: Powinno trafić w PIT art. 21 ust. 1 pkt 154.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 21 ust. 1 pkt 154` | `pit` | `87.971` | 154) przychody ze stosunku służbowego, stosunku pracy, pracy nakładczej, spółdzielczego stosunku pracy, z umów zlecenia, o których mowa w art. 13 pkt 8, z za... |
| `2` | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 30l` | `pit` | `24.9173` | 1. Ryczałt wynosi 200 000 zł za rok podatkowy niezależnie od wysokości uzyskanych w tym roku przychodów zagranicznych. 2. Podatnik jest obowiązany wpłacić ry... |
| `3` | `Ustawa o podatku dochodowym od os?b fizycznych` | `art. 26 ust. 7a pkt 12` | `pit` | `14.3801` | W ramach ulgi rehabilitacyjnej można odliczyć wydatki na leki w wysokości stanowiącej różnicę pomiędzy faktycznie poniesionym wydatkiem w danym miesiącu a kw... |

## 4. Usługa budowlana ryczałt 5.5% czy 8.5%

- Kategoria: `ogólne`
- Ocena: `gap`
- Komentarz: Wyniki nadal wpadają w VAT, bo w bazie brakuje ustawy o ryczałcie.
- Kontekst: Brakuje całej ustawy o zryczałtowanym podatku dochodowym, więc dziś to nadal GAP.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o VAT` | `art. 41 ust. 1-3` | `stawka VAT` | `15.6855` | Ustawa o VAT przewiduje wyłącznie stawki: 0%, 5%, 7% i 22%. Stawki 5,5% i 8,5% nie istnieją w prawie polskim. Każda czynność musi być opodatkowana jedną z cz... |
| `2` | `Ustawa o VAT` | `art. 41 ust. 1-2a` | `Stawki VAT` | `15.282` | Ustawa o VAT nie przewiduje stawki 8,5%. Stawkami wynikającymi z ustawy są: 22% (stawka podstawowa), 7%, 5% (dla określonych towarów i usług) oraz 0% (ekspor... |
| `3` | `Ustawa o VAT` | `art. 41 ust. 1-2a` | `Stawki VAT – usługi` | `15.1775` | Ustawa o VAT nie przewiduje stawki 8%. Czyszczenie może podlegać stawce 7% (jeśli jest wymienione w załączniku nr 3) lub 5% (załącznik nr 10), bądź 22% (jeśl... |

## 5. Obowiązek podatkowy PIT i VAT — data wykonania vs data faktury

- Kategoria: `ogólne`
- Ocena: `good`
- Komentarz: Retriever zwraca oba kluczowe przepisy: VAT art. 19a i PIT art. 14 ust. 1c.
- Kontekst: Powinno zwrócić równolegle VAT art. 19a i PIT art. 14 ust. 1c.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o VAT` | `art. 19a ust. 1` | `vat` | `49.7633` | 1. Obowiązek podatkowy powstaje z chwilą dokonania dostawy towarów lub wykonania usługi, z zastrzeżeniem ust. 1a, 1b, 5 i 7–11, art. 14 ust. 6, art. 20, art.... |
| `2` | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 14 ust. 1c` | `pit` | `39.8828` | 1c. Za datę powstania przychodu, o którym mowa w ust. 1, uważa się, z zastrzeżeniem ust. 1e, 1h–1j i 1n–1p, dzień wydania rzeczy, zbycia prawa majątkowego lu... |
| `3` | `Ustawa o VAT` | `art. 19a ust. 1` | `Moment powstania obowiązku podatkowego` | `32.5831` | VAT ujmujesz w miesiącu kwietnia (data wykonania usługi/dostawy - 30 kwietnia), ponieważ obowiązek podatkowy powstaje z chwilą dokonania dostawy lub wykonani... |

## 6. Przeliczenie wynagrodzenia w euro na PLN — jaki kurs

- Kategoria: `ogólne`
- Ocena: `good`
- Komentarz: Top wynik trafia w przeliczanie przychodów w walucie obcej według kursu NBP.
- Kontekst: Powinno trafić w PIT art. 11a.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 11a ust. 1` | `pit` | `34.2551` | 1. Przychody w walutach obcych przelicza się na złote według kursu średniego walut obcych ogłaszanego przez Narodowy Bank Polski z ostatniego dnia roboczego ... |
| `2` | `Ustawa o VAT` | `art. 31a ust. 1` | `przeliczanie_walut_VAT` | `20.577` | Do rozliczenia VAT (również w VIU-DO) kwoty z faktury wyrażone w walucie obcej (np. CZK) przelicza się na PLN, a nie na EUR. Stosuje się kurs średni NBP dane... |
| `3` | `Ustawa o VAT` | `art. 31a ust. 1` | `przeliczanie_waluty_obcej_vat` | `19.6277` | Podatnik VAT przelicza kwoty w walucie obcej na złote według kursu średniego danej waluty ogłoszonego przez NBP na ostatni dzień roboczy poprzedzający dzień ... |

## 7. Sprzedaż bezpośrednia rolnik — zwolnienie z kasy fiskalnej

- Kategoria: `vat`
- Ocena: `partial`
- Komentarz: Top wynik sensownie pokazuje obowiązek ewidencji, ale pełne zwolnienia wymagają rozporządzenia o kasach rejestrujących.
- Kontekst: VAT art. 111 daje część odpowiedzi, ale pełne zwolnienia wymagają rozporządzenia o kasach rejestrujących.

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| `1` | `Ustawa o VAT` | `art. 111 ust. 1` | `vat` | `85.8016` | 1. 1. Podatnicy dokonujący sprzedaży na rzecz osób fizycznych nieprowadzących działalności gospodarczej oraz rolników ryczałtowych są obowiązani prowadzić ew... |
| `2` | `Ustawa o VAT` | `art. 111 ust. 1` | `obowiązek_kasy_rejestrującej` | `51.8776` | Artykuł 111 nie dotyczy limitów zwolnienia od VAT — limit 240 tys. zł znajduje się w art. 113. Obowiązek kasy fiskalnej w art. 111 ust. 1 dotyczy sprzedaży n... |
| `3` | `Ustawa o VAT` | `art. 111 ust. 1` | `kasy_fiskalne` | `50.5725` | Nie musisz mieć kasy fiskalnej przy wystawianiu faktur. Obowiązek prowadzenia ewidencji przy zastosowaniu kas rejestrujących dotyczy sprzedaży na rzecz osób ... |
