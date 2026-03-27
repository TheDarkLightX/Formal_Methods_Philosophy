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


def test_bundle_semantic_macro_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "bundle semantic-macro frontier"
    assert report["shared_core_size"] == 17
    assert report["patch_count"] == 5
    assert report["search_count"] == 1419857
    assert report["best_family_count"] == 2
    assert report["best_family_subset"] == ["ADD_BUNDLE", "FLIP_BUNDLE"]
    assert report["best_total_macro_instances"] == 6
    assert report["best_patch_assignments"][0] == {
        "patch": "err[6] and err[9] and not err[10]",
        "core": "err[6]",
        "families": ["ADD_BUNDLE"],
        "ops": [
            {
                "family": "ADD_BUNDLE",
                "literals": [
                    {"feature": "err[10]", "sign": "NEG"},
                    {"feature": "err[9]", "sign": "POS"},
                ],
            }
        ],
    }


if __name__ == "__main__":
    test_bundle_semantic_macro_frontier()
    print("ok")
