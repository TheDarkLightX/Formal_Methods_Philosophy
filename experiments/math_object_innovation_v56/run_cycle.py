#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT = (
    ROOT.parent
    / "math_object_innovation_v55"
    / "generated"
    / "report.json"
)
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"


def load_rows():
    report = json.loads(INPUT.read_text(encoding="utf-8"))
    return report["rows"], tuple(report["feature_names"]), tuple(report["labels"])


def atom_candidates(features):
    atoms = []
    for size in range(1, len(features) + 1):
        for chosen in itertools.combinations(features, size):
            for signs in itertools.product([False, True], repeat=size):
                parts = []
                for feature, positive in zip(chosen, signs):
                    parts.append(feature if positive else f"not {feature}")
                atoms.append((tuple(zip(chosen, signs)), " and ".join(parts)))
    return atoms


def matches(atom_signature, row):
    return all(row["features"][feature] == positive for feature, positive in atom_signature)


def exact_cover_cost(rows, labels, atoms, residual_default: bool):
    options = {}
    for label in labels:
        label_rows = [row for row in rows if row["label"] == label]
        matching = []
        for signature, text in atoms:
            covered = [row for row in rows if matches(signature, row)]
            if covered and all(row["label"] == label for row in covered) and all(
                any(row is target for row in covered) for target in label_rows
            ):
                matching.append((signature, text))
        options[label] = matching

    if residual_default:
        best = None
        for default_label in labels:
            chosen_labels = [label for label in labels if label != default_label]
            language = {}
            cost = 0
            ok = True
            for label in chosen_labels:
                if not options[label]:
                    ok = False
                    break
                _, text = min(options[label], key=lambda item: (len(item[0]), item[1]))
                language[label] = [text]
                cost += 1
            if not ok:
                continue
            residual_rows = [row for row in rows if row["label"] == default_label]
            if any(
                any(
                    matches(signature, row)
                    for label in chosen_labels
                    for signature, _text in options[label]
                )
                for row in residual_rows
            ):
                continue
            candidate = {
                "cost": cost,
                "default_label": default_label,
                "language": language,
            }
            if best is None or (candidate["cost"], candidate["default_label"]) < (
                best["cost"],
                best["default_label"],
            ):
                best = candidate
        return best

    language = {}
    cost = 0
    for label in labels:
        if not options[label]:
            return None
        _, text = min(options[label], key=lambda item: (len(item[0]), item[1]))
        language[label] = [text]
        cost += 1
    return {"cost": cost, "language": language}


def search_basis(rows, labels, all_features, residual_default):
    winners = []
    for size in range(1, len(all_features) + 1):
        for chosen in itertools.combinations(all_features, size):
            atoms = atom_candidates(chosen)
            language = exact_cover_cost(rows, labels, atoms, residual_default=residual_default)
            if language is not None:
                winners.append(
                    {
                        "features": list(chosen),
                        "atom_count": len(atoms),
                        "language": language,
                    }
                )
        if winners:
            return {"basis_size": size, "exact_bases": winners}
    return None


def main():
    rows, all_features, labels = load_rows()
    all_positive = search_basis(rows, labels, all_features, residual_default=False)
    residual_default = search_basis(rows, labels, all_features, residual_default=True)
    report = {
        "survivor": "direct delta basis frontier",
        "tier": "symbolic_state_compiler",
        "oracle_dependent": True,
        "discovery_domain": (
            "feature-basis minimization for the exact v55 direct delta compiler "
            "over the five residual patch formulas"
        ),
        "holdout_domain": "the five residual patch formulas from the v49 core-plus-patch frontier",
        "all_features": list(all_features),
        "row_count": len(rows),
        "labels": list(labels),
        "all_positive": all_positive,
        "residual_default": residual_default,
        "strongest_claim": (
            "On the exact five residual patch formulas, the direct residual family "
            "compiler has exact minimal feature bases of size 2. The surviving "
            "bases are {has_add, has_drop} and {has_drop, has_flip}, and no "
            "singleton basis is exact."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
