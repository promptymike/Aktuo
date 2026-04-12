# Eval Failure Priorities

Failed records: **344**

## Root cause summary

| Root cause | Count | Total frequency | Example questions |
| --- | ---: | ---: | --- |
| wrong_category_match | 132 | 435 | Czy to jest poprawne?<br>Czy od samochodu Opel combo van, który ma wpisane w dowodzie rejestracyjnym samochód ciężarowy do 3,5 t, można odliczać 100% VAT?<br>Samochód osobowy z leasingiem operacyjnymWartość powyżej 100 tys bruttoZgłoszony do VAT-26Czy leasing odliczam proporcje? |
| wrong_law_priority | 2 | 12 | Jeśli mam kogoś na zleceniu, ale w 2025 nie przepracował ani 1h i nie zarobił ani 1zł to czy muszę wystawiać zerowy PIT4R?<br>, jak oznaczyć import usług w programie comarvh optima jezeli dotyczy on tylko jednej poxycji na fakturze? |
| needs_clarification_but_answered | 51 | 263 | Faktura wystawiona 1 kwietnia, czyli najpóźniej 2 kwietnia powinna być w KSeF przy założeniu trybu offline, ale nie dotarła?<br>Czy ktoś księguje w InFakt i może podpowiedzieć gdzie tu widać oznaczenia w JPK BFK itp?<br>Faktura do paragonu z kodem GTU - znacznik w JPK VAT - FP, BFK, GTU_?Faktura do paragonu z kodem GTU - znacznik w JPK VAT - FP, BFK, GTU_? |
| unknown | 159 | 775 | Szukam osoby, która wdroży mnie w pfron, tzn rejestracje pełnomocnictwa i składanie wniosków, oczywiście za opłatą?<br>W trakcie użytkowania odliczałam 50% VAT (paliwa, koszty eksploatacji). Czy ta darowizna powinna być opodatkowana VAT?<br>A czemu nie? |

## Top 20 suggested fixes

| Rank | Root cause | Count | Total frequency | Expected area | Suggested fix | Example question |
| ---: | --- | ---: | ---: | --- | --- | --- |
| 1 | needs_clarification_but_answered | 18 | 171 | VAT / JPK / KSeF | Tighten clarification rules for underspecified vat_jpk_ksef questions. | Faktura wystawiona 1 kwietnia, czyli najpóźniej 2 kwietnia powinna być w KSeF przy założeniu trybu offline, ale nie dotarła? |
| 2 | unknown | 10 | 117 | przepisy materialne | Review failed legal_substantive examples manually and refine the weakest layer first. | Szukam osoby, która wdroży mnie w pfron, tzn rejestracje pełnomocnictwa i składanie wniosków, oczywiście za opłatą? |
| 3 | wrong_category_match | 21 | 104 | przepisy materialne | Adjust intent routing so legal_substantive queries are not misclassified. | Może ktoś podpowie? |
| 4 | unknown | 9 | 98 | VAT / JPK / KSeF | Review failed vat_jpk_ksef examples manually and refine the weakest layer first. | W trakcie użytkowania odliczałam 50% VAT (paliwa, koszty eksploatacji). Czy ta darowizna powinna być opodatkowana VAT? |
| 5 | unknown | 22 | 95 | rachunkowość operacyjna | Review failed accounting_operational examples manually and refine the weakest layer first. | Jak to prawidłowo ująć koszty dotyczące tamtego roku, które dopiero teraz przyszły? |
| 6 | unknown | 19 | 95 | oprogramowanie księgowe | Review failed software_tooling examples manually and refine the weakest layer first. | Jaki program do księgowania polecacie do rozliczania najpierw jednej firmy a w dalszej perspektywie może kolejnych? |
| 7 | unknown | 21 | 76 | ZUS | Review failed zus examples manually and refine the weakest layer first. | Czy działa Wam „ e płatnik „ na pue ZUS? |
| 8 | unknown | 19 | 69 | CIT / WHT | Review failed cit_wht examples manually and refine the weakest layer first. | Czy nadal trzeba pisać pisma o stwierdzenie nadpłaty i zwrot jesli wynika z cit8? Czy sami zwrócą? |
| 9 | unknown | 12 | 66 | PIT / ryczałt | Review failed pit_ryczalt examples manually and refine the weakest layer first. | Najem prywatny wykazywany w JPK osoby prowadzącej działalność bez faktury, oznaczenia Di i WEW?? |
| 10 | wrong_category_match | 14 | 56 | Kodeks pracy | Adjust intent routing so hr queries are not misclassified. | Czy to jest poprawne? |
| 11 | unknown | 5 | 52 | PIT / ryczałt + rachunkowość operacyjna | Review failed pit_ryczalt examples manually and refine the weakest layer first. | Czy jeśli faktura była w KSeF wystawiona 3 lutego ale numer nadany 5 lutego to jaka jest ostatecznie data wystawienia faktury pod którą powinnam zaksięgować koszt do kpir? |
| 12 | wrong_category_match | 6 | 47 | VAT / JPK / KSeF | Adjust intent routing so vat_jpk_ksef queries are not misclassified. | Czy od samochodu Opel combo van, który ma wpisane w dowodzie rejestracyjnym samochód ciężarowy do 3,5 t, można odliczać 100% VAT? |
| 13 | wrong_category_match | 13 | 39 | rachunkowość operacyjna | Adjust intent routing so accounting_operational queries are not misclassified. | Czy brać pod uwagę tylko SKWP czy może Fundację Rozwoju Rachunkowości czy Krajową Izbę Księgowych? |
| 14 | unknown | 9 | 39 | Kodeks pracy | Review failed hr examples manually and refine the weakest layer first. | DRA w jdg bez pracownikówSkładki społeczne wykazuje w miejscu finansowane przez ubezpieczonego czy płatnika składek? |
| 15 | wrong_category_match | 10 | 38 | PIT / ryczałt | Adjust intent routing so pit_ryczalt queries are not misclassified. | Czy w Waszych biura h rachunkowych też tak jest, że potwierdzenia sald drukujecie i przychodzi je odebrać ktoś z firmy, sami podpisują i wysyłają? |
| 16 | unknown | 17 | 36 | kadry i płace | Review failed payroll examples manually and refine the weakest layer first. | Czy pit11 można wysłać jeszcze 2 lutego z uwagi na weekend? |
| 17 | wrong_category_match | 10 | 33 | edukacja i społeczność | Adjust intent routing so education_community queries are not misclassified. | Szukam biura, które jak trzeba to skieruje na badania medycyny pracy, podpowie kontakt na szkolenie bhp, podpowie co zrobic by było dobrze/ lepiej (jest kreatywne.)? |
| 18 | wrong_category_match | 12 | 32 | ZUS | Adjust intent routing so zus queries are not misclassified. | Jaka cena za usługę? |
| 19 | unknown | 15 | 30 | Ordynacja podatkowa / procedury | Review failed legal_procedural examples manually and refine the weakest layer first. | Stosunek powierzchni wydaje się rozsądny dla opłat typu czynsz, podatek od nieruchomości, ogrzewanie, ale czy zużycie energii? |
| 20 | needs_clarification_but_answered | 9 | 30 | oprogramowanie księgowe | Tighten clarification rules for underspecified software_tooling questions. | Szukam osoby , która pracuje w programie symfonia e - biuro i jest w stanie odpłatnie wdrożyć w ten program? |
