from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SPLIT_PATH = ROOT / "data" / "curated" / "workflow_vs_legal_vs_out_of_scope.jsonl"
GOLDEN_EVAL_PATH = ROOT / "data" / "curated" / "golden_eval_set.jsonl"
WORKFLOW_DIR = ROOT / "data" / "workflow"
WORKFLOW_SEED_PATH = WORKFLOW_DIR / "workflow_seed.json"
REPORT_JSON_PATH = ROOT / "analysis" / "workflow_seed_report.json"
REPORT_MD_PATH = ROOT / "analysis" / "workflow_seed_report.md"

JSONDict = dict[str, Any]
EXCLUDED_WORKFLOW_PATTERNS: tuple[str, ...] = (
    "jaki program",
    "jakie programy",
    "program polecacie",
    "polecacie",
    "szukam osoby",
    "szukam pracy",
    "wdrozeniow",
    "programiste",
    "informatyka",
    "kurs",
    "szkolen",
    "czy ktos pracuje",
    "czy ktos korzysta",
    "fundacja rozwoju rachunkowosci",
    "stowarzyszeniu ksiegowych",
    "skwp",
)


@dataclass(slots=True)
class WorkflowRecord:
    """A curated workflow-like question selected for workflow seed generation."""

    question: str
    normalized_question: str
    classification: str
    primary_intent: str
    source_category: str
    source_subcategory: str
    source_frequency: int
    missing_clarification_fields: tuple[str, ...]
    golden_overlap: bool


@dataclass(frozen=True, slots=True)
class ClusterDefinition:
    """Deterministic definition describing a workflow cluster."""

    name: str
    workflow_area: str
    title: str
    category: str
    answer_shape: str
    keywords: tuple[str, ...]
    related_forms: tuple[str, ...]
    related_systems: tuple[str, ...]
    priority_weight: float = 1.0


@dataclass(slots=True)
class WorkflowCluster:
    """Assigned cluster with its matching records."""

    definition: ClusterDefinition
    records: list[WorkflowRecord]

    @property
    def total_frequency(self) -> int:
        return sum(record.source_frequency for record in self.records)

    @property
    def weighted_impact(self) -> float:
        return self.total_frequency * self.definition.priority_weight


