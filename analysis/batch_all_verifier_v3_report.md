# Verifier v3 Report — Re-weryfikacja community_feedback_needed (wszystkie 42 drafty)

Data: 2026-04-18
Model: claude-sonnet-4-6
Whitelist: 12 domen (9 z v2 + eureka.mf.gov.pl, orzeczenia.nsa.gov.pl, stat.gov.pl)
Hard cap: $12.00
Koszt: $12.1491
Pool: 329 flag (final_status == community_feedback_needed po v2)
Przetworzone: 114/329
Pominięte (cap lub resume): 215
Error count: 0
Web searches: 118  |  Web fetches: 5

## Rozkład verdictów v3
- confirmed: 39/114 (34.2%)
- false_positive: 58/114 (50.9%)
- still_cannot_verify: 17/114 (14.9%)

**Resolved by v3:** 97/114 (85.1%)

## Skuteczność per domena (flagi rozstrzygnięte przez v3)
- gofin.pl: 40
- interpretacje.gofin.pl: 0
- podatki.gov.pl: 7
- zus.pl: 14
- biznes.gov.pl: 7
- sejm.gov.pl: 6
- isap.sejm.gov.pl: 0
- ksiegowosc.infor.pl: 21
- podatki.biz: 1
- eureka.mf.gov.pl: 0 **(NOWA w v3)**
- orzeczenia.nsa.gov.pl: 0 **(NOWA w v3)**
- stat.gov.pl: 1 **(NOWA w v3)**

## Wkład nowych domen (eureka / NSA / GUS)
Łącznie flag rozstrzygniętych przez nowe domeny: 1
- stat.gov.pl: 1
- orzeczenia.nsa.gov.pl: 0
- eureka.mf.gov.pl: 0

## Resolucja per typ flagi
| Type | Total | Confirmed | False_pos | Still | Resolved% |
|---|---|---|---|---|---|
| missing_critical_info | 39 | 22 | 14 | 3 | 92.3% |
| hallucination_risk | 23 | 3 | 12 | 8 | 65.2% |
| outdated_data_risk | 15 | 3 | 8 | 4 | 73.3% |
| step_contradiction | 15 | 4 | 11 | 0 | 100.0% |
| legal_anchor_uncertainty | 12 | 2 | 10 | 0 | 100.0% |
| edge_case_coverage | 10 | 5 | 3 | 2 | 80.0% |

## Finalne rozkłady po v1+v2+v3 — wszystkie 476 flag z 42 draftów
- Łącznie flag: 476
- Confirmed (v1+v2+v3): 84
- False_positive (v1+v2+v3): 160
- Community_feedback_needed (wciąż nierozstrzygnięte): 232

## Top 5 nowo confirmed flag w v3
- **Draft:** wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac
  - Type: outdated_data_risk | Severity: high
  - Description: Draft jest datowany na 2026-04-18 i zawiera stwierdzenie 'last_verified_at': '2026-04-18', ale odnosi się do przepisów 'od 1.01.2026' jako do przyszłości. Jeśli dokument jest rzeczywiście z kwietnia 2026, przepisy powinny być już w pełni obowiązujące — brak jasności, czy dane o limitach (3 lata przedawnienia, 12 miesięcy między próbami) są aktualne dla 2026+.
  - Source: https://ksiegowosc.infor.pl/zus-kadry/inne/7414860,staz-pracy-zmiany-od-2026-r-trzeba-zlozyc-wniosek-do-zus-by-uzyskac-zaswiadczenie-potwierdzajace-zlecenia-prowadzenie-firmy-czy-prace-zarobkowa-za-granica.html
  - Reasoning: Ustawa nowelizująca KP (Dz.U. 2025 poz. 1423, art. 10) weszła w życie 1.01.2026 dla sektora publicznego, a wg ZUS dla sektora prywatnego dopiero od 1.05.2026. Draft datowany 18.04.2026 traktuje przepisy jednolicie jako obowiązujące 'od 1.01.2026' bez rozróżnienia tych dwóch dat, co jest błędem merytorycznym — dla pracodawców prywatnych przepisy wchodzą w życie dopiero za 2 tygodnie od daty draftu, co draft pomija.
  - Cytat: "od 1 stycznia 2026 r. – do pracodawców będących jednostkami"
