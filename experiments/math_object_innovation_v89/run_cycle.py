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

from experiments.math_object_innovation_v26.run_cycle import (  # noqa: E402
    HOLDOUT,
    gold,
    unique_viable_behaviors,
)
from experiments.math_object_innovation_v88.run_cycle import build_report as build_v88  # noqa: E402


OUT = ROOT / "generated" / "report.json"
V88_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v88" / "generated" / "report.json"
NONTRIVIAL_SCORES = (1, 2, 3, 4)


def feature_name(index: int) -> str:
    return f"err[{HOLDOUT[index]}]"


def rows():
    _, _, viable = unique_viable_behaviors()
    out = []
    for item in viable:
        error_vector = tuple(item["prediction"][state] != gold(state) for state in HOLDOUT)
        out.append(
            {
                "score": item["hold_score"],
                "label": str(item["first_refuter"]),
                "feature_vector": error_vector,
            }
        )
    return out


def all_set_partitions(items):
    items = tuple(items)
    if not items:
        yield ()
        return
    first, *rest = items
    for partition in all_set_partitions(tuple(rest)):
        yield ((first,),) + partition
        for index, block in enumerate(partition):
            yield partition[:index] + (tuple(sorted(block + (first,))),) + partition[index + 1 :]


def canonical_partition(partition):
    return tuple(
        sorted((tuple(sorted(block)) for block in partition), key=lambda block: (len(block), block))
    )


def partitions(items):
    seen = set()
    for partition in all_set_partitions(items):
        canon = canonical_partition(partition)
        if canon not in seen:
            seen.add(canon)
            yield canon


def atom_candidates(max_literals: int):
    atoms = []
    for size in range(1, max_literals + 1):
        for indexes in combinations(range(len(HOLDOUT)), size):
            for values in product([False, True], repeat=size):
                atoms.append((indexes, values))
    return atoms


def atom_name(atom):
    indexes, values = atom
    return " and ".join(
        feature_name(index) if value else f"not {feature_name(index)}"
        for index, value in zip(indexes, values)
    )


def atom_satisfies(feature_vector, atom):
    indexes, values = atom
    return all(feature_vector[index] == value for index, value in zip(indexes, values))


def grouped_rows():
    grouped = defaultdict(list)
    for row in rows():
        if row["score"] in NONTRIVIAL_SCORES:
            grouped[row["score"]].append(row)
    return grouped


def block_rows(region, grouped):
    out = []
    for score in region:
        out.extend(grouped[score])
    return out


def pure_atoms(block, atoms):
    labels = sorted({row["label"] for row in block})
    label_masks = {label: 0 for label in labels}
    for index, row in enumerate(block):
        label_masks[row["label"]] |= 1 << index

    pure = defaultdict(dict)
    for atom in atoms:
        mask = 0
        for index, row in enumerate(block):
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
        block = block_rows(region, grouped)
        labels, label_masks, residual_pure = pure_atoms(block, residual_atoms)
        labels2, label_masks2, certificate_pure = pure_atoms(block, certificate_atoms)
        assert labels == labels2
        assert label_masks == label_masks2

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
            residual_options[label] = minimal_covers(residual_sorted, label_masks[label])
            certificate_options[label] = minimal_covers(certificate_sorted, label_masks[label])

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


def build_report():
    if V88_REPORT.exists():
        v88 = json.loads(V88_REPORT.read_text(encoding="utf-8"))
    else:
        v88 = build_v88()
    prior = {
        row["residual_region_count"]: row
        for row in v88["residual_budget_ladder"]
    }

    grouped = grouped_rows()
    region_modes = build_region_modes_cache(
        grouped,
        residual_atoms=atom_candidates(4),
        certificate_atoms=atom_candidates(5),
    )

    ladder = []
    moved_budgets = []
    for residual_budget in range(0, len(NONTRIVIAL_SCORES) + 1):
        best = None
        feasible_configuration_count = 0
        for partition in partitions(NONTRIVIAL_SCORES):
            if len(partition) < residual_budget:
                continue
            for residual_subset in combinations(range(len(partition)), residual_budget):
                residual_set = set(residual_subset)
                total_cost = 0
                choice_lists = []
                possible = True
                for index, region in enumerate(partition):
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
                    len(partition),
                    partition,
                    tuple(sorted(tuple(partition[index]) for index in residual_set)),
                )
                if best is None or candidate[:3] < best[:3]:
                    best = candidate

        old = prior[residual_budget]
        row = {
            "residual_region_count": residual_budget,
            "feasible_configuration_count": feasible_configuration_count,
            "optimal_shared_schema_count": best[0],
            "optimal_total_cost": best[1],
            "optimal_region_count": best[2],
            "optimal_partition": [list(region) for region in best[3]],
            "optimal_residual_regions": [list(region) for region in best[4]],
            "schema_gain_over_v88": old["optimal_shared_schema_count"] - best[0],
            "cost_gain_over_v88": old["optimal_total_cost"] - best[1],
        }
        if row["schema_gain_over_v88"] != 0 or row["cost_gain_over_v88"] != 0:
            moved_budgets.append(residual_budget)
        ladder.append(row)

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "lab-followup partition-aware residual-budget transfer frontier, keeping residual-default witnesses in the 1-to-4 literal grammar while widening strict certificates from the 1-to-4 literal grammar to the 1-to-5 literal grammar"
        ),
        "holdout_domain": "the 5 holdout fact states induced by the chosen 3-state training set",
        "survivor": "lab-followup widened-certificate saturation boundary",
        "feature_count": len(HOLDOUT),
        "feature_names": [feature_name(index) for index in range(len(HOLDOUT))],
        "nontrivial_scores": list(NONTRIVIAL_SCORES),
        "residual_budget_ladder": ladder,
        "moved_budgets": moved_budgets,
        "strongest_claim": (
            "On the toy lab-followup MPRD frontier, widening strict certificates from the 1-to-4 literal conjunction grammar to the full 1-to-5 literal conjunction grammar does not move any rung of the partition-aware residual-budget ladder. "
            "The merged residual-default region over all mixed score blocks remains exactly optimal, so the transfer object from v88 is already locally saturated on this literal-width axis."
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
