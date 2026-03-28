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
from experiments.math_object_innovation_v44.run_cycle import build_report as build_v44  # noqa: E402


OUT = ROOT / "generated" / "report.json"


def atom_candidates():
    atoms = []
    for size in [1, 2, 3, 4]:
        for indexes in combinations(range(len(FEATURES)), size):
            for values in product([False, True], repeat=size):
                atoms.append((indexes, values))
    return atoms


def exact_positive_cover(block_rows, atoms):
    labels = sorted({row["label"] for row in block_rows})
    label_masks = {label: 0 for label in labels}
    for index, row in enumerate(block_rows):
        label_masks[row["label"]] |= 1 << index

    pure_atoms = defaultdict(dict)
    for atom in atoms:
        mask = 0
        for index, row in enumerate(block_rows):
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

    def cover_label(label):
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
            if remaining == 0:
                return ()
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

    covers = {label: cover_label(label) for label in labels}
    possible = all(formulas is not None for formulas in covers.values())
    total_cost = None if not possible else sum(len(formulas) for formulas in covers.values())
    return {
        "possible": possible,
        "label_count": len(labels),
        "covers": covers,
        "total_cost": total_cost,
    }


def build_report():
    v44 = build_v44()
    best_partition = tuple(tuple(region) for region in v44["best_partition"])
    all_rows = rows()
    grouped_rows = defaultdict(list)
    for row in all_rows:
        grouped_rows[row["score"]].append(row)
    atoms = atom_candidates()

    region_reports = []
    feasible_regions = 0
    total_cost_on_feasible = 0
    shared_schema_feasible = set()
    failing_regions = []

    for region in best_partition:
        block_rows = []
        for score in region:
            block_rows.extend(grouped_rows[score])
        summary = exact_positive_cover(block_rows, atoms)
        report = {
            "scores": list(region),
            "possible": summary["possible"],
            "label_count": summary["label_count"],
            "row_count": len(block_rows),
            "total_cost": summary["total_cost"],
            "covers": summary["covers"],
        }
        region_reports.append(report)
        if summary["possible"]:
            feasible_regions += 1
            total_cost_on_feasible += summary["total_cost"]
            for formulas in summary["covers"].values():
                shared_schema_feasible.update(formulas)
        else:
            failing_regions.append(list(region))

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "exact all-positive certificate search on the hard v44 merged-region witness frontier",
        "holdout_domain": "the same 13 holdout fact states used from v29 through v46",
        "survivor": "hard certificate-language boundary",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "best_partition": [list(region) for region in best_partition],
        "region_reports": region_reports,
        "feasible_region_count": feasible_regions,
        "failing_regions": failing_regions,
        "total_cost_on_feasible_regions": total_cost_on_feasible,
        "shared_schema_count_on_feasible_regions": len(shared_schema_feasible),
        "strongest_claim": (
            "On the hard merged-region witness frontier, the searched all-positive certificate family is not exact everywhere. "
            "It already fails on region `(10,11)` in the same 1-to-4-literal conjunction grammar where the residual-default witness language from v44 is exact. "
            "So on this frontier residual-default witnessing is not only cheaper than all-positive certification. It is necessary in the searched grammar."
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
