# Workflow Evaluation Report

- Records evaluated: 347
- workflow_expected: 150
- legal_expected: 150
- mixed_expected: 47

## Core metrics

- workflow_path_precision: 0.8496
- legal_path_precision: 0.7548
- workflow_recall_on_workflow_questions: 0.48
- legal_leakage_into_workflow: 0.1333
- workflow_leakage_into_legal: 0.24

## Clarification rate per subset

| Subset | Clarification rate |
|---|---:|
| workflow_expected | 0.8267 |
| legal_expected | 0.84 |
| mixed_expected | 0.5106 |

## Top routing failures

### Workflow -> legal

- `legal` | freq=4 | Do tej pory przy pobranych fakturach z KSeF do Comarch miałam przypisane "do rejestru VAT" oraz obok "V" przy statusie, że przeniesionk. Teraz mimo że faktury pobrane do rejestru to nie mam "V" czy ktoś też tak ma? Dlaczego tak się dzieje?
- `legal` | freq=4 | Faktura za odprawę celna w GB traktujemy jak import uslug i ksiegowanie z datą grudniową/towar został wysłany w listopadzie/dziękuję?
- `legal` | freq=4 | Zgadza się?
- `legal` | freq=3 | A na jakiej podstawie?
- `legal` | freq=3 | Czy spółka zoo może udzielić pożyczki wspólnikowi? —?
- `legal` | freq=3 | Szukam doradcy podatkowego lub księgowej zorientowanej w temacie aportu ZCP do spółki komandytowej od strony księgowej?
- `legal` | freq=3 | W takim razie rozliczam to jako import od kwoty brutto czy jako transakcja krajowa?
- `legal` | freq=2 | ) płacił ten abonament i to w odniesieniu do radia w samochodzie?
- `legal` | freq=2 | . Czy będąc na umowie o pracę i płacąc składki tylko zdrowotne z działalności mogę zapisać się do dobrowolnego ZUS?
- `legal` | freq=2 | . Czy ktoś z Was księguje przedszkole (księgowość uproszczona)?

### Legal -> workflow

- `workflow` | freq=20 | Czy jeśli faktura była w KSeF wystawiona 3 lutego ale numer nadany 5 lutego to jaka jest ostatecznie data wystawienia faktury pod którą powinnam zaksięgować koszt do kpir?
- `workflow` | freq=16 | Czy mogę odliczyć VAT w styczniu (faktura wystawiona w grudniu), ale tylko odliczę VAT w styczniu a nie będę ujmować kosztu w kpir?
- `workflow` | freq=15 | Klient dał mi uprawnienia do przeglądania faktur i logowałam się na jego KSeF i widzę faktury ale na OPTIMIE mi ich nie pobiera, musi być token?
- `workflow` | freq=9 | Jak to ująć w KPiR - przychód za okres, którego dotyczy, a wydatek pod datą wystawienia?
- `workflow` | freq=8 | Czy znajdzie się tutaj księgowość dla firmy (spółka z o.o.), która udostępnia w abonamencie narzędzie online dla firm (SaaS)?
- `workflow` | freq=7 | Czy w Waszych biura h rachunkowych też tak jest, że potwierdzenia sald drukujecie i przychodzi je odebrać ktoś z firmy, sami podpisują i wysyłają?
- `workflow` | freq=6 | Https://docs.google.com/forms/d/e/1FAIpQLSceIwmXCXJrGd0jYXamfEWBbHJM-XUtYRZXaIxlzi_jRXGbaQ/viewform?
- `workflow` | freq=6 | Jak księgujecie takie faktury?
- `workflow` | freq=5 | . Klient wystawił fakturę końcem grudnia sprzedał towar handlowy samochód okazało się że bez twardego dowodu?
- `workflow` | freq=5 | Czy faktura wystawiona w marcu ale za wywóz nieczystości w lutym idzie ksiegowo do dochodowego w marcu pod data wystawienia jako koszt pośredni?

### Mixed weak routing

- `legal` | freq=2 | JPK CIT Jak ustawić w systemie oznaczenia różnic przejściowych typu ZUS , umowy zlecenie jeżeli nie mam kont pozabilansowych?
- `legal` | freq=1 | Gdzie wpisać kwotę z poz?

## Strongest workflow areas

- JPK filing / correction / tags — avg_score=14.8421 (19 queries)
- KSeF issuing / correction / invoice circulation — avg_score=14.8125 (56 queries)
- ZUS / PUE / zgłoszenia i wyrejestrowania — avg_score=11.5405 (37 queries)
- Dokumenty księgowe / magazyn / kolumny i klasyfikacja — avg_score=10.8958 (24 queries)
- Sprawozdanie finansowe / podpis / wysyłka — avg_score=9.6316 (38 queries)

## Weakest workflow areas

- Pełnomocnictwa / podpis / kanały złożenia — avg_score=5.5312 (16 queries)
- Oprogramowanie księgowe / integracje / synchronizacja — avg_score=7.6875 (32 queries)
- KPiR / księgowanie / okresy i memoriał — avg_score=8.9 (70 queries)
- KSeF permissions / authorization flow — avg_score=9.0625 (32 queries)
- Sprawozdanie finansowe / podpis / wysyłka — avg_score=9.6316 (38 queries)

## Recommendation

Wzmocnić workflow seed dla obszarów z najniższym workflow_score i najwyższym wolumenem workflow->legal, zwłaszcza tam, gdzie pytania są operacyjne, ale nie łapią się na confident workflow hit.
