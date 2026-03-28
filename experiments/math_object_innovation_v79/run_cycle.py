#!/usr/bin/env python3
from __future__ import annotations

import ast
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
from experiments.math_object_innovation_v46.run_cycle import build_report as build_v46  # noqa: E402


OUT = ROOT / "generated" / "report.json"


def atom_candidates():
    atoms = []
    for size in [1, 2, 3, 4]:
        for indexes in combinations(range(len(FEATURES)), size):
            for values in product([False, True], repeat=size):
                atoms.append((indexes, values))
    return atoms


def solve_binary_language(block_rows, atoms, target_fn):
    masks = {0: 0, 1: 0}
    for index, row in enumerate(block_rows):
        masks[target_fn(row)] |= 1 << index

    pure_atoms = defaultdict(dict)
    for atom in atoms:
        mask = 0
        for index, row in enumerate(block_rows):
            if atom_satisfies(row["feature_vector"], atom):
                mask |= 1 << index
        if mask == 0:
            continue
        for label in [0, 1]:
            if mask & ~masks[label]:
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
        target_mask = masks[label]

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

    covers = {label: minimal_cover(label) for label in [0, 1]}
    best = None
    for default_label in [0, 1]:
        other = 1 - default_label
        if covers[other] is None:
            continue
        cost = len(covers[other])
        candidate = (cost, default_label, covers[other])
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    if best is None:
        raise ValueError("no exact binary language found")
    return {
        "cost": best[0],
        "default_bit": best[1],
        "positive_witnesses": best[2],
    }


def build_report():
    v44 = build_v44()
    v46 = build_v46()
    best_partition = tuple(tuple(region) for region in v44["best_partition"])

    all_rows = rows()
    grouped_rows = defaultdict(list)
    for row in all_rows:
        grouped_rows[row["score"]].append(row)
    atoms = atom_candidates()

    region_reports = []
    total_bit_cost = 0
    shared_schemas = set()
    for region in best_partition:
        block_rows = []
        for score in region:
            block_rows.extend(grouped_rows[score])

        bit_reports = []
        region_cost = 0
        for bit in range(4):
            summary = solve_binary_language(
                block_rows,
                atoms,
                lambda row, bit=bit: ast.literal_eval(row["label"])[bit],
            )
            region_cost += summary["cost"]
            shared_schemas.update(summary["positive_witnesses"])
            bit_reports.append(
                {
                    "bit": bit,
                    "cost": summary["cost"],
                    "default_bit": summary["default_bit"],
                    "positive_witnesses": summary["positive_witnesses"],
                }
            )

        total_bit_cost += region_cost
        region_reports.append(
            {
                "scores": list(region),
                "bit_total_cost": region_cost,
                "label_level_cost": next(
                    row["cost"]
                    for row in v44["best_region_summaries"]
                    if tuple(row["scores"]) == region
                ),
                "bit_summaries": bit_reports,
            }
        )

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "exact bit-fiber decomposition search on the hard v44 merged-region witness frontier",
        "holdout_domain": "the same 13 holdout fact states used from v29 through v46",
        "survivor": "hard decomposition-language boundary",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "best_partition": [list(region) for region in best_partition],
        "region_reports": region_reports,
        "bit_fiber_total_cost": total_bit_cost,
        "label_level_total_cost": v44["best_total_cost"],
        "bit_fiber_shared_schema_count": len(shared_schemas),
        "label_level_shared_schema_count": v46["best_shared_schema_count"],
        "shared_schemas": sorted(shared_schemas),
        "strongest_claim": (
            "On the hard refill witness frontier, exact bit-fiber decomposition does not beat the existing label-level witness languages. "
            "Over the exact v44 partition, the best exact bitwise decomposition has total cost 24, compared with label-level cost 22, "
            "and its shared schema library has size 21, compared with the label-level shared-schema cost 19 from v46. "
            "So decomposition is available, but it is strictly worse than the current label-level witness language on this bounded frontier."
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
