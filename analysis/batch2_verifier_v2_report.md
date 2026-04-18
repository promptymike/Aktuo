# Batch 2 Verifier v2 Report (Sonnet + web_search + whitelist)

Scope: cannot_verify flagi po v1 across wszystkich 42 draftów. Sorted by severity
(high → medium → low), processed aż do hit cost cap $5.00. Pozostałe po capie
(329) → Stage 6 community_feedback_needed.

---

Data: 2026-04-18
Model: claude-sonnet-4-6
Whitelist: 9 domen (gofin.pl, interpretacje.gofin.pl, podatki.gov.pl, zus.pl, biznes.gov.pl, sejm.gov.pl, isap.sejm.gov.pl, ksiegowosc.infor.pl, podatki.biz)
Koszt: $5.0647
Flag to verify: 377 (from cannot_verify pool)
Flag verified: 48/377
Flag pominiętych (hit cost cap): 329
Error count: 0
Web searches: 59  |  Web fetches: 1

## Rozkład verdictów v2
- confirmed: 18/48 (37.5%)
- false_positive: 30/48 (62.5%)
- still_cannot_verify: 0/48 (0.0%)

## Skuteczność whitelist per domain (flagi rozstrzygnięte)
- gofin.pl: 23
- interpretacje.gofin.pl: 0
- podatki.gov.pl: 4
- zus.pl: 3
- biznes.gov.pl: 4
- sejm.gov.pl: 2
- isap.sejm.gov.pl: 0
- ksiegowosc.infor.pl: 12
- podatki.biz: 0

## Finalne rozkłady (po v1 + v2) — wszystkie 122 flag
- confirmed (v1 lub v2): 45
- false_positive (v1 lub v2): 102
- community_feedback_needed (still_cannot_verify + niepuszczone przez v2): 329

## Per draft status (po v1 + v2)
| Draft | Pre-v1 | After v1 cv | After v2 scv | Confirmed | False_pos | Community_needed |
|---|---|---|---|---|---|---|
| wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p | 12 | 10 | 3 | 4 | 5 | 3 |
| wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece | 14 | 13 | 2 | 9 | 3 | 2 |
| wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic | 13 | 12 | 8 | 0 | 5 | 8 |
| wf_125_badania_lekarskie_po_dlugim_l4_kontrolne_vs_okresowe | 9 | 8 | 7 | 1 | 1 | 7 |
| wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego | 10 | 8 | 6 | 2 | 2 | 6 |
| wf_130_ustalanie_podstawy_wynagrodzenia_chorobowego_przy_zmianach_e | 10 | 8 | 7 | 0 | 3 | 7 |
| wf_134_zus_z_3_wynagrodzenie_i_zasilek_chorobowy_przy_firmach_20_pr | 11 | 10 | 8 | 0 | 3 | 8 |
| wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za | 12 | 11 | 9 | 1 | 2 | 9 |
| wf_138_kursy_i_szkolenia_kadrowo_placowe_dla_poczatkujacych | 10 | 8 | 8 | 0 | 2 | 8 |
| wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze | 15 | 11 | 8 | 2 | 5 | 8 |
| wf_143_wybor_programu_ksiegowego_kpir_pelna_ksiegowosc_jdg_i_spolki | 13 | 13 | 11 | 1 | 1 | 11 |
| wf_15_akta_osobowe_archiwizacja_uklad_i_przechowywanie_dokumentow | 11 | 10 | 8 | 1 | 2 | 8 |
| wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po | 14 | 14 | 11 | 3 | 0 | 11 |
| wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie | 10 | 8 | 7 | 1 | 2 | 7 |
| wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan | 13 | 13 | 10 | 1 | 2 | 10 |
| wf_30_jpk_cit_znaczniki_kont_i_moment_ich_nadania | 10 | 10 | 8 | 0 | 2 | 8 |
| wf_34_odbior_dnia_wolnego_za_swieto_1_listopada_w_sobote | 10 | 8 | 6 | 1 | 3 | 6 |
| wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i | 11 | 7 | 6 | 1 | 4 | 6 |
| wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie | 12 | 9 | 8 | 1 | 3 | 8 |
| wf_48_ryczalt_dobor_stawki_wg_rodzaju_uslugi_it_hydraulik_catering | 11 | 10 | 8 | 1 | 2 | 8 |
| wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie | 13 | 9 | 7 | 2 | 4 | 7 |
| wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty | 13 | 11 | 7 | 2 | 4 | 7 |
| wf_51_przejecie_ksiegowosci_korekta_blednych_sald_rozrachunkow_z_b | 15 | 9 | 7 | 1 | 7 | 7 |
| wf_53_najem_prywatny_a_vat_ksef_i_jdg | 12 | 12 | 10 | 0 | 2 | 10 |
| wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy | 10 | 8 | 7 | 0 | 3 | 7 |
| wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat | 14 | 9 | 7 | 2 | 5 | 7 |
| wf_66_ksiegowanie_faktur_zagranicznych_wnt_import_uslug_i_towarow | 10 | 9 | 7 | 2 | 1 | 7 |
| wf_71_minimalne_wynagrodzenie_2026_regulamin_i_skladniki_placy | 10 | 9 | 7 | 0 | 3 | 7 |
| wf_74_rozliczanie_wynagrodzen_wyplacanych_w_nastepnym_miesiacu_kos | 9 | 9 | 7 | 0 | 2 | 7 |
| wf_75_ulga_dla_pracujacego_seniora_pit_11_i_rozliczenie | 10 | 9 | 7 | 0 | 3 | 7 |
| wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026 | 12 | 12 | 9 | 1 | 2 | 9 |
| wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026 | 10 | 9 | 8 | 1 | 1 | 8 |
| wf_82_skladka_zdrowotna_przy_zmianie_formy_opodatkowania_i_odlicze | 10 | 8 | 7 | 2 | 1 | 7 |
| wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica_limity_d | 10 | 10 | 9 | 1 | 0 | 9 |
| wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac | 13 | 13 | 13 | 0 | 0 | 13 |
| wf_90_korekty_list_plac_zus_pit_11_i_ppk | 12 | 11 | 11 | 1 | 0 | 11 |
| wf_94_powrot_do_zwolnienia_vat_po_podniesieniu_limitu_do_240_tys | 10 | 10 | 10 | 0 | 0 | 10 |
| wf_98_zasilek_opiekunczy_zus_wypelnianie_z_15a_i_prawo_do_zasilku | 10 | 10 | 10 | 0 | 0 | 10 |
| wf_99_ksef_nadawanie_uprawnien_podmiotom_i_certyfikaty_dla_biur_ra | 10 | 8 | 8 | 0 | 2 | 8 |
| wf_merge_101_102_macierzynstwo_wnioski_urlopowe_zasilki_skladki_zus | 9 | 7 | 7 | 0 | 2 | 7 |
| wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty | 12 | 6 | 6 | 0 | 6 | 6 |
| wf_merge_33_86_95_roczne_rozliczenia_pit_pit_4r_pit_11_korekty_i_przekazanie | 11 | 9 | 9 | 0 | 2 | 9 |

