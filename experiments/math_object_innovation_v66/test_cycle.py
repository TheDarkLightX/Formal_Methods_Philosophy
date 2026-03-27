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


def test_v66_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "four-role support cost frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["width2"]["table_count"] == 24
    assert report["width2"]["single_literal_star_count"] == 0
    assert report["width2"]["minimal_total_literal_cost_histogram"] == [
        {"cost": 6, "count": 24}
    ]
    assert report["width3"]["table_count"] == 1680
    assert report["width3"]["single_literal_star_count"] == 192
    assert report["width3"]["minimal_total_literal_cost_histogram"] == [
        {"cost": 3, "count": 192},
        {"cost": 4, "count": 576},
        {"cost": 5, "count": 576},
        {"cost": 6, "count": 336},
    ]


if __name__ == "__main__":
    test_v66_report()
    print("ok")
