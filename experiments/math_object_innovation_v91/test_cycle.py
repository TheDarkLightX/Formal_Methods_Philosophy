#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report() -> dict:
    if not REPORT.exists():
        subprocess.run(["python3", str(ROOT / "run_cycle.py")], check=True)
    return json.loads(REPORT.read_text(encoding="utf-8"))


def main() -> int:
    report = ensure_report()
    assert report["survivor"] == "refill maximal score-free merged-subunion boundary"
    assert report["nontrivial_scores"] == [7, 8, 9, 10, 11, 12]
    assert report["atom_count"] == 1696
    assert report["feasible_subset_count"] == 13
    assert report["feasible_subset_count_by_size"] == {"1": 6, "2": 6, "3": 1}
    assert report["all_positive_feasible_subset_count"] == 10
    assert report["all_positive_feasible_subset_count_by_size"] == {"1": 6, "2": 4}
    assert report["maximal_subset_size"] == 3
    assert report["maximal_subset_count"] == 1
    best = report["best_maximal_subset"]
    assert best["scores"] == [9, 10, 12]
    assert best["row_count"] == 17
    assert best["label_count"] == 10
    assert best["all_positive_possible"] is False
    assert best["residual_possible"] is True
    assert best["residual_cost"] == 10
    assert best["default_label"] == "(1, 0, 1, 1)"
    top = report["top_feasible_subsets"][:4]
    assert [entry["scores"] for entry in top] == [[9, 10, 12], [10, 12], [10, 11], [7, 12]]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