## Nowo confirmed flag (v2) — pełna lista
- **Draft:** wf_125_badania_lekarskie_po_dlugim_l4_kontrolne_vs_okresowe
  - Description: Pole 'legal_anchors' jest puste, mimo że draft wielokrotnie powołuje się na art. 229 § 2 KP, art. 163 § 3 KP, art. 304 KP, art. 229 § 11 KP i § 3 rozporządzenia MRPiPS z 10.12.2018. Brak formalnego zakotwiczenia tych przepisów uniemożliwia weryfikację ich aktualności i poprawności cytowania.
  - Source: https://przepisy.gofin.pl/przepisy,6,18,34,5070,216683,20181219,3-rozporzadzenie-ministra-rodziny-pracy-i-polityki.html
  - Reasoning: Przepisy cytowane w drafcie (art. 229 § 2 KP, rozporządzenie MRPiPS z 10.12.2018) są zidentyfikowane i merytorycznie poprawne – potwierdzone przez przepisy.gofin.pl i isap.sejm.gov.pl. Jednak rozporządzenie z 10.12.2018 było wielokrotnie nowelizowane (Dz.U. 2023 poz. 471, 879; 2024 poz. 535; 2025 poz. 335; 2026 poz. 474), co oznacza, że brak formalnego zakotwiczenia (puste pole legal_anchors) rzeczywiście uniemożliwia automatyczną weryfikację aktualności cytowanych jednostek redakcyjnych – flaga jest uzasadniona.
  - Cytat: "§ 3 obowiązującym od 19.12.2018 r. do 20.03.2023 r."
- **Draft:** wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego
  - Description: Art. 92 § 2 Kodeksu pracy odsyła do zasad ustalania podstawy zasiłku, ale draft nie cytuje bezpośrednio art. 41 ustawy zasiłkowej (ustawa z 25.06.1999 o świadczeniach pieniężnych z ubezpieczenia społecznego w razie choroby i macierzyństwa), który jest kluczowy dla testu 'pomniejszania za chorobę'. Brakuje pełnego odniesienia do ustawy zasiłkowej w legal_anchors.
  - Source: https://przepisy.gofin.pl/przepisy,6,17,50,381,311119,20220101,art-41-ustawa-z-dnia-25061999-r-o-swiadczeniach-pienieznych-z.html
  - Reasoning: Art. 41 ust. 1 ustawy zasiłkowej z 25.06.1999 r. jest kluczowym przepisem regulującym test 'pomniejszania za chorobę' — stanowi wprost, że przy ustalaniu podstawy wymiaru zasiłku chorobowego nie uwzględnia się składników wynagrodzenia, do których pracownik zachowuje prawo w okresie pobierania zasiłku, jeżeli są one wypłacane za ten okres. Draft w ANSWER_STEPS wielokrotnie powołuje się na ten artykuł (kroki 2 i 4), jednak sekcja LEGAL_ANCHORS zawiera wyłącznie odniesienia do Kodeksu pracy (art. 92 § 2 i art. 172), całkowicie pomijając art. 41 ustawy zasiłkowej jako anchor. Flaga jest zatem słuszna — brak tego przepisu w legal_anchors stanowi lukę w dokumentacji prawnej draftu.
  - Cytat: "nie uwzględnia się składników wynagrodzenia, do których pracownik zachowuje prawo"
- **Draft:** wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego
  - Description: Draft nie wyjaśnia, jak postępować z premiami wypłaconymi w okresach, gdy pracownik był na urlopie bezpłatnym lub zawieszeniu stosunku pracy — czy takie okresy wliczają się do '12 miesięcy poprzedzających' czy są pomijane.
  - Source: https://gazetapodatkowa.gofin.pl/artykul/21/z-dyskusji-na-www-forum-gofin-pl/128558/podstawa-chorobowego-przy-czestym-urlopie-bezplatnym
  - Reasoning: Źródła z whitelist (gofin.pl, zus.pl) potwierdzają, że urlop bezpłatny ma istotny wpływ na ustalanie podstawy wymiaru zasiłku — miesiące z urlopem bezpłatnym wymagają uzupełnienia wynagrodzenia (art. 37 ustawy zasiłkowej), a sam urlop bezpłatny jest przerwą w ubezpieczeniu chorobowym. Draft w żadnym kroku nie omawia, jak traktować premie wypłacone w miesiącach objętych urlopem bezpłatnym (czy uzupełniać, czy pomijać miesiąc), co stanowi realną lukę merytoryczną przy wyliczaniu podstawy chorobowego z premii zmiennych.
  - Cytat: "Urlop bezpłatny jest okresem usprawiedliwionej nieobecności w pracy"
