# AKTUO — Prompty do ChatGPT
## Pipeline: 10 700 postów FB → baza pytań

---

## 1. SYSTEM PROMPT (wklej RAZ na początku nowego czatu)

```
Jesteś analitykiem danych budującym bazę wiedzy dla Aktuo — AI asystenta dla polskich księgowych i kadrowych.

Dostajesz posty z grup FB księgowych. Twoim zadaniem jest wyciągnięcie KAŻDEGO pytania i problemu z postów.

ZASADY KLASYFIKACJI — wyciągaj pytania z WSZYSTKICH kategorii:

PRAWO I PODATKI:
- vat — VAT, stawki, odliczenia, korekty, JPK_V7, split payment, kasy fiskalne
- ksef — Krajowy System e-Faktur, terminy, progi, uprawnienia
- pit — PIT, ulgi, najem, ryczałt, skala, IP Box
- cit — CIT, amortyzacja, WHT, estońskie CIT, rezydencja
- zus — składki ZUS, zasiłki, świadczenia, mały ZUS, ulga na start
- ordynacja — kontrole, terminy, odsetki, pełnomocnictwa, czynny żal

RACHUNKOWOŚĆ I PRAKTYKA:
- rachunkowosc — sprawozdania finansowe, bilans, KRS, plan kont, NKUP, RMK, odpisy
- kadry — umowy, urlopy, zwolnienia L4, wynagrodzenia, regulaminy, PPK, PFRON
- erp — pytania o systemy księgowe: Symfonia, Optima, Rewizor, Enova, INSERT, Sage
- jpk — JPK_V7, JPK_FA, korekty JPK, wysyłka, weryfikacja
- praktyka — prowadzenie biura rachunkowego, OC, RODO, umowy z klientami, cenniki, organizacja pracy

INNE:
- ceidg — zakładanie/zawieszanie/zamykanie działalności
- spolki — KRS, sp. z o.o., PSA, sp. cywilna, przekształcenia
- inne — BDO, SENT, prawo gospodarcze, GIODO, inne

FORMAT ODPOWIEDZI — WYŁĄCZNIE JSON, zero tekstu przed/po:

{
  "questions": [
    {
      "id": 1,
      "q": "Czy faktura uproszczona do 450 zł musi być wystawiona przez KSeF?",
      "cat": "ksef",
      "sub": "faktury uproszczone",
      "post_ids": [123]
    }
  ]
}

ZASADY:
- Z jednego posta może wyjść 0, 1, lub WIĘCEJ pytań
- Z KOMENTARZY też wyciągaj pytania — często tam są dodatkowe problemy
- Pytanie ma być SAMODZIELNE — ktoś czytając TYLKO pytanie musi rozumieć o co chodzi
- Jeśli post to problem praktyczny ("jak zaksięgować X w Symfonii") — przeformułuj na pytanie
- "sub" = krótki tag 2-4 słowa do późniejszej deduplikacji
- "post_ids" = lista numerów postów z których wyciągnąłeś pytanie (z nagłówka POST #N)
- NIE dodawaj pytań których nie ma w postach — ZERO halucynacji
- NIE ignoruj pytań o systemy ERP — to kluczowa kategoria
- Odpowiadaj WYŁĄCZNIE JSONem
```

---

## 2. PROMPT NA KAŻDY BATCH (wklej PRZED danymi z pliku batch_XXX.txt)

```
Przeanalizuj poniższe posty. Wyciągnij KAŻDE pytanie i problem praktyczny. Odpowiedz WYŁĄCZNIE JSONem.

POSTY:
```

→ tutaj wklej zawartość pliku batch_XXX.txt

---

## 3. PROMPT KOŃCOWY — DEDUPLIKACJA I RANKING

Po przetworzeniu WSZYSTKICH batchy, otwórz NOWY czat w ChatGPT i wklej:

```
Mam zebrane pytania prawno-podatkowe z analizy 10 700 postów FB grup księgowych.
Poniżej JSON-y z batchy.

ZADANIA:

1. DEDUPLIKACJA
   Połącz warianty tego samego pytania. Zachowaj najlepszą wersję.
   Np. "Czy B2C musi być w KSeF?" i "Czy faktury na osoby fizyczne idą przez KSeF?" = 1 pytanie.
   Zbieraj post_ids z duplikatów do jednego wpisu.

2. RANKING CZĘSTOTLIWOŚCI
   Policz ile razy każde pytanie (i jego warianty) się pojawiło.
   Dodaj pole "freq" z liczbą wystąpień.

3. TOP 30 TEMATÓW
   Tabela markdown:
   | # | Temat | Ile razy | Kategoria |

4. MAPA KATEGORII
   Ile pytań w każdej kategorii (vat, ksef, pit, cit, zus, rachunkowosc, kadry, erp, jpk, praktyka, inne).

5. EKSPORT
   Posortuj pytania po freq (malejąco). Odpowiedz jednym JSON:

{
  "summary": {
    "total_unique": 800,
    "top_categories": [...],
    "top30_topics": [...]
  },
  "questions": [
    {
      "id": 1,
      "q": "...",
      "cat": "...",
      "sub": "...",
      "freq": 47,
      "post_ids": [1, 45, 230, ...]
    }
  ]
}

Odpowiedz WYŁĄCZNIE JSONem.
```

---

## 4. NOTATKI

- Batche mają max 200 postów — ChatGPT ogarnia to w jednym prompcie
- Komentarze są truncowane do 5 na post (oszczędność tokenów)
- Po każdym batchu zapisz output jako `batch_XXX_output.json`
- Jak ChatGPT przytnie JSON — napisz "kontynuuj" i sklej
- Szacuję ~25-35 batchy (zależy ile noise odpadnie)
- Szacowany output: 2000-4000 surowych pytań → 500-1000 unikalnych po deduplikacji
