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
    assert report["survivor"] == "certificate-to-patch decoder graph"
    families = {row["family"]: row for row in report["families"]}

    sep = families["separable_patch_family"]
    assert sep["minimal_exact_decoder_cost"] == 3
    assert sep["minimal_exact_decoder_count"] == 1
    assert sep["minimal_exact_decoders"] == [
        {
            "assignment": {
                "bounds": ["bounds_obs"],
                "guard": ["guard_obs"],
                "transform": ["transform_obs"],
            },
            "cost": 3,
        }
    ]

    ov = families["overlap_patch_family"]
    assert ov["minimal_exact_decoder_cost"] == 4
    assert ov["minimal_exact_decoder_count"] == 1
    assert ov["minimal_exact_decoders"] == [
        {
            "assignment": {
                "bounds": ["bounds_obs", "transform_obs"],
                "guard": ["guard_obs"],
                "transform": ["transform_obs"],
            },
            "cost": 4,
        }
    ]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