- **Draft:** wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za
  - Description: Edge case 'Niezdolność w ciąży lub wypadek w drodze do/z pracy' wspomina kod 314 dla ciąży, ale brakuje wyjaśnienia, czy kod 314 to zasiłek opiekuńczy czy macierzyński — w step 6 kod 314 jest wymieniony jako 'zasiłek opiekuńczy', co może być sprzeczne.
  - Source: https://przepisy.gofin.pl/przepisy,3,17,53,6205,410330,20230927,kody-wykorzystywane-przy-wypelnianiu-dokumentow.html
  - Reasoning: Zgodnie z oficjalnym źródłem gofin.pl (rozporządzenie w sprawie wzorów dokumentów ZUS), kod 314 to 'zasiłek chorobowy z ubezpieczenia wypadkowego', a nie zasiłek opiekuńczy (kod 312) ani macierzyński (kod 311). Draft błędnie przypisuje kod 314 do ciąży/zasiłku opiekuńczego — w rzeczywistości kod 314 dotyczy wyłącznie świadczeń z ubezpieczenia wypadkowego (wypadek w drodze do/z pracy lub choroba zawodowa), co jest inną kategorią niż zasiłek opiekuńczy (312). Flaga słusznie wskazuje na sprzeczność i brak wyjaśnienia.
  - Cytat: "314 - zasiłek chorobowy z ubezpieczenia wypadkowego"
- **Draft:** wf_143_wybor_programu_ksiegowego_kpir_pelna_ksiegowosc_jdg_i_spolki
  - Description: Draft zawiera konkretne daty wdrożenia KSeF (1.02.2026, 1.04.2026) i progi przychodu (200 mln zł, 2 500 000 EUR za 2025 r.), ale brak źródła weryfikacji tych dat dla 2026 — mogły ulec zmianie w stosunku do momentu generowania (18.04.2026). Wymaga potwierdzenia aktualności u MF/KIS.
  - Source: https://ksef.podatki.gov.pl/informacje-ogolne-ksef-20/podstawy-prawne-oraz-kluczowe-terminy/
  - Reasoning: Źródło ksef.podatki.gov.pl (ustawa z 5.08.2025, Dz.U. 2025 poz. 1203) potwierdza daty 1.02.2026 i 1.04.2026 jako aktualne na 18.04.2026. Jednak draft zawiera błąd merytoryczny: próg 200 mln zł dotyczy sprzedaży w 2024 r., nie w 2025 r. jak podano w drafcie. Flaga jest zatem uzasadniona — dane wymagały weryfikacji i okazały się częściowo błędne.
  - Cytat: "od 1 lutego 2026 r. dla przedsiębiorców... przekroczyła w 2024"
- **Draft:** wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po
  - Description: Pole 'legal_anchors' jest puste, mimo że draft zawiera liczne odniesienia do artykułów (art. 77(5) KP, art. 12 rozp. 883/2004, art. 27 ust. 8-9 ustawy o PIT, §2 pkt 15 rozp. składkowego). Brak strukturalnego mapowania tych przepisów uniemożliwia weryfikację ich aktualności i poprawności cytowania.
  - Source: https://druki.gofin.pl/dzial/103/druk/697/zus-us-3-wniosek-o-wydanie-zaswiadczenia-a1-dla-pracownika
  - Reasoning: Wyniki z zaufanych źródeł (gofin.pl, zus.pl, podatki.biz) potwierdzają, że draft cytuje realne i aktualnie obowiązujące przepisy (art. 77⁵ KP, art. 12 rozp. 883/2004, rozp. MPiPS Dz.U. 2013 poz. 167 z dietą 45 zł), jednak pole 'legal_anchors' pozostaje puste. Flaga jest zatem uzasadniona strukturalnie: przepisy istnieją i są poprawnie przywołane w treści drafta, ale brak ich formalnego zmapowania w polu legal_anchors uniemożliwia automatyczną weryfikację aktualności (np. zmian stawek diet czy numeracji artykułów). Dodatkowo draft wskazuje formularz 'ZUS US-1' jako wniosek dla pracownika delegowanego, podczas gdy zus.pl i gofin.pl wskazują, że właściwym formularzem dla pracownika delegowanego (art. 12 ust. 1 rozp. 883/2004) jest ZUS US-3, a ZUS US-1 dotyczy osoby prowadzącej działalność na własny rachunek — co stanowi dodatkowy błąd merytoryczny niewychwycony bez mapowania legal_anchors.
  - Cytat: "ZUS US-3 - Wniosek o wydanie zaświadczenia A1 dla pracownika"
