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


def test_score_local_mixed_sign_witness_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "score-local mixed-sign witness frontier"
    assert report["feature_count"] == 8
    assert report["atom_count"] == 576
    assert report["nontrivial_score_count"] == 6
    assert report["nontrivial_scores"] == [7, 8, 9, 10, 11, 12]
    assert report["total_mixed_cost"] == 27
    assert report["all_positive_failure_scores"] == [9, 10]
    assert report["score_summaries"]["7"]["best_default_label"] == "(0, 0, 0, 0)"
    assert report["score_summaries"]["7"]["best_mixed_cost"] == 4
    assert report["score_summaries"]["9"]["best_default_label"] == "(1, 0, 1, 0)"
    assert report["score_summaries"]["9"]["best_mixed_cost"] == 8
    assert report["score_summaries"]["10"]["all_positive_possible"] is False
    assert report["score_summaries"]["10"]["best_default_label"] == "(1, 0, 1, 1)"
    assert report["score_summaries"]["12"]["best_mixed_cost"] == 1


if __name__ == "__main__":
    test_score_local_mixed_sign_witness_frontier()
    print("ok")
