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


def test_direct_delta_basis_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "direct delta basis frontier"
    assert report["tier"] == "symbolic_state_compiler"
    assert report["all_features"] == ["has_add", "has_drop", "has_flip"]
    assert report["row_count"] == 5
    assert report["all_positive"]["basis_size"] == 2
    assert report["residual_default"]["basis_size"] == 2
    assert report["all_positive"]["exact_bases"] == [
        {
            "atom_count": 8,
            "features": ["has_add", "has_drop"],
            "language": {
                "cost": 3,
                "language": {
                    "ADD_BUNDLE": ["has_add and not has_drop"],
                    "ADD_BUNDLE+DROP_BUNDLE": ["has_drop"],
                    "FLIP_BUNDLE": ["not has_add"],
                },
            },
        },
        {
            "atom_count": 8,
            "features": ["has_drop", "has_flip"],
            "language": {
                "cost": 3,
                "language": {
                    "ADD_BUNDLE": ["not has_drop and not has_flip"],
                    "ADD_BUNDLE+DROP_BUNDLE": ["has_drop"],
                    "FLIP_BUNDLE": ["has_flip"],
                },
            },
        }
    ]
    assert report["residual_default"]["exact_bases"] == [
        {
            "atom_count": 8,
            "features": ["has_add", "has_drop"],
            "language": {
                "cost": 2,
                "default_label": "ADD_BUNDLE",
                "language": {
                    "ADD_BUNDLE+DROP_BUNDLE": ["has_drop"],
                    "FLIP_BUNDLE": ["not has_add"],
                },
            },
        },
        {
            "atom_count": 8,
            "features": ["has_drop", "has_flip"],
            "language": {
                "cost": 2,
                "default_label": "ADD_BUNDLE",
                "language": {
                    "ADD_BUNDLE+DROP_BUNDLE": ["has_drop"],
                    "FLIP_BUNDLE": ["has_flip"],
                },
            },
        }
    ]


if __name__ == "__main__":
    test_direct_delta_basis_frontier()
    print("ok")
