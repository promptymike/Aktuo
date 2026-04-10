# Stress test na realnych pytaniach FB

Data: 2026-04-10

Zakres: top 10 pyta? `vat`, top 10 pyta? `pit`, top 10 pyta? `cit` wed?ug `freq`.

## Podsumowanie

- `PARTIAL`: `7`
- `FAIL`: `23`

## Wyniki per pytanie

### VAT | freq 26 | PARTIAL
W trakcie użytkowania odliczałam 50% VAT (paliwa, koszty eksploatacji). Czy ta darowizna powinna być opodatkowana VAT?

1. `PARTIAL` ? `Ustawa o VAT | art. 86a ust. 1 | score 50.5079`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Od wydatków związanych z samochodami odliczasz 50% VAT (art. 86a ust. 1). To dotyczy nabycia, importu, paliwa, napraw, ubezpieczenia i wszystkich kosztów eksploatacji samochodu. Wyjątek: jeśli samochód jest wykorzystywan
   - ?r?d?o ISAP: 86a: Art. 86a. 1. W  przypadku wydatków związanych z  pojazdami samochodowymi kwotę podatku naliczonego, o  której mowa w  art. 86 ust.  2, stanowi 50 % kwoty podatku: 1) wynikającej z faktury otrzymanej przez podatnika; 2) należnego z tytułu: a
2. `PARTIAL` ? `Ustawa o VAT | art. 86a ust. 2 pkt 3 | score 37.4218`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: VAT od paliwa do samochodu firmowego odliczasz według tych samych zasad co od samochodu. Jeśli pojazd nie jest wykorzystywany wyłącznie do działalności gospodarczej - odliczasz 50% VAT. Jeśli jest używany wyłącznie bizne
   - ?r?d?o ISAP: 86a: Art. 86a. 1. W  przypadku wydatków związanych z  pojazdami samochodowymi kwotę podatku naliczonego, o  której mowa w  art. 86 ust.  2, stanowi 50 % kwoty podatku: 1) wynikającej z faktury otrzymanej przez podatnika; 2) należnego z tytułu: a
3. `PARTIAL` ? `Ustawa o VAT | art. 113 ust. 5 | score 34.5055`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Zwolnienie traci moc od czynności, którą przekraczasz próg 240 000 zł. Oznacza to, że już ta transakcja powinna być opodatkowana VAT, a następnie wszystkie kolejne transakcje w roku. Od tego momentu musisz wystawiać fakt
   - ?r?d?o ISAP: 113: Art. 113. 1. Zwalnia się od podatku sprzedaż dokonywaną przez podatnika posiadającego siedzibę działalności gospodarczej na terytorium kraju, u  którego wartość sprzedaży, z  wyłączeniem podatku, nie przekroczyła w  poprzednim ani bieżącym 

### VAT | freq 16 | FAIL
Czy mogę odliczyć VAT w styczniu (faktura wystawiona w grudniu), ale tylko odliczę VAT w styczniu a nie będę ujmować kosztu w kpir?

1. `FAIL` ? `Ustawa o rachunkowości | art. 6 ust. 1 | score 22.6571`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Zgodnie z ustawą o rachunkowości, wszystkie przychody i koszty należy ujmować w księgach w danym roku obrotowym, niezależnie od terminu ich zapłaty (zasada memoriału). Ustawa nie wspomina o magazynie walut jako zasadzie 
2. `FAIL` ? `Ustawa o rachunkowości | art. 39 ust. 2 pkt 1 | score 15.5161`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Tak, powinna być ujęta w bilansie grudnia poprzez bierne rozliczenia międzyokresowe kosztów. Zgodnie z art. 39 ust. 2, tworzy się bierne rozliczenia dla kosztów przyszłych okresów, które przypadają na bieżący okres spraw
3. `FAIL` ? `Ustawa o rachunkowości | art. 39 ust. 1 i 3 | score 13.6764`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Ustawa o rachunkowości nie precyzuje, czy RMK ma być wyliczany od kwoty netto czy brutto. Art. 39 mówi jedynie, że RMK odpisuje się w koszty stosownie do upływu czasu lub wielkości świadczeń, z zachowaniem zasady ostrożn

### VAT | freq 13 | PARTIAL
Czy w takiej sytuacji przysługuje mu pełne odliczenie VAT czy np jak to jest z samochodami w leasingu w mieszanym użytkowaniu 50%?

1. `PARTIAL` ? `Ustawa o VAT | art. 86 ust. 1 | score 44.8851`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Prawo do odliczenia VAT przysługuje w zakresie, w jakim towary i usługi są wykorzystywane do wykonywania czynności opodatkowanych. Oznacza to, że jeśli zakup dotyczy częściowo działalności podlegającej opodatkowaniu VAT,
   - ?r?d?o ISAP: 86: Art. 86. 1. W  zakresie, w  jakim towary i  usługi są wykorzystywane do wykonywania czynności opodatkowanych, podatnikowi, o którym mowa w art. 15, przysługuje prawo do obniżenia kwoty podatku należnego o  kwotę podatku naliczonego, z  zast
2. `PARTIAL` ? `Ustawa o VAT | art. 86 ust. 1 | score 29.2246`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Tak, prawo do odliczenia VAT z faktury za zwykły koszt (np. materiały, usługi) przysługuje w rozliczeniu za okres, w którym podatnik otrzymał fakturę (art. 86 ust. 10b pkt 1), jeśli towar lub usługa są wykorzystywane do 
   - ?r?d?o ISAP: 86: Art. 86. 1. W  zakresie, w  jakim towary i  usługi są wykorzystywane do wykonywania czynności opodatkowanych, podatnikowi, o którym mowa w art. 15, przysługuje prawo do obniżenia kwoty podatku należnego o  kwotę podatku naliczonego, z  zast
3. `PARTIAL` ? `Ustawa o VAT | art. 86a ust. 1 | score 17.8849`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Od wydatków związanych z pojazdami samochodowymi możesz odliczyć tylko 50% podatku naliczonego (art. 86a ust. 1). Dotyczy to VAT wynikającego z faktury, podatku należnego z tytułu świadczenia usług czy dostawy towarów. P
   - ?r?d?o ISAP: 86a: Art. 86a. 1. W  przypadku wydatków związanych z  pojazdami samochodowymi kwotę podatku naliczonego, o  której mowa w  art. 86 ust.  2, stanowi 50 % kwoty podatku: 1) wynikającej z faktury otrzymanej przez podatnika; 2) należnego z tytułu: a

