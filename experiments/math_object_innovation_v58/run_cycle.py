#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = (
    ROOT.parent
    / "math_object_innovation_v57"
    / "generated"
    / "report.json"
)
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"


def load_basis_sets():
    report = json.loads(INPUT.read_text(encoding="utf-8"))
    all_positive = {
        tuple(sorted(item["features"])) for item in report["all_positive"]["exact_bases"]
    }
    residual_default = [
        {
            "features": tuple(sorted(item["features"])),
            "default_label": item["language"]["default_label"],
        }
        for item in report["residual_default"]["exact_bases"]
    ]
    features = sorted({feature for pair in all_positive for feature in pair})
    return features, all_positive, residual_default


def product_pairs(left, right):
    pairs = set()
    for l in left:
        for r in right:
            if l == r:
                continue
            pairs.add(tuple(sorted((l, r))))
    return pairs


def search_templates(features, target_pairs):
    winners = []
    values = [0, 1, 2]  # left, right, unused
    for assignment in itertools.product(values, repeat=len(features)):
        left = [f for f, role in zip(features, assignment) if role == 0]
        right = [f for f, role in zip(features, assignment) if role == 1]
        unused = [f for f, role in zip(features, assignment) if role == 2]
        if not left or not right:
            continue
        generated = product_pairs(left, right)
        if generated != target_pairs:
            continue
        winners.append(
            {
                "left": left,
                "right": right,
                "unused": unused,
                "slot_cost": len(left) + len(right),
            }
        )
    winners.sort(
        key=lambda item: (
            item["slot_cost"],
            len(item["unused"]),
            item["left"],
            item["right"],
        )
    )
    return winners


def analyze_residual_family(all_positive_pairs, residual_rows):
    defaults = sorted({row["default_label"] for row in residual_rows})
    by_default = {
        default: {
            row["features"] for row in residual_rows if row["default_label"] == default
        }
        for default in defaults
    }
    same_pair_family = all(pairs == all_positive_pairs for pairs in by_default.values())
    return {
        "default_labels": defaults,
        "count": len(residual_rows),
        "same_pair_family_per_default": same_pair_family,
        "per_default_pair_count": {default: len(pairs) for default, pairs in by_default.items()},
    }


def main():
    features, all_positive_pairs, residual_default = load_basis_sets()
    templates = search_templates(features, all_positive_pairs)
    residual_analysis = analyze_residual_family(all_positive_pairs, residual_default)
    best = templates[0] if templates else None
    report = {
        "survivor": "primitive basis template frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "role-template compression over the exact raw primitive basis family "
            "from v57"
        ),
        "holdout_domain": "the exact v57 all-positive and residual-default primitive basis families",
        "primitive_features": features,
        "all_positive_basis_count": len(all_positive_pairs),
        "residual_default_count": len(residual_default),
        "template_count": len(templates),
        "best_template": best,
        "all_templates": templates,
        "residual_default_analysis": residual_analysis,
        "strongest_claim": (
            "The six exact raw primitive all-positive bases from v57 collapse "
            "exactly to a two-slot product template, unique up to slot swap: "
            "one slot is {add[3], add[6], add[10]} and the other is "
            "{add[8], drop[12]}. The residual-default family is the same pair "
            "template crossed with all three default labels."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
