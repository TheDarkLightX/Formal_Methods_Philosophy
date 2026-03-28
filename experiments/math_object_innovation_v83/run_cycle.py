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
    NONTRIVIAL_SCORES,
    atom_name,
    atom_satisfies,
    feature_name,
    rows,
)
from experiments.math_object_innovation_v43.run_cycle import all_set_partitions  # noqa: E402
from experiments.math_object_innovation_v82.run_cycle import build_report as build_v82  # noqa: E402


OUT = ROOT / "generated" / "report.json"


def atom_candidates():
    atoms = []
    for size in [1, 2, 3, 4]:
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


def pure_atoms(block_rows, atoms):
    labels = sorted({row["label"] for row in block_rows})
    label_masks = {label: 0 for label in labels}
    for index, row in enumerate(block_rows):
        label_masks[row["label"]] |= 1 << index

    pure = defaultdict(dict)
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
            prior = pure[label].get(mask)
            if prior is None or len(name) < len(prior):
                pure[label][mask] = name
    return labels, label_masks, pure


def minimal_covers(options, target_mask, max_size=6):
    answers = []
    for size in range(1, max_size + 1):
        for combo in combinations(range(len(options)), size):
            union = 0
            formulas = []
            for index in combo:
                union |= options[index][1]
                formulas.append(options[index][0])
            if union == target_mask:
                answers.append(tuple(formulas))
        if answers:
            return sorted(set(answers))
    return []


def build_region_modes_cache(grouped, atoms):
    @lru_cache(maxsize=None)
    def region_modes(region):
        rows_block = block_rows(region, grouped)
        labels, label_masks, pure = pure_atoms(rows_block, atoms)
        if len(labels) <= 1:
            label = labels[0] if labels else None
            return {
                "residual_cost": 0,
                "residual_choices": ({"covers": tuple(), "default_label": label},),
                "certificate_cost": 0,
                "certificate_choices": ({"covers": tuple(), "default_label": label},),
            }

        cover_options = {}
        for label in labels:
            options = sorted(
                [(name, mask) for mask, name in pure[label].items()],
                key=lambda item: (-item[1].bit_count(), len(item[0]), item[0]),
            )
            cover_options[label] = minimal_covers(options, label_masks[label])

        residual_best_cost = None
        residual_choices = []

        def rec_residual(index, labels_without_default, current, default_label):
            if index == len(labels_without_default):
                residual_choices.append(
                    {
                        "covers": tuple(sorted(current.items())),
                        "default_label": default_label,
                    }
                )
                return
            label = labels_without_default[index]
            for formulas in cover_options[label]:
                current[label] = formulas
                rec_residual(index + 1, labels_without_default, current, default_label)
                del current[label]

        for default_label in labels:
            others = [label for label in labels if label != default_label]
            if any(not cover_options[label] for label in others):
                continue
            cost = sum(len(cover_options[label][0]) for label in others)
            if residual_best_cost is None or cost < residual_best_cost:
                residual_best_cost = cost
                residual_choices = []
            if cost == residual_best_cost:
                rec_residual(0, others, {}, default_label)

        certificate_cost = None
        certificate_choices = []
        if all(cover_options[label] for label in labels):
            certificate_cost = sum(len(cover_options[label][0]) for label in labels)

            def rec_certificate(index, current):
                if index == len(labels):
                    certificate_choices.append({"covers": tuple(sorted(current.items()))})
                    return
                label = labels[index]
                for formulas in cover_options[label]:
                    current[label] = formulas
                    rec_certificate(index + 1, current)
                    del current[label]

            rec_certificate(0, {})

        return {
            "residual_cost": residual_best_cost,
            "residual_choices": tuple(residual_choices),
            "certificate_cost": certificate_cost,
            "certificate_choices": tuple(certificate_choices),
        }

    return region_modes


def build_report():
    v82 = build_v82()
    fixed_ladder = {
        row["residual_region_count"]: row for row in v82["residual_budget_schema_ladder"]
    }
    atoms = atom_candidates()
    grouped = grouped_rows()
    region_modes = build_region_modes_cache(grouped, atoms)

    ladder = []
    for residual_budget in range(1, len(NONTRIVIAL_SCORES)):
        best = None
        feasible_configuration_count = 0
        for partition in all_set_partitions(NONTRIVIAL_SCORES):
            regions = tuple(tuple(region) for region in partition)
            if len(regions) < residual_budget:
                continue
            for residual_subset in combinations(range(len(regions)), residual_budget):
                residual_set = set(residual_subset)
                total_cost = 0
                choice_lists = []
                possible = True
                for index, region in enumerate(regions):
                    modes = region_modes(region)
                    if index in residual_set:
                        if modes["residual_cost"] is None:
                            possible = False
                            break
                        total_cost += modes["residual_cost"]
                        choice_lists.append(modes["residual_choices"])
                    else:
                        if modes["certificate_cost"] is None:
                            possible = False
                            break
                        total_cost += modes["certificate_cost"]
                        choice_lists.append(modes["certificate_choices"])
                if not possible:
                    continue

                feasible_configuration_count += 1
                best_schema = [None]

                def rec_schema(index, used_schemas):
                    if best_schema[0] is not None and len(used_schemas) >= best_schema[0]:
                        return
                    if index == len(choice_lists):
                        best_schema[0] = (
                            len(used_schemas)
                            if best_schema[0] is None
                            else min(best_schema[0], len(used_schemas))
                        )
                        return
                    for choice in choice_lists[index]:
                        next_schemas = set(used_schemas)
                        for _, formulas in choice["covers"]:
                            next_schemas.update(formulas)
                        rec_schema(index + 1, next_schemas)

                rec_schema(0, set())
                candidate = (
                    best_schema[0],
                    total_cost,
                    len(regions),
                    regions,
                    tuple(sorted(tuple(regions[index]) for index in residual_set)),
                )
                if best is None or candidate[:3] < best[:3]:
                    best = candidate

        fixed = fixed_ladder[residual_budget]
        ladder.append(
            {
                "residual_region_count": residual_budget,
                "feasible_configuration_count": feasible_configuration_count,
                "optimal_shared_schema_count": best[0],
                "optimal_total_cost": best[1],
                "optimal_region_count": best[2],
                "optimal_partition": [list(region) for region in best[3]],
                "optimal_residual_regions": [list(region) for region in best[4]],
                "schema_gain_over_v82": fixed["optimal_shared_schema_count"] - best[0],
                "cost_gain_over_v82": fixed["optimal_total_cost"] - best[1],
            }
        )

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "joint search over score partitions and exact residual-region budgets "
            "on the hard v38 feature frontier, optimizing global shared-schema count"
        ),
        "holdout_domain": "the same 13 holdout fact states used from v29 through v46",
        "survivor": "hard partition-aware residual-budget frontier",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "nontrivial_scores": list(NONTRIVIAL_SCORES),
        "budget_ladder": ladder,
        "strongest_claim": (
            "On the hard refill witness frontier, the fixed v44 partition from "
            "v81 and v82 is not globally optimal once score partition and "
            "residual structure are searched jointly. For residual budgets 1 "
            "through 4, the best global shared-schema counts become 24, 22, 20, "
            "19, each improving v82 by one schema at the same exact total cost. "
            "The winning low-budget partitions merge scores as `(7,12)` and "
            "`(9,10)` before returning to the original five-region partition at "
            "budget 5."
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
