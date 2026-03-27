#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_arithmetic_refuter_logic() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "arithmetic refuter logic frontier"
    assert report["frontier_size"] == 7104

    total = report["scalar_results"]["holdout_total"]
    assert total["pure_scalar_partition"] is True
    assert total["minimal_exact_decision_list"]["minimal_length"] == 3
    assert total["decision_list"] == [
        "if holdout_total > 3796 then safe",
        "else if holdout_total > 3775 then fail_13116",
        "else if holdout_total mod 23 = 3 then fail_1915",
        "else fail_828",
    ]

    holdout_5 = report["scalar_results"]["holdout_5_hits"]
    assert holdout_5["pure_scalar_partition"] is True
    assert holdout_5["minimal_exact_decision_list"]["minimal_length"] == 3
    assert holdout_5["decision_list"] == [
        "if holdout_5_hits > 2927 then safe",
        "else if holdout_5_hits > 2910 then fail_13116",
        "else if holdout_5_hits mod 17 = 3 then fail_1915",
        "else fail_828",
    ]

    holdout_6 = report["scalar_results"]["holdout_6_hits"]
    assert holdout_6["pure_scalar_partition"] is False
    assert holdout_6["mixed_buckets"] == [{"labels": ["fail_1915", "fail_828"], "pure": False, "value": 859}]


if __name__ == "__main__":
    test_arithmetic_refuter_logic()
    print("ok")
