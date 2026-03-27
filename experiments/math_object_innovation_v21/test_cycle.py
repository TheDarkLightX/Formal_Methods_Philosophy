#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_scalar_refuter_quotient() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "scalar refuter quotient frontier"
    assert report["frontier_size"] == 7104
    assert report["holdout_total_exact_refuter_quotient"] is True
    assert report["holdout_5_exact_refuter_quotient"] is True
    assert report["holdout_6_exact_refuter_quotient"] is False


if __name__ == "__main__":
    test_scalar_refuter_quotient()
    print("ok")
