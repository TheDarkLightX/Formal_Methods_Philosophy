#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_monotone_refill_transfer() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "monotone refill transfer frontier"
    assert report["guard_count"] == 14
    assert report["unique_behavior_count"] == 1640
    assert report["viable_behavior_count"] == 130
    assert report["smallest_exact_semantic_basis_size"] == 6
    assert report["smallest_exact_semantic_basis_features"] == [
        "err[(0, 0, 1, 1)]",
        "err[(0, 1, 1, 0)]",
        "err[(1, 0, 0, 1)]",
        "err[(1, 0, 1, 0)]",
        "err[(1, 0, 1, 1)]",
        "err[(1, 1, 1, 0)]",
    ]


if __name__ == "__main__":
    test_monotone_refill_transfer()
    print("ok")
