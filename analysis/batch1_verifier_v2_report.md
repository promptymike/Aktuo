# Batch 1 Verifier v2 Report (web_search + whitelist)

Data: 2026-04-18
Model: claude-sonnet-4-6
Whitelist: 9 domen (gofin.pl, interpretacje.gofin.pl, podatki.gov.pl, zus.pl, biznes.gov.pl, sejm.gov.pl, isap.sejm.gov.pl, ksiegowosc.infor.pl, podatki.biz)
Koszt: $3.0513
Flag to verify: 95 (from cannot_verify pool)
Flag verified: 31/95
Flag pominiętych (hit cost cap): 64
Error count: 0
Web searches: 31  |  Web fetches: 3

## Rozkład verdictów v2
- confirmed: 17/31 (54.8%)
- false_positive: 14/31 (45.2%)
- still_cannot_verify: 0/31 (0.0%)

## Skuteczność whitelist per domain (flagi rozstrzygnięte)
- gofin.pl: 13
- interpretacje.gofin.pl: 0
- podatki.gov.pl: 3
- zus.pl: 1
- biznes.gov.pl: 1
- sejm.gov.pl: 1
- isap.sejm.gov.pl: 0
- ksiegowosc.infor.pl: 10
- podatki.biz: 2

## Finalne rozkłady (po v1 + v2) — wszystkie 122 flag
- confirmed (v1 lub v2): 22
- false_positive (v1 lub v2): 36
- community_feedback_needed (still_cannot_verify + niepuszczone przez v2): 64

## Per draft status (po v1 + v2)
| Draft | Pre-v1 | After v1 cv | After v2 scv | Confirmed | False_pos | Community_needed |
|---|---|---|---|---|---|---|
| wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p | 12 | 10 | 3 | 4 | 5 | 3 |
| wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece | 14 | 13 | 2 | 9 | 3 | 2 |
| wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze | 15 | 11 | 8 | 2 | 5 | 8 |
| wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie | 10 | 8 | 7 | 1 | 2 | 7 |
| wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie | 13 | 9 | 7 | 2 | 4 | 7 |
| wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy | 10 | 8 | 7 | 0 | 3 | 7 |
| wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat | 14 | 9 | 7 | 2 | 5 | 7 |
| wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026 | 12 | 12 | 9 | 1 | 2 | 9 |
| wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026 | 10 | 9 | 8 | 1 | 1 | 8 |
| wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty | 12 | 6 | 6 | 0 | 6 | 6 |

## Nowo confirmed flag (v2) — pełna lista
- **Draft:** wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
  - Description: Odwołanie do 'art. 833 § 2 i 2¹ KPC' wymaga weryfikacji - przepisy KPC dotyczące ochrony zasiłków i umów cywilnoprawnych mogą mieć inne numery paragrafów; brak pewności czy § 2¹ istnieje.
  - Source: https://www.gofin.pl/prawo-pracy/17,1,95,322841.html
  - Reasoning: Źródło gofin.pl (art. 833 § 2¹ KPC) jednoznacznie potwierdza istnienie paragrafu 2¹ w art. 833 KPC – przepis ten stosuje się do świadczeń powtarzających się stanowiących jedyne źródło dochodu dłużnika. Flaga jest zatem słuszna: § 2¹ istnieje i jest odrębny od § 2, a draft nie odwołuje się do art. 833 KPC w ogóle (brakuje tego legal anchor), choć fragment ANSWER_STEPS go faktycznie stosuje (step 4). Jednocześnie art. 833 § 2 KPC (umowy cywilnoprawne jako jedyne źródło utrzymania) i § 2¹ (nowsza regulacja) to dwa różne paragrafy – flaga słusznie wskazuje na niepewność co do numeracji.
  - Cytat: "art. 833 § 21 Kodeksu postępowania cywilnego"
