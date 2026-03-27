#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report() -> None:
    if REPORT.exists():
        return
    subprocess.run([sys.executable, str(ROOT / "run_cycle.py")], cwd=ROOT, check=True)


def test_five_literal_witness_grammar_boundary_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "five-literal witness-grammar boundary frontier"
    assert report["feature_count"] == 8
    assert report["partition_count"] == 203
    assert report["atom_count_4"] == 1696
    assert report["atom_count_5"] == 3488
    assert report["feasible_partition_count_4"] == 15
    assert report["feasible_partition_count_5"] == 15
    assert report["same_feasible_partition_set"] is True
    assert report["best_total_cost_4"] == 22
    assert report["best_total_cost_5"] == 22
    assert report["best_region_count_4"] == 5
    assert report["best_region_count_5"] == 5
    assert report["best_partition_4"] == [[7], [8], [9], [10, 11], [12]]
    assert report["best_partition_5"] == [[7], [8], [9], [10, 11], [12]]
    assert report["secondary_partition_improvement_count"] == 2
    assert report["secondary_partition_improvements"][0] == {
        "partition": [[7], [8], [9, 10, 12], [11]],
        "cost_4": 24,
        "cost_5": 23,
    }


if __name__ == "__main__":
    test_five_literal_witness_grammar_boundary_frontier()
    print("ok")
