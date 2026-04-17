# Workflow Answer Quality Evaluation

- Records evaluated: 207
- Workflow answer expected: 80
- Legal answer expected: 80
- Legal fallback expected: 47

## Metrics

- workflow_format_rate: 1.0
- workflow_section_completeness: 1.0
- sparse_unit_safety_rate: 1.0
- legal_path_contamination_rate: 0.1732
- workflow_fallback_safety_rate: 0.0638
- workflow_clarification_rate: 0.8375
- legal_safety_rate: 0.975

## Top Weak Workflow Answers

- Jaki program do księgowania polecacie do rozliczania najpierw jednej firmy a w dalszej perspektywie może kolejnych? | path=clarification | sections=none
- Jak to prawidłowo ująć koszty dotyczące tamtego roku, które dopiero teraz przyszły? | path=clarification | sections=none
- Mam fakturę wystawioną 03.02.2026 przez Miasto Stołeczne Warszawa - na górze napis Krajowy system e- Faktur, na dole kod qr a pod nim napis offline, dzis sprawdzam w systemie klienta KSeF ale faktura się nie pojawiła - czyl co oznaczac off w JPK i nie czekać bo ona już się tam nie pojawi? | path=clarification | sections=none
- Odliczam 100% VAT.Leasing (kapitał) nie jest ograniczony proporcja, ponieważ samochód nie jest traktowany jako osobowy w świetle VAT/PIT? | path=clarification | sections=none
- Samochód został wykupiony z leasingu i nie przekazany do firmy, czy teraz można księgować koszty 20 %? | path=clarification | sections=none
- Szukam osoby do pracy w księgowości do biura rachunkowego w Rzeszowie, ze znajomością przepisów i Optimy? | path=clarification | sections=none
- Dlaczego bilansowo do 10/25? Towar idzie na magazyn, to chcesz naginać rzeczywistość, że go nie było już w 2025? | path=clarification | sections=none
- Czy towar idzie do kolumny "zakup towarów", a koszty "koszty uboczne zakupu", czy "pozostałe wydatki? | path=workflow | sections=Krótko
- Jak należy postąpić w przypadkach leasingu operacyjnego z lat poprzednich, gdy samochód nie jest ujęty jako ŚT? | path=clarification | sections=none
- Sprawozdanie finansowe Forma prawna i jest mnóstwo oznaczeń -ma ktoś spis co do którego oznacza? | path=clarification | sections=none

## Top Cases Where Workflow Formatting Should Have Happened But Did Not

- none

## Top Safe Legal Fallback Cases

- Jak technicznie ujmujecie rachunki z umowy zlecenie żeby zgodziły się koszty bilansowe i podatkowe (żeby dało się przyporządkować odpowiednie znaczniki a przy okazji żeby prawidłowo liczyła się zaliczka miesięczna/kwartalna na CIT)? | path=legal_fallback
- Jak zaksiegujecie fakture kosztowa ,która jest refakturą za energie elektryczna? | path=legal_fallback
- Kolumna 32-dochód zwolniony od podatku 253,28zl (kompensata za pranie ciuchów roboczych), gdzie wpisać w PIT-37? | path=legal

## Sparse Workflow Units To Enrich First

- Klasyfikacja dokumentów, kolumn i zapisów magazynowych (4)
- Przygotowanie, podpisanie i wysyłka sprawozdania finansowego (1)
- Obieg faktur, statusów i korekt w KSeF (1)
- Obsługa problemów systemowych i synchronizacji danych (1)

## Recommendation

- enrich workflow seed
