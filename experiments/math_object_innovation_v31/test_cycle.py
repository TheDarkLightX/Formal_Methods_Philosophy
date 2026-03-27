#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_irredundant_refill_horn_basis():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "irredundant refill Horn basis frontier"
    assert report["viable_behavior_count"] == 130
    assert report["basis"] == [3, 6, 8, 9, 10, 12]
    assert report["basis_exact"] is True
    assert all(result["exact"] is False for result in report["drop_results"])
    assert [result["extra_bit"] for result in report["missing_bit_results"]] == [5, 11]
    assert all(result["exact"] is True for result in report["missing_bit_results"])


if __name__ == "__main__":
    test_irredundant_refill_horn_basis()
    print("ok")
