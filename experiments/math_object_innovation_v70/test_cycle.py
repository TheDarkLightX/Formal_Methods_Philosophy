#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report():
    if REPORT.exists():
        return
    subprocess.run([sys.executable, str(ROOT / "run_cycle.py")], check=True)


def test_v70_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "width4 support-count law frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["row_count"] == 6
    assert report["singleton_exact"] == [
        "count_private_roles",
        "count_size2_roles",
        "sum_three_smallest",
    ]
    assert report["chosen_scalar"] == ["count_private_roles"]
    assert report["chosen_scalar_map"] == [
        {"features": [0], "cost": 6},
        {"features": [1], "cost": 5},
        {"features": [2], "cost": 4},
        {"features": [3], "cost": 3},
        {"features": [4], "cost": 3},
    ]


if __name__ == "__main__":
    test_v70_report()
    print("ok")
