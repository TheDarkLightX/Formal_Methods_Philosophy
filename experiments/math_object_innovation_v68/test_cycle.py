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


def test_v68_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "width3 invariant law frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["row_count"] == 6
    assert report["singleton_exact"] == ["degree_sequence"]
    assert report["chosen_pair"] == ["edge_count", "max_degree"]
    assert report["chosen_pair_map"] == [
        {"cost": 6, "features": [0, 0]},
        {"cost": 6, "features": [2, 1]},
        {"cost": 5, "features": [2, 2]},
        {"cost": 4, "features": [3, 2]},
        {"cost": 3, "features": [3, 3]},
        {"cost": 6, "features": [4, 2]},
    ]


if __name__ == "__main__":
    test_v68_report()
    print("ok")
