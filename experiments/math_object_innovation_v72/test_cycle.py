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


def test_v72_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "width4 orbit support-count transfer frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["orbit_count"] == 19
    assert report["cost_singleton_exact"] == [
        "count_private_roles",
        "count_size2_roles",
    ]
    assert report["profile_singleton_exact"] == []
    assert report["chosen_cost_scalar"] == ["count_private_roles"]
    assert report["chosen_cost_map"] == [
        {"features": [0], "cost": 6},
        {"features": [1], "cost": 5},
        {"features": [2], "cost": 4},
        {"features": [3], "cost": 3},
        {"features": [4], "cost": 3},
    ]
    assert report["chosen_profile_pair"] == [
        "count_private_roles",
        "max_support_size",
    ]
    assert report["chosen_profile_map"] == [
        {"features": [0, 2], "profile": [2, 2, 2, 2]},
        {"features": [1, 2], "profile": [1, 2, 2, 2]},
        {"features": [2, 2], "profile": [1, 1, 2, 2]},
        {"features": [3, 2], "profile": [1, 1, 1, 2]},
        {"features": [3, 3], "profile": [1, 1, 1, 3]},
        {"features": [4, 1], "profile": [1, 1, 1, 1]},
    ]


if __name__ == "__main__":
    test_v72_report()
    print("ok")
