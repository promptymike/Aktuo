# Intent Confusion Report

Total wrong-intent failures: **79**

## Top confusion pairs (ranked by total frequency)

| # | Expected | Predicted | Count | Freq | Suggested fix |
|---|----------|-----------|-------|------|---------------|
| 1 | legal_substantive | business_of_accounting_office | 6 | 25 | Hints 'klient', 'biuro rachunkowe' are too broad and capture legal_substantive q |
| 2 | legal_procedural | business_of_accounting_office | 9 | 16 | Hints 'klient', 'biuro rachunkowe' are too broad and capture legal_procedural qu |
| 3 | hr | business_of_accounting_office | 1 | 16 | Hints 'klient', 'biuro rachunkowe' are too broad and capture hr queries. Add dis |
| 4 | vat_jpk_ksef | unknown | 1 | 16 | Add keyword hints for vat_jpk_ksef to INTENT_KEYWORD_HINTS (missing anchor words |
| 5 | zus | business_of_accounting_office | 4 | 13 | Hints 'klient', 'biuro rachunkowe' are too broad and capture zus queries. Add di |
| 6 | legal_substantive | education_community | 2 | 12 | Community hints ('polecacie', 'jak zaczac') capture legal_substantive queries. A |
| 7 | software_tooling | vat_jpk_ksef | 3 | 11 | Broad VAT hints ('faktura', 'nip') pull software_tooling queries into vat_jpk_ks |
| 8 | vat_jpk_ksef | pit_ryczalt | 2 | 10 | The hint 'pit' in pit_ryczalt is overly broad — it captures vat_jpk_ksef queries |
| 9 | legal_substantive | out_of_scope | 1 | 9 | Add disambiguating keyword hints to separate legal_substantive from out_of_scope |
| 10 | accounting_operational | business_of_accounting_office | 3 | 8 | Hints 'klient', 'biuro rachunkowe' are too broad and capture accounting_operatio |
| 11 | pit_ryczalt | vat_jpk_ksef | 2 | 8 | Broad VAT hints ('faktura', 'nip') pull pit_ryczalt queries into vat_jpk_ksef. A |
| 12 | vat_jpk_ksef | out_of_scope | 1 | 8 | Add disambiguating keyword hints to separate vat_jpk_ksef from out_of_scope. Rev |
| 13 | legal_substantive | accounting_operational | 1 | 7 | Broad accounting hints pull legal_substantive queries into accounting_operationa |
| 14 | zus | unknown | 3 | 6 | Add keyword hints for zus to INTENT_KEYWORD_HINTS (missing anchor words). |
| 15 | cit_wht | unknown | 3 | 6 | Add keyword hints for cit_wht to INTENT_KEYWORD_HINTS (missing anchor words). |
| 16 | education_community | vat_jpk_ksef | 3 | 6 | Add out_of_scope / community anchors so queries stop matching vat_jpk_ksef. |
| 17 | hr | payroll | 2 | 6 | Add disambiguating keyword hints to separate hr from payroll. Review overlapping |
| 18 | hr | accounting_operational | 2 | 6 | Broad accounting hints pull hr queries into accounting_operational. Add domain-s |
| 19 | vat_jpk_ksef | legal_substantive | 1 | 6 | Add disambiguating keyword hints to separate vat_jpk_ksef from legal_substantive |
| 20 | legal_procedural | education_community | 3 | 5 | Community hints ('polecacie', 'jak zaczac') capture legal_procedural queries. Ad |

## Detailed examples (top 10 pairs)

### legal_substantive → business_of_accounting_office (6 records, freq=25)

- Jeśli spółka pieczęć lub po złożeniu zaw fa jdg profil zaufany podpis kwalifikowany?
- Czy jest ktoś na grupie kto rozlicza usługi kateringowe dokładnie dostawców/menadżerów w kuchni vikinga?
- Czy wie ktoś coś o systemie SENT? Jak to ma się do ubrań, jak klient wozi detaliczne ilośći ma robić wszystkie procedury?
- Czy wystarczy jak Klient zbiera sobie te potwierdzenia na wypadek kontroli?
- Jak będziecie sobie radzić od stycznia wprowadzać dokumenty do 20 następnego dnia miesiaca?

**Fix**: Hints 'klient', 'biuro rachunkowe' are too broad and capture legal_substantive queries. Add disambiguating hints for legal_substantive.

### legal_procedural → business_of_accounting_office (9 records, freq=16)

- Chciałabym zapytać jak sprzedaje firmą towar z montażem , to fv sprzedaży trzeba rozdzielić na towar i usługę , tak żeby wszystko zgadzało się w reman
- Czy to jest osobna usługa i nie stosuje proporcji? —?
- Jak sobie radzicie z kontrolą wszystkiego?
- Jak wiadomo, przy składaniu wniosku należy podać swoje dane i dane US. — :)?
- Składając ZAWFa do urzędu skarbowego aby nadać uprawnienia do spółki cywilnej dla siebie powinnam w danych osoby uprawnionej do korzystania poddać ide

