#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report() -> dict:
    if not REPORT.exists():
        subprocess.run(["python3", str(ROOT / "run_cycle.py")], check=True)
    return json.loads(REPORT.read_text(encoding="utf-8"))


def main() -> int:
    report = ensure_report()
    assert report["survivor"] == "hard witness-language phase diagram"
    assert report["local_all_positive_failure_scores"] == [9, 10]

    ladder = report["strict_cost_ladder"]
    assert ladder[0]["family"] == "score_local_mixed_witnesses"
    assert ladder[0]["description_cost"] == 27
    assert ladder[1]["family"] == "merged_region_mixed_witnesses"
    assert ladder[1]["description_cost"] == 22
    assert ladder[2]["family"] == "shared_schema_witness_language"
    assert ladder[2]["description_cost"] == 19
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
