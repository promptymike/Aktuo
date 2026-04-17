# FB corpus ingest report

Generated at: 2026-04-17T14:14:16+00:00

## 1. Executive summary

Trzy scrape'y FB (2 grupy) zsumowane: **40537** surowych postów. Po deduplikacji na SHA-256 pierwszych 200 znaków znormalizowanego tekstu i po filtrach jakości (question pattern, job ads, community-only markers) zostaje **24954** postów unikalnych.

Przy heurystyce ~100-150 postów na jeden klaster tematyczny, z tego korpusu realistycznie wyjdzie **~166-249** klastrów (Zadanie 2).

## 2. Volume table

| Source file | Group | Raw | After dedupe | After quality | Survival |
|---|---|---|---|---|---|
| posts_15k_ksiegowosc_moja_pasja.json | ksiegowosc_moja_pasja | 15229 | 14498 | 12183 | 80.0% |
| posts_output.json | grupa_2_507801603233194 | 14608 | 13977 | 12449 | 85.2% |
| posts_output_backup.json | ksiegowosc_moja_pasja | 10700 | 383 | 322 | 3.0% |

Cross-file duplicates removed (resolved by newest scraped_at): **10026**. Duplicates collapsed within a single file: **1629**.

## 3. Quality breakdown

### Rejected

| Reason | Count |
|---|---:|
| too_short | 15 |
| no_question_pattern | 3807 |
| job_ad | 82 |
| community_only | 0 |

### Flagged (kept)

| Flag | Count |
|---|---:|
| too_long | 0 |
| no_comments | 7422 |
| many_links | 0 |

### Top 20 keywords in final corpus

| Rank | Token | Frequency |
|---:|---|---:|
| 1 | pracy | 5125 |
| 2 | więcej | 4565 |
| 3 | pracownik | 4552 |
| 4 | dzień | 3771 |
| 5 | vat | 3654 |
| 6 | zus | 3300 |
| 7 | witam | 3157 |
| 8 | wyświetl | 3138 |
| 9 | ktoś | 3134 |
| 10 | proszę | 3127 |
| 11 | dobry | 3034 |
| 12 | roku | 2886 |
| 13 | dni | 2850 |
| 14 | jeśli | 2582 |
| 15 | pytanie | 2478 |
| 16 | ksef | 2328 |
| 17 | będzie | 2278 |
| 18 | pomoc | 2211 |
| 19 | faktury | 1967 |
| 20 | pit | 1898 |

## 4. Random sample (seed=42, n=10)

- **e8389eda73bb** · grupa_2_507801603233194 · comments: 0
  > Gdzie najlepiej zrobić kurs kadry i płace- Łódź. Chodzi mi o to aby naprawdę się nauczyć niż tylko odbębnić.
- **9630cb2a1d08** · ksiegowosc_moja_pasja · comments: 1
  > Witam, czy mogę przejść na ryczałt jeżeli będę wykonywał te same czynności co na UoP ale dla zupełnie innego podmiotu?
- **d3ae0749fd3f** · ksiegowosc_moja_pasja · comments: 2
  > Gdzie na nowym PUE ZUS znajdują się komunikaty np. O nieopłaconych składkach.Na maila przychodzi informacja że na pue zus (ezus) jest dostarczona informacja. Wchodzę we wszystkie przegrody wiadomości po komunikaty i nic nie widać??????Co robię źle?
- **68051a5f4554** · grupa_2_507801603233194 · comments: 1
  > Witam umowa o pracę na czas nieokreślony Data zatrudnienia maj 2020r w październiku chcę złożyć rozwiązanie umowy z zachowaniem okresu wypowiedzenia. Okres rozwiązania 3 m-ce czy może być krótszy?
- **208e753d3e1c** · ksiegowosc_moja_pasja · comments: 0
  > analizując ten artykuł https://www.interpretacje.pl/.../9492569,stawka-ryczaltu...   jak byście potraktowali demontaż urządzenia klimatyzacji ? również jako roboty budowlane i tym samym 5,5% ryczałt ? Może jest tutaj ktoś kto rozlicza również taką branże na ryczałcie.
- **da6e023ace20** · ksiegowosc_moja_pasja · comments: 0
  > Witam, mam pytanie mąż zawiesza jednoosobową działalność czy może złożyć wniosek do US o uwolnienie środków vat? Drugie pytanie co np z kontrolą z US jak mąż będzie legalnie procował w innym kraju UE?
- **e55079b795ac** · ksiegowosc_moja_pasja · comments: 1
  > Czy można rozliczyć nadpłatę klienta z kolejną fv czy trzeba zrobić kompensatę?
