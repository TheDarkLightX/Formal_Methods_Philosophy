#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v15.run_cycle import PATTERN_CACHE, deserialize_patterns, pattern_choice, residual_consistent_pairs


OUT = ROOT / "generated" / "report.json"


def refuter_label(item, patterns):
    for pattern in patterns:
        if pattern_choice(item["params_1"], item["params_2"], pattern.rows_key) != pattern.target:
            return {
                "kind": "fail",
                "mask": pattern.exemplar_mask,
                "candidates": list(pattern.exemplar_candidates),
                "target": pattern.target,
            }
    return {"kind": "safe"}


def quotient_blocks(viable, patterns, key):
    buckets = defaultdict(list)
    for item in viable:
        buckets[item[key]].append(refuter_label(item, patterns))
    blocks = []
    exact = True
    for value in sorted(buckets, reverse=True):
        labels = {}
        for label in buckets[value]:
            encoded = json.dumps(label, sort_keys=True)
            labels[encoded] = label
        blocks.append({
            "value": value,
            "label_count": len(labels),
            "labels": list(labels.values()),
        })
        exact &= len(labels) == 1
    return exact, blocks


def build_report():
    viable = residual_consistent_pairs()
    patterns = deserialize_patterns(json.loads(PATTERN_CACHE.read_text(encoding="utf-8")))

    exact_total, blocks_total = quotient_blocks(viable, patterns, "holdout_total")
    exact_5, blocks_5 = quotient_blocks(viable, patterns, "holdout_5_hits")
    exact_6, blocks_6 = quotient_blocks(viable, patterns, "holdout_6_hits")

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "scalar quotient analysis of the first-refuter partition over the residual-consistent repair-program frontier",
        "holdout_domain": "same weighted 5x5 and 6x6 frontier summary used in v15",
        "survivor": "scalar refuter quotient frontier",
        "frontier_size": len(viable),
        "holdout_total_exact_refuter_quotient": exact_total,
        "holdout_5_exact_refuter_quotient": exact_5,
        "holdout_6_exact_refuter_quotient": exact_6,
        "holdout_total_blocks": blocks_total,
        "holdout_5_blocks": blocks_5,
        "holdout_6_blocks": blocks_6,
        "strongest_claim": (
            "Within the residual-consistent repair-program frontier, the full first-refuter label is an exact function of `holdout_total`, and also of `holdout_5_hits`, but not of `holdout_6_hits`. "
            "So the bounded refuter partition admits a one-dimensional quotient by at least two different scalar coordinates."
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
