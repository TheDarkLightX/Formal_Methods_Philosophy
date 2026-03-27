#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_regional_refill_ladder():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "regional refill ladder frontier"
    assert report["viable_behavior_count"] == 130
    assert report["basis"] == [3, 6, 8, 9, 10, 12]
    assert report["best_order"] == [3, 6, 8, 9, 10, 12]
    assert report["best_local_depths"] == {
        "0": 0,
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 2,
        "8": 3,
        "9": 4,
        "10": 1,
        "11": 1,
        "12": 1,
    }
    assert report["weighted_cost"] == 118
    assert report["max_depth"] == 4
    assert report["global_k4_cost"] == 520
    assert report["global_k5_cost"] == 650
    assert report["scorewise_lower_bound"] == 108
    assert report["exact_with_max_depth_3"] is False


if __name__ == "__main__":
    test_regional_refill_ladder()
    print("ok")