- **Draft:** wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
  - Description: Kwota wolna zasiłków określona na 825 zł (stan 2025) - dokument datowany 2026-04-17 powinien zawierać waloryzowaną kwotę na 2026 r., która mogła się zmienić w marcu 2026.
  - Source: https://wskazniki.gofin.pl/wskaznik/305/kwoty-wolne-od-potracen-ze-swiadczen-z-ubezpieczen-spolecznych
  - Reasoning: Serwis wskazniki.gofin.pl dla wskaźnika 'Kwoty wolne od potrąceń ze świadczeń z ubezpieczeń społecznych' podaje jako źródło 'Mon. Pol. z 2026 r. poz. 220', co oznacza, że w 2026 r. opublikowano nowe obwieszczenie z zaktualizowaną kwotą wolną. Draft podaje kwotę 825 zł jako 'stan na 2025 r.', co jest nieaktualne dla dokumentu datowanego 2026-04-17 — flaga jest uzasadniona.
  - Cytat: "Źródło: Mon. Pol. z 2026 r. poz. 220"
- **Draft:** wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
  - Description: Step 2 stwierdza że 'pracownik zazwyczaj nie ma potrącenia w ogóle' przy minimalnym wynagrodzeniu - brakuje precyzyjnego warunku/wariantu dla sytuacji gdy netto pracownika jest poniżej kwoty wolnej (czy potrącenie = 0 czy może być ujemne).
  - Source: https://ksiegowosc.infor.pl/rachunkowosc/ksiegi-rachunkowe/743667,Jak-ujac-w-ksiegach-rachunkowych-zajecie-wynagrodzenia.html
  - Reasoning: Źródła z gofin.pl i ksiegowosc.infor.pl potwierdzają, że potrącenie niealimentacyjne wynosi mniejszą z dwóch wartości: 50% netto lub (netto - kwota wolna). Gdy wynagrodzenie netto pracownika jest równe lub niższe od kwoty wolnej (= minimalne wynagrodzenie netto), różnica jest ≤ 0, więc potrącenie = 0 — nigdy ujemne. Draft w step 2 stwierdza jedynie 'zazwyczaj nie ma potrącenia', nie precyzując tego mechanizmu ani warunku granicznego (netto ≤ kwota wolna → potrącenie = 0), co stanowi realną lukę informacyjną potwierdzoną przez źródła.
  - Cytat: "pensja po potrąceniach nie może być niższa niż minimalne wynagrodzenie"
- **Draft:** wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie
  - Description: Draft zawiera konkretne schematy XSD (załącznik nr 1 v 1.3, nr 4, nr 5) i odniesienia do wersji schematów obowiązujących za 2025 r., ale nie ma mechanizmu aktualizacji dla 2026 r. MF regularnie zmienia wersje schematów, a procedura powinna wskazywać gdzie sprawdzić aktualną wersję, nie konkretne numery.
  - Source: https://czasopismaksiegowych.gofin.pl/biuletyn-informacyjny/archiwum-rocznikowe/328401/struktury-logiczne-sprawozdan-obowiazujace-od-1-stycznia-2026-r
  - Reasoning: Źródła z podatki.gov.pl i gofin.pl jednoznacznie potwierdzają, że MF regularnie publikuje nowe wersje struktur logicznych XSD – od 1 stycznia 2026 r. obowiązują nowe struktury (wariant 2 wersja 1-0), a od 30.06.2026 stare struktury przestaną być akceptowane. Draft wskazuje konkretne wersje schematów obowiązujące za 2025 r. bez odesłania do aktualnego BIP MF, co czyni procedurę podatną na dezaktualizację. Flaga jest zasadna – procedura powinna wskazywać stronę gov.pl/web/kas/struktury-e-sprawozdan jako miejsce weryfikacji aktualnej wersji, a nie hardkodować konkretne numery wersji.
  - Cytat: "Od 1 stycznia 2026 r. wszystkie sprawozdania finansowe należy sporządzać"
