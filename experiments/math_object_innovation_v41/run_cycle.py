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

from experiments.math_object_innovation_v29.run_cycle import HOLDOUT, gold, unique_viable_behaviors


OUT = ROOT / "generated" / "report.json"
FEATURES = (
    ("and", (6, 10, 12)),
    3,
    ("and", (9, 10, 12)),
    6,
    8,
    9,
    10,
    12,
)
NONTRIVIAL_SCORES = (7, 8, 9, 10, 11, 12)


def feature_name(feature):
    if isinstance(feature, int):
        return f"err[{feature}]"
    op, subset = feature
    joiner = " OR " if op == "or" else " AND "
    return joiner.join(f"err[{index}]" for index in subset)


def feature_active(feature, vector):
    if isinstance(feature, int):
        return vector[feature]
    op, subset = feature
    values = [vector[index] for index in subset]
    if op == "or":
        return any(values)
    return all(values)


def atom_candidates():
    atoms = []
    for size in [1, 2, 3]:
        for indexes in combinations(range(len(FEATURES)), size):
            for values in product([False, True], repeat=size):
                atoms.append((indexes, values))
    return atoms


def atom_name(atom):
    indexes, values = atom
    parts = []
    for index, value in zip(indexes, values):
        name = feature_name(FEATURES[index])
        parts.append(name if value else f"not {name}")
    return " and ".join(parts)


def atom_satisfies(feature_vector, atom):
    indexes, values = atom
    return all(feature_vector[index] == value for index, value in zip(indexes, values))


def rows():
    _, _, viable = unique_viable_behaviors()
    data = []
    for item in viable:
        error_vector = tuple(item["prediction"][state] != gold(state) for state in HOLDOUT)
        feature_vector = tuple(feature_active(feature, error_vector) for feature in FEATURES)
        data.append(
            {
                "score": item["hold_score"],
                "label": str(item["first_refuter"]),
                "feature_vector": feature_vector,
            }
        )
    return data


def score_options(block_rows, atoms):
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
        best_size = None
        best_covers = []
        for size in range(1, 5):
            for combo in combinations(range(len(options)), size):
                union = 0
                formulas = []
                for index in combo:
                    union |= options[index][1]
                    formulas.append(options[index][0])
                if union == target_mask:
                    best_covers.append(tuple(formulas))
            if best_covers:
                best_size = size
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


def build_report():
    all_rows = rows()
    atoms = atom_candidates()
    grouped = defaultdict(list)
    for row in all_rows:
        grouped[row["score"]].append(row)

    per_score = {}
    for score in NONTRIVIAL_SCORES:
        best_cost, choices = score_options(grouped[score], atoms)
        per_score[score] = {
            "best_cost": best_cost,
            "choices": choices,
        }

    score_list = list(NONTRIVIAL_SCORES)
    best = None

    def rec(index, used_schemas, chosen):
        nonlocal best
        if index == len(score_list):
            schema_list = tuple(sorted(used_schemas))
            candidate = (len(schema_list), schema_list, dict(chosen))
            if best is None or candidate[:2] < best[:2]:
                best = candidate
            return

        score = score_list[index]
        for choice in per_score[score]["choices"]:
            new_schemas = set(used_schemas)
            for _, formulas in choice["covers"]:
                new_schemas.update(formulas)
            if best is not None and len(new_schemas) >= best[0]:
                continue
            chosen[score] = choice
            rec(index + 1, new_schemas, chosen)
            del chosen[score]

    rec(0, set(), {})

    total_mixed_cost = sum(per_score[score]["best_cost"] for score in score_list)
    best_schema_count, best_schemas, best_choices = best

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "global schema-sharing search over score-local mixed-sign witness languages on the hard v38 feature frontier",
        "holdout_domain": "the same 13 holdout fact states from v29 to v40",
        "survivor": "global witness-schema frontier",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "atom_count": len(atoms),
        "nontrivial_scores": list(score_list),
        "total_mixed_cost": total_mixed_cost,
        "best_shared_schema_count": best_schema_count,
        "best_shared_schemas": list(best_schemas),
        "score_best_costs": {str(score): per_score[score]["best_cost"] for score in score_list},
        "choice_count_by_score": {str(score): len(per_score[score]["choices"]) for score in score_list},
        "best_score_choices": {
            str(score): {
                "default_label": best_choices[score]["default_label"],
                "covers": {
                    label: list(formulas)
                    for label, formulas in best_choices[score]["covers"]
                },
            }
            for score in score_list
        },
        "strongest_claim": (
            "In the searched grammar, the exact score-local mixed-sign witness frontier from v40 compresses to a global library of only 20 distinct witness schemas, "
            "improving on the raw local mixed-sign cost of 27."
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
