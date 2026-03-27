#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "generated" / "report.json"


def ensure_report():
    if REPORT.exists():
        return
    subprocess.run([sys.executable, str(ROOT / "run_cycle.py")], check=True)


def test_v64_report():
    ensure_report()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["survivor"] == "support-literal compiler frontier"
    assert report["tier"] == "descriptive_oracle"
    assert report["oracle_dependent"] is True
    common = report["common_result"]
    assert common == {
        "all_domains_minimal_literal_cost": True,
        "all_domains_single_branch_inexact": True,
        "all_domains_two_branch_compilers": True,
        "domain_count": 3,
    }
    assert report["domain_a"]["preferred_compiler"] == {
        "branch_count": 2,
        "branches": [
            {"atom": "not has_v46", "label": "V41_PATCH", "literal_count": 1},
            {"atom": "not has_v41", "label": "V46_PATCH", "literal_count": 1},
        ],
        "default_label": "CORE",
        "total_literal_cost": 2,
    }
    assert report["domain_b"]["preferred_compiler"] == {
        "branch_count": 2,
        "branches": [
            {"atom": "has_AB", "label": "ADD_ANCHOR", "literal_count": 1},
            {"atom": "not has_MIX", "label": "OTHER", "literal_count": 1},
        ],
        "default_label": "MIX_DISCRIM",
        "total_literal_cost": 2,
    }
    assert report["domain_c"]["preferred_compiler"] == {
        "branch_count": 2,
        "branches": [
            {"atom": "has_drop", "label": "ADD_BUNDLE+DROP_BUNDLE", "literal_count": 1},
            {"atom": "has_flip", "label": "FLIP_BUNDLE", "literal_count": 1},
        ],
        "default_label": "ADD_BUNDLE",
        "total_literal_cost": 2,
    }


if __name__ == "__main__":
    test_v64_report()
    print("ok")