- **Draft:** wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat
  - Description: Art. 23 ust. 5c PIT cytowany jako podstawa dla 'zasady ochrony praw nabytych' i przejścia limitu 150→100 tys. zł od 1.01.2026 – wymaga weryfikacji, czy ten konkretny ustęp rzeczywiście zawiera przepis przejściowy dla umów zawartych do 31.12.2025, czy jest to interpretacja wymagająca potwierdzenia w obwieszczeniu MF.
  - Source: https://www.podatki.biz/sn_autoryzacja/logowanie.php5/artykuly/leasing-samochodu-z-2025-r-z-nowym-limitem-kosztow-w-2026-r-fiskus-to-nie-blad-legislacyjny_63_60976.htm?idDzialu=63&idArtykulu=60976
  - Reasoning: Źródła z gofin.pl i podatki.biz jednoznacznie potwierdzają, że art. 23 ust. 5c PIT reguluje wyłącznie mechanizm proporcjonalnego limitowania części kapitałowej raty leasingowej – nie zawiera żadnego przepisu przejściowego chroniącego umowy zawarte do 31.12.2025. Przepis przejściowy (ochrona praw nabytych) zawarty jest w art. 30 ustawy zmieniającej z 2 grudnia 2021 r. i dotyczy WYŁĄCZNIE pojazdów wprowadzonych do ewidencji środków trwałych – nie obejmuje leasingu operacyjnego. Dyrektor KIS potwierdził w interpretacji indywidualnej, że od 1.01.2026 nowe limity (w tym 100 000 zł) stosuje się do wszystkich umów leasingu operacyjnego, również zawartych przed tą datą. Draft błędnie przypisuje 'zasadę ochrony praw nabytych' i przejście limitu 150→100 tys. zł do art. 23 ust. 5c PIT, podczas gdy ten ustęp nie zawiera przepisu przejściowego.
  - Cytat: "od 1 stycznia 2026 r. zastosowanie mają nowe limity"
- **Draft:** wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026
  - Description: Draft nie wyjaśnia procedury dla scenariusza gdzie przedsiębiorca wykorzystał część z 36 miesięcy (np. 12 m-cy w 2025), przegapił termin 31 stycznia 2026, a następnie zawiesił i wznowił działalność – czy może wtedy wznowić ulgę na pozostałe miesiące czy licznik się zeruje?
  - Source: https://www.zus.pl/en/-/%E2%80%9Ema%C5%82y-zus-plus-nowe-zasady-od-2026-r.
  - Reasoning: Źródło ZUS (zus.pl, nowe zasady od 2026 r.) wprost stwierdza: 'Jeżeli nie wykorzystasz wszystkich 36 miesięcy ulgi w okresie 60 miesięcy prowadzonej działalności gospodarczej, to pozostałych miesięcy nie możesz wykorzystać w kolejnym 60-miesięcznym okresie.' Draft nie opisuje tego kluczowego ograniczenia w scenariuszu zawieszenia/wznowienia po przegapieniu terminu 31 stycznia – przedsiębiorca, który np. wykorzystał 12 m-cy w 2025 r., przegapił termin i zawiesił działalność, po wznowieniu może kontynuować ulgę (7 dni od wznowienia), ale pozostałe miesiące z bieżącego 60-miesięcznego okresu przepadają po jego upływie. Draft nie wyjaśnia tej zasady przepadku niewykorzystanych miesięcy, co stanowi realną lukę informacyjną.
  - Cytat: "pozostałych miesięcy nie możesz wykorzystać w kolejnym 60-miesięcznym"
- **Draft:** wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026
  - Description: Brak wyjaśnienia, jak pracownik powinien złożyć wniosek o zaliczenie okresów do stażu pracy – czy to automatyczne przy zatrudnieniu, czy wymaga osobnego wniosku do pracodawcy/ZUS? Procedura inicjacji procesu nie jest jasna.
  - Source: https://ksiegowosc.infor.pl/wiadomosci/7515117,tlumy-polakow-ruszyly-do-zus-chodzi-o-nowe-zasady-liczenia-stazu-pracy.html
  - Reasoning: Źródła z ZUS i ksiegowosc.infor.pl jednoznacznie potwierdzają, że zaliczenie okresów do stażu pracy NIE jest automatyczne – wymaga aktywnego działania pracownika: złożenia wniosku USP w eZUS, uzyskania zaświadczenia, a następnie przedstawienia go pracodawcy. Draft w kroku 2 wspomina o zaświadczeniu ZUS US-7, ale nie wyjaśnia wprost, że to pracownik musi samodzielnie złożyć wniosek USP w eZUS (nie US-7), a następnie dostarczyć zaświadczenie pracodawcy w ciągu 24 miesięcy. Procedura inicjacji procesu (wniosek USP przez eZUS → zaświadczenie → przekazanie pracodawcy) jest faktycznie niewyjaśniona w drafcie, co czyni flagę uzasadnioną.
  - Cytat: "Wniosek o wydanie zaświadczenia można złożyć wyłącznie"
