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


def test_refill_two_concept_ladder_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "refill two-concept ladder frontier"
    assert report["viable_behavior_count"] == 130
    assert report["basis"] == [3, 6, 8, 9, 10, 12]
    assert report["baseline_weighted_cost"] == 118
    assert report["baseline_max_depth"] == 4
    assert report["searched_candidate_count"] == 135240
    assert report["best_weighted_cost"] == 80
    assert report["best_max_depth"] == 2
    assert [item["name"] for item in report["best_primitives"]] == [
        "err[6] AND err[10] AND err[12]",
        "err[9] AND err[10] AND err[12]",
    ]
    assert report["best_local_depths"] == {
        "0": 0,
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 2,
        "8": 2,
        "9": 2,
        "10": 1,
        "11": 1,
        "12": 1,
    }
    assert report["exact_with_max_depth_1"] is False


if __name__ == "__main__":
    test_refill_two_concept_ladder_frontier()
    print("ok")
