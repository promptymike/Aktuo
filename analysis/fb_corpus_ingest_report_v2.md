# FB corpus ingest report

Generated at: 2026-04-17T14:58:24+00:00

## 1. Executive summary

Trzy scrape'y FB (2 grupy) zsumowane: **40537** surowych postów. Po deduplikacji na SHA-256 pierwszych 200 znaków znormalizowanego tekstu i po filtrach jakości (question pattern, job ads, community-only markers) zostaje **24892** postów unikalnych.

Przy heurystyce ~100-150 postów na jeden klaster tematyczny, z tego korpusu realistycznie wyjdzie **~165-248** klastrów (Zadanie 2).

## 2. Volume table

| Source file | Group | Raw | After dedupe | After quality | Survival |
|---|---|---|---|---|---|
| posts_15k_ksiegowosc_moja_pasja.json | ksiegowosc_moja_pasja | 15229 | 14497 | 12147 | 79.8% |
| posts_output.json | grupa_2_507801603233194 | 14608 | 13977 | 12425 | 85.1% |
| posts_output_backup.json | ksiegowosc_moja_pasja | 10700 | 383 | 320 | 3.0% |

Cross-file duplicates removed (resolved by newest scraped_at): **10025**. Duplicates collapsed within a single file: **1631**.

## 3. Quality breakdown

### Rejected

| Reason | Count |
|---|---:|
| too_short | 27 |
| marketing_bold | 37 |
| sales_spam | 21 |
| job_ad | 232 |
| community_only | 0 |
| no_question_pattern | 3648 |

### Flagged (kept)

| Flag | Count |
|---|---:|
| too_long | 0 |
| no_comments | 7388 |
| many_links | 0 |

### Top 20 keywords in final corpus

| Rank | Token | Frequency |
|---:|---|---:|
| 1 | pracy | 5093 |
| 2 | pracownik | 4551 |
| 3 | dzień | 3751 |
| 4 | vat | 3650 |
| 5 | zus | 3299 |
| 6 | witam | 3150 |
| 7 | ktoś | 3124 |
| 8 | proszę | 3116 |
| 9 | dobry | 3018 |
| 10 | roku | 2884 |
| 11 | dni | 2850 |
| 12 | jeśli | 2577 |
| 13 | pytanie | 2474 |
| 14 | ksef | 2327 |
| 15 | będzie | 2276 |
| 16 | pomoc | 2204 |
| 17 | faktury | 1967 |
| 18 | pit | 1897 |
| 19 | teraz | 1831 |
| 20 | pracownika | 1777 |

## 4. Random sample (seed=42, n=10)

- **7d7577191d16** · grupa_2_507801603233194 · comments: 1
  > #systemczasupracyPomocy! Nigdzie nie mogę znaleźć odpowiedzi Jaki zastosować system czasu pracy dla osoby, która chce pracować tylko 4 dni w tygodniu po 8 godzin na 4/5 etatu? Chce mieć środy wolne, każdą. I to ma być tylko środa. I przez to norma czasu pracy w niektórych miesiącach będzie się rozje…
- **94192d8158d7** · ksiegowosc_moja_pasja · comments: 1
  > mam pytanie odnośnie ulgi na dziecko. Czy w przypadku gdy dziecko przekroczyło dochody, to matka może się mimo to rozliczyć jako "samotnie wychowujący " rodzic czy te zarobki dziecka dyskwalifikują zarówno ulgę na dziecko jak i możliwość wspólnego rozliczenia z matką?
- **d3ae0749fd3f** · ksiegowosc_moja_pasja · comments: 2
  > Gdzie na nowym PUE ZUS znajdują się komunikaty np. O nieopłaconych składkach.Na maila przychodzi informacja że na pue zus (ezus) jest dostarczona informacja. Wchodzę we wszystkie przegrody wiadomości po komunikaty i nic nie widać??????Co robię źle?
- **eaa948a4816c** · grupa_2_507801603233194 · comments: 1
  > Jak policzyć podstawę zasiłku Zleceniobiorcy?Zatrudniony od 1.09. Zwolnienie lekarskie od 22.09 do 26.09. Był zgłoszony do dobrowolnego chorobowego u poprzedniego Zleceniodawcy ponad 90 dni.Wynagrodzenie godzinowe. Czy do podstawy wziąć jego przychód z września w uzupełnieniu do pełnego miesiąca. Cz…