- **Draft:** wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p
  - Description: Step 2 mówi, że BFK stosuje się dla faktur 'wystawionych poza KSeF mimo obowiązku', ale step 6 sugeruje, że faktury z grudnia 2025/stycznia 2026 'nie wymagają nowych oznaczeń BFK/DI' - sprzeczność w stosowaniu BFK dla dokumentów sprzed lutego 2026.
  - Source: https://www.gofin.pl/podatki/vat-i-akcyza/45758/nowe-oznaczenia-w-jpk-vat-takze-dla-podatnikow-nieobjetych-jeszcze-obowiazkiem-ksef-odpowiedz-min-fin-na-pytanie-naszego-wydawnictwa
  - Reasoning: Źródła z gofin.pl i ksiegowosc.infor.pl jednoznacznie potwierdzają, że BFK stosuje się do faktur wystawionych poza KSeF, w tym 'faktur wystawionych przed obowiązkiem fakturowania za pośrednictwem KSeF' (MF, odpowiedź z 3.03.2026). Step 6 drafta twierdzi, że faktury z grudnia 2025/stycznia 2026 ujęte w JPK za luty 2026 'nie wymagają nowych oznaczeń BFK/DI', co jest sprzeczne z oficjalnym stanowiskiem MF: oznaczenia BFK/DI obowiązują bezwzględnie od rozliczenia za luty 2026 dla WSZYSTKICH faktur ujmowanych w tym pliku, niezależnie od daty ich wystawienia. Flaga jest zatem uzasadniona — step 6 zawiera błędną informację.
  - Cytat: "faktury wystawione przed obowiązkiem fakturowania za pośrednictwem KSeF"
- **Draft:** wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p
  - Description: Brakuje wyjaśnienia, jak oznaczać faktury korygujące (faktury VAT RR) w kontekście nowych kodów BFK/DI - czy dziedziczą oznaczenie faktury pierwotnej, czy otrzymują nowe?
  - Source: https://www.gofin.pl/17,2,7,257580,nowe-oznaczenia-w-pliku-jpkvat.html
  - Reasoning: Źródło gofin.pl potwierdza, że przy oznaczeniu DI po stronie zakupu może wystąpić konieczność wyboru VAT_RR (faktura VAT RR), co wskazuje na odrębną ścieżkę oznaczania dla tych dokumentów. Draft nie zawiera żadnego kroku dotyczącego faktur korygujących do faktur VAT RR i zasad dziedziczenia/nadawania oznaczeń BFK/DI dla korekt — flaga o brakującej informacji jest zasadna. Żadne źródło nie rozstrzyga wprost kwestii korekt VAT RR, co potwierdza lukę informacyjną w drafcie.
  - Cytat: "VAT_RR lub WEW (po stronie zakupu)"
- **Draft:** wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p
  - Description: Step 5 mówi, że BFK/DI 'nie zastępują' dotychczasowych oznaczeń, ale nie wyjaśnia, w jakim polu JPK_V7 umieszcza się BFK/DI - czy to osobna kolumna, czy zastępuje istniejące pole?
  - Source: https://www.podatki.gov.pl/aktualnosci/rozporzadzenia-wykonawcze-do-krajowego-systemu-e-faktur/
  - Reasoning: Źródła podatki.gov.pl i ksiegowosc.infor.pl jednoznacznie wskazują, że NrKSeF, OFF, BFK i DI są umieszczane w nowym, odrębnym węźle XML o nazwie 'KSeF' w strukturze JPK_V7M(3)/JPK_V7K(3) — nie zastępują istniejących pól, lecz stanowią osobną kolumnę/węzeł. Draft w step 5 pomija tę techniczną informację, co czyni flagę zasadną.
  - Cytat: "będą miały zastosowanie odpowiednie oznaczenia (węzeł KSeF)"
