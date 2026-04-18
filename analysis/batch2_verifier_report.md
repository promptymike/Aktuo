# Batch 2 Verifier Report (v1, Sonnet vs KB)

Scope: wszystkie 42 drafty (10 batch 1 + 32 batch 2). Flagi batch 1 zachowane
z poprzedniego runu (resume via `verdict` already set). Zliczone verdicty
dotyczą wszystkich 476 flag; nowe LLM calls w tym runie dotyczą 354 flag batch 2.

---

Data: 2026-04-18
Model: claude-sonnet-4-6
Koszt: $4.3263
Flag verified: 476
Retry/error count: 0

## Rozkład verdictów
- confirmed: 10/476 (2.1%)
- false_positive: 58/476 (12.2%)
- cannot_verify: 408/476 (85.7%)

## Rozkład confirmed flag per draft (po filtracji false positives)
| Draft | Przed verifier | Confirmed | False_pos | Cannot_verify |
|---|---|---|---|---|
| wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p | 12 | 1 | 1 | 10 |
| wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece | 14 | 1 | 0 | 13 |
| wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic | 13 | 0 | 1 | 12 |
| wf_125_badania_lekarskie_po_dlugim_l4_kontrolne_vs_okresowe | 9 | 0 | 1 | 8 |
| wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego | 10 | 0 | 2 | 8 |
| wf_130_ustalanie_podstawy_wynagrodzenia_chorobowego_przy_zmianach_e | 10 | 0 | 2 | 8 |
| wf_134_zus_z_3_wynagrodzenie_i_zasilek_chorobowy_przy_firmach_20_pr | 11 | 0 | 1 | 10 |
| wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za | 12 | 0 | 1 | 11 |
| wf_138_kursy_i_szkolenia_kadrowo_placowe_dla_poczatkujacych | 10 | 0 | 2 | 8 |
| wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze | 15 | 0 | 4 | 11 |
| wf_143_wybor_programu_ksiegowego_kpir_pelna_ksiegowosc_jdg_i_spolki | 13 | 0 | 0 | 13 |
| wf_15_akta_osobowe_archiwizacja_uklad_i_przechowywanie_dokumentow | 11 | 1 | 0 | 10 |
| wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po | 14 | 0 | 0 | 14 |
| wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie | 10 | 0 | 2 | 8 |
| wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan | 13 | 0 | 0 | 13 |
| wf_30_jpk_cit_znaczniki_kont_i_moment_ich_nadania | 10 | 0 | 0 | 10 |
| wf_34_odbior_dnia_wolnego_za_swieto_1_listopada_w_sobote | 10 | 0 | 2 | 8 |
| wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i | 11 | 1 | 3 | 7 |
| wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie | 12 | 1 | 2 | 9 |
| wf_48_ryczalt_dobor_stawki_wg_rodzaju_uslugi_it_hydraulik_catering | 11 | 0 | 1 | 10 |
| wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie | 13 | 2 | 2 | 9 |
| wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty | 13 | 0 | 2 | 11 |
| wf_51_przejecie_ksiegowosci_korekta_blednych_sald_rozrachunkow_z_b | 15 | 0 | 6 | 9 |
| wf_53_najem_prywatny_a_vat_ksef_i_jdg | 12 | 0 | 0 | 12 |
| wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy | 10 | 0 | 2 | 8 |
| wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat | 14 | 1 | 4 | 9 |
| wf_66_ksiegowanie_faktur_zagranicznych_wnt_import_uslug_i_towarow | 10 | 0 | 1 | 9 |
| wf_71_minimalne_wynagrodzenie_2026_regulamin_i_skladniki_placy | 10 | 0 | 1 | 9 |
| wf_74_rozliczanie_wynagrodzen_wyplacanych_w_nastepnym_miesiacu_kos | 9 | 0 | 0 | 9 |
| wf_75_ulga_dla_pracujacego_seniora_pit_11_i_rozliczenie | 10 | 0 | 1 | 9 |
| wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026 | 12 | 0 | 0 | 12 |
| wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026 | 10 | 0 | 1 | 9 |
| wf_82_skladka_zdrowotna_przy_zmianie_formy_opodatkowania_i_odlicze | 10 | 1 | 1 | 8 |
| wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica_limity_d | 10 | 0 | 0 | 10 |
| wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac | 13 | 0 | 0 | 13 |
| wf_90_korekty_list_plac_zus_pit_11_i_ppk | 12 | 1 | 0 | 11 |
| wf_94_powrot_do_zwolnienia_vat_po_podniesieniu_limitu_do_240_tys | 10 | 0 | 0 | 10 |
| wf_98_zasilek_opiekunczy_zus_wypelnianie_z_15a_i_prawo_do_zasilku | 10 | 0 | 0 | 10 |
| wf_99_ksef_nadawanie_uprawnien_podmiotom_i_certyfikaty_dla_biur_ra | 10 | 0 | 2 | 8 |
| wf_merge_101_102_macierzynstwo_wnioski_urlopowe_zasilki_skladki_zus | 9 | 0 | 2 | 7 |
| wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty | 12 | 0 | 6 | 6 |
| wf_merge_33_86_95_roczne_rozliczenia_pit_pit_4r_pit_11_korekty_i_przekazanie | 11 | 0 | 2 | 9 |

