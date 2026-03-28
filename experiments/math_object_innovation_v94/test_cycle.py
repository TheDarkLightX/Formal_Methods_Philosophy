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
    assert report["survivor"] == "dependency-aware obligation-fibered repair"
    families = {row["family"]: row for row in report["families"]}
    separable = families["separable_patch_family"]
    coupled = families["overlap_patch_family"]

    assert separable["candidate_count"] == 27
    assert separable["naive_fiber_exact_gold_count"] == 27
    assert separable["dependency_fiber_exact_gold_count"] == 27
    assert separable["naive_fiber_average_eval_cost"] < separable["monolithic_average_eval_cost"]

    assert coupled["candidate_count"] == 27
    assert coupled["naive_fiber_exact_gold_count"] < 27
    assert coupled["dependency_fiber_exact_gold_count"] == 27
    assert coupled["dependency_fiber_average_eval_cost"] < coupled["monolithic_average_eval_cost"]
    assert coupled["naive_ambiguous_examples"]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