CLUSTER_DEFINITIONS: tuple[ClusterDefinition, ...] = (
    ClusterDefinition(
        name="jpk_filing_corrections_tags",
        workflow_area="JPK filing / correction / tags",
        title="Obsługa wysyłki, korekty i oznaczeń JPK",
        category="jpk",
        answer_shape="checklist",
        keywords=("jpk", "jpk_v7", "gtu", "bfk", "di", "fp", "ro", "wew", "mpp", "korekta jpk", "bramka"),
        related_forms=("JPK_V7M", "JPK_V7K"),
        related_systems=("JPK", "e-Urząd Skarbowy"),
        priority_weight=1.35,
    ),
    ClusterDefinition(
        name="ksef_permissions_authorizations",
        workflow_area="KSeF permissions / authorization flow",
        title="Nadawanie uprawnień i dostępów w KSeF",
        category="ksef",
        answer_shape="required documents/forms list",
        keywords=("ksef", "uprawn", "token", "zaw-fa", "pełnomoc", "dostęp", "administrator"),
        related_forms=("ZAW-FA", "UPL-1", "PPS-1"),
        related_systems=("KSeF", "e-Urząd Skarbowy", "Profil Zaufany"),
        priority_weight=1.4,
    ),
    ClusterDefinition(
        name="ksef_invoice_circulation",
        workflow_area="KSeF issuing / correction / invoice circulation",
        title="Obieg faktur, statusów i korekt w KSeF",
        category="ksef",
        answer_shape="step-by-step procedure",
        keywords=("ksef", "offline", "qr", "faktura", "korekta", "nie pojawiła", "pobra", "wysła"),
        related_forms=(),
        related_systems=("KSeF", "ERP", "rejestr VAT"),
        priority_weight=1.35,
    ),
    ClusterDefinition(
        name="zus_pue_registrations",
        workflow_area="ZUS / PUE / zgłoszenia i wyrejestrowania",
        title="Obsługa zgłoszeń, wyrejestrowań i deklaracji ZUS",
        category="zus",
        answer_shape="step-by-step procedure",
        keywords=("zus", "pue", "zua", "zwua", "dra", "rca", "rsa", "zgłosz", "wyrejestrow", "e-płatnik"),
        related_forms=("ZUS ZUA", "ZUS ZWUA", "DRA", "RCA", "RSA"),
        related_systems=("PUE ZUS", "e-Płatnik"),
        priority_weight=1.3,
    ),
    ClusterDefinition(
        name="tax_authorizations_and_signatures",
        workflow_area="Pełnomocnictwa / podpis / kanały złożenia",
        title="Pełnomocnictwa, podpisy i elektroniczne kanały złożenia",
        category="procedury",
        answer_shape="required documents/forms list",
        keywords=("upl-1", "pps-1", "pełnomoc", "profil zaufany", "podpis", "bramka", "e-urząd", "czynny żal"),
        related_forms=("UPL-1", "PPS-1"),
        related_systems=("e-Urząd Skarbowy", "Profil Zaufany", "podpis kwalifikowany"),
        priority_weight=1.2,
    ),
    ClusterDefinition(
        name="accounting_posting_and_periods",
        workflow_area="KPiR / księgowanie / okresy i memoriał",
        title="Ujęcie dokumentów w odpowiednim okresie i ewidencji",
        category="rachunkowosc",
        answer_shape="decision tree",
        keywords=("zaksię", "uję", "okres", "kpir", "memoria", "remanent", "bilans", "kup", "kolumn"),
        related_forms=(),
        related_systems=("KPiR", "księgi rachunkowe", "rejestr VAT"),
        priority_weight=1.5,
    ),
    ClusterDefinition(
        name="inventory_documents_and_columns",
        workflow_area="Dokumenty księgowe / magazyn / kolumny i klasyfikacja",
        title="Klasyfikacja dokumentów, kolumn i zapisów magazynowych",
        category="rachunkowosc",
        answer_shape="checklist",
        keywords=("towar", "magazyn", "kolumn", "koszty uboczne", "pozostałe wydatki", "kśt", "środek trwały", "amortyz"),
        related_forms=(),
        related_systems=("KPiR", "magazyn", "ewidencja środków trwałych"),
        priority_weight=1.2,
    ),
    ClusterDefinition(
        name="software_and_sync_operations",
        workflow_area="Oprogramowanie księgowe / integracje / synchronizacja",
        title="Obsługa problemów systemowych i synchronizacji danych",
        category="software_tooling",
        answer_shape="step-by-step procedure",
        keywords=("optima", "symfonia", "comarch", "enova", "insert", "subiekt", "infakt", "streamsoft", "integrac", "import", "eksport"),
        related_forms=(),
        related_systems=("ERP", "program księgowy", "integracja API"),
        priority_weight=1.1,
    ),
    ClusterDefinition(
        name="financial_statements_workflow",
        workflow_area="Sprawozdanie finansowe / podpis / wysyłka",
        title="Przygotowanie, podpisanie i wysyłka sprawozdania finansowego",
        category="rachunkowosc",
        answer_shape="checklist",
        keywords=("sprawozdanie", "sf", "bilans", "rzis", "podpisa", "wysyłk", "krs", "xml"),
        related_forms=("e-Sprawozdanie finansowe",),
        related_systems=("KRS", "eKRS", "bramka e-Sprawozdań"),
        priority_weight=1.35,
    ),
    ClusterDefinition(
        name="fallback_other_workflow",
        workflow_area="Pozostałe operacje workflow",
        title="Pozostałe powtarzalne operacje księgowe i proceduralne",
        category="workflow",
        answer_shape="checklist",
        keywords=(),
        related_forms=(),
        related_systems=(),
        priority_weight=0.8,
    ),
)


def normalize_text(value: str) -> str:
    """Return a lowercase, ASCII-safe representation for keyword matching."""

    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^a-z0-9]+", " ", ascii_value.lower())
    return " ".join(cleaned.split())


