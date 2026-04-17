# Duplicate Groups Report

- **Scan date:** 2026-04-17
- **Total records scanned:** 4544
- **Total duplicate groups (count  2):** 407
- **Thresholds:** true_duplicate  min Jaccard  0.85; near_duplicate  [0.6, 0.85); legitimate_variants  < 0.6

## Classification summary

| classification | groups |
|---|---:|
| true_duplicate | 60 |
| near_duplicate | 12 |
| legitimate_variants | 335 |

## Records impact

| metric | value |
|---|---:|
| would_remove_if_dedupe_true_duplicates | 72 |
| would_remove_if_dedupe_true_and_near | 92 |
| final_kb_size_after_true_dedupe | 4472 |
| final_kb_size_after_true_and_near_dedupe | 4452 |

## Potential key collisions (count > 10)

| group_key | count | classification |
|---|---:|---|
| Ustawa o VAT | art. 86 ust. 1 | 55 | legitimate_variants |
| Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | 40 | legitimate_variants |
| Ustawa o VAT | art. 19a ust. 1 | 33 | legitimate_variants |
| Ustawa o VAT | art. 106gb | 30 | legitimate_variants |
| Ustawa o VAT | art. 41 ust. 1 | 25 | legitimate_variants |
| Ustawa o VAT | art. 106i ust. 1 | 22 | legitimate_variants |
| Ustawa o VAT | art. 103 ust. 1 | 19 | legitimate_variants |
| Ustawa o VAT | art. 111 ust. 1 | 19 | legitimate_variants |
| Ustawa o VAT | art. 113 ust. 1 | 19 | legitimate_variants |
| Ustawa o VAT | art. 86 ust. 10b pkt 1 | 18 | legitimate_variants |
| Ustawa o VAT | art. 106j ust. 1 | 16 | legitimate_variants |
| Ustawa o VAT | art. 106e ust. 1 | 15 | legitimate_variants |
| Ustawa o VAT | art. 96 ust. 1 | 14 | legitimate_variants |
| Ustawa o VAT | art. 106gb ust. 1 | 13 | legitimate_variants |
| Ustawa o podatku dochodowym od osób fizycznych | art. 30 | 13 | legitimate_variants |
| Ustawa o podatku dochodowym od osób fizycznych | art. 7 ust. 1 | 13 | legitimate_variants |
| Ustawa o VAT | art. 106b ust. 1 pkt 1 | 12 | legitimate_variants |
| Ustawa o VAT | art. 86a ust. 1 | 12 | legitimate_variants |
| Ustawa o VAT | art. 99 ust. 1 | 12 | legitimate_variants |
| Ustawa o podatku dochodowym od osób fizycznych | art. 26e | 12 | legitimate_variants |
| Ustawa o VAT | art. 15 ust. 1 | 11 | legitimate_variants |
| Ustawa o VAT | art. 87 ust. 1 | 11 | legitimate_variants |

## Top 10 largest groups (by count)

| group_key | count | classification | min_sim | avg_sim |
|---|---:|---|---:|---:|
| Ustawa o VAT | art. 86 ust. 1 | 55 | legitimate_variants | 0.0139 | 0.1512 |
| Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | 40 | legitimate_variants | 0.0119 | 0.1175 |
| Ustawa o VAT | art. 19a ust. 1 | 33 | legitimate_variants | 0.0143 | 0.1902 |
| Ustawa o VAT | art. 106gb | 30 | legitimate_variants | 0.033 | 0.1767 |
| Ustawa o VAT | art. 41 ust. 1 | 25 | legitimate_variants | 0.0543 | 0.1866 |
| Ustawa o VAT | art. 106i ust. 1 | 22 | legitimate_variants | 0.0235 | 0.1812 |
| Ustawa o VAT | art. 103 ust. 1 | 19 | legitimate_variants | 0.0241 | 0.1889 |
| Ustawa o VAT | art. 111 ust. 1 | 19 | legitimate_variants | 0.0366 | 0.1623 |
| Ustawa o VAT | art. 113 ust. 1 | 19 | legitimate_variants | 0.0435 | 0.1486 |
| Ustawa o VAT | art. 86 ust. 10b pkt 1 | 18 | legitimate_variants | 0.1412 | 0.2651 |

## Top 10 true_duplicate groups (with content previews)

### Kodeks pracy | art. 221  count=3, min_sim=0.9559, avg_sim=0.9706

- **[0]** `law_knowledge.json` idx=215  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 221. § 1. Pracodawca żąda od osoby ubiegającej się o zatrudnienie podania danych osobowych obejmujących: 1) imię (imiona) i nazwisko; 2) datę uro
- **[1]** `law_knowledge.json` idx=216  source: `parsed_article_gap_patch`  verified_date: ``
  - content: Pracodawca żąda od osoby ubiegającej się o zatrudnienie podania danych osobowych obejmujących: 1) imię (imiona) i nazwisko; 2) datę urodzenia; 3) dane
- **[2]** `law_knowledge_curated_additions.json` idx=8  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 221. § 1. Pracodawca żąda od osoby ubiegającej się o zatrudnienie podania danych osobowych obejmujących: 1) imię (imiona) i nazwisko; 2) datę uro

### Kodeks pracy | art. 211  count=3, min_sim=0.9516, avg_sim=0.9677

- **[0]** `law_knowledge.json` idx=202  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 211. Przestrzeganie przepisów i zasad bezpieczeństwa i higieny pracy jest podstawowym obowiązkiem pracownika. W szczególności pracownik jest obow
- **[1]** `law_knowledge.json` idx=203  source: `parsed_article_gap_patch`  verified_date: ``
  - content: Przestrzeganie przepisów i zasad bezpieczeństwa i higieny pracy jest podstawowym obowiązkiem pracownika. W szczególności pracownik jest obowiązany: 1)
- **[2]** `law_knowledge_curated_additions.json` idx=7  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 211. Przestrzeganie przepisów i zasad bezpieczeństwa i higieny pracy jest podstawowym obowiązkiem pracownika. W szczególności pracownik jest obow

### Kodeks pracy | art. 221d  count=3, min_sim=0.9508, avg_sim=0.9672

- **[0]** `law_knowledge.json` idx=220  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 221d. § 1. Pracodawca nie dopuszcza pracownika do pracy, jeżeli kontrola trzeźwości wykaże obecność alkoholu w organizmie pracownika wskazującą n
- **[1]** `law_knowledge.json` idx=221  source: `parsed_article_gap_patch`  verified_date: ``
  - content: Pracodawca nie dopuszcza pracownika do pracy, jeżeli kontrola trzeźwości wykaże obecność alkoholu w organizmie pracownika wskazującą na stan po użyciu
- **[2]** `law_knowledge_curated_additions.json` idx=9  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 221d. § 1. Pracodawca nie dopuszcza pracownika do pracy, jeżeli kontrola trzeźwości wykaże obecność alkoholu w organizmie pracownika wskazującą n

### Kodeks pracy | art. 251  count=3, min_sim=0.9492, avg_sim=0.9661

- **[0]** `law_knowledge.json` idx=275  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 251. § 1. Okres zatrudnienia na podstawie umowy o pracę na czas określony, a także łączny okres zatrudnienia na podstawie umów o pracę na czas ok
- **[1]** `law_knowledge.json` idx=276  source: `parsed_article_gap_patch`  verified_date: ``
  - content: Okres zatrudnienia na podstawie umowy o pracę na czas określony, a także łączny okres zatrudnienia na podstawie umów o pracę na czas określony zawiera
- **[2]** `law_knowledge_curated_additions.json` idx=13  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 251. § 1. Okres zatrudnienia na podstawie umowy o pracę na czas określony, a także łączny okres zatrudnienia na podstawie umów o pracę na czas ok

### Kodeks pracy | art. 149  count=3, min_sim=0.9423, avg_sim=0.9615

- **[0]** `law_knowledge.json` idx=71  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 149. § 1. Pracodawca prowadzi ewidencję czasu pracy pracownika do celów prawidłowego ustalenia jego wynagrodzenia i innych świadczeń związanych z
- **[1]** `law_knowledge.json` idx=72  source: `parsed_article_gap_patch`  verified_date: ``
  - content: Pracodawca prowadzi ewidencję czasu pracy pracownika do celów prawidłowego ustalenia jego wynagrodzenia i innych świadczeń związanych z pracą. Pracoda
