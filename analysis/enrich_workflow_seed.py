from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

WORKFLOW_SEED_PATH = ROOT / "data" / "workflow" / "workflow_seed.json"
WORKFLOW_SPLIT_PATH = ROOT / "data" / "curated" / "workflow_vs_legal_vs_out_of_scope.jsonl"
GOLDEN_EVAL_PATH = ROOT / "data" / "curated" / "golden_eval_set.jsonl"
WORKFLOW_ANSWER_EVAL_PATH = ROOT / "analysis" / "workflow_answer_eval_report.json"
WORKFLOW_ROUTING_EVAL_PATH = ROOT / "analysis" / "workflow_eval_report.json"
REPORT_JSON_PATH = ROOT / "analysis" / "workflow_seed_enrichment_report.json"
REPORT_MD_PATH = ROOT / "analysis" / "workflow_seed_enrichment_report.md"

JSONDict = dict[str, Any]


@dataclass(frozen=True, slots=True)
class CandidateUnit:
    """Deterministic workflow-unit enrichment target."""

    title: str
    workflow_area: str
    category: str
    user_intent: str
    match_keywords: tuple[str, ...]
    template_steps: tuple[str, ...]
    template_required_inputs: tuple[str, ...]
    template_common_pitfalls: tuple[str, ...]
    template_related_forms: tuple[str, ...]
    template_related_systems: tuple[str, ...]
    create_if_missing: bool = False


SYSTEM_PATTERNS: dict[str, tuple[str, ...]] = {
    "KSeF": ("ksef", "krajowy system e-faktur"),
    "e-Urząd Skarbowy": ("e-urzad", "e urząd", "e-urząd"),
    "rejestr VAT": ("rejestr vat",),
    "ERP": ("erp",),
    "Comarch Optima": ("comarch", "optima"),
    "Symfonia": ("symfonia",),
    "Streamsoft": ("streamsoft",),
    "inFakt": ("infakt",),
    "Subiekt": ("subiekt",),
    "Rewizor GT": ("rewizor gt",),
    "Saldeo": ("saldeo",),
    "KRS": ("krs",),
    "eKRS": ("ekrs",),
    "bramka e-Sprawozdań": ("e-sprawozdan", "e sprawozdan"),
    "JPK": ("jpk",),
    "PUE ZUS": ("pue zus", "pue"),
    "e-Płatnik": ("e-platnik", "e platnik"),
    "KPiR": ("kpir",),
    "księgi rachunkowe": ("ksiegi rachunkowe", "pełne księgi", "pelne ksiegi"),
    "ewidencja środków trwałych": ("srodek trwaly", "środek trwały", "ewidencja srodkow trwalych"),
}

FORM_PATTERNS: dict[str, tuple[str, ...]] = {
    "JPK_V7M": ("jpk_v7m", "jpk v7m"),
    "JPK_V7K": ("jpk_v7k", "jpk v7k"),
    "ZAW-FA": ("zaw-fa", "zaw fa"),
    "UPL-1": ("upl-1", "upl 1", "upl"),
    "PPS-1": ("pps-1", "pps 1"),
    "ZUS ZUA": ("zus zua", "zua"),
    "ZUS ZWUA": ("zus zwua", "zwua"),
    "DRA": (" dra ", "zus dra", "deklaracji dra"),
    "RCA": (" rca ", "zus rca"),
    "RSA": (" rsa ", "zus rsa"),
    "PIT-11": ("pit-11", "pit11"),
    "PIT-4R": ("pit-4r", "pit4r"),
    "PIT-37": ("pit-37", "pit37"),
    "PIT-40A": ("pit-40a", "pit40a"),
    "PIT-11A": ("pit-11a", "pit11a"),
    "VAT-26": ("vat-26", "vat26"),
    "e-Sprawozdanie finansowe": ("sprawozdanie finansowe", "e-sprawozdanie", "e sprawozdanie"),
}


def normalize_text(value: str) -> str:
    """Normalize text for deterministic matching."""

    translation = str.maketrans(
        {
            "ą": "a",
            "ć": "c",
            "ę": "e",
            "ł": "l",
            "ń": "n",
            "ó": "o",
            "ś": "s",
            "ż": "z",
            "ź": "z",
        }
    )
    normalized = unicodedata.normalize("NFKD", value.lower().translate(translation))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return " ".join(ascii_value.split())


