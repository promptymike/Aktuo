"""Apply confirmed corrections for batch 2. Thin wrapper over batch 1 module.

The batch 1 apply script already has per-flag resume (skips flags whose
``flag_description`` already appears in ``corrections_applied``), so
running it after batch 2 verifier naturally processes only batch 2
confirmed flags. Overrides:
  - REPORT_PATH → ``analysis/batch2_corrections_log.md``
  - COST_HARD_CAP → $3.00 (user spec for batch 2 stage 5)

Run:
    .venv/Scripts/python -u -X utf8 analysis/apply_confirmed_corrections_batch2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analysis.apply_confirmed_corrections as a  # noqa: E402


def main() -> int:
    a.REPORT_PATH = ROOT / "analysis" / "batch2_corrections_log.md"
    a.COST_HARD_CAP = 3.00
    return a.main()


if __name__ == "__main__":
    raise SystemExit(main())