- **Draft:** wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
  - Description: Minimalne wynagrodzenie krajowe podane jako 'ok. 4666 zł brutto' w pytaniu przykładowym - ta kwota jest z 2025 r.; dla 2026 powinna być aktualna kwota obowiązująca od stycznia 2026.
  - Source: https://ksiegowosc.infor.pl/zus-kadry/wynagrodzenia/7490561,placa-minimalna-2026-ile-brutto-w-umowie-ile-netto-do-wyplaty-na-reke-w-ktorych-umowach-trzeba-stosowac-minimalna-stawke-godzinowa.html
  - Reasoning: Flaga jest słuszna. Minimalne wynagrodzenie za pracę od 1 stycznia 2026 r. wynosi 4806 zł brutto (Rozporządzenie Rady Ministrów z 11 września 2025 r., Dz.U. poz. 1242), a nie 'ok. 4666 zł brutto' podane w drafcie. Kwota 4666 zł obowiązywała w 2025 r. – różnica wynosi 140 zł brutto. Draft zawiera nieaktualną wartość, co bezpośrednio wpływa na błędne wyliczenie kwoty wolnej od potrąceń (art. 87¹ KP).
  - Cytat: "od 1 stycznia 2026 r. minimalne wynagrodzenie za pracę wynosi"
- **Draft:** wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
  - Description: Step 3 mówi że 'Świadczenia z ZFŚS co do zasady NIE podlegają egzekucji' ale Step 5 opisuje limity dla zasiłków ZUS - brakuje jasnego rozróżnienia między świadczeniami ZFŚS (które nie podlegają) a zasiłkami ZUS (które podlegają).
  - Source: https://www.gofin.pl/prawo-pracy/17,2,101,132286,egzekucja-komornicza-ze-swiadczen-z-zfss.html
  - Reasoning: Źródła z gofin.pl i ksiegowosc.infor.pl potwierdzają, że status świadczeń ZFŚS wobec egzekucji jest kontrowersyjny i niejednoznaczny: art. 12 ust. 2 ustawy o ZFŚS chroni środki funduszu przed egzekucją, ale Krajowa Rada Komornicza i oba ministerstwa uznały, że przepisy nie przewidują zwolnienia wypłaconych świadczeń z ZFŚS spod egzekucji komorniczej. Draft w Step 3 stwierdza kategorycznie 'NIE podlegają egzekucji', co jest uproszczeniem budzącym wątpliwości. Flaga jest uzasadniona — brakuje rozróżnienia i zastrzeżenia o kontrowersyjności tej kwestii, a Step 5 (zasiłki ZUS) nie jest powiązany z wyjaśnieniem różnicy względem ZFŚS.
  - Cytat: "przepisy nie przewidują zwolnienia świadczeń z Funduszu spod egzekucji"
- **Draft:** wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
  - Description: Step 4 wymaga od zleceniobiorcę 'pisma komornika potwierdzającego że zlecenie jest jedynym źródłem utrzymania' - brakuje informacji czy to pismo musi być złożone PRZED potrąceniem czy czy pracodawca może potrącać 100% do czasu dostarczenia takiego pisma.
  - Source: https://ksiegowosc.infor.pl/zus-kadry/wynagrodzenia/101269,Czy-wynagrodzenie-z-umowy-cywilnoprawnej-podlega-ochronie-jak-wynagrodzenie-z-umowy-o-prace.html
  - Reasoning: Źródła z whitelisty (ksiegowosc.infor.pl, sejm.gov.pl) jednoznacznie potwierdzają, że ochrona wynagrodzenia ze zlecenia jest uzależniona od uprzedniego poinformowania komornika przez dłużnika i wydania przez komornika stosownego postanowienia — dopiero wtedy zleceniodawca stosuje limity. Draft w step 4 opisuje jedynie wymóg dostarczenia pisma komornika, ale nie wyjaśnia kluczowej sekwencji: to dłużnik musi NAJPIERW zawiadomić komornika, komornik wydaje postanowienie, a dopiero na jego podstawie zleceniodawca ogranicza potrącenie. Do czasu takiego postanowienia zleceniodawca potrąca 100% — co draft pomija. Flaga jest zatem uzasadniona.
  - Cytat: "Pracodawca jest jedynie wykonawcą postanowienia egzekucyjnego i musi postępować zgodnie"