- **6a213c65bb36** · ksiegowosc_moja_pasja · comments: 3
  > Mam wynajęty samochod osobowy w spółce od innej spółki jak mam rozliczać paliwo ? Ile VAT ile Kup ? I wartość samochodu coś ma za znaczenie ? Dziękuję
- **44258da5228d** · ksiegowosc_moja_pasja · comments: 2
  > Jak wystawia to powinien być zgłoszony a po miesiącu rozliczenie . Przynajmniej powinno się rejestrować ale ja z niewiedzy tak robiłem dwa lata co rok mnie wzywali dlaczego nie przeszłam na VAT po okazaniu z niemieckim kontrahentem miałem spokój ale to
- **fe5e9d07f090** · ksiegowosc_moja_pasja · comments: 0
  > Hej  w jaki sposób księgujecie potrącenia na multisport na liście płac?  Fakturę zakupu księgujecie w całości, a następnie wyliczacie VAT należny od polowy kwoty? (pracodawca finansuje 50%)?
- **f68a52471773** · ksiegowosc_moja_pasja · comments: 0
  > Witam, mam przypadek Pani wróciła z dzieckiem do Polski, Pan został w Holandii. Chodzi o odliczenie ulgi na jedno dziecko czyli limitu dochodów małżonków. Pan twierdzi że jest wymeldowany z Polski i przyjezdza może na 30 dni w roku więc dochodów zagranicznych nie powinnam brać pod uwagę. Ale moim zd…
- **45f74adfe272** · grupa_2_507801603233194 · comments: 1
  > Prosze o pomoc. Mamy zgon. Nagła śmierć pracownika. Pracował 3.5 miesiąca, miał zajęcie komornicze.  Z tego co sie orientowałam to swiad.pracy i odprawę wypłaca sie os uprawnionej. Nie jest to skomplikowane.  Tutaj mamy sytuację ze były pracownik byl po rozwodzie i ma nieletnie dzieci. Na dzieciach…
- **6012cae8f0ec** · ksiegowosc_moja_pasja · comments: 0
  > Witam ..zakupione wyposazenie do remontowaanego budynku (inwestycji w obcym śr. trwałym) czy mozna na bieząco w koszty czy dopiero bo przeniesieniu dzialalnosci do nowego budynku?

## 5. Cross-file dedupe verification

- Posty z backupu (2026-04-06, ta sama grupa 1), które miały duplikat w nowszym scrape grupy 1: **9971 / 10354**. Oczekiwanie: większość. Starszy snapshot jest nadzbiorem domeny czasowej nowszego.
- Posty z grupy 1 (nowszy scrape), które miały duplikat w grupie 2 (hash match): **54 / 14551**. Oczekiwanie: 0 albo bardzo mało — różne grupy, hash nie chwyta parafraz.

## 6. Top 20 most engaging (by comments_count)

