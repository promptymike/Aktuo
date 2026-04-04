# Aktuo KB Pipeline

Pipeline automatycznego budowania bazy wiedzy VAT z ustawy ISAP.

## Wymagania

- Python 3.11+
- `ANTHROPIC_API_KEY` w środowisku
- Na Windows pipeline działa z fallbackiem Python bez systemowego `pdftotext`

Instalacja zależności:

```bash
pip install -r requirements.txt
```

Opcjonalnie możesz zainstalować systemowe `pdftotext` i dodać je do `PATH`.
Jeśli go nie ma, `parse_isap.py` automatycznie użyje biblioteki `pypdf`.

## Uruchomienie na Windows

PowerShell:

```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
python run_pipeline.py ustawa_vat.pdf questions_vat.json
```

## Uruchomienie — jedno polecenie

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
python run_pipeline.py ustawa_vat.pdf questions_vat.json
```

## Co robi pipeline

```text
[1] parse_isap.py      - PDF ustawy -> articles.json
                         Lokalnie: najpierw pdftotext, potem fallback pypdf

[2] match_questions.py - pytania + artykuły -> matched.json
                         Claude dopasowuje pytania do artykułów

[3] generate_units.py  - matched pairs -> draft_units.json
                         Claude generuje answer units ze structured output

[4] audit_units.py     - draft units + tekst artykułu -> verified_units.json
                         Claude weryfikuje czy unit jest grounded w źródle
```

## Uruchomienie krok po kroku

```bash
# Krok 1: Parse (nie wymaga API)
python parse_isap.py ustawa_vat.pdf --output output/articles.json

# Krok 2: Match (wymaga API)
python match_questions.py output/articles.json questions_vat.json --output output/matched.json

# Krok 3: Generate (wymaga API)
python generate_units.py output/articles.json output/matched.json --output output/draft_units.json

# Krok 4: Audit (wymaga API)
python audit_units.py output/articles.json output/draft_units.json --output output/verified_units.json
```

## Output

- `output/articles.json` - sparsowane artykuły ustawy
- `output/matched.json` - pytania dopasowane do artykułów
- `output/draft_units.json` - wygenerowane answer units (draft)
- `output/verified_units.json` - pełny wynik z podziałem VERIFIED/NEEDS_FIX/REJECTED
- `output/verified_units_kb.json` - czysta baza wiedzy do załadowania dalej

## Dodawanie nowych ustaw

1. Pobierz PDF z ISAP.
2. Uruchom `python parse_isap.py nowa_ustawa.pdf --output articles_pit.json`.
3. Przygotuj question bank.
4. Uruchom pipeline z nowymi plikami.
