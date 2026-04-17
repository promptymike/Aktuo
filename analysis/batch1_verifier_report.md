# Batch 1 Verifier Report

Data: 2026-04-18
Model: claude-sonnet-4-6
Koszt: $1.5084
Flag verified: 122
Retry/error count: 0

## Rozkład verdictów
- confirmed: 5/122 (4.1%)
- false_positive: 22/122 (18.0%)
- cannot_verify: 95/122 (77.9%)

## Rozkład confirmed flag per draft (po filtracji false positives)
| Draft | Przed verifier | Confirmed | False_pos | Cannot_verify |
|---|---|---|---|---|
| wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p | 12 | 1 | 1 | 10 |
| wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece | 14 | 1 | 0 | 13 |
| wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze | 15 | 0 | 4 | 11 |
| wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie | 10 | 0 | 2 | 8 |
| wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie | 13 | 2 | 2 | 9 |
| wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy | 10 | 0 | 2 | 8 |
| wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat | 14 | 1 | 4 | 9 |
| wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026 | 12 | 0 | 0 | 12 |
| wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026 | 10 | 0 | 1 | 9 |
| wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty | 12 | 0 | 6 | 6 |

## Top 5 najbardziej problematycznych draftów (po confirmed flag)
- wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie — 2 confirmed
- wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p — 1 confirmed
- wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece — 1 confirmed
- wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat — 1 confirmed
- wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze — 0 confirmed

## Top 3 najlepsze drafty (najmniej confirmed flag)
- wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze — 0 confirmed
- wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie — 0 confirmed
- wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy — 0 confirmed

## Kategorie problemów (rozkład verdictów)
- missing_critical_info: 0 confirmed, 8 false_positive, 30 cannot_verify
- hallucination_risk: 3 confirmed, 2 false_positive, 15 cannot_verify
- legal_anchor_uncertainty: 0 confirmed, 8 false_positive, 10 cannot_verify
- outdated_data_risk: 0 confirmed, 1 false_positive, 16 cannot_verify
- step_contradiction: 1 confirmed, 1 false_positive, 13 cannot_verify
- edge_case_coverage: 1 confirmed, 2 false_positive, 11 cannot_verify

## High severity confirmed issues (lista pełna)
- **wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p** → Stanowisko MF z '18.03' (bez roku) dotyczące BFK dla WNT jest cytowane bez pełnej referencji. Brak możliwości weryfikacji, czy taki dokument rzeczywiście istnieje i jaka jest jego pełna treść.
  - *corrective:* Usunąć lub doprecyzować odniesienie do 'MF z 18.03' - podać pełną datę z rokiem, numer dokumentu (np. numer pisma, interpretacji ogólnej lub komunikatu), albo zastąpić sformułowaniem 'według niepotwierdzonych informacji ze szkoleń' lub całkowicie usunąć i pozostawić jedynie rekomendację złożenia zapytania do KIS.

## Cannot_verify summary
Flagi wymagające web_search / expert review (bo KB nie pokrywa):
- missing_critical_info: 30
- outdated_data_risk: 16
- hallucination_risk: 15
- step_contradiction: 13
- edge_case_coverage: 11
- legal_anchor_uncertainty: 10

## Rekomendacje dla następnego kroku
- Drafty do manualnego review przed pokazaniem testerom (≥3 confirmed): brak
- Drafty względnie gotowe (≤1 confirmed): wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p, wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece, wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat, wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze, wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie, wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy, wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026, wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026, wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty
- Kategorie wymagające ogólnej naprawy prompt Opusa dla batch 2 (≥3 confirmed): hallucination_risk