### VAT | freq 12 | PARTIAL
Czy od samochodu Opel combo van, który ma wpisane w dowodzie rejestracyjnym samochód ciężarowy do 3,5 t, można odliczać 100% VAT?

1. `PARTIAL` ? `Ustawa o VAT | art. 86a ust. 3 pkt 1 lit. a | score 91.7061`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Tak, jeśli Opel Combo Van spełnia warunki określone w art. 86a ust. 9 (pojazd z jednym rzędem siedzeń oddzielonym ścianą od części ładunkowej), może kwalifikować do 100% odliczenia VAT zamiast standardowych 50%. Warunkie
   - ?r?d?o ISAP: 86a: Art. 86a. 1. W  przypadku wydatków związanych z  pojazdami samochodowymi kwotę podatku naliczonego, o  której mowa w  art. 86 ust.  2, stanowi 50 % kwoty podatku: 1) wynikającej z faktury otrzymanej przez podatnika; 2) należnego z tytułu: a
2. `PARTIAL` ? `Ustawa o VAT | art. 86a ust. 9 pkt 1 | score 83.006`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Samochód z kratką (przegrodą) daje pełne odliczenie VAT gdy ma jeden rząd siedzeń oddzielony od części ładunkowej ścianą lub trwałą przegrodą, jest klasyfikowany jako wielozadaniowy/van lub ma otwartą część ładunkową. Wy
   - ?r?d?o ISAP: 86a: Art. 86a. 1. W  przypadku wydatków związanych z  pojazdami samochodowymi kwotę podatku naliczonego, o  której mowa w  art. 86 ust.  2, stanowi 50 % kwoty podatku: 1) wynikającej z faktury otrzymanej przez podatnika; 2) należnego z tytułu: a
3. `PARTIAL` ? `Ustawa o VAT | art. 86a ust. 3 pkt 1 lit. a | score 54.2799`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Tak, możesz odliczyć 100% VAT od tego pojazdu. Samochód ciężarowy (inny niż samochód osobowy) z jednym rzędem siedzeń oddzielonym od części przeznaczonej do przewozu ładunków przegrodą jest uznawany za pojazd wykorzystyw
   - ?r?d?o ISAP: 86a: Art. 86a. 1. W  przypadku wydatków związanych z  pojazdami samochodowymi kwotę podatku naliczonego, o  której mowa w  art. 86 ust.  2, stanowi 50 % kwoty podatku: 1) wynikającej z faktury otrzymanej przez podatnika; 2) należnego z tytułu: a

### VAT | freq 12 | PARTIAL
Samochód osobowy z leasingiem operacyjnymWartość powyżej 100 tys bruttoZgłoszony do VAT-26Czy leasing odliczam proporcje?

1. `PARTIAL` ? `Ustawa o VAT | art. 86a ust. 3 pkt 1 lit. a | score 49.7987`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Tak, możesz odliczyć 100% VAT od tego pojazdu. Samochód ciężarowy (inny niż samochód osobowy) z jednym rzędem siedzeń oddzielonym od części przeznaczonej do przewozu ładunków przegrodą jest uznawany za pojazd wykorzystyw
   - ?r?d?o ISAP: 86a: Art. 86a. 1. W  przypadku wydatków związanych z  pojazdami samochodowymi kwotę podatku naliczonego, o  której mowa w  art. 86 ust.  2, stanowi 50 % kwoty podatku: 1) wynikającej z faktury otrzymanej przez podatnika; 2) należnego z tytułu: a
2. `PARTIAL` ? `Ustawa o VAT | art. 113 ust. 1 | score 37.5863`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Nie, jeśli obrót rolnika w roku poprzednim wyniósł 250 tys. zł netto (powyżej limitu 240 tys. zł), to nie może on skorzystać ze zwolnienia do 240 tys. zł w bieżącym roku. Warunek zwolnienia wymaga, aby wartość sprzedaży 
   - ?r?d?o ISAP: 113: Art. 113. 1. Zwalnia się od podatku sprzedaż dokonywaną przez podatnika posiadającego siedzibę działalności gospodarczej na terytorium kraju, u  którego wartość sprzedaży, z  wyłączeniem podatku, nie przekroczyła w  poprzednim ani bieżącym 
3. `PARTIAL` ? `Ustawa o VAT | art. 90 ust. 1 | score 29.308`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Przy działalności mieszanej podatnik musi odrębnie określić kwoty VAT naliczonego związane z czynnościami opodatkowanymi. Jeśli nie można wyodrębnić tych kwot, stosuje się proporcję - można odliczyć taką część VAT nalicz
   - ?r?d?o ISAP: 90: Art. 90. 1. W stosunku do towarów i  usług, które są wykorzystywane przez podatnika do wykonywania czynności, w związku z którymi przysługuje prawo do obniżenia kwoty podatku należnego, jak i  czynności, w  związku z którymi takie prawo nie

### VAT | freq 11 | FAIL
.Jaka stawka VAT na usługi gastronomiczne z owocami morza, a jaka na usługi gastronomiczne tylko z rybami?

1. `PARTIAL` ? `Ustawa o VAT | art. 119 ust. 3a i 6 | score 19.8979`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Podatnik musi prowadzić ewidencję (art. 109 ust. 3) z wyszczególnieniem wydatków na towary i usługi nabyte dla turysty oraz posiadać dokumenty potwierdzające te kwoty. Odrębnie ewidencjonuje usługi własne i odrębnie usłu
   - ?r?d?o ISAP: 119: Art. 119. 1. Podstawą opodatkowania przy wykonywaniu usług turystyki jest kwota marży pomniejszona o kwotę należnego podatku, z zastrzeżeniem ust. 5. 2. Przez marżę, o  której mowa w  ust. 1, rozumie się różnicę między kwotą, którą ma zapła; 6: Art. 6. Przepisów ustawy nie stosuje się do: 1) transakcji zbycia przedsiębiorstwa lub zorganizowanej części przedsiębiorstwa; 2) czynności, które nie mogą być przedmiotem prawnie skutecznej umowy. 3) (uchylony) Rozdział 2 Dostawa towarów i
2. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 16 ust. 1 pkt 28 | score 17.0293`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Koszty posiłków pracowników nie stanowią kosztów uzyskania przychodów, ponieważ art. 16 ust. 1 pkt 28 ustawy zawiera katalog wydatków na usługi gastronomiczne i zakup żywności określonych jako koszty reprezentacji, które
3. `PARTIAL` ? `Ustawa o VAT | art. 28c ust. 1 | score 14.2494`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Przepisy art. 28c określają miejsce świadczenia usług, ale nie zawierają informacji o mechanizmie odwrotnego obciążenia (reverse charge) ani stawkach VAT. Aby stwierdzić, czy usługa podlega odwróceniu obowiązku zapłaty V
   - ?r?d?o ISAP: 28c: Art. 28c. 1. Miejscem świadczenia usług na rzecz podmiotów niebędących podatnikami jest miejsce, w  którym usługodawca posiada siedzibę działalności gospodarczej, z zastrzeżeniem ust. 2 i 3 oraz art. 28d, art. 28e, art. 28f ust. 1, 2 i 3, a

### VAT | freq 11 | FAIL
Odliczam 100% VAT.Leasing (kapitał) nie jest ograniczony proporcja, ponieważ samochód nie jest traktowany jako osobowy w świetle VAT/PIT?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 23b ust. 1 | score 27.3608`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Przepisy art. 23b nie określają wymaganego formatu harmonogramu spłat leasingu ani nie nakładają obowiązku podziału opłat na kapitał i odsetki. Ustawa odnosi się jedynie do całości opłat ustalonych w umowie leasingu w po
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 3 ust. 2a | score 23.3279`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Osoba fizyczna z rezydencją podatkową w Niemczech NIE podlega obowiązkowi podatkowemu w Polsce. W Polsce ma zastosowanie ograniczony obowiązek podatkowy - płaci podatek tylko od dochodów uzyskanych na terytorium Polski. 
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 21 ust. 1 pkt 17 | score 21.0753`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Diety i zwrot kosztów otrzymywane przez osoby pełniące funkcje obywatelskie (w tym sołtysów) są zwolnione od podatku dochodowego do wysokości nieprzekraczającej miesięcznie 3000 zł. Ponieważ Twoja dieta wynosi 2700 zł mi

### VAT | freq 9 | PARTIAL
Korekta in minus kosztowa: wystawiona 20.02 dot usługi z 12.02. VAT i dochodowy księguję pod datą wystawienia 20.02?

1. `PARTIAL` ? `Ustawa o VAT | art. 106j ust. 1 pkt 4 | score 76.8545`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Faktura korygująca powinna być wystawiona w związku ze zmianą podstawy opodatkowania lub zwrotem zapłaty. Артykuł 106j nie określa terminu, w jakim korekta musi być wystawiona po zmianie okoliczności. Faktura korygująca 
   - ?r?d?o ISAP: 106j: Art. 106j. 1. W przypadku gdy po wystawieniu faktury: 1) podstawa opodatkowania lub kwota podatku wskazana w fakturze uległa zmianie, 2) (uchylony)  3) dokonano zwrotu podatnikowi towarów i opakowań, 4) dokonano zwrotu nabywcy całości lub c
2. `PARTIAL` ? `Ustawa o VAT | art. 106j ust. 2 pkt 2 | score 50.4967`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Art. 106j ust. 2 pkt 2 wymaga, aby faktura korygująca zawierała numer kolejny oraz datę jej wystawienia. Data wystawienia faktury korygującej to data, kiedy faktycznie jest wystawiona, nie zaś data faktury pierwotnej czy
   - ?r?d?o ISAP: 106j: Art. 106j. 1. W przypadku gdy po wystawieniu faktury: 1) podstawa opodatkowania lub kwota podatku wskazana w fakturze uległa zmianie, 2) (uchylony)  3) dokonano zwrotu podatnikowi towarów i opakowań, 4) dokonano zwrotu nabywcy całości lub c
3. `PARTIAL` ? `Ustawa o VAT | art. 106j ust. 1 pkt 1 i 5 | score 28.5784`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Ustawa nie łączy prawa do odliczenia VAT naliczonego z powodem wystawienia faktury korygującej. Jeśli jednak faktura była wystawiona dla błędnego kontrahenta, VAT nie powinien był być odliczony wcześnie, bo zabrakłoby do
   - ?r?d?o ISAP: 106j: Art. 106j. 1. W przypadku gdy po wystawieniu faktury: 1) podstawa opodatkowania lub kwota podatku wskazana w fakturze uległa zmianie, 2) (uchylony)  3) dokonano zwrotu podatnikowi towarów i opakowań, 4) dokonano zwrotu nabywcy całości lub c; 5: Art. 5. 1. Opodatkowaniu podatkiem od towarów i  usług, zwanym dalej „podatkiem”, podlegają: 1) odpłatna dostawa towarów i odpłatne świadczenie usług na terytorium kraju; 2) eksport towarów; 3) import towarów na terytorium kraju; 4) wewnątr

### VAT | freq 8 | PARTIAL
Oznaczenia BFK DI Czy faktury sprzedażowe na kontrahenta zagranicznego oznaczamy BFK czy DI?

1. `PARTIAL` ? `Ustawa o VAT | art. 106e ust. 1 pkt 6 | score 79.773`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Przepisy art. 106e nie definiują oznaczeń BFK ani DI dla faktur wewnętrznych. Artykuł zawiera wymóg, by faktura zawierała datę dokonania lub zakończenia dostawy (pkt 6), ale nie wskazuje konkretnego kodu lub oznaczenia d
   - ?r?d?o ISAP: 106e: Art. 106e. 1. Faktura powinna zawierać: 1) datę wystawienia; 2) kolejny numer nadany w  ramach jednej lub więcej serii, który w  sposób jednoznaczny identyfikuje fakturę; 3) imiona i nazwiska lub nazwy podatnika i nabywcy towarów lub usług 
