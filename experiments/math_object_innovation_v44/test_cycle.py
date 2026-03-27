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


def test_richer_witness_grammar_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "richer witness-grammar frontier"
    assert report["feature_count"] == 8
    assert report["atom_count"] == 1696
    assert report["nontrivial_scores"] == [7, 8, 9, 10, 11, 12]
    assert report["partition_count"] == 203
    assert report["feasible_partition_count"] == 15
    assert report["previous_best_total_cost"] == 23
    assert report["best_total_cost"] == 22
    assert report["best_region_count"] == 5
    assert report["best_partition"] == [[7], [8], [9], [10, 11], [12]]
    score_nine = report["best_region_summaries"][2]
    assert score_nine["scores"] == [9]
    assert score_nine["cost"] == 7
    assert score_nine["default_label"] == "(0, 0, 1, 0)"
    assert (
        "not err[3] and not err[6] and not err[8] and err[10]"
        in score_nine["language"]["(1, 0, 1, 0)"]
    )


if __name__ == "__main__":
    test_richer_witness_grammar_frontier()
    print("ok")
