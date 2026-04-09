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
    text = "Ordynacja Podatkowa okresla zasady postepowania podatkowego."
    result = anonymize_text(text)

    assert "Ordynacja Podatkowa" in result
    assert "[PERSON]" not in result


def test_anonymize_text_still_redacts_person_name() -> None:
    text = "Jan Kowalski zlozyl korekte deklaracji."
    result = anonymize_text(text)

    assert "Jan Kowalski" not in result
    assert "[PERSON]" in result


def test_anonymize_text_redacts_pesel() -> None:
    result = anonymize_text("PESEL klienta to 90010112345.")

    assert "[PESEL]" in result
    assert "90010112345" not in result


def test_anonymize_text_redacts_nip_with_separators() -> None:
    result = anonymize_text("NIP kontrahenta: 123-456-32-18.")

    assert "[NIP]" in result
    assert "123-456-32-18" not in result


def test_anonymize_text_redacts_nip_with_prefix() -> None:
    result = anonymize_text("NIP: 1234563218 powinien byc ukryty.")

    assert "[NIP]" in result
    assert "1234563218" not in result


def test_anonymize_text_redacts_regon_only_with_context() -> None:
    result = anonymize_text("REGON 123456789 nalezy zamaskowac.")

    assert "[REGON]" in result
    assert "123456789" not in result


def test_anonymize_text_does_not_treat_plain_nine_digits_as_regon() -> None:
    result = anonymize_text("Numer referencyjny 123456789 pozostaje bez zmian.")

    assert "[REGON]" not in result
    assert "[PHONE]" not in result
    assert "123456789" in result


def test_anonymize_text_redacts_iban() -> None:
    result = anonymize_text("IBAN klienta: PL61109010140000071219812874.")

    assert "[IBAN]" in result
    assert "PL61109010140000071219812874" not in result


def test_anonymize_text_redacts_account_number() -> None:
    result = anonymize_text("Konto do zwrotu: 12 3456 7890 1234 5678 9012 3456.")

    assert "[KONTO]" in result
    assert "12 3456 7890 1234 5678 9012 3456" not in result
