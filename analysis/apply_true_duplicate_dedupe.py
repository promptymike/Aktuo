from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = ROOT / "analysis"
SEED_DIR = ROOT / "data" / "seeds"

REPORT_PATH = ANALYSIS_DIR / "duplicate_groups_report.json"
PLAN_PATH = ANALYSIS_DIR / "dedupe_true_duplicate_plan.json"
APPLIED_PATH = ANALYSIS_DIR / "dedupe_true_duplicate_applied.json"

KB_PATHS = {
    "law_knowledge.json": SEED_DIR / "law_knowledge.json",
    "law_knowledge_additions.json": SEED_DIR / "law_knowledge_additions.json",
    "law_knowledge_curated_additions.json": SEED_DIR / "law_knowledge_curated_additions.json",
}

BACKUP_SUFFIX = ".backup_pre_dedupe_true"
EXPECTED_TRUE_GROUPS = 60
EXPECTED_RECORDS_TO_REMOVE = 72
EXPECTED_FINAL_RECORD_COUNT = 4472
CURATED_FILE = "law_knowledge_curated_additions.json"
PRIMARY_FILE = "law_knowledge.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deduplicate true duplicates from KB files.")
    parser.add_argument("--apply", action="store_true", help="Apply dedupe plan to KB files.")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_payload_and_records(path: Path) -> tuple[Any, list[dict[str, Any]]]:
    payload = load_json(path)
    records = payload["records"] if isinstance(payload, dict) else payload
    return payload, records


def write_payload(path: Path, payload: Any) -> None:
    dump_json(path, payload)


