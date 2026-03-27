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


def test_semantic_macro_family_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "semantic macro-family frontier"
    assert report["shared_core_size"] == 17
    assert report["patch_count"] == 5
    assert report["search_count"] == 1419857
    assert report["best_family_count"] == 2
    assert report["best_family_subset"] == ["ADD_LITERAL", "FLIP_SIGN"]
    assert report["best_total_ops"] == 11
    assert report["best_patch_assignments"][0] == {
        "patch": "err[6] and err[9] and not err[10]",
        "core": "err[6]",
        "families": ["ADD_LITERAL"],
        "ops": [
            {
                "family": "ADD_LITERAL",
                "feature": "err[10]",
                "kind": "ATOM",
                "sign": "NEG",
            },
            {
                "family": "ADD_LITERAL",
                "feature": "err[9]",
                "kind": "ATOM",
                "sign": "POS",
            },
        ],
    }


if __name__ == "__main__":
    test_semantic_macro_family_frontier()
    print("ok")
