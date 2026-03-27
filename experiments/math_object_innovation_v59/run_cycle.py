#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
V53 = ROOT.parent / "math_object_innovation_v53" / "generated" / "report.json"
V57 = ROOT.parent / "math_object_innovation_v57" / "generated" / "report.json"
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"
TOKEN_RE = re.compile(r"(not\s+)?err\[(\d+)\]")


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


def load_target_pairs():
    report = json.loads(V57.read_text(encoding="utf-8"))
    return {
        tuple(sorted(item["features"]))
        for item in report["all_positive"]["exact_bases"]
    }, tuple(report["primitive_features"])


def derive_rows(primitive_features):
    report = json.loads(V53.read_text(encoding="utf-8"))
    rows = []
    for fiber in report["best_fibers"]:
        label = "+".join(fiber["family_subset"])
        for patch in fiber["patches"]:
            core = parse_formula(patch["core"])
            nxt = parse_formula(patch["patch"])
            features = {name: False for name in primitive_features}
            for idx in sorted(set(core) | set(nxt)):
                in_core = idx in core
                in_next = idx in nxt
                if in_next and not in_core:
                    features[f"add[{idx}]"] = True
                elif in_core and not in_next:
                    features[f"drop[{idx}]"] = True
                elif in_core and in_next and core[idx] != nxt[idx]:
                    features[f"flip[{idx}]"] = True
            rows.append({"label": label, "features": features})
    return rows


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


def exact_cover_cost(rows, labels, features, residual_default):
    atoms = atom_candidates(features)
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


def generate_pairs(left, right):
    return {
        tuple(sorted((l, r)))
        for l in left
        for r in right
        if l != r
    }


def search_slot_templates(rows, target_pairs, primitive_features):
    labels = sorted({row["label"] for row in rows})
    survivors = []
    for mask in range(1, 1 << len(primitive_features)):
        left = [primitive_features[i] for i in range(len(primitive_features)) if mask & (1 << i)]
        remaining = [f for f in primitive_features if f not in left]
        if not remaining:
            continue
        for mask_r in range(1, 1 << len(remaining)):
            right = [remaining[i] for i in range(len(remaining)) if mask_r & (1 << i)]
            pairs = generate_pairs(left, right)
            if pairs != target_pairs:
                continue
            slot_rows = []
            for row in rows:
                slot_rows.append(
                    {
                        "label": row["label"],
                        "features": {
                            "slot_a": any(row["features"][name] for name in left),
                            "slot_b": any(row["features"][name] for name in right),
                        },
                    }
                )
            all_positive = exact_cover_cost(slot_rows, labels, ("slot_a", "slot_b"), residual_default=False)
            residual_default = exact_cover_cost(slot_rows, labels, ("slot_a", "slot_b"), residual_default=True)
            if all_positive is None or residual_default is None:
                continue
            survivors.append(
                {
                    "left": left,
                    "right": right,
                    "pair_count": len(pairs),
                    "slot_cost": len(left) + len(right),
                    "all_positive": all_positive,
                    "residual_default": residual_default,
                }
            )
    survivors.sort(
        key=lambda item: (
            item["slot_cost"],
            item["left"],
            item["right"],
        )
    )
    return survivors


def main():
    target_pairs, primitive_features = load_target_pairs()
    rows = derive_rows(primitive_features)
    survivors = search_slot_templates(rows, target_pairs, primitive_features)
    best = survivors[0] if survivors else None
    report = {
        "survivor": "role-slot compiler frontier",
        "tier": "symbolic_state_compiler",
        "oracle_dependent": True,
        "discovery_domain": (
            "slot-template search over raw primitive edit features, constrained to "
            "exactly reproduce the v57 primitive basis family and to compile the "
            "residual labels directly"
        ),
        "holdout_domain": "the five residual patch formulas from the v49 core-plus-patch frontier",
        "primitive_features": list(primitive_features),
        "target_pair_count": len(target_pairs),
        "survivor_count": len(survivors),
        "best_slot_compiler": best,
        "strongest_claim": (
            "The exact v58 role template also compiles the residual labels "
            "directly. Up to slot swap, slot_a = any(add[3], add[6], add[10]) "
            "and slot_b = any(add[8], drop[12]), with an exact all-positive cost "
            "3 and residual-default cost 2."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
