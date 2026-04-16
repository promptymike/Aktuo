# Workflow Evaluation Report

- Records evaluated: 347
- workflow_expected: 150
- legal_expected: 150
- mixed_expected: 47

## Core metrics

- workflow_path_precision: 0.7356
- legal_path_precision: 0.6188
- workflow_recall_on_workflow_questions: 0.3267
- legal_leakage_into_workflow: 0.1533
- workflow_leakage_into_legal: 0.2933

## Clarification rate per subset

| Subset | Clarification rate |
|---|---:|
| workflow_expected | 0.86 |
| legal_expected | 0.86 |
| mixed_expected | 0.7872 |

## Top routing failures

### Workflow -> legal

- `legal` | freq=4 | Czy brać pod uwagę tylko SKWP czy może Fundację Rozwoju Rachunkowości czy Krajową Izbę Księgowych?
- `legal` | freq=4 | Faktura za odprawę celna w GB traktujemy jak import uslug i ksiegowanie z datą grudniową/towar został wysłany w listopadzie/dziękuję?
- `legal` | freq=4 | Pod jaki KŚT dać taki zakup? 337 jako kompensatory synchroniczne?
- `legal` | freq=4 | Prosze o pomoc jak zaksięgować fv na której jest zakup towarów do sprzedazy oraz zakup, który powinien być w kosztach?
- `legal` | freq=4 | Zgadza się?
- `legal` | freq=3 | A jaką datę przyjąć do zaksięgowania na koncie 300- rozliczenie zakupu?
- `legal` | freq=3 | A na jakiej podstawie?
- `legal` | freq=3 | Czy spółka zoo może udzielić pożyczki wspólnikowi? —?
- `legal` | freq=3 | Data wystawienia 28.02 Data zapisania w KSeF /otrzymania 02.03.2026 Mogę zaksięgować w KPiR pod data 28.02?
- `legal` | freq=3 | Jaka jest wasza opinia na ten temat?

### Legal -> workflow

- `workflow` | freq=21 | Czy ktoś księguje w InFakt i może podpowiedzieć gdzie tu widać oznaczenia w JPK BFK itp?
- `workflow` | freq=15 | Czy sprzedaż internetową na osoby prywatne na paragony bez fiskalizacji mogę wykazać zbiorczo do JPK dowolnym dokumentem bez oznaczenia RO?
- `workflow` | freq=15 | Klient dał mi uprawnienia do przeglądania faktur i logowałam się na jego KSeF i widzę faktury ale na OPTIMIE mi ich nie pobiera, musi być token?
- `workflow` | freq=11 | Czy działa Wam „ e płatnik „ na pue ZUS?
- `workflow` | freq=9 | Korekta in minus kosztowa: wystawiona 20.02 dot usługi z 12.02. VAT i dochodowy księguję pod datą wystawienia 20.02?
- `workflow` | freq=8 | W pue wyskakują mi jakieś błędy,Podpowie dobra duszyczka ile wynoszą łącznie teraz składki na ZUS preferencyjny ryczałt 60k-300k?
- `workflow` | freq=7 | Czy w Waszych biura h rachunkowych też tak jest, że potwierdzenia sald drukujecie i przychodzi je odebrać ktoś z firmy, sami podpisują i wysyłają?
- `workflow` | freq=7 | Kasa fiskalna a dzierżawa gruntów sprzedaż osoby fizyczne Dzień dobry, przedsiębiorstwo dzierżawi grunty pod garaże blaszane i lokale użytkowe czy wystawiając fakturę z forma płatności przelew przedsiębiorstwo nadal musi posiadać kasę fiskalną od 1.04?
- `workflow` | freq=6 | Https://docs.google.com/forms/d/e/1FAIpQLSceIwmXCXJrGd0jYXamfEWBbHJM-XUtYRZXaIxlzi_jRXGbaQ/viewform?
- `workflow` | freq=6 | Jakiego oznaczenia użylibyście w przypadku faktur wewnętrznych, wykazujących VAT należny od transakcji WNT: BFK czy DI?

### Mixed weak routing

- `legal` | freq=2 | JPK CIT Jak ustawić w systemie oznaczenia różnic przejściowych typu ZUS , umowy zlecenie jeżeli nie mam kont pozabilansowych?
- `legal` | freq=2 | Jak ująć taka korektę w JPK?
- `legal` | freq=2 | Jak zaksięgować to na kontach z rozliczeniem VAT?
- `legal` | freq=2 | Pełne księgi. Jak zaksięgować? VAT i koszty do lutego?
- `legal` | freq=2 | Wiem, że VAT dopiero wykaże w JPK w styczniu, ale jak zaksięgować (na jakie konta) tą fakturę w 2025 roku?
- `legal` | freq=2 | Wytłumaczy ktoś jak ująć fakturę z PLAY wystawioną w KSeF?
- `legal` | freq=1 | ...jak ując do VAT paragon za wpłatę zwrotnego depozytu OBU czechy?
- `legal` | freq=1 | A ja myślę że skoro nota wystawiona i otrzymana w styczniu to tak powinniśmy jak zaksięgować i zapłacić VAT za styczeń a nie dopiero jak otrzymamy zapłatę?
- `legal` | freq=1 | Canva,subskrypcja z VAT 23%, jak zaksięgować na kh?
- `legal` | freq=1 | Czy księgować w koszty netto czy brutto oraz jak zaksięgować VAT w księgach?

## Strongest workflow areas

- JPK filing / correction / tags — avg_score=16.0263 (19 queries)
- KSeF issuing / correction / invoice circulation — avg_score=13.9688 (64 queries)
- ZUS / PUE / zgłoszenia i wyrejestrowania — avg_score=10.0349 (43 queries)
- Dokumenty księgowe / magazyn / kolumny i klasyfikacja — avg_score=9.86 (25 queries)
- Sprawozdanie finansowe / podpis / wysyłka — avg_score=8.6977 (43 queries)

## Weakest workflow areas

- Pełnomocnictwa / podpis / kanały złożenia — avg_score=5.1429 (21 queries)
- Oprogramowanie księgowe / integracje / synchronizacja — avg_score=6.9483 (29 queries)
- KSeF permissions / authorization flow — avg_score=8.119 (42 queries)
- KPiR / księgowanie / okresy i memoriał — avg_score=8.6212 (33 queries)
- Sprawozdanie finansowe / podpis / wysyłka — avg_score=8.6977 (43 queries)

## Recommendation

Wzmocnić workflow seed dla obszarów z najniższym workflow_score i najwyższym wolumenem workflow->legal, zwłaszcza tam, gdzie pytania są operacyjne, ale nie łapią się na confident workflow hit.
