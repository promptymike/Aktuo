# Batch 2 Corrections Log

Data: 2026-04-18
Applied: 20 / 23 (batch 2 confirmed flag — batch 1's 22 skipped as already applied via resume)
Failed: 3 (wszystkie: `json_parse end_turn` — LLM wygenerował malformed JSON 3x, taki sam pattern jak wf_79 flag#4 z batch 1)
Koszt: $1.6301 (cap $3.00)
Pytest: 260 passed, 0 failed
Model: claude-sonnet-4-6, max_tokens=16000, temperature=0.1

Failed items do manualnej obsługi:
- `wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan` flag#0
- `wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty` flag#2
- `wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty` flag#4

---

## Per draft
| Draft | Flag applied | Flag skipped (errors) |
|---|---|---|
| wf_125_badania_lekarskie_po_dlugim_l4_kontrolne_vs_okresowe | 1 | 0 |
| wf_127_premie_w_podstawie_wynagrodzenia_chorobowego_i_urlopowego | 2 | 0 |
| wf_135_przejscie_roku_wynagrodzenie_chorobowe_vs_zasilek_i_okres_za | 1 | 0 |
| wf_143_wybor_programu_ksiegowego_kpir_pelna_ksiegowosc_jdg_i_spolki | 1 | 0 |
| wf_15_akta_osobowe_archiwizacja_uklad_i_przechowywanie_dokumentow | 1 | 0 |
| wf_19_delegowanie_i_podroze_sluzbowe_pracownikow_za_granice_zus_po | 3 | 0 |
| wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan | 0 | 1 |
| wf_34_odbior_dnia_wolnego_za_swieto_1_listopada_w_sobote | 1 | 0 |
| wf_35_ewidencja_i_rozliczanie_czasu_pracy_przy_roznych_systemach_i | 1 | 0 |
| wf_45_wymiar_urlopu_wypoczynkowego_przy_niepelnym_etacie_i_zmianie | 1 | 0 |
| wf_48_ryczalt_dobor_stawki_wg_rodzaju_uslugi_it_hydraulik_catering | 1 | 0 |
| wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty | 0 | 2 |
| wf_51_przejecie_ksiegowosci_korekta_blednych_sald_rozrachunkow_z_b | 1 | 0 |
| wf_66_ksiegowanie_faktur_zagranicznych_wnt_import_uslug_i_towarow | 2 | 0 |
| wf_82_skladka_zdrowotna_przy_zmianie_formy_opodatkowania_i_odlicze | 2 | 0 |
| wf_87_pit_ulga_na_dziecko_i_rozliczenie_samotnego_rodzica_limity_d | 1 | 0 |
| wf_90_korekty_list_plac_zus_pit_11_i_ppk | 1 | 0 |

## Top 3 examples (przed/po)
(brak — żaden draft z listy priorytetowej nie został zmodyfikowany)
## Błędy
- **wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan** flag [legal_anchor_uncertainty]: correction failed after 3 attempts: json_parse stop_reason=end_turn: Expecting ',' delimiter: line 22 column 482 (char 2242)
- **wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty** flag [outdated_data_risk]: correction failed after 3 attempts: json_parse stop_reason=end_turn: Expecting ',' delimiter: line 34 column 47 (char 3889)
- **wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty** flag [missing_critical_info]: correction failed after 3 attempts: json_parse stop_reason=end_turn: Expecting ',' delimiter: line 34 column 47 (char 3790)

## Pytest wynik (ogon outputu)
```
........................................................................ [ 27%]
........................................................................ [ 55%]
........................................................................ [ 83%]
............................................                             [100%]
260 passed in 5.45s
```