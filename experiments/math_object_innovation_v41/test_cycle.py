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


def test_global_witness_schema_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "global witness-schema frontier"
    assert report["feature_count"] == 8
    assert report["atom_count"] == 576
    assert report["nontrivial_scores"] == [7, 8, 9, 10, 11, 12]
    assert report["total_mixed_cost"] == 27
    assert report["best_shared_schema_count"] == 20
    assert report["score_best_costs"] == {
        "7": 4,
        "8": 5,
        "9": 8,
        "10": 4,
        "11": 5,
        "12": 1,
    }
    assert report["choice_count_by_score"] == {
        "7": 5,
        "8": 13,
        "9": 1,
        "10": 1,
        "11": 6,
        "12": 2,
    }
    assert report["best_score_choices"]["8"]["default_label"] == "(0, 0, 1, 0)"
    assert "err[3] and err[8]" in report["best_shared_schemas"]


if __name__ == "__main__":
    test_global_witness_schema_frontier()
    print("ok")
