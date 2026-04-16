# Workflow Seed Report

- Workflow questions analyzed: 2152
- Workflow seed units created: 9

## Top workflow clusters by impact

| Cluster | Area | Questions | Total freq | Impact |
|---|---|---:|---:|---:|
| accounting_posting_and_periods | KPiR / księgowanie / okresy i memoriał | 1294 | 1583 | 2374.5 |
| financial_statements_workflow | Sprawozdanie finansowe / podpis / wysyłka | 197 | 255 | 344.25 |
| ksef_invoice_circulation | KSeF issuing / correction / invoice circulation | 176 | 215 | 290.25 |
| fallback_other_workflow | Pozostałe operacje workflow | 194 | 265 | 212.0 |
| software_and_sync_operations | Oprogramowanie księgowe / integracje / synchronizacja | 110 | 135 | 148.5 |
| inventory_documents_and_columns | Dokumenty księgowe / magazyn / kolumny i klasyfikacja | 83 | 119 | 142.8 |
| jpk_filing_corrections_tags | JPK filing / correction / tags | 58 | 67 | 90.45 |
| zus_pue_registrations | ZUS / PUE / zgłoszenia i wyrejestrowania | 24 | 28 | 36.4 |
| ksef_permissions_authorizations | KSeF permissions / authorization flow | 8 | 8 | 11.2 |
| tax_authorizations_and_signatures | Pełnomocnictwa / podpis / kanały złożenia | 8 | 8 | 9.6 |

## Top workflow areas

| Area | Questions |
|---|---:|
| KPiR / księgowanie / okresy i memoriał | 1294 |
| Sprawozdanie finansowe / podpis / wysyłka | 197 |
| Pozostałe operacje workflow | 194 |
| KSeF issuing / correction / invoice circulation | 176 |
| Oprogramowanie księgowe / integracje / synchronizacja | 110 |
| Dokumenty księgowe / magazyn / kolumny i klasyfikacja | 83 |
| JPK filing / correction / tags | 58 |
| ZUS / PUE / zgłoszenia i wyrejestrowania | 24 |
| KSeF permissions / authorization flow | 8 |
| Pełnomocnictwa / podpis / kanały złożenia | 8 |

## Top missing information fields

| Field | Count |
|---|---:|
| rodzaj_dokumentu | 1290 |
| rodzaj_ksiąg_lub_ewidencji | 1284 |
| okres_księgowy | 1247 |
| nazwa_systemu | 628 |
| czynność_operacyjna | 592 |
| okres_lub_data | 34 |
| forma_opodatkowania | 12 |
| źródło_przychodu | 10 |
| typ_podmiotu | 3 |
| typ_umowy | 3 |

## Suggested top 10 workflow units

1. Ujęcie dokumentów w odpowiednim okresie i ewidencji (rachunkowosc) — required inputs: rodzaj_ksiąg_lub_ewidencji, rodzaj_dokumentu, okres_księgowy, nazwa_systemu, czynność_operacyjna
2. Przygotowanie, podpisanie i wysyłka sprawozdania finansowego (rachunkowosc) — required inputs: rodzaj_dokumentu, okres_księgowy, rodzaj_ksiąg_lub_ewidencji, nazwa_systemu, czynność_operacyjna
3. Obieg faktur, statusów i korekt w KSeF (ksef) — required inputs: czynność_operacyjna, nazwa_systemu, okres_lub_data, rodzaj_ksiąg_lub_ewidencji, rodzaj_dokumentu
4. Obsługa problemów systemowych i synchronizacji danych (software_tooling) — required inputs: nazwa_systemu, czynność_operacyjna
5. Klasyfikacja dokumentów, kolumn i zapisów magazynowych (rachunkowosc) — required inputs: rodzaj_ksiąg_lub_ewidencji, rodzaj_dokumentu, okres_księgowy, nazwa_systemu, czynność_operacyjna
6. Obsługa wysyłki, korekty i oznaczeń JPK (jpk) — required inputs: nazwa_systemu, czynność_operacyjna, okres_lub_data
7. Obsługa zgłoszeń, wyrejestrowań i deklaracji ZUS (zus) — required inputs: nazwa_systemu, czynność_operacyjna, typ_umowy, okres_lub_data, tytuł_ubezpieczenia
8. Nadawanie uprawnień i dostępów w KSeF (ksef) — required inputs: nazwa_systemu, czynność_operacyjna
9. Pełnomocnictwa, podpisy i elektroniczne kanały złożenia (procedury) — required inputs: czynność_operacyjna, nazwa_systemu, rodzaj_ksiąg_lub_ewidencji, rodzaj_dokumentu, okres_księgowy

## Recommended next step

Zbudować osobny indeks retrieval dla workflow_seed.json i uruchamiać go przed legal KB dla pytań o klasyfikacji workflow/software_tooling, z zachowaniem dopytań o brakujące pola wejściowe.