- **Draft:** wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac
  - Type: step_contradiction | Severity: high
  - Description: Krok 3 stwierdza, że prawo do nagrody za próg osiągnięty wstecznie (przed 1.01.2026) 'NIE przysługuje', ale krok 4 mówi o 3-letnim przedawnieniu z art. 291 § 1 KP bez wyraźnego wyjaśnienia, jak te dwie reguły się łączą — czy przedawnienie 'ratuje' roszczenie z okresu sprzed 1.01.2026, czy nie?
  - Source: https://przepisy.gofin.pl/przepisy,3,9,9,212,462756,20250319,art-291-295-przedawnienie-roszczen.html
  - Reasoning: Draft zawiera realną sprzeczność logiczną: krok 3 stwierdza, że prawo do nagrody 'NIE przysługuje' jeśli próg osiągnięto przed 1.01.2026, ale krok 4 wprowadza 3-letnie przedawnienie z art. 291 § 1 KP bez wyjaśnienia relacji między tymi regułami. Z art. 291 § 1 KP (potwierdzony przez gofin.pl) wynika, że przedawnienie biegnie od dnia wymagalności roszczenia — a skoro krok 3 wyklucza samo powstanie roszczenia przed 1.01.2026, to przedawnienie z kroku 4 nie może go 'ratować'. Draft nie wyjaśnia tej zależności, co tworzy rzeczywistą sprzeczność merytoryczną dla czytelnika: albo roszczenie nie powstało (krok 3) i przedawnienie jest irrelewantne, albo jednak powstało i krok 3 jest zbyt kategoryczny. Orzecznictwo SN (wyrok II PSKP 3/21 cytowany przez gofin.pl) potwierdza, że prawo do nagrody jubileuszowej powstaje dopiero od dnia wejścia w życie przepisu ją wprowadzającego, co wspiera krok 3 — ale tym samym czyni krok 4 (przedawnienie) niejasnym w kontekście roszczeń sprzed 1.01.2026.
  - Cytat: "Roszczenia ze stosunku pracy ulegają przedawnieniu z upływem 3 lat"
- **Draft:** wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac
  - Type: missing_critical_info | Severity: high
  - Description: Draft nie wyjaśnia, czy 'data nabycia prawa' to data osiągnięcia progu stażu czy data dostarczenia dokumentów ZUS. To kluczowe dla interpretacji art. 6 ustawy nowelizującej — jeśli pracownik osiągnął 20 lat w grudniu 2025, ale dokumenty dostarczył w lutym 2026, które daty się liczy?
  - Source: https://przepisy.gofin.pl/przepisy,6,18,35,471,95198,20180101,8-rozporzadzenie-rady-ministrow-z-dnia-18032009-r-w.html
  - Reasoning: Źródła z gofin.pl jednoznacznie potwierdzają, że data nabycia prawa do nagrody jubileuszowej to dzień upływu okresu uprawniającego (osiągnięcia progu stażu), a NIE dzień dostarczenia dokumentów — co wprost stwierdza §8 ust.1 rozporządzenia o pracownikach samorządowych oraz komentarze praktyków. Draft w step 2 i step 4 używa zamiennie 'dnia dostarczenia dokumentów' jako daty nabycia prawa, co jest błędem merytorycznym — flaga jest zatem uzasadniona, bo draft nie rozróżnia tych dwóch dat i może wprowadzać w błąd.
  - Cytat: "nabywa prawo do nagrody jubileuszowej w dniu upływu okresu"
- **Draft:** wf_90_korekty_list_plac_zus_pit_11_i_ppk
  - Type: missing_critical_info | Severity: high
  - Description: Brakuje procedury dla sytuacji gdy pracownik zwraca nadpłatę w ratach lub gdy pracodawca nie może potrącić całej kwoty z jednej wypłaty. Step 4 wspomina 'za pisemną zgodą' ale nie definiuje procedury gdy pracownik odmówi zgody na potrącenie.
  - Source: https://www.gofin.pl/prawo-pracy/17,2,95,197608,odliczenie-nadplaty-wynagrodzenia-z-nastepnej-wyplaty.html
  - Reasoning: Źródło gofin.pl (art. 87 KP / stanowisko GIP) potwierdza, że gdy pracownik odmawia zgody na potrącenie nadpłaty wynagrodzenia spowodowanej błędem pracodawcy, jedyną drogą jest powództwo cywilne o bezpodstawne wzbogacenie. Draft step 4 nie opisuje tej ścieżki. Dodatkowo ksiegowosc.infor.pl potwierdza, że zwrot w ratach jest dopuszczalny i wpływa na rozliczenie art. 41b PIT (odliczenie adekwatnie do każdej raty), co również nie jest opisane w drafcie.
  - Cytat: "pracodawcy pozostaje jedynie wystąpienie na drogę sądową"
