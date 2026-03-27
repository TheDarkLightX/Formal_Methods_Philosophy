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


def test_anchored_third_shortcut_boundary_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "anchored third-shortcut boundary frontier"
    assert report["viable_behavior_count"] == 130
    assert report["fixed_primitives"] == [
        "err[6] AND err[10] AND err[12]",
        "err[9] AND err[10] AND err[12]",
    ]
    assert report["baseline_weighted_cost"] == 80
    assert report["baseline_max_depth"] == 2
    assert report["baseline_bucket_total"] == 51
    assert report["searched_candidate_count"] == 612
    assert report["best_weighted_cost"] == 80
    assert report["best_max_depth"] == 2
    assert report["best_bucket_total"] == 48
    assert report["best_extra_primitive"] == "err[3] OR err[6] OR err[8]"
    assert report["best_insert_position"] == 6
    assert report["best_local_depths"] == {
        "0": 0,
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
        "7": 2,
        "8": 2,
        "9": 2,
        "10": 1,
        "11": 1,
        "12": 1,
    }
    assert report["exact_with_max_depth_1"] is False


if __name__ == "__main__":
    test_anchored_third_shortcut_boundary_frontier()
    print("ok")