**Fix**: Hints 'klient', 'biuro rachunkowe' are too broad and capture legal_procedural queries. Add disambiguating hints for legal_procedural.

### hr → business_of_accounting_office (1 records, freq=16)

- Czy to jest poprawne?

**Fix**: Hints 'klient', 'biuro rachunkowe' are too broad and capture hr queries. Add disambiguating hints for hr.

### vat_jpk_ksef → unknown (1 records, freq=16)

- Czy to prawda?

**Fix**: Add keyword hints for vat_jpk_ksef to INTENT_KEYWORD_HINTS (missing anchor words).

### zus → business_of_accounting_office (4 records, freq=13)

- Jaka cena za usługę?
- Czy jako biura rachunkowe, ksiegowosc macie ubezpieczenia na wypadek pomyłek?. —?
- Czy zmiana formy opodatkowania jest zgłaszana tylko do US?
- Dotyczące formularza A1.Prowadzę jednoosobową działalność gospodarczą w branży budowlanej w Polsce. —?

**Fix**: Hints 'klient', 'biuro rachunkowe' are too broad and capture zus queries. Add disambiguating hints for zus.

### legal_substantive → education_community (2 records, freq=12)

- Czy znajdzie się tutaj księgowość dla firmy (spółka z o.o.), która udostępnia w abonamencie narzędzie online dla firm (SaaS)?
- Osoba ma jdg, czy może otworzyć spółkę cywilną, gdzie udziałowcem będzie jdg Jan Kowalski i Jan Kowalski jako osoba fizyczna?

**Fix**: Community hints ('polecacie', 'jak zaczac') capture legal_substantive queries. Add more specific anchors for legal_substantive.

### software_tooling → vat_jpk_ksef (3 records, freq=11)

- Do tej pory przy pobranych fakturach z KSeF do Comarch miałam przypisane "do rejestru VAT" oraz obok "V" przy statusie, że przeniesionk. Teraz mimo że
- Faktura za odprawę celna w GB traktujemy jak import uslug i ksiegowanie z datą grudniową/towar został wysłany w listopadzie/dziękuję?
- Jak zaksięgowalibyście fakturę od Apple (NIP UE – Irlandia) jako import usług zgodnie z art. 28b ustawy o VAT?

**Fix**: Broad VAT hints ('faktura', 'nip') pull software_tooling queries into vat_jpk_ksef. Add stronger anchors for software_tooling.

### vat_jpk_ksef → pit_ryczalt (2 records, freq=10)

- Czy faktura wystawiona w marcu ale za wywóz nieczystości w lutym idzie ksiegowo do dochodowego w marcu pod data wystawienia jako koszt pośredni?
- Czy ktoś mógłby pomóc? Mam fakturę za leasing samochodu wystawiona 23.02, a data zakończenia 09.03? ja to rozliczyć w kosztach bilansowych i KUP? w kt

**Fix**: The hint 'pit' in pit_ryczalt is overly broad — it captures vat_jpk_ksef queries that mention PIT forms. Add disambiguating hints to vat_jpk_ksef or narrow pit_ryczalt.

### legal_substantive → out_of_scope (1 records, freq=9)

- Co o tym myślicie?

**Fix**: Add disambiguating keyword hints to separate legal_substantive from out_of_scope. Review overlapping tokens.

### accounting_operational → business_of_accounting_office (3 records, freq=8)

- Czy spółka zoo może udzielić pożyczki wspólnikowi? —?
- Potrzebuję pomocy przy księgowaniu dewelopera, jeżeli ktoś miał do czynienia z takim profilem działalności, proszę o odzew?
- .Jako firma (spółka akcyjna, pełne księgi) wzięliśmy udział w promocji i po spełnieniu warunków nieodpłatnie otrzymaliśmy prezent w postaci akumulator

**Fix**: Hints 'klient', 'biuro rachunkowe' are too broad and capture accounting_operational queries. Add disambiguating hints for accounting_operational.
