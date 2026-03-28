#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v94.run_cycle import (
    TESTS,
    TRANSFORMS_COUPLED,
    TRANSFORMS_SEPARABLE,
    patch_family,
    run_patch,
    summarize_family,
)

OUT = ROOT / "generated" / "report.json"


OBS_NAMES = ("guard", "bounds", "transform")


def certificate_observation(patch, index: int) -> int:
    _, flag, value = TESTS[index]
    return run_patch(patch, flag, value)


def analyze_family(name: str, transforms: tuple[str, ...]) -> dict[str, object]:
    family = patch_family(transforms)
    v94_summary = summarize_family(name, transforms)
    exact_bases = []
    basis_rows = []
    for r in range(1, len(OBS_NAMES) + 1):
        for subset in combinations(range(len(OBS_NAMES)), r):
            buckets = {}
            for patch in family:
                key = tuple(certificate_observation(patch, i) for i in subset)
                buckets.setdefault(key, []).append(patch)
            exact = all(len(v) == 1 for v in buckets.values())
            max_bucket = max(len(v) for v in buckets.values())
            row = {
                "basis": [OBS_NAMES[i] for i in subset],
                "size": len(subset),
                "key_count": len(buckets),
                "exact": exact,
                "max_bucket": max_bucket,
            }
            basis_rows.append(row)
            if exact:
                exact_bases.append(row)

    minimal_exact_size = min(row["size"] for row in exact_bases)
    minimal_exact_bases = [row["basis"] for row in exact_bases if row["size"] == minimal_exact_size]
    certificate_cost = minimal_exact_size

    return {
        "family": name,
        "candidate_count": len(family),
        "basis_scan": basis_rows,
        "minimal_exact_certificate_size": minimal_exact_size,
        "minimal_exact_certificate_bases": minimal_exact_bases,
        "certificate_verification_cost": certificate_cost,
        "v94_dependency_fiber_average_eval_cost": v94_summary["dependency_fiber_average_eval_cost"],
        "v94_monolithic_average_eval_cost": v94_summary["monolithic_average_eval_cost"],
    }


def build_report() -> dict[str, object]:
    separable = analyze_family("separable_patch_family", TRANSFORMS_SEPARABLE)
    overlap = analyze_family("overlap_patch_family", TRANSFORMS_COUPLED)
    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "bounded software-engineering patch corpora with three local failure fibers, "
            "searching minimal exact certificate bases over local observation tokens"
        ),
        "holdout_domain": "exhaustive over both 27-patch corpora and all observation-token subsets",
        "survivor": "certificate-carrying repair basis",
        "strongest_claim": (
            "On the bounded patch corpora from v94, carrying a local certificate over fiber observations reduces "
            "verification from dependency-aware search cost 9 to direct verification cost 3, and no singleton or pair "
            "basis is exact on either corpus."
        ),
        "families": [separable, overlap],
        "software_loop_ranking_hint": [
            "certificate_carrying_repair",
            "obligation_fibered_repair",
            "minimal_repair_language_discovery",
        ],
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