2. `PARTIAL` ? `Ustawa o VAT | art. 106e ust. 3 | score 55.4095`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Tekst ustawy o VAT nie określa, jakie oznaczenia w księdze pamiętowej (KPL) stosować dla poszczególnych rodzajów faktur VAT, w tym dla faktury dotyczącej procedury marży. Przepisy dotyczą wyłącznie wymogów treści faktury
   - ?r?d?o ISAP: 106e: Art. 106e. 1. Faktura powinna zawierać: 1) datę wystawienia; 2) kolejny numer nadany w  ramach jednej lub więcej serii, który w  sposób jednoznaczny identyfikuje fakturę; 3) imiona i nazwiska lub nazwy podatnika i nabywcy towarów lub usług 
3. `PARTIAL` ? `Ustawa o VAT | art. 106e ust. 1 | score 50.4446`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Ustawa o VAT nie definiuje skrótów takich jak 'BFK' ani nie reguluje systemu oznaczeń dla faktur zakupowych (kosztowych). Ustawowo faktury muszą zawierać elementy wymienione w art. 106e (np. datę, numer, dane stron, staw
   - ?r?d?o ISAP: 106e: Art. 106e. 1. Faktura powinna zawierać: 1) datę wystawienia; 2) kolejny numer nadany w  ramach jednej lub więcej serii, który w  sposób jednoznaczny identyfikuje fakturę; 3) imiona i nazwiska lub nazwy podatnika i nabywcy towarów lub usług 

### VAT | freq 7 | PARTIAL
Czy taką sprzedaż należy wykazać ze stawką ZW (i liczyć do limitu zwolnienia z VAT)?

1. `PARTIAL` ? `Ustawa o VAT | art. 113 ust. 2 pkt 2 | score 19.534`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Sprzedaż zwolniona od podatku na podstawie art. 43 ust. 1 nie wlicza się do limitu 240 000 zł z art. 113 ust. 1, z pewnymi wyjątkami. Nie liczy się także sprzedaż zwolniona na podstawie art. 82 ust. 3, za wyjątkiem trans
   - ?r?d?o ISAP: 113: Art. 113. 1. Zwalnia się od podatku sprzedaż dokonywaną przez podatnika posiadającego siedzibę działalności gospodarczej na terytorium kraju, u  którego wartość sprzedaży, z  wyłączeniem podatku, nie przekroczyła w  poprzednim ani bieżącym 
2. `PARTIAL` ? `Ustawa o VAT | art. 106ga ust. 2 pkt 6 | score 13.5345`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Podatnicy korzystający ze zwolnienia z VAT (art. 113a ust. 1) są zwolnieni z obowiązku wystawiania faktur ustrukturyzowanych w Krajowym Systemie e-Faktur. W takim przypadku mogą wystawiać faktury elektroniczne lub papier
   - ?r?d?o ISAP: 106g: Art. 106g. (uchylony)
3. `PARTIAL` ? `Ustawa o VAT | art. 113 ust. 12 | score 12.4778`
   - Pow?d: w?a?ciwa ustawa, ale chunk wymaga r?cznej oceny lub doprecyzowania wzgl?dem ?r?d?a
   - Chunk: Nie. Ustawa przewiduje mechanizm zabezpieczający przed omijaniem limitu poprzez art. 113 ust. 12 - jeśli między tobą a kontrahentem istnieje związek (np. powiązanie kapitałowe), który wpływa na zaniżenie wartości sprzeda
   - ?r?d?o ISAP: 113: Art. 113. 1. Zwalnia się od podatku sprzedaż dokonywaną przez podatnika posiadającego siedzibę działalności gospodarczej na terytorium kraju, u  którego wartość sprzedaży, z  wyłączeniem podatku, nie przekroczyła w  poprzednim ani bieżącym 

### PIT | freq 10 | FAIL
Jeśli mam kogoś na zleceniu, ale w 2025 nie przepracował ani 1h i nie zarobił ani 1zł to czy muszę wystawiać zerowy PIT4R?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 14c ust. 1 pkt 1 | score 23.5462`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Przy wyborze metody kasowej od 2026 roku musisz sprawdzić przychody z roku bezpośrednio poprzedzającego - czyli z 2025 roku. Limit wynosi 1 000 000 zł i stosuje się niezależnie od formy opodatkowania, którą stosowałeś w 
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 14 ust. 1e | score 22.9759`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Jeśli strony umowy ustalą, że usługa jest rozliczana w okresach rozliczeniowych, przychód powstaje w ostatnim dniu danego okresu rozliczeniowego określonego w umowie lub wystawionej fakturze (art. 14 ust. 1e). Przepis te
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 22 ust. 4 | score 21.2209`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Koszty poniesione w 2025 roku są potrącalne w roku, w którym zostały poniesione, czyli 2025 roku. Przychód z odszkodowania otrzymany w 2026 roku będzie przychodem roku 2026. Jeśli są to koszty bezpośrednio związane z tym

### PIT | freq 6 | FAIL
Bo sie zgubiłam. PIT-37 Ulga rehabilitacyjna na niepełnosprawnego syna i faktury za leki powyżej 100 zl?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 22 ust. 2 pkt 1 | score 36.5455`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Przychód z pracy wykazujesz w wysokości kwot wykazanych przez pracodawcę na PIT-11 (brutto, przed potrąceniami). Na PIT-37 wykazujesz przychód z tytułu stosunku pracy, następnie odliczasz od niego koszty uzyskania przych
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 21 ust. 1 pkt 17 | score 34.8796`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Diety i zwrot kosztów otrzymywane przez osoby pełniące funkcje obywatelskie (w tym sołtysów) są zwolnione od podatku dochodowego do wysokości nieprzekraczającej miesięcznie 3000 zł. Ponieważ Twoja dieta wynosi 2700 zł mi
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 27 ust. 1 | score 32.8465`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Od dochodu do 120 000 zł podatek wynosi 12% minus kwota zmniejszająca podatek 3600 zł. Od dochodu powyżej 120 000 zł podatek wynosi 10 800 zł plus 32% nadwyżki ponad 120 000 zł. To skala progresywna z dwoma przedziałami.

