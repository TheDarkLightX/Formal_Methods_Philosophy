#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_mprd_semantic_repair() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "MPRD semantic repair frontier"
    assert report["viable_behavior_count"] == 164
    assert report["smallest_exact_semantic_repair_count"] == 4
    assert report["smallest_exact_semantic_repair_features"] == [
        "err[(0, 0, 1)]",
        "err[(0, 1, 0)]",
        "err[(0, 1, 1)]",
        "err[(1, 1, 0)]",
    ]


if __name__ == "__main__":
    test_mprd_semantic_repair()
    print("ok")