- **[2]** `law_knowledge_curated_additions.json` idx=2  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 149. § 1. Pracodawca prowadzi ewidencję czasu pracy pracownika do celów prawidłowego ustalenia jego wynagrodzenia i innych świadczeń związanych z

### Kodeks pracy | art. 108  count=3, min_sim=0.9412, avg_sim=0.9608

- **[0]** `law_knowledge.json` idx=20  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 108. § 1. Za nieprzestrzeganie przez pracownika ustalonej organizacji i porządku w procesie pracy, przepisów bezpieczeństwa i higieny pracy, prze
- **[1]** `law_knowledge.json` idx=21  source: `parsed_article_gap_patch`  verified_date: ``
  - content: Za nieprzestrzeganie przez pracownika ustalonej organizacji i porządku w procesie pracy, przepisów bezpieczeństwa i higieny pracy, przepisów przeciwpo
- **[2]** `law_knowledge_curated_additions.json` idx=0  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 108. § 1. Za nieprzestrzeganie przez pracownika ustalonej organizacji i porządku w procesie pracy, przepisów bezpieczeństwa i higieny pracy, prze

### Kodeks pracy | art. 183b  count=3, min_sim=0.9403, avg_sim=0.9602

- **[0]** `law_knowledge.json` idx=150  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 183b. § 1. Za naruszenie zasady równego traktowania w zatrudnieniu, z zastrzeżeniem § 2–4, uważa się różnicowanie przez pracodawcę sytuacji praco
- **[1]** `law_knowledge.json` idx=151  source: `parsed_article_gap_patch`  verified_date: ``
  - content: Za naruszenie zasady równego traktowania w zatrudnieniu, z zastrzeżeniem § 2–4, uważa się różnicowanie przez pracodawcę sytuacji pracownika z jednej l
- **[2]** `law_knowledge_curated_additions.json` idx=5  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 183b. § 1. Za naruszenie zasady równego traktowania w zatrudnieniu, z zastrzeżeniem § 2–4, uważa się różnicowanie przez pracodawcę sytuacji praco

### Kodeks pracy | art. 171  count=3, min_sim=0.9167, avg_sim=0.9444

- **[0]** `law_knowledge.json` idx=117  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 171. § 1. W przypadku niewykorzystania przysługującego urlopu w całości lub w części z powodu rozwiązania lub wygaśnięcia stosunku pracy pracowni
- **[1]** `law_knowledge.json` idx=118  source: `parsed_article_gap_patch`  verified_date: ``
  - content: W przypadku niewykorzystania przysługującego urlopu w całości lub w części z powodu rozwiązania lub wygaśnięcia stosunku pracy pracownikowi przysługuj
- **[2]** `law_knowledge_curated_additions.json` idx=4  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 171. § 1. W przypadku niewykorzystania przysługującego urlopu w całości lub w części z powodu rozwiązania lub wygaśnięcia stosunku pracy pracowni

### Kodeks pracy | art. 229  count=3, min_sim=0.9167, avg_sim=0.9444

- **[0]** `law_knowledge.json` idx=235  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 229. § 1. Wstępnym badaniom lekarskim, z zastrzeżeniem § 11, podlegają: 1) osoby przyjmowane do pracy; 2) pracownicy młodociani przenoszeni na in
- **[1]** `law_knowledge.json` idx=236  source: `parsed_article_gap_patch`  verified_date: ``
  - content: Wstępnym badaniom lekarskim, z zastrzeżeniem § 11, podlegają: 1) osoby przyjmowane do pracy; 2) pracownicy młodociani przenoszeni na inne stanowiska p
- **[2]** `law_knowledge_curated_additions.json` idx=11  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 229. § 1. Wstępnym badaniom lekarskim, z zastrzeżeniem § 11, podlegają: 1) osoby przyjmowane do pracy; 2) pracownicy młodociani przenoszeni na in

### Kodeks pracy | art. 97  count=3, min_sim=0.8833, avg_sim=0.9222

- **[0]** `law_knowledge.json` idx=449  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 97. § 1. W związku z rozwiązaniem lub wygaśnięciem stosunku pracy pracodawca jest obowiązany wydać pracownikowi świadectwo pracy w dniu, w którym
- **[1]** `law_knowledge.json` idx=450  source: `parsed_article_gap_patch`  verified_date: ``
  - content: W związku z rozwiązaniem lub wygaśnięciem stosunku pracy pracodawca jest obowiązany wydać pracownikowi świadectwo pracy w dniu, w którym następuje ust
- **[2]** `law_knowledge_curated_additions.json` idx=21  source: `curate_kb_and_synonyms`  verified_date: ``
  - content: Art. 97. § 1. W związku z rozwiązaniem lub wygaśnięciem stosunku pracy pracodawca jest obowiązany wydać pracownikowi świadectwo pracy w dniu, w którym

## Top 10 legitimate_variants groups (sanity check)

### Ustawa o podatku dochodowym od osób fizycznych | art. 27 ust. 1  count=5, min_sim=0.0, avg_sim=0.1606

- **[0]** `law_knowledge.json` idx=1598
  - content: Od dochodu do 120 000 zł podatek wynosi 12% minus kwota zmniejszająca podatek 3600 zł. Od dochodu powyżej 120 000 zł podatek wynosi 10 800 zł plus 32%
- **[1]** `law_knowledge.json` idx=1599
  - content: Podane artykuły nie zawierają przepisów dotyczących zmiany formy opodatkowania w przypadku, gdy przychody są osiągane tylko pod koniec roku. Artykuł 3
- **[2]** `law_knowledge.json` idx=1600
  - content: Podane artykuły nie zawierają żadnych informacji o PIT 36. Artykuł 27 opisuje skalę podatkową (12% do 120 tys. zł, potem 32% od nadwyżki), ale nie uzy
- **[3]** `law_knowledge.json` idx=1601
  - content: Podstawową formą opodatkowania działalności gospodarczej osób fizycznych jest podatek dochodowy według progresywnej skali podatkowej. Dla dochodów do 
- **[4]** `law_knowledge.json` idx=1602
  - content: Skala podatkowa 12% i 32% to skala obligatoryjna określona w art. 27 ust. 1 ustawy o podatku dochodowym od osób fizycznych. Podatnicy są zobowiązani s

### Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1  count=40, min_sim=0.0119, avg_sim=0.1175

- **[0]** `law_knowledge.json` idx=1758
  - content: Art. 45 nie zawiera informacji o wersji formularza ani o zmianach wersji. Vzory deklaracji podatkowych ustala się w rozporządzeniu ministra, informacj
