from __future__ import annotations

from core.anonymizer import anonymize_text


def test_anonymize_text_redacts_name_email_and_phone() -> None:
    text = "Jan Kowalski sent an email to jan@example.com and called +48 555 444 333."
    result = anonymize_text(text)

    assert "[PERSON]" in result
    assert "[EMAIL]" in result
    assert "[PHONE]" in result
    assert "jan@example.com" not in result


def test_anonymize_text_keeps_legal_whitelist_term() -> None:
    text = "Ordynacja Podatkowa określa zasady postępowania podatkowego."
    result = anonymize_text(text)

    assert "Ordynacja Podatkowa" in result
    assert "[PERSON]" not in result


def test_anonymize_text_still_redacts_person_name() -> None:
    text = "Jan Kowalski złożył korektę deklaracji."
    result = anonymize_text(text)

    assert "Jan Kowalski" not in result
    assert "[PERSON]" in result
