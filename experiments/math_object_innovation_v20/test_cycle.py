#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_major_score_blocks_have_pure_first_refuters() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "score-block staircase frontier"
    assert report["block_count"] == 10
    assert report["blocks"][0]["holdout_total"] == 3821
    assert report["blocks"][0]["pure_block"] is True
    assert report["blocks"][1]["holdout_total"] == 3796
    assert report["blocks"][1]["pure_block"] is True
    assert report["blocks"][2]["holdout_total"] == 3775
    assert report["blocks"][2]["pure_block"] is True


if __name__ == "__main__":
    test_major_score_blocks_have_pure_first_refuters()
    print("ok")