- **Draft:** wf_merge_33_86_95_roczne_rozliczenia_pit_pit_4r_pit_11_korekty_i_przekazanie
  - Type: missing_critical_info | Severity: high
  - Description: Krok 6 stwierdza, że PIT-11 dla pracownika 'musi być opatrzony podpisem kwalifikowanym płatnika LUB w formie PDF z UPO' — brakuje wyjaśnienia, czy oba warianty są równoprawne, czy jeden jest preferowany; brakuje też informacji o wymaganiach dotyczących bezpieczeństwa przesyłania (szyfrowanie, hasła).
  - Source: https://ksiegowosc.infor.pl/podatki/pit/pit/pracownik/5203571,Jak-dostarczyc-pracownikowi-PIT11.html
  - Reasoning: Źródła z ksiegowosc.infor.pl (interpretacje KIS) jednoznacznie wskazują, że elektroniczne przekazanie PIT-11 pracownikowi wymaga pliku w formacie nieedytowalnym (PDF) podpisanego kwalifikowanym podpisem elektronicznym — wariant 'PDF z UPO' opisany w drafcie nie jest równoprawną alternatywą dla podpisu kwalifikowanego przy przekazaniu pracownikowi (UPO dotyczy potwierdzenia złożenia do US, nie podpisu na dokumencie dla pracownika). Draft myli dwa odrębne wymogi: podpis kwalifikowany na dokumencie dla pracownika vs. UPO jako dowód złożenia do urzędu. Brakuje też informacji o wymaganiu nieedytowalności pliku i zabezpieczeniu platformy (login/hasło), co potwierdza zasadność flagi missing_critical_info.
  - Cytat: "w pliku PDF podpisanego kwalifikowanym podpisem elektronicznym"

## Top 3 nowo false_positive flag w v3 (sanity check)
- **Draft:** wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica_limity_d
  - Type: outdated_data_risk | Severity: high
  - Description: Stawki ulgi prorodzinnej (1 112,04 zł, 2 000,04 zł, 2 700,00 zł) są podane dla 2025 roku — dla rozliczeń za 2026 będą inne, a draft nie zawiera informacji o konieczności weryfikacji aktualnych stawek.
  - Source: https://ksiegowosc.infor.pl/podatki/pit/pit/ulgi-odliczenia/6503869,ulga-na-jedno-dziecko-w-pit-zasady-i-warunki-odliczenia-w-2026-r-112-tys-zl-to-jeden-wspolny-limit-dochodow-rodzicow.html.amp
  - Reasoning: Źródła z whitelisty (ksiegowosc.infor.pl, podatki.gov.pl) jednoznacznie potwierdzają, że stawki ulgi prorodzinnej w 2026 roku są identyczne jak w 2025 roku — kwoty 92,67 zł/miesiąc (1 112,04 zł/rok) na 1. i 2. dziecko, 166,67 zł/miesiąc na 3. dziecko i 225,00 zł/miesiąc na 4. i kolejne dziecko nie zmieniły się. Artykuł z ksiegowosc.infor.pl z lutego 2026 r. wprost stwierdza, że 'w 2026 roku w zakresie ulgi na dziecko obowiązują takie same przepisy jak w roku poprzednim (2025) a także w 2024 r., 2023 r. i 2022 r.'. Stawki podane w drafcie (1 112,04 zł, 2 000,04 zł, 2 700,00 zł) są zatem aktualne i poprawne dla rozliczeń za 2025 rok składanych w 2026 roku.
  - Cytat: "w 2026 roku obowiązują takie same przepisy jak w roku"
