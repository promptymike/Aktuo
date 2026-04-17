# Zadanie 3 — Batch 1: 10 workflow draft rekordów (raport)

**Data wygenerowania:** 2026-04-17T20:06:23Z  **Batch:** batch1  **Model:** claude-opus-4-7

## 1. Wykonanie

- Target: **10** draftów.
- Finalnie wygenerowano: **10** draftów.
- Schema valid: **10/10**.
- Parse fails (attempts): **1**.
- Schema fails (attempts): **0**.
- Pierwotny run: 10 ok / 0 failed — cluster `62` hit max_tokens=4096 dwa razy (8192 output), recovery poszedł przez jednorazowy `retry_cluster_62.py` z max_tokens=6500 (1 próba, 4209 out, OK). Cluster `merge_120_121` wygenerowany w probe-runie, w głównym batchu tylko `RESUMED`.

- **Koszt łączny: $4.85** (input 90,205 tok · output 46,587 tok).
- Cennik Opus 4.7: $0.015/1k input, $0.075/1k output.
- **Czas runu**: główny batch 634s (~10 min) + probe (~60s) + retry_62 (~60s) ≈ **12 min wall clock**.

### Uwaga o koszcie — delta vs estymata

Paweł estymował $1.50 za 10 klastrów (2500 in + 1500 out). Real: 90,205 in + 46,587 out = **$4.85** (~3× estymaty). Powody:

- Input tokens per cluster: ~7-8k (nie 2.5k). Prompt zawiera 10 postów centroidu z 3 komentarzami każdy + 5 postów high-engagement z **pełnymi** komentarzami + 10 kandydatów KB. Rich material to higher cost.
- Output tokens per cluster: ~3.5-4.2k (nie 1.5k). Opus generuje 7 kroków po ~200 słów każdy plus 3-4 edge_cases po 1-2 zdania plus 3 anchors z uzasadnieniami — to ok. 3.5k tokenów polskich znaków.
- Next batch (40): jeśli utrzymamy format 10+5 przykładów i 7 kroków, spodziewany koszt to ~$20 za batch 2 (40 klastrów × $0.50). Jeśli to za dużo, do rozważenia: (a) 5 centroidów zamiast 10, (b) comments trimowane do 150 znaków zamiast 300.

## 2. Tabela zbiorcza

| # | Cluster | Topic | Title | #Steps | #Anchors | Manual? | Status | in tok | out tok |
|---:|---|---|---|---:|---:|:---:|:---:|---:|---:|
| 1 | `merge_120_121` | KSeF | KSeF: moment podatkowy, data wystawienia faktury i ujęcie korekt w VAT/JPK | 7 | 2 | — | ♻️ RESUMED | 0 | 0 |
| 2 | `7` | kadry | Zaliczanie okresów umów zlecenie i działalności gospodarczej do stażu pracy od 1 stycznia 2026 r. | 7 | 1 | ⚠️ TAK | ✅ OK | 7635 | 3503 |
| 3 | `63` | PIT | Leasing operacyjny samochodu osobowego – limity KUP i odliczenie VAT | 7 | 3 | — | ✅ OK | 7749 | 3751 |
| 4 | `79` | ZUS | Mały ZUS Plus – ponowne skorzystanie z ulgi po przerwie od 2026 roku | 7 | 2 | ⚠️ TAK | ✅ OK | 8086 | 3699 |
| 5 | `49` | KPiR | Środki trwałe do 10 tys. zł i powyżej – wybór między kosztami bezpośrednimi, jednorazową amortyzacją a amortyzacją liniową | 7 | 3 | — | ✅ OK | 7434 | 4081 |
| 6 | `10` | kadry | Potrącenia komornicze niealimentacyjne z wynagrodzeń, zasiłków i umów zlecenia | 7 | 2 | — | ✅ OK | 15979 | 7872 |
| 7 | `107` | JPK | Oznaczenia BFK vs DI w JPK_VAT od lutego 2026 - faktury WNT, import usług, poza KSeF | 7 | 3 | — | ✅ OK | 6915 | 3531 |
| 8 | `62` | VAT | VAT przy wykupie, sprzedaży i darowiźnie samochodu osobowego z firmy (leasing, ST, cele prywatne) | 7 | 3 | — | 🟢 OK (retry) | 7211 | 4209 |
| 9 | `21` | rachunkowość | Sporządzanie i składanie sprawozdań finansowych do KRS/KAS - schematy, wersje, procedura | 6 | 3 | — | ✅ OK | 6533 | 3729 |
| 10 | `139` | KSeF | KSeF w biurze rachunkowym: obieg, archiwizacja i weryfikacja faktur kosztowych klientów | 7 | 3 | — | ✅ OK | 8162 | 4020 |

### Kotwice prawne — weryfikacja obecności w KB Aktuo

Każda kotwica sprawdzona pod kątem obecności w `data/seeds/law_knowledge.json` (4388 rekordów).

| Cluster | law_name | article_number | Status |
|---|---|---|---|
| `merge_120_121` | Ustawa o VAT | `art. 106na ust. 1 i 3` | ✅ EXACT |
| `merge_120_121` | Ustawa o VAT | `art. 106gb ust. 3` | ✅ EXACT |
| `7` | Kodeks pracy | `art. 22` | ✅ EXACT |
| `63` | Ustawa o VAT | `art. 86a ust. 1-3` | 🟡 PARTIAL |
| `63` | Ustawa o PIT | `art. 23 ust. 1 pkt 47a oraz ust. 5c` | 🟡 PARTIAL |
| `63` | Ustawa o PIT | `art. 23 ust. 1 pkt 46a` | 🟡 PARTIAL |
| `79` | Ustawa o systemie ubezpieczeń społecznych | `art. 18c` | ✅ EXACT |
| `79` | Ustawa o systemie ubezpieczeń społecznych | `art. 36 ust. 14` | 🟡 PARTIAL |
| `49` | Ustawa o podatku dochodowym od osób fizycznych | `art. 22d ust. 1 oraz art. 22f ust. 3` | 🟡 PARTIAL |
| `49` | Ustawa o podatku dochodowym od osób fizycznych | `art. 22k ust. 7 oraz art. 22k ust. 14` | 🟡 PARTIAL |
| `49` | Ustawa o podatku dochodowym od osób fizycznych | `art. 22h ust. 2` | ✅ EXACT |
| `10` | Kodeks pracy | `art. 87¹` | 🟡 PARTIAL |
| `10` | Kodeks pracy | `art. 87` | ✅ EXACT |
| `107` | Rozporządzenie w sprawie JPK_V7 | `§ 10` | ✅ EXACT |
| `107` | Ustawa o VAT | `art. 106gb ust. 4 pkt 1 i ust. 5` | 🟡 PARTIAL |
| `107` | Ustawa o VAT | `art. 109 ust. 14` | ✅ EXACT |
| `62` | Ustawa o VAT | `art. 86a ust. 1-3` | 🟡 PARTIAL |
| `62` | Ustawa o VAT | `art. 5 ust. 1 pkt 1` | ✅ EXACT |
| `62` | Ustawa o VAT | `art. 7 ust. 2` | ✅ EXACT |
| `21` | Ustawa o rachunkowości | `art. 69 ust. 1` | ✅ EXACT |
| `21` | Ustawa o rachunkowości | `art. 69 ust. 1 pkt 3` | ✅ EXACT |
| `21` | Ustawa o rachunkowości | `art. 45 ust. 1g` | ✅ EXACT |
| `139` | Ustawa o VAT | `art. 106gb ust. 3-6 oraz art. 106na ust. 1, 3-4` | ✅ EXACT |
| `139` | Ustawa o VAT | `art. 106nd ust. 2 pkt 1-6 i 11` | ✅ EXACT |
| `139` | Ustawa o VAT | `art. 106ga ust. 2` | 🟡 PARTIAL |

Legenda: **EXACT** — dokładny match law_name + article_number; **PARTIAL** — ten sam law_name i artykuł bazowy, różne ust./pkt (np. KB ma `art. 22h ust. 2`, draft odnosi się do `art. 22h ust. 2 pkt 3`); **NOT_FOUND** — brak w KB. Po aliasie `Ustawa o PIT`↔`Ustawa o podatku dochodowym od osób fizycznych` oraz `Rozporządzenie w sprawie JPK_V7`↔`Rozporządzenie JPK_V7` — **wszystkie kotwice są zidentyfikowane w KB, zero halucynacji artykułów**.

### ⚠️ Drafty z `requires_manual_legal_anchor=true`

Opus uznał, że kotwice z retrieval'u nie są wystarczająco relevantne — te klastry potrzebują dodatkowych materiałów referencyjnych w KB od Pawła:

- **`7` — Zaliczanie okresów umów zlecenie i działalności gospodarczej do stażu pracy od 1 stycznia 2026 r.** — topic: kadry. Obecne kotwice: art. 22
- **`79` — Mały ZUS Plus – ponowne skorzystanie z ulgi po przerwie od 2026 roku** — topic: ZUS. Obecne kotwice: art. 18c, art. 36 ust. 14

---

## 3. Drafty szczegółowe (z checklist review)

### 1. Cluster `merge_120_121` — KSeF: moment podatkowy, data wystawienia faktury i ujęcie korekt w VAT/JPK

- **topic_area:** `KSeF`
- **size (źródłowych postów):** (resumed)  **avg_comments:** None
- **answer_steps:** 7  **legal_anchors:** 2  **requires_manual_legal_anchor:** `False`
- **tokens:** in=0 out=0  **elapsed:** 0.0s  **status:** ♻️ RESUMED

**Draft (JSON):**

