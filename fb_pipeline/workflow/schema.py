"""Pure-Python validator for Aktuo workflow draft JSON (Zadanie 3).

Returns ``(True, None)`` on success and ``(False, reason)`` otherwise.
Covers only the structural contract — merit review is Paweł's job.
"""

from __future__ import annotations

from typing import Any

REQUIRED_FIELDS: tuple[str, ...] = (
    "id",
    "title",
    "topic_area",
    "question_examples",
    "answer_steps",
    "legal_anchors",
    "edge_cases",
    "common_mistakes",
    "related_questions",
    "last_verified_at",
    "draft",
    "requires_manual_legal_anchor",
    "generation_metadata",
)

STEP_FIELDS: tuple[str, ...] = ("step", "action", "detail")
ANCHOR_FIELDS: tuple[str, ...] = ("law_name", "article_number", "reason")
METADATA_FIELDS: tuple[str, ...] = (
    "model",
    "cluster_id",
    "cluster_label",
    "generated_at",
    "source_post_ids",
)


def validate_draft(record: Any) -> tuple[bool, str | None]:
    if not isinstance(record, dict):
        return False, f"root must be object, got {type(record).__name__}"

    for field in REQUIRED_FIELDS:
        if field not in record:
            return False, f"missing required field: {field}"

    # Simple type checks.
    if not isinstance(record["id"], str) or not record["id"]:
        return False, "id must be non-empty string"
    if not isinstance(record["title"], str) or not record["title"]:
        return False, "title must be non-empty string"
    if not isinstance(record["topic_area"], str) or not record["topic_area"]:
        return False, "topic_area must be non-empty string"

    qe = record["question_examples"]
    if not isinstance(qe, list) or len(qe) < 3:
        return False, "question_examples must be list of >=3 strings"
    if not all(isinstance(q, str) and q.strip() for q in qe):
        return False, "question_examples entries must be non-empty strings"

    steps = record["answer_steps"]
    if not isinstance(steps, list) or not (3 <= len(steps) <= 10):
        return False, "answer_steps must be list of 3-10 items"
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            return False, f"answer_steps[{i}] must be object"
        for key in STEP_FIELDS:
            if key not in step:
                return False, f"answer_steps[{i}] missing key: {key}"
        if not isinstance(step["step"], int):
            return False, f"answer_steps[{i}].step must be int"
        if not isinstance(step["action"], str) or not step["action"].strip():
            return False, f"answer_steps[{i}].action must be non-empty string"
        if not isinstance(step["detail"], str):
            return False, f"answer_steps[{i}].detail must be string"
        # condition optional, may be null or str
        cond = step.get("condition")
        if cond is not None and not isinstance(cond, str):
            return False, f"answer_steps[{i}].condition must be string or null"

    anchors = record["legal_anchors"]
    if not isinstance(anchors, list):
        return False, "legal_anchors must be list"
    if len(anchors) > 5:
        return False, "legal_anchors: at most 5"
    for i, a in enumerate(anchors):
        if not isinstance(a, dict):
            return False, f"legal_anchors[{i}] must be object"
        for key in ANCHOR_FIELDS:
            if key not in a:
                return False, f"legal_anchors[{i}] missing key: {key}"
            if not isinstance(a[key], str) or not a[key].strip():
                return False, f"legal_anchors[{i}].{key} must be non-empty string"

    for field in ("edge_cases", "common_mistakes", "related_questions"):
        value = record[field]
        if not isinstance(value, list):
            return False, f"{field} must be list"
        if not all(isinstance(x, str) and x.strip() for x in value):
            return False, f"{field} entries must be non-empty strings"

    if not isinstance(record["last_verified_at"], str) or len(record["last_verified_at"]) < 10:
        return False, "last_verified_at must be ISO date string"
    if not isinstance(record["draft"], bool):
        return False, "draft must be bool"
    if not isinstance(record["requires_manual_legal_anchor"], bool):
        return False, "requires_manual_legal_anchor must be bool"

    meta = record["generation_metadata"]
    if not isinstance(meta, dict):
        return False, "generation_metadata must be object"
    for key in METADATA_FIELDS:
        if key not in meta:
            return False, f"generation_metadata missing key: {key}"
    if not isinstance(meta["source_post_ids"], list):
        return False, "generation_metadata.source_post_ids must be list"

    # Consistency: if requires_manual_legal_anchor is False, we expect >=1 anchor.
    if not record["requires_manual_legal_anchor"] and len(anchors) == 0:
        return False, "requires_manual_legal_anchor=false but legal_anchors is empty"

    return True, None