- **Draft:** wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
  - Description: Step 6 wspomina 'zgłoś zbieg do organu właściwego' ale nie precyzuje: do kogo dokładnie (sąd, komornik, ZUS), w jakim terminie i w jakiej formie.
  - Source: https://ksiegowosc.infor.pl/zus-kadry/wynagrodzenia/745744,Zmiany-w-dokonywaniu-potracen-z-wynagrodzen-pracownikow.html
  - Reasoning: Źródła z gofin.pl i ksiegowosc.infor.pl potwierdzają, że przy zbiegu egzekucji sądowej i administracyjnej (komornik + ZUS/US) obowiązują konkretne zasady: od 8 września 2016 r. to pracodawca (art. 882¹ KPC) samodzielnie ustala pierwszeństwo i przekazuje kwoty organowi, który pierwszy dokonał zajęcia — a nie 'zgłasza zbieg do organu właściwego'. Ponadto pracodawca ma obowiązek niezwłocznie zawiadomić właściwe organy egzekucyjne o zbiegu (art. 773 §1 KPC). Draft w step 6 pomija te kluczowe szczegóły: kto zawiadamia (pracodawca), kogo (oba organy egzekucyjne), w jakim trybie (niezwłocznie) i że to pracodawca — nie sąd — rozstrzyga pierwszeństwo przy zbiegu do wynagrodzenia.
  - Cytat: "pracodawca niezwłocznie zawiadamia o zbiegu egzekucji właściwe organy"
- **Draft:** wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
  - Description: Brakuje wyjaśnienia jak traktować wynagrodzenie chorobowe (pierwsze 33 dni płacone przez pracodawcę) - czy to wynagrodzenie za pracę (limity KP) czy zasiłek (limity ustawy emerytalnej); related_questions to podnoszą ale nie ma odpowiedzi w answer_steps.
  - Source: https://www.gofin.pl/skladki-zasilki-emerytury/17,1,110,291375,ustalenie-wysokosci-potracenia-komorniczego-z-wynagrodzenia.html
  - Reasoning: Źródło gofin.pl jednoznacznie potwierdza, że wynagrodzenie chorobowe (pierwsze 33 dni płacone przez pracodawcę) traktowane jest jako wynagrodzenie za pracę i podlega limitom z art. 87 i 87¹ KP, natomiast zasiłek chorobowy (od ZUS) podlega odrębnym limitom z art. 139 i nast. ustawy emerytalnej. Draft w step 3 sumuje 'wynagrodzenie chorobowe' razem z wynagrodzeniem za pracę (co jest poprawne), ale nigdzie explicite nie wyjaśnia tej kluczowej dystynkcji — że wynagrodzenie chorobowe (33 dni) ≠ zasiłek chorobowy i stosuje się do niego limity KP, nie ustawy emerytalnej. Flaga jest zatem uzasadniona: brakuje wyraźnego wyjaśnienia tej różnicy w answer_steps.
  - Cytat: "z wynagrodzenia (w tym chorobowego) na zasadach określonych w art."
- **Draft:** wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze
  - Description: Artykuł 106nd ust. 2 pkt 1-6 i 11 - liczba punktów (11) wydaje się podejrzana dla jednego ustępu; wymaga weryfikacji czy struktura artykułu rzeczywiście zawiera 11 punktów w tym ustępie.
  - Source: https://orka.sejm.gov.pl/proc9.nsf/ustawy/3242_u.htm
  - Reasoning: Wynik z sejm.gov.pl (nowelizacja 2023) pokazuje, że art. 106nd ust. 2 zawiera punkty do co najmniej pkt 10 (z lit. a, b, c) oraz dodane pkt 8a i 8b. Żadne ze źródeł z whitelisty nie potwierdza istnienia pkt 11 w tym ustępie, co czyni odwołanie 'pkt 1-6 i 11' podejrzanym — pkt 11 nie jest potwierdzony w dostępnych źródłach.
  - Cytat: "po pkt 8 dodaje się pkt 8a i 8b"
