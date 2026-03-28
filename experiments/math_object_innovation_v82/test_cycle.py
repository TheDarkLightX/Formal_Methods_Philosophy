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
    assert report["survivor"] == "hard residual-budget schema ladder"
    ladder = report["residual_budget_schema_ladder"]
    assert ladder[0]["optimal_shared_schema_count"] is None
    assert ladder[1]["optimal_shared_schema_count"] == 25
    assert ladder[1]["optimal_total_cost"] == 28
    assert ladder[1]["schema_gain_over_v81"] == 1
    assert ladder[1]["optimal_subsets"] == [[[10, 11]]]
    assert ladder[2]["optimal_shared_schema_count"] == 23
    assert ladder[2]["optimal_total_cost"] == 26
    assert ladder[2]["schema_gain_over_v81"] == 1
    assert ladder[3]["optimal_shared_schema_count"] == 21
    assert ladder[4]["optimal_shared_schema_count"] == 20
    assert ladder[5]["optimal_shared_schema_count"] == 19
    assert ladder[5]["optimal_total_cost"] == 22
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