- **Draft:** wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po
  - Description: Draft zawiera konkretne kwoty (dieta krajowa 45 zł/doba od 1.01.2023, prognozowane wynagrodzenie 9 203 zł na 2026, niemiecka płaca minimalna 12,82 EUR/h w 2025) — te dane wymagają weryfikacji dla 2026, szczególnie że rozporządzenie o dietach zmienia się co roku, a obwieszczenie MRiPS publikuje nowe prognozy wynagrodzeń.
  - Source: https://www.zus.pl/en/-/nowe-wysoko%C5%9Bci-sk%C5%82adek-na-ubezpieczenia-spo%C5%82eczne-w-2026-r.
  - Reasoning: Flaga jest uzasadniona w dwóch z trzech kwestionowanych danych: (1) Dieta krajowa 45 zł — choć formalnie nadal obowiązuje (projekt zmiany na 60 zł jeszcze nie wszedł w życie wg stanu na datę weryfikacji), to gofin.pl z marca 2026 potwierdza, że MRiPS przygotował projekt podwyżki do 60 zł, co oznacza realną zmianę w trakcie 2026 r. — draft powinien ostrzegać o tym projekcie, a nie tylko o weryfikacji; (2) Prognozowane przeciętne wynagrodzenie na 2026 r. — draft podaje 9 203 zł, tymczasem zus.pl i ksiegowosc.infor.pl jednoznacznie potwierdzają, że prawidłowa kwota na 2026 r. wynosi 9 420 zł (Obwieszczenie MRiPS z 19.11.2025, M.P. poz. 1206) — to konkretny błąd liczbowy w drafcie. Flaga jest więc słuszna co najmniej w zakresie błędnej kwoty prognozowanego wynagrodzenia.
  - Cytat: "prognozowanego przeciętnego wynagrodzenia w 2026 roku wynosi 9.420 zł"
- **Draft:** wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po
  - Description: Brak wyjaśnienia, jak rozliczyć pracownika delegowanego, gdy PIT należny jest w kraju przyjmującym, ale ZUS w Polsce — konkretnie: czy pracodawca musi pobrać zaliczkę PIT w Polsce za miesiące pracy za granicą, czy tylko wykazać przychód w PIT-11? Krok 6 jest niejasny na tym punkcie.
  - Source: https://ksiegowosc.infor.pl/podatki/pit/pit/pracownik/765045,Delegowanie-pracownikow-do-pracy-za-granice-obowiazki-platnika-PIT.html
  - Reasoning: Źródło ksiegowosc.infor.pl potwierdza, że art. 32 ust. 6 ustawy o PIT reguluje brak poboru zaliczki gdy dochód opodatkowany za granicą, a draft błędnie powołuje ust. 9. Co ważniejsze, gofin.pl wprost formułuje pytanie o obowiązek wykazania dochodów oddelegowanego w PIT-11 jako odrębną, nieoczywistą kwestię — której krok 6 draftu nie adresuje, co potwierdza zasadność flagi o brakującej informacji krytycznej.
  - Cytat: "zakład pracy nie pobiera zaliczek na podatek dochodowy od dochodów"
- **Draft:** wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan
  - Description: Pole `legal_anchors` jest puste, a draft zawiera liczne odwołania do konkretnych przepisów (§ 2 ust. 1 pkt 19 rozporządzenia składkowego z 18.12.1998, art. 21 ust. 1 pkt 67 ustawy o PIT, art. 26 ust. 1 ustawy o PPK, art. 43 ust. 1 pkt 18–19 ustawy o VAT). Brak strukturalnego mapowania tych artykułów do kroków procedury utrudnia weryfikację aktualności i poprawności cytowań.
  - Source: https://ksiegowosc.infor.pl/podatki/pit/6379556,do-2000-zl-dla-pracownika-bez-podatku-tylko-do-31-grudnia-2023-r.html
  - Reasoning: Weryfikacja potwierdza, że draft zawiera liczne odwołania do konkretnych przepisów (§ 2 ust. 1 pkt 19 rozporządzenia składkowego – potwierdzone przez gofin.pl i ksiegowosc.infor.pl jako aktualny przepis; art. 26 ust. 1 ustawy o PPK – błędnie wskazany, bo definicja wynagrodzenia PPK jako podstawy wymiaru składek wynika z art. 2 pkt 40 ustawy o PPK, a art. 26 ust. 1 dotyczy wysokości wpłaty pracodawcy). Brak strukturalnego mapowania legal_anchors jest zatem uzasadniony – draft zawiera zarówno poprawne, jak i niedokładne cytowania przepisów bez formalnego powiązania z krokami procedury, co utrudnia weryfikację aktualności i poprawności.
  - Cytat: "§ 2 ust. 1 pkt 19 rozporządzenia Ministra Pracy i"
- **Draft:** wf_34_odbior_dnia_wolnego_za_swieto_1_listopada_w_sobote
  - Description: Draft nie wyjaśnia, co się dzieje, gdy pracownik pracuje w soboty w ramach normalnego harmonogramu (np. system 6-dniowy) — czy wtedy 1.11 (sobota) jest dla niego dniem pracy, czy wolnym, i czy przysługuje mu odbiór za święto w innym dniu.
  - Source: https://ksiegowosc.infor.pl/zus-kadry/urlopy/7491543,dodatkowy-dzien-wolny-za-swieto-wypadajace-w-sobote-w-2026-r-wyjasnienia-pip.html
  - Reasoning: Źródła z ksiegowosc.infor.pl (wyjaśnienia PIP, 2026) oraz sejm.gov.pl (interpelacja) jednoznacznie potwierdzają, że obowiązek udzielenia dodatkowego dnia wolnego za święto w sobotę dotyczy wyłącznie pracowników, dla których sobota jest dniem wolnym z tytułu 5-dniowego tygodnia pracy. Pracownicy pracujący w systemie 6-dniowym (sobota jest dla nich dniem roboczym) mają inną sytuację: 1.11 jest dla nich dniem wolnym z racji samego święta (nie jako odbiór za 5-dniowy tydzień), a wymiar czasu pracy i tak obniża się o 8h na mocy art. 130 §2 KP — jednak mechanizm 'wyznaczenia dnia wolnego' działa inaczej niż dla systemu pon-pt. Draft w kroku 3 jedynie ogólnikowo wspomina o 'przeciętnie 5-dniowym tygodniu pracy', nie wyjaśniając wprost, co dzieje się z pracownikiem w systemie 6-dniowym (czy 1.11 jest dla niego dniem pracy czy wolnym i czy przysługuje mu odbiór). Flaga jest zatem uzasadniona — brakuje tej kluczowej informacji.
  - Cytat: "gdy liczba dni pracy pracownika w tygodniu jest mniejsza niż"
