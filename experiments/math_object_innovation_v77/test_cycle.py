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
    assert report["survivor"] == "minimal witness-language phase diagram"
    assert report["frontier_state_count"] == 10

    optima = report["semantic_optima"]
    assert optima["all_positive_unordered"]["family"] == "positive_invented_cover"
    assert optima["all_positive_unordered"]["description_cost"] == 4
    assert optima["all_positive_unordered"]["fully_positive"] is True

    assert optima["residual_default_unordered"]["family"] == "mixed_atom_cover"
    assert optima["residual_default_unordered"]["description_cost"] == 4
    assert optima["residual_default_unordered"]["default_label"] == "fail_828"

    assert optima["ordered_exact_classifier"]["family"] == "ordered_decision_list"
    assert optima["ordered_exact_classifier"]["description_cost"] == 4
    assert optima["ordered_exact_classifier"]["default_label"] == "fail_828"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
