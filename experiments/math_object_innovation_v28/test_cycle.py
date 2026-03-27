#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_earliest_error_compiler() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "earliest-error compiler frontier"
    assert report["viable_behavior_count"] == 164
    assert report["earliest_error_exact"] is True
    assert report["four_bit_basis_exact"] is True
    assert report["four_bit_basis_bucket_count"] == 31
    assert all(not row["exact"] for row in report["three_bit_results"])


if __name__ == "__main__":
    test_earliest_error_compiler()
    print("ok")
