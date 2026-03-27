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


def test_cross_frontier_core_plus_patch_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "cross-frontier core-plus-patch frontier"
    assert report["core_schema_count"] == 17
    assert report["v41_patch_count"] == 3
    assert report["v46_patch_count"] == 2
    assert report["residual_union_count"] == 5
    assert report["residual_template_count"] == 5
    assert report["residual_template_irreducible"] is True
    assert report["v41_only_schemas"] == [
        "err[6] and err[9] and not err[10]",
        "not err[3] and err[9] AND err[10] AND err[12] and not err[6]",
        "not err[8] and not err[12]",
    ]
    assert report["v46_only_schemas"] == [
        "not err[3] and not err[6] and err[10] and err[12]",
        "not err[3] and not err[6] and not err[8] and err[10]",
    ]


if __name__ == "__main__":
    test_cross_frontier_core_plus_patch_frontier()
    print("ok")
