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


def test_v76_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "width4 mixed-basis uniqueness frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["orbit_count"] == 19
    assert report["mixed_feature_count"] == 8
    assert report["pair_exact"] == [
        ["count_private_roles", "distance_multiset"],
        ["count_size2_roles", "distance_multiset"],
        ["profile", "distance_multiset"],
    ]
    assert report["nontrivial_pair_exact"] == [
        ["count_private_roles", "distance_multiset"],
        ["count_size2_roles", "distance_multiset"],
    ]


if __name__ == "__main__":
    test_v76_report()
    print("ok")
