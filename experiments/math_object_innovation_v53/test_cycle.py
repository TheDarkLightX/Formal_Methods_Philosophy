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


def test_semantic_fiber_decomposition_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "semantic fiber decomposition frontier"
    assert report["patch_count"] == 5
    assert report["partition_count"] == 52
    assert report["best_score"] == {
        "mixed_patch_count": 1,
        "mixed_fiber_count": 1,
        "fiber_count": 3,
        "total_family_count": 4,
        "total_ops": 6,
    }
    assert report["best_fibers"][0]["family_subset"] == ["FLIP_BUNDLE"]
    assert len(report["best_fibers"][0]["patches"]) == 3
    assert report["best_fibers"][1]["family_subset"] == ["ADD_BUNDLE"]
    assert len(report["best_fibers"][1]["patches"]) == 1
    assert report["best_fibers"][2]["family_subset"] == ["ADD_BUNDLE", "DROP_BUNDLE"]
    assert len(report["best_fibers"][2]["patches"]) == 1


if __name__ == "__main__":
    test_semantic_fiber_decomposition_frontier()
    print("ok")