```json
{
  "id": "wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty",
  "title": "KSeF: moment podatkowy, data wystawienia faktury i ujęcie korekt w VAT/JPK",
  "topic_area": "KSeF",
  "question_examples": [
    "Faktura kosztowa wystawiona 28 lutego, przesłana do KSeF 1 marca – w którym miesiącu odliczam VAT: w lutym czy w marcu?",
    "Faktura korygująca sprzedaży ma datę wystawienia luty, a datę sprzedaży styczeń – w którym okresie ująć ją w rejestrze VAT i JPK?",
    "Faktura za energię/usługę ciągłą: dostawa styczeń, data wystawienia luty – kiedy koszt w KPiR, a kiedy VAT?",
    "Kontrahent zrobił korektę błędnych danych nabywcy (nazwa, NIP) w styczniu do faktury grudniowej – jak zaksięgować pierwotną i korektę?",
    "Faktura z Allegro/Orange w KSeF ma 3-4 różne daty (wystawienia, sprzedaży, wysyłki do KSeF) – którą datą kierować się przy VAT i KPiR?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Ustal datę wystawienia faktury ustrukturyzowanej",
      "detail": "Dla faktur w KSeF datą wystawienia jest dzień przesłania faktury do KSeF (a nie data wpisana w polu P_1 przez wystawcę). Datą otrzymania jest dzień nadania numeru KSeF. Jeśli wystawca wpisał datę 28.02, ale faktura trafiła do KSeF 01.03 – data wystawienia to 01.03.",
      "condition": null
    },
    {
      "step": 2,
      "action": "Określ moment obowiązku podatkowego w VAT po stronie sprzedawcy",
      "detail": "Obowiązek VAT powstaje co do zasady z chwilą dokonania dostawy/wykonania usługi (art. 19a ust. 1 ustawy o VAT), niezależnie od daty wystawienia faktury w KSeF. Dla mediów, najmu, usług ciągłych – z chwilą wystawienia faktury, nie później niż z upływem terminu płatności (art. 19a ust. 5 pkt 4). Faktura z datą sprzedaży styczeń trafia do rejestru VAT stycznia, nawet gdy data wystawienia w KSeF to luty.",
      "condition": null
    },
    {
      "step": 3,
      "action": "Ustal okres odliczenia VAT po stronie nabywcy",
      "detail": "Prawo do odliczenia powstaje w okresie, w którym powstał obowiązek podatkowy u sprzedawcy, ale nie wcześniej niż w okresie otrzymania faktury (art. 86 ust. 10 i 10b pkt 1). W KSeF 'otrzymanie' = data nadania numeru KSeF. Faktura za styczeń z datą KSeF 09.02 – VAT odliczasz najwcześniej w lutym (lub w jednym z trzech kolejnych okresów).",
      "condition": null
    },
    {
      "step": 4,
      "action": "Przypisz koszt w KPiR/CIT według daty wykonania usługi lub dostawy",
      "detail": "Zasada memoriałowa: koszt przypisujesz do miesiąca, którego dotyczy (data sprzedaży/wykonania usługi), niezależnie od daty wystawienia faktury w KSeF. Na przełomie roku jest to obligatoryjne; w ciągu roku część biur księguje kaskadowo w miesiącu faktury, ale poprawnie jest zawsze w miesiącu wykonania (istotne dla JPK_CIT od 2025/2026).",
      "condition": "if podatnik prowadzi KPiR metodą memoriałową lub księgi rachunkowe"
    },
    {
      "step": 5,
      "action": "Rozksięguj fakturę korygującą według powodu korekty",
      "detail": "Korekta z powodu błędu rachunkowego lub pierwotnej wady (np. błędna cena od początku, błędna stawka) – ujmij w okresie faktury pierwotnej. Korekta z przyczyn następczych (zwrot, rabat, obniżka po sprzedaży) – ujmij w okresie uzgodnienia warunków korekty po stronie sprzedawcy (art. 29a ust. 13) i otrzymania/uzgodnienia po stronie nabywcy (art. 86 ust. 19a). Korekta wyłącznie danych formalnych (nazwa, adres, NIP – poza zmianą nabywcy) nie wpływa na VAT ani KPiR – tylko podpinasz pod fakturę pierwotną.",
      "condition": null
    },
    {
      "step": 6,
      "action": "Zweryfikuj zaciąganie dat w programie księgowym",
      "detail": "W Comarch Optima, Symfonia, Enova i wFirma import z KSeF często zaciąga datę wystawienia i datę sprzedaży z daty wpływu do KSeF – należy ręcznie skorygować datę sprzedaży na zgodną z rzeczywistym momentem dostawy (np. 31.01 zamiast 09.02), aby faktura trafiła do właściwego okresu VAT i KPiR.",
      "condition": "if program zaciąga datę z KSeF zamiast z treści faktury"
    },
    {
      "step": 7,
      "action": "Wykaż korektę w JPK_VAT z prawidłowymi datami",
      "detail": "Korekta faktury wystawiona w KSeF ma własny numer KSeF – w ewidencji JPK_VAT wykazujesz zarówno fakturę pierwotną (w swoim okresie), jak i korektę (w okresie wynikającym z kroku 5). Jeśli wystawca błędnie wystawił fakturę z datą marzec zamiast luty i skorygował ją do zera, do JPK trafia tylko prawidłowa faktura – błędnej i jej korekty nie ujmujesz w rejestrze sprzedaży (są neutralne), ale pozostają w KSeF.",
      "condition": null
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 106na ust. 1 i 3",
      "reason": "Definiuje datę wystawienia faktury ustrukturyzowanej jako dzień przesłania do KSeF oraz datę otrzymania jako dzień nadania numeru KSeF – kluczowe dla ustalenia momentu odliczenia VAT."
    },
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 106gb ust. 3",
      "reason": "Reguluje zasady wystawiania faktur korygujących w KSeF i dostępu do nich, co determinuje sposób ujęcia korekt w ewidencji JPK_VAT."
    }
  ],
  "edge_cases": [
    "Faktura VAT metoda kasowa: VAT rozliczasz w dacie zapłaty (art. 21 ustawy o VAT), niezależnie od daty wystawienia w KSeF – przy zmianie biura rachunkowego należy pobrać od klienta wyciągi bankowe i zaksięgować niezapłacone faktury dopiero po otrzymaniu płatności.",
    "Import towarów spoza UE: faktura handlowa z Chin z grudnia trafia do KPiR w dacie wystawienia (przeliczona po kursie z dnia poprzedzającego), a VAT rozliczasz dopiero z dokumentu celnego (SAD/PZC) w styczniu – dwie różne daty dla PIT i VAT.",
    "Samofakturowanie (np. Respect Energy): faktura przyjęta do KSeF 09.02 za dostawę styczniową – data sprzedaży 31.01 decyduje o okresie VAT i KPiR, nawet jeśli program zaciąga 09.02.",
    "Korekta wyłącznie danych formalnych nabywcy (literówka, adres) w KSeF – od likwidacji not korygujących wystawca musi wystawić fakturę korygującą, ale nie wpływa ona ani na VAT, ani na KPiR; podpinasz ją pod fakturę pierwotną w tym samym okresie."
  ],
  "common_mistakes": [
    "Utożsamianie daty wystawienia wpisanej w polu P_1 faktury z datą wystawienia w rozumieniu ustawy – w KSeF wiąże wyłącznie data przesłania faktury do systemu.",
    "Księgowanie kosztu w miesiącu daty wystawienia faktury z KSeF zamiast w miesiącu faktycznego wykonania usługi/dostawy – narusza zasadę memoriału i jest widoczne w JPK_CIT.",
    "Automatyczne akceptowanie dat zaciąganych przez program księgowy z KSeF bez weryfikacji daty sprzedaży z treści faktury – skutkuje błędnym okresem w JPK_VAT."
  ],
  "related_questions": [
    "Jak rozliczyć w VAT i KPiR fakturę w KSeF, gdy nabywca stosuje metodę kasową VAT?",
    "Jak ująć w JPK_VAT fakturę, która została odrzucona w KSeF i wystawiona ponownie z nowym numerem?",
    "W jakim okresie ująć fakturę korygującą in minus po stronie nabywcy, gdy została wystawiona w KSeF, ale nie otrzymano jeszcze potwierdzenia warunków korekty?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": false,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "merge_120_121",
    "cluster_label": "KSeF: moment podatkowy, data wystawienia, korekty",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "13ec08262051",
      "9e3061e1d89e",
      "0a6a302bb980",
      "ffce92b1a111",
      "ee1aeb71b3b3",
      "07236587429f",
      "51b3852c2b6d",
      "523469be3a46",
      "070829674796",
      "09eada7b424a",
      "9feb8b685618",
      "7944deb51910",
      "690761acb3a1",
      "f23c99aadca1",
      "cc7f6ae7f073"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

### 2. Cluster `7` — Zaliczanie okresów umów zlecenie i działalności gospodarczej do stażu pracy od 1 stycznia 2026 r.

- **topic_area:** `kadry`
- **size (źródłowych postów):** 797  **avg_comments:** 1.221
- **answer_steps:** 7  **legal_anchors:** 1  **requires_manual_legal_anchor:** `True`
- **tokens:** in=7635 out=3503  **elapsed:** 51.84s  **status:** ✅ OK

**Draft (JSON):**

```json
{
  "id": "wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026",
  "title": "Zaliczanie okresów umów zlecenie i działalności gospodarczej do stażu pracy od 1 stycznia 2026 r.",
  "topic_area": "kadry",
  "question_examples": [
    "Czy okres pracy na umowie zlecenie (także w trakcie studiów) wlicza się do stażu pracy i od kiedy można go zaliczyć?",
    "Jakie dokumenty pracownik musi przedstawić, aby zaliczyć do stażu pracy okres prowadzenia działalności gospodarczej oraz umów zlecenia?",
    "Czy samo zaświadczenie z ZUS wystarczy do zaliczenia umowy zlecenia do stażu pracy, czy potrzebne są też inne dokumenty?",
    "Czy mogę zaliczyć do stażu pracy umowy zlecenie studenta (poniżej 26 lat), od których nie odprowadzano składek społecznych?",
    "Czy okresy zasiłku chorobowego i macierzyńskiego w trakcie prowadzenia DG wliczają się do stażu pracy?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Zweryfikuj podstawę prawną i datę wejścia zmian",
      "detail": "Od 1 stycznia 2026 r. do stażu pracy wlicza się okresy wykonywania umowy zlecenia oraz prowadzenia pozarolniczej działalności gospodarczej, w których osoba podlegała ubezpieczeniom społecznym (emerytalnemu i rentowemu) lub była z nich zwolniona z mocy ustawy. Podstawa: znowelizowany art. 3021 Kodeksu pracy.",
      "condition": null
    },
    {
      "step": 2,
      "action": "Zażądaj od pracownika zaświadczenia US-7 z ZUS",
      "detail": "Dla okresów umów zlecenia ozusowanych oraz dla JDG – zaświadczenie ZUS US-7 (o okresach podlegania ubezpieczeniom społecznym i podstawach wymiaru składek) jest dokumentem podstawowym i rozstrzygającym. Pracownik składa wniosek przez PUE ZUS lub w placówce ZUS; ciężar udowodnienia okresu zatrudnienia spoczywa na pracowniku.",
      "condition": null
    },
    {
      "step": 3,
      "action": "Dla zleceń studenckich (bez składek ZUS) zbierz dokumenty zastępcze",
      "detail": "Jeżeli zleceniobiorca był studentem do 26. roku życia i nie podlegał składkom, zaświadczenie z ZUS nie wykaże tego okresu. Przyjmij: umowę zlecenie, rachunki, potwierdzenia przelewów, PIT-11, zaświadczenie od byłego zleceniodawcy z datami oraz zaświadczenie/legitymację potwierdzającą status studenta. Nowelizacja przewiduje zaliczanie tych okresów na podstawie innych dokumentów potwierdzających wykonywanie zlecenia.",
      "condition": "if pracownik w okresie zlecenia miał status studenta poniżej 26 lat i nie były odprowadzane składki społeczne"
    },
    {
      "step": 4,
      "action": "Sprawdź nakładanie się okresów i zastosuj zasadę niepodwajania",
      "detail": "Okresy zbiegające się (np. dwie umowy zlecenia w tym samym czasie, zlecenie + umowa o pracę, DG + zlecenie) liczą się tylko raz – analogicznie jak dwa etaty w tym samym miesiącu dają jeden miesiąc stażu. Zweryfikuj daty z US-7 i wyeliminuj duplikaty przed wprowadzeniem do systemu.",
      "condition": null
    },
    {
      "step": 5,
      "action": "Zalicz okresy zasiłkowe w ramach DG/zlecenia",
      "detail": "Okresy pobierania zasiłku chorobowego, macierzyńskiego i opiekuńczego w trakcie prowadzenia DG lub wykonywania zlecenia wliczają się do stażu pracy, o ile figurują w zaświadczeniu US-7 jako okresy podlegania ubezpieczeniom (przerwy w opłacaniu składek z tytułu zasiłku nie przerywają ciągłości ubezpieczenia).",
      "condition": "if pracownik w okresie DG/zlecenia korzystał z zasiłków z ubezpieczenia społecznego"
    },
    {
      "step": 6,
      "action": "Wprowadź zaktualizowany staż pracy do systemu kadrowo-płacowego",
      "detail": "W Comarch Optima, Symfonia Kadry i Płace lub Enova zaktualizuj kartotekę pracownika w zakładce 'Historia zatrudnienia' / 'Staż pracy', dodając okresy pozapracownicze w osobnych pozycjach z adnotacją 'zlecenie' lub 'DG' i wskazaniem dokumentu źródłowego (US-7, umowa, PIT-11). Sprawdź, czy program przelicza wymiar urlopu, nagrodę jubileuszową i dodatek stażowy.",
      "condition": null
    },
    {
      "step": 7,
      "action": "Rozróżnij staż pracy ogólny od stażu urlopowego",
      "detail": "Umowy zlecenia i DG wlicza się do stażu pracy ogólnego (decydującego m.in. o nagrodzie jubileuszowej, dodatku stażowym, okresie wypowiedzenia). Do stażu urlopowego nie wlicza się okresu nauki, jeśli w tym samym czasie pracownik wykonywał zlecenie – obowiązuje zasada korzystniejszego dla pracownika okresu, bez podwajania.",
      "condition": null
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Kodeks pracy",
      "article_number": "art. 22",
      "reason": "Definiuje stosunek pracy i odróżnia go od zatrudnienia cywilnoprawnego, co jest podstawą do wyodrębnienia okresów zlecenia i DG jako okresów pozapracowniczych zaliczanych do stażu pracy od 2026 r."
    }
  ],
  "edge_cases": [
    "Umowa zlecenie studenta poniżej 26 r.ż. bez składek – brak wpisu w ZUS, zaliczenie możliwe na podstawie umowy, rachunków, przelewów i PIT-11 oraz zaświadczenia o studiach.",
    "Nakładające się okresy (dwa zlecenia równolegle, zlecenie w trakcie umowy o pracę, DG + zlecenie) – liczą się jednokrotnie, nie sumujemy równoległych okresów.",
    "Brak dokumentów źródłowych sprzed wielu lat (np. zlecenie z lat 2002–2003, zleceniodawca już nie istnieje) – pracownik składa wniosek USP w ZUS; jeśli okres nie był ozusowany, udowodnienie może być niemożliwe.",
    "Okresy zasiłków (chorobowy, macierzyński, opiekuńczy) w trakcie DG – wliczają się do stażu, jeśli wynikają z zaświadczenia ZUS; sama przerwa w opłacaniu składek w tym czasie nie wyklucza zaliczenia."
  ],
  "common_mistakes": [
    "Opieranie się wyłącznie na umowie zlecenia lub oświadczeniu pracownika bez zaświadczenia US-7 z ZUS – z samej umowy nie wynika, czy składki były faktycznie odprowadzane.",
    "Podwójne liczenie nakładających się okresów (np. równoległe zlecenia u dwóch zleceniodawców lub zlecenie w trakcie etatu).",
    "Mylenie stażu pracy ogólnego ze stażem urlopowym – zaliczanie okresu studiów i jednocześnie zlecenia wykonywanego w trakcie studiów do stażu urlopowego (podczas gdy przepisy przewidują wybór korzystniejszego, bez dublowania)."
  ],
  "related_questions": [
    "Jak udokumentować staż pracy na podstawie umowy B2B wykonywanej za granicą na rzecz polskiego kontrahenta?",
    "Czy okres pobierania zasiłku dla bezrobotnych wlicza się do stażu pracy na nowych zasadach od 2026 r.?",
    "Jak od 2026 r. zaliczać staż pracy osobom, które prowadziły gospodarstwo rolne lub były pomocnikami rolnika (KRUS)?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": true,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "7",
    "cluster_label": "Zaliczanie umów zlecenie i DG do stażu pracy od 2026",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "5524fe102d29",
      "075e641c91f8",
      "ecb07ec14ab2",
      "c5ee58a04c1b",
      "e421511893dd",
      "94341fe9b112",
      "bec7fb3eb05a",
      "f72745fbf5da",
      "092d5d130fbb",
      "731739f57810",
      "4de044192293",
      "7e08ae2a5d4b",
      "a2c973af8523"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

### 3. Cluster `63` — Leasing operacyjny samochodu osobowego – limity KUP i odliczenie VAT

- **topic_area:** `PIT`
- **size (źródłowych postów):** 359  **avg_comments:** 1.44
- **answer_steps:** 7  **legal_anchors:** 3  **requires_manual_legal_anchor:** `False`
- **tokens:** in=7749 out=3751  **elapsed:** 56.9s  **status:** ✅ OK

**Draft (JSON):**

```json
{
  "id": "wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat",
  "title": "Leasing operacyjny samochodu osobowego – limity KUP i odliczenie VAT",
  "topic_area": "PIT",
  "question_examples": [
    "Samochód osobowy w leasingu operacyjnym o wartości powyżej 100 tys. zł netto, zgłoszony do VAT-26 – czy raty leasingowe odliczam w proporcji, czy w całości?",
    "Nie jestem VAT-owcem, leasing operacyjny auta osobowego – czy fakturę leasingową księguję w 100% czy 75% w KUP?",
    "Leasing operacyjny, użytek mieszany – jaką kwotę z umowy leasingu biorę do wyliczenia proporcji KUP (brutto z wyposażeniem czy netto do amortyzacji)?",
    "Auto osobowe w leasingu o wartości netto 170 tys. zł wykorzystywane do wynajmu (100% VAT) – jak rozliczam raty oraz koszty eksploatacji (paliwo, naprawy)?",
    "Czy samochody wprowadzone do leasingu/EŚT do 31.12.2025 zachowują dotychczasowy limit 150 000 zł, czy od 1.01.2026 obowiązuje limit 100 000 zł?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Ustal podstawę wartości samochodu dla proporcji KUP",
      "detail": "Weź wartość samochodu z umowy leasingu (pozycja 'wartość przedmiotu wraz z wyposażeniem dodatkowym'). Dla VAT-owca odliczającego 50% VAT – do limitu doliczasz 50% nieodliczonego VAT. Dla nie-VAT-owca lub pełne 50% nieodliczalne – wartość brutto. Dla pełnego odliczenia 100% VAT – wartość netto.",
      "condition": null
    },
    {
      "step": 2,
      "action": "Porównaj wartość samochodu z obowiązującym limitem KUP",
      "detail": "Limit 150 000 zł stosujesz dla umów zawartych do 31.12.2025 (samochody spalinowe/hybrydowe) oraz 225 000 zł dla elektryków. Od 1.01.2026 limit dla samochodów spalinowych emitujących >50g CO2/km spada do 100 000 zł (umowy zawarte od tej daty). Umowa podpisana i auto wydane do 31.12.2025 – zachowuje limit 150 000 zł na cały okres leasingu.",
      "condition": "if wartość samochodu > obowiązujący limit"
    },
    {
      "step": 3,
      "action": "Wylicz współczynnik proporcji KUP dla części kapitałowej raty",
      "detail": "Proporcja = limit KUP / wartość samochodu (ta sama baza co w kroku 1). Np. auto 200 000 zł netto, VAT 100% odliczalny, limit 150 000 → proporcja 75%. Mnożnik stosujesz do części kapitałowej raty (spłata wartości) oraz opłaty wstępnej. Część odsetkowa raty – całość w KUP bez proporcji.",
      "condition": "if leasing operacyjny i wartość > limit"
    },
    {
      "step": 4,
      "action": "Określ odliczenie VAT od rat leasingowych",
      "detail": "Przy użytku mieszanym: 50% VAT z faktury (bez limitu kwotowego na ratę, limit 150 tys. zł dot. tylko KUP). Przy zgłoszeniu VAT-26 + ewidencja przebiegu + regulamin: 100% VAT. Jeśli podatnik prowadzi sprzedaż mieszaną – dodatkowo stosuj współczynnik sprzedaży (art. 90 VAT).",
      "condition": null
    },
    {
      "step": 5,
      "action": "Zaksięguj koszty eksploatacji odrębnie od rat leasingowych",
      "detail": "Paliwo, naprawy, myjnia, części: przy użytku mieszanym – 75% w KUP i 50% VAT; przy VAT-26 – 100% KUP i 100% VAT. Ubezpieczenie OC/NNW/Assistance wyodrębnione na polisie – 100% KUP. AC/GAP – proporcja do limitu 150 000 zł liczona od wartości samochodu z polisy.",
      "condition": null
    },
    {
      "step": 6,
      "action": "Wprowadź pojazd i ustawienia proporcji do programu księgowego",
      "detail": "W Comarch Optima (moduł Środki Trwałe → Pojazdy) lub WFirma (Pojazdy → Dodaj pojazd) ustaw: typ użytkowania (mieszany/firmowy), wartość pojazdu, datę zawarcia umowy leasingu, status VAT-26. Program automatycznie zastosuje proporcję KUP i odliczenie VAT przy księgowaniu faktur.",
      "condition": null
    },
    {
      "step": 7,
      "action": "Przy najmie długoterminowym zastosuj analogiczne zasady jak do leasingu",
      "detail": "Dla umów najmu powyżej 6 miesięcy wartość samochodu przyjmuj z polisy AC (rynkowa wartość pojazdu) lub od wynajmującego. Proporcja KUP i ograniczenia VAT – identyczne jak przy leasingu operacyjnym. Najem krótkoterminowy (≤6 mies.) – bez limitu wartości, tylko ograniczenia VAT i 75% KUP przy mieszanym.",
      "condition": "if umowa najmu/dzierżawy zamiast leasingu"
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 86a ust. 1-3",
      "reason": "Reguluje zasadę 50% odliczenia VAT przy użytku mieszanym oraz 100% przy wykorzystaniu wyłącznie do działalności (VAT-26 + ewidencja przebiegu)."
    },
    {
      "law_name": "Ustawa o PIT",
      "article_number": "art. 23 ust. 1 pkt 47a oraz ust. 5c",
      "reason": "Wprowadza limit 150 000 zł (225 000 zł dla elektryków) dla opłat leasingowych w części dotyczącej spłaty wartości samochodu osobowego oraz zasadę proporcjonalnego zaliczania do KUP."
    },
    {
      "law_name": "Ustawa o PIT",
      "article_number": "art. 23 ust. 1 pkt 46a",
      "reason": "Określa zaliczanie 75% wydatków eksploatacyjnych do KUP przy użytku mieszanym samochodu osobowego."
    }
  ],
  "edge_cases": [
    "Umowa leasingu zawarta do 31.12.2025 – zachowuje limit 150 000 zł przez cały okres trwania, nawet po wejściu nowego limitu 100 000 zł od 1.01.2026 (zasada ochrony praw nabytych, art. 23 ust. 5c PIT).",
    "Samochód z homologacją ciężarową (np. Renault Master z częścią ładunkową, brak wpisu VAT w dowodzie) – mimo zgłoszenia VAT-26 może być traktowany jako osobowy dla celów PIT, co wymusza proporcję KUP do limitu.",
    "Sprzedaż mieszana VAT (proporcja sprzedaży np. 79%) – odliczenie VAT liczysz dwukrotnie: najpierw 50% z art. 86a, następnie wskaźnikiem sprzedaży. Nieodliczony VAT zwiększa wartość samochodu przyjmowaną do proporcji KUP.",
    "Wykup z leasingu do majątku prywatnego + dalsze wykorzystanie do działalności bez wprowadzania do EŚT – brak prawa do odliczenia VAT z faktury wykupu; przy bieżących wydatkach eksploatacyjnych przysługuje 20% KUP i 50% VAT (auto prywatne używane w firmie)."
  ],
  "common_mistakes": [
    "Stosowanie proporcji 75% KUP do części kapitałowej raty leasingu operacyjnego zamiast proporcji wartościowej (limit/wartość auta) – 75% dotyczy tylko wydatków eksploatacyjnych, nie rat leasingowych.",
    "Ograniczanie części odsetkowej raty leasingowej proporcją – część odsetkowa zalicza się w 100% do KUP bez względu na wartość samochodu.",
    "Przyjmowanie wartości netto do proporcji przy użytku mieszanym (50% VAT) – prawidłowa podstawa to netto + 50% nieodliczonego VAT (wartość 'przeliczeniowa')."
  ],
  "related_questions": [
    "Jak rozliczyć wykup samochodu z leasingu operacyjnego do majątku prywatnego i późniejszą sprzedaż – kiedy powstaje przychód z działalności?",
    "Czy opłata wstępna (czynsz inicjalny) w leasingu operacyjnym podlega tej samej proporcji KUP co raty i czy można ją rozliczyć jednorazowo?",
    "Jak rozliczyć leasing finansowy samochodu osobowego – amortyzacja, część odsetkowa, limit 150/100 tys. zł i moment ujęcia w KUP?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": false,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "63",
    "cluster_label": "Leasing samochodu osobowego: limity KUP i odliczenie VAT",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "30ae43f4a41f",
      "12186b408679",
      "41fb4a9ab5bf",
      "da48d3b87055",
      "0e18f16496f5",
      "dbbf35141d4d",
      "fb5fb9a5b858",
      "a613b2c010fd",
      "3124364db736",
      "546f2867cc73",
      "894a1d6aed44",
      "6cc60c254f19"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

### 4. Cluster `79` — Mały ZUS Plus – ponowne skorzystanie z ulgi po przerwie od 2026 roku

- **topic_area:** `ZUS`
- **size (źródłowych postów):** 306  **avg_comments:** 1.389
- **answer_steps:** 7  **legal_anchors:** 2  **requires_manual_legal_anchor:** `True`
- **tokens:** in=8086 out=3699  **elapsed:** 55.77s  **status:** ✅ OK

**Draft (JSON):**

```json
{
  "id": "wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026",
  "title": "Mały ZUS Plus – ponowne skorzystanie z ulgi po przerwie od 2026 roku",
  "topic_area": "ZUS",
  "question_examples": [
    "Klient wykorzystał już 36 miesięcy Małego ZUS Plus w latach 2020-2022, a w 2023-2025 opłacał duży ZUS – czy od 1 stycznia 2026 może ponownie skorzystać z ulgi i rozpocząć nowy okres 36 miesięcy?",
    "Przedsiębiorca był w 2025 na dużym ZUS, ale jego przychody nie przekroczyły 120 tys. zł i prowadził firmę cały rok – czy może od 2026 wejść na Mały ZUS Plus?",
    "Czy jeśli podatnik wykorzystał 12 miesięcy Małego ZUS Plus w 2025 i przegapił termin styczniowy, może zawiesić działalność z datą wsteczną i zgłosić się do ulgi po wznowieniu?",
    "Czy osoba, która zawiesi firmę na styczeń i wznowi w lutym 2026, może wejść na Mały ZUS Plus od lutego i ile dni ma na zgłoszenie?",
    "Przedsiębiorca wykorzystał 6 m-cy ulgi na start, 24 m-ce preferencji, a w 2025 przez 8 miesięcy miał zawieszoną działalność – czy może od stycznia 2026 przejść na Mały ZUS Plus?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Zweryfikuj limit przychodu za 2025 rok",
      "detail": "Sprawdź w KPiR / ewidencji przychodów, czy przychód z działalności w 2025 r. nie przekroczył 120 000 zł (próg proporcjonalny, jeśli działalność prowadzona krócej niż cały rok). Bez spełnienia tego warunku Mały ZUS Plus w 2026 nie przysługuje.",
      "condition": null
    },
    {
      "step": 2,
      "action": "Sprawdź minimalny okres prowadzenia działalności w poprzednim roku",
      "detail": "Ustal, czy przedsiębiorca prowadził JDG w 2025 r. przez co najmniej 60 dni kalendarzowych (okresy zawieszenia NIE wliczają się do tych 60 dni). Jeśli nie – ulga nie przysługuje w 2026 r.",
      "condition": null
    },
    {
      "step": 3,
      "action": "Zweryfikuj wykorzystane wcześniej miesiące Małego ZUS Plus",
      "detail": "W danych płatnika na PUE ZUS (zakładka Ubezpieczony → Ulgi) lub w historii kodów tytułu ubezpieczenia (0590) policz, ile miesięcy Małego ZUS Plus wykorzystano w ostatnich 60 miesiącach kalendarzowych. Ulga przysługuje maksymalnie 36 miesięcy w ciągu kolejnych 60 miesięcy – po upływie 60 m-cy licznik się zeruje.",
      "condition": null
    },
    {
      "step": 4,
      "action": "Wyklucz przesłanki negatywne",
      "detail": "Sprawdź, czy klient nie świadczy w 2026 r. usług na rzecz byłego pracodawcy tożsamych z wykonywanymi w ramach stosunku pracy w bieżącym lub poprzednim roku kalendarzowym, oraz czy nie rozlicza się kartą podatkową ze zwolnieniem z VAT. Te okoliczności wykluczają prawo do ulgi niezależnie od pozostałych warunków.",
      "condition": null
    },
    {
      "step": 5,
      "action": "Dokonaj przerejestrowania kodu tytułu ubezpieczenia na 0590",
      "detail": "Złóż ZUS ZWUA z dotychczasowym kodem (0510 / 0570) z datą 31.12.2025 oraz ZUS ZUA/ZZA z kodem 0590 od 01.01.2026. W Comarch Optima / WFirma / Symfonia ustaw schemat składek „Mały ZUS Plus” od stycznia 2026. Termin: do 31 stycznia 2026 r.",
      "condition": "if klient kontynuuje działalność bez przerwy od stycznia 2026"
    },
    {
      "step": 6,
      "action": "Zgłoś Mały ZUS Plus w ciągu 7 dni od wznowienia działalności",
      "detail": "Jeśli działalność jest zawieszona w styczniu i wznawiana w trakcie 2026 r., przedsiębiorca ma 7 dni od dnia wznowienia na złożenie ZUA z kodem 0590. Nie obowiązuje go wtedy termin 31 stycznia.",
      "condition": "if działalność zawieszona w styczniu 2026 i wznowiona później"
    },
    {
      "step": 7,
      "action": "Złóż DRA cz. II (ZUS DRA II) za styczeń lub pierwszy miesiąc ulgi",
      "detail": "Wraz z pierwszym DRA (do 20 lutego 2026 lub do 20. dnia miesiąca po wznowieniu) złóż DRA II z wyliczeniem podstawy według dochodu z 2025 r. Jeśli kontynuujesz ulgę z 2025 r. bez przerwy – nie trzeba się wyrejestrowywać, ale DRA II za 2026 trzeba złożyć ponownie z nową podstawą.",
      "condition": null
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Ustawa o systemie ubezpieczeń społecznych",
      "article_number": "art. 18c",
      "reason": "Przepis określa warunki, limity przychodu i dochodu oraz zasady 36/60 miesięcy korzystania z Małego ZUS Plus, w tym ograniczenia podmiotowe (świadczenie na rzecz byłego pracodawcy, karta podatkowa)."
    },
    {
      "law_name": "Ustawa o systemie ubezpieczeń społecznych",
      "article_number": "art. 36 ust. 14",
      "reason": "Reguluje termin 7 dni na zgłoszenie zmiany kodu tytułu ubezpieczenia od dnia zaistnienia zmiany (wznowienie działalności) oraz termin do 31 stycznia na zgłoszenie do Małego ZUS Plus w przypadku kontynuacji."
    }
  ],
  "edge_cases": [
    "Zawieszenie działalności NIE przerywa biegu 24 miesięcy preferencyjnych składek (kod 0570) – ZUS liczy je ciągiem od dnia rozpoczęcia JDG, niezależnie od przerw (potwierdzone decyzjami ZUS).",
    "Jeśli przedsiębiorca kontynuuje Mały ZUS Plus z 2025 r. na 2026 r. bez wykorzystania pełnych 36 m-cy, nie musi się wyrejestrowywać ani ponownie zgłaszać z kodem 0590 – wystarczy przeliczyć podstawę i złożyć nowe DRA II.",
    "Po wykorzystaniu pełnych 36 miesięcy Małego ZUS Plus trzeba opłacać duży ZUS (0510) przez kolejne 24 miesiące, zanim licznik 60-miesięczny pozwoli ponownie skorzystać z ulgi – chyba że cała „60-ka” się zakończyła.",
    "Świadczenie usług na rzecz byłego pracodawcy tożsamych z pracą z etatu wyklucza Mały ZUS Plus aż do momentu zaprzestania tej współpracy + upływu karencji; ta sama przesłanka wyklucza wakacje składkowe."
  ],
  "common_mistakes": [
    "Mylenie kodu preferencyjnych składek (0570) z kodem Małego ZUS Plus (0590) – po zakończeniu 24 m-cy preferencji trzeba aktywnie zgłosić się na 0590, samo pozostanie na 0570 powoduje przejście na duży ZUS.",
    "Przegapienie terminu 31 stycznia przy kontynuacji działalności – po tym terminie wejście na Mały ZUS Plus możliwe dopiero w kolejnym roku albo poprzez wznowienie zawieszonej działalności (wtedy 7 dni).",
    "Liczenie 60 dni prowadzenia działalności łącznie z okresami zawieszenia – dni zawieszenia nie wliczają się do minimalnego okresu kwalifikującego do ulgi."
  ],
  "related_questions": [
    "Jak obliczyć podstawę wymiaru składek Mały ZUS Plus na 2026 rok przy dochodzie mieszanym (część roku preferencja, część duży ZUS)?",
    "Czy okres korzystania z wakacji składkowych wlicza się do 36 miesięcy limitu Małego ZUS Plus?",
    "Jakie skutki ma przekroczenie limitu 120 tys. zł przychodu w trakcie roku korzystania z Małego ZUS Plus?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": true,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "79",
    "cluster_label": "Mały ZUS Plus: ponowne skorzystanie po przerwie 2026",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "41ca3a49bde1",
      "e3c79fc941c6",
      "5a0807305ab1",
      "31814fa720f1",
      "e8deddedd686",
      "0eb9cea002fc",
      "1d98d179fc35",
      "caf6d889df11",
      "610436ca9fe9",
      "05ed43bceaff",
      "dbd79b2a110f",
      "333944e06267",
      "db98dce421d0",
      "3d1f3d7ba9d7",
      "7ec80ae95c6e"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

### 5. Cluster `49` — Środki trwałe do 10 tys. zł i powyżej – wybór między kosztami bezpośrednimi, jednorazową amortyzacją a amortyzacją liniową

- **topic_area:** `KPiR`
- **size (źródłowych postów):** 288  **avg_comments:** 1.028
- **answer_steps:** 7  **legal_anchors:** 3  **requires_manual_legal_anchor:** `False`
- **tokens:** in=7434 out=4081  **elapsed:** 60.54s  **status:** ✅ OK

**Draft (JSON):**

```json
{
  "id": "wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie",
  "title": "Środki trwałe do 10 tys. zł i powyżej – wybór między kosztami bezpośrednimi, jednorazową amortyzacją a amortyzacją liniową",
  "topic_area": "KPiR",
  "question_examples": [
    "Czy zakup sprzętu za 5 600 zł netto muszę ująć jako jednorazową amortyzację, czy mogę wrzucić bezpośrednio w koszty bez wpisu do ewidencji środków trwałych?",
    "Czy sprzęt poniżej 10 tys. zł używany dłużej niż rok musi być wprowadzony na ewidencję środków trwałych?",
    "Klient kupił w grudniu 4 maszyny poniżej 10 tys. zł każda – czy mogę zastosować amortyzację liniową, żeby odpisy obniżały podstawę opodatkowania w kolejnym roku?",
    "Czy nowe meble biurowe mogę zamortyzować jednorazowo w ramach limitu 100 000 zł dla fabrycznie nowych środków trwałych (bez de minimis)?",
    "Czy mogę jednorazowo zamortyzować środek trwały o wartości 23 tys. zł netto w ramach pomocy de minimis?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Ustal wartość początkową składnika majątku netto (dla czynnego podatnika VAT) lub brutto (dla nie-VATowca) oraz przewidywany okres używania.",
      "detail": "Jeśli wartość ≤ 10 000 zł i okres używania > 1 rok – masz trzy ścieżki do wyboru (patrz krok 2). Jeśli wartość > 10 000 zł i okres używania > 1 rok – musi trafić do ewidencji środków trwałych i być amortyzowany.",
      "condition": null
    },
    {
      "step": 2,
      "action": "Wybierz jedną z trzech opcji dla składnika o wartości ≤ 10 000 zł.",
      "detail": "Opcja A: zaliczenie bezpośrednio w koszty (kol. 13 KPiR) bez wprowadzania do ewidencji – art. 22d ust. 1 ustawy o PIT. Opcja B: wpis do ewidencji ŚT i jednorazowy odpis amortyzacyjny w miesiącu przyjęcia do używania lub miesiącu następnym – art. 22f ust. 3 PIT. Opcja C: wpis do ewidencji ŚT i amortyzacja liniowa według stawek z Wykazu. Decyzję podejmuje podatnik, kierując się optymalizacją podatkową.",
      "condition": "if wartość początkowa ≤ 10 000 zł"
    },
    {
      "step": 3,
      "action": "Sprawdź możliwość skorzystania z jednorazowej amortyzacji dla składnika > 10 000 zł.",
      "detail": "Dostępne są dwie ścieżki: (1) jednorazowa amortyzacja de minimis do 50 000 euro rocznie dla małych podatników i rozpoczynających działalność (art. 22k ust. 7 PIT) – obejmuje grupy KŚT 3–8 z wyłączeniem samochodów osobowych; (2) jednorazowa amortyzacja fabrycznie nowych ŚT do 100 000 zł rocznie (art. 22k ust. 14 PIT) – tylko grupy KŚT 3–6 i 8, bez grupy 7 (środki transportu).",
      "condition": "if wartość > 10 000 zł i chcesz przyspieszyć rozliczenie"
    },
    {
      "step": 4,
      "action": "Zweryfikuj status podatnika i limity pomocy de minimis przed wyborem art. 22k ust. 7.",
      "detail": "Mały podatnik to ten, u którego przychody brutto w poprzednim roku nie przekroczyły 2 mln euro. Przy przychodzie ok. 8 mln zł status małego podatnika jest zachowany, ale sprawdź dostępny limit de minimis (300 tys. euro w 3 latach). Pamiętaj, że pomocą de minimis jest tylko korzyść podatkowa (różnica między podatkiem przy jednorazowej a liniowej amortyzacji), a nie cała wartość odpisu.",
      "condition": "if wybrano jednorazową amortyzację de minimis"
    },
    {
      "step": 5,
      "action": "Wprowadź środek trwały do ewidencji i zaksięguj odpis w programie księgowym.",
      "detail": "W Comarch Optima / WFirma / Symfonia: utwórz kartę ŚT, przypisz KŚT (np. 669 dla testera diagnostycznego, 808 dla mebli biurowych), ustal metodę i stawkę amortyzacji, wygeneruj dokument OT. Odpis trafia do kol. 13 KPiR w dacie wynikającej z wybranej metody (miesiąc następny po przyjęciu dla liniowej; miesiąc przyjęcia lub następny dla jednorazowej).",
      "condition": "if składnik trafia do ewidencji ŚT"
    },
    {
      "step": 6,
      "action": "Przy ulepszeniu istniejącego ŚT o kwotę > 10 000 zł w roku – zwiększ wartość początkową, nie księguj w koszty bezpośrednie.",
      "detail": "Art. 22g ust. 17 PIT: suma wydatków na ulepszenie (przebudowa, rozbudowa, rekonstrukcja, adaptacja, modernizacja) przekraczająca 10 000 zł rocznie zwiększa wartość początkową ŚT. Od zwiększonej podstawy naliczasz dalsze odpisy według dotychczasowej metody. Jest to istotne wobec wchodzącego JPK_ST.",
      "condition": "if dotyczy ulepszenia istniejącego ŚT"
    },
    {
      "step": 7,
      "action": "Przy sprzedaży ŚT wykaż w PIT-36/36L zał. B wartość początkową jako przychód i niezamortyzowaną (nieumorzoną) część jako koszt.",
      "detail": "Kosztem uzyskania przychodów przy odpłatnym zbyciu ŚT jest wartość początkowa pomniejszona o sumę dokonanych odpisów amortyzacyjnych (art. 23 ust. 1 pkt 1 PIT). Przychodem – cena sprzedaży. W praktyce w kosztach wykazujesz wartość nieumorzoną, nie pełną wartość początkową.",
      "condition": "if następuje sprzedaż ŚT"
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
      "article_number": "art. 22d ust. 1 oraz art. 22f ust. 3",
      "reason": "Określa prawo podatnika do nieujmowania w ewidencji ŚT składników o wartości ≤ 10 000 zł i zaliczenia wydatku bezpośrednio w koszty lub jednorazowego odpisu."
    },
    {
      "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
      "article_number": "art. 22k ust. 7 oraz art. 22k ust. 14",
      "reason": "Reguluje jednorazową amortyzację w ramach pomocy de minimis (limit 50 000 euro) oraz jednorazową amortyzację fabrycznie nowych ŚT z grup 3–6 i 8 (limit 100 000 zł)."
    },
    {
      "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
      "article_number": "art. 22h ust. 2",
      "reason": "Nakazuje kontynuację raz wybranej metody amortyzacji do pełnego zamortyzowania – kluczowe przy decyzji między liniową a jednorazową."
    }
  ],
  "edge_cases": [
    "Mieszkanie wykorzystywane jako lokal firmy – od 2023 r. podatkowo nie można go amortyzować (art. 22c pkt 2 PIT), ale bilansowo amortyzacja jest nadal dokonywana.",
    "Spółka z o.o. kupująca fabrycznie nowy kocioł węglowy (35 tys. zł) – może skorzystać z art. 16k ust. 14 CIT (limit 100 tys. zł), ale samochód dostawczy 3,5 t (grupa 7) jest wyłączony i musi być amortyzowany standardowo.",
    "Zaświadczenie z US o pomocy de minimis pokazuje tylko korzyść podatkową (np. 4,3 tys. zł przy ŚT za 90 tys. zł), a nie pełną wartość odpisu – to różnica między podatkiem przy jednorazowej a rozłożonej amortyzacji.",
    "Środek trwały zakupiony na fakturę z NIP-em przedsiębiorcy wprowadzamy do ewidencji na podstawie faktury zakupu + OT; oświadczenie o przekazaniu na potrzeby działalności stosuje się dla majątku prywatnego."
  ],
  "common_mistakes": [
    "Wykazywanie przy sprzedaży ŚT w kosztach pełnej wartości początkowej zamiast wartości niezamortyzowanej (nieumorzonej).",
    "Mylenie limitu jednorazowej amortyzacji fabrycznie nowych ŚT (100 tys. zł, grupy 3–6 i 8) z de minimis (50 tys. euro, grupy 3–8) – a są to dwa niezależne instrumenty.",
    "Księgowanie ulepszenia ŚT > 10 000 zł jako niskocennego wyposażenia zamiast zwiększenia wartości początkowej środka trwałego."
  ],
  "related_questions": [
    "Jak ustalić wartość początkową środka trwałego wniesionego z majątku prywatnego do działalności gospodarczej?",
    "Jakie stawki amortyzacji indywidualnej można zastosować dla używanych środków trwałych i jakie są warunki (art. 22j PIT)?",
    "Czy leasing operacyjny środka trwałego wyklucza możliwość późniejszej jednorazowej amortyzacji po wykupie?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": false,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "49",
    "cluster_label": "Środki trwałe: jednorazowa amortyzacja vs koszty bezpośrednie",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "d28558e44602",
      "03f11e507249",
      "a75c246c7484",
      "1445de9be31a",
      "4ab142baaa40",
      "22b95ef77ec3",
      "113f97c2a1a0",
      "b8dbe45628ed",
      "1ba52ae2b9ef",
      "70876af50688",
      "54c4757d43c5",
      "c0eece56491e",
      "fa1369aea058",
      "581d6a6893d2",
      "0522495a4cf8"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

### 6. Cluster `10` — Potrącenia komornicze niealimentacyjne z wynagrodzeń, zasiłków i umów zlecenia

- **topic_area:** `kadry`
- **size (źródłowych postów):** 212  **avg_comments:** 1.302
- **answer_steps:** 7  **legal_anchors:** 2  **requires_manual_legal_anchor:** `False`
- **tokens:** in=15979 out=7872  **elapsed:** 117.57s  **status:** ✅ OK

**Draft (JSON):**

```json
{
  "id": "wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece",
  "title": "Potrącenia komornicze niealimentacyjne z wynagrodzeń, zasiłków i umów zlecenia",
  "topic_area": "kadry",
  "question_examples": [
    "Pracownik zarabia minimalne wynagrodzenie (ok. 4666 zł brutto) i ma zajęcie niealimentacyjne - czy muszę coś potrącać?",
    "Pracownik ma umowę zlecenie ok. 1700 zł brutto, przyszło pismo od komornika - potrącam całość czy zostawiam kwotę wolną?",
    "W grudniu wypłacam świadczenie z ZFŚS, nagrodę i wynagrodzenie - czy potrącenie komornicze liczyć osobno od każdej kwoty czy od sumy?",
    "Pracownik ma wynagrodzenie za pracę 1108 zł brutto i zasiłek wypadkowy 4246 zł - ile potrącę z tytułu zajęcia niealimentacyjnego?",
    "Z trzynastki potrącam 50% netto dla komornika, czy sumuję ją z wynagrodzeniem miesięcznym i liczę limit łącznie?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Ustal tytuł zajęcia i zakres objęcia",
      "detail": "Przeczytaj pismo komornika i sprawdź, czy zajęcie obejmuje wynagrodzenie za pracę, wierzytelności z umów cywilnoprawnych, zasiłki czy inne świadczenia. Od tego zależy, jakie limity potrąceń stosujesz (art. 87-871 KP dotyczą wyłącznie stosunku pracy).",
      "condition": null
    },
    {
      "step": 2,
      "action": "Zastosuj limit 50% wynagrodzenia netto i kwotę wolną dla umowy o pracę",
      "detail": "Przy zajęciu niealimentacyjnym maksymalne potrącenie to 50% wynagrodzenia netto po odliczeniu ZUS, zaliczki PIT i PPK. Kwota wolna to 100% minimalnego wynagrodzenia netto (pełny etat) - w 2025/2026 przy minimalnej krajowej pracownik na pełnym etacie z podstawowymi kosztami i ulgą zazwyczaj nie ma potrącenia w ogóle. W Comarch Optima/Symfonia wprowadź zajęcie jako 'Komornicze inne' i ustaw typ 'niealimentacyjne'.",
      "condition": "if tytuł zajęcia to wynagrodzenie ze stosunku pracy"
    },
    {
      "step": 3,
      "action": "Zsumuj wszystkie składniki wypłaty z danego miesiąca przed wyliczeniem potrącenia",
      "detail": "Wynagrodzenie zasadnicze, premia, nagroda, trzynastka, ekwiwalent za urlop - wszystko co stanowi wynagrodzenie za pracę sumujesz i od łącznej kwoty netto liczysz 50% oraz kwotę wolną (nie osobno od każdego składnika). Świadczenia z ZFŚS co do zasady NIE podlegają egzekucji przy zajęciu wynagrodzenia (chyba że pismo obejmuje wierzytelności).",
      "condition": "if w miesiącu wypłacasz kilka składników wynagrodzenia"
    },
    {
      "step": 4,
      "action": "Dla umowy zlecenia potrąć całą kwotę, chyba że zleceniobiorca udokumentuje ochronę",
      "detail": "Umowy cywilnoprawne nie są chronione limitami z Kodeksu pracy. Potrącasz 100% wynagrodzenia - CHYBA że zleceniobiorca dostarczy pismo komornika potwierdzające, że zlecenie jest jego jedynym, powtarzającym się źródłem utrzymania (art. 833 § 2 i 2¹ KPC) - wtedy stosujesz limity jak przy umowie o pracę. Pracownik musi sam złożyć wniosek do komornika.",
      "condition": "if zajęcie dotyczy umowy zlecenia"
    },
    {
      "step": 5,
      "action": "Dla zasiłków z ubezpieczenia społecznego zastosuj limity z ustawy emerytalnej",
      "detail": "Z zasiłku chorobowego, opiekuńczego, macierzyńskiego, wypadkowego przy zajęciu niealimentacyjnym maksymalne potrącenie to 25% świadczenia brutto. Kwota wolna to 825 zł miesięcznie (stan na 2025 r., waloryzowana corocznie w marcu), liczona proporcjonalnie do liczby dni zasiłku. Limity te stosuje się osobno od limitów wynagrodzenia za pracę.",
      "condition": "if pracownik otrzymuje zasiłek ZUS w danym miesiącu"
    },
    {
      "step": 6,
      "action": "Przy zbiegu egzekucji alimentacyjnej i niealimentacyjnej zachowaj łączny limit 60%",
      "detail": "Najpierw potrąć alimenty (do 60% netto, bez kwoty wolnej), potem niealimentacyjne - ale łącznie nie więcej niż 60% wynagrodzenia netto. Przy zbiegu zajęć od różnych komorników lub komornik + ZUS zgłoś zbieg do organu właściwego (komornik 'wygrywa' z ZUS przy egzekucji niealimentacyjnej - patrz art. 773 KPC).",
      "condition": "if występuje kilka zajęć jednocześnie"
    },
    {
      "step": 7,
      "action": "Przekaż potrąconą kwotę komornikowi i wyślij odpowiedź w 7 dni",
      "detail": "W ciągu 7 dni od otrzymania pisma odpowiedz komornikowi (formularz z zajęcia): podaj wysokość wynagrodzenia, inne zajęcia, przeszkody w wypłacie. Potrąconą kwotę przelewaj w terminie wypłaty na rachunek wskazany w piśmie. Potrącenie ewidencjonuj na liście płac jako osobną pozycję - w Optimie/Symfonii/Enova dodaj element 'Potrącenie komornicze'.",
      "condition": null
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Kodeks pracy",
      "article_number": "art. 87¹",
      "reason": "Określa kwotę wolną od potrąceń w wysokości minimalnego wynagrodzenia netto przy zajęciach niealimentacyjnych - to kluczowa podstawa ochrony pracownika."
    },
    {
      "law_name": "Kodeks pracy",
      "article_number": "art. 87",
      "reason": "Ustala kolejność i limity potrąceń z wynagrodzenia za pracę - 50% przy egzekucji niealimentacyjnej i 60% łącznie przy zbiegu z alimentami."
    }
  ],
  "edge_cases": [
    "Umowa zlecenie jako jedyne źródło utrzymania - po dostarczeniu przez zleceniobiorcę pisma od komornika stosujemy limity jak przy umowie o pracę (art. 833 § 2¹ KPC).",
    "Dwie wypłaty w jednym miesiącu kalendarzowym (np. wypłata grudniowa + styczniowa wypłacona 31.12) - potrącenie liczymy od łącznego przychodu miesiąca; druga wypłata może w całości pójść do komornika jeśli kwota wolna została już wykorzystana.",
    "Pracownik tylko na zasiłku (bez wynagrodzenia za pracę) - stosujemy wyłącznie limity z ustawy emerytalnej (25% brutto, kwota wolna 825 zł proporcjonalnie), nie limity z Kodeksu pracy.",
    "Zajęcie przez ZUS za zaległe składki z działalności - traktujemy tak samo jak zajęcie komornicze niealimentacyjne (50%, kwota wolna = minimalna krajowa netto)."
  ],
  "common_mistakes": [
    "Potrącanie 50% osobno od każdego składnika wypłaty (wynagrodzenie, premia, nagroda) zamiast od łącznej sumy netto miesiąca.",
    "Stosowanie limitów z Kodeksu pracy do umowy zlecenia bez pisma komornika potwierdzającego, że to jedyne źródło utrzymania - w efekcie zleceniobiorca dostaje za dużo, a wierzyciel za mało.",
    "Mylenie kwoty wolnej od zasiłku (825 zł, waloryzowana) z minimalnym wynagrodzeniem netto - i odwrotnie, stosowanie kwoty wolnej z KP do zasiłków ZUS."
  ],
  "related_questions": [
    "Jak rozliczyć zbieg egzekucji alimentacyjnej i niealimentacyjnej - który komornik ma pierwszeństwo?",
    "Czy z wynagrodzenia chorobowego (pierwsze 33 dni płacone przez pracodawcę) stosujemy limity z Kodeksu pracy czy z ustawy emerytalnej?",
    "Jak wyliczyć potrącenie komornicze dla pracownika zatrudnionego na część etatu - czy kwota wolna jest proporcjonalna?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": false,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "10",
    "cluster_label": "Potrącenia komornicze niealimentacyjne z wynagrodzeń i zleceń",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "415cc82e63d3",
      "8ad9d2380b5b",
      "f73ebf4734cf",
      "5f8c705c4f34",
      "737be2ed09c3",
      "f18e9e4f3685",
      "483953e1d9e6",
      "a9e58c01fb2c",
      "01396068941f",
      "3a94f51d46fd",
      "c36b99ed3368",
      "2350a1c97ee2",
      "d3cc6dbb3ba4"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

### 7. Cluster `107` — Oznaczenia BFK vs DI w JPK_VAT od lutego 2026 - faktury WNT, import usług, poza KSeF

- **topic_area:** `JPK`
- **size (źródłowych postów):** 179  **avg_comments:** 1.425
- **answer_steps:** 7  **legal_anchors:** 3  **requires_manual_legal_anchor:** `False`
- **tokens:** in=6915 out=3531  **elapsed:** 54.71s  **status:** ✅ OK

**Draft (JSON):**

```json
{
  "id": "wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p",
  "title": "Oznaczenia BFK vs DI w JPK_VAT od lutego 2026 - faktury WNT, import usług, poza KSeF",
  "topic_area": "JPK",
  "question_examples": [
    "Jakie oznaczenie w ewidencji zakupu i sprzedaży stosować dla faktury WNT - BFK czy DI?",
    "Jak oznaczać faktury za import usług i WNT w nowym pliku JPK - DI czy BFK?",
    "Czy faktury sprzedaży wystawiane poza KSeF (przed wejściem obowiązku) oznaczamy kodem BFK?",
    "Czy paragony z NIP do 450 zł (faktury uproszczone) niewysyłane do KSeF oznaczamy BFK w JPK?",
    "Czy podmiot wchodzący do KSeF od kwietnia już w JPK za luty musi oznaczać faktury sprzedaży znacznikiem BFK?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Ustal od kiedy obowiązuje nowa struktura JPK_V7",
      "detail": "Nowe oznaczenia BFK i DI obowiązują w JPK_V7 od rozliczenia za luty 2026 (plik wysyłany w marcu 2026), niezależnie od daty wejścia podatnika do obowiązkowego KSeF.",
      "condition": null
    },
    {
      "step": 2,
      "action": "Zastosuj BFK dla faktur, które teoretycznie mogłyby być w KSeF, ale faktycznie są poza KSeF",
      "detail": "Kod BFK (Brak Faktury w KSeF) stosuj dla: faktur wystawionych poza KSeF mimo obowiązku (np. awaria, tryb offline), faktur uproszczonych - paragonów z NIP do 450 zł niewysyłanych do KSeF, faktur wystawianych przez podatnika przed jego datą wejścia do KSeF, faktur B2C dla konsumentów.",
      "condition": "if faktura dotyczy transakcji krajowej, która normalnie podlegałaby KSeF"
    },
    {
      "step": 3,
      "action": "Zastosuj DI dla dokumentów, które strukturalnie nie mieszczą się w KSeF",
      "detail": "Kod DI (Dokument Inny/wewnętrzny) stosuj dla: faktur WNT (dostawca zagraniczny - faktura nie przechodzi przez KSeF), importu usług, importu towarów, dokumentów wewnętrznych WEW, faktur od kontrahentów zagranicznych nieposiadających polskiego NIP, eksportu towarów i WDT (według stanowiska KIS z infolinii).",
      "condition": "if transakcja jest zagraniczna lub udokumentowana dowodem wewnętrznym"
    },
    {
      "step": 4,
      "action": "Oznacz fakturę w module handlowym/księgowym programu",
      "detail": "W Comarch Optima oznaczenie ustawiasz w 4. zakładce 'JPK' na fakturze. W Symfonii, Enova, WFirma - w sekcji parametrów JPK/rejestru VAT. Oznaczenie powinno być nadawane już na etapie wystawiania lub księgowania dokumentu, nie dopiero przy generowaniu pliku.",
      "condition": null
    },
    {
      "step": 5,
      "action": "Zachowaj dotychczasowe oznaczenia procedur obok nowych kodów",
      "detail": "Nowe kody BFK/DI nie zastępują dotychczasowych oznaczeń - WEW, FP, RO, MK, GTU_01-13 itd. stosujesz dalej równolegle. Np. dokument wewnętrzny dla WNT otrzyma DI + WEW, paragon z NIP do 450 zł - BFK + FP (jeśli był wystawiony do paragonu).",
      "condition": null
    },
    {
      "step": 6,
      "action": "Skoryguj faktury wystawione przed lutym 2026 ujęte w JPK za luty",
      "detail": "Faktury z grudnia 2025 i stycznia 2026 księgowane w rozliczeniu za luty 2026 nie wymagają nowych oznaczeń BFK/DI - jeśli program wymusza kod, wybierz opcję odpowiadającą charakterowi dokumentu (BFK dla krajowych poza KSeF, DI dla zagranicznych). W razie blokady rozważ korektę JPK za styczeń.",
      "condition": "if faktury są z okresu przed lutym 2026"
    },
    {
      "step": 7,
      "action": "Zweryfikuj stanowisko KIS w razie wątpliwości pisemnym zapytaniem",
      "detail": "W temacie BFK vs DI dla WNT/importu usług pojawiają się sprzeczne interpretacje (MF z 18.03 - BFK przy fakturze; szkolenia KIS - wszystko DI). Przy znacznej wartości transakcji złóż zapytanie do KIS lub wniosek o interpretację, by zabezpieczyć się przed ryzykiem sankcji.",
      "condition": "if transakcje mają znaczną wartość lub są powtarzalne"
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Rozporządzenie w sprawie JPK_V7",
      "article_number": "§ 10",
      "reason": "Określa zakres danych ewidencji sprzedaży, w tym oznaczenia procedur i typów dokumentów stosowane w JPK_V7 - podstawa prawna dla nowych kodów BFK i DI od lutego 2026."
    },
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 106gb ust. 4 pkt 1 i ust. 5",
      "reason": "Reguluje sytuacje, gdy faktura ustrukturyzowana jest udostępniana poza KSeF lub gdy kontrahent zagraniczny nie uczestniczy w KSeF - to materia, której dotyczą kody BFK (poza KSeF) i DI (kontrahent zagraniczny)."
    },
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 109 ust. 14",
      "reason": "Deleguje Ministrowi Finansów kompetencję do określenia szczegółowych danych ewidencji VAT w drodze rozporządzenia - podstawa ustawowa obowiązku stosowania oznaczeń typu BFK/DI."
    }
  ],
  "edge_cases": [
    "Paragon fiskalny z NIP do 450 zł (faktura uproszczona) - nie idzie do KSeF, w JPK oznaczenie BFK (obok dotychczasowego FP jeśli dotyczy).",
    "Apteka wystawiająca paragon z NIP powyżej 450 zł - fakturę do takiego paragonu z NIP nabywcy wysyłasz do KSeF z oznaczeniem FP (nie BFK); dla osób prywatnych faktura do paragonu - poza KSeF.",
    "Faktura WNT/import usług - dominująca praktyka i stanowisko KIS to DI, ale część interpretacji MF z 18.03 wskazuje na BFK jeśli istnieje faktura od kontrahenta - rozbieżność interpretacyjna.",
    "Podatnik wchodzący do obowiązkowego KSeF dopiero od 1 kwietnia 2026 - faktury sprzedaży za luty i marzec 2026 wystawione poza KSeF oznacza w JPK kodem BFK (zarówno sprzedaż jak i zakup)."
  ],
  "common_mistakes": [
    "Pomijanie oznaczenia BFK dla faktur B2C i paragonów z NIP do 450 zł w przekonaniu, że skoro nie idą do KSeF, to kod nie jest potrzebny - kod BFK jest wymagany właśnie dla takich dokumentów.",
    "Stosowanie BFK dla WNT i importu usług na podstawie samej faktury zagranicznej bez wystawiania dokumentu wewnętrznego - dominujące stanowisko KIS wskazuje, że dla transakcji transgranicznych właściwy jest DI.",
    "Zastępowanie dotychczasowych oznaczeń (WEW, FP, GTU) nowymi kodami BFK/DI - te oznaczenia są komplementarne, stosujesz je równolegle, a nie zamiennie."
  ],
  "related_questions": [
    "Czy dokumenty wewnętrzne WEW (np. rozliczenie prowizji, dokumenty na kasę fiskalną) w nowym JPK od lutego 2026 oznaczamy DI czy zachowują tylko WEW?",
    "Jak oznaczać w JPK faktury wystawione w trybie offline24 lub podczas awarii KSeF - BFK czy innym kodem?",
    "Czy faktury WDT i eksportowe w nowym JPK oznaczamy DI, czy pozostają bez nowego oznaczenia?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": false,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "107",
    "cluster_label": "Nowe oznaczenia JPK_VAT: BFK vs DI dla faktur WNT, importu i poza KSeF",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "8df09435d3e5",
      "253ca9d7afea",
      "b6ee496c7a6a",
      "c2074d6c6b0e",
      "7ce1c1f2e145",
      "41bf36519fbf",
      "c7a0cd9a8c40",
      "390d16ec7b81",
      "f296da1c9a6b",
      "566196d1d9bc",
      "e022667d2faf",
      "593e5e65bba7",
      "4cb5ee9f16ec",
      "3c052a0e1f34",
      "bfb64fab2f2c"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

### 8. Cluster `62` — VAT przy wykupie, sprzedaży i darowiźnie samochodu osobowego z firmy (leasing, ST, cele prywatne)

- **topic_area:** `VAT`
- **size (źródłowych postów):** 179  **avg_comments:** 1.179
- **answer_steps:** 7  **legal_anchors:** 3  **requires_manual_legal_anchor:** `False`
- **tokens:** in=7211 out=4209  **elapsed:** 59.14s  **status:** 🟢 OK (retry)

**Draft (JSON):**

```json
{
  "id": "wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy",
  "title": "VAT przy wykupie, sprzedaży i darowiźnie samochodu osobowego z firmy (leasing, ST, cele prywatne)",
  "topic_area": "VAT",
  "question_examples": [
    "Wykupiłem samochód osobowy z leasingu operacyjnego na firmę, ale nie wprowadziłem faktury wykupu do kosztów i nie odliczyłem VAT – czy przy późniejszej sprzedaży muszę naliczyć VAT?",
    "Klient wykupił samochód z leasingu na firmę (nie odliczył VAT, wprowadził do ŚT) – czy może darować auto ojcu bez VAT i bez PIT?",
    "Podatnik zakupił samochód osobowy na fakturę VAT marża, wprowadził do majątku firmy bez odliczenia VAT, amortyzował – czy przy sprzedaży wystawia zwykłą fakturę z 23% VAT?",
    "Auto kupione na umowę kupna-sprzedaży (bez VAT) i wprowadzone do firmy – czy przy sprzedaży wystąpi VAT?",
    "Samochód po wykupie z leasingu wykupiony prywatnie (nie ŚT), chcę sprzedać przed upływem 6 lat – czy będzie VAT i PIT, czy tylko PIT?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Ustal status pojazdu w firmie",
      "detail": "Sprawdź, czy samochód był wprowadzony do ewidencji środków trwałych, czy wykupiony prywatnie (faktura wykupu na firmę, ale bez ujęcia w ŚT i bez odliczenia VAT), czy stanowił towar handlowy. Od tego zależy zarówno skutek w VAT, jak i w PIT.",
      "condition": null
    },
    {
      "step": 2,
      "action": "Ustal prawo do odliczenia VAT przy nabyciu",
      "detail": "Zweryfikuj dokument zakupu: faktura VAT zwykła (prawo do odliczenia 50% lub 100%), faktura VAT marża (brak prawa do odliczenia), umowa kupna-sprzedaży (brak VAT naliczonego). Kluczowe jest PRAWO do odliczenia, a nie faktyczne odliczenie – jeśli prawo przysługiwało, sprzedaż/darowizna będzie opodatkowana VAT nawet gdy podatnik z odliczenia nie skorzystał.",
      "condition": null
    },
    {
      "step": 3,
      "action": "Określ sposób opodatkowania sprzedaży samochodu firmowego",
      "detail": "Przy sprzedaży środka trwałego czynny podatnik VAT wystawia fakturę z 23% VAT od pełnej ceny sprzedaży (art. 5 i art. 41 ustawy o VAT). Jeśli auto kupione było na VAT marża i spełnione są warunki z art. 120 – można sprzedać w procedurze marży. W Comarch Optima / wFirma / Symfonia zaksięguj fakturę sprzedaży ŚT i dokonaj likwidacji ŚT z rozliczeniem niezamortyzowanej wartości w kosztach.",
      "condition": "if samochód jest środkiem trwałym u czynnego podatnika VAT"
    },
    {
      "step": 4,
      "action": "Rozlicz wykup z leasingu przekazany na cele prywatne",
      "detail": "Jeśli przedsiębiorca wykupił auto z leasingu fakturą na firmę, ale NIE wprowadził do ŚT, NIE ujął w kosztach i NIE odliczył VAT – uznaje się wykup za nabycie na cele prywatne. Późniejsza sprzedaż nie podlega VAT ani PIT z działalności, ale uwaga: w PIT prywatnym obowiązuje 6-letni okres (art. 10 ust. 2 pkt 4 ustawy o PIT liczony od pierwszego dnia miesiąca następującego po wycofaniu/wykupie).",
      "condition": "if faktura wykupu nie ujęta w kosztach i VAT nieodliczony"
    },
    {
      "step": 5,
      "action": "Zweryfikuj skutki darowizny samochodu firmowego",
      "detail": "Nieodpłatne przekazanie towaru (w tym samochodu) podlega VAT na podstawie art. 7 ust. 2 ustawy o VAT, jeżeli podatnikowi przysługiwało prawo do odliczenia VAT przy nabyciu (w całości lub w części). Oznacza to, że przy wykupie z leasingu z fakturą VAT darowizna auta córce/ojcu zwykle będzie opodatkowana VAT od wartości rynkowej, nawet jeśli podatnik nie skorzystał z odliczenia. Darowiznę udokumentuj fakturą wewnętrzną/dokumentem wewnętrznym.",
      "condition": "if planowana darowizna samochodu z firmy"
    },
    {
      "step": 6,
      "action": "Sprawdź skutki PIT przy sprzedaży po wycofaniu na cele prywatne",
      "detail": "Zgodnie z art. 10 ust. 2 pkt 4 ustawy o PIT – sprzedaż samochodu wycofanego z działalności przed upływem 6 lat (licząc od pierwszego dnia miesiąca po wycofaniu) stanowi przychód z działalności gospodarczej. W koszty można ująć niezamortyzowaną wartość początkową (lub wartość wykupu, jeśli nie był ŚT, ale był wykorzystywany w firmie – tu uwaga na stanowiska organów).",
      "condition": "if sprzedaż przed upływem 6 lat od wycofania"
    },
    {
      "step": 7,
      "action": "Zgłoś darowiznę do US i rozważ alternatywy",
      "detail": "Obdarowany z I grupy (np. córka, ojciec) składa SD-Z2 w ciągu 6 miesięcy – zwolnienie z podatku od spadków i darowizn. Jeśli obdarowany sprzeda auto po upływie 6 miesięcy od nabycia (art. 10 ust. 1 pkt 8 PIT) – nie płaci PIT. Alternatywa: sprzedaż z rabatem zamiast darowizny – prostsze podatkowo dla przedsiębiorcy, ale uwaga na wartość rynkową dla VAT (podstawa nie może być rażąco zaniżona).",
      "condition": "if darowizna w rodzinie"
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 86a ust. 1-3",
      "reason": "Reguluje 50%/100% odliczenia VAT od wydatków na pojazdy samochodowe, co determinuje prawo do odliczenia przy wykupie i dalsze skutki przy sprzedaży/darowiźnie."
    },
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 5 ust. 1 pkt 1",
      "reason": "Wskazuje, że odpłatna dostawa towaru (sprzedaż samochodu firmowego) podlega opodatkowaniu VAT – podstawa naliczenia VAT przy sprzedaży ŚT."
    },
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 7 ust. 2",
      "reason": "Nieodpłatne przekazanie (darowizna) towaru traktuje jak dostawę opodatkowaną VAT, jeżeli przy nabyciu przysługiwało prawo do odliczenia – kluczowe dla darowizny auta z firmy."
    }
  ],
  "edge_cases": [
    "Wykup z leasingu na fakturę firmową bez ujęcia w kosztach i bez odliczenia VAT + przekazanie na cele prywatne – przy późniejszej sprzedaży prywatnej brak VAT, PIT tylko jeśli sprzedaż przed upływem 6 lat liczonych od wycofania.",
    "Samochód kupiony na VAT marża i wprowadzony do ŚT – przy sprzedaży można zastosować procedurę marży (art. 120), jeśli spełnione warunki, zamiast 23% VAT od pełnej ceny.",
    "Samochód kupiony na umowę kupna-sprzedaży (brak VAT naliczonego) – przy sprzedaży jako ŚT u czynnego podatnika VAT co do zasady 23% VAT od pełnej ceny, chyba że zastosowana zostanie procedura marży dla towarów używanych.",
    "Spółka na CIT estońskim sprzedająca samochód nieujęty w ŚT – ryzyko ukrytych zysków/wydatków niezwiązanych z działalnością; sprzedaż sama w sobie nie generuje 50% CIT estońskiego, ale wcześniejsze użytkowanie prywatne może.",
    "Darowizna towarów handlowych/samochodów (np. ojciec → córka) – VAT należny od wartości rynkowej, jeśli przysługiwało prawo odliczenia; często korzystniejsza jest sprzedaż z rabatem niż darowizna."
  ],
  "common_mistakes": [
    "Mylenie 'nie odliczyłem VAT' z 'nie miałem prawa odliczyć' – dla skutków VAT przy sprzedaży/darowiźnie liczy się PRAWO do odliczenia, a nie faktyczne skorzystanie z niego.",
    "Pominięcie VAT przy darowiźnie samochodu wykupionego z leasingu z fakturą VAT – podatnicy zakładają, że skoro nie odliczyli VAT, to darowizna jest neutralna, podczas gdy art. 7 ust. 2 wymaga opodatkowania.",
    "Błędne liczenie 6-letniego okresu w PIT od daty zakupu zamiast od pierwszego dnia miesiąca następującego po miesiącu wycofania z działalności (art. 10 ust. 2 pkt 4 PIT)."
  ],
  "related_questions": [
    "Jak rozliczyć VAT i PIT od rat leasingu operacyjnego samochodu osobowego powyżej 150 000 zł?",
    "Czy przy wycofaniu samochodu z firmy na cele prywatne trzeba skorygować wcześniej odliczony VAT (korekta wieloletnia)?",
    "Jak zastosować procedurę VAT marża przy sprzedaży samochodu używanego nabytego od osoby prywatnej jako towar handlowy?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": false,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "62",
    "cluster_label": "VAT przy wykupie, sprzedaży i darowiźnie samochodu z firmy",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "d43a1bec6705",
      "a1e8ceb1e6f3",
      "6664543ff8bd",
      "8e435a57f70f",
      "2575a08012f7",
      "8c1c03ed9204",
      "7f474bb7dc1d",
      "4d516701aa0c",
      "0a870e96771d",
      "2f51aa19b173",
      "68b4e7c75f0e",
      "199876631f56",
      "3fb763039ad1",
      "e38933f7a37a"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

### 9. Cluster `21` — Sporządzanie i składanie sprawozdań finansowych do KRS/KAS - schematy, wersje, procedura

- **topic_area:** `rachunkowość`
- **size (źródłowych postów):** 271  **avg_comments:** 1.059
- **answer_steps:** 6  **legal_anchors:** 3  **requires_manual_legal_anchor:** `False`
- **tokens:** in=6533 out=3729  **elapsed:** 57.24s  **status:** ✅ OK

**Draft (JSON):**

```json
{
  "id": "wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie",
  "title": "Sporządzanie i składanie sprawozdań finansowych do KRS/KAS - schematy, wersje, procedura",
  "topic_area": "rachunkowość",
  "question_examples": [
    "Czy za 2025 rok można sporządzić sprawozdanie spółki z o.o. w wersji schemy 1.3, czy trzeba czekać na 2.1?",
    "Na jakim schemacie (załącznik nr 1 v 1.3?) sporządzić sprawozdanie spółki z o.o. za 2025 rok?",
    "Jak i gdzie złożyć sprawozdanie finansowe spółki z o.o. do KRS - przez S24 czy e-formularze?",
    "Czy spółka cywilna prowadząca pełne księgi ze względu na obroty składa gdzieś sprawozdanie finansowe?",
    "Czy uchwała o stosowaniu uproszczeń w SF musi być dołączona do zgłoszenia w KRS i podpisana elektronicznie?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Ustal obowiązek sprawozdawczy i miejsce złożenia dla danego podmiotu",
      "detail": "Spółki z KRS (sp. z o.o., S.A., komandytowa, jawna z pełną księgowością) - SF do KRS przez RDF (eKRS). Osoby fizyczne prowadzące KH oraz spółki cywilne osób fizycznych - SF do Szefa KAS przez e-Sprawozdania Finansowe. Spółka cywilna prowadząca KH ze względu na obroty: SF sporządza i podpisuje, ale nie składa do żadnego rejestru (pozostaje w dokumentacji jednostki).",
      "condition": null
    },
    {
      "step": 2,
      "action": "Dobierz właściwy schemat XSD (załącznik i wersję) do rodzaju jednostki",
      "detail": "Dla spółki z o.o. na zasadach ogólnych - załącznik nr 1 do UoR. Dla jednostki mikro - załącznik nr 4, dla małej - załącznik nr 5. Za 2025 r. obowiązuje wersja schemy opublikowana przez MF na stronie gov.pl/sf przed dniem sporządzenia - sprawdź komunikat MF. Nie sporządzaj w wersji archiwalnej jeśli MF wydał nową obowiązującą.",
      "condition": "if jednostka kwalifikuje się jako mikro/mała - wymagana uchwała organu zatwierdzającego o stosowaniu uproszczeń"
    },
    {
      "step": 3,
      "action": "Wygeneruj plik XML w programie księgowym i podpisz elektronicznie",
      "detail": "W Comarch Optima, Symfonia, Enova lub WFirma skorzystaj z modułu e-Sprawozdania. Podpis: kwalifikowany, profil zaufany lub podpis osobisty. SF podpisuje osoba prowadząca księgi i KAŻDY członek zarządu (można złożyć oświadczenie jednego członka + odmowę pozostałych). Termin sporządzenia: 3 miesiące od dnia bilansowego (dla roku kalendarzowego: do 31 marca).",
      "condition": null
    },
    {
      "step": 4,
      "action": "Przygotuj komplet dokumentów zatwierdzających",
      "detail": "Po zatwierdzeniu SF przez organ (zgromadzenie wspólników) - do 6 miesięcy od dnia bilansowego. Skompletuj: SF (XML), uchwałę o zatwierdzeniu SF, uchwałę o podziale zysku/pokryciu straty, sprawozdanie z działalności (jeśli wymagane), opinię biegłego (jeśli badanie), uchwałę o stosowaniu uproszczeń (jeśli dotyczy - dołącza się do KRS wraz z SF, podpisana elektronicznie lub skan podpisanego dokumentu).",
      "condition": "if spółka z o.o./S.A. - wymagane sprawozdanie z działalności zarządu"
    },
    {
      "step": 5,
      "action": "Złóż SF do właściwego rejestru w ustawowym terminie",
      "detail": "KRS: w ciągu 15 dni od zatwierdzenia SF przez RDF (bezpłatne zgłoszenie finansowe) - NIE przez S24. Zgłoszenie RDF wymaga PESEL osoby uprawnionej ujawnionej w KRS. KAS (osoby fizyczne z KH): do 30 kwietnia roku następującego po roku podatkowym, przez bramkę e-Sprawozdania Finansowe. Do KAS nie załącza się uchwał (nie dotyczy osób fizycznych).",
      "condition": null
    },
    {
      "step": 6,
      "action": "W przypadku opóźnienia - złóż SF niezwłocznie, nawet po terminie",
      "detail": "KRS za brak SF wydaje najpierw wezwanie z grzywną przymuszającą - po złożeniu zaległego SF grzywna nieopłacona przestaje być wymagalna. Przy dużych opóźnieniach sąd może zawiadomić prokuraturę (art. 79 UoR - odpowiedzialność karna). Nie ma formalnej procedury wniosku o odstąpienie od kary, ale samo złożenie zaległych SF typowo kończy sprawę bez sankcji finansowej.",
      "condition": "if przekroczony termin 15 dni od zatwierdzenia"
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Ustawa o rachunkowości",
      "article_number": "art. 69 ust. 1",
      "reason": "Określa obowiązek i 15-dniowy termin złożenia SF wraz z uchwałą zatwierdzającą i uchwałą o podziale zysku we właściwym rejestrze sądowym (KRS)."
    },
    {
      "law_name": "Ustawa o rachunkowości",
      "article_number": "art. 69 ust. 1 pkt 3",
      "reason": "Wymaga dołączenia do zgłoszenia w KRS odpisu uchwały organu zatwierdzającego o zatwierdzeniu rocznego sprawozdania finansowego."
    },
    {
      "law_name": "Ustawa o rachunkowości",
      "article_number": "art. 45 ust. 1g",
      "reason": "Nakłada obowiązek sporządzenia sprawozdania finansowego w postaci elektronicznej w strukturze logicznej udostępnionej przez MF (schemy XSD)."
    }
  ],
  "edge_cases": [
    "Spółka cywilna prowadząca KH ze względu na przekroczenie limitu obrotów - sporządza i podpisuje SF, ale nie składa go do żadnego rejestru (pozostaje w dokumentacji jednostki).",
    "Spółka zawieszona vs zamrożona: spółka zawieszona bez żadnych operacji gospodarczych w roku obrotowym może nie sporządzać SF (art. 3 ust. 6 UoR), ale pojedyncza transakcja (np. opłacenie faktury księgowej) przywraca obowiązek sporządzenia SF.",
    "Przekształcenie sp. komandytowej w sp. z o.o. - SF sporządzone na dzień poprzedzający przekształcenie NIE jest składane do KRS (art. 12 ust. 2 pkt 3 UoR - brak zamknięcia ksiąg przy kontynuacji), ale bilansowo zamyka się księgi spółki przekształcanej.",
    "Przejęcie spółki bez dokumentów od poprzedniego biura - zaległe SF należy odtworzyć na bazie deklaracji z US/ZUS, wyciągów bankowych, JPK; równolegle zaleca się złożenie zawiadomienia o podejrzeniu popełnienia przestępstwa do prokuratury (art. 77 UoR) jako zabezpieczenie odpowiedzialności klienta."
  ],
  "common_mistakes": [
    "Próba składania SF do KRS przez portal S24 - SF składa się wyłącznie przez bezpłatny system RDF (Repozytorium Dokumentów Finansowych) w eKRS.",
    "Dołączanie uchwały o podziale zysku do SF osoby fizycznej składanego do KAS - osoby fizyczne nie sporządzają i nie składają uchwał o podziale zysku (brak organu zatwierdzającego).",
    "Dynamiczne korygowanie zatwierdzonego SF po zmianach stanów magazynowych - SF sporządza się na dzień bilansowy i koryguje wyłącznie w razie istotnych błędów (art. 54 UoR), a nie bieżących zmian operacyjnych po dniu bilansowym."
  ],
  "related_questions": [
    "Jak podpisać e-SF gdy jeden z członków zarządu nie ma polskiego PESEL ani podpisu kwalifikowanego?",
    "Czy sprawozdanie z działalności zarządu można dołączyć jako PDF, czy musi być w strukturze XML?",
    "W jakim terminie i gdzie złożyć SF spółki, która zmieniła rok obrotowy w trakcie roku kalendarzowego?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": false,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "21",
    "cluster_label": "Sprawozdania finansowe do KRS/KAS: schematy i składanie",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "c7ad127f9296",
      "0eb0e6142629",
      "214f7d8d83d7",
      "bffda0b4d41e",
      "a51bd560f9c2",
      "a1c8ec18535e",
      "a51bd560f9c2",
      "d15677cdd119",
      "227c400dc3c0",
      "afd7c2038e98",
      "69128abf0c6d",
      "bad0d6d90599",
      "ce9969991b5e",
      "9d36c799e46d",
      "1845d0a5f61d",
      "d31a2f2e7159"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

### 10. Cluster `139` — KSeF w biurze rachunkowym: obieg, archiwizacja i weryfikacja faktur kosztowych klientów

- **topic_area:** `KSeF`
- **size (źródłowych postów):** 109  **avg_comments:** 1.89
- **answer_steps:** 7  **legal_anchors:** 3  **requires_manual_legal_anchor:** `False`
- **tokens:** in=8162 out=4020  **elapsed:** 64.51s  **status:** ✅ OK

**Draft (JSON):**

```json
{
  "id": "wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze",
  "title": "KSeF w biurze rachunkowym: obieg, archiwizacja i weryfikacja faktur kosztowych klientów",
  "topic_area": "KSeF",
  "question_examples": [
    "Jak w praktyce zorganizować pracę z KSeF - czy klienci nadal mają dostarczać faktury, czy bazujemy tylko na tym co jest w KSeF i jak klient ma oznaczać które faktury są KUP?",
    "Jak weryfikować faktury ściągnięte z KSeF skoro fizycznie nie mamy dokumentu - drukować wizualizacje czy pracować tylko na XML?",
    "Jak wygląda archiwizacja faktur klientów po wejściu KSeF - czy drukujemy i wpinamy do segregatorów, czy wystarczy że są na serwerze MF?",
    "Czy zakładać dla każdego klienta osobny folder na pliki XML z KSeF czy wystarczy automatyczny zaczyt do programu księgowego?",
    "W jaki sposób klient ma nam potwierdzać, że daną fakturę z KSeF mamy zaksięgować (transakcja doszła do skutku, jest KUP, nie jest wystawiona błędnie na jego NIP)?"
  ],
  "answer_steps": [
    {
      "step": 1,
      "action": "Ustal z klientem pisemnie model obiegu faktur kosztowych",
      "detail": "W aneksie do umowy/procedurze określ: kto pobiera faktury z KSeF (biuro czy klient), jak klient akceptuje koszty (OCR typu Saldeo/Symfonia Obieg Dokumentów, panel klienta w Comarch Optima/Enova, zestawienie Excel, mail z listą numerów KSeF do zaksięgowania) oraz jak oznacza faktury nie-KUP i błędnie wystawione na jego NIP. Bez tego biuro zaksięguje faktury, których klient nie akceptuje jako koszt.",
      "condition": null
    },
    {
      "step": 2,
      "action": "Skonfiguruj automatyczny pobór XML z KSeF do programu księgowego",
      "detail": "W Comarch Optima, Symfonii, Enova lub wFirma włącz integrację z KSeF tokenem/certyfikatem klienta (uprawnienie 'dostęp do faktur' nadane biuru). Ustaw harmonogram pobierania (np. codziennie) i mapowanie pól - szczególnie data sprzedaży, sposób i termin płatności, bo te pola często są puste w wizualizacji gdy sprzedawca źle je zmapował.",
      "condition": null
    },
    {
      "step": 3,
      "action": "Wprowadź dwustopniową weryfikację kosztową przed księgowaniem",
      "detail": "Krok A: klient w OCR/panelu zatwierdza fakturę jako KUP/nie-KUP i oznacza błędne (wystawione omyłkowo na jego NIP - takie zgłasza do sprzedawcy z żądaniem korekty do zera, bo w KSeF nie można 'odrzucić' faktury). Krok B: księgowa sprawdza w programie kompletność danych (data sprzedaży, MPP, WNT, split payment, KSeF ID) i dopiero księguje.",
      "condition": null
    },
    {
      "step": 4,
      "action": "Ustal zasady archiwizacji plików XML i wizualizacji",
      "detail": "Faktura ustrukturyzowana jest w KSeF przechowywana przez MF przez 10 lat - nie ma obowiązku drukowania ani dodatkowej archiwizacji po stronie biura. Rekomendowany minimalny backup: pobieraj XML do folderu klienta (np. /Klient/2026/KSeF_zakup/) co najmniej raz na okres rozliczeniowy, aby zabezpieczyć się przed awarią MF i mieć dowód przy kontroli offline.",
      "condition": null
    },
    {
      "step": 5,
      "action": "Obsłuż faktury spoza KSeF (tryb offline, awaria, B2C, kontrahent zagraniczny, zwolnieni)",
      "detail": "Stwórz w procedurze osobną ścieżkę dla: faktur wystawionych w trybie offline24/awaryjnym (mają kod QR, trafiają do KSeF z opóźnieniem), faktur od podatników zwolnionych z KSeF (zagraniczni bez stałego miejsca w PL, OSS/IOSS), paragonów z NIP, not księgowych i dokumentów wewnętrznych. Te klient nadal dostarcza tradycyjnie (PDF/papier) i wymagają osobnego rejestru.",
      "condition": "if klient ma kontrahentów zwolnionych z KSeF lub dokumenty spoza systemu"
    },
    {
      "step": 6,
      "action": "Rozwiąż problem brakujących danych na wizualizacji KSeF",
      "detail": "Jeśli wizualizacja w programie (Optima, Symfonia) nie pokazuje daty sprzedaży, terminu lub sposobu płatności - pobierz surowy XML i sprawdź węzły P_6 (data sprzedaży), Platnosc/TerminyPlatnosci. Brak danych to najczęściej wina mapowania po stronie sprzedawcy. Poproś klienta o kontakt ze sprzedawcą lub opieraj się na danych z XML, nie z wizualizacji.",
      "condition": "if program nie wyświetla kompletnych danych faktury"
    },
    {
      "step": 7,
      "action": "Przeszkol klienta z oznaczania trybu wystawienia i numeru KSeF",
      "detail": "Poinformuj, że tryb wystawienia (online, offline24, awaryjny) jest widoczny w XML i wpływa na moment powstania obowiązku podatkowego oraz datę otrzymania faktury. Przy masowych zaciągach plikowych ustaw w programie filtr/raport po trybie, aby nie przeglądać każdej faktury ręcznie.",
      "condition": null
    }
  ],
  "legal_anchors": [
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 106gb ust. 3-6 oraz art. 106na ust. 1, 3-4",
      "reason": "Reguluje moment uznania faktury za otrzymaną w KSeF, sposób udostępniania faktury nabywcy oraz obsługę faktur poza KSeF z kodem weryfikacyjnym - kluczowe dla procedury obiegu i archiwizacji w biurze."
    },
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 106nd ust. 2 pkt 1-6 i 11",
      "reason": "Definiuje funkcje KSeF jako systemu przechowywania, uwierzytelniania i udostępniania faktur - uzasadnia rezygnację z dublowania archiwizacji papierowej przez biuro."
    },
    {
      "law_name": "Ustawa o VAT",
      "article_number": "art. 106ga ust. 2",
      "reason": "Wskazuje kategorie podatników zwolnionych z obowiązku KSeF (zagraniczni, OSS/IOSS, B2C), czyli ścieżkę faktur które klient nadal musi dostarczać poza systemem."
    }
  ],
  "edge_cases": [
    "Klient prowadzący małą firmę, której kontrahenci jeszcze nie wdrożyli KSeF - w praktyce nadal połowa faktur wpływa papierowo/PDF, więc przez okres przejściowy trzeba utrzymać równolegle obieg tradycyjny i elektroniczny.",
    "Faktura z KSeF ma datę sprzedaży w innym miesiącu niż data wystawienia (np. sprzedaż 01/2026, wystawienie 02/2026) - w pełnych księgach decyduje data sprzedaży (moment powstania kosztu/obowiązku podatkowego), nie data wystawienia widoczna na wizualizacji.",
    "Faktura wystawiona błędnie na NIP klienta przez obcego kontrahenta - w KSeF nie można jej 'odrzucić', jedyna droga to żądanie korekty do zera od wystawcy; do czasu korekty klient oznacza ją w OCR/panelu jako 'nie moja' i biuro jej nie księguje.",
    "Klient nie chce wdrażać OCR/panelu akceptacji - wtedy alternatywą jest comiesięczne zestawienie (Excel/mail) faktur do zaksięgowania z numerami KSeF, ale wydłuża to zamknięcie miesiąca i zwiększa ryzyko pominięcia faktury."
  ],
  "common_mistakes": [
    "Drukowanie wszystkich faktur z KSeF 'dla bezpieczeństwa' i wpinanie do segregatorów - zbędna praca, bo faktura ustrukturyzowana jest przechowywana w KSeF przez 10 lat i wizualizacja PDF nie jest dokumentem źródłowym (źródłem jest XML).",
    "Księgowanie wszystkich faktur zaciągniętych z KSeF bez akceptacji klienta - prowadzi do zaksięgowania faktur błędnie wystawionych na NIP klienta lub niebędących kosztem uzyskania przychodu.",
    "Opieranie się wyłącznie na wizualizacji w programie księgowym - różne programy pokazują różny zakres danych (np. Optima nie pokazuje daty sprzedaży czy sposobu płatności), co prowadzi do błędów w księgowaniu; zawsze weryfikuj XML przy niepełnych danych."
  ],
  "related_questions": [
    "Jak wygląda moment powstania obowiązku podatkowego VAT i moment otrzymania faktury w KSeF przy trybie offline24 i awaryjnym?",
    "Jak nadać biuru rachunkowemu uprawnienia do KSeF klienta i czym różni się uwierzytelnianie tokenem, certyfikatem KSeF a pieczęcią kwalifikowaną?",
    "Jak księgować w KSeF faktury od kontrahentów zagranicznych i faktury B2C - czy w ogóle trafiają do systemu?"
  ],
  "last_verified_at": "2026-04-17",
  "draft": true,
  "requires_manual_legal_anchor": false,
  "generation_metadata": {
    "model": "claude-opus-4-7",
    "cluster_id": "139",
    "cluster_label": "KSeF: obieg, archiwizacja i weryfikacja faktur w biurze",
    "generated_at": "2026-04-17T00:00:00Z",
    "source_post_ids": [
      "cc5cc333f5c2",
      "7d3402451576",
      "150ba10bb077",
      "7d6b5192e15f",
      "204c6f23959f",
      "f1b9b91d4a33",
      "972d1bebb32b",
      "91ad8e785a7e",
      "49ce40a7ef6c",
      "440935078e6a",
      "9ae0202035be"
    ]
  }
}
```

**Quick review checklist dla Pawła:**

- [ ] Pytania `question_examples` są prawdziwe (nie wymyślone)
- [ ] Kroki `answer_steps` są konkretne (nie ogólnikowe)
- [ ] `legal_anchors` pasują do tematu i są realne (nie halucynacja)
- [ ] `edge_cases` są realistyczne i wywiedzione z dyskusji
- [ ] Brak oczywistych błędów merytorycznych
- [ ] `title` dobrze oddaje workflow (max ~10 słów, konkretny)
- [ ] `related_questions` są zbliżone ale różne

**Decyzja Pawła:** `[APPROVE / REVISE / REJECT]`  
**Komentarz:** _______________________________________________

---

## 4. Unrelated observations (Claude Code)

1. **`requires_manual_legal_anchor=true` wystąpił 2× w batchu** (cluster `7` Zaliczanie umów zlecenie do stażu pracy oraz `79` Mały ZUS Plus 2026) — to są świeże zmiany przepisów (Kodeks pracy nowela dotycząca stażu pracy wchodzi w 2026, Mały ZUS Plus nowe zasady 2026). Retriever zwrócił stare, bardziej ogólne kotwice które Opus słusznie odrzucił. **Priorytet dla Pawła: dodać świeże wersje ustaw/rozporządzeń z datą effective_from=2026-01-01 do KB.**

2. **Comments w postach są rzadkie i krótkie** — wiele postów z `comments_count>=3` ma bardzo krótkie komentarze ("tak", "zgoda", "również tak robię"). Wartość merytoryczna komentarzy dla części klastrów jest niska. Dla batcha 2 warto rozważyć filtr `min_comment_length=40 znaków` przy high-engagement pickingu.

3. **Cluster 62 hit max_tokens=4096 (x2)** — tylko ten klaster z całego batcha. Prawdopodobnie VAT przy samochodach ma więcej wariantów (wykup, sprzedaż, darowizna, leasing operacyjny, wykup a potem sprzedaż) → Opus generował dłuższą odpowiedź. **Rekomendacja dla batcha 2: ustawić default max_tokens=6500** (bez widocznego wzrostu kosztu, bo płacimy tylko za realnie wyemitowane tokeny).

4. **KB alias niedopasowania** — Opus używa `Ustawa o PIT` zamiast `Ustawa o podatku dochodowym od osób fizycznych` i `Rozporządzenie w sprawie JPK_V7` zamiast `Rozporządzenie JPK_V7`. Artykuły są identyczne, ale dopasowanie wymaga aliasu. **Rekomendacja: dodać prompt-instrukcję żeby Opus używał pełnej nazwy ustawy ze strony KB, albo w post-processingu canonicalize law_name.**

5. **KB ma 4388 rekordów, a nie 4472** (Paweł podał taką liczbę w briefie). Delta 84 — być może brief odwoływał się do innej wersji KB. To tylko liczbowy drobiazg, ale zaznaczam dla ścisłości.

6. **Jakość draftów jest merytorycznie wysoka** — steps zawierają konkretne liczby, daty, stawki, kody (np. `kod ZUS 331`, `art. 1025 kpc`, `limit 150 tys. KUP`, `art. 86a ust. 2 kpd` dla kilometrówki). Wiele kroków odwołuje się do konkretnych programów księgowych (Optima, Symfonia, Enova, wFirma) zgodnie z promptem. Nie widzę oczywistych halucynacji — 24/24 kotwic prawnych istnieje w KB (po aliasach).

7. **Cluster `merge_120_121` był wygenerowany w probe-runie** (dlatego status `RESUMED` w tabeli). Draft przeszedł pełną ścieżkę walidacji — to nie jest specjalny przypadek, tylko artefakt tego że nie re-generowaliśmy go w głównym batchu żeby zaoszczędzić $0.40.
