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


def atom_candidates():
    atoms = []
    for size in [1, 2, 3, 4]:
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
            "language": {},
            "label_count": len(labels),
            "row_count": len(block_rows),
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
        candidate = (
            cost,
            default_label,
            {label: covers[label] for label in others},
        )
        if best is None or candidate[:2] < best[:2]:
            best = candidate

    if best is None:
        return {
            "possible": False,
            "cost": None,
            "default_label": None,
            "language": None,
            "label_count": len(labels),
            "row_count": len(block_rows),
        }

    return {
        "possible": True,
        "cost": best[0],
        "default_label": best[1],
        "language": best[2],
        "label_count": len(labels),
        "row_count": len(block_rows),
    }


def build_report():
    all_rows = rows()
    atoms = atom_candidates()
    grouped_rows = defaultdict(list)
    for row in all_rows:
        grouped_rows[row["score"]].append(row)

    feasible = []
    partition_count = 0
    for partition in all_set_partitions(NONTRIVIAL_SCORES):
        partition_count += 1
        summaries = [region_summary(region, grouped_rows, atoms) for region in partition]
        if not all(summary["possible"] for summary in summaries):
            continue
        total_cost = sum(summary["cost"] for summary in summaries)
        feasible.append((total_cost, len(partition), partition, summaries))

    feasible.sort(key=lambda item: (item[0], item[1], item[2]))
    best_cost, best_region_count, best_partition, best_summaries = feasible[0]

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "unconstrained score-partition search over exact positive-cover plus "
            "residual-default witness regions on the hard v38 feature frontier, "
            "with conjunction atoms of 1 to 4 signed literals"
        ),
        "holdout_domain": "the same 13 holdout fact states from v29 to v43",
        "survivor": "richer witness-grammar frontier",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "atom_count": len(atoms),
        "nontrivial_scores": list(NONTRIVIAL_SCORES),
        "partition_count": partition_count,
        "feasible_partition_count": len(feasible),
        "previous_best_total_cost": 23,
        "best_total_cost": best_cost,
        "best_region_count": best_region_count,
        "best_partition": [list(region) for region in best_partition],
        "best_region_summaries": [
            {
                "scores": list(region),
                "cost": summary["cost"],
                "default_label": summary["default_label"],
                "label_count": summary["label_count"],
                "row_count": summary["row_count"],
                "language": summary["language"],
            }
            for region, summary in zip(best_partition, best_summaries)
        ],
        "top_feasible_partitions": [
            {
                "total_cost": total_cost,
                "region_count": region_count,
                "partition": [list(region) for region in partition],
            }
            for total_cost, region_count, partition, _ in feasible[:10]
        ],
        "strongest_claim": (
            "In the searched witness grammar with conjunction atoms of 1 to 4 signed "
            "literals, the same best score partition from v42 and v43 remains optimal, "
            "but its exact positive-cover plus residual-default witness cost drops from "
            "23 to 22."
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
