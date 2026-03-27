#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_k4_refill_order_law():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "k4 refill order law frontier"
    assert report["viable_behavior_count"] == 130
    assert report["basis"] == [3, 6, 8, 9, 10, 12]
    assert report["exact_order_count"] == 504
    assert report["total_order_count"] == 720
    assert report["law_exact_match"] is True
    assert report["mismatches"] == []


if __name__ == "__main__":
    test_k4_refill_order_law()
    print("ok")