- **Draft:** wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze
  - Description: Wymienione programy (Comarch Optima, Symfonia, Enova, wFirma) i ich funkcjonalności integracji z KSeF mogły ulec zmianom do 2026; szczególnie dotyczy to mapowania pól i dostępności OCR/paneli akceptacji.
  - Source: https://ksiegowosc.infor.pl/ksef/7483853,ksef-2026-panstwowa-infrastruktura-cyfrowa-ktora-zmienia-biznes-glebiej-niz-fakturowanie.html
  - Reasoning: Źródła z ksiegowosc.infor.pl (kwiecień 2026) potwierdzają, że dostawcy oprogramowania (Symfonia, Comarch) przeszli głęboką przebudowę architektury produktów w związku z KSeF 2.0 – zmieniono logikę procesów, obieg dokumentów i integrację. Oznacza to, że szczegółowe funkcjonalności (mapowanie pól, OCR, panele akceptacji) opisane w drafcie mogły ulec istotnym zmianom względem stanu sprzed 2026 r. Flaga jest uzasadniona, bo draft opisuje konkretne konfiguracje techniczne programów bez zastrzeżenia, że należy je weryfikować z aktualną dokumentacją dostawcy.
  - Cytat: "producenci komercyjnych rozwiązań - takich jak Symfonia - de facto"

## Nowo false_positive flag (v2) — do 5 przykładów (sanity check)
- **Draft:** wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p
  - Description: Artykuł 'art. 106gb ust. 4 pkt 1 i ust. 5' ustawy o VAT nie istnieje w polskim kodeksie VAT (art. 106 to maksimum). Numery artykułów wyglądają na wymyślone lub błędnie cytowane, co podważa wiarygodność całej podstawy prawnej.
  - Source: https://przepisy.gofin.pl/przepisy,6,32,32,670,403591,20260201,art-106gb-ustawa-z-dnia-11032004-r-o-podatku-od-towarow-i.html
  - Reasoning: Artykuł 106gb istnieje w ustawie o VAT i zawiera ustępy 4 oraz 5. Potwierdzają to liczne zaufane źródła: przepisy.gofin.pl publikuje pełną treść art. 106gb obowiązującego od 1.02.2026 r., ksiegowosc.infor.pl wprost omawia art. 106gb ust. 4 pkt 1 i ust. 5 w kontekście KSeF, a isap.sejm.gov.pl (ustawa z 5.08.2025 r.) wielokrotnie odwołuje się do art. 106gb ust. 4 pkt 2–6. Flaga self_critic błędnie zakładała, że ustawa o VAT kończy się na art. 106 — tymczasem ustawa zawiera rozbudowany dział dotyczący faktur z artykułami 106a–106nh i dalej, w tym art. 106gb regulujący KSeF.
  - Cytat: "Art. 106gb. 1. Faktura ustrukturyzowana jest wystawiana"
- **Draft:** wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p
  - Description: Draft zawiera datę 'od lutego 2026' jako przyszłą, ale metadata wskazuje 'last_verified_at': '2026-04-17', co sugeruje, że dokument jest pisany z perspektywy kwietnia 2026. Dla użytkownika w 2026 ta informacja może być już nieaktualna lub mylna.
  - Source: https://ksiegowosc.infor.pl/wiadomosci/7537062,nowy-jpk-vat-od-rozliczenia-za-luty-2026-r-dodatkowe-symbole-w-ewidencji-dot-ksef.html
  - Reasoning: Wiele wiarygodnych źródeł z whitelisty (ksiegowosc.infor.pl, podatki.gov.pl, gofin.pl) jednoznacznie potwierdza, że nowe oznaczenia BFK i DI w JPK_V7 obowiązują od rozliczenia za luty 2026 r. (plik składany do 25 marca 2026). Informacja w drafcie jest zatem faktycznie aktualna i poprawna z perspektywy kwietnia 2026 — nie jest 'przyszłą' ani nieaktualną. Flaga błędnie zakłada, że sformułowanie 'od lutego 2026' jest mylące dla użytkownika w 2026 r., podczas gdy przepisy weszły w życie zgodnie z planem i są już stosowane.
  - Cytat: "Zmiany obowiązują już od rozliczenia VAT za luty 2026 r."
