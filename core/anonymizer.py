from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
IBAN_PATTERN = re.compile(r"\b[A-Z]{2}\d{2}(?:\s?\d{4}){6}\b")
ACCOUNT_PATTERN = re.compile(r"\b\d{2}(?:\s?\d{4}){6}\b")
NIP_PREFIX_PATTERN = re.compile(r"\bNIP\s*:?\s*\d{10}\b", re.IGNORECASE)
NIP_PATTERN = re.compile(r"\b\d{3}[-\u2010]?\d{3}[-\u2010]?\d{2}[-\u2010]?\d{2}\b")
REGON_PATTERN = re.compile(r"\bREGON\s*:?\s*(?:\d{9}|\d{14})\b", re.IGNORECASE)
PESEL_PATTERN = re.compile(r"\b\d{11}\b")
PHONE_PATTERN = re.compile(
    r"(?:\b(?:\+|00)\d{1,3}[\s-]?(?:\d[\s-]?){7,}\d\b)|(?:\b\d{3}[\s-]\d{3}[\s-]\d{3}\b)"
)
PERSON_PATTERN = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")
PERSON_WHITELIST = {
    "Ordynacja Podatkowa",
    "Kodeks Karny",
    "Kodeks Skarbowy",
    "Ustawa VAT",
    "Naczelny S\u0105d",
    "S\u0105d Administracyjny",
    "Krajowy System",
    "Izba Skarbowa",
    "Urz\u0105d Skarbowy",
    "Dyrektor Krajowy",
    "Minister Finans\u00f3w",
    "Trybuna\u0142 Konstytucyjny",
}


def _replace_person(match: re.Match[str]) -> str:
    phrase = match.group(0)
    if phrase in PERSON_WHITELIST:
        return phrase
    return "[PERSON]"


def anonymize_text(text: str) -> str:
    text = EMAIL_PATTERN.sub("[EMAIL]", text)
    text = IBAN_PATTERN.sub("[IBAN]", text)
    text = ACCOUNT_PATTERN.sub("[KONTO]", text)
    text = NIP_PREFIX_PATTERN.sub("[NIP]", text)
    text = NIP_PATTERN.sub("[NIP]", text)
    text = REGON_PATTERN.sub("[REGON]", text)
    text = PESEL_PATTERN.sub("[PESEL]", text)
    text = PHONE_PATTERN.sub("[PHONE]", text)
    text = PERSON_PATTERN.sub(_replace_person, text)
    return text
