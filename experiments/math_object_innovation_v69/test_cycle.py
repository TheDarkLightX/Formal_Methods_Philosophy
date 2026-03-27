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


def test_v69_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "width4 support-profile frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["cost_histogram"] == [
        {"cost": 3, "count": 8832},
        {"cost": 4, "count": 18432},
        {"cost": 5, "count": 13056},
        {"cost": 6, "count": 3360},
    ]
    assert [
        {
            "profile": row["profile"],
            "count": row["count"],
            "cost": row["cost"],
        }
        for row in report["profile_histogram"]
    ] == [
        {"profile": [1, 1, 1, 1], "count": 384, "cost": 3},
        {"profile": [1, 1, 1, 2], "count": 4608, "cost": 3},
        {"profile": [1, 1, 1, 3], "count": 3840, "cost": 3},
        {"profile": [1, 1, 2, 2], "count": 18432, "cost": 4},
        {"profile": [1, 2, 2, 2], "count": 13056, "cost": 5},
        {"profile": [2, 2, 2, 2], "count": 3360, "cost": 6},
    ]


if __name__ == "__main__":
    test_v69_report()
    print("ok")
