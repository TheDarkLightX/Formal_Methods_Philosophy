#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
V49 = ROOT.parent / "math_object_innovation_v49" / "generated" / "report.json"
V53 = ROOT.parent / "math_object_innovation_v53" / "generated" / "report.json"
V55 = ROOT.parent / "math_object_innovation_v55" / "generated" / "report.json"
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
                "label": "CORE" if schema in core else "V41_PATCH" if schema in v41_only else "V46_PATCH",
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
                "label": "ADD_ANCHOR" if feat in slot_a else "MIX_DISCRIM" if feat in slot_b else "OTHER",
                "features": {
                    "has_AB": "ADD_BUNDLE" in info["labels"],
                    "has_MIX": "ADD_BUNDLE+DROP_BUNDLE" in info["labels"],
                },
            }
        )
    return rows


def domain_c_rows():
    v55 = json.loads(V55.read_text(encoding="utf-8"))
    return [
        {
            "item": f"{row['core']} -> {row['patch']}",
            "label": row["label"],
            "features": row["features"],
        }
        for row in v55["rows"]
    ]


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


def exact_label_atoms(rows, features):
    atoms = atom_candidates(features)
    labels = sorted({row["label"] for row in rows})
    exact = {}
    for label in labels:
        label_rows = [row for row in rows if row["label"] == label]
        exact[label] = []
        for signature, text in atoms:
            covered = [row for row in rows if matches(signature, row)]
            if covered and all(row["label"] == label for row in covered) and all(
                any(row is target for row in covered) for target in label_rows
            ):
                exact[label].append(
                    {
                        "signature": signature,
                        "text": text,
                        "literal_count": len(signature),
                    }
                )
    return exact


def exact_residual_default_compilers(rows):
    features = tuple(rows[0]["features"].keys())
    labels = sorted({row["label"] for row in rows})
    exact_atoms = exact_label_atoms(rows, features)
    winners = []
    for default_label in labels:
        chosen_labels = [label for label in labels if label != default_label]
        choices = [exact_atoms[label] for label in chosen_labels]
        for picked in itertools.product(*choices):
            language = {label: atom["text"] for label, atom in zip(chosen_labels, picked)}
            default_rows = [row for row in rows if row["label"] == default_label]
            if any(
                any(matches(atom["signature"], row) for atom in picked)
                for row in default_rows
            ):
                continue
            total_literal_cost = sum(atom["literal_count"] for atom in picked)
            winners.append(
                {
                    "default_label": default_label,
                    "branches": [
                        {
                            "label": label,
                            "atom": atom["text"],
                            "literal_count": atom["literal_count"],
                        }
                        for label, atom in zip(chosen_labels, picked)
                    ],
                    "branch_count": len(picked),
                    "total_literal_cost": total_literal_cost,
                }
            )
    return winners


def exact_one_branch_possible(rows):
    features = tuple(rows[0]["features"].keys())
    labels = sorted({row["label"] for row in rows})
    exact_atoms = exact_label_atoms(rows, features)
    for default_label in labels:
        for label in labels:
            if label == default_label:
                continue
            for atom in exact_atoms[label]:
                default_rows = [row for row in rows if row["label"] == default_label]
                third_rows = [row for row in rows if row["label"] not in {default_label, label}]
                if any(matches(atom["signature"], row) for row in default_rows):
                    continue
                if any(not matches(atom["signature"], row) for row in third_rows):
                    # the third label would merge into the default class, so a
                    # one-branch compiler would still be inexact
                    continue
                return True
    return False


def realized_signatures(rows):
    features = tuple(rows[0]["features"].keys())
    counts = {}
    for row in rows:
        signature = tuple(int(row["features"][feature]) for feature in features)
        counts.setdefault(signature, set()).add(row["label"])
    return {
        "".join(str(bit) for bit in signature): sorted(labels)
        for signature, labels in sorted(counts.items())
    }


def pick_preferred(winners):
    return min(
        winners,
        key=lambda item: (
            item["total_literal_cost"],
            item["branch_count"],
            item["default_label"],
            tuple(branch["label"] for branch in item["branches"]),
            tuple(branch["atom"] for branch in item["branches"]),
        ),
    )


def summarize_domain(rows):
    winners = exact_residual_default_compilers(rows)
    minimal_literal_cost = min(item["total_literal_cost"] for item in winners)
    minimal = [item for item in winners if item["total_literal_cost"] == minimal_literal_cost]
    return {
        "features": list(rows[0]["features"].keys()),
        "row_count": len(rows),
        "role_count": len({row["label"] for row in rows}),
        "realized_signatures": realized_signatures(rows),
        "single_branch_exact": exact_one_branch_possible(rows),
        "minimal_literal_cost": minimal_literal_cost,
        "minimal_winner_count": len(minimal),
        "preferred_compiler": pick_preferred(minimal),
    }


def main():
    domains = {
        "domain_a": summarize_domain(domain_a_rows()),
        "domain_b": summarize_domain(domain_b_rows()),
        "domain_c": summarize_domain(domain_c_rows()),
    }
    report = {
        "survivor": "support-literal compiler frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "minimal residual-default support compilers across three exact bounded "
            "frontiers"
        ),
        "holdout_domain": (
            "domain A: v49 core-plus-patch roles; domain B: v62 primitive roles; "
            "domain C: v55 direct delta roles"
        ),
        **domains,
        "common_result": {
            "domain_count": 3,
            "all_domains_single_branch_inexact": all(
                not item["single_branch_exact"] for item in domains.values()
            ),
            "all_domains_minimal_literal_cost": all(
                item["minimal_literal_cost"] == 2 for item in domains.values()
            ),
            "all_domains_two_branch_compilers": all(
                item["preferred_compiler"]["branch_count"] == 2 for item in domains.values()
            ),
        },
        "strongest_claim": (
            "All three bounded domains admit exact residual-default support "
            "compilers with two single-literal branches and total literal cost 2, "
            "while no exact single-branch support compiler exists on any domain. "
            "The support-signature line therefore upgrades from a transferred role "
            "law to a tiny reusable support-literal compiler family."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
