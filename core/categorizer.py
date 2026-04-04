from __future__ import annotations


def categorize_query(query: str) -> str:
    lowered = query.lower()
    keyword_map = {
        "housing": ("tenant", "landlord", "lease", "deposit", "rent"),
        "employment": ("employee", "employer", "salary", "wage", "termination"),
        "privacy": ("privacy", "data", "gdpr", "personal data", "consent"),
        "contracts": ("contract", "breach", "clause", "agreement", "invoice"),
    }
    for category, keywords in keyword_map.items():
        if any(keyword in lowered for keyword in keywords):
            return category
    return "general"
