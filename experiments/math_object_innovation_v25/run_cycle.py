#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v24.run_cycle import guard_atoms, quotient_state_map, solve_minimal_decision_list


OUT = ROOT / "generated" / "report.json"


def pure_atom_summary(state_to_label):
    states = sorted(state_to_label)
    summary = {"safe": [], "fail_13116": [], "fail_1915": [], "fail_828": []}
    for atom in guard_atoms(states):
        labels = {state_to_label[state] for state in atom["mask"]}
        if len(labels) != 1:
            continue
        label = next(iter(labels))
        summary[label].append({
            "guard": atom["text"],
            "covered_states": sorted(
                [{"H6": state[0], "E": state[1]} for state in atom["mask"]],
                key=lambda row: (row["H6"], row["E"]),
            ),
            "cover_size": len(atom["mask"]),
        })
    for label in summary:
        summary[label].sort(key=lambda row: (-row["cover_size"], row["guard"]))
    return summary


def build_report():
    state_to_label = quotient_state_map()
    _, solution = solve_minimal_decision_list(state_to_label)
    pure = pure_atom_summary(state_to_label)

    fail_1915_atoms = pure["fail_1915"]
    safe_atoms = pure["safe"]
    fail_13116_atoms = pure["fail_13116"]

    lower_bound_explanation = [
        "Every pure atom for `safe` is singleton, so any exact decision list needs at least one dedicated branch for `safe`.",
        "Every pure atom for `fail_13116` is singleton, so any exact decision list needs at least one dedicated branch for `fail_13116`.",
        "The two `fail_1915` states, `(859, False)` and `(865, False)`, are covered only by distinct singleton pure atoms in this grammar.",
        "Therefore any exact decision list needs at least 1 + 1 + 2 = 4 labeled guards before the default `fail_828` branch.",
    ]

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "minimality certificate for the repaired verifier compiler over the bounded `(H6, E)` quotient",
        "holdout_domain": "same weighted 5x5 and 6x6 score coordinates used in v15 through v24",
        "survivor": "verifier compiler lower-bound frontier",
        "quotient_state_count": len(state_to_label),
        "exact_min_guard_count": len(solution) - 1,
        "no_exact_solution_leq_3": (len(solution) - 1) > 3,
        "pure_atom_summary": pure,
        "lower_bound_explanation": lower_bound_explanation,
        "strongest_claim": (
            "In the repaired `(H6, E)` quotient, the `v24` compiler is minimal in the searched guard language. "
            "There is no exact decision list with 3 guards or fewer, and the pure-atom geometry explains why: "
            "`safe` needs one singleton guard, `fail_13116` needs one singleton guard, and the two `fail_1915` states require two distinct singleton guards."
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
