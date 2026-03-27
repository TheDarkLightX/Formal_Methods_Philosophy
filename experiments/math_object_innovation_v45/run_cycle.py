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

from experiments.math_object_innovation_v42.run_cycle import (
    FEATURES,
    NONTRIVIAL_SCORES,
    atom_name,
    atom_satisfies,
    feature_name,
    rows,
)
from experiments.math_object_innovation_v43.run_cycle import all_set_partitions


OUT = ROOT / "generated" / "report.json"


def atom_candidates(max_size: int):
    atoms = []
    for size in range(1, max_size + 1):
        for indexes in combinations(range(len(FEATURES)), size):
            for values in product([False, True], repeat=size):
                atoms.append((indexes, values))
    return atoms


def region_summary(region, grouped_rows, atoms):
    block_rows = []
    for score in region:
        block_rows.extend(grouped_rows[score])

    labels = sorted({row["label"] for row in block_rows})
    if len(labels) <= 1:
        return {
            "possible": True,
            "cost": 0,
            "default_label": labels[0] if labels else None,
        }

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

    covers = {label: minimal_cover(label) for label in labels}
    best = None
    for default_label in labels:
        others = [label for label in labels if label != default_label]
        if any(covers[label] is None for label in others):
            continue
        cost = sum(len(covers[label]) for label in others)
        candidate = (cost, default_label)
        if best is None or candidate < best:
            best = candidate

    if best is None:
        return {"possible": False, "cost": None, "default_label": None}

    return {"possible": True, "cost": best[0], "default_label": best[1]}


def feasible_map(max_size: int):
    atoms = atom_candidates(max_size)
    grouped_rows = defaultdict(list)
    for row in rows():
        grouped_rows[row["score"]].append(row)

    feasible = {}
    for partition in all_set_partitions(NONTRIVIAL_SCORES):
        summaries = [region_summary(region, grouped_rows, atoms) for region in partition]
        if not all(summary["possible"] for summary in summaries):
            continue
        feasible[tuple(tuple(region) for region in partition)] = sum(
            summary["cost"] for summary in summaries
        )
    return atoms, feasible


def build_report():
    atoms4, feasible4 = feasible_map(4)
    atoms5, feasible5 = feasible_map(5)

    best4 = min((cost, len(partition), partition) for partition, cost in feasible4.items())
    best5 = min((cost, len(partition), partition) for partition, cost in feasible5.items())
    improved_secondary = [
        {"partition": [list(region) for region in partition], "cost_4": feasible4[partition], "cost_5": feasible5[partition]}
        for partition in sorted(feasible4)
        if feasible4[partition] != feasible5[partition]
    ]

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "comparison of unconstrained score-partition witness frontiers on the hard "
            "v38 feature space, using conjunction atoms of 1 to 4 versus 1 to 5 "
            "signed literals"
        ),
        "holdout_domain": "the same 13 holdout fact states from v29 to v44",
        "survivor": "five-literal witness-grammar boundary frontier",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "nontrivial_scores": list(NONTRIVIAL_SCORES),
        "partition_count": 203,
        "atom_count_4": len(atoms4),
        "atom_count_5": len(atoms5),
        "feasible_partition_count_4": len(feasible4),
        "feasible_partition_count_5": len(feasible5),
        "same_feasible_partition_set": set(feasible4) == set(feasible5),
        "best_total_cost_4": best4[0],
        "best_total_cost_5": best5[0],
        "best_region_count_4": best4[1],
        "best_region_count_5": best5[1],
        "best_partition_4": [list(region) for region in best4[2]],
        "best_partition_5": [list(region) for region in best5[2]],
        "secondary_partition_improvement_count": len(improved_secondary),
        "secondary_partition_improvements": improved_secondary,
        "strongest_claim": (
            "Allowing conjunction atoms of 1 to 5 signed literals does not improve "
            "the best exact hard-frontier witness object from v44: the feasible "
            "partition set stays the same, the best partition stays the same, and "
            "the best total witness cost stays 22."
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