### PIT | freq 6 | FAIL
Czy pit11 można wysłać jeszcze 2 lutego z uwagi na weekend?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 21.8888`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Zeznanie podatkowe trzeba złożyć w terminie od 15 lutego do 30 kwietnia roku następującego po roku podatkowym. Zeznania złożone przed 15 lutego uznaje się za złożone w dniu 15 lutego. To oznacza, że dla roku 2025 termin 
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 21.0835`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Zeznanie o wysokości osiągniętego dochodu (PIT-36) należy złożyć w terminie od 15 lutego do 30 kwietnia roku następującego po roku podatkowym. Zeznania złożone przed 15 lutego traktuje się jako złożone w dniu 15 lutego.
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 20.9358`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Zeznanie roczne o dochodach należy złożyć w terminie od 15 lutego do 30 kwietnia roku następującego po roku podatkowym. Zeznania złożone przed 15 lutego uznaje się za złożone w dniu 15 lutego roku następującego po roku p

### PIT | freq 6 | FAIL
Mam taki mix:Żona PIT36 (dg + UoP) + PIT/M (połowa nagrody)Mąż PIT36L (dg) oraz PIT36 (zerowy) + PIT/M (połowa nagrody)Czy w przypadku męża będzie właśnie tak?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 20 ust. 1 | score 59.7744`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Nagrody stanowią przychody z innych źródeł (art. 20 ust. 1), nie z działalności gospodarczej. Rozliczane są w PIT-11 (zeznaniu rocznym) razem z dochodami z pozostałych źródeł, nie w ryczałcie PIT-28. Karta podarunkowa o 
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 12 ust. 1 | score 52.1744`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Tak, premie, nagrody i różnego rodzaju dodatki stanowią przychód ze stosunku pracy. Są one wymieniane w art. 12 ust. 1 jako część przychodów pracownika, niezależnie od tego, czy ich wysokość została z góry ustalona.
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 12 ust. 1 | score 39.3849`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Przychodem ze stosunku pracy są wszelkiego rodzaju wypłaty pieniężne oraz wartość świadczeń w naturze bądź ich ekwiwalenty, niezależnie od źródła finansowania. Obejmuje to: wynagrodzenia zasadnicze, dodatki, nagrody, ekw

### PIT | freq 6 | FAIL
Ulga na dziecko Córka ma 22 lata i studiuje w Danii. Czy w takim przypadku mogę zastosować ulgę na dziecko?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 21 ust. 1 pkt 8 | score 20.1357`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Renta rodzinna pobierana przez dziecko po zmarłym ojcu jest wolna od podatku dochodowego na podstawie art. 21 ust. 1 pkt 8, dlatego nie stanowi dochodu podlegającego opodatkowaniu. Ulga na dziecko przysługuje rodzicom ni
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 27f ust. 1 | score 19.2968`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Matka samotnie wychowująca może skorzystać z ulgi na dziecko za każdy miesiąc, w którym dziecko pozostawało małoletnie i spełniały się warunki z art. 27f ust. 1. Jednak od lipca dziecko może być już pełnoletnie - jeśli t
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 27f ust. 2 pkt 1 lit. b | score 17.3327`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Tak, samotna matka może się rozliczać z ulgą na dziecko, jeśli spełnia warunki określone w art. 27f. Jeśli nie pozostaje w związku małżeńskim (w tym przez część roku), limit dochodów wynosi 56 000 zł rocznie. Jeśli samot

### PIT | freq 5 | FAIL
Czy jeśli działalność w 2025 była na ryczałcie od 03-12.2025 to czy w 2026 można użyć jako podstawy - przychodu z roku poprzedniego do ustalenia podstawy zdrowotnej?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 22 ust. 4 | score 27.1984`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Koszty poniesione w 2025 roku są potrącalne w roku, w którym zostały poniesione, czyli 2025 roku. Przychód z odszkodowania otrzymany w 2026 roku będzie przychodem roku 2026. Jeśli są to koszty bezpośrednio związane z tym
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 14c ust. 1 pkt 1 | score 24.6839`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Przy wyborze metody kasowej od 2026 roku musisz sprawdzić przychody z roku bezpośrednio poprzedzającego - czyli z 2025 roku. Limit wynosi 1 000 000 zł i stosuje się niezależnie od formy opodatkowania, którą stosowałeś w 
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 22.7094`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Dochody osiągnięte w roku podatkowym 2025 wykazuje się w zeznaniu PIT-36 (lub PIT-37) składanym w terminie od 15 lutego do 30 kwietnia 2026 roku (art. 45 ust. 1). Zeznanie za rok 2025 dotyczy dochodów uzyskanych w tym ro

### PIT | freq 5 | FAIL
Pit-37 Zamotałam się osoba która otrzymuje PIT40A z KRUS i PIT11A otrzymuje z Zusu powinna taką osoba rozliczyć się PIT 37?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 26g | score 61.7401`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Przepisy ustawy o podatku dochodowym nie zawierają szczegółowych instrukcji dotyczących konkretnych pól w formularzu PIT-37. Odliczenie kosztów kwalifikowanych dokonujesz w zeznaniu za rok podatkowy, w którym je poniosłe
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 59.7203`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Artykuł 45 nie zawiera konkretnych informacji o formularzu PIT-36. Przepis mówi ogólnie o zeznaniu rocznym, ale dokładną definicję i zastosowanie poszczególnych formularzy (PIT-36, PIT-36L, PIT-37) określają inne przepis
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 21 ust. 1 pkt 17 | score 55.2914`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Diety i zwrot kosztów otrzymywane przez osoby pełniące funkcje obywatelskie (w tym sołtysów) są zwolnione od podatku dochodowego do wysokości nieprzekraczającej miesięcznie 3000 zł. Ponieważ Twoja dieta wynosi 2700 zł mi

### PIT | freq 4 | FAIL
Chciałabym zapytać czy ktoś może miał taką sytuację, że od 2016 roku zawieszona jest działalność, a podatnik rozliczony na formularzu PIT 37 zamiast PIT 36.Teraz wydaje mi się, że trzeba złożyć korekty wstecz od 2020 roku?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 79.2684`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Artykuł 45 nie zawiera konkretnych informacji o formularzu PIT-36. Przepis mówi ogólnie o zeznaniu rocznym, ale dokładną definicję i zastosowanie poszczególnych formularzy (PIT-36, PIT-36L, PIT-37) określają inne przepis
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 76.327`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Dochody osiągnięte w roku podatkowym 2025 wykazuje się w zeznaniu PIT-36 (lub PIT-37) składanym w terminie od 15 lutego do 30 kwietnia 2026 roku (art. 45 ust. 1). Zeznanie za rok 2025 dotyczy dochodów uzyskanych w tym ro
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 26 ust. 1 pkt 9 | score 74.0325`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Tak, darowizny odliczasz w zeznaniu podatkowym, którym dla niektórych podatników jest PIT-37 (zamiast PIT-36). W zeznaniu wykazujesz kwotę przekazanej darowizny, kwotę dokonanego odliczenia i dane obdarowanego. Odliczeni

