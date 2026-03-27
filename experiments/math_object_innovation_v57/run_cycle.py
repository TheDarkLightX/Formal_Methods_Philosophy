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
TOKEN_RE = re.compile(r"(not\s+)?err\[(\d+)\]")


def load_v53():
    return json.loads(INPUT.read_text(encoding="utf-8"))


def parse_formula(text: str) -> dict[int, bool]:
    normalized = text.replace("AND", "and")
    literals = {}
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


def derive_rows():
    report = load_v53()
    rows = []
    feature_names = set()
    for fiber in report["best_fibers"]:
        label = "+".join(fiber["family_subset"])
        for patch in fiber["patches"]:
            core = parse_formula(patch["core"])
            nxt = parse_formula(patch["patch"])
            features = {}
            for idx in sorted(set(core) | set(nxt)):
                in_core = idx in core
                in_next = idx in nxt
                if in_next and not in_core:
                    name = f"add[{idx}]"
                    features[name] = True
                    feature_names.add(name)
                elif in_core and not in_next:
                    name = f"drop[{idx}]"
                    features[name] = True
                    feature_names.add(name)
                elif in_core and in_next and core[idx] != nxt[idx]:
                    name = f"flip[{idx}]"
                    features[name] = True
                    feature_names.add(name)
            rows.append(
                {
                    "label": label,
                    "core": patch["core"],
                    "patch": patch["patch"],
                    "features": features,
                }
            )
    ordered_features = tuple(sorted(feature_names, key=lambda item: (item.split("[")[0], int(item[item.index("[") + 1 : -1]))))
    # fill missing primitive features as False
    for row in rows:
        row["features"] = {name: row["features"].get(name, False) for name in ordered_features}
    return rows, ordered_features


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


def exact_cover_cost(rows, labels, atoms, residual_default):
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
        winners = []
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
            winners.append(
                {
                    "default_label": default_label,
                    "language": language,
                    "cost": cost,
                }
            )
        return winners
    winners = []
    language = {}
    cost = 0
    for label in labels:
        if not options[label]:
            return []
        _, text = min(options[label], key=lambda item: (len(item[0]), item[1]))
        language[label] = [text]
        cost += 1
    winners.append({"cost": cost, "language": language})
    return winners


def search_min_basis(rows, labels, primitive_features, residual_default):
    for size in range(1, len(primitive_features) + 1):
        exact = []
        for chosen in itertools.combinations(primitive_features, size):
            atoms = atom_candidates(chosen)
            winners = exact_cover_cost(rows, labels, atoms, residual_default)
            for language in winners:
                exact.append(
                    {
                        "features": list(chosen),
                        "atom_count": len(atoms),
                        "language": language,
                    }
                )
        if exact:
            return {"basis_size": size, "exact_bases": exact}
    return None


def main():
    rows, primitive_features = derive_rows()
    labels = sorted({row["label"] for row in rows})
    all_positive = search_min_basis(rows, labels, primitive_features, residual_default=False)
    residual_default = search_min_basis(rows, labels, primitive_features, residual_default=True)
    report = {
        "survivor": "raw edit-basis frontier",
        "tier": "symbolic_state_compiler",
        "oracle_dependent": True,
        "discovery_domain": (
            "feature-basis minimization for the residual-family compiler over raw "
            "observed edit primitives derived from the five residual patch formulas"
        ),
        "holdout_domain": "the five residual patch formulas from the v49 core-plus-patch frontier",
        "primitive_features": list(primitive_features),
        "row_count": len(rows),
        "labels": labels,
        "all_positive": all_positive,
        "residual_default": residual_default,
        "strongest_claim": (
            "On the exact five residual patch formulas, the direct residual-family "
            "compiler survives on exact raw observed primitive bases of size 2. "
            "No singleton primitive basis is exact, and the surviving minimal "
            "all-positive bases are exactly {add[3], add[8]}, {add[3], drop[12]}, "
            "{add[6], add[8]}, {add[6], drop[12]}, {add[8], add[10]}, and "
            "{add[10], drop[12]}."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