## Top 5 najbardziej problematycznych draftów (po confirmed flag)
- wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie — 2 confirmed
- wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p — 1 confirmed
- wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece — 1 confirmed
- wf_15_akta_osobowe_archiwizacja_uklad_i_przechowywanie_dokumentow — 1 confirmed
- wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i — 1 confirmed

## Top 3 najlepsze drafty (najmniej confirmed flag)
- wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic — 0 confirmed
- wf_125_badania_lekarskie_po_dlugim_l4_kontrolne_vs_okresowe — 0 confirmed
- wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego — 0 confirmed

## Kategorie problemów (rozkład verdictów)
- missing_critical_info: 3 confirmed, 14 false_positive, 126 cannot_verify
- hallucination_risk: 3 confirmed, 4 false_positive, 70 cannot_verify
- outdated_data_risk: 0 confirmed, 9 false_positive, 64 cannot_verify
- legal_anchor_uncertainty: 2 confirmed, 17 false_positive, 49 cannot_verify
- step_contradiction: 1 confirmed, 7 false_positive, 51 cannot_verify
- edge_case_coverage: 1 confirmed, 7 false_positive, 48 cannot_verify

## High severity confirmed issues (lista pełna)
- **wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p** → Stanowisko MF z '18.03' (bez roku) dotyczące BFK dla WNT jest cytowane bez pełnej referencji. Brak możliwości weryfikacji, czy taki dokument rzeczywiście istnieje i jaka jest jego pełna treść.
  - *corrective:* Usunąć lub doprecyzować odniesienie do 'MF z 18.03' - podać pełną datę z rokiem, numer dokumentu (np. numer pisma, interpretacji ogólnej lub komunikatu), albo zastąpić sformułowaniem 'według niepotwierdzonych informacji ze szkoleń' lub całkowicie usunąć i pozostawić jedynie rekomendację złożenia zapytania do KIS.
- **wf_82_skladka_zdrowotna_przy_zmianie_formy_opodatkowania_i_odlicze** → Pole 'legal_anchors' jest puste, mimo że draft wielokrotnie powołuje się na art. 22 ust. 6bb, art. 26 ust. 1 pkt 2, art. 30c ust. 2 pkt 2 ustawy o PIT oraz 'rok składkowy zdrowotny luty–styczeń'. Brak weryfikacji czy te numery artykułów są aktualne dla 2026 i czy rzeczywiście dotyczą opisanych sytuacji.
  - *corrective:* Należy zweryfikować w aktualnym tekście ustawy o PIT (stan na 2026 r.) czy art. 22 ust. 6bb istnieje i dotyczy składek społecznych przedsiębiorcy, oraz czy art. 26 ust. 1 pkt 2 obejmuje opisaną sytuację. Jeśli art. 22 ust. 6bb nie istnieje, prawdopodobnie chodzi o art. 22 ust. 6ba lub inny ustęp. Uzupełnić pole legal_anchors o zweryfikowane referencje z podaniem pełnej nazwy ustawy i aktualnego brzmienia.
