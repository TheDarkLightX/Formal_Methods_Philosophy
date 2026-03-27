#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
V64 = ROOT.parent / "math_object_innovation_v64" / "generated" / "report.json"
OUT_DIR = ROOT / "generated"
OUT_PATH = OUT_DIR / "report.json"


def literal_text(feature: str, value: int) -> str:
    return feature if value else f"not {feature}"


def star_witness(signatures: dict[str, tuple[int, ...]]):
    labels = sorted(signatures)
    width = len(next(iter(signatures.values())))
    for default in labels:
        others = [label for label in labels if label != default]
        for first, second in itertools.permutations(others):
            witnesses = []
            ok = True
            for target, other in ((first, second), (second, first)):
                found = []
                for idx in range(width):
                    target_val = signatures[target][idx]
                    if (
                        signatures[default][idx] != target_val
                        and signatures[other][idx] != target_val
                    ):
                        found.append((idx, target_val))
                if not found:
                    ok = False
                    break
                witnesses.append((target, found))
            if ok:
                return {
                    "default_label": default,
                    "branches": [
                        {
                            "label": label,
                            "feature_index": sorted(
                                found,
                                key=lambda item: (0 if item[1] == 1 else 1, item[0]),
                            )[0][0],
                            "value": sorted(
                                found,
                                key=lambda item: (0 if item[1] == 1 else 1, item[0]),
                            )[0][1],
                            "all_private_literals": found,
                        }
                        for label, found in witnesses
                    ],
                }
    return None


def abstract_counts(max_width: int = 7):
    counts = []
    for width in range(2, max_width + 1):
        values = list(range(1 << width))
        total = 0
        exact = 0
        for triple in itertools.permutations(values, 3):
            total += 1
            signatures = {
                "A": tuple((triple[0] >> idx) & 1 for idx in reversed(range(width))),
                "B": tuple((triple[1] >> idx) & 1 for idx in reversed(range(width))),
                "C": tuple((triple[2] >> idx) & 1 for idx in reversed(range(width))),
            }
            if star_witness(signatures) is not None:
                exact += 1
        counts.append({"width": width, "exact": exact, "total": total})
    return counts


def domain_instances():
    v64 = json.loads(V64.read_text(encoding="utf-8"))
    domains = {}
    for domain_key in ("domain_a", "domain_b", "domain_c"):
        domain = v64[domain_key]
        features = domain["features"]
        signatures = {}
        for sig_text, labels in domain["realized_signatures"].items():
            assert len(labels) == 1
            signatures[labels[0]] = tuple(int(ch) for ch in sig_text)
        witness = star_witness(signatures)
        if witness is None:
            raise RuntimeError(f"no star witness for {domain_key}")
        compiler = {
            "default_label": witness["default_label"],
            "branches": [
                {
                    "label": branch["label"],
                    "atom": literal_text(features[branch["feature_index"]], branch["value"]),
                }
                for branch in witness["branches"]
            ],
        }
        domains[domain_key] = {
            "features": features,
            "realized_signatures": domain["realized_signatures"],
            "star_witness": witness,
            "compiler": compiler,
        }
    return domains


def main():
    counts = abstract_counts()
    instances = domain_instances()
    report = {
        "survivor": "three-signature support law frontier",
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": (
            "all labeled three-role support tables with one distinct realized "
            "signature per role, exhaustively for widths 2 through 7"
        ),
        "holdout_domain": "the three live support domains from v64",
        "abstract_counts": counts,
        "domain_instances": instances,
        "strongest_claim": (
            "Every labeled three-role support table with distinct realized "
            "signatures in widths 2 through 7 admits an exact residual-default "
            "compiler with two single literals. Equivalently, every such table "
            "admits a private-literal star witness. The v64 domains are exact "
            "instances of this bounded law."
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
