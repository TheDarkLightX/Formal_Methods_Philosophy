#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_mixed_bucket_repair() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "mixed-bucket repair frontier"
    assert report["frontier_size"] == 7104
    assert report["mixed_bucket_value"] == 859
    assert report["mixed_bucket_size"] == 672
    assert report["mixed_bucket_labels"] == ["fail_1915", "fail_828"]
    assert report["survivor_count"] == 1
    assert report["best_repair_feature"]["name"] == "num_eq[4]"
    assert report["best_repair_feature"]["mixed_bucket_partition"] == {
        "False": ["fail_1915"],
        "True": ["fail_828"],
    }


if __name__ == "__main__":
    test_mixed_bucket_repair()
    print("ok")
