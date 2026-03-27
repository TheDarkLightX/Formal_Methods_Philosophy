#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"


def sig_from_int(x: int, width: int = 4) -> tuple[int, ...]:
    return tuple((x >> idx) & 1 for idx in reversed(range(width)))


def minimal_unique_support_sizes(ordered):
    signatures = [sig_from_int(value) for value in ordered]
    masks = [
        mask
        for size in range(1, 5)
        for mask in itertools.combinations(range(4), size)
    ]
    mins = []
    for i, signature in enumerate(signatures):
        others = [other for j, other in enumerate(signatures) if j != i]
        best = None
        for coords in masks:
            pattern = tuple(signature[idx] for idx in coords)
            if all(tuple(other[idx] for idx in coords) != pattern for other in others):
                best = len(coords)
                break
        if best is None:
            raise RuntimeError("no unique-support witness found")
        mins.append(best)
    return mins


def summarize():
    histogram = {}
    profile_histogram = {}
    profile_examples = {}
    for ordered in itertools.permutations(range(16), 4):
        mins = minimal_unique_support_sizes(ordered)
        profile = tuple(sorted(mins))
        cost = sum(profile[:3])
        histogram[cost] = histogram.get(cost, 0) + 1
        profile_histogram[profile] = profile_histogram.get(profile, 0) + 1
        profile_examples.setdefault(
            profile,
            {
                "ordered_subset": ordered,
                "raw_role_sizes": mins,
                "cost": cost,
            },
        )
    return histogram, profile_histogram, profile_examples


def main():
    histogram, profiles, examples = summarize()
    report = {
        "survivor": "width4 support-profile frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "labeled four-role support tables with one distinct realized support "
            "signature per role at width 4"
        ),
        "holdout_domain": "the full width-4 abstract support-table family",
        "cost_histogram": [
            {"cost": cost, "count": count}
            for cost, count in sorted(histogram.items())
        ],
        "profile_histogram": [
            {
                "profile": list(profile),
                "count": count,
                "cost": sum(profile[:3]),
                "example": examples[profile],
            }
            for profile, count in sorted(profiles.items())
        ],
        "strongest_claim": (
            "On the exhaustive width-4 four-role support-table family, only six "
            "sorted minimal unique-support profiles occur, and the exact minimal "
            "compiler cost is determined by that profile, equivalently by the sum "
            "of its three smallest entries."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