### PIT | freq 4 | FAIL
Mam tak w Volkswagen Leasing, samochód osobowy elektryczny, proporcja ustalona ale na fakturach i harmonogramie brak podziału. Co z tym zrobić?

1. `FAIL` ? `Ustawa o VAT | art. 145n ust. 1 pkt 1 | score 23.2149`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Tak, w okresie od 1 lutego do 31 grudnia 2026 r. podatnicy obowiązani do wystawiania faktur ustrukturyzowanych mogą wystawiać faktury elektroniczne lub papierowe przy zastosowaniu kas rejestrujących. Wartość sprzedaży z 
   - ?r?d?o ISAP: 145n: Art. 145n. 1. W okresie od dnia 1  lutego 2026 r. do dnia 31  grudnia 2026 r. podatnicy obowiązani do wystawiania faktur ustrukturyzowanych mogą wystawiać: 1) faktury elektroniczne lub faktury w postaci papierowej przy zastosowaniu kas reje
2. `FAIL` ? `Ustawa o VAT | art. 106gb | score 20.5333`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Artykuł 106gb nie zawiera żadnych informacji o fakturach zaliczkowych. Odpowiedź na to pytanie wymaga weryfikacji w innych przepisach ustawy o VAT.
   - ?r?d?o ISAP: 106g: Art. 106g. (uchylony)
3. `FAIL` ? `Ustawa o VAT | art. 106j ust. 1 pkt 5 | score 18.3967`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Tak, jeśli stwierdzisz pomyłkę w dowolnej pozycji faktury (w tym w nazwie towaru), musisz wystawić fakturę korygującą (art. 106j ust. 1 pkt 5). Dotyczy to również literówek. W korrekcie powinna być wykazana prawidłowa tr
   - ?r?d?o ISAP: 106j: Art. 106j. 1. W przypadku gdy po wystawieniu faktury: 1) podstawa opodatkowania lub kwota podatku wskazana w fakturze uległa zmianie, 2) (uchylony)  3) dokonano zwrotu podatnikowi towarów i opakowań, 4) dokonano zwrotu nabywcy całości lub c

### PIT | freq 3 | FAIL
(do tej pory robiłem taką w druczkach a teraz podobno trzeba elektronicznie)?

1. `FAIL` ? `Ustawa o VAT | art. 96 ust. 1, 3 | score 12.9946`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Zarówno rejestracja obowiązkowa jak i dobrowolna muszą być dokonane PRZED dniem wykonania pierwszej czynności opodatkowanej. Brak różnicy w terminach - w obu przypadkach zgłoszenie trzeba złożyć przed rozpoczęciem działa
   - ?r?d?o ISAP: 96: Art. 96. 1. Podmioty, o  których mowa w  art. 15 i art. 15a, są obowiązane przed dniem wykonania pierwszej czynności okreś lonej w  art. 5 złożyć naczelnikowi urzędu skarbowego zgłoszenie rejestracyjne, z zastrzeżeniem ust. 3. 1a. Dostawca ; 3: Art. 3. 1. (uchylony) 2. (uchylony) 3. W przypadku: 1) (uchylony)  2) podatników: a) nieposiadających siedziby działalności gospodarczej lub stałego miejsca prowadzenia działalności gospodarczej na terytorium kraju, b) o których mowa w art.
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 4 | score 8.4129`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Tak, podatek trzeba wpłacić przed upływem terminu do złożenia zeznania (do 30 kwietnia). Wpłacić trzeba: różnicę między podatkiem należnym z zeznania a sumą zapłaconych zaliczek, lub pełny podatek należny z zeznania o do
3. `FAIL` ? `Ustawa o VAT | art. 106i ust. 2 | score 6.6242`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Nie, taka faktura nie jest BFK. Według art. 106i ust. 2 Ustawy o VAT, jeśli otrzymasz całość lub część zapłaty PRZED dostawą, faktura powinna być wystawiona nie później niż 15. dnia miesiąca następującego po miesiącu, w 
   - ?r?d?o ISAP: 106: Art. 106. (uchylony)

### CIT | freq 29 | FAIL
Czy ktoś posiada certyfikat rezydencji podatkowej za 2025 od: *Weglot SAS *Stripe *Squarespace Ireland *Serif Europe LTD?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 3 ust. 1a | score 17.6308`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Ustawa o PIT nie zawiera definicji ani regulacji dotyczącej certyfikatu rezydencji podatkowej. Przepisy art. 3 określają status rezydenta podatkowego w oparciu o miejsce zamieszkania (art. 3 ust. 1a) – czyli centrum inte
2. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 21 ust. 3 pkt 2 | score 16.0162`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Ustawa o podatku dochodowym od osób prawnych nie zawiera terminu 'certyfikat rezydencji podatkowej'. Zwolnienie od podatku od odsetek, praw autorskich i należności licencyjnych (art. 21 ust. 3) wymaga spełnienia warunków
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 30j ust. 1 pkt 1 | score 11.5525`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Aby skorzystać z ryczałtu od przychodów zagranicznych dla osób przenoszących miejsce zamieszkania na terytorium Polski, musisz do końca stycznia roku następującego po roku, w którym się przeprowadziłeś, złożyć w urzędzie

