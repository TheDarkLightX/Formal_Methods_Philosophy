#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "generated" / "report.json"
V53 = REPO_ROOT / "experiments" / "math_object_innovation_v53" / "generated" / "report.json"

FEATURES = ("has_add", "has_drop", "has_flip")


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
        name = FEATURES[index]
        parts.append(name if value else f"not {name}")
    return " and ".join(parts)


def atom_satisfies(feature_vector, atom):
    indexes, values = atom
    return all(feature_vector[index] == value for index, value in zip(indexes, values))


def minimal_cover(label_rows, atoms):
    labels = sorted({row["label"] for row in label_rows})
    label_masks = {label: 0 for label in labels}
    for index, row in enumerate(label_rows):
        label_masks[row["label"]] |= 1 << index

    pure_atoms = defaultdict(dict)
    for atom in atoms:
        mask = 0
        for index, row in enumerate(label_rows):
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

    def best_cover(label):
        options = sorted(
            [(name, mask) for mask, name in pure_atoms[label].items()],
            key=lambda item: (-item[1].bit_count(), len(item[0]), item[0]),
        )
        target_mask = label_masks[label]

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

    covers = {label: best_cover(label) for label in labels}

    all_positive = None
    if all(covers[label] is not None for label in labels):
        all_positive = {
            "cost": sum(len(covers[label]) for label in labels),
            "language": {label: covers[label] for label in labels},
        }

    best_residual = None
    for default_label in labels:
        others = [label for label in labels if label != default_label]
        if any(covers[label] is None for label in others):
            continue
        cost = sum(len(covers[label]) for label in others)
        candidate = {
            "cost": cost,
            "default_label": default_label,
            "language": {label: covers[label] for label in others},
        }
        if best_residual is None or (candidate["cost"], candidate["default_label"]) < (
            best_residual["cost"],
            best_residual["default_label"],
        ):
            best_residual = candidate

    return {"all_positive": all_positive, "residual_default": best_residual}


def build_rows():
    data = json.loads(V53.read_text(encoding="utf-8"))
    rows = []
    for fiber_index, fiber in enumerate(data["best_fibers"]):
        label = "+".join(fiber["family_subset"])
        for patch in fiber["patches"]:
            used = set(patch["used_families"])
            rows.append(
                {
                    "fiber_index": fiber_index,
                    "patch": patch["patch"],
                    "label": label,
                    "feature_vector": (
                        "ADD_BUNDLE" in used,
                        "DROP_BUNDLE" in used,
                        "FLIP_BUNDLE" in used,
                    ),
                }
            )
    return rows


def build_report():
    rows = build_rows()
    atoms = atom_candidates()
    summary = minimal_cover(rows, atoms)

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "certificate-language search over the exact v53 explanation-fiber labels, "
            "using patch-summary features has_add, has_drop, and has_flip"
        ),
        "holdout_domain": "the five residual patches labeled by the exact v53 fiber decomposition",
        "survivor": "fiber-certificate frontier",
        "feature_names": list(FEATURES),
        "atom_count": len(atoms),
        "row_count": len(rows),
        "labels": sorted({row["label"] for row in rows}),
        "all_positive": summary["all_positive"],
        "residual_default": summary["residual_default"],
        "strongest_claim": (
            "On the exact v53 fiber labels, the smallest exact all-positive "
            "certificate language has cost 3, while a positive-certificate plus "
            "residual-default language has cost 2 over the patch-summary features "
            "has_add, has_drop, and has_flip."
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
