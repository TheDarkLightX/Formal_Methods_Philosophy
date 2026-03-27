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


def test_typed_semantic_patch_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "typed semantic-patch frontier"
    assert report["shared_core_size"] == 17
    assert report["patch_count"] == 5
    assert report["search_count"] == 1419857
    assert report["nearest_core_signature_count"] == 5
    assert report["best_signature_vocab_size"] == 4
    assert report["best_total_edit_cost"] == 15
    assert report["best_signature_vocab"] == [
        ["ADD_NEG_ATOM", "ADD_NEG_ATOM", "ADD_POS_ATOM", "DROP_POS_ATOM"],
        ["ADD_NEG_ATOM", "ADD_NEG_ATOM", "DROP_POS_ATOM"],
        ["ADD_NEG_ATOM", "ADD_POS_ATOM"],
        ["ADD_POS_AND3", "DROP_NEG_AND3"],
    ]
    assert report["best_patch_assignments"][0] == {
        "patch": "err[6] and err[9] and not err[10]",
        "core": "err[6]",
        "edit_cost": 2,
        "signature": ["ADD_NEG_ATOM", "ADD_POS_ATOM"],
    }


if __name__ == "__main__":
    test_typed_semantic_patch_frontier()
    print("ok")
