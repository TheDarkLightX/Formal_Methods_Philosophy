#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report() -> None:
    if REPORT.exists():
        return
    subprocess.run([sys.executable, str(ROOT / "run_cycle.py")], cwd=ROOT, check=True)


def test_global_witness_synthesis_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "global witness-synthesis frontier"
    assert report["feature_count"] == 8
    assert report["atom_count"] == 1696
    assert report["best_partition"] == [[7], [8], [9], [10, 11], [12]]
    assert report["total_region_cost"] == 22
    assert report["best_shared_schema_count"] == 19
    assert report["region_best_costs"] == {
        "7": 4,
        "8": 5,
        "9": 7,
        "10,11": 5,
        "12": 1,
    }
    assert report["choice_count_by_region"] == {
        "7": 5,
        "8": 13,
        "9": 1,
        "10,11": 1,
        "12": 2,
    }
    assert "not err[3] and not err[6] and not err[8] and err[10]" in report["best_shared_schemas"]


if __name__ == "__main__":
    test_global_witness_synthesis_frontier()
    print("ok")