| Rank | id | group | comments | text (first 200 chars) |
|---:|---|---|---:|---|
| 1 | 36e13a9301fd | ksiegowosc_moja_pasja | 10 | I jesteśmy z niedużej miejscowości jak by ktoś myślał że to Warszawa. |
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
| 14 | e29231b8abce | grupa_2_507801603233194 | 6 | Pit 2 sekcja C wypełnił? jeżeli tak to z perspektywy pracodawcy rozliczenie jest prawidłowe. Z perspektywy podatnika jeżeli nie wycofał ulgi w Zusie od emerytury to oświadczył nieprawdę. Konsekwencja… |
| 15 | 380e70f39edc | ksiegowosc_moja_pasja | 6 | Jak ksiegujecie VAT naliczony i należy od importu usług? Bo właśnie jestem w nowej firmie i nie pasuje mi, jak to jest księgowane... Księgują to poprzez funkcję naliczenia VATu naliczonego i należnego… |
| 16 | f0edd6e9989f | grupa_2_507801603233194 | 6 | Cześć, mam pytanie. Pracownik na umowie zlecenie, pobierajacy jednocześnie emeryturę.  Bez skladki chorobowej. Czy należy stosować  kwotę zmniejszającą podatek ? I drugie pytanie jeśli pracownica na u… |
| 17 | 808c0f29bbdc | grupa_2_507801603233194 | 6 | Samo zaświadczenie jako dokument ważne jest od 27.10.2025, dość nietrafne określenie, natomiast jak już komentarz wyżej wskazał, skoro jest na II roku to jednak jest ciągłość. Nawet jeśli przebywała n… |
| 18 | e636b427c2c2 | ksiegowosc_moja_pasja | 6 | OC zwraca różnicę klientowi - dodam że nie stanowi to kosztu jego przychodu skoro kosztów nie ponosi. Klijent zyskuje na składkach a Ty co najwyżej będziesz mieć troszkę większą składkę na OC z racji… |
| 19 | 7554d7eab221 | ksiegowosc_moja_pasja | 6 | Rzetelna odpowiedź wymagałaby pół godziny pisania komentarza, plus trochę pytań dodatkowych. Temat jest gorący i jest na topie jeśli chodzi o kontrole, więc jak chcesz podejść do niego porządnie to id… |
| 20 | 5851f77a41f1 | ksiegowosc_moja_pasja | 6 | Obecnie od 3 lat na stanowisku seniorskim, w korpo, w wewnętrznej księgowości - 16k brutto + benefity takie jak: bardzo duży dodatek ubraniowy, na odzież naszej marki, od kwietnia karta lunchowa, mult… |

## 7. Wpływ 1.5b fixes (Before / After)

Porównanie ilościowe v1 (commit 97a6efe, Zadanie 1) vs v1.5d (obecny run). Trzymane fixes: strip cutoff markerów (`Wyświetl więcej`, ellipsis) przed hashem, rozszerzone prefiksy `job_ad`, oraz nowe kategorie odrzuceń `sales_spam` i `marketing_bold`. Flaga `probably_comment` została wycofana w v1.5d (zbyt niska precyzja).

| Metric | v1 | v1.5d | Δ |
|---|---:|---:|---:|
| Raw total | 40537 | 40537 | 0 |
| Final total | 24954 | 24892 | -62 |
| Duplicates within files | 1629 | 1631 | +2 |
| Cross-file duplicates | 10026 | 10025 | -1 |
| Rejected: too_short | 15 | 27 | +12 |
| Rejected: no_question_pattern | 3807 | 3648 | -159 |
| Rejected: job_ad | 82 | 232 | +150 |
| Rejected: community_only | 0 | 0 | 0 |
| Rejected: marketing_bold (new) | — | 37 | n/a |
| Rejected: sales_spam (new) | — | 21 | n/a |
| Flagged: too_long | 0 | 0 | 0 |
| Flagged: no_comments | 7422 | 7388 | -34 |
| Flagged: many_links | 0 | 0 | 0 |
| Cutoff markers stripped (new) | — | 9113 | n/a |

Uwaga: spadek `final_total` między v1 i v1.5b to suma odrzuceń z trzech nowych reguł (`marketing_bold`, `sales_spam`, rozszerzone `job_ad`). Flagi nie usuwają postów z korpusu.

## 8. Unrelated observations

- README.md opisuje tylko wcześniejszy stateless scaffold — brak wzmianki o workflow layer, intent routing i clarification gate, które są już w repo. Dokumentacyjny dług, do naprawy osobno.
- fb_pipeline/posts_tagged.json (10700 rekordów) to post-processed wariant posts_output_backup.json z dodanymi polami tag/char_count. Nie jest używany w tym ingestie, ale nadal jest tracked w git i nie w .gitignore — można rozważyć osobne uprzątnięcie legacy pipeline'u.
- v1.5b: usunięto scraperowe cutoff markery (`Wyświetl więcej`, ellipsis) przed obliczeniem hasha. Efekt: mniej fałszywych duplikatów i czysty top-N keywords bez tokenów UI.
- v1.5d: wycofaliśmy heurystyczną flagę `probably_comment` (v1.5b/v1.5c miały za wysoki FP rate). Komentarze-jako-posty to bug scrapera — odfiltrujemy je na poziomie klastrów w Zadaniu 2 (posty i komentarze mają różny profil semantyczny: opis+pytanie vs instrukcja/opinia).
