#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_horn_closed_refill_basis() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "horn-closed refill basis frontier"
    assert report["viable_behavior_count"] == 130
    assert report["v29_basis"] == [3, 6, 8, 9, 10, 12]
    assert report["v29_basis_closure_size"] == 11
    assert report["closure_missing_bits"] == [5, 11]
    assert report["smallest_exact_horn_closed_basis"] == [3, 6, 8, 9, 10, 12]
    assert report["smallest_exact_horn_closed_basis_size"] == 6


if __name__ == "__main__":
    test_horn_closed_refill_basis()
    print("ok")
