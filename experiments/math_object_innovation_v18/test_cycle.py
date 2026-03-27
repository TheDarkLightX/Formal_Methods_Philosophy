#!/usr/bin/env python3
from __future__ import annotations

from run_cycle import build_report


def test_size_one_region_certificate_exists() -> None:
    report = build_report()
    assert report["survivor"] == "safe-region certificate frontier"
    assert report["frontier_size"] == 7104
    assert report["safe_count"] == 288
    assert report["first_region_certificate_size"] == 1
    assert report["best_by_size"][1]["best_safe_support"] == 288


if __name__ == "__main__":
    test_size_one_region_certificate_exists()
    print("ok")
