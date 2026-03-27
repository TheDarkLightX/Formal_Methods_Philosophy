#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
INPUT = (
    ROOT.parent
    / "math_object_innovation_v53"
    / "generated"
    / "report.json"
)
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"

ATOM_FEATURES = ("has_add", "has_drop", "has_flip")


TOKEN_RE = re.compile(r"(not\s+)?err\[(\d+)\]")


def load_v53():
    return json.loads(INPUT.read_text(encoding="utf-8"))


def parse_formula(text: str) -> dict[int, bool]:
    normalized = text.replace("AND", "and")
    literals: dict[int, bool] = {}
    for raw in normalized.split("and"):
        token = raw.strip()
        if not token:
            continue
        match = TOKEN_RE.fullmatch(token)
        if not match:
            raise ValueError(f"unparsed token: {token!r}")
        neg, idx = match.groups()
        literals[int(idx)] = neg is None
    return literals


def derive_delta_features(core_text: str, patch_text: str) -> dict[str, bool]:
    core = parse_formula(core_text)
    patch = parse_formula(patch_text)
    added = []
    dropped = []
    flipped = []
    for idx in sorted(set(core) | set(patch)):
        in_core = idx in core
        in_patch = idx in patch
        if in_patch and not in_core:
            added.append(idx)
        elif in_core and not in_patch:
            dropped.append(idx)
        elif in_core and in_patch and core[idx] != patch[idx]:
            flipped.append(idx)
    return {
        "has_add": bool(added),
        "has_drop": bool(dropped),
        "has_flip": bool(flipped),
    }


def load_rows():
    report = load_v53()
    rows = []
    for fiber in report["best_fibers"]:
        label = "+".join(fiber["family_subset"])
        for patch in fiber["patches"]:
            features = derive_delta_features(patch["core"], patch["patch"])
            rows.append(
                {
                    "label": label,
                    "features": features,
                    "core": patch["core"],
                    "patch": patch["patch"],
                }
            )
    return rows


def atom_candidates():
    atoms = []
    for size in range(1, len(ATOM_FEATURES) + 1):
        for chosen in itertools.combinations(ATOM_FEATURES, size):
            for signs in itertools.product([False, True], repeat=size):
                parts = []
                for feature, positive in zip(chosen, signs):
                    parts.append(feature if positive else f"not {feature}")
                atoms.append((tuple(zip(chosen, signs)), " and ".join(parts)))
    return atoms


def matches(atom_signature, row):
    return all(row["features"][feature] == positive for feature, positive in atom_signature)


def exact_cover_cost(rows, labels, atoms, residual_default: bool):
    options: dict[str, list[tuple[tuple[tuple[str, bool], ...], str]]] = {}
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

    best = None
    if residual_default:
        for default_label in labels:
            chosen_labels = [label for label in labels if label != default_label]
            current = {}
            cost = 0
            ok = True
            for label in chosen_labels:
                if not options[label]:
                    ok = False
                    break
                _, text = min(options[label], key=lambda item: (len(item[0]), item[1]))
                current[label] = [text]
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
                "language": current,
            }
            if best is None or (candidate["cost"], candidate["default_label"]) < (
                best["cost"],
                best["default_label"],
            ):
                best = candidate
    else:
        current = {}
        cost = 0
        for label in labels:
            if not options[label]:
                return None
            _, text = min(options[label], key=lambda item: (len(item[0]), item[1]))
            current[label] = [text]
            cost += 1
        best = {"cost": cost, "language": current}
    return best


def main():
    rows = load_rows()
    labels = sorted({row["label"] for row in rows})
    atoms = atom_candidates()
    report = {
        "survivor": "direct delta-certificate frontier",
        "tier": "symbolic_state_compiler",
        "oracle_dependent": True,
        "discovery_domain": (
            "certificate-language search over the exact five residual patch formulas, "
            "using direct symbolic delta features has_add, has_drop, and has_flip "
            "derived from each core -> patch edit"
        ),
        "holdout_domain": (
            "the five residual patch formulas from the v49 core-plus-patch frontier"
        ),
        "feature_names": list(ATOM_FEATURES),
        "atom_count": len(atoms),
        "row_count": len(rows),
        "labels": labels,
        "rows": rows,
        "all_positive": exact_cover_cost(rows, labels, atoms, residual_default=False),
        "residual_default": exact_cover_cost(rows, labels, atoms, residual_default=True),
        "strongest_claim": (
            "On the exact five residual patch formulas, the family split "
            "FLIP_BUNDLE / ADD_BUNDLE / ADD_BUNDLE+DROP_BUNDLE can be compiled "
            "directly from symbolic patch-state delta features. The smallest exact "
            "all-positive language has cost 3, and a positive-certificate plus "
            "residual-default language has cost 2."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
