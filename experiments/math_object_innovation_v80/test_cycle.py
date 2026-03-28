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
    assert report["survivor"] == "hard certificate-language boundary"
    assert report["feasible_region_count"] == 4
    assert report["failing_regions"] == [[10, 11]]
    assert report["total_cost_on_feasible_regions"] == 23
    assert report["shared_schema_count_on_feasible_regions"] == 21
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