def normalize_preview(text: str, width: int = 160) -> str:
    compact = " ".join(text.split())
    return compact[:width]


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verified(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def ensure_backup(path: Path) -> Path:
    backup = path.with_name(path.name + BACKUP_SUFFIX)
    if not backup.exists():
        shutil.copy2(path, backup)
    return backup


def restore_backups() -> None:
    for path in KB_PATHS.values():
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        if backup.exists():
            shutil.copy2(backup, path)


def load_true_duplicate_groups() -> list[dict[str, Any]]:
    report = load_json(REPORT_PATH)
    true_groups = [group for group in report["groups"] if group["classification"] == "true_duplicate"]
    if report["classification_summary"]["true_duplicate"] != EXPECTED_TRUE_GROUPS:
        raise ValueError(
            f"Expected {EXPECTED_TRUE_GROUPS} true_duplicate groups, found "
            f"{report['classification_summary']['true_duplicate']}."
        )
    would_remove = report["records_impact"]["would_remove_if_dedupe_true_duplicates"]
    if would_remove != EXPECTED_RECORDS_TO_REMOVE:
        raise ValueError(
            f"Expected {EXPECTED_RECORDS_TO_REMOVE} records to remove, found {would_remove}."
        )
    if len(true_groups) != EXPECTED_TRUE_GROUPS:
        raise ValueError(
            f"Expected {EXPECTED_TRUE_GROUPS} true_duplicate groups in report body, found {len(true_groups)}."
        )
    computed_remove = sum(group["count"] - 1 for group in true_groups)
    if computed_remove != EXPECTED_RECORDS_TO_REMOVE:
        raise ValueError(
            f"Expected computed removable records = {EXPECTED_RECORDS_TO_REMOVE}, found {computed_remove}."
        )
    return true_groups


def load_all_records() -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    payloads: dict[str, Any] = {}
    per_file_records: dict[str, list[dict[str, Any]]] = {}
    merged: list[dict[str, Any]] = []
    for file_name, path in KB_PATHS.items():
        payload, records = load_payload_and_records(path)
        payloads[file_name] = payload
        per_file_records[file_name] = records
        for index, record in enumerate(records):
            merged_record = dict(record)
            merged_record["_source_file"] = file_name
            merged_record["_record_index"] = index
            merged.append(merged_record)
    return payloads, per_file_records, merged


def build_lookup(records: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    return {(record["_source_file"], record["_record_index"]): record for record in records}


def choose_record(group: dict[str, Any], records: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    verified_candidates = [record for record in records if verified(record.get("verified_date"))]
    if verified_candidates:
        if len(verified_candidates) == 1:
            return verified_candidates[0], "priority_1_verified"
        curated_verified = [record for record in verified_candidates if record["_source_file"] == CURATED_FILE]
        candidate_pool = curated_verified or verified_candidates
        candidate_pool = sorted(
            candidate_pool,
            key=lambda record: (-len(record.get("content", "")), record["_record_index"]),
        )
        leader = candidate_pool[0]
        if len(candidate_pool) >= 2 and abs(len(candidate_pool[0].get("content", "")) - len(candidate_pool[1].get("content", ""))) <= 5:
            return min(candidate_pool, key=lambda record: record["_record_index"]), "tiebreak_lowest_index"
        return leader, "priority_1_verified"

    curated_candidates = [record for record in records if record["_source_file"] == CURATED_FILE]
    if curated_candidates:
        if len(curated_candidates) == 1:
            return curated_candidates[0], "priority_2_curated_additions"
        sorted_curated = sorted(
            curated_candidates,
            key=lambda record: (-len(record.get("content", "")), record["_record_index"]),
        )
        leader = sorted_curated[0]
        if len(sorted_curated) >= 2 and abs(len(sorted_curated[0].get("content", "")) - len(sorted_curated[1].get("content", ""))) <= 5:
            return min(sorted_curated, key=lambda record: record["_record_index"]), "tiebreak_lowest_index"
        return leader, "priority_2_curated_additions"

    primary_candidates = [record for record in records if record["_source_file"] == PRIMARY_FILE]
    candidate_pool = primary_candidates or records
    sorted_candidates = sorted(
        candidate_pool,
        key=lambda record: (-len(record.get("content", "")), record["_record_index"]),
    )
    leader = sorted_candidates[0]
    if len(sorted_candidates) >= 2 and abs(len(sorted_candidates[0].get("content", "")) - len(sorted_candidates[1].get("content", ""))) <= 5:
        return min(sorted_candidates, key=lambda record: record["_record_index"]), "tiebreak_lowest_index"
    return leader, "priority_3_longest_content"


def build_decisions(true_groups: list[dict[str, Any]], merged_records: list[dict[str, Any]]) -> dict[str, Any]:
    lookup = build_lookup(merged_records)
    decisions: list[dict[str, Any]] = []
    summary_by_priority = Counter(
        {
            "priority_1_verified": 0,
            "priority_2_curated": 0,
            "priority_3_longest_content": 0,
            "tiebreak_lowest_index": 0,
        }
    )
    total_records_to_remove = 0

    for group in true_groups:
        resolved_records: list[dict[str, Any]] = []
        for record in group["records"]:
            key = (record["source_file"], record["record_index"])
            if key not in lookup:
                raise ValueError(f"Record {key} from report not found in current KB.")
            resolved_records.append(lookup[key])

        kept, reason = choose_record(group, resolved_records)
        removed = [record for record in resolved_records if record is not kept]
        total_records_to_remove += len(removed)

        if reason == "priority_1_verified":
            summary_by_priority["priority_1_verified"] += 1
        elif reason == "priority_2_curated_additions":
            summary_by_priority["priority_2_curated"] += 1
        elif reason == "priority_3_longest_content":
            summary_by_priority["priority_3_longest_content"] += 1
        elif reason == "tiebreak_lowest_index":
            summary_by_priority["tiebreak_lowest_index"] += 1
        else:
            raise ValueError(f"Unexpected reason: {reason}")

        decisions.append(
            {
                "group_key": group["group_key"],
                "law_name": group["law_name"],
                "article_number": group["article_number"],
                "kept": {
                    "file": kept["_source_file"],
                    "index": kept["_record_index"],
                    "content_preview": normalize_preview(kept.get("content", "")),
                    "content_hash": content_hash(kept.get("content", "")),
                    "verified_date": kept.get("verified_date", ""),
                },
                "reason": reason,
                "removed": [
                    {
                        "file": record["_source_file"],
                        "index": record["_record_index"],
                        "content_preview": normalize_preview(record.get("content", "")),
                        "content_hash": content_hash(record.get("content", "")),
                        "verified_date": record.get("verified_date", ""),
                    }
                    for record in sorted(removed, key=lambda item: (item["_source_file"], item["_record_index"]))
                ],
            }
        )

    if len(decisions) != EXPECTED_TRUE_GROUPS:
        raise ValueError(f"Expected {EXPECTED_TRUE_GROUPS} decisions, found {len(decisions)}.")
    if total_records_to_remove != EXPECTED_RECORDS_TO_REMOVE:
        raise ValueError(
            f"Expected {EXPECTED_RECORDS_TO_REMOVE} records to remove, planned {total_records_to_remove}."
        )

    return {
        "total_groups_processed": len(decisions),
        "total_records_to_remove": total_records_to_remove,
        "decisions": decisions,
        "summary_by_priority": dict(summary_by_priority),
    }


def plan_payload(plan_data: dict[str, Any], mode: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "total_groups_processed": plan_data["total_groups_processed"],
        "total_records_to_remove": plan_data["total_records_to_remove"],
        "decisions": plan_data["decisions"],
        "summary_by_priority": plan_data["summary_by_priority"],
    }


def verify_plan_matches_current(plan: dict[str, Any], merged_records: list[dict[str, Any]]) -> None:
    lookup = build_lookup(merged_records)
    for decision in plan["decisions"]:
        group_key = decision["group_key"]
        for kept_or_removed in [decision["kept"], *decision["removed"]]:
            key = (kept_or_removed["file"], kept_or_removed["index"])
            current = lookup.get(key)
            if current is None:
                raise ValueError(f"{group_key}: record {key} no longer exists.")
            current_hash = content_hash(current.get("content", ""))
            if current_hash != kept_or_removed["content_hash"]:
                raise ValueError(f"{group_key}: record {key} content hash changed since dry-run.")


def remove_records_from_payloads(
    payloads: dict[str, Any],
    per_file_records: dict[str, list[dict[str, Any]]],
    plan: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, int]]:
    removals_by_file: dict[str, set[int]] = defaultdict(set)
    for decision in plan["decisions"]:
        for removed in decision["removed"]:
            removals_by_file[removed["file"]].add(removed["index"])

    records_removed_per_file: dict[str, int] = {}
    updated_payloads: dict[str, Any] = {}

    for file_name, payload in payloads.items():
        records = per_file_records[file_name]
        remove_indexes = removals_by_file.get(file_name, set())
        updated_records = [record for index, record in enumerate(records) if index not in remove_indexes]
        records_removed_per_file[file_name] = len(remove_indexes)
        if isinstance(payload, dict):
            new_payload = dict(payload)
            new_payload["records"] = updated_records
        else:
            new_payload = updated_records
        updated_payloads[file_name] = new_payload

    return updated_payloads, records_removed_per_file


def validate_json_files() -> None:
    for path in KB_PATHS.values():
        load_json(path)


def validate_true_duplicates_resolved(true_groups: list[dict[str, Any]]) -> int:
    _, _, merged_records = load_all_records()
    counts = Counter((record["law_name"], record["article_number"]) for record in merged_records)
    unresolved = 0
    for group in true_groups:
        key = (group["law_name"], group["article_number"])
        if counts[key] != 1:
            unresolved += 1
    return unresolved


def total_kb_records() -> int:
    return sum(len(load_payload_and_records(path)[1]) for path in KB_PATHS.values())


def run_dry_run() -> dict[str, Any]:
    true_groups = load_true_duplicate_groups()
    _, _, merged_records = load_all_records()
    plan_data = build_decisions(true_groups, merged_records)
    payload = plan_payload(plan_data, mode="dry_run")
    dump_json(PLAN_PATH, payload)
    return payload


def run_apply() -> dict[str, Any]:
    if not PLAN_PATH.exists():
        raise FileNotFoundError("Dry-run plan not found. Run without --apply first.")

    true_groups = load_true_duplicate_groups()
    plan = load_json(PLAN_PATH)
    if plan.get("mode") != "dry_run":
        raise ValueError("Plan file must be a dry_run report before applying.")
    if plan.get("total_groups_processed") != EXPECTED_TRUE_GROUPS:
        raise ValueError("Plan file has unexpected number of groups.")
    if plan.get("total_records_to_remove") != EXPECTED_RECORDS_TO_REMOVE:
        raise ValueError("Plan file has unexpected number of records to remove.")

    payloads, per_file_records, merged_records = load_all_records()
    verify_plan_matches_current(plan, merged_records)

    for path in KB_PATHS.values():
        ensure_backup(path)

    try:
        updated_payloads, records_removed_per_file = remove_records_from_payloads(payloads, per_file_records, plan)
        removed_total = sum(records_removed_per_file.values())
        if removed_total != EXPECTED_RECORDS_TO_REMOVE:
            raise ValueError(
                f"Expected to remove {EXPECTED_RECORDS_TO_REMOVE} records, removed {removed_total}."
            )

        for file_name, path in KB_PATHS.items():
            write_payload(path, updated_payloads[file_name])

        validate_json_files()
        new_total = total_kb_records()
        if new_total != EXPECTED_FINAL_RECORD_COUNT:
            raise ValueError(
                f"Expected final KB size {EXPECTED_FINAL_RECORD_COUNT}, found {new_total}."
            )

        unresolved_true_groups = validate_true_duplicates_resolved(true_groups)
        validation_passed = unresolved_true_groups == 0
        if not validation_passed:
            raise ValueError(f"Remaining true duplicate groups after apply: {unresolved_true_groups}.")

        applied = {
            "mode": "applied",
            "total_groups_processed": plan["total_groups_processed"],
            "total_records_to_remove": plan["total_records_to_remove"],
            "summary_by_priority": plan["summary_by_priority"],
            "records_removed_per_file": records_removed_per_file,
            "new_kb_total_records": new_total,
            "validation_passed": validation_passed,
            "remaining_duplicate_groups_true": unresolved_true_groups,
            "plan_report": str(PLAN_PATH.relative_to(ROOT)),
            "decisions": plan["decisions"],
        }
        dump_json(APPLIED_PATH, applied)
        return applied
    except Exception:
        restore_backups()
        raise


def main() -> int:
    args = parse_args()
    if args.apply:
        applied = run_apply()
        print(
            f"Applied true duplicate dedupe: removed {applied['total_records_to_remove']} records, "
            f"new KB size = {applied['new_kb_total_records']}."
        )
        print(f"Report written to {APPLIED_PATH.relative_to(ROOT)}")
        return 0

    plan = run_dry_run()
    print(
        f"Dry-run complete: {plan['total_groups_processed']} groups, "
        f"{plan['total_records_to_remove']} records to remove."
    )
    print(f"Plan written to {PLAN_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
