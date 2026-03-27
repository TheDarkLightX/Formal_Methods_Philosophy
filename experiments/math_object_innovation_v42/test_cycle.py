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


def test_score_abstraction_witness_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "score-abstraction witness frontier"
    assert report["feature_count"] == 8
    assert report["atom_count"] == 576
    assert report["nontrivial_scores"] == [7, 8, 9, 10, 11, 12]
    assert report["feasible_partition_count"] == 2
    assert report["best_total_cost"] == 23
    assert report["best_region_count"] == 5
    assert report["best_partition"] == [[7], [8], [9], [10, 11], [12]]
    merged = report["best_region_summaries"][3]
    assert merged["scores"] == [10, 11]
    assert merged["cost"] == 5
    assert merged["default_label"] == "(1, 0, 1, 1)"
    assert "(1, 1, 0, 0)" in merged["language"]


if __name__ == "__main__":
    test_score_abstraction_witness_frontier()
    print("ok")
