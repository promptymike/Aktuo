"""Retag community_feedback for batch 2 (idempotent, processes all drafts).

The retag logic is deterministic and already re-runs safely on batch 1.
After batch 2 verifier, it covers 10 batch 1 + 32 batch 2 = 42 drafts.
This wrapper just writes the summary to a batch2-named file so batch 1
artifact stays a point-in-time snapshot.

Run:
    .venv/Scripts/python -u -X utf8 analysis/retag_community_feedback_batch2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analysis.retag_community_feedback as r  # noqa: E402


def main() -> int:
    r.REPORT_PATH = ROOT / "analysis" / "batch2_community_feedback_summary.md"
    return r.main()


if __name__ == "__main__":
    raise SystemExit(main())
