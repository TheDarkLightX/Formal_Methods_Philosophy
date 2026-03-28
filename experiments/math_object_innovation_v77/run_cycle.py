#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
OUT = ROOT / "generated" / "report.json"

V24_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v24" / "generated" / "report.json"
V35_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v35" / "generated" / "report.json"
V36_REPORT = REPO_ROOT / "experiments" / "math_object_innovation_v36" / "generated" / "report.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def family_rows(v24: dict, v35: dict, v36: dict) -> list[dict]:
    decision_default = v24["decision_list"][-1].removeprefix("else ")
    decision_positive_labels = sorted(
        {
            step.split(" then ", 1)[1]
            for step in v24["decision_list"][:-1]
        }
    )
    return [
        {
            "family": "positive_atom_cover",
            "description_cost": v35["all_positive_cost"],
            "ordered": False,
            "invented_primitives": False,
            "default_label": None,
            "positive_labels": sorted(v35["positive_covers"]),
            "positive_label_count": len(v35["positive_covers"]),
            "positive_witness_count": v35["all_positive_cost"],
            "fully_positive": True,
            "source_cycle": "v35",
        },
        {
            "family": "mixed_atom_cover",
            "description_cost": v35["best_mixed_cost"],
            "ordered": False,
            "invented_primitives": False,
            "default_label": v35["best_default_label"],
            "positive_labels": sorted(v35["best_mixed_language"]),
            "positive_label_count": len(v35["best_mixed_language"]),
            "positive_witness_count": v35["best_mixed_cost"],
            "fully_positive": False,
            "source_cycle": "v35",
        },
        {
            "family": "positive_invented_cover",
            "description_cost": v36["best_two_primitives"]["total_cost"],
            "ordered": False,
            "invented_primitives": True,
            "default_label": None,
            "positive_labels": sorted(v36["best_two_primitives"]["covers"]),
            "positive_label_count": len(v36["best_two_primitives"]["covers"]),
            "positive_witness_count": v36["best_two_primitives"]["total_cost"],
            "fully_positive": True,
            "source_cycle": "v36",
        },
        {
            "family": "ordered_decision_list",
            "description_cost": v24["guard_count"],
            "ordered": True,
            "invented_primitives": False,
            "default_label": decision_default,
            "positive_labels": decision_positive_labels,
            "positive_label_count": len(decision_positive_labels),
            "positive_witness_count": len(v24["decision_list"]) - 1,
            "fully_positive": False,
            "source_cycle": "v24",
        },
    ]


def choose_min(rows: list[dict], predicate) -> dict:
    options = [row for row in rows if predicate(row)]
    options.sort(key=lambda row: (row["description_cost"], row["family"]))
    return options[0]


def build_report() -> dict:
    v24 = load(V24_REPORT)
    v35 = load(V35_REPORT)
    v36 = load(V36_REPORT)
    rows = family_rows(v24, v35, v36)

    semantic_optima = {
        "all_positive_unordered": choose_min(
            rows,
            lambda row: row["fully_positive"] and not row["ordered"],
        ),
        "residual_default_unordered": choose_min(
            rows,
            lambda row: row["default_label"] is not None and not row["ordered"],
        ),
        "ordered_exact_classifier": choose_min(
            rows,
            lambda row: row["ordered"],
        ),
    }

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "semantics-aware minimal witness-language comparison on the repaired 10-state `(H6, E)` verifier frontier",
        "holdout_domain": "the same repaired verifier quotient states used in v24, v35, and v36",
        "survivor": "minimal witness-language phase diagram",
        "frontier_state_count": len(v24["state_rows"]),
        "families": rows,
        "semantic_optima": semantic_optima,
        "strongest_claim": (
            "On the repaired verifier frontier, minimal exact language search does not return one universally best family. "
            "Instead the optimum depends on the local witness contract: the smallest exact all-positive unordered language "
            "is the invented positive-cover family from v36 with cost 4, the smallest exact unordered residual-default "
            "language is the mixed atom-cover family from v35 with cost 4, and the smallest exact ordered classifier is "
            "the decision-list compiler from v24 with 4 guards. This is bounded evidence for minimal witness-language "
            "discovery as a meta-loop above verifier compilation."
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