def read_json(path: Path) -> Any:
    """Load JSON from disk."""

    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[JSONDict]:
    """Load JSONL rows from disk."""

    rows: list[JSONDict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def write_json(path: Path, payload: Any) -> Path:
    """Write deterministic JSON to disk."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def unique_preserving_order(values: list[str], *, limit: int | None = None) -> list[str]:
    """Return unique stripped strings while preserving original order."""

    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned:
            continue
        key = normalize_text(cleaned)
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
        if limit is not None and len(result) >= limit:
            break
    return result


def field_richness(record: JSONDict) -> JSONDict:
    """Return simple richness counts for a workflow unit."""

    return {
        "question_examples": len(record.get("question_examples", [])),
        "steps": len(record.get("steps", [])),
        "required_inputs": len(record.get("required_inputs", [])),
        "common_pitfalls": len(record.get("common_pitfalls", [])),
        "related_forms": len(record.get("related_forms", [])),
        "related_systems": len(record.get("related_systems", [])),
    }


def detect_related_items(question: str, patterns: dict[str, tuple[str, ...]]) -> list[str]:
    """Extract canonical forms or systems mentioned in a question."""

    normalized = f" {normalize_text(question)} "
    found: list[str] = []
    for canonical, aliases in patterns.items():
        if any(alias in normalized for alias in aliases):
            found.append(canonical)
    return found


def keyword_score(spec: CandidateUnit, text: str) -> int:
    """Compute a simple keyword hit score for one candidate unit."""

    normalized = f" {normalize_text(text)} "
    return sum(1 for keyword in spec.match_keywords if normalize_text(keyword) in normalized)


CANDIDATE_UNITS: tuple[CandidateUnit, ...] = (
    CandidateUnit(
        title="Ujęcie dokumentów w odpowiednim okresie i ewidencji",
        workflow_area="KPiR / księgowanie / okresy i memoriał",
        category="rachunkowosc",
        user_intent="decision tree",
        match_keywords=("kpir", "memorial", "memoriał", "okres", "data wystawienia", "zaksięgować", "ująć"),
        template_steps=(
            "Określ, czy pytanie dotyczy bieżącego ujęcia, korekty wcześniejszego okresu czy powiązania kosztu z okresem lub dostawą.",
            "Zanim zapiszesz dokument, rozdziel wpływ na ewidencję podatkową, bilansową i VAT, jeśli pytanie dotyczy więcej niż jednego obszaru.",
        ),
        template_required_inputs=("sposób_ujęcia_lub_korekty", "powiązanie_z_okresem_lub_dostawą"),
        template_common_pitfalls=(
            "Mieszanie daty dokumentu z datą ujęcia bez zapisania przyjętej zasady księgowej lub podatkowej.",
            "Brak rozdzielenia skutku bilansowego, podatkowego i VAT przed zaksięgowaniem korekty albo kosztu.",
        ),
        template_related_forms=(),
        template_related_systems=("RMK",),
    ),
    CandidateUnit(
        title="Przygotowanie, podpisanie i wysyłka sprawozdania finansowego",
        workflow_area="Sprawozdanie finansowe / podpis / wysyłka",
        category="rachunkowosc",
        user_intent="checklist",
        match_keywords=("sprawozdanie", "krs", "ekrs", "bilans", "podpis", "wysyłk"),
        template_steps=(
            "Ustal, czy problem dotyczy przygotowania pliku, podpisu, wysyłki albo walidacji po stronie KRS lub bramki e-Sprawozdań.",
            "Przed wysyłką sprawdź komplet podpisów, typ jednostki i wariant dokumentu odpowiadający formie prawnej.",
        ),
        template_required_inputs=("forma_prawna_lub_typ_jednostki", "rodzaj_podpisu"),
        template_common_pitfalls=(
            "Mylenie błędu merytorycznego w sprawozdaniu z błędem technicznej wysyłki.",
            "Brak sprawdzenia, czy wszystkie wymagane osoby mogą podpisać dokument właściwym kanałem.",
        ),
        template_related_forms=("UPO",),
        template_related_systems=(),
    ),
    CandidateUnit(
        title="Obieg faktur, statusów i korekt w KSeF",
        workflow_area="KSeF issuing / correction / invoice circulation",
        category="ksef",
        user_intent="step-by-step procedure",
        match_keywords=("ksef", "offline", "qr", "status", "faktur", "pobran", "korekt"),
        template_steps=(
            "Najpierw ustal, czy problem dotyczy wystawienia, pobrania, statusu dokumentu, korekty czy synchronizacji z ERP.",
            "Zweryfikuj status dokumentu po stronie KSeF i po stronie systemu docelowego zanim ręcznie zmienisz rejestr lub ewidencję.",
        ),
        template_required_inputs=("status_dokumentu_lub_komunikat", "kanał_wystawienia_lub_pobrania"),
        template_common_pitfalls=(
            "Zakładanie, że brak dokumentu w ERP oznacza brak dokumentu w KSeF.",
            "Ręczne poprawianie ewidencji bez zapisania statusu dokumentu, numeru KSeF albo kanału obiegu.",
        ),
        template_related_forms=(),
        template_related_systems=("Comarch Optima", "Symfonia", "Streamsoft"),
    ),
    CandidateUnit(
        title="Obsługa problemów systemowych i synchronizacji danych",
        workflow_area="Oprogramowanie księgowe / integracje / synchronizacja",
        category="software_tooling",
        user_intent="step-by-step procedure",
        match_keywords=("program", "system", "symfonia", "optima", "subiekt", "rewizor", "saldeo", "błąd", "synchroniz", "integrac"),
        template_steps=(
            "Zanotuj nazwę systemu, moduł, komunikat błędu i moment procesu, w którym pojawia się problem.",
            "Oddziel problem techniczny integracji od pytania o poprawną ewidencję albo skutki podatkowe dokumentu.",
        ),
        template_required_inputs=("moduł_lub_funkcja", "komunikat_błędu_lub_status"),
        template_common_pitfalls=(
            "Mieszanie problemu konfiguracyjnego z pytaniem o poprawną ewidencję księgową lub podatkową.",
            "Brak odnotowania wersji systemu, modułu albo kanału importu i eksportu przed zgłoszeniem błędu.",
        ),
        template_related_forms=(),
        template_related_systems=("Comarch Optima", "Symfonia", "Streamsoft", "Subiekt", "Rewizor GT", "Saldeo", "inFakt"),
    ),
    CandidateUnit(
        title="Klasyfikacja dokumentów, kolumn i zapisów magazynowych",
        workflow_area="Dokumenty księgowe / magazyn / kolumny i klasyfikacja",
        category="rachunkowosc",
        user_intent="checklist",
        match_keywords=("kolumn", "towar", "koszty uboczne", "magazyn", "kst", "konto 300", "zakup"),
        template_steps=(
            "Ustal, czy dokument wymaga jednego zapisu, czy podziału na część towarową, kosztową, magazynową albo środek trwały.",
            "Jeżeli pytanie dotyczy kolumn, kont albo KŚT, przygotuj wariant klasyfikacji przed księgowaniem właściwym.",
        ),
        template_required_inputs=("rodzaj_zapisu_lub_klasyfikacji", "czy_dokument_wymaga_podziału"),
        template_common_pitfalls=(
            "Księgowanie całego dokumentu jednym schematem mimo różnych części gospodarczych na fakturze.",
            "Brak odnotowania, dlaczego wybrano daną kolumnę, konto, KŚT albo zapis magazynowy.",
        ),
        template_related_forms=(),
        template_related_systems=("konto 300",),
    ),
    CandidateUnit(
        title="Obsługa wysyłki, korekty i oznaczeń JPK",
        workflow_area="JPK filing / correction / tags",
        category="jpk",
        user_intent="checklist",
        match_keywords=("jpk", "gtu", "bfk", "di", "korekt", "oznaczen", "znacznik"),
        template_steps=(
            "Ustal, czy chodzi o pierwszą wysyłkę, korektę pliku, oznaczenie GTU/procedury czy techniczne złożenie JPK.",
            "Przed wysyłką sprawdź, czy zmiana dotyczy części ewidencyjnej, deklaracyjnej czy obu części pliku.",
        ),
        template_required_inputs=("typ_pliku_lub_wersja_jpk", "rodzaj_korekty_lub_oznaczenia"),
        template_common_pitfalls=(
            "Zmiana oznaczeń bez wskazania okresu, typu korekty albo części pliku, której dotyczy poprawka.",
            "Brak zachowania UPO albo numeru referencyjnego po ponownej wysyłce pliku.",
        ),
        template_related_forms=("UPO",),
        template_related_systems=("bramka JPK", "program księgowy"),
    ),
    CandidateUnit(
        title="Obsługa zgłoszeń, wyrejestrowań i deklaracji ZUS",
        workflow_area="ZUS / PUE / zgłoszenia i wyrejestrowania",
        category="zus",
        user_intent="step-by-step procedure",
        match_keywords=("zus", "pue", "e-platnik", "zua", "zwua", "dra", "rca", "rsa", "wyrejestrow"),
        template_steps=(
            "Ustal, czy sprawa dotyczy zgłoszenia, wyrejestrowania, deklaracji rozliczeniowej czy odpowiedzi z PUE/ZUS.",
            "Przed wysyłką sprawdź status osoby, tytuł do ubezpieczenia i zakres dokumentu, który chcesz poprawić albo złożyć.",
        ),
        template_required_inputs=("status_osoby", "rodzaj_dokumentu_zus"),
        template_common_pitfalls=(
            "Wysyłka formularza bez ustalenia właściwego tytułu do ubezpieczenia albo rodzaju zgłoszenia.",
            "Brak rozróżnienia między pierwszym zgłoszeniem, korektą i wyrejestrowaniem.",
        ),
        template_related_forms=(),
        template_related_systems=(),
    ),
    CandidateUnit(
        title="Nadawanie uprawnień i dostępów w KSeF",
        workflow_area="KSeF permissions / authorization flow",
        category="ksef",
        user_intent="required documents/forms list",
        match_keywords=("uprawnien", "dostep", "token", "certyfikat", "zaw-fa", "przekazywania", "administratora"),
        template_steps=(
            "Ustal, kto nadaje dostęp, komu i czy chodzi o podgląd, wystawianie, pobieranie czy dalsze delegowanie uprawnień.",
            "Sprawdź, czy operacja wymaga tokenu, certyfikatu albo przejścia przez e-Urząd Skarbowy.",
        ),
        template_required_inputs=("rola_lub_status_strony", "zakres_uprawnienia"),
        template_common_pitfalls=(
            "Mylenie uprawnienia do podglądu z uprawnieniem do dalszego nadawania albo zarządzania dostępami.",
            "Brak ustalenia, czy operacja ma być wykonana bezpośrednio w KSeF czy przez e-Urząd Skarbowy.",
        ),
        template_related_forms=(),
        template_related_systems=(),
    ),
    CandidateUnit(
        title="Pełnomocnictwa, podpisy i elektroniczne kanały złożenia",
        workflow_area="Pełnomocnictwa / podpis / kanały złożenia",
        category="procedury",
        user_intent="required documents/forms list",
        match_keywords=("pełnomocnict", "upl", "pps", "czynny żal", "podpis", "profil zaufany", "e-urzad"),
        template_steps=(
            "Ustal, czy sprawa dotyczy pełnomocnictwa, podpisu, czynnego żalu, UPL-1/PPS-1 czy samego kanału złożenia dokumentu.",
            "Przed wysyłką sprawdź, kto podpisuje dokument, w jakiej roli działa i przez jaki kanał ma zostać złożony.",
        ),
        template_required_inputs=("rola_podpisującego", "kanał_złożenia"),
        template_common_pitfalls=(
            "Złożenie dokumentu innym kanałem niż przyjęty dla reszty sprawy bez zapisania potwierdzenia złożenia.",
            "Brak ustalenia, czy podpis składa podatnik, pełnomocnik czy księgowy działający w imieniu klienta.",
        ),
        template_related_forms=(),
        template_related_systems=(),
    ),
    CandidateUnit(
        title="Leasing, wykup samochodu i ewidencja kosztów pojazdu",
        workflow_area="Leasing / samochód / VAT-26 / koszty i ewidencja",
        category="rachunkowosc",
        user_intent="decision tree",
        match_keywords=("leasing", "samoch", "vat-26", "vat26", "wykup", "śt", "srodek trwaly", "amortyz", "20 %", "100% vat"),
        template_steps=(
            "Ustal, czy pytanie dotyczy leasingu operacyjnego, wykupu pojazdu, klasyfikacji do ewidencji czy rozliczenia kosztów po zmianie sposobu używania.",
            "Zanim zaksięgujesz dokument, rozdziel wpływ na rejestr VAT, KPiR albo księgi rachunkowe oraz ewidencję środka trwałego.",
            "Sprawdź, czy pojazd jest firmowy, prywatny po wykupie czy używany mieszanie, i odnotuj to w opisie operacji.",
            "Zapisz przyjęty wariant ewidencji oraz dokument potwierdzający status pojazdu i sposób użytkowania.",
        ),
        template_required_inputs=(
            "rodzaj_leasingu",
            "status_pojazdu_w_firmie",
            "sposób_użytkowania_pojazdu",
            "okres_lub_data",
            "rodzaj_ewidencji",
        ),
        template_common_pitfalls=(
            "Mieszanie skutku bilansowego, podatkowego i VAT bez rozpisania każdego obszaru osobno.",
            "Brak ustalenia, czy pojazd po wykupie trafia do firmy, do majątku prywatnego czy do ewidencji środka trwałego.",
        ),
        template_related_forms=("VAT-26",),
        template_related_systems=("rejestr VAT", "KPiR", "księgi rachunkowe", "ewidencja środków trwałych"),
        create_if_missing=True,
    ),
)

NEXT_BATCH_RECOMMENDATIONS: tuple[CandidateUnit, ...] = (
    CandidateUnit(
        title="Wybór i wdrożenie programu księgowego",
        workflow_area="ERP / wybór systemu / wdrożenie zespołu",
        category="software_tooling",
        user_intent="decision tree",
        match_keywords=("program", "wdroż", "system", "optima", "symfonia", "subiekt", "saldeo", "rewizor"),
        template_steps=(),
        template_required_inputs=(),
        template_common_pitfalls=(),
        template_related_forms=(),
        template_related_systems=(),
    ),
    CandidateUnit(
        title="Import usług i dokumentów zagranicznych w systemie księgowym",
        workflow_area="VAT / import usług / dokumenty zagraniczne w ewidencji",
        category="vat_jpk_ksef",
        user_intent="checklist",
        match_keywords=("import usług", "import uslug", "kontrahent zagraniczny", "apple", "irlandia", "art. 28b"),
        template_steps=(),
        template_required_inputs=(),
        template_common_pitfalls=(),
        template_related_forms=(),
        template_related_systems=(),
    ),
    CandidateUnit(
        title="Dekretacja list płac i zgodność bilansowo-podatkowa",
        workflow_area="Kadry / płace / dekretacja i koszty",
        category="kadry",
        user_intent="checklist",
        match_keywords=("umowa zlecenie", "lista płac", "zaliczka miesięczna", "zaliczka kwartalna", "koszty bilansowe"),
        template_steps=(),
        template_required_inputs=(),
        template_common_pitfalls=(),
        template_related_forms=(),
        template_related_systems=(),
    ),
    CandidateUnit(
        title="Konta techniczne, RMK i przeksięgowania roczne",
        workflow_area="Rachunkowość operacyjna / RMK / konta techniczne",
        category="rachunkowosc",
        user_intent="decision tree",
        match_keywords=("rmk", "konto 300", "konto 245", "konto 249", "przeksięgowanie", "przeksiegowanie"),
        template_steps=(),
        template_required_inputs=(),
        template_common_pitfalls=(),
        template_related_forms=(),
        template_related_systems=(),
    ),
    CandidateUnit(
        title="Sprawozdawczość i znaczniki w konkretnych systemach ERP",
        workflow_area="Sprawozdanie finansowe / ERP / znaczniki i walidacja",
        category="rachunkowosc",
        user_intent="step-by-step procedure",
        match_keywords=("rewizor", "znaczniki", "krs", "e-sprawozdanie", "wysyłki do krs", "wysylki do krs"),
        template_steps=(),
        template_required_inputs=(),
        template_common_pitfalls=(),
        template_related_forms=(),
        template_related_systems=(),
    ),
    CandidateUnit(
        title="Kadry i płace w systemach operacyjnych",
        workflow_area="Kadry / płace / systemy kadrowo-płacowe",
        category="kadry",
        user_intent="checklist",
        match_keywords=("kadrowo", "placow", "składkę zdrowotną", "skladke zdrowotna", "dwóch pracowników", "program kadrowo"),
        template_steps=(),
        template_required_inputs=(),
        template_common_pitfalls=(),
        template_related_forms=(),
        template_related_systems=(),
    ),
)


def merge_rows(workflow_rows: list[JSONDict], golden_rows: list[JSONDict]) -> list[JSONDict]:
    """Merge workflow and golden datasets by normalized question."""

    merged: dict[str, JSONDict] = {}
    for row in workflow_rows + golden_rows:
        question = str(row.get("question", "")).strip()
        if not question:
            continue
        key = normalize_text(question)
        previous = merged.get(key)
        candidate = dict(row)
        if previous is None or int(candidate.get("source_frequency", 1) or 1) > int(previous.get("source_frequency", 1) or 1):
            merged[key] = candidate
    return list(merged.values())


def gather_candidate_context(
    spec: CandidateUnit,
    merged_rows: list[JSONDict],
    answer_eval_report: JSONDict,
    routing_eval_report: JSONDict,
) -> JSONDict:
    """Collect matched dataset rows and failure signals for one candidate unit."""

    matched_rows = [
        row
        for row in merged_rows
        if keyword_score(
            spec,
            " ".join(
                str(row.get(field, ""))
                for field in ("question", "notes", "source_category", "source_subcategory", "expected_law_or_area")
            ),
        )
        > 0
    ]
    matched_rows.sort(
        key=lambda row: (
            -keyword_score(
                spec,
                " ".join(
                    str(row.get(field, ""))
                    for field in ("question", "notes", "source_category", "source_subcategory", "expected_law_or_area")
                ),
            ),
            -int(row.get("source_frequency", 1) or 1),
            str(row.get("question", "")),
        )
    )

    answer_records = [
        row
        for row in answer_eval_report.get("records", [])
        if keyword_score(spec, " ".join(str(row.get(field, "")) for field in ("question", "expected_law_or_area", "source_category"))) > 0
    ]
    routing_failures = [
        row
        for row in routing_eval_report.get("error_analysis", {}).get("top_workflow_questions_incorrectly_went_to_legal", [])
        if keyword_score(spec, " ".join(str(row.get(field, "")) for field in ("question", "expected_law_or_area", "source_category"))) > 0
    ]

    clarification_freq = sum(
        int(row.get("source_frequency", 1) or 1)
        for row in answer_records
        if row.get("subset") == "workflow_answer_expected" and row.get("needs_clarification")
    )
    routing_failure_freq = sum(int(row.get("source_frequency", 1) or 1) for row in routing_failures)
    dataset_freq = sum(int(row.get("source_frequency", 1) or 1) for row in matched_rows[:10])

    return {
        "matched_rows": matched_rows,
        "answer_records": answer_records,
        "routing_failures": routing_failures,
        "clarification_freq": clarification_freq,
        "routing_failure_freq": routing_failure_freq,
        "dataset_freq": dataset_freq,
        "impact_score": round((clarification_freq * 2.0) + (routing_failure_freq * 1.5) + dataset_freq, 2),
    }


def build_unit_record(
    spec: CandidateUnit,
    existing_record: JSONDict | None,
    context: JSONDict,
) -> JSONDict:
    """Create an enriched workflow record from evidence and deterministic templates."""

    matched_rows: list[JSONDict] = context["matched_rows"]
    question_examples = unique_preserving_order(
        list(existing_record.get("question_examples", []) if existing_record else [])
        + [str(row.get("question", "")).strip() for row in matched_rows[:8]],
        limit=8,
    )
    matched_missing_fields = [
        str(slot)
        for row in matched_rows
        for slot in row.get("missing_clarification_fields", [])
        if isinstance(slot, str)
    ]

    return {
        "workflow_area": spec.workflow_area,
        "title": spec.title,
        "category": spec.category,
        "question_examples": question_examples,
        "steps": unique_preserving_order(
            list(existing_record.get("steps", []) if existing_record else []) + list(spec.template_steps),
            limit=7,
        ),
        "required_inputs": unique_preserving_order(
            list(existing_record.get("required_inputs", []) if existing_record else [])
            + list(spec.template_required_inputs)
            + matched_missing_fields,
            limit=7,
        ),
        "common_pitfalls": unique_preserving_order(
            list(existing_record.get("common_pitfalls", []) if existing_record else [])
            + list(spec.template_common_pitfalls),
            limit=6,
        ),
        "related_forms": unique_preserving_order(
            list(existing_record.get("related_forms", []) if existing_record else [])
            + [
                form
                for row in matched_rows[:12]
                for form in detect_related_items(str(row.get("question", "")), FORM_PATTERNS)
            ]
            + list(spec.template_related_forms),
            limit=6,
        ),
        "related_systems": unique_preserving_order(
            list(existing_record.get("related_systems", []) if existing_record else [])
            + [
                system
                for row in matched_rows[:12]
                for system in detect_related_items(str(row.get("question", "")), SYSTEM_PATTERNS)
            ]
            + list(spec.template_related_systems),
            limit=8,
        ),
        "source_type": str(existing_record.get("source_type", "workflow_seed_v1")) if existing_record else "workflow_seed_v1",
        "user_intent": str(existing_record.get("user_intent", spec.user_intent)) if existing_record else spec.user_intent,
        "cluster_impact": dict(existing_record.get("cluster_impact", {})) if existing_record else {
            "question_count": len(matched_rows),
            "total_frequency": context["dataset_freq"],
            "weighted_impact": round(context["impact_score"], 2),
        },
    }


def safe_enough(record: JSONDict) -> bool:
    """Return True when a workflow unit can support a minimal useful answer."""

    return (
        len(record.get("question_examples", [])) >= 3
        and len(record.get("steps", [])) >= 3
        and (
            len(record.get("required_inputs", [])) >= 1
            or len(record.get("common_pitfalls", [])) >= 1
        )
    )


def build_next_recommendations(
    merged_rows: list[JSONDict],
    answer_eval_report: JSONDict,
) -> list[JSONDict]:
    """Build deterministic next-batch recommendations from remaining weak workflow evidence."""

    weak_rows = [
        row
        for row in answer_eval_report.get("records", [])
        if row.get("subset") == "workflow_answer_expected" and row.get("needs_clarification")
    ]
    recommendations: list[JSONDict] = []
    for spec in NEXT_BATCH_RECOMMENDATIONS:
        matched_questions = [
            row
            for row in weak_rows
            if keyword_score(
                spec,
                " ".join(str(row.get(field, "")) for field in ("question", "source_category", "expected_law_or_area")),
            )
            > 0
        ]
        if not matched_questions:
            continue
        examples = unique_preserving_order([str(row.get("question", "")).strip() for row in matched_questions], limit=3)
        total_frequency = sum(int(row.get("source_frequency", 1) or 1) for row in matched_questions)
        recommendations.append(
            {
                "title": spec.title,
                "workflow_area": spec.workflow_area,
                "impact_score": round((len(matched_questions) * 2.0) + total_frequency, 2),
                "question_count": len(matched_questions),
                "total_frequency": total_frequency,
                "examples": examples,
            }
        )

    if recommendations:
        return sorted(
            recommendations,
            key=lambda item: (-float(item["impact_score"]), item["title"]),
        )[:5]

    fallback_rows = sorted(
        (
            row
            for row in weak_rows
            if str(row.get("question", "")).strip()
        ),
        key=lambda row: (-int(row.get("source_frequency", 1) or 1), str(row.get("question", ""))),
    )
    fallback: list[JSONDict] = []
    for row in fallback_rows[:5]:
        fallback.append(
            {
                "title": str(row.get("question", "")).strip()[:80],
                "workflow_area": str(row.get("source_category", "workflow")).strip(),
                "impact_score": int(row.get("source_frequency", 1) or 1),
                "question_count": 1,
                "total_frequency": int(row.get("source_frequency", 1) or 1),
                "examples": [str(row.get("question", "")).strip()],
            }
        )
    return fallback


def enrich_workflow_seed(
    *,
    workflow_seed_path: Path = WORKFLOW_SEED_PATH,
    workflow_split_path: Path = WORKFLOW_SPLIT_PATH,
    golden_eval_path: Path = GOLDEN_EVAL_PATH,
    workflow_answer_eval_path: Path = WORKFLOW_ANSWER_EVAL_PATH,
    workflow_routing_eval_path: Path = WORKFLOW_ROUTING_EVAL_PATH,
    report_json_path: Path = REPORT_JSON_PATH,
    report_md_path: Path = REPORT_MD_PATH,
) -> JSONDict:
    """Enrich top workflow units in-place using deterministic project evidence."""

    seed_rows: list[JSONDict] = read_json(workflow_seed_path)
    workflow_rows = read_jsonl(workflow_split_path)
    golden_rows = read_jsonl(golden_eval_path)
    answer_eval_report: JSONDict = read_json(workflow_answer_eval_path)
    routing_eval_report: JSONDict = read_json(workflow_routing_eval_path)
    merged_rows = merge_rows(workflow_rows, golden_rows)

    existing_by_title = {str(row.get("title", "")): row for row in seed_rows}
    contexts = {
        spec.title: gather_candidate_context(spec, merged_rows, answer_eval_report, routing_eval_report)
        for spec in CANDIDATE_UNITS
    }

    selected_specs = sorted(
        CANDIDATE_UNITS,
        key=lambda spec: (
            -contexts[spec.title]["impact_score"],
            -len(existing_by_title.get(spec.title, {}).get("question_examples", [])),
            spec.title,
        ),
    )[:10]
    selected_titles = {spec.title for spec in selected_specs}

    before_seed = json.loads(json.dumps(seed_rows, ensure_ascii=False))
    enriched_records: dict[str, JSONDict] = {}
    report_units: list[JSONDict] = []
    safely_enriched: list[str] = []
    deferred: list[JSONDict] = []

    for spec in selected_specs:
        existing_record = existing_by_title.get(spec.title)
        enriched = build_unit_record(spec, existing_record, contexts[spec.title])
        enriched_records[spec.title] = enriched

        before_richness = field_richness(existing_record) if existing_record else {
            "question_examples": 0,
            "steps": 0,
            "required_inputs": 0,
            "common_pitfalls": 0,
            "related_forms": 0,
            "related_systems": 0,
        }
        after_richness = field_richness(enriched)

        if safe_enough(enriched):
            safely_enriched.append(spec.title)
        else:
            deferred.append(
                {
                    "title": spec.title,
                    "reason": "insufficient_evidence_for_minimum_answer_viability",
                }
            )

        report_units.append(
            {
                "title": spec.title,
                "workflow_area": spec.workflow_area,
                "selected_because": {
                    "clarification_freq": contexts[spec.title]["clarification_freq"],
                    "routing_failure_freq": contexts[spec.title]["routing_failure_freq"],
                    "dataset_freq": contexts[spec.title]["dataset_freq"],
                    "impact_score": contexts[spec.title]["impact_score"],
                },
                "before_richness": before_richness,
                "after_richness": after_richness,
                "added_question_examples": max(0, after_richness["question_examples"] - before_richness["question_examples"]),
                "estimated_impact_on_clarification": {
                    "affected_questions": contexts[spec.title]["clarification_freq"],
                    "heuristic_priority": "high" if contexts[spec.title]["clarification_freq"] >= 10 else "medium" if contexts[spec.title]["clarification_freq"] >= 4 else "low",
                },
                "top_examples": enriched["question_examples"][:5],
                "safely_enriched": spec.title in safely_enriched,
            }
        )

    updated_seed: list[JSONDict] = []
    existing_titles_in_seed = {row["title"] for row in seed_rows if "title" in row}
    for row in seed_rows:
        title = str(row.get("title", ""))
        updated_seed.append(enriched_records.get(title, row))

    for spec in selected_specs:
        if (
            spec.create_if_missing
            and spec.title not in existing_titles_in_seed
            and spec.title in enriched_records
        ):
            updated_seed.append(enriched_records[spec.title])

    workflow_seed_path.write_text(json.dumps(updated_seed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    next_candidates = build_next_recommendations(merged_rows, answer_eval_report)

    report = {
        "selected_units": report_units,
        "selected_count": len(selected_specs),
        "safely_enriched_units": safely_enriched,
        "deferred_units": deferred,
        "units_safely_enriched_count": len(safely_enriched),
        "before_seed_unit_count": len(before_seed),
        "after_seed_unit_count": len(updated_seed),
        "new_units_added": [spec.title for spec in selected_specs if spec.title not in existing_titles_in_seed],
        "next_recommended_units": next_candidates,
    }
    write_json(report_json_path, report)

    md_lines = [
        "# Workflow Seed Enrichment Report",
        "",
        f"- Selected top units: {len(selected_specs)}",
        f"- Safely enriched: {len(safely_enriched)}",
        f"- New units added: {len(report['new_units_added'])}",
        "",
        "## Selected Top Units",
        "",
    ]
    for unit in report_units:
        md_lines.extend(
            [
                f"### {unit['title']}",
                f"- workflow_area: {unit['workflow_area']}",
                f"- impact_score: {unit['selected_because']['impact_score']}",
                f"- clarification_freq: {unit['selected_because']['clarification_freq']}",
                f"- routing_failure_freq: {unit['selected_because']['routing_failure_freq']}",
                f"- dataset_freq: {unit['selected_because']['dataset_freq']}",
                f"- before richness: {unit['before_richness']}",
                f"- after richness: {unit['after_richness']}",
                f"- safely_enriched: {unit['safely_enriched']}",
                "",
            ]
        )

    md_lines.extend(["## Deferred Units", ""])
    if not deferred:
        md_lines.append("- none")
    else:
        for item in deferred:
            md_lines.append(f"- {item['title']}: {item['reason']}")

    md_lines.extend(["", "## Next 5 Recommended Units", ""])
    if not next_candidates:
        md_lines.append("- none")
    else:
        for item in next_candidates:
            md_lines.append(f"- {item['title']} ({item['impact_score']})")

    report_md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    """CLI entry point for workflow-seed enrichment."""

    parser = argparse.ArgumentParser(description="Enrich high-impact workflow seed units.")
    parser.parse_args()
    report = enrich_workflow_seed()
    print(
        json.dumps(
            {
                "selected_count": report["selected_count"],
                "units_safely_enriched_count": report["units_safely_enriched_count"],
                "new_units_added": report["new_units_added"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