- **Draft:** wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac
  - Type: legal_anchor_uncertainty | Severity: high
  - Description: Pole 'legal_anchors' jest puste, mimo że draft zawiera liczne odniesienia do artykułów (art. 38 ust. 2, art. 302 KP, art. 6 ustawy nowelizującej, art. 291 § 1 KP, art. 47 Karty Nauczyciela, art. 23 ustawy o pracownikach urzędów państwowych). Brak sformalizowanego listy źródeł prawnych utrudnia weryfikację i aktualizację.
  - Source: https://isap.sejm.gov.pl/isap.nsf/download.xsp/WDU20250001423/O/D20251423.pdf
  - Reasoning: Wyszukiwanie potwierdziło merytoryczną poprawność wszystkich kluczowych odniesień prawnych w drafcie: art. 302 KP (nowe brzmienie od 1.01.2026 dot. zlecenia/B2B) istnieje i pochodzi z ustawy z 26.09.2025 (Dz.U. 2025 poz. 1423, isap.sejm.gov.pl); art. 47 Karty Nauczyciela dot. nagrody jubileuszowej jest potwierdzony przez przepisy.gofin.pl; art. 291 § 1 KP (przedawnienie 3 lata) jest standardowym przepisem KP. Flaga dotyczy wyłącznie braku formalnej listy 'legal_anchors' w metadanych draftu — jest to problem struktury/formatu dokumentu, a nie błędu merytorycznego. Artykuły przywołane w drafcie są realne i aktualne, więc flaga jako sygnał o błędzie prawnym jest false positive; ewentualny problem to brak pola metadanych, nie błąd w treści.
  - Cytat: "Ustawa wchodzi w życie z dniem 1 stycznia 2026 r."
- **Draft:** wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac
  - Type: hallucination_risk | Severity: high
  - Description: Draft wielokrotnie odwołuje się do 'komentarzy HE' (HE5/1, HE3/3, HE1, HE4/3, HE1/2, HE3/1, HE2/3, HE5/1) oraz '[6]/1' i '[8]/2', które nie są zdefiniowane w dokumencie i nie ma pewności, czy odnoszą się do istniejących publikacji, orzeczeń czy stanowisk MRPiPS.
  - Source: https://isap.sejm.gov.pl/isap.nsf/download.xsp/WDU20250001423/O/D20251423.pdf
  - Reasoning: Flaga dotyczy rzekomych odwołań do niezdefiniowanych 'komentarzy HE' i oznaczeń '[6]/1', '[8]/2' — jednak w przytoczonym fragmencie drafta (ANSWER_STEPS 1–7) takich oznaczeń w ogóle nie ma. Fragment zawiera wyłącznie odwołania do konkretnych przepisów prawa (art. 302 KP, art. 291 § 1 KP, art. 38 ust. 2 ustawy o pracownikach samorządowych itp.), które są weryfikowalne i potwierdzone przez isap.sejm.gov.pl (Dz.U. 2025 poz. 1423) oraz zus.pl. Flaga hallucination_risk odnosi się prawdopodobnie do innej części dokumentu niż dostarczony fragment, co czyni ją false positive w stosunku do tego konkretnego fragmentu.
  - Cytat: "Ustawa wchodzi w życie z dniem 1 stycznia 2026 r."