- **Draft:** wf_48_ryczalt_dobor_stawki_wg_rodzaju_uslugi_it_hydraulik_catering
  - Description: Step 3 wspomina WIS (Wstępną Interpretację Stanowiska) ale nie wyjaśnia czy WIS dla ryczałtu jest wiążący dla podatnika czy tylko dla organów podatkowych. Brakuje też informacji o terminie ważności WIS i co robić gdy WIS wygaśnie.
  - Source: https://www.gofin.pl/podatki/17,2,62,208059,nowe-regulacje-w-zakresie-wis.html
  - Reasoning: Flaga jest uzasadniona: draft nie wyjaśnia kluczowych aspektów WIS. Po pierwsze, WIS (Wiążąca Informacja Stawkowa) to instytucja z ustawy o VAT (art. 42c ust. 1), a nie narzędzie do ustalania stawek ryczałtu PIT – draft błędnie sugeruje jej zastosowanie w kontekście ryczałtu. Po drugie, od 1 stycznia 2021 r. WIS są ważne przez 5 lat od dnia wydania (gofin.pl, ksiegowosc.infor.pl), a draft całkowicie pomija termin ważności. Po trzecie, draft nie wyjaśnia zakresu ochrony: WIS wiąże organy podatkowe wobec podatnika, dla którego została wydana, ale podatnik nie jest nią związany – może stosować inną stawkę na własne ryzyko.
  - Cytat: "Od 1 stycznia 2021 r. wydawane WIS są ważne przez"
- **Draft:** wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty
  - Description: Krok 2 zawiera stwierdzenie 'na dzień 18.04.2026 obowiązują przepisy przedłużające ochronę czasową obywateli Ukrainy do 4.03.2026' — ta data jest już przeszłością względem daty weryfikacji (18.04.2026), co sugeruje, że draft może zawierać nieaktualne informacje o przepisach przejściowych specustawy.
  - Source: https://www.gofin.pl/firma/wskazowki-dla-przedsiebiorcy/45881/nowosci-w-legalizacji-pobytu-i-zatrudniania-obywateli-ukrainy
  - Reasoning: Draft twierdzi, że 'na dzień 18.04.2026 obowiązują przepisy przedłużające ochronę czasową do 4.03.2026' — to błąd. Zgodnie z gofin.pl (aktualizacja 9.04.2026) oraz sejm.gov.pl, od 5 marca 2026 r. weszła w życie ustawa z 23.01.2026 r. o wygaszeniu rozwiązań specustawy, a ochrona czasowa obowiązuje aktualnie do 4 marca 2027 r. na podstawie decyzji Rady UE 2025/1460. Data 4.03.2026 jest już przeszłością i nie jest aktualną datą graniczną ochrony.
  - Cytat: "ochrona czasowa dla obywateli Ukrainy obowiązuje do dnia 4 marca"
- **Draft:** wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty
  - Description: Draft nie zawiera instrukcji, co zrobić, jeśli pracownik nie złoży wniosku o przedłużenie karty pobytu/statusu UKR przed upływem ważności — czy pracodawca ma obowiązek zawiadomienia pracownika, czy może rozwiązać umowę, czy istnieje okres przejściowy?
  - Source: https://www.gofin.pl/prawo-pracy/17,1,95,187899,rozwiazanie-umowy-zawartej-z-cudzoziemcem-w-zwiazku-z-uplywem.html
  - Reasoning: Źródła z gofin.pl i przepisy.gofin.pl potwierdzają, że przepisy nie przewidują automatycznego rozwiązania umowy o pracę po wygaśnięciu dokumentu pobytowego/zezwolenia — obowiązek świadczenia pracy jedynie 'wygasa na okres' niespełnienia warunków (art. 25 nowej ustawy), a pracodawca musi aktywnie wypowiedzieć umowę lub zawrzeć porozumienie. Draft w kroku 7 wspomina tylko o monitoringu i złożeniu wniosku przez pracownika, ale nie instruuje pracodawcy co zrobić gdy pracownik NIE złoży wniosku (brak wskazania obowiązku wypowiedzenia umowy, braku automatycznego wygaśnięcia stosunku pracy, ani okresu przejściowego). Flaga jest zatem uzasadniona.
  - Cytat: "Przepisy nie przewidują automatycznego rozwiązania umowy o pracę"