def read_jsonl(path: Path) -> list[JSONDict]:
    """Read a JSONL file into a list of dictionaries."""

    records: list[JSONDict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def is_excluded_workflow_question(normalized_question: str) -> bool:
    """Filter out community, recruiting, and tool-recommendation questions from the seed."""

    return any(pattern in normalized_question for pattern in EXCLUDED_WORKFLOW_PATTERNS)


def select_workflow_records(
    workflow_split_path: Path = WORKFLOW_SPLIT_PATH,
    golden_eval_path: Path = GOLDEN_EVAL_PATH,
) -> list[WorkflowRecord]:
    """Select workflow and mixed questions, preserving useful context for prioritisation."""

    golden_questions = {
        normalize_text(record["question"])
        for record in read_jsonl(golden_eval_path)
        if record.get("question")
    }
    selected: list[WorkflowRecord] = []
    for record in read_jsonl(workflow_split_path):
        if record.get("classification") not in {"workflow", "mixed"}:
            continue
        question = str(record.get("question", "")).strip()
        if not question:
            continue
        normalized_question = normalize_text(question)
        if is_excluded_workflow_question(normalized_question):
            continue
        selected.append(
            WorkflowRecord(
                question=question,
                normalized_question=normalized_question,
                classification=str(record.get("classification", "workflow")),
                primary_intent=str(record.get("primary_intent", "workflow")),
                source_category=str(record.get("source_category", "")),
                source_subcategory=str(record.get("source_subcategory", "")),
                source_frequency=int(record.get("source_frequency", 1) or 1),
                missing_clarification_fields=tuple(record.get("missing_clarification_fields", [])),
                golden_overlap=normalized_question in golden_questions,
            )
        )
    return sorted(
        selected,
        key=lambda item: (
            -item.source_frequency,
            item.primary_intent,
            item.source_category,
            item.normalized_question,
        ),
    )


def _match_score(record: WorkflowRecord, definition: ClusterDefinition) -> int:
    """Return a simple deterministic keyword score for a cluster."""

    if definition.name == "fallback_other_workflow":
        return -1
    haystack = " ".join(
        [
            record.normalized_question,
            normalize_text(record.source_category),
            normalize_text(record.source_subcategory),
            normalize_text(record.primary_intent),
        ]
    )
    tokens = haystack.split()
    score = 0
    for keyword in definition.keywords:
        normalized_keyword = normalize_text(keyword)
        if not normalized_keyword:
            continue
        if " " in normalized_keyword:
            matched = f" {normalized_keyword} " in f" {haystack} "
            if matched:
                score += 3
            continue
        if len(normalized_keyword) <= 4:
            matched = normalized_keyword in tokens
        else:
            matched = any(token.startswith(normalized_keyword) for token in tokens)
        if matched:
            score += 2
    if definition.category == record.source_category:
        score += 2
    if record.golden_overlap:
        score += 1
    return score


def assign_cluster(record: WorkflowRecord) -> str:
    """Assign the most suitable workflow cluster name for a single record."""

    scored = sorted(
        ((definition.name, _match_score(record, definition)) for definition in CLUSTER_DEFINITIONS),
        key=lambda item: (-item[1], item[0]),
    )
    best_name, best_score = scored[0]
    return best_name if best_score > 1 else "fallback_other_workflow"


def cluster_workflow_records(records: list[WorkflowRecord]) -> list[WorkflowCluster]:
    """Group workflow records into deterministic high-level workflow clusters."""

    grouped: dict[str, list[WorkflowRecord]] = defaultdict(list)
    definitions = {definition.name: definition for definition in CLUSTER_DEFINITIONS}
    for record in records:
        grouped[assign_cluster(record)].append(record)
    clusters = [
        WorkflowCluster(
            definition=definitions[name],
            records=sorted(
                items,
                key=lambda record: (-record.source_frequency, record.normalized_question),
            ),
        )
        for name, items in grouped.items()
    ]
    return sorted(
        clusters,
        key=lambda cluster: (
            -cluster.weighted_impact,
            -cluster.total_frequency,
            cluster.definition.name,
        ),
    )


def _top_unique_questions(records: list[WorkflowRecord], limit: int = 5) -> list[str]:
    """Return top unique question examples for a cluster."""

    seen: set[str] = set()
    results: list[str] = []
    for record in records:
        if record.question in seen:
            continue
        seen.add(record.question)
        results.append(record.question)
        if len(results) >= limit:
            break
    return results


def _top_missing_fields(records: list[WorkflowRecord], limit: int = 5) -> list[str]:
    """Return most common missing clarification fields inside a cluster."""

    counts = Counter(field for record in records for field in record.missing_clarification_fields)
    return [field for field, _ in counts.most_common(limit)]


def _workflow_steps(definition: ClusterDefinition, missing_fields: list[str]) -> list[str]:
    """Build a concise workflow-first step list grounded in recurring dataset themes."""

    base_steps = [
        "Ustal, jakiej czynności operacyjnej dotyczy pytanie i jaki jest oczekiwany efekt końcowy.",
        "Zbierz minimalne dane wejściowe potrzebne do wykonania czynności w systemie lub ewidencji.",
        "Zweryfikuj okres, dokument oraz rolę użytkownika przed wykonaniem operacji lub wysyłki.",
        "Wykonaj operację w odpowiednim module lub kanale i zapisz numer referencyjny, status albo potwierdzenie.",
        "Po zakończeniu sprawdź wynik w systemie docelowym i zanotuj ewentualne punkty kontrolne do korekty.",
    ]
    if definition.answer_shape == "required documents/forms list":
        base_steps[1] = "Zbierz wymagane dokumenty, uprawnienia i kanał podpisu potrzebny do wykonania czynności."
    if definition.answer_shape == "decision tree":
        base_steps[2] = "Ustal właściwy wariant działania na podstawie okresu, typu ewidencji i rodzaju dokumentu."
    if missing_fields:
        base_steps.insert(1, f"Najpierw doprecyzuj brakujące informacje: {', '.join(missing_fields)}.")
    return base_steps[:5]


def _workflow_pitfalls(definition: ClusterDefinition, missing_fields: list[str]) -> list[str]:
    """Return practical pitfalls for a workflow cluster without inventing legal content."""

    pitfalls = [
        "Rozpoczęcie operacji bez potwierdzenia okresu, dokumentu lub właściwego modułu.",
        "Brak zapisania statusu, numeru referencyjnego albo potwierdzenia po wysyłce.",
    ]
    if definition.related_forms:
        pitfalls.append("Pominięcie właściwego formularza lub podpisu elektronicznego dla danej czynności.")
    if definition.category in {"ksef", "jpk", "zus"}:
        pitfalls.append("Założenie, że dane zsynchronizowały się automatycznie bez sprawdzenia statusu po stronie systemu docelowego.")
    if missing_fields:
        pitfalls.append(f"Brak doprecyzowania pól wejściowych: {', '.join(missing_fields)}.")
    return pitfalls[:4]


def build_workflow_units(clusters: list[WorkflowCluster], unit_limit: int = 10) -> list[JSONDict]:
    """Convert the top-impact clusters into workflow seed units."""

    units: list[JSONDict] = []
    for cluster in clusters:
        if cluster.definition.name == "fallback_other_workflow":
            continue
        if len(units) >= unit_limit:
            break
        missing_fields = _top_missing_fields(cluster.records)
        units.append(
            {
                "workflow_area": cluster.definition.workflow_area,
                "title": cluster.definition.title,
                "category": cluster.definition.category,
                "question_examples": _top_unique_questions(cluster.records),
                "steps": _workflow_steps(cluster.definition, missing_fields),
                "required_inputs": missing_fields,
                "common_pitfalls": _workflow_pitfalls(cluster.definition, missing_fields),
                "related_forms": list(cluster.definition.related_forms),
                "related_systems": list(cluster.definition.related_systems),
                "source_type": "workflow_seed_v1",
                "user_intent": cluster.definition.answer_shape,
                "cluster_impact": {
                    "question_count": len(cluster.records),
                    "total_frequency": cluster.total_frequency,
                    "weighted_impact": round(cluster.weighted_impact, 2),
                },
            }
        )
    return units


def validate_workflow_units(units: list[JSONDict]) -> None:
    """Raise ValueError if the workflow seed schema is incomplete."""

    mandatory_keys = (
        "workflow_area",
        "title",
        "category",
        "question_examples",
        "steps",
        "required_inputs",
        "common_pitfalls",
        "related_forms",
        "related_systems",
        "source_type",
    )
    for index, unit in enumerate(units):
        for key in mandatory_keys:
            if key not in unit:
                raise ValueError(f"Workflow unit {index} is missing key: {key}")
            value = unit[key]
            if isinstance(value, str) and not value.strip():
                raise ValueError(f"Workflow unit {index} has empty value for key: {key}")
            if isinstance(value, list) and key in {"question_examples", "steps"} and not value:
                raise ValueError(f"Workflow unit {index} has empty list for key: {key}")


def build_workflow_seed_report(clusters: list[WorkflowCluster], units: list[JSONDict], analyzed_count: int) -> JSONDict:
    """Build a machine-readable report summarizing the workflow seed selection."""

    area_counts = Counter(cluster.definition.workflow_area for cluster in clusters for _ in cluster.records)
    missing_field_counts = Counter(
        field for cluster in clusters for record in cluster.records for field in record.missing_clarification_fields
    )
    return {
        "workflow_questions_analyzed": analyzed_count,
        "workflow_seed_units_created": len(units),
        "top_workflow_clusters_by_impact": [
            {
                "cluster_name": cluster.definition.name,
                "workflow_area": cluster.definition.workflow_area,
                "question_count": len(cluster.records),
                "total_frequency": cluster.total_frequency,
                "weighted_impact": round(cluster.weighted_impact, 2),
                "top_examples": _top_unique_questions(cluster.records, limit=3),
                "answer_shape": cluster.definition.answer_shape,
            }
            for cluster in clusters[:10]
        ],
        "top_workflow_areas": [
            {"workflow_area": area, "question_count": count}
            for area, count in area_counts.most_common(10)
        ],
        "top_missing_information_fields": [
            {"field": field, "count": count}
            for field, count in missing_field_counts.most_common(10)
        ],
        "suggested_top_10_workflow_units": [
            {
                "title": unit["title"],
                "workflow_area": unit["workflow_area"],
                "category": unit["category"],
                "question_examples_count": len(unit["question_examples"]),
                "required_inputs": unit["required_inputs"],
            }
            for unit in units[:10]
        ],
        "recommended_next_step": (
            "Zbudować osobny indeks retrieval dla workflow_seed.json i uruchamiać go przed legal KB "
            "dla pytań o klasyfikacji workflow/software_tooling, z zachowaniem dopytań o brakujące pola wejściowe."
        ),
    }


def render_workflow_seed_report_markdown(report: JSONDict) -> str:
    """Render a concise markdown report for humans."""

    lines = [
        "# Workflow Seed Report",
        "",
        f"- Workflow questions analyzed: {report['workflow_questions_analyzed']}",
        f"- Workflow seed units created: {report['workflow_seed_units_created']}",
        "",
        "## Top workflow clusters by impact",
        "",
        "| Cluster | Area | Questions | Total freq | Impact |",
        "|---|---|---:|---:|---:|",
    ]
    for cluster in report["top_workflow_clusters_by_impact"]:
        lines.append(
            f"| {cluster['cluster_name']} | {cluster['workflow_area']} | {cluster['question_count']} | "
            f"{cluster['total_frequency']} | {cluster['weighted_impact']} |"
        )
    lines.extend(
        [
            "",
            "## Top workflow areas",
            "",
            "| Area | Questions |",
            "|---|---:|",
        ]
    )
    for area in report["top_workflow_areas"]:
        lines.append(f"| {area['workflow_area']} | {area['question_count']} |")
    lines.extend(
        [
            "",
            "## Top missing information fields",
            "",
            "| Field | Count |",
            "|---|---:|",
        ]
    )
    for field in report["top_missing_information_fields"]:
        lines.append(f"| {field['field']} | {field['count']} |")
    lines.extend(["", "## Suggested top 10 workflow units", ""])
    for index, unit in enumerate(report["suggested_top_10_workflow_units"], start=1):
        lines.append(
            f"{index}. {unit['title']} ({unit['category']}) — required inputs: "
            f"{', '.join(unit['required_inputs']) if unit['required_inputs'] else 'brak'}"
        )
    lines.extend(["", "## Recommended next step", "", report["recommended_next_step"], ""])
    return "\n".join(lines)


def write_json(path: Path, payload: Any) -> None:
    """Write JSON using UTF-8 and stable formatting."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def build_workflow_seed(
    workflow_split_path: Path = WORKFLOW_SPLIT_PATH,
    golden_eval_path: Path = GOLDEN_EVAL_PATH,
    workflow_seed_path: Path = WORKFLOW_SEED_PATH,
    report_json_path: Path = REPORT_JSON_PATH,
    report_md_path: Path = REPORT_MD_PATH,
    unit_limit: int = 10,
) -> tuple[list[JSONDict], JSONDict]:
    """Build workflow seed units and write both machine-readable and markdown reports."""

    records = select_workflow_records(workflow_split_path, golden_eval_path)
    clusters = cluster_workflow_records(records)
    units = build_workflow_units(clusters, unit_limit=unit_limit)
    validate_workflow_units(units)
    report = build_workflow_seed_report(clusters, units, analyzed_count=len(records))
    write_json(workflow_seed_path, units)
    write_json(report_json_path, report)
    report_md_path.parent.mkdir(parents=True, exist_ok=True)
    report_md_path.write_text(render_workflow_seed_report_markdown(report), encoding="utf-8")
    return units, report


def main() -> None:
    """CLI entrypoint for generating the workflow knowledge seed."""

    parser = argparse.ArgumentParser(description="Build the first workflow knowledge seed from curated data.")
    parser.add_argument("--unit-limit", type=int, default=10, help="How many top workflow units to emit.")
    args = parser.parse_args()
    units, report = build_workflow_seed(unit_limit=args.unit_limit)
    print(f"Workflow questions analyzed: {report['workflow_questions_analyzed']}")
    print(f"Workflow seed units created: {len(units)}")
    top_titles = ", ".join(unit["title"] for unit in units[:3])
    print(f"Top workflow units: {top_titles}")


if __name__ == "__main__":
    main()
