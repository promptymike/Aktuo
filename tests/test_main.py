from __future__ import annotations

from app.main import is_valid_email, normalize_email


def test_normalize_email_lowercases_and_strips() -> None:
    assert normalize_email("  Jan.Kowalski@Firma.PL  ") == "jan.kowalski@firma.pl"


def test_is_valid_email_accepts_well_formed_address() -> None:
    assert is_valid_email("jan.kowalski+beta@firma.pl") is True


def test_is_valid_email_rejects_missing_domain_suffix() -> None:
    assert is_valid_email("admin@") is False


def test_is_valid_email_rejects_short_or_script_like_values() -> None:
    assert is_valid_email("x@x") is False
    assert is_valid_email('"><script>alert(1)</script>@x.com') is False
