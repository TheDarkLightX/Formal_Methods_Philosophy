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


OUT = ROOT / "generated" / "report.json"
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


def build_region_modes_cache(grouped, atoms):
    @lru_cache(maxsize=None)
    def region_modes(region):
        block = block_rows(region, grouped)
        labels, label_masks, pure = pure_atoms(block, atoms)
        if len(labels) <= 1:
            label = labels[0] if labels else None
            trivial = ({"covers": tuple(), "default_label": label},)
            return {
                "residual_cost": 0,
                "residual_choices": trivial,
                "certificate_cost": 0,
                "certificate_choices": trivial,
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
    grouped = grouped_rows()
    atoms = atom_candidates(4)
    region_modes = build_region_modes_cache(grouped, atoms)

    ladder = []
    best_budget = None
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

        row = {
            "residual_region_count": residual_budget,
            "feasible_configuration_count": feasible_configuration_count,
            "optimal_shared_schema_count": best[0],
            "optimal_total_cost": best[1],
            "optimal_region_count": best[2],
            "optimal_partition": [list(region) for region in best[3]],
            "optimal_residual_regions": [list(region) for region in best[4]],
        }
        ladder.append(row)
        if best_budget is None or (row["optimal_shared_schema_count"], row["optimal_total_cost"]) < (
            best_budget["optimal_shared_schema_count"],
            best_budget["optimal_total_cost"],
        ):
            best_budget = row

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "partition-aware residual-budget witness-language transfer search on the toy lab-followup MPRD frontier, "
            "using 1-to-4-literal signed conjunctions over holdout error bits for both strict certificates and residual-default witnesses"
        ),
        "holdout_domain": "the 5 holdout fact states induced by the chosen 3-state training set",
        "survivor": "lab-followup partition-aware residual-budget transfer frontier",
        "feature_count": len(HOLDOUT),
        "feature_names": [feature_name(index) for index in range(len(HOLDOUT))],
        "nontrivial_scores": list(NONTRIVIAL_SCORES),
        "residual_budget_ladder": ladder,
        "best_budget": best_budget["residual_region_count"],
        "best_budget_shared_schema_count": best_budget["optimal_shared_schema_count"],
        "best_budget_total_cost": best_budget["optimal_total_cost"],
        "strongest_claim": (
            "On the toy lab-followup MPRD frontier, the partition-aware residual-budget witness-language loop transfers, "
            "but its exact geometry differs from the refill frontier. In the 1-to-4 literal signed-conjunction grammar over holdout error bits, "
            "a single merged residual-default region over all mixed score blocks lowers the best exact presentation from shared-schema cost 5 and total cost 5 "
            "to shared-schema cost 4 and total cost 4. Additional exact residual regions do not improve schema count and strictly worsen total cost. "
            "So residual structure transfers here as one merged exception layer rather than as a descending residual-budget ladder."
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