### CIT | freq 19 | FAIL
Czy nadal trzeba pisać pisma o stwierdzenie nadpłaty i zwrot jesli wynika z cit8? Czy sami zwrócą?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 28b ust. 6 | score 16.5808`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Organ podatkowy zwraca podatek bez zbędnej zwłoki, nie później jednak niż w terminie 6 miesięcy od dnia wpływu wniosku o zwrot podatku. Termin ten biegnie na nowo od dnia wpływu zmienionego wniosku. W przypadku bezwątpli
2. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 8 ust. 6 | score 14.6401`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Zgodnie z art. 8 ust. 6, jeśli z odrębnych przepisów wynika obowiązek zamknięcia ksiąg przed upływem roku podatkowego, następny rok podatkowy biegnie od dnia otwarcia ksiąg rachunkowych do końca przyjętego roku podatkowe
3. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 7aa ust. 2 pkt 3 | score 13.4071`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Art. 7aa dotyczy tzw. dochodu z przekształcenia przy przejściu na ryczałt. Jeśli spółka przechodzi z normalnego opodatkowania na ryczałt, musi wykazać dochód z przekształcenia będący różnicą między wartością księgową (fi

### CIT | freq 10 | FAIL
Ma może ktoś certyfikat rezydencji za rok 2025 od firmy Timocom Platz oraz Cookie Script?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 3 ust. 1a | score 14.3647`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Ustawa o PIT nie zawiera definicji ani regulacji dotyczącej certyfikatu rezydencji podatkowej. Przepisy art. 3 określają status rezydenta podatkowego w oparciu o miejsce zamieszkania (art. 3 ust. 1a) – czyli centrum inte
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 13.6425`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Artykuł 45 wymaga złożenia zeznania za dany rok podatkowy w terminie od 15 lutego do 30 kwietnia roku następującego. Przychody za 2024 rok powinny być wykazane w zeznaniu za 2024 (złożonym do 30 kwietnia 2025). Brak złoż
3. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 21 ust. 3 pkt 2 | score 13.0897`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Ustawa o podatku dochodowym od osób prawnych nie zawiera terminu 'certyfikat rezydencji podatkowej'. Zwolnienie od podatku od odsetek, praw autorskich i należności licencyjnych (art. 21 ust. 3) wymaga spełnienia warunków

### CIT | freq 7 | FAIL
Estoński CIT czy zakupiony obiad dla pracowników co jakiś czas to wydatek niezwiązany z działalnością gospodarczą czy kolacja służbowa?

1. `FAIL` ? `Ustawa o podatku dochodowym od osÃ³b prawnych | art. 28j ust. 1 | score 46.2104`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Estoński CIT może wybrać podatnik CIT mający siedzibę lub zarząd w Polsce, jeżeli spełnia warunki z art. 28j ust. 1, w szczególności dotyczące struktury przychodów, poziomu zatrudnienia lub ponoszenia określonych wydatkó
2. `FAIL` ? `Ustawa o podatku dochodowym od osÃ³b prawnych | art. 28j ust. 1 oraz art. 28k ust. 1 | score 39.0693`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Estoński CIT, czyli ryczałt od dochodów spółek, może wybrać podatnik CIT mający siedzibę lub zarząd w Polsce, jeżeli spełnia warunki z art. 28j ust. 1, w tym dotyczące struktury przychodów, zatrudnienia, formy prowadzeni
3. `FAIL` ? `Ustawa o podatku dochodowym od osÃ³b prawnych | art. 28k ust. 1 | score 37.3666`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Z estońskiego CIT wyłączeni są podatnicy wskazani w art. 28k ust. 1, w tym m.in. przedsiębiorstwa finansowe, instytucje pożyczkowe, podatnicy korzystający z niektórych zwolnień strefowych, podmioty w upadłości lub likwid

### CIT | freq 7 | FAIL
Wynajem auta za granica. Czy w tej sytuacji należy pobrać podatek u źródła (WHT)?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 21 ust. 1 | score 68.4867`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Wynajem samochodu zagranicą nie jest wymieniony w art. 21 ust. 1 jako przychód podlegający obowiązkowi pobrania podatku u źródła. Art. 21 zawiera katalog przychodów polegających podatek u źródła (odsetki, prawa autorskie
2. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 12 ust. 2 | score 24.7383`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Przychody w walutach obcych ze sprzedaży stoików za granicą należy przeliczyć na złote według kursu średniego ogłaszanego przez Narodowy Bank Polski z ostatniego dnia roboczego poprzedzającego dzień uzyskania przychodu. 
3. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 15 ust. 1 | score 23.6869`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Aby zaliczyć płatność do kosztów uzyskania przychodów, musi być ona poniesiona w celu osiągnięcia przychodów ze źródła przychodów lub zachowania/zabezpieczenia tego źródła. Koszty bezpośrednio związane z przychodami zali

### CIT | freq 6 | FAIL
Doby wieczór!. Składacie państwo deklarację IFT2R? Czy składa się do miesięcznej subskrypcji (Google, Adobe itp)?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 27 ust. 1 | score 13.1485`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Zeznanie CIT za rok 2025 należy złożyć do końca trzeciego miesiąca roku następnego, czyli do 31 marca 2026 roku. W tym samym terminie należy wpłacić podatek należny albo różnicę między podatkiem należnym a sumą zapłacony
2. `FAIL` ? `Ustawa o VAT | art. 26a ust. 1 i 2 | score 11.8991`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Miejscem importu towarów z Chin jest terytorium Polski — to miejsce, gdzie towary znajdują się w momencie ich wprowadzenia na terytorium Unii Europejskiej. Jeśli towary podlegają procedurze celnej (uszlachetnianie, skład
   - ?r?d?o ISAP: 26a: Art. 26a. 1. Miejscem importu towarów jest terytorium państwa członkowskiego, na którym towary znajdują się w momencie ich wprowadzenia na terytorium Unii Europejskiej.  2. W przypadku gdy towary zostaną objęte z momentem ich wprowadzenia n; 2: Art. 2. Ilekroć w dalszych przepisach jest mowa o: 1) terytorium kraju – rozumie się przez to terytorium Rzeczypospolitej Polskiej, z zastrzeżeniem art. 2a; 2) państwie członkowskim – rozumie się przez to państwo członkowskie Unii Europejsk