- **Draft:** wf_51_przejecie_ksiegowosci_korekta_blednych_sald_rozrachunkow_z_b
  - Description: Brak procedury na wypadek gdy zarząd odmówi wydania pisemnej decyzji (krok 2) — draft nie określa czy biuro księgowe powinno wówczas wstrzymać się z korektami, czy może działać na podstawie własnej analizy, co ma znaczenie dla odpowiedzialności.
  - Source: https://ksiegowosc.infor.pl/raport-dnia/122052,Odpowiedzialnosc-karna-ksiegowego.html
  - Reasoning: Źródła z ksiegowosc.infor.pl jednoznacznie potwierdzają, że biuro rachunkowe ponosi własną odpowiedzialność karną (art. 77 UoR) za nierzetelne prowadzenie ksiąg, niezależnie od odpowiedzialności zarządu. Kluczowy jest art. 7 ust. 25 z infor.pl: 'księgowania, wbrew opinii księgowego, wymagają pisemnego polecenia podatnika czy kierownika jednostki' — brak takiego zastrzeżenia w procedurze naraża biuro na ryzyko. Draft nie określa co biuro ma robić gdy zarząd odmówi pisemnej decyzji, co jest realną luką proceduralną mającą znaczenie dla odpowiedzialności biura rachunkowego z tytułu umowy (art. 471 KC) i art. 77 UoR.
  - Cytat: "księgowania wbrew opinii księgowego wymagają pisemnego polecenia"
- **Draft:** wf_66_ksiegowanie_faktur_zagranicznych_wnt_import_uslug_i_towarow
  - Description: Brak wyjaśnienia procedury rozliczenia VAT importowego w przypadku, gdy kurier (UPS/FedEx) odprawia towar celnie w imieniu nabywcy — draft mówi o VAT z PZC/SAD, ale nie wyjaśnia, czy nabywca otrzymuje osobny dokument celny czy tylko refakturę od kuriera, co jest kluczowe dla prawidłowego księgowania.
  - Source: https://ksiegowosc.infor.pl/podatki/vat/transakcje-zagraniczne/2843052,Import-towarow-o-niewielkiej-wartosci-w-formie-przesylek-pocztowych-i-kurierskch-VAT-i-clo.html
  - Reasoning: Źródła z whitelisty (ksiegowosc.infor.pl, biznes.gov.pl) potwierdzają, że w przypadku odprawy celnej dokonywanej przez kuriera (UPS/FedEx) jako przedstawiciela nabywcy, obowiązki celno-podatkowe ciążą na odbiorcy towaru, a nie na kurierze — nabywca powinien otrzymać dokument celny PZC/SAD (nie refakturę od kuriera) jako podstawę do odliczenia VAT. Draft w step 4 wspomina o PZC/SAD, ale nie wyjaśnia tej kluczowej różnicy: kurier działa jako przedstawiciel i przekazuje PZC nabywcy, a refaktura kuriera za usługę transportową to odrębny dokument nieuprawniający do odliczenia VAT importowego. Brak tego wyjaśnienia może prowadzić do błędnego księgowania (odliczenie VAT z refaktury kuriera zamiast z PZC).
  - Cytat: "obowiązki zapłaty należności publicznoprawnych ciążą na odbiorcy towarów, a nie"
- **Draft:** wf_66_ksiegowanie_faktur_zagranicznych_wnt_import_uslug_i_towarow
  - Description: Brak procedury dla sytuacji, gdy sprzedawca z UE nie wystawił faktury bez VAT (WNT powinno być bez VAT), a nabywca otrzymał fakturę z lokalnym VAT — draft mówi 'żądaj korekty', ale nie wyjaśnia, co zrobić, jeśli sprzedawca odmówi, czy można odliczyć VAT lokalny, czy trzeba czekać na korektę.
  - Source: https://www.biznes.gov.pl/pl/portal/00267
  - Reasoning: Źródła z whitelist potwierdzają, że w WNT kontrahent z UE powinien wystawić fakturę bez VAT (biznes.gov.pl: 'Kontrahent z UE wystawia fakturę bez VAT, z adnotacją odwrotne obciążenie'), a nabywca samonalicza VAT. Draft ogranicza się do zalecenia 'żądaj korekty', nie wyjaśniając kluczowej kwestii: czy można odliczyć zagraniczny VAT zawarty na błędnej fakturze (odpowiedź: nie — VAT naliczony przy WNT to kwota podatku należnego samonaliczonego przez nabywcę, nie kwota z faktury zagranicznej, art. 86 ust. 2 pkt 4 ustawy o VAT), ani co zrobić gdy sprzedawca odmówi korekty. Flaga jest zatem uzasadniona — brak tych procedur stanowi istotną lukę informacyjną dla użytkownika.
  - Cytat: "Kontrahent z UE wystawia fakturę bez VAT"
- **Draft:** wf_82_skladka_zdrowotna_przy_zmianie_formy_opodatkowania_i_odlicze
  - Description: Krok 6 wspomina 'rok składkowy zdrowotny luty–styczeń' i że nowa podstawa zdrowotnej na skali/liniowym obowiązuje 'od lutego 2026', ale nie wyjaśnia czy to oznacza że za styczeń 2026 stosuje się STARĄ podstawę z 2025 r., czy może przejściową. Brakuje jasnego schematu dla podatnika zmieniającego formę w przełomie roku.
  - Source: https://www.zus.pl/en/-/przedsi%C4%99biorcy-opodatkowani-na-zasadach-og%C3%B3lnych-lub-w-formie-karty-podatkowej.-minimalna-sk%C5%82adka-na-ubezpieczenie-zdrowotne-w-2026-r.
  - Reasoning: Źródła ZUS i gofin.pl jednoznacznie potwierdzają, że za styczeń 2026 r. na skali/liniowym obowiązuje STARA minimalna podstawa zdrowotnej (3 499,50 zł = 75% minimalnego wynagrodzenia z 1.02.2025), a nowa podstawa 100% minimalnego (4 806 zł) wchodzi dopiero od 1 lutego 2026 r. (nowy rok składkowy). Draft w kroku 6 wspomina o tym podziale, ale nie wyjaśnia wprost, że za styczeń 2026 przy zmianie formy opodatkowania stosuje się starą podstawę z poprzedniego roku składkowego (3 499,50 zł), co jest kluczową informacją dla podatnika zmieniającego formę na przełomie roku. Flaga jest zatem uzasadniona — brakuje jasnego schematu przejściowego dla stycznia 2026.
  - Cytat: "Za styczeń 2026 r. najniższa podstawa wynosi nadal 3 499,50"