- **9a42e4e0bd6e** · ksiegowosc_moja_pasja · comments: 1
  > Faktury na osoby fizyczne krajowe i zagraniczne dot. sprzedaży towaru na Allegro - sprzedaż wysyłkowa bez kasy fiskalnej - czy od 2026 roku muszę każdą fakturę księgować w KPiR i VAT?  Nie są to FP, tylko faktury imienne na kazdą sprzedaż zamiast paragonów.
- **4b904142c87d** · grupa_2_507801603233194 · comments: 1
  > Ile urlopu tacierzynskiego i rodzicielskiego moze wykorzystać ojciec dziecka jesli matka nie pracujeIle urlopu tacierzynskiego i rodzicielskiego moze wykorzystać ojciec dziecka jesli matka nie pracuje
- **03bbc7dd5e41** · ksiegowosc_moja_pasja · comments: 0
  > Witam, jak prawidłowo liczy się opłatę prolongacyjną od odroczenia podatku ? Od dnia następnego od wydania decyzji czy od pierwotnej daty płatności podatku?

## 5. Cross-file dedupe verification

- Posty z backupu (2026-04-06, ta sama grupa 1), które miały duplikat w nowszym scrape grupy 1: **9972 / 10355**. Oczekiwanie: większość. Starszy snapshot jest nadzbiorem domeny czasowej nowszego.
- Posty z grupy 1 (nowszy scrape), które miały duplikat w grupie 2 (hash match): **54 / 14552**. Oczekiwanie: 0 albo bardzo mało — różne grupy, hash nie chwyta parafraz.

## 6. Top 20 most engaging (by comments_count)

