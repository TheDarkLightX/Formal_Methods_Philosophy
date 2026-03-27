#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_mprd_transfer_boundary() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "MPRD transfer boundary frontier"
    assert report["guard_count"] == 26
    assert report["unique_behavior_count"] == 5283
    assert report["viable_behavior_count"] == 164
    assert report["smallest_exact_repair_feature_count"] == 4
    assert report["smallest_exact_repair_features"] == [
        "pred[(0, 0, 1)]",
        "pred[(0, 1, 0)]",
        "pred[(0, 1, 1)]",
        "pred[(1, 1, 0)]",
    ]


if __name__ == "__main__":
    test_mprd_transfer_boundary()
    print("ok")
