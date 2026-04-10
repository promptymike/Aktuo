# KB Unit Quality Diagnostic

- Total units: **4124**
- TYP A (przetworzone): **1172** (28%)
- TYP B (surowe): **2952** (72%)

## Breakdown per ustawa

| Ustawa | TYP A | TYP B | Razem | % A |
| --- | ---: | ---: | ---: | ---: |
| Kodeks pracy | 123 | 308 | 431 | 29% |
| Ordynacja podatkowa | 220 | 542 | 762 | 29% |
| Rozporządzenie JPK_V7 | 3 | 6 | 9 | 33% |
| Rozporządzenie MF o kasach rejestrujących | 0 | 61 | 61 | 0% |
| Ustawa o VAT | 507 | 974 | 1481 | 34% |
| Ustawa o VAT - KSeF terminy wdrożenia | 0 | 1 | 1 | 0% |
| Ustawa o VAT - KSeF uproszczenia 2026 | 1 | 0 | 1 | 100% |
| Ustawa o VAT - KSeF zwolnienia | 0 | 1 | 1 | 0% |
| Ustawa o podatku dochodowym od os?b fizycznych | 206 | 309 | 515 | 40% |
| Ustawa o podatku dochodowym od os?b prawnych | 28 | 31 | 59 | 47% |
| Ustawa o podatku dochodowym od osób fizycznych | 10 | 138 | 148 | 7% |
| Ustawa o podatku dochodowym od osób prawnych | 9 | 159 | 168 | 5% |
| Ustawa o rachunkowości | 37 | 159 | 196 | 19% |
| Ustawa o systemie ubezpieczeń społecznych | 28 | 197 | 225 | 12% |
| Ustawa o zryczałtowanym podatku dochodowym | 0 | 66 | 66 | 0% |
| **SUMA** | **1172** | **2952** | **4124** | **28%** |

## 5 przykładów TYP A (dobre)

**A1.** `Ordynacja podatkowa` | `art. 255` | cat=`ordynacja` | 245 zn.
> Organ podatkowy pierwszej instancji uchyla decyzję, jeżeli została ona wydana z zastrzeżeniem dopełnienia przez stronę określonych czynności, a strona nie dopełniła ich w wyznaczonym terminie. § 2. Or...

**A2.** `Kodeks pracy` | `art. 1881` | cat=`kadry` | 567 zn.
> Pracownik wychowujący dziecko, do ukończenia przez nie 8 roku życia, może złożyć wniosek w postaci papierowej lub elektronicznej o zastosowanie do niego elastycznej organizacji pracy. Wniosek składa s...

**A3.** `Ustawa o VAT` | `art. 19a ust. 1` | cat=`obowiązek podatkowy` | 429 zn.
> Tak, terminy powstania obowiązku podatkowego różnią się zależnie od rodzaju czynności. Ogólnie obowiązek powstaje z chwilą dostawy lub wykonania usługi (art. 19a ust. 1), ale dla energii, usług teleko...

**A4.** `Ustawa o VAT` | `art. 113 ust. 5` | cat=`zwolnienie_vat_maly_podatnik` | 306 zn.
> Zwolnienie traci moc od czynności, którą przekroczono limit 240 tys. zł. Oznacza to, że jeśli limit został przekroczony w grudniu, to czynności od momentu przekroczenia (a nie od 1 stycznia nowego rok...

**A5.** `Ustawa o VAT` | `art. 106q` | cat=`fakturowanie` | 263 zn.
> Minister właściwy do spraw finansów publicznych może określić, w drodze rozporządzenia, późniejsze niż określone w art. 106i terminy wystawiania faktur, uwzględniając specyfikę niektórych rodzajów dzi...

## 5 przykładów TYP B (surowe)

**B1.** `Ordynacja podatkowa` | `art. 20y` | cat=`ordynacja` | 209 zn.
> W okresie 2 lat od dnia rozwiązania umowy o współdziałanie przez Szefa Krajowej Administracji Skarbowej na podstawie art. 20x § 2 podatnik ten nie może złożyć wniosku o zawarcie kolejnej umowy o współ...

**B2.** `Ordynacja podatkowa` | `art. 127` | cat=`ordynacja` | 42 zn.
> Postępowanie podatkowe jest dwuinstancyjne

**B3.** `Ustawa o systemie ubezpieczeń społecznych` | `art. 74` | cat=`zus` | 464 zn.
> 1. Zarząd Zakładu składa się z Prezesa Zakładu oraz z 2–4 osób, powoływanych i odwoływanych przez Radę Nadzorczą Zakładu, na wniosek Prezesa Zakładu. 2. Zarząd kieruje działaniami Zakładu w zakresie n...

**B4.** `Ustawa o podatku dochodowym od osób fizycznych` | `art. 30f` | cat=`pit` | 461 zn.
> 1. Podatek od dochodów zagranicznej jednostki kontrolowanej uzyskanych przez podatnika, o którym mowa w art. 3 ust. 1, wynosi 19 % podstawy obliczenia podatku. 2. Użyte w niniejszym artykule określeni...

**B5.** `Ordynacja podatkowa` | `art. 119za` | cat=`ordynacja` | 290 zn.
> Opinia zabezpieczająca zawiera w szczególności: 1) wyczerpujący opis czynności, której dotyczył wniosek; 2) ocenę, że do wskazanej we wniosku korzyści podatkowej wynikającej z czynności nie ma zastoso...

