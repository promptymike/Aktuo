"""Verifier v1 (Sonnet vs KB) for batch 2. Thin wrapper over batch 1 module.

The batch 1 verifier already has per-flag resume (skips any flag whose
``verdict`` is already set), so running it after batch 2 self-validation
naturally processes only the batch 2 flags. We only override:
  - REPORT_PATH → ``analysis/batch2_verifier_report.md``
  - COST_HARD_CAP → $5.00 (user spec for batch 2 stage 3)

Run:
    .venv/Scripts/python -u -X utf8 analysis/verify_self_critique_batch2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analysis.verify_self_critique_batch1 as v  # noqa: E402


def main() -> int:
    v.REPORT_PATH = ROOT / "analysis" / "batch2_verifier_report.md"
    v.COST_HARD_CAP = 5.00
    return v.main()


if __name__ == "__main__":
    raise SystemExit(main())
