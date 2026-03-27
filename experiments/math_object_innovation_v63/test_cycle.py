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


def test_support_signature_transfer_frontier():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "support-signature transfer frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["domain_a"] == {
        "features": ["has_v41", "has_v46"],
        "language": {
            "CORE": ["has_v41 and has_v46"],
            "V41_PATCH": ["not has_v46"],
            "V46_PATCH": ["not has_v41"],
        },
        "role_count": 3,
        "row_count": 22,
    }
    assert report["domain_b"] == {
        "features": ["has_AB", "has_MIX"],
        "language": {
            "ADD_ANCHOR": ["has_AB"],
            "MIX_DISCRIM": ["not has_AB and has_MIX"],
            "OTHER": ["not has_MIX"],
        },
        "role_count": 3,
        "row_count": 9,
    }


if __name__ == "__main__":
    test_support_signature_transfer_frontier()
    print("ok")
