#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_score_safety_collapse_is_exact() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "score-safety collapse frontier"
    assert report["frontier_size"] == 7104
    assert report["safe_count"] == 288
    assert report["holdout_total_exact_collapse"] is True
    assert report["holdout_5_exact_collapse"] is True
    assert report["holdout_6_exact_collapse"] is True
    assert report["holdout_total_blocks"][0]["value"] == 3821
    assert report["holdout_total_blocks"][0]["safe"] == 288


if __name__ == "__main__":
    test_score_safety_collapse_is_exact()
    print("ok")
