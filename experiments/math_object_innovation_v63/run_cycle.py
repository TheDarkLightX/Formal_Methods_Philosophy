#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
V49 = ROOT.parent / "math_object_innovation_v49" / "generated" / "report.json"
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


def domain_a_rows():
    v49 = json.loads(V49.read_text(encoding="utf-8"))
    core = set(v49["core_schemas"])
    v41_only = set(v49["v41_only_schemas"])
    v46_only = set(v49["v46_only_schemas"])
    rows = []
    for schema in sorted(core | v41_only | v46_only):
        rows.append(
            {
                "item": schema,
                "role": "CORE" if schema in core else "V41_PATCH" if schema in v41_only else "V46_PATCH",
                "features": {
                    "has_v41": schema in core or schema in v41_only,
                    "has_v46": schema in core or schema in v46_only,
                },
            }
        )
    return rows


def domain_b_rows():
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
                if idx in nxt and idx not in core:
                    feat = f"add[{idx}]"
                elif idx in core and idx not in nxt:
                    feat = f"drop[{idx}]"
                elif idx in core and idx in nxt and core[idx] != nxt[idx]:
                    feat = f"flip[{idx}]"
                if feat is None:
                    continue
                entry = primitive.setdefault(feat, {"labels": set()})
                entry["labels"].add(label)
    rows = []
    for feat, info in sorted(primitive.items()):
        rows.append(
            {
                "item": feat,
                "role": "ADD_ANCHOR" if feat in slot_a else "MIX_DISCRIM" if feat in slot_b else "OTHER",
                "features": {
                    "has_AB": "ADD_BUNDLE" in info["labels"],
                    "has_MIX": "ADD_BUNDLE+DROP_BUNDLE" in info["labels"],
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


def exact_role_language(rows):
    labels = sorted({row["role"] for row in rows})
    features = tuple(rows[0]["features"].keys())
    atoms = atom_candidates(features)
    language = {}
    for label in labels:
        label_rows = [row for row in rows if row["role"] == label]
        matches_for_label = []
        for signature, text in atoms:
            covered = [row for row in rows if matches(signature, row)]
            if covered and all(row["role"] == label for row in covered) and all(
                any(row is target for row in covered) for target in label_rows
            ):
                matches_for_label.append((signature, text))
        if not matches_for_label:
            raise RuntimeError(f"no exact language for {label}")
        _, text = min(matches_for_label, key=lambda item: (len(item[0]), item[1]))
        language[label] = [text]
    return {
        "features": list(features),
        "role_count": len(labels),
        "row_count": len(rows),
        "language": language,
    }


def main():
    a = exact_role_language(domain_a_rows())
    b = exact_role_language(domain_b_rows())
    report = {
        "survivor": "support-signature transfer frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "transfer of the support-signature role law across two exact bounded "
            "frontiers"
        ),
        "holdout_domain": "domain A: v49 core-plus-patch roles; domain B: v62 primitive roles",
        "domain_a": a,
        "domain_b": b,
        "strongest_claim": (
            "Both bounded domains compile exactly by two-bit support signatures. "
            "The v62 support-profile law is therefore not isolated, it transfers "
            "to a second exact frontier as a generic support-signature role law."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
