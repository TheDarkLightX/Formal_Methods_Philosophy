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


def test_v67_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "width3 four-role geometry frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["orbit_count"] == 6
    assert report["cost_histogram"] == [
        {"cost": 3, "count": 192},
        {"cost": 4, "count": 576},
        {"cost": 5, "count": 576},
        {"cost": 6, "count": 336},
    ]
    atlas = {
        tuple(entry["representative"]): (
            entry["orbit_size"],
            entry["edge_count"],
            entry["uniform_cost"],
            entry["labeled_table_count"],
        )
        for entry in report["orbit_atlas"]
    }
    assert atlas == {
        (0, 1, 2, 3): (6, 4, 6, 144),
        (0, 1, 2, 4): (8, 3, 3, 192),
        (0, 1, 2, 5): (24, 3, 4, 576),
        (0, 1, 2, 7): (24, 2, 5, 576),
        (0, 1, 6, 7): (6, 2, 6, 144),
        (0, 3, 5, 6): (2, 0, 6, 48),
    }


if __name__ == "__main__":
    test_v67_report()
    print("ok")