- **wf_90_korekty_list_plac_zus_pit_11_i_ppk** → Draft powołuje się na art. 39 ustawy PIT jako podstawę dla rozstrzygnięcia kiedy korygować PIT-11, ale art. 39 dotyczy obowiązku przesłania informacji PIT-11, a nie zasad jej korekty. Brakuje odniesienia do art. 41b ustawy PIT (zwrot przychodów) i art. 26 ust. 1 pkt 5 ustawy PIT (odliczenia), które są faktycznie cytowane w krokach, ale nie w legal_anchors.
  - *corrective:* Uzupełnić legal_anchors o art. 41b ustawy PIT (zwrot przychodów przez podatnika) jako kluczową podstawę dla step 4. Rozważyć dodanie art. 26 ust. 1 pkt 2 ustawy PIT (odliczenie składek ZUS). Opis roli art. 39 w legal_anchors powinien być zawężony do 'obowiązku wystawienia PIT-11' bez rozszerzania go na zasady korekty, które wynikają z innych przepisów lub praktyki administracyjnej.

## Cannot_verify summary
Flagi wymagające web_search / expert review (bo KB nie pokrywa):
- missing_critical_info: 126
- hallucination_risk: 70
- outdated_data_risk: 64
- step_contradiction: 51
- legal_anchor_uncertainty: 49
- edge_case_coverage: 48

## Rekomendacje dla następnego kroku
- Drafty do manualnego review przed pokazaniem testerom (≥3 confirmed): brak
- Drafty względnie gotowe (≤1 confirmed): wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p, wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece, wf_15_akta_osobowe_archiwizacja_uklad_i_przechowywanie_dokumentow, wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i, wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie, wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat, wf_82_skladka_zdrowotna_przy_zmianie_formy_opodatkowania_i_odlicze, wf_90_korekty_list_plac_zus_pit_11_i_ppk, wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic, wf_125_badania_lekarskie_po_dlugim_l4_kontrolne_vs_okresowe, wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego, wf_130_ustalanie_podstawy_wynagrodzenia_chorobowego_przy_zmianach_e, wf_134_zus_z_3_wynagrodzenie_i_zasilek_chorobowy_przy_firmach_20_pr, wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za, wf_138_kursy_i_szkolenia_kadrowo_placowe_dla_poczatkujacych, wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze, wf_143_wybor_programu_ksiegowego_kpir_pelna_ksiegowosc_jdg_i_spolki, wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po, wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie, wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan, wf_30_jpk_cit_znaczniki_kont_i_moment_ich_nadania, wf_34_odbior_dnia_wolnego_za_swieto_1_listopada_w_sobote, wf_48_ryczalt_dobor_stawki_wg_rodzaju_uslugi_it_hydraulik_catering, wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty, wf_51_przejecie_ksiegowosci_korekta_blednych_sald_rozrachunkow_z_b, wf_53_najem_prywatny_a_vat_ksef_i_jdg, wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy, wf_66_ksiegowanie_faktur_zagranicznych_wnt_import_uslug_i_towarow, wf_71_minimalne_wynagrodzenie_2026_regulamin_i_skladniki_placy, wf_74_rozliczanie_wynagrodzen_wyplacanych_w_nastepnym_miesiacu_kos, wf_75_ulga_dla_pracujacego_seniora_pit_11_i_rozliczenie, wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026, wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026, wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica_limity_d, wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac, wf_94_powrot_do_zwolnienia_vat_po_podniesieniu_limitu_do_240_tys, wf_98_zasilek_opiekunczy_zus_wypelnianie_z_15a_i_prawo_do_zasilku, wf_99_ksef_nadawanie_uprawnien_podmiotom_i_certyfikaty_dla_biur_ra, wf_merge_101_102_macierzynstwo_wnioski_urlopowe_zasilki_skladki_zus, wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty, wf_merge_33_86_95_roczne_rozliczenia_pit_pit_4r_pit_11_korekty_i_przekazanie
- Kategorie wymagające ogólnej naprawy prompt Opusa dla batch 2 (≥3 confirmed): hallucination_risk, missing_critical_info
