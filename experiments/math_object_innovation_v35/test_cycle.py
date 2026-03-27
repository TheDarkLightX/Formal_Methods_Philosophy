#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def test_mixed_sign_label_language():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "mixed-sign label language frontier"
    assert report["state_count"] == 10
    assert report["all_positive_cost"] == 7
    assert report["best_default_label"] == "fail_828"
    assert report["best_mixed_cost"] == 4
    assert report["positive_covers"]["safe"] == ["H6 > 869"]
    assert report["positive_covers"]["fail_13116"] == ["H6 = 869"]
    assert report["positive_covers"]["fail_1915"] == ["H6 = 859 and E = False", "H6 = 865"]
    assert report["positive_covers"]["fail_828"] == ["E = True", "H6 = 858", "H6 = 864"]


if __name__ == "__main__":
    test_mixed_sign_label_language()
    print("ok")
