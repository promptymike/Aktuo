"""
Pipeline builder bazy wiedzy Aktuo.
Uruchamia 4 kroki: parse → match → generate → audit

Użycie:
    python run_pipeline.py ustawa.pdf questions.json

Wymaga: ANTHROPIC_API_KEY w env
Wynik: output/verified_units.json + output/verified_units_kb.json
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from env_utils import get_env_value


def run_step(step_name: str, cmd: list[str]) -> bool:
    """Uruchamia krok pipeline'u."""
    print(f"\n{'='*60}")
    print(f"  {step_name}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    if result.returncode != 0:
        print(f"\n❌ {step_name} — FAILED (exit code {result.returncode})")
        return False
    print(f"\n✓ {step_name} — OK")
    return True


def main():
    if len(sys.argv) < 3:
        print("Użycie: python run_pipeline.py <ustawa.pdf> <questions.json>")
        print()
        print("Przykład:")
        print("  export ANTHROPIC_API_KEY='sk-...'")
        print("  python run_pipeline.py ustawa_vat.pdf questions_vat.json")
        sys.exit(1)

    pdf_path = sys.argv[1]
    questions_path = sys.argv[2]

    api_key = get_env_value("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Ustaw ANTHROPIC_API_KEY")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    # Ścieżki outputów
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    articles_path = output_dir / "articles.json"
    matched_path = output_dir / "matched.json"
    draft_path = output_dir / "draft_units.json"
    verified_path = output_dir / "verified_units.json"

    scripts_dir = Path(__file__).parent

    # Krok 1: Parse (nie wymaga API key)
    if not run_step(
        "KROK 1/4: Parsowanie ustawy z PDF",
        [sys.executable, str(scripts_dir / "parse_isap.py"), pdf_path, "--output", str(articles_path)],
    ):
        sys.exit(1)

    # Pokaż statystyki
    data = json.loads(articles_path.read_text())
    print(f"  Artykułów: {data['stats']['active_articles']} aktywnych, {data['stats']['repealed_articles']} uchylonych")

    # Krok 2: Match (wymaga API)
    if not run_step(
        "KROK 2/4: Dopasowanie pytań do artykułów (Claude API)",
        [sys.executable, str(scripts_dir / "match_questions.py"), str(articles_path), questions_path, "--output", str(matched_path)],
    ):
        sys.exit(1)

    # Krok 3: Generate (wymaga API)
    if not run_step(
        "KROK 3/4: Generowanie answer units (Claude API)",
        [sys.executable, str(scripts_dir / "generate_units.py"), str(articles_path), str(matched_path), "--output", str(draft_path)],
    ):
        sys.exit(1)

    # Krok 4: Audit (wymaga API)
    if not run_step(
        "KROK 4/4: Audyt answer units (Claude API)",
        [sys.executable, str(scripts_dir / "audit_units.py"), str(articles_path), str(draft_path), "--output", str(verified_path)],
    ):
        sys.exit(1)

    # Podsumowanie
    result = json.loads(verified_path.read_text())
    meta = result["metadata"]

    print(f"\n{'='*60}")
    print(f"  PIPELINE ZAKOŃCZONY")
    print(f"{'='*60}")
    print(f"  Unitów wygenerowanych: {meta['total_units']}")
    print(f"  ✓ VERIFIED:            {meta['verified']}")
    print(f"  ⚠ NEEDS_FIX:           {meta['needs_fix']}")
    print(f"  ✗ REJECTED:            {meta['rejected']}")
    print(f"  Koszt audytu:          ${meta['total_cost_usd']}")
    print()
    print(f"  Pliki:")
    print(f"    Artykuły:       {articles_path}")
    print(f"    Dopasowania:    {matched_path}")
    print(f"    Draft units:    {draft_path}")
    print(f"    Verified units: {verified_path}")
    print(f"    Czysta KB:      {str(verified_path).replace('.json', '_kb.json')}")
    print()
    print(f"  Następny krok: wgraj verified_units_kb.json do Supabase jako knowledge base")


if __name__ == "__main__":
    main()
