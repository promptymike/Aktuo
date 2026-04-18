"""Apply 7 pending manual fixes (wf_24 x5 + wf_4 x2) — no LLM calls.

Fixes flags that repeatedly failed LLM JSON generation (same pattern as
wf_79 batch 1). Each function makes a narrow, targeted edit directly, then
logs the result in corrections_applied with source "*_manual".
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = ROOT / "data" / "workflow_drafts"
LOG_PATH = ROOT / "analysis" / "pending_manual_fixes_log.md"


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------
# wf_24 fixes
# ------------------------------------------------------------------

def _find_step(draft: dict[str, Any], step_no: int) -> dict[str, Any] | None:
    for s in draft.get("answer_steps") or []:
        if s.get("step") == step_no:
            return s
    return None


def wf24_flag0_legal_anchors(draft: dict[str, Any]) -> dict[str, Any]:
    """Populate empty legal_anchors with explicit references used in draft."""
    anchors = [
        {
            "law_name": "Rozporządzenie Ministra Pracy i Polityki Socjalnej z dnia 18 grudnia 1998 r. w sprawie szczegółowych zasad ustalania podstawy wymiaru składek na ubezpieczenia emerytalne i rentowe",
            "article_number": "§ 2 ust. 1 pkt 19",
            "description": "Zwolnienie ze składek ZUS świadczeń finansowanych z ZFŚS (kryterium socjalne).",
            "source": "ISAP Dz.U. 1998 nr 161 poz. 1106",
        },
        {
            "law_name": "Rozporządzenie Ministra Pracy i Polityki Socjalnej z dnia 18 grudnia 1998 r. w sprawie szczegółowych zasad ustalania podstawy wymiaru składek na ubezpieczenia emerytalne i rentowe",
            "article_number": "§ 2 ust. 1 pkt 26",
            "description": "Zwolnienie ze składek ZUS korzyści materialnych po cenie niższej niż detaliczna (wymaga zapisu w regulaminie + odpłatność pracownika min. 1 gr).",
            "source": "ISAP Dz.U. 1998 nr 161 poz. 1106",
        },
        {
            "law_name": "Rozporządzenie Ministra Pracy i Polityki Socjalnej z dnia 18 grudnia 1998 r. w sprawie szczegółowych zasad ustalania podstawy wymiaru składek na ubezpieczenia emerytalne i rentowe",
            "article_number": "§ 3 pkt 3",
            "description": "Zasady wyceny nieodpłatnego udostępnienia lokalu mieszkalnego dla celów ZUS (czynsz spółdzielczy/komunalny, stawki komunalne dla lokali własnościowych).",
            "source": "ISAP Dz.U. 1998 nr 161 poz. 1106",
        },
        {
            "law_name": "Ustawa z dnia 26 lipca 1991 r. o podatku dochodowym od osób fizycznych",
            "article_number": "art. 12 ust. 1",
            "description": "Definicja przychodu ze stosunku pracy (świadczenia w naturze jako przychód).",
            "source": "ustawa o PIT",
        },
        {
            "law_name": "Ustawa z dnia 26 lipca 1991 r. o podatku dochodowym od osób fizycznych",
            "article_number": "art. 21 ust. 1 pkt 67",
            "description": "Zwolnienie z PIT świadczeń finansowanych z ZFŚS do limitu 2 000 zł rocznie na pracownika (limit przedłużony na 2026 r.).",
            "source": "ustawa o PIT",
        },
        {
            "law_name": "Ustawa z dnia 4 października 2018 r. o pracowniczych planach kapitałowych",
            "article_number": "art. 2 pkt 40",
            "description": "Definicja 'wynagrodzenia' stanowiącego podstawę naliczania wpłat PPK — odwołanie do podstawy wymiaru składek emerytalno-rentowych (poprawna podstawa prawna dla podstawy wymiaru PPK).",
            "source": "ustawa o PPK",
        },
        {
            "law_name": "Ustawa z dnia 4 października 2018 r. o pracowniczych planach kapitałowych",
            "article_number": "art. 26 ust. 1",
            "description": "Wysokość wpłaty podstawowej pracodawcy do PPK (1,5% wynagrodzenia).",
            "source": "ustawa o PPK",
        },
        {
            "law_name": "Ustawa z dnia 11 marca 2004 r. o podatku od towarów i usług",
            "article_number": "art. 43 ust. 1 pkt 18-19",
            "description": "Zwolnienie z VAT usług w zakresie opieki medycznej (pakiety medyczne).",
            "source": "ustawa o VAT",
        },
        {
            "law_name": "Ustawa z dnia 11 marca 2004 r. o podatku od towarów i usług",
            "article_number": "poz. 186 załącznika nr 3",
            "description": "Stawka 8% VAT dla usług rekreacyjnych 'wyłącznie w zakresie wstępu' (karty typu Multisport).",
            "source": "ustawa o VAT",
        },
    ]
    draft["legal_anchors"] = anchors

    # Fix step 4 detail: it references art. 26 ust. 1 as the basis — swap to art. 2 pkt 40
    # per v2 reasoning (art. 26 ust. 1 dotyczy wysokości wpłaty, NIE podstawy).
    step4 = _find_step(draft, 4)
    if step4 is not None:
        old = step4.get("detail") or ""
        new = old.replace(
            "Podstawą naliczenia wpłat PPK jest podstawa wymiaru składek emerytalno-rentowych (art. 26 ust. 1 ustawy o PPK).",
            "Podstawą naliczenia wpłat PPK jest wynagrodzenie w rozumieniu art. 2 pkt 40 ustawy o PPK (podstawa wymiaru składek emerytalno-rentowych). Wysokość wpłaty pracodawcy 1,5% wynika z art. 26 ust. 1 ustawy o PPK.",
        )
        step4["detail"] = new
    return draft


def wf24_flag4_refaktura_clarification(draft: dict[str, Any]) -> dict[str, Any]:
    """Step 6: clarify that refaktura requires VAT document, not book entry; faktura wewnętrzna obsolete."""
    step6 = _find_step(draft, 6)
    if step6 is not None:
        old = step6.get("detail") or ""
        new = old.replace(
            "VAT: jeżeli pracownik współfinansuje, od części przypadającej na pracownika wystaw fakturę wewnętrzną/refakturę lub rozpoznaj sprzedaż opodatkowaną VAT 23% (dla Multisportu — 8% jako usługi rekreacyjne; pakiet medyczny — zwolniony z VAT art. 43 ust. 1 pkt 18–19 ustawy o VAT, więc bez VAT należnego od części pracownika).",
            "VAT: jeżeli pracownik współfinansuje, REFAKTURĘ wystaw jako faktycznie dokument VAT (fakturę) na pracownika ze stawką analogiczną do faktury zakupowej — dla pakietu medycznego 'zw' (art. 43 ust. 1 pkt 18–19 ustawy o VAT), dla Multisportu 8% (poz. 186 zał. nr 3 do ustawy o VAT — usługi rekreacyjne 'wyłącznie w zakresie wstępu'). UWAGA: nie jest to tylko zapis księgowy — refaktura wymaga wystawienia dokumentu VAT (JPK_V7). Faktura wewnętrzna została zniesiona w 2014 r. i nie jest już stosowana w polskim VAT; zastąpiły ją zwykłe faktury refaktury.",
        )
        step6["detail"] = new
    return draft


def wf24_flag7_edge_case_lokal(draft: dict[str, Any]) -> dict[str, Any]:
    """Add edge case about proper valuation of udostępnienie lokalu mieszkalnego (§ 3 pkt 3)."""
    ec = draft.get("edge_cases") or []
    new_ec = {
        "scenario": "Nieodpłatne udostępnienie lokalu mieszkalnego pracownikowi (mieszkanie służbowe, kwatera).",
        "handling": (
            "Dla ZUS wycena odbywa się wg § 3 pkt 3 rozporządzenia MPiPS z 18.12.1998 — NIE wg swobodnie "
            "ustalanej 'wartości rynkowej najmu'. Zasady: (a) lokale spółdzielcze — w wysokości czynszu spółdzielczego; "
            "(b) lokale komunalne — w wysokości czynszu komunalnego; (c) lokale własnościowe — w wysokości czynszu "
            "określonego wg zasad komunalnych dla lokali danej miejscowości; (d) domy/hotele robotnicze — wg rzeczywistych "
            "kosztów utrzymania. Dla PIT — wartość świadczenia wg art. 11 ust. 2a pkt 3 ustawy o PIT (cena stosowana wobec "
            "innych odbiorców). Obie wyceny mogą się różnić — stosuj każdą do właściwego rozliczenia (ZUS vs PIT)."
        ),
    }
    ec.append(new_ec)
    draft["edge_cases"] = ec
    return draft


def wf24_flag10_rozporzadzenie_title(draft: dict[str, Any]) -> dict[str, Any]:
    """Fix inline short references to 'rozporządzenie składkowe' — give full correct title in step 1 and step 2."""
    # Insert a clarifying first mention in step 1 and step 2 details.
    step1 = _find_step(draft, 1)
    if step1 is not None:
        old = step1.get("detail") or ""
        # Replace first occurrence of abbreviated label with full name + abbreviation mapping
        replacement = (
            "§ 2 ust. 1 pkt 19 rozporządzenia Ministra Pracy i Polityki Socjalnej z 18 grudnia 1998 r. "
            "w sprawie szczegółowych zasad ustalania podstawy wymiaru składek na ubezpieczenia emerytalne i rentowe "
            "(Dz.U. 1998 nr 161 poz. 1106, dalej: 'rozporządzenie składkowe')"
        )
        new = old.replace(
            "§ 2 ust. 1 pkt 19 rozporządzenia składkowego z 18.12.1998",
            replacement,
            1,
        )
        step1["detail"] = new

    step2 = _find_step(draft, 2)
    if step2 is not None:
        old = step2.get("detail") or ""
        # Ensure the § 2 ust. 1 pkt 26 reference uses the same full title at least once
        if "§ 2 ust. 1 pkt 26 rozporządzenia składkowego" in old and "Polityki Socjalnej" not in old:
            new = old.replace(
                "§ 2 ust. 1 pkt 26 rozporządzenia składkowego",
                "§ 2 ust. 1 pkt 26 rozporządzenia składkowego (rozporządzenie MPiPS z 18.12.1998 w sprawie podstawy wymiaru składek emerytalno-rentowych, Dz.U. 1998 nr 161 poz. 1106)",
                1,
            )
            step2["detail"] = new
    return draft


def wf24_flag11_multisport_vat(draft: dict[str, Any]) -> dict[str, Any]:
    """Step 6: expand VAT 8% note for Multisport with proper legal basis + exception."""
    step6 = _find_step(draft, 6)
    if step6 is not None:
        detail = step6.get("detail") or ""
        # Expand the existing 'dla Multisportu — 8%' clause if present (post flag#4 rewrite)
        if "Multisportu 8%" in detail and "wyłącznie w zakresie wstępu" in detail:
            # already expanded by flag#4 fix — still add the 23% exception footnote
            addition = (
                " Zastosowanie stawki 8% zależy od zakresu świadczenia — dla usług niesprowadzających się do samego wstępu "
                "(np. sprzedaż sprzętu, usługi indywidualne poza wstępem, pakiety z elementami towarowymi) "
                "stosuje się stawkę podstawową 23%. Przy wątpliwościach zweryfikuj z dostawcą (Benefit Systems, Medicover, PZU) "
                "klasyfikację PKWiU i zakres refakturowanej usługi — błędna stawka VAT grozi zaległością i odsetkami."
            )
            if addition.strip() not in detail:
                step6["detail"] = detail + addition
        else:
            # fallback — append context
            step6["detail"] = detail + (
                " VAT 8% dla Multisport/kart sportowych wynika z poz. 186 załącznika nr 3 do ustawy o VAT "
                "(usługi rekreacyjne 'wyłącznie w zakresie wstępu') — niezależnie od dostawcy. "
                "WYJĄTEK: dla usług wykraczających poza sam wstęp stosuje się stawkę podstawową 23%."
            )
    return draft


# ------------------------------------------------------------------
# wf_4 fixes
# ------------------------------------------------------------------

def wf4_flag2_ochrona_czasowa_date(draft: dict[str, Any]) -> dict[str, Any]:
    """Step 2: update ochrona czasowa date 4.03.2026 → 4.03.2027 + note specustawa wygaszona 5.03.2026."""
    step2 = _find_step(draft, 2)
    if step2 is not None:
        old = step2.get("detail") or ""
        new = old.replace(
            "UWAGA: na dzień 18.04.2026 obowiązują przepisy przedłużające ochronę czasową obywateli Ukrainy do 4.03.2026 — zweryfikuj aktualny stan nowelizacji specustawy (pisemne zapytanie w PUP / kancelarii wojewody), bo przepisy przejściowe mogły zostać zmie",
            "UWAGA: na dzień 18.04.2026 ochrona czasowa dla obywateli Ukrainy obowiązuje do 4 marca 2027 r. na podstawie decyzji Rady UE 2025/1460. Specustawa z 12.03.2022 została wygaszona ustawą z 23.01.2026 r. (wejście w życie 5.03.2026) i zastąpiona nowymi przepisami — zweryfikuj u siebie aktualny stan (gofin.pl, sejm.gov.pl), ponieważ przepisy przejściowe mogą zostać zmie",
        )
        step2["detail"] = new
    return draft


def wf4_flag4_brak_wniosku_o_przedluzenie(draft: dict[str, Any]) -> dict[str, Any]:
    """Step 7: add guidance for case when employee does NOT renew pobyt documents."""
    step7 = _find_step(draft, 7)
    if step7 is not None:
        old = step7.get("detail") or ""
        addition = (
            " KLUCZOWE — gdy pracownik NIE złoży wniosku o przedłużenie przed upływem ważności dokumentu: "
            "przepisy NIE przewidują automatycznego rozwiązania umowy o pracę po wygaśnięciu dokumentu pobytowego/zezwolenia. "
            "Obowiązek świadczenia pracy 'wygasa na okres' niespełnienia warunków (art. 25 ustawy z 23.01.2026 r. o zatrudnianiu "
            "cudzoziemców), a pracodawca MUSI aktywnie wypowiedzieć umowę lub zawrzeć porozumienie rozwiązujące — "
            "nie wystarczy bierne oczekiwanie. Procedura: (1) pisemne poinformowanie pracownika o zbliżającym się końcu "
            "legalnego pobytu (z co najmniej 30-dniowym wyprzedzeniem, potwierdzenie odbioru); "
            "(2) jeśli do daty wygaśnięcia nie zostanie złożony wniosek — wypowiedzenie umowy z powodu braku podstawy "
            "do wykonywania pracy (przyczyna niedotycząca pracownika sensu stricto) lub porozumienie stron; "
            "(3) w aktach osobowych załącz kopię wygasłego dokumentu + kopię pisma informacyjnego + dokument rozwiązania umowy. "
            "Nie ma okresu przejściowego — umowa nie rozwiązuje się 'sama' mimo utraty podstawy pobytu."
        )
        if addition.strip() not in old:
            step7["detail"] = old + addition
    return draft


# ------------------------------------------------------------------
# Orchestration
# ------------------------------------------------------------------

FIXES: list[dict[str, Any]] = [
    {
        "draft_id": "wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan",
        "flag_type": "legal_anchor_uncertainty",
        "flag_description_prefix": "Pole `legal_anchors` jest puste",
        "source": "v2_manual",
        "fn": wf24_flag0_legal_anchors,
        "summary": "Populacja legal_anchors (9 wpisów) + poprawka step 4: art. 2 pkt 40 ustawy o PPK jako podstawa wymiaru (art. 26 ust. 1 dotyczy wysokości wpłaty).",
    },
    {
        "draft_id": "wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan",
        "flag_type": "missing_critical_info",
        "flag_description_prefix": "Krok 6 wspomina 'refakturę' i 'fakturę wewnętrzną'",
        "source": "v3_manual",
        "fn": wf24_flag4_refaktura_clarification,
        "summary": "Step 6: refaktura wymaga wystawienia dokumentu VAT (nie tylko zapisu księgowego); faktura wewnętrzna zniesiona w 2014 r.",
    },
    {
        "draft_id": "wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan",
        "flag_type": "edge_case_coverage",
        "flag_description_prefix": "Edge case o nieodpłatnym udostępnieniu lokalu",
        "source": "v3_manual",
        "fn": wf24_flag7_edge_case_lokal,
        "summary": "Dodano edge_case o wycenie udostępnienia lokalu mieszkalnego wg § 3 pkt 3 rozporządzenia składkowego.",
    },
    {
        "draft_id": "wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan",
        "flag_type": "legal_anchor_uncertainty",
        "flag_description_prefix": "Draft wielokrotnie odwołuje się do 'rozporządzenia składkowego",
        "source": "v3_manual",
        "fn": wf24_flag10_rozporzadzenie_title,
        "summary": "Step 1 + step 2: pełny tytuł rozporządzenia MPiPS z 18.12.1998 (Polityki Socjalnej, nie Społecznej; ubezpieczenia emerytalne i rentowe).",
    },
    {
        "draft_id": "wf_24_benefity_pracownicze_oskladkowanie_opodatkowanie_i_ksiegowan",
        "flag_type": "missing_critical_info",
        "flag_description_prefix": "Krok 6 wspomina VAT 8% dla Multisportu",
        "source": "v3_manual",
        "fn": wf24_flag11_multisport_vat,
        "summary": "Step 6: poz. 186 zał. nr 3 ustawy o VAT, niezależna od dostawcy, wyjątek 23% dla usług poza 'wstępem'.",
    },
    {
        "draft_id": "wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty",
        "flag_type": "outdated_data_risk",
        "flag_description_prefix": "Krok 2 zawiera stwierdzenie 'na dzień 18.04.2026",
        "source": "v2_manual",
        "fn": wf4_flag2_ochrona_czasowa_date,
        "summary": "Step 2: ochrona czasowa do 4.03.2027 (decyzja Rady UE 2025/1460); specustawa wygaszona 5.03.2026 ustawą z 23.01.2026.",
    },
    {
        "draft_id": "wf_4_zatrudnianie_obywateli_ukrainy_formalnosci_i_dokumenty",
        "flag_type": "missing_critical_info",
        "flag_description_prefix": "Draft nie zawiera instrukcji, co zrobić, jeśli pracownik nie złoży wniosku",
        "source": "v2_manual",
        "fn": wf4_flag4_brak_wniosku_o_przedluzenie,
        "summary": "Step 7: dodano procedurę dla braku wniosku o przedłużenie — brak automatyki, obowiązek aktywnego wypowiedzenia (art. 25 ustawy z 23.01.2026).",
    },
]


def _find_flag(
    draft: dict[str, Any],
    flag_type: str,
    description_prefix: str,
) -> tuple[int, dict[str, Any]] | None:
    issues = (draft.get("self_critique") or {}).get("issues") or []
    for idx, f in enumerate(issues):
        if f.get("type") != flag_type:
            continue
        desc = f.get("description") or ""
        if desc.startswith(description_prefix):
            return idx, f
    return None


def apply_one(fix: dict[str, Any]) -> dict[str, Any]:
    """Apply one fix. Return status dict for logging."""
    draft_path = DRAFTS_DIR / f"{fix['draft_id']}.json"
    draft = json.loads(draft_path.read_text(encoding="utf-8"))

    located = _find_flag(draft, fix["flag_type"], fix["flag_description_prefix"])
    if located is None:
        return {
            "draft_id": fix["draft_id"],
            "flag_type": fix["flag_type"],
            "status": "SKIPPED_NOT_FOUND",
            "summary": fix["summary"],
        }
    flag_idx, flag = located

    # Already applied? (by description in corrections_applied list with matching source)
    for e in draft.get("corrections_applied") or []:
        if e.get("flag_description") == flag.get("description") and e.get("source") == fix["source"]:
            return {
                "draft_id": fix["draft_id"],
                "flag_type": fix["flag_type"],
                "flag_idx": flag_idx,
                "status": "SKIPPED_ALREADY_APPLIED",
                "summary": fix["summary"],
            }

    fn: Callable[[dict[str, Any]], dict[str, Any]] = fix["fn"]
    fn(draft)

    # Append corrections_applied entry
    entry = {
        "flag_type": flag.get("type"),
        "flag_description": flag.get("description"),
        "applied_at": now_iso_utc(),
        "source": fix["source"],
        "note": "Manual fix - LLM generated malformed JSON 3 times",
    }
    ca = draft.get("corrections_applied") or []
    ca.append(entry)
    draft["corrections_applied"] = ca

    draft_path.write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "draft_id": fix["draft_id"],
        "flag_type": fix["flag_type"],
        "flag_idx": flag_idx,
        "flag_description": flag.get("description"),
        "status": "APPLIED",
        "source": fix["source"],
        "summary": fix["summary"],
    }


def main() -> int:
    results: list[dict[str, Any]] = []
    for fix in FIXES:
        r = apply_one(fix)
        results.append(r)
        desc = (r.get("flag_description") or "")[:80]
        print(f"[{r['status']}] {r['draft_id'][:55]} [{r['flag_type']}] — {desc}")

    # Write log
    applied = [r for r in results if r["status"] == "APPLIED"]
    skipped = [r for r in results if r["status"] != "APPLIED"]
    lines: list[str] = []
    lines.append("# Pending Manual Fixes Log")
    lines.append("")
    lines.append(f"Data: {now_iso_utc()}")
    lines.append(f"Total pending flags: {len(FIXES)}")
    lines.append(f"Applied: {len(applied)}")
    lines.append(f"Skipped / not found: {len(skipped)}")
    lines.append("")
    lines.append("## Kontekst")
    lines.append(
        "Te flagi zawiodły Stage 5 (batch 2) albo Stage 8 (v3 corrections) z powodu LLM "
        "generującego malformed JSON przy 3 kolejnych próbach (identyczny pattern co wf_79 "
        "flag#4 batch 1). Napraw. bez LLM call — bezpośrednio w strukturze JSON."
    )
    lines.append("")
    lines.append("## Zastosowane fixy")
    for r in applied:
        lines.append(f"### {r['draft_id']} — flag [{r['flag_type']}]")
        lines.append(f"- **Source:** {r['source']}")
        lines.append(f"- **Flag opis:** {(r.get('flag_description') or '')[:400]}")
        lines.append(f"- **Zmiana:** {r['summary']}")
        lines.append("")
    if skipped:
        lines.append("## Skipped")
        for r in skipped:
            lines.append(f"- {r['draft_id']} [{r['flag_type']}] — {r['status']}")
        lines.append("")
    LOG_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nLog: {LOG_PATH}")
    return 0 if len(applied) == len(FIXES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
