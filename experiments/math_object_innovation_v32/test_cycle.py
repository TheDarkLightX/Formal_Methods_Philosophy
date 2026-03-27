#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_ordered_refill_basis_compiler():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "ordered refill basis compiler frontier"
    assert report["viable_behavior_count"] == 130
    assert report["basis"] == [3, 6, 8, 9, 10, 12]
    assert report["k3"]["exact_order_count"] == 0
    assert report["k4"]["exact_order_count"] == 504
    assert report["k5"]["exact_order_count"] == 720


if __name__ == "__main__":
    test_ordered_refill_basis_compiler()
    print("ok")
