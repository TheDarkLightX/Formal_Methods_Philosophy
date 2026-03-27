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


def test_role_slot_compiler_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "role-slot compiler frontier"
    assert report["tier"] == "symbolic_state_compiler"
    assert report["target_pair_count"] == 6
    assert report["survivor_count"] == 2
    best = report["best_slot_compiler"]
    assert best["slot_cost"] == 5
    assert sorted([sorted(best["left"]), sorted(best["right"])]) == [
        ["add[10]", "add[3]", "add[6]"],
        ["add[8]", "drop[12]"],
    ]
    assert best["all_positive"] == {
        "cost": 3,
        "language": {
            "ADD_BUNDLE": ["slot_a and not slot_b"],
            "ADD_BUNDLE+DROP_BUNDLE": ["slot_b"],
            "FLIP_BUNDLE": ["not slot_a"],
        },
    }
    assert best["residual_default"] == {
        "cost": 2,
        "default_label": "ADD_BUNDLE",
        "language": {
            "ADD_BUNDLE+DROP_BUNDLE": ["slot_b"],
            "FLIP_BUNDLE": ["not slot_a"],
        },
    }


if __name__ == "__main__":
    test_role_slot_compiler_frontier()
    print("ok")