| Rank | id | group | comments | text (first 200 chars) |
|---:|---|---|---:|---|
| 1 | a16a33a07ddd | ksiegowosc_moja_pasja | 10 | I jesteśmy z niedużej miejscowości jak by ktoś myślał że to Warszawa. … Wyświetl więcej |
| 2 | b698f050709c | ksiegowosc_moja_pasja | 9 | Najważniejsze co masz w umowie, jeśli tylko pośredniczysz to nie jest to Twoim przychodem i brak podstaw do re fakturowania, a jeśli Ty opłacasz to rektura |
| 3 | 841b955f7757 | ksiegowosc_moja_pasja | 8 | A czym tu się załamywać ludzie Nie wiem skąd kwota kup 2000 bo nawet jak zastosowane podwyższone koszty to 300x 6. Pani robiąc pit roczny musi zastosować kup zgodny z prawdą to znaczy przez 11 mc 250… |
| 4 | 7208fbf3e42b | grupa_2_507801603233194 | 8 | Tak jak pisali poprzednicy, pracownik składa wniosek o UB na czas służby, podstawa jego udzielania to art. 305 ustawy o obronie Ojczyzny. Jeśli chodzi służyć w wolne dni, np. weekend to oczywiście nie… |
| 5 | d168fc3b9726 | ksiegowosc_moja_pasja | 8 | MZ+ wybierasz na cały rok. Rozumiem, że w ciagu 7 dni od końca okresu na kodzie 0570 dokonałaś rejestracji na kod 0590? Jeśli tak, to musisz w styczniu dokonać weryfikacji czy masz prawo na kolejny ro… |
| 6 | 145c5140f2e2 | grupa_2_507801603233194 | 8 | Mam podobny problem, nauczyciel zatrudniony 01.09.2024-29.04.2025. W 2025 nie ma wymaganej il dni. Moim zdaniem się nie należy ale proszę o potwierdzenie jeżeli ktoś się orientuje |
| 7 | 86a0281d3083 | ksiegowosc_moja_pasja | 7 | Przez całe lata pracowałam w biurach rachunkowych i tak jak Ty zapieprzałam za śmieszne pieniądze, od 8 lat pracuje w dużej firmie, łącznie z główną księgową jest nas w dziale 13 osób, każdy ma swoją… |
| 8 | 0ffeff8a59a3 | ksiegowosc_moja_pasja | 7 | Jeżeli rozliczasz się z małżonkiem który nie ma dochodów twój dochód dzieli się na dwa z tego co widać po podzieleniu połowa dochodu jest niższa niż kwota wolna od podatku w związku z tym cały podatek… |
| 9 | 0d7c598fe95f | grupa_2_507801603233194 | 7 | Zgłosić do bhpowca aby sporządził protokół. Jak zdarzenie będzie uznane za wypadek, wtedy chorobowe dla pracownika 100% płatne. W protokole będzie napisane jakie kroki ma zastosować pracodawca. Składk… |
| 10 | beebf620a81a | ksiegowosc_moja_pasja | 7 | A nie odwrotnie? Jak kwota vat w pln to robisz przelew mpp na sam vat i kwota przelewu i kwota vat to tyle samo. A resztę w euro można i na konto walutowe i z walutowego. |
| 11 | dbd79b2a110f | ksiegowosc_moja_pasja | 6 | Po Nowym Roku pisałam do ZUS w sprawie podlegania pod mały ZUS Plus ponieważ akurat z końcem 2025 kończył się okres preferencyjnych składek. Otrzymałam odpowiedź że jeżeli spełniam wymogi mogę nadal k… |
| 12 | 95058af271e3 | ksiegowosc_moja_pasja | 6 | Pełne księgi , faktura wystawiona np 7 maj data sprzedaży 30  kwiecień , przybijam że wpłynęła 10 maja VAT maj a koszt ? Kwiecień ? Maj? Zawsze robiliśmy po dacie wpływu wg polityki rachunkowości . Cz… |
| 13 | 1d45464bbb98 | ksiegowosc_moja_pasja | 6 | #księgowanie kosztów pośrednich na przełomie roku.Podzielcie się proszę ze mną informacją,  do którego miesiąca zaliczacie w Sp. z o.o. w koszty podatkowe:1. wykonane usługi w grudniu, na które faktur… |
| 14 | 380e70f39edc | ksiegowosc_moja_pasja | 6 | Jak ksiegujecie VAT naliczony i należy od importu usług? Bo właśnie jestem w nowej firmie i nie pasuje mi, jak to jest księgowane... Księgują to poprzez funkcję naliczenia VATu naliczonego i należnego… |
| 15 | e29231b8abce | grupa_2_507801603233194 | 6 | Pit 2 sekcja C wypełnił? jeżeli tak to z perspektywy pracodawcy rozliczenie jest prawidłowe. Z perspektywy podatnika jeżeli nie wycofał ulgi w Zusie od emerytury to oświadczył nieprawdę. Konsekwencja… |
| 16 | 7554d7eab221 | ksiegowosc_moja_pasja | 6 | Rzetelna odpowiedź wymagałaby pół godziny pisania komentarza, plus trochę pytań dodatkowych. Temat jest gorący i jest na topie jeśli chodzi o kontrole, więc jak chcesz podejść do niego porządnie to id… |
| 17 | 5851f77a41f1 | ksiegowosc_moja_pasja | 6 | Obecnie od 3 lat na stanowisku seniorskim, w korpo, w wewnętrznej księgowości - 16k brutto + benefity takie jak: bardzo duży dodatek ubraniowy, na odzież naszej marki, od kwietnia karta lunchowa, mult… |
| 18 | 64198f84b5c4 | grupa_2_507801603233194 | 6 | Jeżeli jest przerwa to będzie świadectwo pracy, wyrejestrowanie z ZUS, wypłata ekwiwalentu za urlop jeśli nie został cały wykorzystany. A od 2 stycznia nowa umowa, nowe zatrudnienie i nowe zgłoszenie… |
| 19 | 2586f286931d | grupa_2_507801603233194 | 6 | Ja po poronieniu oddawałam "materiał" do badań genetycznych aby określić płeć oraz poznać ewentualna przyczyne poronienia. W szpitalu poprosiłam o wypisanie karty urodzenia martwego dziecka (nie pamię… |
| 20 | 2aadf964b478 | grupa_2_507801603233194 | 6 | Jeśli z tego co rozumiem- jest to wypłata pieniężna, spoza ZFŚS bo jak wynika z posta go nie ma, równa dla każdego pracownika (na jej wysokość nie wpływają żadne osiągnięcia indywidualne tylko po pros… |

## 7. Unrelated observations

- README.md opisuje tylko wcześniejszy stateless scaffold — brak wzmianki o workflow layer, intent routing i clarification gate, które są już w repo. Dokumentacyjny dług, do naprawy osobno.
- fb_pipeline/posts_tagged.json (10700 rekordów) to post-processed wariant posts_output_backup.json z dodanymi polami tag/char_count. Nie jest używany w tym ingestie, ale nadal jest tracked w git i nie w .gitignore — można rozważyć osobne uprzątnięcie legacy pipeline'u.
- Token 'wyświetl' i 'więcej' zajmują top-8/top-2 miejsca w keywords. To artefakt scrapera — FB ucina długie posty zostawiając UI label '... Wyświetl więcej'. Do usunięcia albo po stronie scrapera, albo jako dodatkowy krok normalizacji przed Zadaniem 2 (klasteryzacja).
- Top 1 engaging post (10 komentarzy) wygląda na długi komentarz, nie post — scraper najwyraźniej zagarnia też wątki odpowiedzi. Ryzyko dla klasteryzacji: treści konwersacyjne zamiast pytań. Warto w Zadaniu 2 dodać filtr na brak pytajnika w długich tekstach albo sprawdzić, czy scraper nie myli posta z najwyżej głosowanym komentarzem.