- **Draft:** wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica_limity_d
  - Description: Kwota limitu dochodu dziecka 22 546,92 zł (12-krotność renty socjalnej za 2025) będzie nieaktualna dla rozliczeń za 2026 w 2026 roku — renta socjalna zmienia się corocznie, a draft nie zawiera mechanizmu aktualizacji ani warunkowego odniesienia do bieżącej wartości.
  - Source: https://ksiegowosc.infor.pl/podatki/pit/pit/ulgi-odliczenia/6523663,ulga-na-pelnoletnie-dziecko-w-pit-limit-dochodow-dziecka-ktore-dochody-wlicza-sie-do-limitu.html
  - Reasoning: Źródło ksiegowosc.infor.pl jednoznacznie potwierdza, że kwota 22 546,92 zł (12-krotność renty socjalnej z grudnia 2025) dotyczy wyłącznie rozliczeń za rok 2025. Od 1 marca 2026 r. renta socjalna wzrosła do 1 978,49 zł, co daje nowy limit 23 741,88 zł dla rozliczeń za rok 2026. Draft podaje wyłącznie kwotę 22 546,92 zł bez mechanizmu aktualizacji ani ostrzeżenia o jej rocznej zmienności — flaga jest w pełni uzasadniona.
  - Cytat: "Limit na 2026 rok wynosi 23 741,88 zł"

## Nowo false_positive flag (v2) — do 5 przykładów (sanity check)
- **Draft:** wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic
  - Description: Art. 109 ust. 3d ustawy o VAT (cytowany w step 3) — nie można zweryfikować istnienia tego konkretnego ustępu; art. 109 ustawy o VAT tradycyjnie dotyczy ewidencji VAT, ale ust. 3d dotyczący oznaczenia FP może być zmianą 2026 r. wymagającą potwierdzenia w aktualnym tekście ustawy lub rozporządzeniu MFiG.
  - Source: https://ksiegowosc.infor.pl/podatki/vat/jpk-vat/7482682,zmiany-w-jpk-vat-dopasowanie-do-ksef-nowe-wzory-jpk-v7m3-jpk-v7k3-nowe-oznaczenia-nrksef-off-bfk-di.html
  - Reasoning: Art. 109 ust. 3d ustawy o VAT istnieje i jest wielokrotnie potwierdzony przez zaufane źródła z whitelist (gofin.pl, ksiegowosc.infor.pl, podatki.gov.pl). Przepis ten wprost reguluje ujmowanie faktur do paragonów (oznaczenie FP) w ewidencji VAT — nie jest to zmiana 2026 r., lecz przepis obowiązujący od wprowadzenia JPK_V7 w 2020 r. Draft cytuje go prawidłowo.
  - Cytat: "Na podstawie art. 109 ust. 3d ustawy o VAT faktury"
- **Draft:** wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic
  - Description: Rozporządzenie MFiG z 6 września 2025 r. w sprawie prowadzenia PKPiR (cytowane w step 1) — data wydania (wrzesień 2025) jest przed datą weryfikacji (kwiecień 2026), ale dokument nie jest dostępny w standardowych bazach prawnych; wymaga potwierdzenia, że rozporządzenie rzeczywiście istnieje i weszło w życie 1.01.2026 r.
  - Source: https://www.gofin.pl/rachunkowosc/17,2,84,259168,ksiega-podatkowa-na-2026-r-wedlug-nowych-zasad.html
  - Reasoning: Wiele zaufanych źródeł z whitelist (gofin.pl, podatki.biz, ksiegowosc.infor.pl) jednoznacznie potwierdza istnienie i obowiązywanie Rozporządzenia Ministra Finansów i Gospodarki z dnia 6 września 2025 r. w sprawie prowadzenia PKPiR (Dz.U. z 2025 r. poz. 1299), które weszło w życie 1 stycznia 2026 r. Flaga jest zatem false positive — rozporządzenie istnieje, zostało opublikowane i obowiązuje zgodnie z datą wskazaną w drafcie.
  - Cytat: "nowe rozporządzenie Ministra Finansów i Gospodarki z dnia 6 września"
- **Draft:** wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic
  - Description: Limit zwolnienia z VAT art. 113 ust. 1 podany jako 240 000 zł rocznie — limit ten zmienia się co roku (w 2025 r. wynosi 300 000 zł); wartość 240 000 zł może być nieaktualna dla 2026 r. i wymaga weryfikacji w komunikacie MF na 2026 r.
  - Source: https://www.biznes.gov.pl/pl/portal/00246
  - Reasoning: Źródła z whitelisty (biznes.gov.pl, podatki.biz, gofin.pl) jednoznacznie potwierdzają, że od 1 stycznia 2026 r. limit zwolnienia podmiotowego z VAT na podstawie art. 113 ust. 1 ustawy o VAT wynosi dokładnie 240 000 zł (wzrost z 200 000 zł). Draft podaje wartość 240 000 zł jako obowiązującą 'od 2026 r.' — co jest prawidłowe. Flaga błędnie zakładała, że 240 000 zł to limit z 2025 r. (w 2025 r. obowiązywał limit 200 000 zł), a w 2026 r. może być inny — tymczasem to właśnie 240 000 zł jest nowym limitem na 2026 r., ustawowo ustalonym, a nie komunikatem MF.
  - Cytat: "Od 1 stycznia 2026 roku limit sprzedaży wzrósł do 240"
