#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
V53 = ROOT.parent / "math_object_innovation_v53" / "generated" / "report.json"
V57 = ROOT.parent / "math_object_innovation_v57" / "generated" / "report.json"
V59 = ROOT.parent / "math_object_innovation_v59" / "generated" / "report.json"
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


def load_inputs():
    v53 = json.loads(V53.read_text(encoding="utf-8"))
    v57 = json.loads(V57.read_text(encoding="utf-8"))
    v59 = json.loads(V59.read_text(encoding="utf-8"))
    primitive_features = tuple(v57["primitive_features"])
    target_pairs = {
        tuple(sorted(item["features"]))
        for item in v57["all_positive"]["exact_bases"]
    }
    rows = []
    for fiber in v53["best_fibers"]:
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
    return primitive_features, target_pairs, rows, v59["best_slot_compiler"]


def atom_candidates(features):
    atoms = []
    for size in range(1, len(features) + 1):
        for chosen in itertools.combinations(features, size):
            for signs in itertools.product([False, True], repeat=size):
                text = " and ".join(
                    feature if positive else f"not {feature}"
                    for feature, positive in zip(chosen, signs)
                )
                atoms.append((tuple(zip(chosen, signs)), text))
    return atoms


def matches(atom_signature, row):
    return all(row["features"][feature] == positive for feature, positive in atom_signature)


def exact_cover(rows, labels, residual_default=False):
    atoms = atom_candidates(("slot_a", "slot_b"))
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
            chosen = [label for label in labels if label != default_label]
            language = {}
            cost = 0
            ok = True
            for label in chosen:
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
                    for label in chosen
                    for signature, _ in options[label]
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


def slot_rows(rows, left, right):
    return [
        {
            "label": row["label"],
            "features": {
                "slot_a": any(row["features"][name] for name in left),
                "slot_b": any(row["features"][name] for name in right),
            },
        }
        for row in rows
    ]


def search_label_only(primitive_features, rows):
    labels = sorted({row["label"] for row in rows})
    survivors = []
    for mask in range(1, 1 << len(primitive_features)):
        left = [primitive_features[i] for i in range(len(primitive_features)) if mask & (1 << i)]
        remaining = [f for f in primitive_features if f not in left]
        if not remaining:
            continue
        for mask_r in range(1, 1 << len(remaining)):
            right = [remaining[i] for i in range(len(remaining)) if mask_r & (1 << i)]
            compiled_rows = slot_rows(rows, left, right)
            all_positive = exact_cover(compiled_rows, labels, residual_default=False)
            residual_default = exact_cover(compiled_rows, labels, residual_default=True)
            if all_positive is None or residual_default is None:
                continue
            survivors.append(
                {
                    "left": left,
                    "right": right,
                    "slot_cost": len(left) + len(right),
                    "all_positive": all_positive,
                    "residual_default": residual_default,
                }
            )
    survivors.sort(key=lambda item: (item["slot_cost"], item["left"], item["right"]))
    best_cost = survivors[0]["slot_cost"]
    best = [item for item in survivors if item["slot_cost"] == best_cost]
    return survivors, best_cost, best


def normalize_unordered(best_ordered):
    unordered = {}
    for item in best_ordered:
        left = tuple(item["left"])
        right = tuple(item["right"])
        key = tuple(sorted((left, right)))
        unordered[key] = {
            "slots": [list(key[0]), list(key[1])],
            "slot_cost": item["slot_cost"],
        }
    result = list(unordered.values())
    result.sort(key=lambda item: item["slots"])
    return result


def main():
    primitive_features, target_pairs, rows, basis_faithful = load_inputs()
    ordered_label_survivors, label_best_cost, label_best = search_label_only(primitive_features, rows)
    unordered_label_best = normalize_unordered(label_best)
    report = {
        "survivor": "quotient boundary frontier",
        "tier": "symbolic_state_compiler",
        "oracle_dependent": True,
        "discovery_domain": (
            "comparison between the smallest exact label-only slot quotient and "
            "the smallest exact basis-faithful slot quotient over the raw "
            "primitive edit features"
        ),
        "holdout_domain": "the five residual patch formulas from the v49 core-plus-patch frontier",
        "primitive_features": list(primitive_features),
        "target_pair_count": len(target_pairs),
        "label_only": {
            "survivor_count": len(ordered_label_survivors),
            "best_slot_cost": label_best_cost,
            "ordered_best_count": len(label_best),
            "unordered_best_count": len(unordered_label_best),
            "best_ordered": label_best,
            "best_unordered": unordered_label_best,
        },
        "basis_faithful": {
            "best_slot_cost": len(basis_faithful["left"]) + len(basis_faithful["right"]),
            "best_slot_compiler": basis_faithful,
        },
        "strongest_claim": (
            "On the exact five residual patch formulas, direct label compilation "
            "admits exact singleton-slot quotients of total slot cost 2, while "
            "the smallest exact basis-faithful slot quotient has slot cost 5. "
            "Predictive compression is strictly cheaper than structure-preserving "
            "compression on this bounded residual family."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