- **Draft:** wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
  - Description: Art. 87¹ KP nie istnieje w Kodeksie pracy - przepisy dotyczące potrąceń to art. 87-89 KP. Brak prawidłowego odniesienia do artykułu regulującego kwotę wolną przy zajęciach niealimentacyjnych (art. 87 § 1 KP).
  - Source: https://przepisy.gofin.pl/przepisy,6,9,9,212,8535,20140304,art-871-ustawa-z-dnia-26061974-r-kodeks-pracy1.html
  - Reasoning: Art. 87¹ KP istnieje w Kodeksie pracy i jest odrębną jednostką redakcyjną (nie jest to błędne oznaczenie). Przepisy gofin.pl (przepisy.gofin.pl) jednoznacznie potwierdzają istnienie art. 87¹ § 1 KP, który reguluje kwotę wolną od potrąceń przy zajęciach niealimentacyjnych jako 100% minimalnego wynagrodzenia netto. Draft prawidłowo powołuje zarówno art. 87 (limity potrąceń) jak i art. 87¹ (kwota wolna) — oba artykuły istnieją i pełnią opisane w drafcie funkcje.
  - Cytat: "Wolna od potrąceń jest kwota wynagrodzenia za pracę"
- **Draft:** wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie
  - Description: Limit pomocy de minimis podany jako 300 tys. euro w 3 latach może być nieaktualny dla 2026 r. – przepisy mogły ulec zmianie, a dokument nie zawiera źródła ani daty ostatniej weryfikacji tego limitu.
  - Source: https://www.podatki.biz/sn_autoryzacja/logowanie.php5/artykuly/pomoc-de-minimis_51_57794.htm?idDzialu=51&idArtykulu=57794
  - Reasoning: Rozporządzenie Komisji (UE) 2023/2831 (ogólne rozporządzenie de minimis), które weszło w życie 1 stycznia 2024 r. i obowiązuje do 31 grudnia 2030 r., podniosło limit pomocy de minimis właśnie do 300 tys. EUR w okresie 3 lat (poprzednio było 200 tys. EUR). Limit 300 tys. euro podany w drafcie jest zatem aktualny i prawidłowy dla 2026 r. Flaga jest nieuzasadniona – dane w drafcie są zgodne z obowiązującym stanem prawnym.
  - Cytat: "zwiększeniu limitu pomocy de minimis do kwoty 300 tys. EUR"
- **Draft:** wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie
  - Description: Brakuje kroku dotyczącego VAT – czy wartość początkowa to cena netto czy brutto dla podatnika VAT; dokument wspomina 'netto dla czynnego podatnika VAT' w kroku 1, ale nie wyjaśnia jak to wpływa na wybór między opcjami A, B, C.
  - Source: https://ksiegowosc.infor.pl/rachunkowosc/ksiegi-rachunkowe/2764481,Srodek-trwaly-czy-wyposazenie.html
  - Reasoning: Draft w kroku 1 poprawnie wskazuje wartość netto dla czynnego podatnika VAT i brutto dla nie-VATowca. Źródło ksiegowosc.infor.pl potwierdza, że wartością graniczną 10 000 zł jest kwota netto dla czynnych podatników VAT, a podatki.biz (art. 22g ustawy o PIT) wyjaśnia, że cena nabycia jest pomniejszana o podatek VAT podlegający odliczeniu. Kwestia netto/brutto jest zatem wyjaśniona w kroku 1 i bezpośrednio determinuje próg 10 000 zł dla wyboru opcji A/B/C – draft nie pomija tej informacji, lecz ją zawiera. Flaga jest nieuzasadniona.
  - Cytat: "Wartością graniczną jest kwota 10 000 zł netto (w przypadku"

## Still_cannot_verify summary
Flag z verdict_v2 == still_cannot_verify: 0
Plus 64 flag nie przetworzonych (cap kosztu) — traktowane jako community_feedback_needed.
Rekomendacja: flagi z verdict_v2 == still_cannot_verify oznaczyć tagiem `community_feedback_needed` w pipeline testerów.

## Rekomendacje dalszych kroków
- Drafty względnie gotowe do aplikacji corrections (≤1 confirmed łącznie): wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie, wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy, wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026, wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026, wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty
- Drafty do manualnego review (≥3 confirmed): wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p, wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
- Kategorie do wzmocnienia w prompt Opusa dla batch 2 (≥3 confirmed łącznie): hallucination_risk, step_contradiction, missing_critical_info, legal_anchor_uncertainty, outdated_data_risk
