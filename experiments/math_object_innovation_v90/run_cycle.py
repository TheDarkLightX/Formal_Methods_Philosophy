#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
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
HOLDOUT_NAMES = [str(state) for state in HOLDOUT]


def feature_name(index: int) -> str:
    return f"e{index + 1}"


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


def unsafe_rows():
    _, _, viable = unique_viable_behaviors()
    out = []
    for item in viable:
        if item["hold_score"] == len(HOLDOUT):
            continue
        error_vector = tuple(item["prediction"][state] != gold(state) for state in HOLDOUT)
        out.append(
            {
                "score": item["hold_score"],
                "label": str(item["first_refuter"]),
                "feature_vector": error_vector,
            }
        )
    return out


def pure_atoms(rows, atoms):
    labels = sorted({row["label"] for row in rows})
    label_masks = {label: 0 for label in labels}
    for index, row in enumerate(rows):
        label_masks[row["label"]] |= 1 << index

    pure = defaultdict(dict)
    for atom in atoms:
        mask = 0
        for index, row in enumerate(rows):
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


def search_languages(rows, atoms):
    labels, label_masks, pure = pure_atoms(rows, atoms)
    cover_options = {}
    for label in labels:
        options = sorted(
            [(name, mask) for mask, name in pure[label].items()],
            key=lambda item: (-item[1].bit_count(), len(item[0]), item[0]),
        )
        cover_options[label] = minimal_covers(options, label_masks[label])

    all_positive_cost = None
    all_positive_labels = []
    if all(cover_options[label] for label in labels):
        all_positive_cost = sum(len(cover_options[label][0]) for label in labels)
        all_positive_labels = labels

    residual_best_cost = None
    residual_defaults = []
    for default_label in labels:
        others = [label for label in labels if label != default_label]
        if any(not cover_options[label] for label in others):
            continue
        cost = sum(len(cover_options[label][0]) for label in others)
        if residual_best_cost is None or cost < residual_best_cost:
            residual_best_cost = cost
            residual_defaults = [default_label]
        elif cost == residual_best_cost:
            residual_defaults.append(default_label)

    return {
        "labels": labels,
        "cover_options": cover_options,
        "all_positive_cost": all_positive_cost,
        "all_positive_labels": all_positive_labels,
        "minimal_residual_cost": residual_best_cost,
        "minimal_residual_defaults": residual_defaults,
    }


def earliest_error_formula_map():
    return {
        str(HOLDOUT[1]): "not e1 and e2",
        str(HOLDOUT[2]): "not e1 and not e2 and e3",
        str(HOLDOUT[3]): "not e1 and not e2 and not e3 and e4",
        str(HOLDOUT[4]): "not e1 and not e2 and not e3 and not e4",
    }


def evaluate_formula(feature_vector, formula: str) -> bool:
    atoms = [part.strip() for part in formula.split(" and ")]
    for atom in atoms:
        if atom.startswith("not "):
            index = int(atom[5:]) - 1
            if feature_vector[index]:
                return False
        else:
            index = int(atom[1:]) - 1
            if not feature_vector[index]:
                return False
    return True


def direct_earliest_error_check(rows):
    formulas = earliest_error_formula_map()
    default_label = str(HOLDOUT[0])
    mismatches = []
    for row in rows:
        predicted = default_label
        for label, formula in formulas.items():
            if evaluate_formula(row["feature_vector"], formula):
                predicted = label
                break
        if predicted != row["label"]:
            mismatches.append({"score": row["score"], "expected": row["label"], "predicted": predicted})
    return {
        "default_label": default_label,
        "formula_map": formulas,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:5],
    }


def build_report():
    rows = unsafe_rows()
    atoms = atom_candidates(4)
    language = search_languages(rows, atoms)
    direct_check = direct_earliest_error_check(rows)
    label_counts = Counter(row["label"] for row in rows)

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "score-free earliest-error residual-language search on the unsafe block of the toy lab-followup MPRD frontier"
        ),
        "holdout_domain": "the 5 ordered holdout fact states induced by the chosen 3-state training set",
        "survivor": "lab-followup unsafe earliest-error residual law",
        "feature_count": len(HOLDOUT),
        "feature_names": [feature_name(index) for index in range(len(HOLDOUT))],
        "unsafe_behavior_count": len(rows),
        "label_counts": {label: label_counts[label] for label in sorted(label_counts)},
        "smallest_exact_all_positive_cost": language["all_positive_cost"],
        "smallest_exact_residual_cost": language["minimal_residual_cost"],
        "minimal_residual_defaults": language["minimal_residual_defaults"],
        "direct_earliest_error_check": direct_check,
        "strongest_claim": (
            "On the unsafe block of the toy lab-followup MPRD frontier, the first-refuter labels admit an exact score-free earliest-error residual-default law in the 1-to-4 literal signed-conjunction grammar. "
            "Defaulting to the first holdout state and certifying the later holdout states by earliest-error clauses yields exact cost 4, while the best exact all-positive presentation costs 5. "
            "This explains why the partition-aware transfer frontier from v88 prefers one merged residual-default region."
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
