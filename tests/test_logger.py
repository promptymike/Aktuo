from __future__ import annotations

import json

import core.logger as logger


class ImmediateThread:
    def __init__(self, *, target, args=(), daemon=None):
        self._target = target
        self._args = args

    def start(self) -> None:
        self._target(*self._args)


def test_log_query_appends_jsonl_entry(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "queries.jsonl"
    monkeypatch.setattr(logger, "LOG_PATH", log_path)
    monkeypatch.setattr(logger, "Thread", ImmediateThread)

    logger.log_query(
        session_id="session-123",
        user_email="beta@aktuo.pl",
        question="Od kiedy KSeF jest obowiązkowy?",
        redacted_query="Od kiedy KSeF jest obowiązkowy?",
        category="ksef",
        chunks_returned=2,
        chunk_ids=["Ustawa o VAT art. 106ga", "Ustawa o VAT art. 145l"],
        answer_length=120,
        grounded=True,
    )

    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["session_id"] == "session-123"
    assert entry["user_email"] == "beta@aktuo.pl"
    assert entry["category"] == "ksef"
    assert entry["chunks_returned"] == 2
    assert entry["grounded"] is True


def test_log_feedback_appends_jsonl_entry(tmp_path, monkeypatch) -> None:
    feedback_path = tmp_path / "feedback.jsonl"
    monkeypatch.setattr(logger, "FEEDBACK_PATH", feedback_path)
    monkeypatch.setattr(logger, "Thread", ImmediateThread)

    logger.log_feedback(
        session_id="session-123",
        user_email="beta@aktuo.pl",
        query="Czy mogę skorygować JPK_V7?",
        rating="down",
        comment="Za mało konkretów o korekcie.",
    )

    lines = feedback_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["session_id"] == "session-123"
    assert entry["user_email"] == "beta@aktuo.pl"
    assert entry["query"] == "Czy mogę skorygować JPK_V7?"
    assert entry["rating"] == "down"
    assert entry["comment"] == "Za mało konkretów o korekcie."
