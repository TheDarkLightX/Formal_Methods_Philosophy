#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
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
    rows,
)


OUT = ROOT / "generated" / "report.json"


def feature_name(feature) -> str:
    if isinstance(feature, int):
        return f"err[{feature}]"
    _, subset = feature
    return "(" + " AND ".join(f"err[{index}]" for index in subset) + ")"


def feature_active(feature_vector, atom) -> bool:
    indexes, values = atom
    return all(feature_vector[index] == value for index, value in zip(indexes, values))


def atom_candidates():
    atoms = []
    for size in [1, 2, 3, 4]:
        for indexes in combinations(range(len(FEATURES)), size):
            for values in product([False, True], repeat=size):
                atoms.append((indexes, values))
    return atoms


def atom_name(atom) -> str:
    indexes, values = atom
    parts = []
    for index, value in zip(indexes, values):
        name = feature_name(FEATURES[index])
        if value:
            parts.append(name)
        else:
            parts.append(f"not {name}")
    return " and ".join(parts)


def subset_rows(subset):
    score_set = set(subset)
    return [row for row in rows() if row["score"] in score_set]


def pure_atoms(block_rows, atoms):
    labels = sorted({row["label"] for row in block_rows})
    label_masks = {label: 0 for label in labels}
    for index, row in enumerate(block_rows):
        label_masks[row["label"]] |= 1 << index

    pure = defaultdict(dict)
    for atom in atoms:
        mask = 0
        for index, row in enumerate(block_rows):
            if feature_active(row["feature_vector"], atom):
                mask |= 1 << index
        if mask == 0:
            continue
        for label in labels:
            if mask & ~label_masks[label]:
                continue
            name = atom_name(atom)
            prior = pure[label].get(mask)
            if prior is None or len(name) < len(prior) or (len(name) == len(prior) and name < prior):
                pure[label][mask] = name
    return labels, label_masks, pure


def minimal_cover(options, target_mask):
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


def analyze_subset(subset, atoms):
    block_rows = subset_rows(subset)
    labels, label_masks, pure = pure_atoms(block_rows, atoms)
    cover_options = {}
    covers = {}
    for label in labels:
        cover_options[label] = sorted(
            [(name, mask) for mask, name in pure[label].items()],
            key=lambda item: (-item[1].bit_count(), len(item[0]), item[0]),
        )
        covers[label] = minimal_cover(cover_options[label], label_masks[label])

    all_positive_language = None
    all_positive_cost = None
    if all(covers[label] is not None for label in labels):
        all_positive_language = {label: covers[label] for label in labels}
        all_positive_cost = sum(len(covers[label]) for label in labels)

    residual_best = None
    for default_label in labels:
        others = [label for label in labels if label != default_label]
        if any(covers[label] is None for label in others):
            continue
        language = {label: covers[label] for label in others}
        cost = sum(len(formulas) for formulas in language.values())
        candidate = (cost, default_label, language)
        if residual_best is None or candidate[:2] < residual_best[:2]:
            residual_best = candidate

    return {
        "scores": list(subset),
        "row_count": len(block_rows),
        "label_count": len(labels),
        "labels": labels,
        "all_positive_possible": all_positive_language is not None,
        "all_positive_cost": all_positive_cost,
        "all_positive_language": all_positive_language,
        "residual_possible": residual_best is not None,
        "residual_cost": residual_best[0] if residual_best is not None else None,
        "default_label": residual_best[1] if residual_best is not None else None,
        "residual_language": residual_best[2] if residual_best is not None else None,
    }


def build_report():
    atoms = atom_candidates()
    analyses = []
    for size in range(1, len(NONTRIVIAL_SCORES) + 1):
        for subset in combinations(NONTRIVIAL_SCORES, size):
            analysis = analyze_subset(subset, atoms)
            if analysis["residual_possible"]:
                analyses.append(analysis)

    all_positive_feasible = [entry for entry in analyses if entry["all_positive_possible"]]
    feasible_by_size = Counter(len(entry["scores"]) for entry in analyses)
    all_positive_by_size = Counter(len(entry["scores"]) for entry in all_positive_feasible)
    maximal_subset_size = max(len(entry["scores"]) for entry in analyses)
    maximal_subsets = [
        entry
        for entry in analyses
        if len(entry["scores"]) == maximal_subset_size
    ]
    maximal_subsets.sort(key=lambda entry: (entry["residual_cost"], entry["row_count"], entry["scores"]))
    best_maximal = maximal_subsets[0]

    top_feasible = sorted(
        analyses,
        key=lambda entry: (-len(entry["scores"]), entry["residual_cost"], entry["row_count"], entry["scores"]),
    )

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "merged score-subunion search for exact score-free residual-default witness languages "
            "on the hard refill frontier, using the v42 feature surface and signed conjunction "
            "atoms of width 1 to 4"
        ),
        "holdout_domain": "the same 13 holdout fact states from v29 to v46",
        "survivor": "refill maximal score-free merged-subunion boundary",
        "feature_count": len(FEATURES),
        "feature_names": [feature_name(feature) for feature in FEATURES],
        "atom_count": len(atoms),
        "nontrivial_scores": list(NONTRIVIAL_SCORES),
        "feasible_subset_count": len(analyses),
        "feasible_subset_count_by_size": {str(size): feasible_by_size[size] for size in sorted(feasible_by_size)},
        "all_positive_feasible_subset_count": len(all_positive_feasible),
        "all_positive_feasible_subset_count_by_size": {
            str(size): all_positive_by_size[size] for size in sorted(all_positive_by_size)
        },
        "maximal_subset_size": maximal_subset_size,
        "maximal_subset_count": len(maximal_subsets),
        "maximal_subsets": maximal_subsets,
        "best_maximal_subset": best_maximal,
        "top_feasible_subsets": top_feasible[:10],
        "strongest_claim": (
            "In the searched score-free refill witness grammar, the full nontrivial score union "
            "and every merged subunion of size 4 or larger fail exact residual-default witnessing. "
            "The unique maximal exact merged subunion is (9,10,12), it still does not admit an "
            "exact all-positive presentation, and its best residual-default cost is 10. "
            "So the lab-followup earliest-error law from v90 does not transfer to refill as a whole-block "
            "score-free law. Refill only admits sparse exact merged islands in this grammar."
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
