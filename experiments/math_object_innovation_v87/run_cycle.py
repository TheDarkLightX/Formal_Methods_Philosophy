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
from experiments.math_object_innovation_v85.run_cycle import build_report as build_v85  # noqa: E402


OUT = ROOT / "generated" / "report.json"
V85_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v85" / "generated" / "report.json"
LOW_RESIDUAL_BUDGETS = (0, 1, 2)


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


def pure_atoms(region_rows, atoms):
    labels = sorted({row["label"] for row in region_rows})
    label_masks = {label: 0 for label in labels}
    for index, row in enumerate(region_rows):
        label_masks[row["label"]] |= 1 << index

    pure = defaultdict(dict)
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


def build_region_modes_cache(grouped, residual_atoms, certificate_atoms):
    @lru_cache(maxsize=None)
    def region_modes(region):
        rows_block = block_rows(region, grouped)
        labels, label_masks, residual_pure = pure_atoms(rows_block, residual_atoms)
        certificate_labels, certificate_masks, certificate_pure = pure_atoms(
            rows_block, certificate_atoms
        )
        assert labels == certificate_labels
        assert label_masks == certificate_masks

        if len(labels) <= 1:
            label = labels[0] if labels else None
            trivial = ({"covers": tuple(), "default_label": label},)
            return {
                "residual_cost": 0,
                "residual_choices": trivial,
                "certificate_cost": 0,
                "certificate_choices": trivial,
            }

        residual_options = {}
        certificate_options = {}
        for label in labels:
            residual_sorted = sorted(
                [(name, mask) for mask, name in residual_pure[label].items()],
                key=lambda item: (-item[1].bit_count(), len(item[0]), item[0]),
            )
            certificate_sorted = sorted(
                [(name, mask) for mask, name in certificate_pure[label].items()],
                key=lambda item: (-item[1].bit_count(), len(item[0]), item[0]),
            )
            residual_options[label] = minimal_covers(
                residual_sorted, label_masks[label]
            )
            certificate_options[label] = minimal_covers(
                certificate_sorted, label_masks[label]
            )

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
            for formulas in residual_options[label]:
                current[label] = formulas
                rec_residual(index + 1, labels_without_default, current, default_label)
                del current[label]

        for default_label in labels:
            others = [label for label in labels if label != default_label]
            if any(not residual_options[label] for label in others):
                continue
            cost = sum(len(residual_options[label][0]) for label in others)
            if residual_best_cost is None or cost < residual_best_cost:
                residual_best_cost = cost
                residual_choices = []
            if cost == residual_best_cost:
                rec_residual(0, others, {}, default_label)

        certificate_cost = None
        certificate_choices = []
        if all(certificate_options[label] for label in labels):
            certificate_cost = sum(len(certificate_options[label][0]) for label in labels)

            def rec_certificate(index, current):
                if index == len(labels):
                    certificate_choices.append({"covers": tuple(sorted(current.items()))})
                    return
                label = labels[index]
                for formulas in certificate_options[label]:
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


def build_budget_row(residual_budget: int, region_modes):
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

    return {
        "residual_region_count": residual_budget,
        "feasible_configuration_count": feasible_configuration_count,
        "optimal_shared_schema_count": best[0],
        "optimal_total_cost": best[1],
        "optimal_region_count": best[2],
        "optimal_partition": [list(region) for region in best[3]],
        "optimal_residual_regions": [list(region) for region in best[4]],
    }


def build_report():
    if V85_REPORT.exists():
        v85 = json.loads(V85_REPORT.read_text(encoding="utf-8"))
    else:
        v85 = build_v85()
    prior = {
        row["residual_region_count"]: row
        for row in v85["budget_ladder"]
        if row["residual_region_count"] in LOW_RESIDUAL_BUDGETS
    }
    grouped = grouped_rows()
    region_modes = build_region_modes_cache(
        grouped,
        residual_atoms=atom_candidates(4),
        certificate_atoms=atom_candidates(6),
    )

    ladder = []
    moved_budgets = []
    for residual_budget in LOW_RESIDUAL_BUDGETS:
        row = build_budget_row(residual_budget, region_modes)
        old = prior[residual_budget]
        row["schema_gain_over_v85"] = old["optimal_shared_schema_count"] - row["optimal_shared_schema_count"]
        row["cost_gain_over_v85"] = old["optimal_total_cost"] - row["optimal_total_cost"]
        if row["schema_gain_over_v85"] != 0 or row["cost_gain_over_v85"] != 0:
            moved_budgets.append(residual_budget)
        ladder.append(row)

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "low-residual slice of the hard partition-aware residual-budget frontier, "
            "keeping residual-default witnesses in the 1-to-4 literal grammar while "
            "widening strict certificates from the 1-to-5 literal grammar to the 1-to-6 literal grammar"
        ),
        "holdout_domain": "the same 13 holdout fact states used from v29 through v86",
        "survivor": "low-residual widened-certificate saturation boundary",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "low_residual_budgets": list(LOW_RESIDUAL_BUDGETS),
        "budget_ladder": ladder,
        "moved_budgets": moved_budgets,
        "strongest_claim": (
            "On the hard refill witness frontier, widening strict certificates further from "
            "the 1-to-5 literal conjunction grammar to the 1-to-6 literal conjunction grammar "
            "does not move the low-residual end of the partition-aware residual-budget ladder. "
            "Budgets 0, 1, and 2 remain exactly fixed, so the full ladder is now locally saturated along this literal-width axis."
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