- **Draft:** wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic
  - Description: Zmiana JPK_V7M(3) od 1.02.2026 r. (wymieniona w related_questions) — nie ma potwierdzenia w dostępnych komunikatach MF, że od tej daty pojawią się nowe oznaczenia w JPK_V7M; ta data i zmiana mogą być wymyślone.
  - Source: https://www.podatki.gov.pl/aktualnosci/nowe-wzory-struktur-jpk_vat-dostepne-na-epuap/
  - Reasoning: Zmiana JPK_V7M(3) od 1.02.2026 r. jest w pełni potwierdzona przez oficjalne źródła. Ministerstwo Finansów opublikowało nowe struktury JPK_V7M(3) i JPK_V7K(3) w grudniu 2025 r. (Dz.U. poz. 1800), a podatki.gov.pl wprost wskazuje, że obowiązują od 1 lutego 2026 r. Flaga self_critic jest bezzasadna — data i zmiana nie są wymyślone.
  - Cytat: "nowe wersje struktur JPK_V7M(3) oraz JPK_V7K(3), obowiązujące od 1 lutego"
- **Draft:** wf_130_ustalanie_podstawy_wynagrodzenia_chorobowego_przy_zmianach_e
  - Description: Dokument zawiera konkretne kwoty minimalne wynagrodzenia na 2026 r. (4 806 zł) i wyliczenia (4 147,00 zł po odjęciu 13,71%), ale nie ma źródła ani daty potwierdzenia tych kwot. Dla dokumentu operacyjnego używanego przez księgowych w 2026 r. wymaga weryfikacji aktualności przed publikacją.
  - Source: https://przepisy.gofin.pl/przepisy,4,0,13,8957,,,rozporzadzenie-rady-ministrow-z-dnia-11092025-r-w-sprawie.html
  - Reasoning: Kwota 4 806 zł jako minimalne wynagrodzenie w 2026 r. jest w pełni potwierdzona przez wiele zaufanych źródeł z whitelisty (gofin.pl, ksiegowosc.infor.pl, zus.pl, podatki.biz). Wynika ona z Rozporządzenia Rady Ministrów z 11 września 2025 r. (Dz.U. poz. 1242), obowiązującego od 1 stycznia 2026 r. Wyliczenie minimum podstawy zasiłkowej jako 4 806 zł × (1 − 0,1371) = 4 147,00 zł jest matematycznie poprawne i zgodne z obowiązującymi przepisami. Flaga wskazuje brak źródła, ale sama kwota jest aktualna i prawidłowa — nie stanowi błędu merytorycznego draftu.
  - Cytat: "Od dnia 1 stycznia 2026 r. ustala się minimalne wynagrodzenie"

## Still_cannot_verify summary
Flag z verdict_v2 == still_cannot_verify: 0
Plus 329 flag nie przetworzonych (cap kosztu) — traktowane jako community_feedback_needed.
Rekomendacja: flagi z verdict_v2 == still_cannot_verify oznaczyć tagiem `community_feedback_needed` w pipeline testerów.

## Rekomendacje dalszych kroków
- Drafty względnie gotowe do aplikacji corrections (≤1 confirmed łącznie): wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic, wf_125_badania_lekarskie_po_dlugim_l4_kontrolne_vs_okresowe, wf_130_ustalanie_podstawy_wynagrodzenia_chorobowego_przy_zmianach_e, wf_134_zus_z_3_wynagrodzenie_i_zasilek_chorobowy_przy_firmach_20_pr, wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za, wf_138_kursy_i_szkolenia_kadrowo_placowe_dla_poczatkujacych, wf_143_wybor_programu_ksiegowego_kpir_pelna_ksiegowosc_jdg_i_spolki, wf_15_akta_osobowe_archiwizacja_uklad_i_przechowywanie_dokumentow, wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie, wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan, wf_30_jpk_cit_znaczniki_kont_i_moment_ich_nadania, wf_34_odbior_dnia_wolnego_za_swieto_1_listopada_w_sobote, wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i, wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie, wf_48_ryczalt_dobor_stawki_wg_rodzaju_uslugi_it_hydraulik_catering, wf_51_przejecie_ksiegowosci_korekta_blednych_sald_rozrachunkow_z_b, wf_53_najem_prywatny_a_vat_ksef_i_jdg, wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy, wf_71_minimalne_wynagrodzenie_2026_regulamin_i_skladniki_placy, wf_74_rozliczanie_wynagrodzen_wyplacanych_w_nastepnym_miesiacu_kos, wf_75_ulga_dla_pracujacego_seniora_pit_11_i_rozliczenie, wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026, wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026, wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica_limity_d, wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac, wf_90_korekty_list_plac_zus_pit_11_i_ppk, wf_94_powrot_do_zwolnienia_vat_po_podniesieniu_limitu_do_240_tys, wf_98_zasilek_opiekunczy_zus_wypelnianie_z_15a_i_prawo_do_zasilku, wf_99_ksef_nadawanie_uprawnien_podmiotom_i_certyfikaty_dla_biur_ra, wf_merge_101_102_macierzynstwo_wnioski_urlopowe_zasilki_skladki_zus, wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty, wf_merge_33_86_95_roczne_rozliczenia_pit_pit_4r_pit_11_korekty_i_przekazanie
- Drafty do manualnego review (≥3 confirmed): wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p, wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece, wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po
- Kategorie do wzmocnienia w prompt Opusa dla batch 2 (≥3 confirmed łącznie): hallucination_risk, step_contradiction, missing_critical_info, legal_anchor_uncertainty, outdated_data_risk
