#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
V69 = ROOT.parent / "math_object_innovation_v69" / "generated" / "report.json"
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"


def ensure_v69():
    if V69.exists():
        return
    subprocess.run(
        [sys.executable, str(V69.parent.parent / "run_cycle.py")],
        check=True,
    )


def rows():
    ensure_v69()
    report = json.loads(V69.read_text(encoding="utf-8"))
    out = []
    for entry in report["profile_histogram"]:
        profile = tuple(entry["profile"])
        out.append(
            {
                "profile": profile,
                "count": entry["count"],
                "cost": entry["cost"],
                "count_private_roles": sum(value == 1 for value in profile),
                "count_size2_roles": sum(value == 2 for value in profile),
                "count_size3_roles": sum(value == 3 for value in profile),
                "max_support_size": max(profile),
                "sum_support_sizes": sum(profile),
                "sum_three_smallest": sum(profile[:3]),
                "smallest_support_size": profile[0],
            }
        )
    return out


def exact_on(data, features, target):
    seen = {}
    for row in data:
        key = tuple(row[feature] for feature in features)
        if key in seen and seen[key] != row[target]:
            return False
        seen[key] = row[target]
    return True


def build_map(data, features, target):
    mapping = {}
    for row in data:
        key = tuple(row[feature] for feature in features)
        mapping[key] = row[target]
    return [
        {
            "features": list(key),
            target: list(value) if isinstance(value, tuple) else value,
        }
        for key, value in sorted(mapping.items())
    ]


def main():
    data = rows()
    feature_names = [
        "count_private_roles",
        "count_size2_roles",
        "count_size3_roles",
        "max_support_size",
        "sum_support_sizes",
        "sum_three_smallest",
        "smallest_support_size",
    ]
    singleton_exact = [name for name in feature_names if exact_on(data, [name], "profile")]
    pair_exact = [
        (a, b)
        for i, a in enumerate(feature_names)
        for b in feature_names[i + 1 :]
        if exact_on(data, [a, b], "profile")
    ]
    chosen = ("count_private_roles", "max_support_size")
    report = {
        "survivor": "width4 profile-pair law frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "minimal exact basis for reconstructing the width-4 support-profile "
            "frontier from v69, within the searched profile-derived statistic library"
        ),
        "holdout_domain": "the exact six-profile width-4 frontier from v69",
        "row_count": len(data),
        "singleton_exact": singleton_exact,
        "pair_exact": [list(item) for item in pair_exact],
        "chosen_pair": list(chosen),
        "chosen_pair_map": build_map(data, chosen, "profile"),
        "strongest_claim": (
            "On the exact width-4 support-profile frontier from v69, no searched "
            "singleton scalar reconstructs the full six-profile law, but the pair "
            "(count_private_roles, max_support_size) does so exactly."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
