# Audyt pytań showcase

Data: 2026-04-10

Zakres:
- `Termin złożenia JPK_V7?`
- `Estoński CIT — kto może?`
- `Okres wypowiedzenia umowy`

## Wynik

### 1. Termin złożenia JPK_V7?
- Kategoria: `jpk`
- Ocena: `OK`
- Wniosek: baza ma wystarczający materiał do poprawnej odpowiedzi. Najmocniejszy chunk pochodzi z `art. 99 ust. 1-3 ustawy o VAT` i zawiera konkretny termin 25. dnia miesiąca oraz rozróżnienie między `JPK_V7M` i `JPK_V7K`.

Top 5 chunków:
1. `Ustawa o VAT | art. 99 ust. 1-3 | score 30.66`
2. `Rozporządzenie JPK_V7 | § 12 | score 27.04`
3. `Rozporządzenie JPK_V7 | § 2 | score 23.20`
4. `Ustawa o podatku dochodowym od osób fizycznych | art. 12 ust. 1 | score 6.96`
5. `Ustawa o VAT | art. 28q | score 5.55`

### 2. Estoński CIT — kto może?
- Kategoria: `cit`
- Ocena: `OK`
- Wniosek: baza ma wystarczający materiał do poprawnej odpowiedzi. Trzy najwyższe chunki pochodzą z ustawy o CIT i pokrywają zarówno warunki wejścia (`art. 28j ust. 1`), jak i wyłączenia (`art. 28k ust. 1`).

Top 5 chunków:
1. `Ustawa o podatku dochodowym od osób prawnych | art. 28j ust. 1 oraz art. 28k ust. 1 | score 34.55`
2. `Ustawa o podatku dochodowym od osób prawnych | art. 28k ust. 1 | score 33.47`
3. `Ustawa o podatku dochodowym od osób prawnych | art. 28j ust. 1 | score 21.44`
4. `Ustawa o VAT | art. 106nb | score 8.07`
5. `Ustawa o VAT | art. 89a ust. 5 | score 7.21`

### 3. Okres wypowiedzenia umowy
- Kategoria: `kadry`
- Ocena: `OK`
- Wniosek: baza ma wystarczający materiał do poprawnej odpowiedzi. Najważniejsze normy dla użytkownika końcowego są pokryte przez `art. 34` i `art. 36 § 1 Kodeksu pracy`.

Top 5 chunków:
1. `Kodeks pracy | art. 34 | score 56.49`
2. `Kodeks pracy | art. 36 § 1 | score 50.43`
3. `Kodeks pracy | art. 55 § 11 | score 42.21`
4. `Ustawa o podatku dochodowym od osób fizycznych | art. 22a ust. 1 | score 7.90`
5. `Ustawa o podatku dochodowym od osób fizycznych | art. 22b ust. 1 | score 7.18`

## Wprowadzone poprawki KB

- usunięto placeholderowe unity JPK, które zawierały odpowiedzi typu „nie można udzielić odpowiedzi”
- usunięto placeholderowy unit CIT dla estońskiego CIT
- dodano ręcznie zweryfikowane unity:
  - `Ustawa o VAT | art. 99 ust. 1-3`
  - `Rozporządzenie JPK_V7 | § 2`
  - `Rozporządzenie JPK_V7 | § 4-5`
  - `Rozporządzenie JPK_V7 | § 12`
  - `Ustawa o podatku dochodowym od osób prawnych | art. 28j ust. 1`
  - `Ustawa o podatku dochodowym od osób prawnych | art. 28k ust. 1`
  - `Ustawa o podatku dochodowym od osób prawnych | art. 28j ust. 1 oraz art. 28k ust. 1`
  - `Kodeks pracy | art. 34`
  - `Kodeks pracy | art. 36 § 1`

## Konkluzja

Po patchu wszystkie trzy pytania showcase dają odpowiedzi grounded, bez `insufficient data`, oparte o właściwe ustawy i konkretne przepisy.
