# V3 Corrections Log

Data: 2026-04-19
Model: claude-sonnet-4-6
Applied: 35 / 39
Failed: 4
Koszt: $3.2722 (cap $4.50)
Pytest: 260 passed, 0 failed

## Ready-for-testers drafty które dostały v3 corrections
- wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic (applied: 3, failed: 0)
- wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego (applied: 2, failed: 0)
- wf_134_zus_z_3_wynagrodzenie_i_zasilek_chorobowy_przy_firmach_20_pr (applied: 3, failed: 0)
- wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za (applied: 3, failed: 0)
- wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze (applied: 1, failed: 0)
- wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po (applied: 3, failed: 0)
- wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i (applied: 1, failed: 0)
- wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie (applied: 1, failed: 0)

## Per draft
| Draft | Flag applied | Flag failed |
|---|---|---|
| wf_110_kpir_2026_ksiegowanie_faktur_do_paragonu_i_sprzedazy_detalic | 3 | 0 |
| wf_125_badania_lekarskie_po_dlugim_l4_kontrolne_vs_okresowe | 2 | 0 |
| wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego | 2 | 0 |
| wf_134_zus_z_3_wynagrodzenie_i_zasilek_chorobowy_przy_firmach_20_pr | 3 | 0 |
| wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za | 3 | 0 |
| wf_138_kursy_i_szkolenia_kadrowo_placowe_dla_poczatkujacych | 2 | 0 |
| wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze | 1 | 0 |
| wf_143_wybor_programu_ksiegowego_kpir_pelna_ksiegowosc_jdg_i_spolki | 3 | 0 |
| wf_15_akta_osobowe_archiwizacja_uklad_i_przechowywanie_dokumentow | 1 | 0 |
| wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po | 3 | 0 |
| wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie | 1 | 0 |
| wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan | 0 | 4 |
| wf_30_jpk_cit_znaczniki_kont_i_moment_ich_nadania | 2 | 0 |
| wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i | 1 | 0 |
| wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie | 1 | 0 |
| wf_48_ryczalt_dobor_stawki_wg_rodzaju_uslugi_it_hydraulik_catering | 2 | 0 |
| wf_8_nagroda_jubileuszowa_po_doniesieniu_dokumentow_do_stazu_prac | 3 | 0 |
| wf_90_korekty_list_plac_zus_pit_11_i_ppk | 1 | 0 |
| wf_merge_33_86_95_roczne_rozliczenia_pit_pit_4r_pit_11_korekty_i_przekazanie | 1 | 0 |

## Failed items (do ewentualnego manual fix później)
- **wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan** flag [missing_critical_info]: correction failed after 3 attempts: json_parse stop_reason=end_turn: Expecting ',' delimiter: line 22 column 482 (char 2242)
- **wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan** flag [edge_case_coverage]: correction failed after 3 attempts: json_parse stop_reason=end_turn: Expecting ',' delimiter: line 22 column 482 (char 2242)
- **wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan** flag [legal_anchor_uncertainty]: correction failed after 3 attempts: json_parse stop_reason=end_turn: Expecting ',' delimiter: line 22 column 635 (char 2535)
- **wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan** flag [missing_critical_info]: correction failed after 3 attempts: json_parse stop_reason=end_turn: Expecting ',' delimiter: line 22 column 482 (char 2242)

## Pytest wynik (ogon outputu)
```
........................................................................ [ 27%]
........................................................................ [ 55%]
........................................................................ [ 83%]
............................................                             [100%]
260 passed in 6.51s
```