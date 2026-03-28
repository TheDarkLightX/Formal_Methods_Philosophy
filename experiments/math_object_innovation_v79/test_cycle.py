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
    assert report["survivor"] == "hard decomposition-language boundary"
    assert report["bit_fiber_total_cost"] == 24
    assert report["label_level_total_cost"] == 22
    assert report["bit_fiber_shared_schema_count"] == 21
    assert report["label_level_shared_schema_count"] == 19
    scores_to_cost = {
        tuple(region["scores"]): region["bit_total_cost"]
        for region in report["region_reports"]
    }
    assert scores_to_cost[(7,)] == 4
    assert scores_to_cost[(8,)] == 5
    assert scores_to_cost[(9,)] == 7
    assert scores_to_cost[(10, 11)] == 6
    assert scores_to_cost[(12,)] == 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
