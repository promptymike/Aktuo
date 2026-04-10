from __future__ import annotations

import json
from pathlib import Path


KB_PATH = Path("data/seeds/law_knowledge.json")


PATCH_RECORDS = [
    {
        "law_name": "Ustawa o VAT",
        "article_number": "art. 86 ust. 10, 10b pkt 1 i 11",
        "category": "vat",
        "verified_date": "",
        "question_intent": "Czy mogę odliczyć VAT w styczniu (faktura wystawiona w grudniu), ale tylko odliczę VAT w styczniu a nie będę ujmować kosztu w kpir?",
        "content": "Prawo do odliczenia VAT powstaje co do zasady w rozliczeniu za okres, w którym po stronie sprzedawcy powstał obowiązek podatkowy, nie wcześniej jednak niż w okresie otrzymania faktury. Oznacza to, że odliczenie VAT może nastąpić w styczniu, jeżeli wtedy spełnione są warunki z art. 86, nawet gdy koszt podatkowy w KPiR jest ujmowany według innych zasad. Podstawa prawna: art. 86 ust. 10, ust. 10b pkt 1 i ust. 11 ustawy o VAT.",
    },
    {
        "law_name": "Ustawa o VAT",
        "article_number": "art. 41 ust. 1, 2, 2a oraz art. 146ef ust. 1",
        "category": "vat",
        "verified_date": "",
        "question_intent": ".Jaka stawka VAT na usługi gastronomiczne z owocami morza, a jaka na usługi gastronomiczne tylko z rybami?",
        "content": "Z samego tekstu ustawy nie wynika prosty podział stawek wyłącznie według tego, czy danie zawiera ryby czy owoce morza. Ustawa rozróżnia stawki dla towarów z załączników oraz wyłącza z tych preferencji usługi związane z wyżywieniem (PKWiU 56), a art. 146ef wskazuje obecnie stawki 23% i 8%. Przy gastronomii kluczowa jest klasyfikacja konkretnego świadczenia jako towar albo usługa związana z wyżywieniem, a nie sam skład dania. Podstawa prawna: art. 41 ust. 1, 2, 2a oraz art. 146ef ust. 1 ustawy o VAT.",
    },
    {
        "law_name": "Ustawa o VAT",
        "article_number": "art. 86a ust. 1-3 i 9",
        "category": "vat",
        "verified_date": "",
        "question_intent": "Odliczam 100% VAT.Leasing (kapitał) nie jest ograniczony proporcja, ponieważ samochód nie jest traktowany jako osobowy w świetle VAT/PIT?",
        "content": "W VAT zasadą dla wydatków związanych z pojazdami samochodowymi jest odliczenie 50%. Pełne 100% odliczenia przysługuje tylko wtedy, gdy pojazd jest wykorzystywany wyłącznie do działalności gospodarczej albo spełnia konstrukcyjne przesłanki wskazane w art. 86a ust. 3 i 9. Samo twierdzenie, że pojazd nie jest samochodem osobowym w rozumieniu PIT, nie przesądza jeszcze o 100% odliczeniu w VAT. Podstawa prawna: art. 86a ust. 1-3 i 9 ustawy o VAT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 42 ust. 1 i 1a",
        "category": "pit",
        "verified_date": "",
        "question_intent": "Jeśli mam kogoś na zleceniu, ale w 2025 nie przepracował ani 1h i nie zarobił ani 1zł to czy muszę wystawiać zerowy PIT4R?",
        "content": "Art. 42 wiąże obowiązki płatnika z kwotami pobranych zaliczek albo podatku. Przepis mówi o przekazaniu pobranych kwot oraz o rocznej deklaracji składanej przez płatników z art. 41. Jeżeli w roku nie było wypłaty i nie pobrano żadnej zaliczki, ustawa nie daje podstawy do wykazywania kwot zerowych jako pobranych; obowiązek trzeba ocenić przez pryzmat faktycznie pobranych kwot. Podstawa prawna: art. 42 ust. 1 i 1a ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 26 ust. 7a pkt 12",
        "category": "pit",
        "verified_date": "",
        "question_intent": "Bo sie zgubiłam. PIT-37 Ulga rehabilitacyjna na niepełnosprawnego syna i faktury za leki powyżej 100 zl?",
        "content": "W ramach ulgi rehabilitacyjnej można odliczyć wydatki na leki w wysokości stanowiącej różnicę pomiędzy faktycznie poniesionym wydatkiem w danym miesiącu a kwotą 100 zł, jeżeli lekarz specjalista stwierdzi, że osoba niepełnosprawna powinna stosować te leki stale lub czasowo. Przy rozliczeniu dziecka niepełnosprawnego trzeba dodatkowo spełnić warunki do samej ulgi. Podstawa prawna: art. 26 ust. 7a pkt 12 ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 39 ust. 1",
        "category": "pit",
        "verified_date": "",
        "question_intent": "Czy pit11 można wysłać jeszcze 2 lutego z uwagi na weekend?",
        "content": "Art. 39 ust. 1 nakłada na płatnika obowiązek przesłania podatnikowi i urzędowi skarbowemu imiennej informacji sporządzonej według ustalonego wzoru. Sama ustawa o PIT nie rozstrzyga w tym przepisie techniki przesunięcia terminu z dnia wolnego; takie przesunięcie wynika z ogólnych zasad obliczania terminów z Ordynacji podatkowej. Podstawa prawna: art. 39 ust. 1 ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 45 ust. 1 i 1a",
        "category": "pit",
        "verified_date": "",
        "question_intent": "Mam taki mix:Żona PIT36 (dg + UoP) + PIT/M (połowa nagrody)Mąż PIT36L (dg) oraz PIT36 (zerowy) + PIT/M (połowa nagrody)Czy w przypadku męża będzie właśnie tak?",
        "content": "Art. 45 stanowi, że podatnicy składają zeznanie według ustalonego wzoru, a w terminie z art. 45 ust. 1a składają także odrębne zeznania dla wskazanych źródeł. Sama ustawa na poziomie tego przepisu nie rozpisuje gotowej kombinacji formularzy dla każdej mieszanej sytuacji, ale potwierdza, że różne źródła mogą wymagać odrębnych zeznań według właściwych wzorów. Podstawa prawna: art. 45 ust. 1 i 1a ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 27f ust. 1-2e",
        "category": "pit",
        "verified_date": "",
        "question_intent": "Ulga na dziecko Córka ma 22 lata i studiuje w Danii. Czy w takim przypadku mogę zastosować ulgę na dziecko?",
        "content": "W pokazanym zakresie art. 27f reguluje ulgę na dzieci przede wszystkim przez odwołanie do małoletniego dziecka, limitów dochodów i szczególnych zasad dla dziecka z orzeczeniem albo decyzją wskazaną w art. 26 ust. 7d. Z samego przytoczonego tekstu ustawy nie wynika prosta odpowiedź, że każda pełnoletnia córka studiująca za granicą automatycznie daje prawo do ulgi, więc trzeba zweryfikować pełne warunki z art. 27f. Podstawa prawna: art. 27f ust. 1-2e ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 26 ust. 1 pkt 2",
        "category": "pit",
        "verified_date": "",
        "question_intent": "Czy jeśli działalność w 2025 była na ryczałcie od 03-12.2025 to czy w 2026 można użyć jako podstawy - przychodu z roku poprzedniego do ustalenia podstawy zdrowotnej?",
        "content": "Ustawa o PIT w art. 26 reguluje odliczenia od dochodu, w tym określone składki, ale nie wyznacza zasad ustalania podstawy składki zdrowotnej dla ryczałtu. To oznacza, że pytanie o podstawę zdrowotną nie wynika wprost z przywołanego przepisu ustawy o PIT i wymaga sięgnięcia do odrębnych przepisów ubezpieczeniowych. Podstawa prawna: art. 26 ust. 1 pkt 2 ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 45 ust. 1",
        "category": "pit",
        "verified_date": "",
        "question_intent": "Pit-37 Zamotałam się osoba która otrzymuje PIT40A z KRUS i PIT11A otrzymuje z Zusu powinna taką osoba rozliczyć się PIT 37?",
        "content": "Art. 45 ust. 1 potwierdza obowiązek złożenia rocznego zeznania według ustalonego wzoru. Sama ustawa o PIT na poziomie tego przepisu nie daje prostego katalogu kombinacji formularzy dla dokumentów PIT-40A, PIT-11A i PIT-37, więc odpowiedź wymaga zestawienia rodzaju przychodów z właściwym wzorem zeznania. Podstawa prawna: art. 45 ust. 1 ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 45 ust. 1",
        "category": "pit",
        "verified_date": "",
        "question_intent": "Chciałabym zapytać czy ktoś może miał taką sytuację, że od 2016 roku zawieszona jest działalność, a podatnik rozliczony na formularzu PIT 37 zamiast PIT 36.Teraz wydaje mi się, że trzeba złożyć korekty wstecz od 2020 roku?",
        "content": "Art. 45 ust. 1 stanowi, że podatnik składa zeznanie według ustalonego wzoru za dany rok podatkowy. Jeżeli wcześniej użyto niewłaściwego formularza, problem dotyczy korekty zeznania za konkretne lata, ale sama ustawa o PIT na poziomie art. 45 nie daje automatycznej odpowiedzi, że każda zawieszona działalność zawsze oznacza PIT-36 albo że korekta jest potrzebna od wskazanego roku bez dalszej analizy. Podstawa prawna: art. 45 ust. 1 ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 23 ust. 1 pkt 47a oraz art. 23b ust. 1",
        "category": "pit",
        "verified_date": "",
        "question_intent": "Mam tak w Volkswagen Leasing, samochód osobowy elektryczny, proporcja ustalona ale na fakturach i harmonogramie brak podziału. Co z tym zrobić?",
        "content": "Przy leasingu samochodu osobowego koszty uzyskania przychodów podlegają ustawowym ograniczeniom, a dla samochodu elektrycznego ustawodawca przewiduje wyższy limit wartości. Opłaty leasingowe są kosztem na zasadach z art. 23b, ale ograniczenie z art. 23 ust. 1 pkt 47a stosuje się proporcjonalnie do tej części opłaty, która dotyczy spłaty wartości samochodu. Podstawa prawna: art. 23 ust. 1 pkt 47a oraz art. 23b ust. 1 ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób fizycznych",
        "article_number": "art. 45 ust. 1",
        "category": "pit",
        "verified_date": "",
        "question_intent": "(do tej pory robiłem taką w druczkach a teraz podobno trzeba elektronicznie)?",
        "content": "Art. 45 ust. 1 wskazuje obowiązek złożenia zeznania według ustalonego wzoru. Sam ten przepis nie rozstrzyga wprost w przytoczonej treści, czy dany formularz ma być złożony papierowo czy elektronicznie, dlatego przy pytaniu o kanał wysyłki trzeba sprawdzić aktualny wzór i techniczny sposób składania udostępniony przez administrację skarbową. Podstawa prawna: art. 45 ust. 1 ustawy o PIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 26 ust. 1",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Czy ktoś posiada certyfikat rezydencji podatkowej za 2025 od: *Weglot SAS *Stripe *Squarespace Ireland *Serif Europe LTD?",
        "content": "Dla zastosowania stawki z umowy o unikaniu podwójnego opodatkowania albo niepobrania podatku u źródła płatnik musi udokumentować siedzibę podatnika uzyskanym od niego certyfikatem rezydencji. Art. 26 ust. 1 nakazuje też dochowanie należytej staranności przy weryfikacji warunków preferencji. Podstawa prawna: art. 26 ust. 1 ustawy o CIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 27 ust. 1",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Czy nadal trzeba pisać pisma o stwierdzenie nadpłaty i zwrot jesli wynika z cit8? Czy sami zwrócą?",
        "content": "Ustawa o CIT w art. 27 ust. 1 reguluje obowiązek złożenia CIT-8 i zapłaty podatku do końca trzeciego miesiąca roku następnego. Sam tryb stwierdzenia nadpłaty i jej zwrotu nie wynika z tego przepisu i co do zasady podlega Ordynacji podatkowej, więc z samej ustawy o CIT nie wynika automatyczny zwrot 'bez pisma' w każdej sytuacji. Podstawa prawna: art. 27 ust. 1 ustawy o CIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 26 ust. 1",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Ma może ktoś certyfikat rezydencji za rok 2025 od firmy Timocom Platz oraz Cookie Script?",
        "content": "Dla zastosowania preferencji WHT płatnik musi mieć certyfikat rezydencji podatnika i dochować należytej staranności przy weryfikacji warunków. Bez certyfikatu rezydencji art. 26 ust. 1 nie pozwala bezpiecznie zastosować stawki z umowy o unikaniu podwójnego opodatkowania ani nie pobrać podatku. Podstawa prawna: art. 26 ust. 1 ustawy o CIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 28m ust. 1 pkt 2 i 3",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Estoński CIT czy zakupiony obiad dla pracowników co jakiś czas to wydatek niezwiązany z działalnością gospodarczą czy kolacja służbowa?",
        "content": "W estońskim CIT opodatkowaniu podlegają m.in. ukryte zyski oraz wydatki niezwiązane z działalnością gospodarczą. Artykuł 28m ust. 1 nie tworzy automatycznej reguły, że każdy obiad dla pracowników jest albo zawsze kosztem firmowym, albo zawsze wydatkiem niezwiązanym z działalnością; trzeba ocenić rzeczywisty związek wydatku z działalnością spółki. Podstawa prawna: art. 28m ust. 1 pkt 2 i 3 ustawy o CIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 21 ust. 1 pkt 1 oraz art. 26 ust. 1",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Wynajem auta za granica. Czy w tej sytuacji należy pobrać podatek u źródła (WHT)?",
        "content": "Art. 21 ust. 1 pkt 1 obejmuje należności za użytkowanie lub prawo do użytkowania urządzenia przemysłowego, w tym także środka transportu. Jeżeli wypłata za zagraniczny wynajem auta mieści się w tym katalogu, płatnik co do zasady analizuje WHT według art. 26 ust. 1, z możliwością zastosowania umowy o unikaniu podwójnego opodatkowania po udokumentowaniu rezydencji kontrahenta. Podstawa prawna: art. 21 ust. 1 pkt 1 oraz art. 26 ust. 1 ustawy o CIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 26a ust. 1 oraz art. 21 ust. 1 pkt 2a",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Doby wieczór!. Składacie państwo deklarację IFT2R? Czy składa się do miesięcznej subskrypcji (Google, Adobe itp)?",
        "content": "Art. 26a ust. 1 przewiduje roczne deklaracje składane przez płatników po roku, w którym powstał obowiązek zapłaty podatku, a art. 21 ust. 1 pkt 2a wskazuje m.in. usługi reklamowe i przetwarzania danych jako należności mogące podlegać WHT. To oznacza, że przy subskrypcjach trzeba najpierw ocenić, czy płatność mieści się w katalogu art. 21 ust. 1 pkt 2a; dopiero wtedy powstaje temat obowiązków informacyjnych i deklaracyjnych. Podstawa prawna: art. 26a ust. 1 oraz art. 21 ust. 1 pkt 2a ustawy o CIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 26 ust. 1",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Czy ktoś z Państwa posiada certyfikat rezydencji podatkowej firmy Apple Distribution International Ltd. i mógłby się podzielić?",
        "content": "Dla zastosowania stawki traktatowej albo niepobrania WHT płatnik musi posiadać certyfikat rezydencji podatnika i dochować należytej staranności. Sama praktyczna dostępność certyfikatu od kontrahenta nie wynika z ustawy, ale bez tego dokumentu art. 26 ust. 1 nie daje podstawy do preferencyjnego rozliczenia podatku u źródła. Podstawa prawna: art. 26 ust. 1 ustawy o CIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 26 ust. 1",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Czy ma ktoś certyfikaty rezydencji za rok 2025 dla: Canva, Klaviyo,BunnyWay,Manychat, Zoom??",
        "content": "Przy rozliczeniu WHT płatnik stosuje preferencję z umowy o unikaniu podwójnego opodatkowania albo nie pobiera podatku tylko wtedy, gdy ma certyfikat rezydencji kontrahenta i dochowa należytej staranności. Bez certyfikatu rezydencji art. 26 ust. 1 nie pozwala bezpiecznie zastosować traktatowej stawki lub zwolnienia. Podstawa prawna: art. 26 ust. 1 ustawy o CIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 27 ust. 1 oraz art. 28b ust. 1",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Czy powinnam złożyć wniosek do US już teraz czy po wysłaniu CIT-8?",
        "content": "Art. 27 ust. 1 reguluje termin złożenia CIT-8 i zapłaty podatku, natomiast art. 28b ust. 1 przewiduje zwrot podatku pobranego zgodnie z art. 26 ust. 2e na wniosek. To oznacza, że moment składania wniosku zależy od tego, czy pytanie dotyczy zwrotu WHT z art. 28b, czy zwykłego rozliczenia rocznego z CIT-8, bo ustawa reguluje te tryby odrębnie. Podstawa prawna: art. 27 ust. 1 oraz art. 28b ust. 1 ustawy o CIT.",
    },
    {
        "law_name": "Ustawa o podatku dochodowym od osób prawnych",
        "article_number": "art. 26a ust. 1 oraz art. 21 ust. 1 pkt 2a",
        "category": "cit",
        "verified_date": "",
        "question_intent": "Czy składacie IFT-2R za dostęp do dysku w chmurze i usługi reklamowe z APPLE?Czy składacie IFT-2R za dostęp do dysku w chmurze i usługi reklamowe z APPLE?",
        "content": "Usługi reklamowe są wprost wymienione w art. 21 ust. 1 pkt 2a jako należności potencjalnie objęte WHT, a art. 26a ust. 1 reguluje roczne deklaracje składane po roku, w którym powstał obowiązek podatkowy. Dlatego przy płatnościach za reklamę i podobne usługi trzeba najpierw ustalić, czy świadczenie mieści się w katalogu art. 21 ust. 1 pkt 2a, a dopiero potem ocenić obowiązki informacyjne i deklaracyjne. Podstawa prawna: art. 26a ust. 1 oraz art. 21 ust. 1 pkt 2a ustawy o CIT.",
    },
]


def main() -> None:
    data = json.loads(KB_PATH.read_text(encoding="utf-8"))
    existing_keys = {
        (
            rec.get("law_name", ""),
            rec.get("article_number", ""),
            rec.get("question_intent", ""),
            rec.get("content", ""),
        )
        for rec in data
    }
    added = 0
    for rec in PATCH_RECORDS:
        key = (
            rec["law_name"],
            rec["article_number"],
            rec["question_intent"],
            rec["content"],
        )
        if key not in existing_keys:
            data.append(rec)
            existing_keys.add(key)
            added += 1
    data.sort(
        key=lambda rec: (
            rec.get("law_name", ""),
            rec.get("article_number", ""),
            rec.get("question_intent", ""),
            rec.get("content", ""),
        )
    )
    KB_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"added {added} records; total {len(data)}")


if __name__ == "__main__":
    main()
