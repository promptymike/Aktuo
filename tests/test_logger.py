from __future__ import annotations

import hashlib
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
        question="Jan Kowalski pyta: Od kiedy KSeF jest obowiązkowy?",
        redacted_query="Jan Kowalski pyta: Od kiedy KSeF jest obowiązkowy?",
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
    assert entry["user_email"] == hashlib.sha256(b"beta@aktuo.pl").hexdigest()[:8]
    assert entry["category"] == "ksef"
    assert entry["chunks_returned"] == 2
    assert entry["grounded"] is True
    assert entry["question"] == "[PERSON] pyta: Od kiedy KSeF jest obowiązkowy?"
    assert entry["redacted_query"] == "[PERSON] pyta: Od kiedy KSeF jest obowiązkowy?"
    assert "beta@aktuo.pl" not in lines[0]
    assert "Jan Kowalski" not in lines[0]


def test_log_query_includes_optional_no_match_reason(tmp_path, monkeypatch) -> None:
    log_path = tmp_path / "queries.jsonl"
    monkeypatch.setattr(logger, "LOG_PATH", log_path)
    monkeypatch.setattr(logger, "Thread", ImmediateThread)

    logger.log_query(
        session_id="session-124",
        user_email="beta@aktuo.pl",
        question="Jak rozliczyć cło importowe?",
        redacted_query="Jak rozliczyć cło importowe?",
        category="ogólne",
        chunks_returned=5,
        chunk_ids=["Ustawa o VAT art. 1"],
        answer_length=180,
        grounded=False,
        no_match_reason="low_bm25_score",
    )

    entry = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
    assert entry["no_match_reason"] == "low_bm25_score"


def test_log_feedback_appends_jsonl_entry(tmp_path, monkeypatch) -> None:
    feedback_path = tmp_path / "feedback.jsonl"
    monkeypatch.setattr(logger, "FEEDBACK_PATH", feedback_path)
    monkeypatch.setattr(logger, "Thread", ImmediateThread)

    logger.log_feedback(
        session_id="session-123",
        user_email="beta@aktuo.pl",
        query="Jan Kowalski może skorygować JPK_V7?",
        rating="down",
        comment="Jan Kowalski dostał za mało konkretów o korekcie.",
    )

    lines = feedback_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["session_id"] == "session-123"
    assert entry["user_email"] == hashlib.sha256(b"beta@aktuo.pl").hexdigest()[:8]
    assert entry["query"] == "[PERSON] może skorygować JPK_V7?"
    assert entry["rating"] == "down"
    assert entry["comment"] == "[PERSON] dostał za mało konkretów o korekcie."
    assert "beta@aktuo.pl" not in lines[0]
    assert "Jan Kowalski" not in lines[0]
