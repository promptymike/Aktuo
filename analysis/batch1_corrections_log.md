# Batch 1 Corrections Log

Data: 2026-04-18
Applied (kumulatywnie): 21 / 22 confirmed flag z verifier v1+v2
Failed: 1 (wf_79 flag#4 — malformed JSON z modelu, 3 retry)
Koszt ostatni run: $1.1818 (hard cap $2.00 niewyczerpany)
Poprzedni częściowy run (przed fixem KeyError): ~8 flag zapplikowanych, nie liczony w koszcie
Pytest: 260 passed, 0 failed
Model: claude-sonnet-4-6, max_tokens=16000, temperature=0.1

## Per draft (flag confirmed / applied / failed)
| Draft | Confirmed | Applied | Failed |
|---|---|---|---|
| wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p | 4 | 4 | 0 |
| wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece | 9 | 9 | 0 |
| wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze | 2 | 2 | 0 |
| wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie | 1 | 1 | 0 |
| wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie | 2 | 2 | 0 |
| wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat | 2 | 2 | 0 |
| wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026 | 1 | 0 | 1 |
| wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026 | 1 | 1 | 0 |
| wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy | 0 | 0 | 0 |
| wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty | 0 | 0 | 0 |

## Top 3 examples (przed/po)
### 1. wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece — flag [missing_critical_info] Step 2 stwierdza że 'pracownik zazwyczaj nie ma potrącenia w ogóle' przy minimalnym wynagrodzeniu - brakuje precyzyjnego
**Źródło:** https://ksiegowosc.infor.pl/rachunkowosc/ksiegi-rachunkowe/743667,Jak-ujac-w-ksiegach-rachunkowych-zajecie-wynagrodzenia.html

```
  - step #2 changed:
    BEFORE: Zastosuj limit 50% wynagrodzenia netto i kwotę wolną dla umowy o pracę — Przy zajęciu niealimentacyjnym maksymalne potrącenie to 50% wynagrodzenia netto po odliczeniu ZUS, zaliczki PIT i PPK. Kwota wolna to 100% minimalnego
    AFTER:  Zastosuj limit 50% wynagrodzenia netto i kwotę wolną dla umowy o pracę — Przy zajęciu niealimentacyjnym maksymalne potrącenie to 50% wynagrodzenia netto po odliczeniu ZUS, zaliczki PIT i PPK. Kwota wolna to 100% minimalnego
```

### 2. wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p — flag [missing_critical_info] Brakuje wyjaśnienia, jak oznaczać faktury korygujące (faktury VAT RR) w kontekście nowych kodów BFK/DI - czy dziedziczą 
**Źródło:** https://www.gofin.pl/17,2,7,257580,nowe-oznaczenia-w-pliku-jpkvat.html

```
  - step #7 changed:
    BEFORE: Zweryfikuj stanowisko KIS w razie wątpliwości pisemnym zapytaniem — W temacie BFK vs DI dla WNT/importu usług pojawiają się sprzeczne interpretacje - według niepotwierdzonych informacji ze szkoleń część głosów wskazuje
    AFTER:  Ustal oznaczenie BFK/DI dla faktur korygujących i faktur VAT RR — Faktury korygujące co do zasady dziedziczą oznaczenie faktury pierwotnej - korekta do faktury z BFK otrzymuje BFK, korekta do dokumentu z DI otrzymuje
  - step #8 changed:
    AFTER:  Zweryfikuj stanowisko KIS w razie wątpliwości pisemnym zapytaniem — W temacie BFK vs DI dla WNT/importu usług pojawiają się sprzeczne interpretacje - według niepotwierdzonych informacji ze szkoleń część głosów wskazuje
edge_cases: changed
common_mistakes: changed
```

### 3. wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat — flag [legal_anchor_uncertainty] Art. 23 ust. 5c PIT cytowany jako podstawa dla 'zasady ochrony praw nabytych' i przejścia limitu 150→100 tys. zł od 1.01
**Źródło:** https://www.podatki.biz/sn_autoryzacja/logowanie.php5/artykuly/leasing-samochodu-z-2025-r-z-nowym-limitem-kosztow-w-2026-r-fiskus-to-nie-blad-legislacyjny_63_60976.htm?idDzialu=63&idArtykulu=60976

```
legal_anchors changed:
  - anchor #1:
    BEFORE: Ustawa o PIT art. 23 ust. 1 pkt 47a oraz ust. 5c
    AFTER:  Ustawa o PIT art. 23 ust. 1 pkt 47a oraz ust. 5c
  - anchor #3:
    AFTER:  Ustawa zmieniająca z 2 grudnia 2021 r. art. 30
  - step #2 changed:
    BEFORE: Porównaj wartość samochodu z obowiązującym limitem KUP — Limit 150 000 zł stosujesz dla umów zawartych do 31.12.2025 (samochody spalinowe/hybrydowe) oraz 225 000 zł dla elektryków. Od 1.01.2026 limit dla sam
    AFTER:  Porównaj wartość samochodu z obowiązującym limitem KUP — Limit 150 000 zł stosuje się dla umów leasingu operacyjnego zawartych do 31.12.2025 (samochody spalinowe/hybrydowe) oraz 225 000 zł dla elektryków. Od
edge_cases: changed
common_mistakes: changed
```

## Błędy
- **wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026** flag [missing_critical_info]: correction failed after 3 attempts: json_parse stop_reason=end_turn: Expecting ',' delimiter: line 40 column 207 (char 3340)

## Pytest wynik (ogon outputu)
```
........................................................................ [ 27%]
........................................................................ [ 55%]
........................................................................ [ 83%]
............................................                             [100%]
260 passed in 12.70s
```