## Per draft — finalny status po v3
| Draft | Total | Confirmed | False_pos | Community | % uncertain |
|---|---|---|---|---|---|
| wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze | 15 | 3 | 10 | 2 | 13% |
| wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece | 14 | 9 | 3 | 2 | 14% |
| wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic | 13 | 3 | 8 | 2 | 15% |
| wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie | 12 | 2 | 8 | 2 | 17% |
| wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego | 10 | 4 | 4 | 2 | 20% |
| wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan | 13 | 5 | 5 | 3 | 23% |
| wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p | 12 | 4 | 5 | 3 | 25% |
| wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za | 12 | 4 | 5 | 3 | 25% |
| wf_134_zus_z_3_wynagrodzenie_i_zasilek_chorobowy_przy_firmach_20_pr | 11 | 3 | 5 | 3 | 27% |
| wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i | 11 | 2 | 6 | 3 | 27% |
| wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po | 14 | 6 | 4 | 4 | 29% |
| wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie | 10 | 2 | 5 | 3 | 30% |
| wf_30_jpk_cit_znaczniki_kont_i_moment_ich_nadania | 10 | 2 | 5 | 3 | 30% |
| wf_34_odbior_dnia_wolnego_za_swieto_1_listopada_w_sobote | 10 | 1 | 6 | 3 | 30% |
| wf_125_badania_lekarskie_po_dlugim_l4_kontrolne_vs_okresowe | 9 | 3 | 3 | 3 | 33% |
| wf_48_ryczalt_dobor_stawki_wg_rodzaju_uslugi_it_hydraulik_catering | 11 | 3 | 4 | 4 | 36% |
| wf_143_wybor_programu_ksiegowego_kpir_pelna_ksiegowosc_jdg_i_spolki | 13 | 4 | 4 | 5 | 38% |
| wf_130_ustalanie_podstawy_wynagrodzenia_chorobowego_przy_zmianach_e | 10 | 0 | 6 | 4 | 40% |
| wf_51_przejecie_ksiegowosci_korekta_blednych_sald_rozrachunkow_z_b | 15 | 1 | 7 | 7 | 47% |
| wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat | 14 | 2 | 5 | 7 | 50% |
| wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty | 12 | 0 | 6 | 6 | 50% |
| wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie | 13 | 2 | 4 | 7 | 54% |
| wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty | 13 | 2 | 4 | 7 | 54% |
| wf_15_akta_osobowe_archiwizacja_uklad_i_przechowywanie_dokumentow | 11 | 2 | 3 | 6 | 55% |
| wf_138_kursy_i_szkolenia_kadrowo_placowe_dla_poczatkujacych | 10 | 2 | 2 | 6 | 60% |
| wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac | 13 | 3 | 2 | 8 | 62% |
| wf_merge_101_102_macierzynstwo_wnioski_urlopowe_zasilki_skladki_zus | 9 | 0 | 3 | 6 | 67% |
| wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy | 10 | 0 | 3 | 7 | 70% |
| wf_66_ksiegowanie_faktur_zagranicznych_wnt_import_uslug_i_towarow | 10 | 2 | 1 | 7 | 70% |
| wf_71_minimalne_wynagrodzenie_2026_regulamin_i_skladniki_placy | 10 | 0 | 3 | 7 | 70% |
| wf_75_ulga_dla_pracujacego_seniora_pit_11_i_rozliczenie | 10 | 0 | 3 | 7 | 70% |
| wf_82_skladka_zdrowotna_przy_zmianie_formy_opodatkowania_i_odlicze | 10 | 2 | 1 | 7 | 70% |
| wf_99_ksef_nadawanie_uprawnien_podmiotom_i_certyfikaty_dla_biur_ra | 10 | 0 | 3 | 7 | 70% |
| wf_merge_33_86_95_roczne_rozliczenia_pit_pit_4r_pit_11_korekty_i_przekazanie | 11 | 1 | 2 | 8 | 73% |
| wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026 | 12 | 1 | 2 | 9 | 75% |
| wf_74_rozliczanie_wynagrodzen_wyplacanych_w_nastepnym_miesiacu_kos | 9 | 0 | 2 | 7 | 78% |
| wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026 | 10 | 1 | 1 | 8 | 80% |
| wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica_limity_d | 10 | 1 | 1 | 8 | 80% |
| wf_94_powrot_do_zwolnienia_vat_po_podniesieniu_limitu_do_240_tys | 10 | 0 | 2 | 8 | 80% |
| wf_98_zasilek_opiekunczy_zus_wypelnianie_z_15a_i_prawo_do_zasilku | 10 | 0 | 2 | 8 | 80% |
| wf_53_najem_prywatny_a_vat_ksef_i_jdg | 12 | 0 | 2 | 10 | 83% |
| wf_90_korekty_list_plac_zus_pit_11_i_ppk | 12 | 2 | 0 | 10 | 83% |

## Rekomendacje
- **Ready for testers (<30% uncertainty):** 11 draftów
  - wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p, wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece, wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic, wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego, wf_134_zus_z_3_wynagrodzenie_i_zasilek_chorobowy_przy_firmach_20_pr, wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za, wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze, wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po, wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan, wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i, wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie
- **Heavy review needed (>60% uncertainty):** 17 draftów
  - wf_53_najem_prywatny_a_vat_ksef_i_jdg, wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy, wf_66_ksiegowanie_faktur_zagranicznych_wnt_import_uslug_i_towarow, wf_71_minimalne_wynagrodzenie_2026_regulamin_i_skladniki_placy, wf_74_rozliczanie_wynagrodzen_wyplacanych_w_nastepnym_miesiacu_kos, wf_75_ulga_dla_pracujacego_seniora_pit_11_i_rozliczenie, wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026, wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026, wf_82_skladka_zdrowotna_przy_zmianie_formy_opodatkowania_i_odlicze, wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica_limity_d, wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac, wf_90_korekty_list_plac_zus_pit_11_i_ppk, wf_94_powrot_do_zwolnienia_vat_po_podniesieniu_limitu_do_240_tys, wf_98_zasilek_opiekunczy_zus_wypelnianie_z_15a_i_prawo_do_zasilku, wf_99_ksef_nadawanie_uprawnien_podmiotom_i_certyfikaty_dla_biur_ra, wf_merge_101_102_macierzynstwo_wnioski_urlopowe_zasilki_skladki_zus, wf_merge_33_86_95_roczne_rozliczenia_pit_pit_4r_pit_11_korekty_i_przekazanie