- **[1]** `law_knowledge.json` idx=1759
  - content: Art. 45 ust. 1 i 1a nakładają obowiązek na podatnika (osobę fizyczną) do złożenia zeznania – nie wymagają korzystania z pośrednika (biura rachunkowego
- **[2]** `law_knowledge.json` idx=1760
  - content: Art. 45 ust. 1 potwierdza obowiązek złożenia rocznego zeznania według ustalonego wzoru. Sama ustawa o PIT na poziomie tego przepisu nie daje prostego 
- **[3]** `law_knowledge.json` idx=1761
  - content: Art. 45 ust. 1 stanowi, że podatnik składa zeznanie według ustalonego wzoru za dany rok podatkowy. Jeżeli wcześniej użyto niewłaściwego formularza, pr
- **[4]** `law_knowledge.json` idx=1762
  - content: Art. 45 ust. 1 wskazuje obowiązek złożenia zeznania według ustalonego wzoru. Sam ten przepis nie rozstrzyga wprost w przytoczonej treści, czy dany for
- **[5]** `law_knowledge.json` idx=1763
  - content: Art. 45 wskazuje, że w zeznaniu wykazuje się osiągnięty dochód (lub stratę), a w szczególnych przypadkach (art. 45 ust. 3c) wykazuje się przychody od 
- **[6]** `law_knowledge.json` idx=1764
  - content: Artykuł 45 nie reguluje wieku podatnika ani sposobu składania zeznania (papier vs. internet). Pełnoletnia osoba (18 lat) ma status podatnika pełnopraw
- **[7]** `law_knowledge.json` idx=1765
  - content: Artykuł 45 nie zawiera informacji o zmianach formularzy czy możliwości autouzupełniania danych. Kwestię wzorów zeznań, ich zmian oraz procedury uzupeł
- **[8]** `law_knowledge.json` idx=1766
  - content: Artykuł 45 nie zawiera konkretnych informacji o formularzu PIT-36. Przepis mówi ogólnie o zeznaniu rocznym, ale dokładną definicję i zastosowanie posz
- **[9]** `law_knowledge.json` idx=1767
  - content: Artykuł 45 reguluje obowiązek złożenia zeznania podatkowego w ustalonym terminie, ale nie zawiera przepisów dotyczących rezygnacji z automatycznego ro
- **[10]** `law_knowledge.json` idx=1768
  - content: Artykuł 45 reguluje obowiązek złożenia zeznania przez podatnika, ale nie zawiera szczegółów dotyczących reprezentacji przez rodziców, sposobu podpisan
- **[11]** `law_knowledge.json` idx=1769
  - content: Artykuł 45 ustawy PIT definiuje obowiązek i termin złożenia zeznania, ale nie zawiera informacji o konsekwencjach za niezłożenie lub spóźnione złożeni
- **[12]** `law_knowledge.json` idx=1770
  - content: Artykuł 45 wymaga złożenia zeznania za dany rok podatkowy w terminie od 15 lutego do 30 kwietnia roku następującego. Przychody za 2024 rok powinny być
- **[13]** `law_knowledge.json` idx=1771
  - content: Dochód (lub stratę) osiągnięty w roku podatkowym wykazujesz w zeznaniu podatkowym składanym do urzędu skarbowego. Jeśli osiągasz dochody z różnych źró
- **[14]** `law_knowledge.json` idx=1772
  - content: Dochody osiągnięte w roku podatkowym 2025 wykazuje się w zeznaniu PIT-36 (lub PIT-37) składanym w terminie od 15 lutego do 30 kwietnia 2026 roku (art.
- **[15]** `law_knowledge.json` idx=1773
  - content: Obowiązek złożenia zeznania podatkowego (rozliczenia się) wynika z ustawy, a nie z samego otrzymania PIT. Każdy podatnik osiągający dochody w danym ro
- **[16]** `law_knowledge.json` idx=1774
  - content: Podatnicy mają obowiązek złożyć zeznanie podatkowe (PIT) w terminie od 15 lutego do 30 kwietnia roku następującego po roku podatkowym (art. 45 ust. 1)
- **[17]** `law_knowledge.json` idx=1775
  - content: Podatnicy mają obowiązek złożyć zeznanie roczne niezależnie od tego, czy pobierano zaliczki. Obowiązek dotyczy wysokości osiągniętego dochodu (lub str
- **[18]** `law_knowledge.json` idx=1776
  - content: Pracownik rozliczający się indywidualnie ma obowiązek złożyć zeznanie PIT-37 między 15 lutego a 30 kwietnia roku następnego (art. 45 ust. 1). W zeznan
- **[19]** `law_knowledge.json` idx=1777
  - content: Tak, obowiązek złożenia zeznania rocznego istnieje niezależnie od tego, czy pracodawca pobierał zaliczki. W zeznaniu rocznym podatnik wykazuje różnicę
- **[20]** `law_knowledge.json` idx=1778
  - content: Tak, przychody z odsetek (jako przychody z kapitałów pieniężnych) trzeba wykazać w rocznym zeznaniu PIT-36 lub PIT-36L za rok, w którym zostały otrzym
- **[21]** `law_knowledge.json` idx=1779
  - content: Tekst art. 45 nie zawiera szczegółowych regulacji dotyczących procedury rozliczania PIT-38 za osoby zmarłe ani obowiązków spadkobierców w tym zakresie
- **[22]** `law_knowledge.json` idx=1780
  - content: Tekst art. 45 Ustawy o podatku dochodowym od osób fizycznych nie określa sposobu podpisywania zeznań podatkowych ani nie wskazuje, czy dopuszczalne są
- **[23]** `law_knowledge.json` idx=1781
  - content: Tekst artykułów nie zawiera szczegółowych instrukcji dotyczących sposobu agregacji dochodów z wielu pracodawców w ramach PIT-11. Artykuł 45 reguluje g
- **[24]** `law_knowledge.json` idx=1782
  - content: Tekst artykułów ustawy o podatku dochodowym od osób fizycznych nie zawiera przepisów dotyczących obowiązku dołączania formularza PIT 0 do rozliczenia 
- **[25]** `law_knowledge.json` idx=1783
  - content: Tekst artykułu 45 nie zawiera informacji o tym, czy w PIT-28 należy wpisać NIP czy PESEL, ani nie reguluje kwestii identyfikacji podatnika w formularz
- **[26]** `law_knowledge.json` idx=1784
  - content: Termin do złożenia zeznania rocznego wynosi od 15 lutego do 30 kwietnia roku następującego po roku podatkowym, w którym osiągnięto przychód. Jeśli pie
- **[27]** `law_knowledge.json` idx=1785
  - content: Termin na złożenie zeznania PIT wynosi od 15 lutego do 30 kwietnia roku następującego po roku podatkowym. To oznacza, że za rok 2024 musisz złożyć zez
- **[28]** `law_knowledge.json` idx=1786
  - content: Termin na złożenie zeznania wynosi 15 lutego – 30 kwietnia dla wszystkich podatników bez względu na to, czy wynika z niego podatek do zapłaty czy zwro
- **[29]** `law_knowledge.json` idx=1787
  - content: Termin składania zeznania rocznego to do 30 kwietnia roku następującego po roku podatkowym, nie do 20. Zeznania złożone wcześniej (przed 15 lutego) uw
- **[30]** `law_knowledge.json` idx=1788
  - content: Ustawa art. 45 wymaga złożenia zeznania według ustalonego wzoru w terminie od 15 lutego do 30 kwietnia. Nie zawiera informacji o wymaganych techniczny
- **[31]** `law_knowledge.json` idx=1789
  - content: Ustawa nie określa minimalnej kwoty dochodu dla elektronicznego składania zeznania. Obowiązek złożenia zeznania w terminie od 15 lutego do 30 kwietnia
- **[32]** `law_knowledge.json` idx=1790
  - content: Ustawa o podatku dochodowym od osób fizycznych reguluje obowiązek złożenia zeznania w terminie do 30 kwietnia (art. 45 ust. 1), ale nie zawiera szczeg
- **[33]** `law_knowledge.json` idx=1791
  - content: W terminie od 15 lutego do 30 kwietnia 2026 roku musisz złożyć zeznanie PIT (formularz roczny) do urzędu skarbowego właściwego dla Twojego miejsca zam
- **[34]** `law_knowledge.json` idx=1792
  - content: Za rok 2025 termin na złożenie zeznania wynosi od 15 lutego do 30 kwietnia 2026 roku. Termin jest zawsze taki sam – każdy rok podatkowy rozliczasz w o
- **[35]** `law_knowledge.json` idx=1793
  - content: Zeznania złożone przed oficjalnym terminem (15 lutego – 30 kwietnia) uznaje się za złożone w dniu 15 lutego roku następującego po roku podatkowym. Nie
- **[36]** `law_knowledge.json` idx=1794
  - content: Zeznanie o wysokości osiągniętego dochodu (lub poniesionej straty) należy złożyć w urzędzie skarbowym właściwym dla Twojego miejsca zamieszkania, w te
- **[37]** `law_knowledge.json` idx=1795
  - content: Zeznanie o wysokości osiągniętego dochodu (PIT-36) należy złożyć w terminie od 15 lutego do 30 kwietnia roku następującego po roku podatkowym. Zeznani
- **[38]** `law_knowledge.json` idx=1796
  - content: Zeznanie podatkowe trzeba złożyć w terminie od 15 lutego do 30 kwietnia roku następującego po roku podatkowym. Zeznania złożone przed 15 lutego uznaje
- **[39]** `law_knowledge.json` idx=1797
  - content: Zeznanie roczne o dochodach należy złożyć w terminie od 15 lutego do 30 kwietnia roku następującego po roku podatkowym. Zeznania złożone przed 15 lute

### Ustawa o VAT | art. 106e ust. 1  count=15, min_sim=0.0135, avg_sim=0.1289

- **[0]** `law_knowledge.json` idx=2832
  - content: Art. 106e reguluje wymagania dotyczące faktury, ale nie zawiera żadnego obowiązku wystawiania paragonu ani żadnego odniesienia do paragonów. Przepis d
- **[1]** `law_knowledge.json` idx=2833
  - content: Dane do rozliczenia VAT powinny pochodzić z faktury, ponieważ art. 106e określa dokładnie, jakie dane powinna zawierać faktura, którą otrzymujesz. Fak
- **[2]** `law_knowledge.json` idx=2834
  - content: Faktura musi zawierać: datę wystawienia, numer identyfikacyjny, dane podatnika i nabywcy (imiona, nazwiska, adresy, numery VAT), datę dostawy/wykonani
- **[3]** `law_knowledge.json` idx=2835
  - content: Faktura musi zawierać: datę wystawienia, numer identyfikacyjny, imiona/nazwiska podatnika i nabywcy z adresami, numer VAT obydwu stron, datę dostawy/w
- **[4]** `law_knowledge.json` idx=2836
  - content: Faktura od hurtowni (np. Makro) to dokument sprzedaży, który podatnik otrzymuje od dostawcy. Podatnik ma prawo do odliczenia VAT wykazanego na fakturz
- **[5]** `law_knowledge.json` idx=2837
  - content: Mail od kontrahenta zagranicznego nie spełnia wymogów faktury wymaganej art. 106e, która musi zawierać konkretne elementy obowiązkowe (datę, numer, da
- **[6]** `law_knowledge.json` idx=2838
  - content: Przepisy art. 106e nie określają obowiązkowego znacznika (adnotacji słownej) dla faktur dotyczących wewnątrzwspólnotowych dostaw towarów czy importu u
- **[7]** `law_knowledge.json` idx=2839
  - content: Przepisy art. 106e Ustawy o VAT nie zawierają wymogów dotyczących oznaczeń "BFK" czy "DI" na fakturach. Artykuł określa jedynie, jakie dane muszą znal
- **[8]** `law_knowledge.json` idx=2840
  - content: Tekst art. 106e nie wymaga, aby REGON był obligatoryjnie wykazywany na fakturze. Ustawodawca wymaga numeru identyfikacyjnego dla podatku VAT, ale nie 
- **[9]** `law_knowledge.json` idx=2841
  - content: Ustawa nie ogranicza waluty, w której wystawia się fakturę VAT-UE. Faktura może być wystawiona w PLN. Jeśli kwoty są w walucie obcej, podatnik przelic
- **[10]** `law_knowledge.json` idx=2842
  - content: Ustawa o VAT nie definiuje específicznych znaczników dla WNT na fakturze w art. 106e. Artykuł wymienia konkretne oznaczenia dla odwrotnego obciążenia 
- **[11]** `law_knowledge.json` idx=2843
  - content: Ustawa o VAT nie definiuje skrótów takich jak 'BFK' ani nie reguluje systemu oznaczeń dla faktur zakupowych (kosztowych). Ustawowo faktury muszą zawie
- **[12]** `law_knowledge.json` idx=2844
  - content: Ustawa o VAT nie wymaga, aby faktura zawierała numer paragonu. Paragraf i faktura to odrębne dokumenty. Faktura musi zawierać wymagane elementy z art.
- **[13]** `law_knowledge.json` idx=2845
  - content: Ustawa o VAT nie wymaga umieszczania dopisku 'VAT-1' na fakturze. Faktura musi zawierać wymienione w art. 106e ust. 1 elementy, takie jak stawka VAT l
- **[14]** `law_knowledge.json` idx=2846
  - content: Ustawa o VAT nie zawiera lub nie dostarcza gotowych wzorów faktury. Przepisy wymagają, aby faktura zawierała określone dane (art. 106e), ale to podatn

### Ustawa o VAT | art. 86 ust. 1  count=55, min_sim=0.0139, avg_sim=0.1512

- **[0]** `law_knowledge.json` idx=3858
  - content: Art. 86 nie reguluje bezpośrednio kwestii przełączania towarów z celów gospodarczych na prywatne. Ta sprawa należy do art. 7-8 (definicja i warunki cz
- **[1]** `law_knowledge.json` idx=3859
  - content: Art. 86 reguluje wyłącznie odliczenie VAT dla podatników czynnych, nie zaś procedury rejestracji czy wyrejestrowania z VAT. Pytanie o możliwość powrot
- **[2]** `law_knowledge.json` idx=3860
  - content: Art. 86 reguluje wyłącznie odliczenie VAT (obniżenie VAT należnego), nie zaś sposób ujmowania wydatków w rachunkowości czy kosztach dla podatku dochod
- **[3]** `law_knowledge.json` idx=3861
  - content: Art. 86 reguluje wyłącznie odliczenie VAT (zmniejszenie VAT należnego), nie zaś ujmowanie wydatków w rachunkowości czy dla celów podatku dochodowego. 
- **[4]** `law_knowledge.json` idx=3862
  - content: Art. 86 ust. 1 wymaga bycia podatnikiem czynnym (art. 15). Jednak przepis nie precyzuje dokładnie, czy decyduje data wystawienia faktury, data otrzyma
- **[5]** `law_knowledge.json` idx=3863
  - content: Art. 86 ustawy o VAT reguluje odliczenie VAT dla podatników czynnych VAT. Połączenie ryczałtu od przychodów ewidencjonowanych z VAT czynnym wymaga odr
- **[6]** `law_knowledge.json` idx=3864
  - content: Artykuł nie zawiera bezpośrednich przepisów dotyczących odliczania VAT z faktur sprzed rejestracji jako podatnika VAT. Prawo do odliczenia przysługuje
- **[7]** `law_knowledge.json` idx=3865
  - content: Artykuł nie zawiera szczegółowych regulacji dotyczących odliczania VAT z zakupów dokonanych przed formalnym rozpoczęciem działalności gospodarczej. Pr
- **[8]** `law_knowledge.json` idx=3866
  - content: Czynni podatnicy VAT mają prawo do obniżenia podatku należnego o podatek naliczony, ale tylko w zakresie, w jakim towary i usługi są wykorzystywane do
- **[9]** `law_knowledge.json` idx=3867
  - content: Do celów VAT różnica między kosztem a towarem handlowym nie ma znaczenia — obydwa dają prawo do odliczenia VAT, jeśli są wykorzystywane do czynności o
- **[10]** `law_knowledge.json` idx=3868
  - content: Faktura za internet może być zaliczona do kosztów uzyskania przychodu w kwocie netto (bez VAT). VAT naliczony wykazany na fakturze za internet możesz 
- **[11]** `law_knowledge.json` idx=3869
  - content: Faktury za terminal bezgotówkowy można odliczyć VAT w standardowym trybie (art. 86 ust. 1, 10b) — jeśli terminal jest wykorzystywany do wykonywania cz
- **[12]** `law_knowledge.json` idx=3870
  - content: Jeśli posiadasz fakturę z VAT, muszą Ci przysługiwać oba elementy: zarówno koszt netto w wydatkach, jak i prawo do odliczenia VAT. Prawo do odliczenia
- **[13]** `law_knowledge.json` idx=3871
  - content: Jeśli towary/usługi są bezpośrednio związane ze sprzedażą zwolnioną z VAT, podatnikowi nie przysługuje prawo do odliczenia VAT naliczonego. Należy odr
- **[14]** `law_knowledge.json` idx=3872
  - content: Materiały nabywane do wykonania usług podlegają odliczeniu VAT na zasadach ogólnych (art. 86 ust. 1) - są zaliczane do kosztów działalności (mogą stan
- **[15]** `law_knowledge.json` idx=3873
  - content: Możesz odliczyć VAT w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatkowanych. Jeśli szkolenie pracownika służy dz
- **[16]** `law_knowledge.json` idx=3874
  - content: Nie możesz arbitralnie odliczać 50% VAT. Wysokość odliczanego VAT musi wynikać z rzeczywistego zakresu wykorzystania towaru/usługi do czynności opodat
- **[17]** `law_knowledge.json` idx=3875
  - content: Nie możesz odliczyć VAT z faktur z listopada, gdy byłeś zwolniony z VAT, na podstawie art. 86 ust. 1 Ustawy o VAT. Prawo do obniżenia podatku należneg
- **[18]** `law_knowledge.json` idx=3876
  - content: Nie. VAT należny od sprzedaży jest obliczany niezależnie od tego, czy odliczyłeś VAT z zakupów. VAT należny powstaje od każdej dokonanej dostawy towar
- **[19]** `law_knowledge.json` idx=3877
  - content: Odpowiedź wymaga szczegółowej analizy konkretnej sytuacji faktycznej. Art. 86 Ustawy o VAT stanowi, że prawo do odliczenia przysługuje podatnikowi (ar
- **[20]** `law_knowledge.json` idx=3878
  - content: Prąd (energia elektryczna) to usługa, a VAT naliczony z faktury za prąd odliczasz w ramach podatku naliczonego (art. 86 ust. 2 pkt 1 lit. a), jeśli en
- **[21]** `law_knowledge.json` idx=3879
  - content: Prawo do obniżenia VAT należnego o VAT naliczony przysługuje w rozliczeniu za okres, w którym powstał obowiązek podatkowy (dla faktury) lub w którym p
- **[22]** `law_knowledge.json` idx=3880
  - content: Prawo do odliczenia 100% VAT istnieje tylko wtedy, gdy towary i usługi są wykorzystywane do wykonywania czynności opodatkowanych. Jeśli jednocześnie u
- **[23]** `law_knowledge.json` idx=3881
  - content: Prawo do odliczenia VAT (art. 86 ust. 1) wymaga, aby towary i usługi były wykorzystywane do wykonywania czynności opodatkowanych. Jeśli przedsiębiorca
- **[24]** `law_knowledge.json` idx=3882
  - content: Prawo do odliczenia VAT nie zależy od czy transakcja dotyczy integracji. Decyduje wyłącznie to, czy towary/usługi są wykorzystywane do czynności opoda
- **[25]** `law_knowledge.json` idx=3883
  - content: Prawo do odliczenia VAT (obniżenia kwoty podatku należnego o podatek naliczony) przysługuje wyłącznie gdy towary i usługi są wykorzystywane do wykonyw
- **[26]** `law_knowledge.json` idx=3884
  - content: Prawo do odliczenia VAT od wyposażenia i artykułów remontowych powstaje w rozliczeniu za okres, w którym otrzymałeś fakturę (art. 86 ust. 10b pkt 1). 
- **[27]** `law_knowledge.json` idx=3885
  - content: Prawo do odliczenia VAT przysługuje podatnikowi czynnie zarejestrowanemu w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynnośc
- **[28]** `law_knowledge.json` idx=3886
  - content: Prawo do odliczenia VAT przysługuje podatnikowi VAT czynnemu w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatkowa
- **[29]** `law_knowledge.json` idx=3887
  - content: Prawo do odliczenia VAT przysługuje tylko podatnikom VAT w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatkowanych
- **[30]** `law_knowledge.json` idx=3888
  - content: Prawo do odliczenia VAT przysługuje tylko w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatkowanych. Jeśli podatni
- **[31]** `law_knowledge.json` idx=3889
  - content: Prawo do odliczenia VAT przysługuje w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatkowanych (art. 86 ust. 1). Po
- **[32]** `law_knowledge.json` idx=3890
  - content: Prawo do odliczenia VAT przysługuje w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatkowanych (art. 86 ust. 1). Sa
- **[33]** `law_knowledge.json` idx=3891
  - content: Prawo do odliczenia VAT przysługuje w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatkowanych. Oznacza to, że jeśl
- **[34]** `law_knowledge.json` idx=3892
  - content: Prawo do odliczenia VAT przysługuje w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatkowanych. Oznacza to, że może
- **[35]** `law_knowledge.json` idx=3893
  - content: Prawo do odliczenia VAT z faktury za naprawę przysługuje w całości niezależnie od tego, kto dokonał zapłaty. Kwotę podatku naliczonego stanowi suma kw
- **[36]** `law_knowledge.json` idx=3894
  - content: Prawo do odliczenia VAT zależy od użytkownia towaru lub usługi, a nie od relacji między VAT a kosztem. Jeśli towar/usługa jest wykorzystywany do czynn
- **[37]** `law_knowledge.json` idx=3895
  - content: Prawo do odliczenia VAT zależy od zakresu wykorzystania towarów i usług. Możesz odliczyć 100% VAT tylko w zakresie, w jakim towary i usługi są wykorzy
- **[38]** `law_knowledge.json` idx=3896
  - content: Pytanie dotyczące zaliczenia VAT jako kosztu do rozliczenia podatku dochodowego wykracza poza zakres ustawy o VAT. Ustawa o VAT reguluje wyłącznie odl
- **[39]** `law_knowledge.json` idx=3897
  - content: Pytanie dotyczy procedury rozliczeniowej VAT i kodowania w ewidencji, które nie są bezpośrednio uregulowane w art. 86 ustawy o VAT. Kodowanie transakc
- **[40]** `law_knowledge.json` idx=3898
  - content: Raty leasingowe zawierające VAT podlegają tym samym zasadom odliczenia jak inne usługi. Jeśli są wykorzystywane do czynności opodatkowanych, przysługu
- **[41]** `law_knowledge.json` idx=3899
  - content: Tak, jeśli towary lub usługi są wykorzystywane do wykonywania czynności opodatkowanych, przysługuje prawo do odliczenia VAT naliczonego z faktury (art
- **[42]** `law_knowledge.json` idx=3900
  - content: Tak, jeśli w danym okresie rozliczeniowym kwota podatku naliczonego jest wyższa od kwoty podatku należnego, możesz przenieść nadwyżkę do następnych ok
- **[43]** `law_knowledge.json` idx=3901
  - content: Tak, możesz odliczyć VAT z dokumentów związanych z zakupem (faktury lub dokumentu celnego), ale tylko jeśli: 1) jesteś czynnym podatnikiem VAT, 2) tow
- **[44]** `law_knowledge.json` idx=3902
  - content: Tak, możesz odliczyć VAT z faktury za prowizję za pośrednictwo płatnicze od Stripe, jeśli usługa jest wykorzystywana do wykonywania czynności opodatko
- **[45]** `law_knowledge.json` idx=3903
  - content: Tak, możesz odliczyć VAT z oprogramowania (usługi), jeśli w całości jest wykorzystywane do wykonywania czynności opodatkowanych w ramach Twojej działa
- **[46]** `law_knowledge.json` idx=3904
  - content: Tak, możesz odliczyć VAT z wewnątrzwspólnotowego nabycia towarów z Czech, jeśli jesteś podatnikiem VAT czynnym. Prawo do odliczenia powstaje w rozlicz
- **[47]** `law_knowledge.json` idx=3905
  - content: TAK, podatnik może odliczyć 100% VAT naliczonego, ale wyłącznie jeśli towary i usługi są w całości wykorzystywane do wykonywania czynności opodatkowan
- **[48]** `law_knowledge.json` idx=3906
  - content: Tak, prawo do odliczenia VAT z faktury za zwykły koszt (np. materiały, usługi) przysługuje w rozliczeniu za okres, w którym podatnik otrzymał fakturę 
- **[49]** `law_knowledge.json` idx=3907
  - content: Tekst art. 86 nie reguluje kwestii prezentów i progów wartościowych. Aby odpowiedzieć na to pytanie, konieczna byłaby analiza art. 7 (warunki wykonywa
- **[50]** `law_knowledge.json` idx=3908
  - content: Ustawa o VAT nie reguluje wartości brutto czy netto w koszcie — to kwestia ksiąg rachunkowych, nie VAT. VAT odliczasz na podstawie faktury, niezależni
- **[51]** `law_knowledge.json` idx=3909
  - content: Usługa cateringowa może podlegać odliczeniu VAT, ale wyłącznie w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatko
- **[52]** `law_knowledge.json` idx=3910
  - content: VAT naliczony (z faktur od dostawców) odliczasz z VAT należnego (z własnych sprzedaży). W rozliczeniu VAT wykazujesz zarówno VAT należny, jak i VAT na
- **[53]** `law_knowledge.json` idx=3911
  - content: W rejestrze VAT wykazujesz fakturę w pełnej kwocie brutto, ale odliczasz tylko tę część VAT, którą faktycznie Ty zapłaciłaś (50%). VAT zapłacony przez
- **[54]** `law_knowledge.json` idx=3912
  - content: Waciki bezpyłowe do stylizacji paznokci są utrzymanymi w запасе materiałami (kosztami) wykorzystywanymi do świadczenia usługi, a nie towarem handlowym

### Ustawa o VAT | art. 19a ust. 1  count=33, min_sim=0.0143, avg_sim=0.1902

- **[0]** `law_knowledge.json` idx=3473
  - content: 1. Obowiązek podatkowy powstaje z chwilą dokonania dostawy towarów lub wykonania usługi, z zastrzeżeniem ust. 1a, 1b, 5 i 7–11, art. 14 ust. 6, art. 2
- **[1]** `law_knowledge.json` idx=3474
  - content: Artykuł 19a nie zawiera szczegółowych przepisów dotyczących momentu powstania obowiązku podatkowego przy eksporcie towarów. Wymienia jedynie ogólną za
- **[2]** `law_knowledge.json` idx=3475
  - content: Data na fakturze nie jest automatycznie datą dostawy dla VAT. Obowiązek podatkowy powstaje z chwilą faktycznego dokonania dostawy towarów. Jeśli na fa
- **[3]** `law_knowledge.json` idx=3476
  - content: Dla płatności bezgotówkowej VAT powstaje w dacie dokonania dostawy/wykonania usługi (art. 19a ust. 1), a nie w dacie przelewu. Data dokonania przelewu
- **[4]** `law_knowledge.json` idx=3477
  - content: Forma płatności (gotówka lub przelew) nie wpływa na moment powstania obowiązku podatkowego. VAT powstaje z chwilą dokonania usługi, niezależnie od teg
- **[5]** `law_knowledge.json` idx=3478
  - content: Obowiązek podatkowy powstaje w momencie wykonania usługi, czyli w lutym, a nie w marcu gdy wystawiono fakturę. Zgodnie z art. 19a ust. 1, obowiązek po
- **[6]** `law_knowledge.json` idx=3479
  - content: Obowiązek podatkowy powstaje z chwilą dokonania dostawy (tankowania), czyli w dniu 31.12, niezależnie od daty wystawienia faktury. VAT ujmujesz w mies
- **[7]** `law_knowledge.json` idx=3480
  - content: Obowiązek podatkowy powstaje z chwilą dokonania dostawy towarów lub wykonania usługi, a nie od daty zobowiązania (art. 19a ust. 1). To oznacza, że VAT
- **[8]** `law_knowledge.json` idx=3481
  - content: Obowiązek podatkowy powstaje z chwilą dokonania dostawy towarów lub wykonania usługi, niezależnie od sposobu dokonania płatności (gotówka, przelew czy
- **[9]** `law_knowledge.json` idx=3482
  - content: Obowiązek podatkowy powstaje z chwilą dokonania dostawy towarów lub wykonania usługi — to jest moment podstawowy. Jednak są ważne wyjątki: jeśli otrzy
- **[10]** `law_knowledge.json` idx=3483
  - content: Obowiązek podatkowy powstaje z chwilą dokonania dostawy towaru lub wykonania usługi, a nie z chwilą wystawienia faktury. W Twoim przypadku obowiązek p
- **[11]** `law_knowledge.json` idx=3484
  - content: Obowiązek podatkowy powstaje z chwilą dokonania dostawy towaru lub wykonania usługi, a nie z datą wystawienia faktury. Wyjątek stanowią określone usłu
- **[12]** `law_knowledge.json` idx=3485
  - content: Obowiązek podatkowy powstaje z chwilą dokonania usługi (art. 19a ust. 1). Jeśli przed wykonaniem usługi otrzymasz całość lub część zapłaty (przedpłatę
- **[13]** `law_knowledge.json` idx=3486
  - content: Obowiązek podatkowy przy sprzedaży maszyny powstaje z chwilą dokonania dostawy towarów, czyli przeniesienia prawa do rozporządzania towarem jak właści
- **[14]** `law_knowledge.json` idx=3487
  - content: Obowiązek podatkowy VAT powstaje najczęściej z chwilą dokonania dostawy towaru lub wykonania usługi. Dla wybranych usług (energia, telekomunikacja, le
- **[15]** `law_knowledge.json` idx=3488
  - content: Obowiązek podatkowy VAT powstaje w zasadzie z chwilą dokonania dostawy towaru. Wyjątkiem jest otrzymanie przedpłaty, zaliczki, zadatku lub raty przed 
- **[16]** `law_knowledge.json` idx=3489
  - content: Obowiązek podatkowy VAT powstaje z chwilą dokonania dostawy lub wykonania usługi, czyli w naszym przypadku okresu, za który prowizja jest liczona (sty
- **[17]** `law_knowledge.json` idx=3490
  - content: Obowiązek podatkowy VAT powstaje z chwilą dokonania dostawy towarów lub wykonania usługi. Jednak są wyjątki: dla niektórych usług (z ratami lub rozlic
- **[18]** `law_knowledge.json` idx=3491
  - content: Obowiązek podatkowy VAT powstaje z chwilą dokonania dostawy towarów lub wykonania usługi. To jest zasada główna, ale ustawa przewiduje liczne wyjątki 
- **[19]** `law_knowledge.json` idx=3492
  - content: Obowiązek podatkowy VAT powstaje z chwilą dokonania dostawy towaru lub wykonania usługi, a nie z datą wystawienia faktury. Jeśli faktura zostanie wyst
- **[20]** `law_knowledge.json` idx=3493
  - content: Obowiązek podatkowy w VAT powstaje z chwilą dokonania dostawy towarów. Dostawę towarów rozumie się jako przeniesienie prawa do rozporządzania towarami
- **[21]** `law_knowledge.json` idx=3494
  - content: Tak, jeśli dostawę/usługę wykonano w styczniu, a fakturę wystawiłeś w lutym, to VAT ujmujesz w styczniu (w momencie dostawy, art. 19a ust. 1). Do ksią
- **[22]** `law_knowledge.json` idx=3495
  - content: Tak, jeśli usługę świadczysz za rok, obowiązek VAT powstaje dopiero w momencie wykonania tej usługi (art. 19a ust. 1), czyli w roku, w którym faktyczn
- **[23]** `law_knowledge.json` idx=3496
  - content: Tak, przychód (obowiązek podatkowy) powstał w grudniu 2025, ponieważ obowiązek powstaje z chwilą dokonania dostawy towarów. Data dostarczenia towaru t
- **[24]** `law_knowledge.json` idx=3497
  - content: Tak, terminy powstania obowiązku podatkowego różnią się zależnie od rodzaju czynności. Ogólnie obowiązek powstaje z chwilą dostawy lub wykonania usług
- **[25]** `law_knowledge.json` idx=3498
  - content: Tekst artykułu nie zawiera informacji o wprowadzaniu znaczników czy odrębnych kodów rozróżniających datę usługi od daty wystawienia faktury. Dla celów
- **[26]** `law_knowledge.json` idx=3499
  - content: VAT nie zależy od wybranej metody księgowania do CIT (kasowa vs memoriałowa). Dla VAT obowiązek powstaje zawsze z dostawą towaru lub wykonaniem usługi
- **[27]** `law_knowledge.json` idx=3500
  - content: VAT powstaje w dacie dokonania dostawy lub wykonania usługi. Jeśli zarówno informacja (realizacja) i faktura dotyczą lutego, VAT również zaliczasz na 
- **[28]** `law_knowledge.json` idx=3501
  - content: VAT ujmujesz w miesiącu kwietnia (data wykonania usługi/dostawy - 30 kwietnia), ponieważ obowiązek podatkowy powstaje z chwilą dokonania dostawy lub w
- **[29]** `law_knowledge.json` idx=3502
  - content: Zasadą jest, że obowiązek podatkowy powstaje z chwilą dokonania dostawy towaru lub wykonania usługi, niezależnie od tego, czy otrzymałeś już zapłatę. 
- **[30]** `law_knowledge.json` idx=3503
  - content: Zasadą jest, że obowiązek podatkowy powstaje z chwilą wykonania usługi (art. 19a ust. 1). Jednak istnieją wyjątki: obowiązek może powstać wcześniej (p
- **[31]** `law_knowledge.json` idx=3504
  - content: Zasadniczo obowiązek podatkowy VAT powstaje z chwilą dokonania dostawy towarów. Wyjątkiem są szczególne przypadki, gdzie obowiązek powstaje z momentem
- **[32]** `law_knowledge.json` idx=3505
  - content: Zasadniczo obowiązek VAT powstaje z chwilą dokonania dostawy towaru lub wykonania usługi, a nie w dniu płatności. Data płatności ma znaczenie tylko w 

### Ustawa o VAT | art. 106i ust. 1  count=22, min_sim=0.0235, avg_sim=0.1812

- **[0]** `law_knowledge.json` idx=2991
  - content: Art. 106i reguluje termin WYSTAWIENIA faktury, a nie termin płatności. Termin płatności (np. 30 dni od faktury) to sprawa umowy między Tobą a kupujący
- **[1]** `law_knowledge.json` idx=2992
  - content: Faktura korygująca księguje się z datą jej wystawienia (art. 106i ust. 1) - to data, kiedy powstaje obowiązek VAT. Data otrzymania korekty (wpływu) je
- **[2]** `law_knowledge.json` idx=2993
  - content: Faktura korygująca wystawiona w swojej dacie (styczeń) wpływa na VAT w okresie wystawienia korekty (styczeń) zgodnie z art. 106i ust. 1 i art. 19a ust
- **[3]** `law_knowledge.json` idx=2994
  - content: Faktura powinna być wystawiona nie później niż 15. dnia miesiąca następującego po miesiącu dokonania dostawy (art. 106i ust. 1). Nie możesz wystawić f
- **[4]** `law_knowledge.json` idx=2995
  - content: Faktura powinna być wystawiona nie później niż 15. dnia miesiąca następującego po miesiącu, w którym dokonano dostawy (art. 106i ust. 1). Jednak dla V
- **[5]** `law_knowledge.json` idx=2996
  - content: Fakturę do operacji z dnia 31.01.2026 można wystawić w dniu 2.02.2026. Zgodnie z art. 106i ust. 1, faktura wystawia się nie później niż 15. dnia miesi
- **[6]** `law_knowledge.json` idx=2997
  - content: Fakturę należy wystawić nie później niż 15. dnia miesiąca następującego po miesiącu, w którym dokonano dostawy towaru lub wykonano usługę. Jeśli otrzy
- **[7]** `law_knowledge.json` idx=2998
  - content: Fakturę wystawia się nie później niż 15. dnia miesiąca następującego po miesiącu, w którym dokonano dostawy lub wykonano usługę. Nie ma obowiązku wyst
- **[8]** `law_knowledge.json` idx=2999
  - content: Fakturę wystawia się nie później niż 15. dnia miesiąca następującego po miesiącu, w którym dokonano dostawy towaru lub wykonano usługę. Data na faktur
- **[9]** `law_knowledge.json` idx=3000
  - content: Fakturę wystawia się nie później niż 15. dnia miesiąca następującego po miesiącu, w którym dokonano dostawy towaru lub wykonano usługę. Datą wystawien
- **[10]** `law_knowledge.json` idx=3001
  - content: Fakturę wystawia się nie później niż 15. dnia miesiąca następującego po miesiącu, w którym dokonano dostawy towaru lub wykonano usługę. To znaczy, że 
- **[11]** `law_knowledge.json` idx=3002
  - content: Fakturę wystawiasz najpóźniej do 15. dnia miesiąca następującego po miesiącu, w którym dokonano dostawy towaru lub wykonano usługę. Dla przykładu: usł
- **[12]** `law_knowledge.json` idx=3003
  - content: Fakturę wystawiasz najpóźniej do 15. dnia miesiąca następującego po miesiącu, w którym dokonałeś dostawy towaru lub wykonałeś usługę. Jeśli jednak otr
- **[13]** `law_knowledge.json` idx=3004
  - content: Fakturę za dostawę lub usługę wykonaną w danym miesiącu wystawiasz nie później niż 15. dnia miesiąca następującego. Dla dostawy/usługi z grudnia wysta
- **[14]** `law_knowledge.json` idx=3005
  - content: Nie, opóźnienie w dostarczeniu dokumentów przez klienta nie zwalnia Cię z obowiązku wystawienia faktury. Termin wystawienia liczę od dnia dostawy towa
- **[15]** `law_knowledge.json` idx=3006
  - content: Podstawową regułą jest wystawienie faktury nie później niż 15. dnia miesiąca następującego po miesiącu, w którym dokonano dostawy towaru lub wykonano 
- **[16]** `law_knowledge.json` idx=3007
  - content: Przepisy art. 106i-106b ustawy o VAT nie określają formy wysyłania faktury (papierowa, email, elektroniczna). Regulują jedynie obowiązek jej wystawien
- **[17]** `law_knowledge.json` idx=3008
  - content: Przepisy ustawy o VAT nie zawierają szczególnych regulacji dotyczących terminu wprowadzenia obowiązku faktur dla fotowoltaiki. Ogólnie: każdy podatnik
- **[18]** `law_knowledge.json` idx=3009
  - content: Przepisy VAT nie ustanawiają oddzielnego terminu dla wystawienia faktury korygującej. Faktura korygująca podlega jednak ogólnej zasadzie z art. 106i u
- **[19]** `law_knowledge.json` idx=3010
  - content: Tekst artykułu nie określa bezpośrednio zasad księgowania do VAT ani które daty wykorzystać do ewidencji VAT. Te informacje znajdują się w innych arty
- **[20]** `law_knowledge.json` idx=3011
  - content: Ustawa o VAT nie reguluje okresu zaliczenia kosztów do CIT. VAT wykazuje się z datą wystawienia faktury/korekty (art. 106i i 106j) - jeśli korekta wyd
- **[21]** `law_knowledge.json` idx=3012
  - content: Ustawę o VAT nie pozwala na wybór czasu wystawiania faktur w celach wygody — każda czynność (dostawa towaru, wykonanie usługi) musi być zdokumentowana

### Ustawa o VAT | art. 103 ust. 1  count=19, min_sim=0.0241, avg_sim=0.1889

- **[0]** `law_knowledge.json` idx=2762
  - content: Artykuł 103 reguluje wyłącznie termin wpłaty kwot podatku VAT. Zasady wyliczania VAT (netto vs brutto) i wykazywania zobowiązań z tytułu VAT zawarte s
- **[1]** `law_knowledge.json` idx=2763
  - content: Artykuł 103 reguluje wyłącznie termin wpłaty podatku VAT (do 25. dnia miesiąca następującego po miesiącu rozliczeniowym). Terminy składania deklaracji
- **[2]** `law_knowledge.json` idx=2764
  - content: Podatek VAT musisz wpłacić do 25. dnia miesiąca następującego po miesiącu, w którym powstał obowiązek podatkowy. Wpłata powinna być dokonana na rachun
- **[3]** `law_knowledge.json` idx=2765
  - content: Podatek VAT należy wpłacić w terminie do 25. dnia miesiąca następującego po miesiącu, w którym powstał obowiązek podatkowy (art. 103 ust. 1). Mali pod
- **[4]** `law_knowledge.json` idx=2766
  - content: Podatek VAT wpłacasz w terminie do 25. dnia miesiąca następującego po miesiącu, w którym powstał obowiązek podatkowy. Na przykład VAT za styczeń wpłac
- **[5]** `law_knowledge.json` idx=2767
  - content: Podatnicy rozliczający VAT miesięcznie muszą wpłacić podatek do 25. dnia miesiąca następującego po miesiącu, w którym powstał obowiązek podatkowy. Prz
- **[6]** `law_knowledge.json` idx=2768
  - content: Podatnicy są obowiązani wpłacić VAT za okres miesięczny do 25. dnia miesiąca następującego po miesiącu, w którym powstał obowiązek podatkowy (art. 103
- **[7]** `law_knowledge.json` idx=2769
  - content: Podatnicy VAT muszą wpłacić podatek za okresy miesięczne do 25. dnia miesiąca następującego po miesiącu, w którym powstał obowiązek podatkowy (art. 10
- **[8]** `law_knowledge.json` idx=2770
  - content: Przepisy ustawy o VAT nie regulują przeksięgowania nadpłat z PIT na VAT — ta materia należy do ustawy o podatku dochodowym. Zatem do czasu udzielenia 
- **[9]** `law_knowledge.json` idx=2771
  - content: Termin wpłaty podatku VAT zależy od okresu rozliczeniowego: dla podatników rozliczających się miesięcznie – do 25. dnia miesiąca następującego po mies
- **[10]** `law_knowledge.json` idx=2772
  - content: Termin wpłaty podatku VAT zależy od okresu rozliczeniowego podatnika. Dla podatników rozliczających się miesięcznie – wpłata do 25. dnia miesiąca nast
- **[11]** `law_knowledge.json` idx=2773
  - content: Ustawa o VAT nie reguluje warunków technicznych wpłat (waluty, opłaty bankowe, czasy transferu). Musisz wpłacić VAT na rachunek urzędu skarbowego w te
- **[12]** `law_knowledge.json` idx=2774
  - content: Ustawa o VAT nie reguluje, z jakiego konta lub jakim instrumentem płatniczym dokonywać wpłat podatku VAT. Artykuł 103 wymaga tylko wpłaty na rachunek 
- **[13]** `law_knowledge.json` idx=2775
  - content: Ustawa o VAT nie reguluje zasad identyfikacji przelewów ani skutków błędnych tytułów — ta materia należy do prawa obowiązków podatkowych i praktyki ur
- **[14]** `law_knowledge.json` idx=2776
  - content: Ustawa o VAT w art. 103 określa jedynie terminy i sposoby wpłaty podatku VAT na rachunek urzędu skarbowego, ale nie zawiera przepisów dotyczących spos
- **[15]** `law_knowledge.json` idx=2777
  - content: Ustawa o VAT wymaga wpłaty VAT do 25. dnia miesiąca następującego po miesiącu rozliczeniowym. Płatność wcześniejsza spełnia obowiązek (nie ma ryzyka o
- **[16]** `law_knowledge.json` idx=2778
  - content: Ustawa o VAT wymaga wpłaty VAT na rachunek urzędu skarbowego. Artykuł 103 nie precyzuje, czy możliwa jest płatność gotówką. Konieczna jest weryfikacja
- **[17]** `law_knowledge.json` idx=2779
  - content: VAT należny wykazujesz w terminie do 25. dnia miesiąca następującego po miesiącu, w którym powstał obowiązek podatkowy (art. 103 ust. 1). Dla większoś
- **[18]** `law_knowledge.json` idx=2780
  - content: VAT za grudzień musisz wpłacić do 25. stycznia następnego roku. Termin zawsze liczony jest od 25. dnia miesiąca następującego po miesiącu, w którym po

### Ustawa o rachunkowości | art. 32 ust. 1  count=5, min_sim=0.0244, avg_sim=0.122

- **[0]** `law_knowledge.json` idx=2355
  - content: Amortyzacja powinna być wykazana w kosztach operacyjnych bez ograniczenia do ceny sprzedaży. Art. 32 ust. 1 mówi jedynie, że podczas ustalania okresu 
- **[1]** `law_knowledge.json` idx=2356
  - content: Amortyzacja rozpoczyna się nie wcześniej niż po przyjęciu środka trwałego do używania (art. 32 ust. 1). Jeśli w zeszłym roku środek trwały został przy
- **[2]** `law_knowledge.json` idx=2357
  - content: Amortyzacja zakończy się najpóźniej z chwilą zrównania wartości odpisów amortyzacyjnych z wartością początkową środka trwałego (art. 32 ust. 1). Jeśli
- **[3]** `law_knowledge.json` idx=2358
  - content: Artykuł 32 ust. 1 wskazuje, że amortyzacja polega na systematycznym, planowym rozłożeniu wartości początkowej na ustalony okres. Metoda rachunkowa (np
- **[4]** `law_knowledge.json` idx=2359
  - content: Koszt zakupionego środka trwałego nie ujmuje się od razu jako koszt operacyjny. Wartość początkową (cenę nabycia) ujmuje się w aktywach (jako środek t

### Ustawa o podatku dochodowym od osób fizycznych | art. 45cd ust. 1  count=3, min_sim=0.0256, avg_sim=0.0857

- **[0]** `law_knowledge.json` idx=1833
  - content: Artykuł 45cd nie reguluje terminu ustalenia lub zwrotu podatku — określa jedynie procedurę udostępniania zeznania przez organ podatkowy (od 15 lutego)
- **[1]** `law_knowledge.json` idx=1834
  - content: Artykuły 45cd i 45cf nie określają terminu płatności różnicy podatkowej za cały rok podatkowy. Artykuły dotyczyć będą procedury akceptacji zeznania ro
- **[2]** `law_knowledge.json` idx=1835
  - content: Organ podatkowy udostępnia zeznanie najpóźniej do 15 lutego roku następującego po roku podatkowym. To oznacza, że zeznanie będzie dostępne w Twoim e-U

### Ustawa o podatku dochodowym od osób fizycznych | art. 22 ust. 1  count=7, min_sim=0.0263, avg_sim=0.1242

- **[0]** `law_knowledge.json` idx=1451
  - content: Aby opłata była kosztem uzyskania przychodu, musi być poniesiona w celu osiągnięcia przychodów lub zachowania/zabezpieczenia źródła przychodów (art. 2
- **[1]** `law_knowledge.json` idx=1452
  - content: Kosztami uzyskania przychodów są koszty poniesione w celu osiągnięcia przychodów lub zachowania albo zabezpieczenia źródła przychodów (art. 22 ust. 1)
- **[2]** `law_knowledge.json` idx=1453
  - content: Kosztami uzyskania przychodów są wyłącznie koszty poniesione w celu osiągnięcia przychodów lub zachowania albo zabezpieczenia źródła przychodów. Jeśli
- **[3]** `law_knowledge.json` idx=1454
  - content: Refakturowanie (rozliczenie kosztu z klientem) nie zmienia charakteru wydatku. Koszt jest odliczalny, jeśli został rzeczywiście poniesiony w celu uzys
- **[4]** `law_knowledge.json` idx=1455
  - content: Ustawa podatku dochodowego jest ścisła - koszty muszą być bezpośrednio związane z przychodami i faktycznie poniesione. Nie ma legalnych 'kruczków'. Ws
- **[5]** `law_knowledge.json` idx=1456
  - content: W PIT-B wykazujesz dochód (przychód minus koszty) z prowadzonej działalności. Jeśli skorzystałaś z ulgi termomodernizacyjnej, zmniejszyła ona dochód p
- **[6]** `law_knowledge.json` idx=1457
  - content: Zakupy (wydatki) wprowadzasz do księgi przychodów i rozchodów jako koszty uzyskania przychodów, jeśli zostały poniesione w celu osiągnięcia przychodów

## Recommendation

KB po dedup `true_duplicate`: **4472** rekordw (usunite: 72 z 60 grup). KB po dedup `true + near`: **4452** rekordw (usunite: 92 z 72 grup). `legitimate_variants`: **335** grup  do zachowania jako rne ujcia tego samego artykuu. **Sugerowana strategia:** w pierwszej kolejnoci dedupe tylko `true_duplicate` (bezpieczne, wysoka pewno  min Jaccard  0.85), zachowujc rekord z niepustym `verified_date` lub  jeli brak  z `law_knowledge_curated_additions.json`, potem `law_knowledge.json`. `near_duplicate` wymaga manualnego przegldu (moliwe redakcyjne warianty tego samego przepisu vs. komplementarne wyjanienia). Grupy oznaczone `potential_key_collision` (count > 10) mog sygnalizowa kolizj klucza `(law_name, article_number)`  rozway wzbogacenie klucza o `paragraph` lub `ustep` przed dedup.
