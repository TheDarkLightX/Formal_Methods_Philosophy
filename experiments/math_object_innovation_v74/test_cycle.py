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


def test_v74_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "width4 orbit scalarized mixed-law frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    assert report["orbit_count"] == 19
    assert report["singleton_exact"] == []
    assert report["pair_exact"] == []
    assert report["triple_exact"] == [
        ["count_private_roles", "max_degree", "diameter"],
        ["count_private_roles", "isolated_count", "diameter"],
        ["count_size2_roles", "max_degree", "diameter"],
        ["count_size2_roles", "isolated_count", "diameter"],
    ]
    assert report["chosen_triple"] == [
        "count_private_roles",
        "max_degree",
        "diameter",
    ]
    assert len(report["chosen_triple_map"]) == 19


if __name__ == "__main__":
    test_v74_report()
    print("ok")
