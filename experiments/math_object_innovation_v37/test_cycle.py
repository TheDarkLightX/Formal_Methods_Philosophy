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


def test_refill_concept_market_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "refill concept-market frontier"
    assert report["viable_behavior_count"] == 130
    assert report["basis"] == [3, 6, 8, 9, 10, 12]
    assert report["baseline_weighted_cost"] == 118
    assert report["baseline_max_depth"] == 4
    assert report["fixed_order_insertion_search"]["searched_candidate_count"] == 490
    assert report["fixed_order_insertion_search"]["best_weighted_cost"] == 90
    assert report["fixed_order_insertion_search"]["best_max_depth"] == 3
    assert report["fixed_order_insertion_search"]["best_primitive"] == "err[10] AND err[12]"
    assert report["fixed_order_insertion_search"]["best_insert_position"] == 4
    assert report["fixed_order_insertion_search"]["best_local_depths"] == {
        "0": 0,
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 2,
        "8": 2,
        "9": 3,
        "10": 1,
        "11": 1,
        "12": 1,
    }
    assert report["fixed_order_insertion_search"]["exact_with_max_depth_2"] is False
    assert report["replacement_search"]["searched_language_count"] == 70
    assert report["replacement_search"]["searched_order_count"] == 4560
    assert report["replacement_search"]["exact_count"] == 0
    assert report["replacement_search"]["best_exact"] is None


if __name__ == "__main__":
    test_refill_concept_market_frontier()
    print("ok")
