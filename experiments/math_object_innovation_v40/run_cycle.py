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


def feature_name(feature):
    if isinstance(feature, int):
        return f"err[{feature}]"
    op, subset = feature
    joiner = " AND " if op == "and" else " OR "
    return joiner.join(f"err[{index}]" for index in subset)


def feature_active(feature, vector):
    if isinstance(feature, int):
        return vector[feature]
    op, subset = feature
    values = [vector[index] for index in subset]
    if op == "or":
        return any(values)
    return all(values)


def rows():
    _, _, viable = unique_viable_behaviors()
    data = []
    for item in viable:
        error_vector = tuple(item["prediction"][state] != gold(state) for state in HOLDOUT)
        feature_vector = tuple(feature_active(feature, error_vector) for feature in FEATURES)
        data.append(
            {
                "score": item["hold_score"],
                "label": item["first_refuter"],
                "feature_vector": feature_vector,
            }
        )
    return data


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


def minimal_cover(target_mask, options):
    target_mask = int(target_mask)
    option_masks = [mask for _, mask in options]

    @lru_cache(maxsize=None)
    def solve(mask):
        if mask == target_mask:
            return ()
        remaining = target_mask & ~mask
        pivot = (remaining & -remaining).bit_length() - 1
        best = None
        for index, option_mask in enumerate(option_masks):
            if not (option_mask & (1 << pivot)):
                continue
            if option_mask | mask == mask:
                continue
            suffix = solve(mask | option_mask)
            if suffix is None:
                continue
            candidate = (index,) + suffix
            if best is None or len(candidate) < len(best):
                best = candidate
        return best

    answer = solve(0)
    if answer is None:
        return None
    return [options[index][0] for index in answer]


def score_block_summary(block_rows, atoms):
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

    positive_covers = {}
    missing_positive_labels = []
    for label in labels:
        options = sorted(
            [(name, mask) for mask, name in pure_atoms[label].items()],
            key=lambda item: (bin(item[1]).count("1"), len(item[0]), item[0]),
        )
        cover = minimal_cover(label_masks[label], options)
        positive_covers[str(label)] = cover
        if cover is None:
            missing_positive_labels.append(str(label))

    all_positive_possible = not missing_positive_labels
    all_positive_cost = None
    if all_positive_possible:
        all_positive_cost = sum(len(positive_covers[str(label)]) for label in labels)

    best_default = None
    best_mixed_cost = None
    best_mixed_language = None
    for default_label in labels:
        others = [label for label in labels if label != default_label]
        if any(positive_covers[str(label)] is None for label in others):
            continue
        cost = sum(len(positive_covers[str(label)]) for label in others)
        candidate = (
            cost,
            str(default_label),
            {
                str(label): positive_covers[str(label)]
                for label in others
            },
        )
        if best_mixed_cost is None or candidate[:2] < (best_mixed_cost, best_default):
            best_mixed_cost = cost
            best_default = str(default_label)
            best_mixed_language = candidate[2]

    return {
        "block_size": len(block_rows),
        "label_count": len(labels),
        "labels": [str(label) for label in labels],
        "all_positive_possible": all_positive_possible,
        "all_positive_cost": all_positive_cost,
        "missing_positive_labels": missing_positive_labels,
        "positive_covers": positive_covers,
        "best_default_label": best_default,
        "best_mixed_cost": best_mixed_cost,
        "best_mixed_language": best_mixed_language,
    }


def build_report():
    all_rows = rows()
    atoms = atom_candidates()
    score_blocks = defaultdict(list)
    for row in all_rows:
        score_blocks[row["score"]].append(row)

    summaries = {}
    total_mixed_cost = 0
    nontrivial_scores = []
    all_positive_failure_scores = []

    for score in sorted(score_blocks):
        summary = score_block_summary(score_blocks[score], atoms)
        if summary["label_count"] > 1:
            summaries[str(score)] = summary
            nontrivial_scores.append(score)
            total_mixed_cost += summary["best_mixed_cost"]
            if not summary["all_positive_possible"]:
                all_positive_failure_scores.append(score)

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "score-local mixed-sign witness-language search on the hard v38 feature frontier",
        "holdout_domain": "the same 13 holdout fact states from v29 to v39",
        "survivor": "score-local mixed-sign witness frontier",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "atom_count": len(atoms),
        "nontrivial_score_count": len(nontrivial_scores),
        "nontrivial_scores": nontrivial_scores,
        "total_mixed_cost": total_mixed_cost,
        "all_positive_failure_scores": all_positive_failure_scores,
        "score_summaries": summaries,
        "strongest_claim": (
            "In the searched witness-atom grammar over the hard v38 feature space, every nontrivial score block admits an exact mixed-sign witness language, "
            "with total mixed-sign cost 27 across the six nontrivial score blocks. "
            "All-positive witness languages already fail on score 9 and score 10 in the same grammar."
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