3. `FAIL` ? `Ustawa o VAT | art. 99 ust. 4 | score 11.7837`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Aby przejść z rozliczeń kwartalnych na miesięczne, należy po upływie 4 kwartałów rozliczeń kwartalnych zawiadomić na piśmie naczelnika urzędu skarbowego. Zawiadomienie składa się w terminie do dnia złożenia pierwszej dek
   - ?r?d?o ISAP: 99: Art. 99. 1. Podatnicy, o  których mowa w  art. 15, są obowiązani składać w urzędzie skarbowym deklaracje podatkowe za okresy miesięczne w  terminie do 25. dnia miesiąca następującego po każdym kolejnym miesiącu, z  zastrzeżeniem ust. 2–10, 

### CIT | freq 4 | FAIL
Czy ktoś z Państwa posiada certyfikat rezydencji podatkowej firmy Apple Distribution International Ltd. i mógłby się podzielić?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 3 ust. 1a | score 17.6308`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Ustawa o PIT nie zawiera definicji ani regulacji dotyczącej certyfikatu rezydencji podatkowej. Przepisy art. 3 określają status rezydenta podatkowego w oparciu o miejsce zamieszkania (art. 3 ust. 1a) – czyli centrum inte
2. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 21 ust. 3 pkt 2 | score 16.0162`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Ustawa o podatku dochodowym od osób prawnych nie zawiera terminu 'certyfikat rezydencji podatkowej'. Zwolnienie od podatku od odsetek, praw autorskich i należności licencyjnych (art. 21 ust. 3) wymaga spełnienia warunków
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 30j ust. 1 pkt 1 | score 11.5525`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Aby skorzystać z ryczałtu od przychodów zagranicznych dla osób przenoszących miejsce zamieszkania na terytorium Polski, musisz do końca stycznia roku następującego po roku, w którym się przeprowadziłeś, złożyć w urzędzie

### CIT | freq 3 | FAIL
Czy ma ktoś certyfikaty rezydencji za rok 2025 dla: Canva, Klaviyo,BunnyWay,Manychat, Zoom??

1. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 13.6425`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Artykuł 45 wymaga złożenia zeznania za dany rok podatkowy w terminie od 15 lutego do 30 kwietnia roku następującego. Przychody za 2024 rok powinny być wykazane w zeznaniu za 2024 (złożonym do 30 kwietnia 2025). Brak złoż
2. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 6 ust. 2 pkt 2 | score 10.0833`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Tak, małżeństwo zawarte w lutym 2025 roku może się rozliczyć wspólnie za rok 2025. Prawo do wspólnego rozliczenia obejmuje także małżonków, którzy zawarli związek w trakcie roku podatkowego — wówczas rozliczenie dotyczy 
3. `FAIL` ? `Ustawa o podatku dochodowym od osób fizycznych | art. 45 ust. 1 | score 10.0833`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Dochody osiągnięte w roku podatkowym 2025 wykazuje się w zeznaniu PIT-36 (lub PIT-37) składanym w terminie od 15 lutego do 30 kwietnia 2026 roku (art. 45 ust. 1). Zeznanie za rok 2025 dotyczy dochodów uzyskanych w tym ro

### CIT | freq 3 | FAIL
Czy powinnam złożyć wniosek do US już teraz czy po wysłaniu CIT-8?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 27 ust. 1 | score 22.5124`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Zeznanie CIT za rok 2025 należy złożyć do końca trzeciego miesiąca roku następnego, czyli do 31 marca 2026 roku. W tym samym terminie należy wpłacić podatek należny albo różnicę między podatkiem należnym a sumą zapłacony
2. `FAIL` ? `Ustawa o podatku dochodowym od osÃ³b prawnych | art. 28j ust. 1 | score 21.4407`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Estoński CIT może wybrać podatnik CIT mający siedzibę lub zarząd w Polsce, jeżeli spełnia warunki z art. 28j ust. 1, w szczególności dotyczące struktury przychodów, poziomu zatrudnienia lub ponoszenia określonych wydatkó
3. `FAIL` ? `Ustawa o podatku dochodowym od osÃ³b prawnych | art. 28k ust. 1 | score 19.8584`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Z estońskiego CIT wyłączeni są podatnicy wskazani w art. 28k ust. 1, w tym m.in. przedsiębiorstwa finansowe, instytucje pożyczkowe, podatnicy korzystający z niektórych zwolnień strefowych, podmioty w upadłości lub likwid

### CIT | freq 3 | FAIL
Czy składacie IFT-2R za dostęp do dysku w chmurze i usługi reklamowe z APPLE?Czy składacie IFT-2R za dostęp do dysku w chmurze i usługi reklamowe z APPLE?

1. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 21 ust. 1 pkt 2a | score 81.1278`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Tekst artykułu 21 ustawy o podatku dochodowym od osób prawnych definiuje opodatkowanie przychodów z usług reklamowych na poziomie 20%, jednak nie zawiera szczegółowych wskazówek dotyczących formularza IFT-2R ani konkretn
2. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 3, art. 4 | score 79.2225`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Pytanie dotyczy procedur sprawozdawczych (IFT-2R), które nie są regulowane w Ustawie o podatku dochodowym od osób prawnych. Artykuły 3 i 4 tej ustawy dotyczą jedynie zasad określenia obowiązku podatkowego i zakresu teryt
3. `FAIL` ? `Ustawa o podatku dochodowym od osób prawnych | art. 12 ust. 3 i 3a | score 17.3513`
   - Pow?d: z?a ustawa albo brak wiarygodnego artyku?u ?r?d?owego
   - Chunk: Przychód ze sprzedaży stoiska targowego za granicą (czy zawiera dostawę, montaż czy usługę) podlega zasadom art. 12. Przychód powstaje w dniu wydania rzeczy/wykonania usługi, nie później niż dzień wystawienia faktury lub

