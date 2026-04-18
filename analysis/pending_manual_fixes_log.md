# Pending Manual Fixes Log

Data: 2026-04-18T16:46:00Z
Total pending flags: 7
Applied: 7
Skipped / not found: 0

## Kontekst
Te flagi zawiodły Stage 5 (batch 2) albo Stage 8 (v3 corrections) z powodu LLM generującego malformed JSON przy 3 kolejnych próbach (identyczny pattern co wf_79 flag#4 batch 1). Napraw. bez LLM call — bezpośrednio w strukturze JSON.

## Zastosowane fixy
### wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan — flag [legal_anchor_uncertainty]
- **Source:** v2_manual
- **Flag opis:** Pole `legal_anchors` jest puste, a draft zawiera liczne odwołania do konkretnych przepisów (§ 2 ust. 1 pkt 19 rozporządzenia składkowego z 18.12.1998, art. 21 ust. 1 pkt 67 ustawy o PIT, art. 26 ust. 1 ustawy o PPK, art. 43 ust. 1 pkt 18–19 ustawy o VAT). Brak strukturalnego mapowania tych artykułów do kroków procedury utrudnia weryfikację aktualności i poprawności cytowań.
- **Zmiana:** Populacja legal_anchors (9 wpisów) + poprawka step 4: art. 2 pkt 40 ustawy o PPK jako podstawa wymiaru (art. 26 ust. 1 dotyczy wysokości wpłaty).

### wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan — flag [missing_critical_info]
- **Source:** v3_manual
- **Flag opis:** Krok 6 wspomina 'refakturę' i 'fakturę wewnętrzną' jako sposób rozliczenia VAT od części pracownika, ale nie wyjaśnia czy refaktura wymaga wystawienia dokumentu VAT czy czy jest to tylko zapis księgowy — brak jasności co do formalnych wymogów.
- **Zmiana:** Step 6: refaktura wymaga wystawienia dokumentu VAT (nie tylko zapisu księgowego); faktura wewnętrzna zniesiona w 2014 r.

### wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan — flag [edge_case_coverage]
- **Source:** v3_manual
- **Flag opis:** Edge case o nieodpłatnym udostępnieniu lokalu mieszkalnego mówi o 'wartości rynkowej najmu, jeżeli wyższa' — brak wyjaśnienia jak pracownik/pracodawca powinni ustalić tę wartość rynkową (wycena niezależna? średnia z rynku?) i czy ZUS akceptuje takie szacunki.
- **Zmiana:** Dodano edge_case o wycenie udostępnienia lokalu mieszkalnego wg § 3 pkt 3 rozporządzenia składkowego.

### wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan — flag [legal_anchor_uncertainty]
- **Source:** v3_manual
- **Flag opis:** Draft wielokrotnie odwołuje się do 'rozporządzenia składkowego z 18.12.1998' bez pełnego tytułu — brak pewności czy to prawidłowe oznaczenie (Rozporządzenie Ministra Pracy i Polityki Społecznej z 18 grudnia 1998 r. w sprawie szczegółowych zasad ustalania podstawy wymiaru składek na ubezpieczenia społeczne).
- **Zmiana:** Step 1 + step 2: pełny tytuł rozporządzenia MPiPS z 18.12.1998 (Polityki Socjalnej, nie Społecznej; ubezpieczenia emerytalne i rentowe).

### wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan — flag [missing_critical_info]
- **Source:** v3_manual
- **Flag opis:** Krok 6 wspomina VAT 8% dla Multisportu 'jako usługi rekreacyjne' — brak wyjaśnienia czy ta stawka dotyczy wszystkich dostawców (Benefit Systems, Medicover itp.) czy tylko niektórych, i czy zmienia się w zależności od zakresu usług.
- **Zmiana:** Step 6: poz. 186 zał. nr 3 ustawy o VAT, niezależna od dostawcy, wyjątek 23% dla usług poza 'wstępem'.

### wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty — flag [outdated_data_risk]
- **Source:** v2_manual
- **Flag opis:** Krok 2 zawiera stwierdzenie 'na dzień 18.04.2026 obowiązują przepisy przedłużające ochronę czasową obywateli Ukrainy do 4.03.2026' — ta data jest już przeszłością względem daty weryfikacji (18.04.2026), co sugeruje, że draft może zawierać nieaktualne informacje o przepisach przejściowych specustawy.
- **Zmiana:** Step 2: ochrona czasowa do 4.03.2027 (decyzja Rady UE 2025/1460); specustawa wygaszona 5.03.2026 ustawą z 23.01.2026.

### wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty — flag [missing_critical_info]
- **Source:** v2_manual
- **Flag opis:** Draft nie zawiera instrukcji, co zrobić, jeśli pracownik nie złoży wniosku o przedłużenie karty pobytu/statusu UKR przed upływem ważności — czy pracodawca ma obowiązek zawiadomienia pracownika, czy może rozwiązać umowę, czy istnieje okres przejściowy?
- **Zmiana:** Step 7: dodano procedurę dla braku wniosku o przedłużenie — brak automatyki, obowiązek aktywnego wypowiedzenia (art. 25 ustawy z 23.01.2026).
