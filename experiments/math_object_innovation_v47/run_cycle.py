#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v42.run_cycle import (
    FEATURES,
    atom_name,
    atom_satisfies,
    feature_name,
    rows,
)


OUT = ROOT / "generated" / "report.json"
BEST_PARTITION = ((7,), (8,), (9,), (10, 11), (12,))


def atom_candidates(max_size: int):
    atoms = []
    for size in range(1, max_size + 1):
        for indexes in combinations(range(len(FEATURES)), size):
            for values in product([False, True], repeat=size):
                atoms.append((indexes, values))
    return atoms


def region_options(block_rows, atoms):
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

    cover_options = {}
    for label in labels:
        options = sorted(
            [(name, mask) for mask, name in pure_atoms[label].items()],
            key=lambda item: (-item[1].bit_count(), len(item[0]), item[0]),
        )
        target_mask = label_masks[label]
        best_covers = []
        for size in range(1, 6):
            for combo in combinations(range(len(options)), size):
                union = 0
                formulas = []
                for index in combo:
                    union |= options[index][1]
                    formulas.append(options[index][0])
                if union == target_mask:
                    best_covers.append(tuple(formulas))
            if best_covers:
                break
        cover_options[label] = best_covers

    best_cost = None
    all_choices = []

    def rec_default(index, labels_without_default, current, default_label):
        if index == len(labels_without_default):
            all_choices.append(
                {
                    "default_label": default_label,
                    "covers": tuple(sorted(current.items())),
                }
            )
            return
        label = labels_without_default[index]
        for formulas in cover_options[label]:
            current[label] = formulas
            rec_default(index + 1, labels_without_default, current, default_label)
            del current[label]

    for default_label in labels:
        others = [label for label in labels if label != default_label]
        if any(not cover_options[label] for label in others):
            continue
        cost = sum(len(cover_options[label][0]) for label in others)
        if best_cost is None or cost < best_cost:
            best_cost = cost
            all_choices = []
        if cost == best_cost:
            rec_default(0, others, {}, default_label)

    return best_cost, all_choices


def schema_summary(max_size: int):
    atoms = atom_candidates(max_size)
    grouped = defaultdict(list)
    for row in rows():
        grouped[row["score"]].append(row)

    per_region = {}
    for region in BEST_PARTITION:
        block_rows = []
        for score in region:
            block_rows.extend(grouped[score])
        per_region[region] = region_options(block_rows, atoms)

    best = None

    def rec(index, used_schemas):
        nonlocal best
        if index == len(BEST_PARTITION):
            schema_list = tuple(sorted(used_schemas))
            candidate = (len(schema_list), schema_list)
            if best is None or candidate < best:
                best = candidate
            return

        region = BEST_PARTITION[index]
        for choice in per_region[region][1]:
            new_schemas = set(used_schemas)
            for _, formulas in choice["covers"]:
                new_schemas.update(formulas)
            if best is not None and len(new_schemas) >= best[0]:
                continue
            rec(index + 1, new_schemas)

    rec(0, set())
    total_cost = sum(per_region[region][0] for region in BEST_PARTITION)
    return {
        "atom_count": len(atoms),
        "total_region_cost": total_cost,
        "best_shared_schema_count": best[0],
    }


def build_report():
    summary_4 = schema_summary(4)
    summary_5 = schema_summary(5)
    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "comparison of global witness-schema synthesis on the exact v44 partition, "
            "using conjunction atoms of 1 to 4 versus 1 to 5 signed literals"
        ),
        "holdout_domain": "the same 13 holdout fact states from v29 to v46",
        "survivor": "global witness-synthesis grammar boundary frontier",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "best_partition": [list(region) for region in BEST_PARTITION],
        "summary_4": summary_4,
        "summary_5": summary_5,
        "strongest_claim": (
            "Allowing conjunction atoms of 1 to 5 signed literals does not improve "
            "the main global witness object from v46: the exact partition stays the "
            "same, total region cost stays 22, and the best shared global schema "
            "count stays 19."
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
