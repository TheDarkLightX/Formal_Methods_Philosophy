#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
V53 = ROOT.parent / "math_object_innovation_v53" / "generated" / "report.json"
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


def load_rows():
    v53 = json.loads(V53.read_text(encoding="utf-8"))
    v59 = json.loads(V59.read_text(encoding="utf-8"))
    slot_a = set(v59["best_slot_compiler"]["left"])
    slot_b = set(v59["best_slot_compiler"]["right"])
    primitive = {}
    for fiber in v53["best_fibers"]:
        label = "+".join(fiber["family_subset"])
        for patch in fiber["patches"]:
            core = parse_formula(patch["core"])
            nxt = parse_formula(patch["patch"])
            for idx in sorted(set(core) | set(nxt)):
                feat = None
                kind = None
                if idx in nxt and idx not in core:
                    feat = f"add[{idx}]"
                    kind = "add"
                elif idx in core and idx not in nxt:
                    feat = f"drop[{idx}]"
                    kind = "drop"
                elif idx in core and idx in nxt and core[idx] != nxt[idx]:
                    feat = f"flip[{idx}]"
                    kind = "flip"
                if feat is None:
                    continue
                entry = primitive.setdefault(
                    feat,
                    {"kind": kind, "idx": idx, "labels": set(), "patch_count": 0},
                )
                entry["labels"].add(label)
                entry["patch_count"] += 1
    rows = []
    for feat, info in sorted(primitive.items()):
        rows.append(
            {
                "primitive": feat,
                "role": "slot_a" if feat in slot_a else "slot_b" if feat in slot_b else "other",
                "features": {
                    "is_add": info["kind"] == "add",
                    "is_drop": info["kind"] == "drop",
                    "is_flip": info["kind"] == "flip",
                    "has_AB": "ADD_BUNDLE" in info["labels"],
                    "has_MIX": "ADD_BUNDLE+DROP_BUNDLE" in info["labels"],
                    "has_FLIP": "FLIP_BUNDLE" in info["labels"],
                    "count_1": info["patch_count"] == 1,
                    "count_2": info["patch_count"] == 2,
                },
            }
        )
    return rows


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


def exact_cover(rows, labels, features, residual_default=False):
    atoms = atom_candidates(features)
    options = {}
    for label in labels:
        label_rows = [row for row in rows if row["role"] == label]
        matching = []
        for signature, text in atoms:
            covered = [row for row in rows if matches(signature, row)]
            if covered and all(row["role"] == label for row in covered) and all(
                any(row is target for row in covered) for target in label_rows
            ):
                matching.append((signature, text))
        options[label] = matching
    if residual_default:
        winners = []
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
            residual_rows = [row for row in rows if row["role"] == default_label]
            if any(
                any(
                    matches(signature, row)
                    for label in chosen
                    for signature, _ in options[label]
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
        winners.sort(key=lambda item: (item["cost"], item["default_label"], item["language"]))
        return winners
    language = {}
    cost = 0
    for label in labels:
        if not options[label]:
            return []
        _, text = min(options[label], key=lambda item: (len(item[0]), item[1]))
        language[label] = [text]
        cost += 1
    return [{"cost": cost, "language": language}]


def search_minimal_bases(rows):
    labels = sorted({row["role"] for row in rows})
    all_features = tuple(rows[0]["features"].keys())
    positive_winners = []
    residual_winners = []
    for subset_size in range(1, len(all_features) + 1):
        for feature_subset in itertools.combinations(all_features, subset_size):
            positive = exact_cover(rows, labels, feature_subset, residual_default=False)
            residual = exact_cover(rows, labels, feature_subset, residual_default=True)
            if positive:
                positive_winners.append(
                    {
                        "features": list(feature_subset),
                        "language": positive[0],
                    }
                )
            if residual:
                residual_winners.extend(
                    {
                        "features": list(feature_subset),
                        "language": item,
                    }
                    for item in residual
                )
        if positive_winners and residual_winners:
            return all_features, positive_winners, residual_winners
    raise RuntimeError("no exact semantic basis found")


def pick_support_profile_explanation(winners, residual_default=False):
    preferred = {"has_AB", "has_MIX"}
    for item in winners:
        if set(item["features"]) == preferred:
            if residual_default and item["language"]["default_label"] != "other":
                continue
            return item
    raise RuntimeError("preferred support-profile explanation missing")


def main():
    rows = load_rows()
    all_features, positive_winners, residual_winners = search_minimal_bases(rows)
    report = {
        "survivor": "semantic slot frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "minimal semantic explanation of the exact v59 slot roles over "
            "primitive metadata features"
        ),
        "holdout_domain": "the primitive-role dataset induced by the exact v59 slot compiler",
        "metadata_features": list(all_features),
        "row_count": len(rows),
        "positive_basis_size": len(positive_winners[0]["features"]),
        "residual_basis_size": len(residual_winners[0]["features"]),
        "positive_winner_count": len(positive_winners),
        "residual_winner_count": len(residual_winners),
        "preferred_support_profile_all_positive": pick_support_profile_explanation(
            positive_winners, residual_default=False
        ),
        "preferred_support_profile_residual_default": pick_support_profile_explanation(
            residual_winners, residual_default=True
        ),
        "strongest_claim": (
            "The exact v59 slot roles admit exact semantic explanations on a "
            "two-feature metadata basis. A natural support-profile explanation "
            "uses {has_AB, has_MIX}: slot_a iff has_AB, slot_b iff has_MIX and "
            "not has_AB, and other iff not has_MIX."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