## Retriever tests

### Przeliczenie wynagrodzenia w euro na PLN jaki kurs
- Kategoria: `ogólne`
- Oczekiwany artykuł: `art. 11a`
- Trafienie w top 5: **TAK**

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| 1 | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 11a ust. 1` | `pit` | 34.6318 | 1. Przychody w walutach obcych przelicza się na złote według kursu średniego walut obcych ogłaszanego przez Narodowy Bank Polski z ostatnieg... |
| 2 | `Ustawa o VAT` | `art. 31a ust. 1` | `przeliczanie_walut_VAT` | 20.7819 | Do rozliczenia VAT (również w VIU-DO) kwoty z faktury wyrażone w walucie obcej (np. CZK) przelicza się na PLN, a nie na EUR. Stosuje się kur... |
| 3 | `Ustawa o VAT` | `art. 31a ust. 1` | `przeliczanie_waluty_obcej_vat` | 19.8323 | Podatnik VAT przelicza kwoty w walucie obcej na złote według kursu średniego danej waluty ogłoszonego przez NBP na ostatni dzień roboczy pop... |
| 4 | `Ustawa o VAT` | `art. 130c ust. 8` | `procedury_szczególne_oss` | 16.3158 | Podatnik płaci VAT wyłącznie w euro, wskazując numer deklaracji VAT. Jeśli płatności za towary lub usługi dokonywane były w innej walucie, d... |
| 5 | `Ustawa o VAT` | `art. 31a ust. 2` | `przeliczanie waluty obcej - EUR konkretnie` | 15.0283 | Kurs EUR (tak jak każdej waluty) bierzesz z ostatniego dnia roboczego poprzedzającego wystawienie faktury ze średniego kursu NBP (art. 31a u... |

### Ulga dla seniora czy przysługuje
- Kategoria: `pit`
- Oczekiwany artykuł: `art. 21 ust. 1 pkt 154`
- Trafienie w top 5: **TAK**

| # | Ustawa | Artykuł | Kategoria | Score | Preview |
| ---: | --- | --- | --- | ---: | --- |
| 1 | `Ustawa o podatku dochodowym od osób fizycznych` | `art. 21 ust. 1 pkt 154` | `pit` | 47.4619 | 154) przychody ze stosunku służbowego, stosunku pracy, pracy nakładczej, spółdzielczego stosunku pracy, z umów zlecenia, o których mowa w ar... |
| 2 | `Ustawa o podatku dochodowym od os?b fizycznych` | `art. 26 ust. 7a pkt 12` | `pit` | 14.5542 | W ramach ulgi rehabilitacyjnej można odliczyć wydatki na leki w wysokości stanowiącej różnicę pomiędzy faktycznie poniesionym wydatkiem w da... |
| 3 | `Ustawa o podatku dochodowym od os?b fizycznych` | `art. 27f ust. 1-2e` | `pit` | 14.1507 | W pokazanym zakresie art. 27f reguluje ulgę na dzieci przede wszystkim przez odwołanie do małoletniego dziecka, limitów dochodów i szczególn... |
| 4 | `Ustawa o podatku dochodowym od os?b fizycznych` | `art. 26g` | `ulgi_i_odliczenia` | 11.3751 | Tekst art. 26g nie opisuje sytuacji, w której ulga by nie przysługiwała lub nic nie zmieniała. Artykuł jedynie określa, gdzie podatnik wykaz... |
| 5 | `Ustawa o podatku dochodowym od os?b fizycznych` | `art. 27f ust. 2 pkt 1 lit. b` | `ulgi podatkowe` | 11.0106 | Tak, samotna matka może się rozliczać z ulgą na dziecko, jeśli spełnia warunki określone w art. 27f. Jeśli nie pozostaje w związku małżeński... |
