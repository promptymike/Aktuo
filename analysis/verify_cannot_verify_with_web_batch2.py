"""Verifier v2 (Sonnet + web) for batch 2. Thin wrapper over batch 1 module.

The batch 1 v2 verifier already has per-flag resume (skips flags with
``verdict_v2`` already set and processes ``cannot_verify`` ones sorted by
severity). Running it after batch 2 v1 naturally targets only batch 2
cannot_verify flags. Overrides:
  - REPORT_PATH → ``analysis/batch2_verifier_v2_report.md``
  - COST_HARD_CAP → $5.00

Run:
    .venv/Scripts/python -u -X utf8 analysis/verify_cannot_verify_with_web_batch2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analysis.verify_cannot_verify_with_web as v2  # noqa: E402


def main() -> int:
    v2.REPORT_PATH = ROOT / "analysis" / "batch2_verifier_v2_report.md"
    v2.COST_HARD_CAP = 5.00
    return v2.main()


if __name__ == "__main__":
    raise SystemExit(main())
