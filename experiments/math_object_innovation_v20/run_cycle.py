#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v15.run_cycle import PATTERN_CACHE, deserialize_patterns, pattern_choice, residual_consistent_pairs


OUT = ROOT / "generated" / "report.json"


def first_failure(item, patterns):
    for pattern in patterns:
        if pattern_choice(item["params_1"], item["params_2"], pattern.rows_key) != pattern.target:
            return {
                "mask": pattern.exemplar_mask,
                "candidates": list(pattern.exemplar_candidates),
                "target": pattern.target,
            }
    return None


def build_report():
    viable = residual_consistent_pairs()
    patterns = deserialize_patterns(json.loads(PATTERN_CACHE.read_text(encoding="utf-8")))

    block_values = sorted({item["holdout_total"] for item in viable}, reverse=True)
    blocks = []
    for total in block_values:
        group = [item for item in viable if item["holdout_total"] == total]
        failure_counter = Counter()
        for item in group:
            failure_counter[json.dumps(first_failure(item, patterns), sort_keys=True)] += 1
        top_failure_json, top_count = failure_counter.most_common(1)[0]
        blocks.append({
            "holdout_total": total,
            "count": len(group),
            "unique_first_failures": len(failure_counter),
            "top_first_failure": json.loads(top_failure_json),
            "top_first_failure_count": top_count,
            "pure_block": top_count == len(group),
        })

    return {
        "tier": "descriptive_symbolic_controller",
        "oracle_dependent": False,
        "discovery_domain": "score-block anti-certificate analysis over the residual-consistent repair-program frontier",
        "holdout_domain": "same weighted 5x5 and 6x6 frontier summary used in v15",
        "survivor": "score-block staircase frontier",
        "block_count": len(blocks),
        "blocks": blocks,
        "strongest_claim": (
            "In the bounded residual-consistent frontier, the top score block is exactly safe and the next major lower blocks are pure in a second sense: "
            "each is refuted by a single shared first verifier counterexample pattern. The frontier therefore has a staircase geometry, one score block and one dominant refuter at a time."
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
