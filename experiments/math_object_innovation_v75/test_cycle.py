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


def test_v75_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "width4 broad-scalar minimality frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["orbit_count"] == 19
    assert report["scalar_feature_count"] == 21
    assert report["singleton_exact"] == []
    assert report["pair_exact"] == []
    assert report["triple_exact_count"] == 38
    assert report["chosen_triple"] == [
        "count_private_roles",
        "max_degree",
        "diameter",
    ]
    assert len(report["chosen_triple_map"]) == 19


if __name__ == "__main__":
    test_v75_report()
    print("ok")
