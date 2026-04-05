from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?:(?:\+|00)\d{1,3}[\s-]?)?(?:\d[\s-]?){7,}\d")
PERSON_PATTERN = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")
PERSON_WHITELIST = {
    "Ordynacja Podatkowa",
    "Kodeks Karny",
    "Kodeks Skarbowy",
    "Ustawa VAT",
    "Naczelny Sąd",
    "Sąd Administracyjny",
    "Krajowy System",
    "Izba Skarbowa",
    "Urząd Skarbowy",
    "Dyrektor Krajowy",
    "Minister Finansów",
    "Trybunał Konstytucyjny",
}


def _replace_person(match: re.Match[str]) -> str:
    phrase = match.group(0)
    if phrase in PERSON_WHITELIST:
        return phrase
    return "[PERSON]"


def anonymize_text(text: str) -> str:
    text = EMAIL_PATTERN.sub("[EMAIL]", text)
    text = PHONE_PATTERN.sub("[PHONE]", text)
    text = PERSON_PATTERN.sub(_replace_person, text)
    return text
