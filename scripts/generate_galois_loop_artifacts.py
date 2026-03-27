#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from analyze_galois_loops import exhaustive_report, random_report


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "data" / "galois_loop_reports.json"


def build_report() -> dict[str, object]:
    return {
        "tutorial": "galois-loops-and-obligation-carving",
        "source_script": "scripts/generate_galois_loop_artifacts.py",
        "receipts": {
            "exhaustive_3x3": exhaustive_report(3, 3),
            "exhaustive_3x4": exhaustive_report(3, 4),
            "random_6x8_seed17_trials1000": {
                "x_size": 6,
                "y_size": 8,
                "seed": 17,
                "trials": 1000,
                "rows": random_report(6, 8, 1000, 17),
            },
        },
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
