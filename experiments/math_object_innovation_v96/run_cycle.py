#!/usr/bin/env python3
from __future__ import annotations

import json
from itertools import combinations, product
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v94.run_cycle import (
    TESTS,
    Patch,
    TRANSFORMS_COUPLED,
    TRANSFORMS_SEPARABLE,
    patch_family,
    run_patch,
)


OUT = ROOT / "generated" / "report.json"
OBS = ("guard_obs", "bounds_obs", "transform_obs")
FIELDS = ("guard", "bounds", "transform")


def patch_observation_vector(patch: Patch) -> tuple[int, int, int]:
    values = []
    for _, flag, value in TESTS:
        values.append(run_patch(patch, flag, value))
    return tuple(values)


def valid_subset_assignments():
    subsets = []
    for r in range(1, len(OBS) + 1):
        subsets.extend(combinations(range(len(OBS)), r))
    for choices in product(subsets, repeat=len(FIELDS)):
        yield choices


def field_value(patch: Patch, field: str) -> str:
    return getattr(patch, field)


def exact_for_field(
    family: list[Patch],
    obs_vectors: dict[Patch, tuple[int, int, int]],
    field: str,
    subset: tuple[int, ...],
) -> bool:
    buckets = {}
    for patch in family:
        key = tuple(obs_vectors[patch][i] for i in subset)
        value = field_value(patch, field)
        if key in buckets and buckets[key] != value:
            return False
        buckets[key] = value
    return True


def exact_assignment(
    family: list[Patch],
    obs_vectors: dict[Patch, tuple[int, int, int]],
    assignment: tuple[tuple[int, ...], ...],
) -> bool:
    return all(
        exact_for_field(family, obs_vectors, field, subset)
        for field, subset in zip(FIELDS, assignment)
    )


def assignment_cost(assignment: tuple[tuple[int, ...], ...]) -> int:
    return sum(len(subset) for subset in assignment)


def format_assignment(assignment: tuple[tuple[int, ...], ...]) -> dict[str, list[str]]:
    return {
        field: [OBS[i] for i in subset]
        for field, subset in zip(FIELDS, assignment)
    }


def analyze_family(name: str, transforms: tuple[str, ...]) -> dict[str, object]:
    family = patch_family(transforms)
    obs_vectors = {patch: patch_observation_vector(patch) for patch in family}
    exact_rows = []
    min_cost = None
    best_assignments = []

    for assignment in valid_subset_assignments():
        if exact_assignment(family, obs_vectors, assignment):
            cost = assignment_cost(assignment)
            row = {
                "cost": cost,
                "assignment": format_assignment(assignment),
            }
            exact_rows.append(row)
            if min_cost is None or cost < min_cost:
                min_cost = cost
                best_assignments = [row]
            elif cost == min_cost:
                best_assignments.append(row)

    cost_hist = {}
    for row in exact_rows:
        key = str(row["cost"])
        cost_hist[key] = cost_hist.get(key, 0) + 1

    return {
        "family": name,
        "candidate_count": len(family),
        "minimal_exact_decoder_cost": min_cost,
        "minimal_exact_decoder_count": len(best_assignments),
        "minimal_exact_decoders": best_assignments,
        "exact_decoder_cost_histogram": cost_hist,
    }


def build_report() -> dict[str, object]:
    separable = analyze_family("separable_patch_family", TRANSFORMS_SEPARABLE)
    overlap = analyze_family("overlap_patch_family", TRANSFORMS_COUPLED)
    return {
        "tier": "symbolic_state_compiler",
        "oracle_dependent": True,
        "discovery_domain": (
            "bounded software patch corpora from v94/v95, searching exact symbolic decoders "
            "from carried certificate observations back to patch fields"
        ),
        "holdout_domain": "exhaustive over both 27-patch corpora and all nonempty observation-subset decoders",
        "survivor": "certificate-to-patch decoder graph",
        "strongest_claim": (
            "On the bounded software corpora, the carried witness from v95 compiles back into the patch via a tiny exact "
            "decoder graph. The separable family has minimal decoder cost 3, one observation per field, while the overlap "
            "family has minimal cost 4, requiring exactly one extra dependency edge from transform observation into the "
            "bounds decoder."
        ),
        "families": [separable, overlap],
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
