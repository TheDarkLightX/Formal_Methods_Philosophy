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
    assert report["survivor"] == "shared repair-language template"

    additive = report["additive_template_best"]
    assert additive["total_cost"] == 4
    assert additive["base_edges"] == [
        "bounds_obs->bounds",
        "guard_obs->guard",
        "transform_obs->transform",
    ]
    assert additive["family_deltas"] == {
        "overlap_patch_family": ["transform_obs->bounds"],
        "separable_patch_family": [],
    }
    assert report["additive_template_minima_count"] == 1

    signed = report["signed_template_best"]
    assert signed["total_cost"] == 4
    assert signed["base_edges"] == [
        "bounds_obs->bounds",
        "guard_obs->guard",
        "transform_obs->transform",
    ]
    assert signed["family_edits"] == {
        "overlap_patch_family": {"add": ["transform_obs->bounds"], "remove": []},
        "separable_patch_family": {"add": [], "remove": []},
    }
    assert report["signed_template_minima_count"] == 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
