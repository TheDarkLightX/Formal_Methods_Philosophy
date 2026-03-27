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


def test_primitive_basis_template_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "primitive basis template frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["primitive_features"] == [
        "add[10]",
        "add[3]",
        "add[6]",
        "add[8]",
        "drop[12]",
    ]
    assert report["all_positive_basis_count"] == 6
    assert report["residual_default_count"] == 18
    assert report["template_count"] == 2
    best = report["best_template"]
    assert best["slot_cost"] == 5
    assert sorted([sorted(best["left"]), sorted(best["right"])]) == [
        ["add[10]", "add[3]", "add[6]"],
        ["add[8]", "drop[12]"],
    ]
    assert best["unused"] == []
    assert report["residual_default_analysis"] == {
        "count": 18,
        "default_labels": [
            "ADD_BUNDLE",
            "ADD_BUNDLE+DROP_BUNDLE",
            "FLIP_BUNDLE",
        ],
        "per_default_pair_count": {
            "ADD_BUNDLE": 6,
            "ADD_BUNDLE+DROP_BUNDLE": 6,
            "FLIP_BUNDLE": 6,
        },
        "same_pair_family_per_default": True,
    }


if __name__ == "__main__":
    test_primitive_basis_template_frontier()
    print("ok")
