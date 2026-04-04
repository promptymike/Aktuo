# Aktuo MVP

Minimal stateless legal-assistant scaffold built with Python 3.11+ and Streamlit.

## Structure

- `app/` Streamlit UI
- `core/` Stateless RAG pipeline
- `data/` Seed knowledge and prompts
- `db/migrations/` SQL schema
- `config/` Environment-driven settings
- `tests/` Minimal pytest coverage

## Requirements

- Python 3.11+
- Environment variables only
- No hardcoded secrets

## Quick start

PowerShell example:

```powershell
$env:AKTUO_APP_NAME="Aktuo MVP"
$env:AKTUO_SYSTEM_PROMPT="You are Aktuo, a cautious legal information assistant."
$env:AKTUO_LAW_KNOWLEDGE_PATH="data/seeds/law_knowledge.json"
$env:ANTHROPIC_API_KEY="your_anthropic_api_key"
py -3.11 -m pip install -r requirements.txt
py -3.11 -m streamlit run app/main.py
```

Run tests:

```powershell
py -3.11 -m pytest -q
```

## Notes

- The backend logic is stateless and pure-function oriented.
- The SQL migration creates exactly two tables: `law_chunks` and `conversations`.
- If required environment variables are missing, the Streamlit app shows a friendly setup message.
