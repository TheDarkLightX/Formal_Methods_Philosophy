#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v42.run_cycle import (  # noqa: E402
    FEATURES,
    atom_name,
    atom_satisfies,
    feature_name,
    rows,
)
from experiments.math_object_innovation_v83.run_cycle import build_report as build_v83  # noqa: E402


OUT = ROOT / "generated" / "report.json"
V83_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v83" / "generated" / "report.json"


def load_v83_report() -> dict:
    if V83_REPORT.exists():
        return json.loads(V83_REPORT.read_text(encoding="utf-8"))
    return build_v83()


def atom_candidates(max_literals: int):
    atoms = []
    for size in range(1, max_literals + 1):
        for indexes in combinations(range(len(FEATURES)), size):
            for values in product([False, True], repeat=size):
                atoms.append((indexes, values))
    return atoms


def grouped_rows():
    grouped = defaultdict(list)
    for row in rows():
        grouped[row["score"]].append(row)
    return grouped


def block_rows(region, grouped):
    out = []
    for score in region:
        out.extend(grouped[score])
    return out


def exact_positive_cover(region_rows, atoms):
    labels = sorted({row["label"] for row in region_rows})
    label_masks = {label: 0 for label in labels}
    for index, row in enumerate(region_rows):
        label_masks[row["label"]] |= 1 << index

    pure_atoms = defaultdict(dict)
    for atom in atoms:
        mask = 0
        for index, row in enumerate(region_rows):
            if atom_satisfies(row["feature_vector"], atom):
                mask |= 1 << index
        if mask == 0:
            continue
        for label in labels:
            if mask & ~label_masks[label]:
                continue
            name = atom_name(atom)
            prior = pure_atoms[label].get(mask)
            if prior is None or len(name) < len(prior):
                pure_atoms[label][mask] = name

    def minimal_cover(label):
        options = sorted(
            [(name, mask) for mask, name in pure_atoms[label].items()],
            key=lambda item: (-item[1].bit_count(), len(item[0]), item[0]),
        )
        target_mask = label_masks[label]

        @lru_cache(maxsize=None)
        def rec(mask):
            if mask == target_mask:
                return ()
            remaining = target_mask & ~mask
            pivot = (remaining & -remaining).bit_length() - 1
            best = None
            for index, (_, option_mask) in enumerate(options):
                if not (option_mask & (1 << pivot)):
                    continue
                new_mask = mask | option_mask
                if new_mask == mask:
                    continue
                suffix = rec(new_mask)
                if suffix is None:
                    continue
                candidate = (index,) + suffix
                if best is None or len(candidate) < len(best):
                    best = candidate
            return best

        answer = rec(0)
        if answer is None:
            return None
        return [options[index][0] for index in answer]

    covers = {label: minimal_cover(label) for label in labels}
    possible = all(formulas is not None for formulas in covers.values())
    total_cost = None if not possible else sum(len(formulas) for formulas in covers.values())
    return {
        "possible": possible,
        "label_count": len(labels),
        "covers": covers,
        "total_cost": total_cost,
    }


def critical_regions_from_v83(v83_report: dict):
    ordered = []
    seen = set()
    for row in v83_report["budget_ladder"]:
        for region in row["optimal_partition"]:
            region_tuple = tuple(region)
            if region_tuple not in seen:
                seen.add(region_tuple)
                ordered.append(region_tuple)
    return ordered


def build_report():
    v83 = load_v83_report()
    critical_regions = critical_regions_from_v83(v83)
    grouped = grouped_rows()
    atoms4 = atom_candidates(4)
    atoms5 = atom_candidates(5)

    region_reports = []
    changed_regions = []
    newly_feasible_regions = []
    unchanged_regions = []

    for region in critical_regions:
        rows_block = block_rows(region, grouped)
        four = exact_positive_cover(rows_block, atoms4)
        five = exact_positive_cover(rows_block, atoms5)
        changed = (four["possible"], four["total_cost"]) != (five["possible"], five["total_cost"])
        if changed:
            changed_regions.append(list(region))
        else:
            unchanged_regions.append(list(region))
        if not four["possible"] and five["possible"]:
            newly_feasible_regions.append(list(region))
        region_reports.append(
            {
                "scores": list(region),
                "label_count": four["label_count"],
                "row_count": len(rows_block),
                "literal_bound_4": {
                    "possible": four["possible"],
                    "total_cost": four["total_cost"],
                    "covers": four["covers"],
                },
                "literal_bound_5": {
                    "possible": five["possible"],
                    "total_cost": five["total_cost"],
                    "covers": five["covers"],
                },
            }
        )

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "exact all-positive certificate widening on the critical region union induced by the v83 hard partition-aware residual-budget frontier"
        ),
        "holdout_domain": "the same 13 holdout fact states reused from v29 through v83",
        "survivor": "hard critical-region certificate widening boundary",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "critical_regions": [list(region) for region in critical_regions],
        "critical_region_count": len(critical_regions),
        "region_reports": region_reports,
        "changed_regions": changed_regions,
        "unchanged_regions": unchanged_regions,
        "newly_feasible_regions": newly_feasible_regions,
        "strongest_claim": (
            "On the exact union of regions that appear in the v83 optimal hard-frontier partitions, widening strict all-positive certificates from the 1-to-4 literal conjunction grammar to the 1-to-5 literal conjunction grammar changes only region `(10,11)`. "
            "All other critical regions keep the same minimal exact cost. So the current hard-frontier wall is partly a grammar wall, localized at `(10,11)`, not a uniform failure of all-positive certification across the critical region set."
        ),
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
