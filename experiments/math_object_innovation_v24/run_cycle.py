#!/usr/bin/env python3
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.math_object_innovation_v15.run_cycle import (
    PATTERN_CACHE,
    deserialize_patterns,
    pattern_choice,
    residual_consistent_pairs,
)


OUT = ROOT / "generated" / "report.json"

LABEL_NAME = {
    ("safe",): "safe",
    ("fail", 13116, (0, 1, 2, 3), 0): "fail_13116",
    ("fail", 1915, (0, 1, 2), 2): "fail_1915",
    ("fail", 828, (0, 1, 2, 3), 0): "fail_828",
}


def refuter_label(item, patterns):
    for pattern in patterns:
        if pattern_choice(item["params_1"], item["params_2"], pattern.rows_key) != pattern.target:
            return ("fail", pattern.exemplar_mask, tuple(pattern.exemplar_candidates), pattern.target)
    return ("safe",)


def quotient_state_map():
    patterns = deserialize_patterns(json.loads(PATTERN_CACHE.read_text(encoding="utf-8")))
    mapping = {}
    for item in residual_consistent_pairs():
        state = (item["holdout_6_hits"], item["params_1"][4] == item["params_2"][4])
        label = LABEL_NAME[refuter_label(item, patterns)]
        if state in mapping and mapping[state] != label:
            raise ValueError(f"mixed quotient state {state}: {mapping[state]} vs {label}")
        mapping[state] = label
    return mapping


def guard_atoms(states):
    atoms = []
    h6_values = sorted({state[0] for state in states}, reverse=True)
    for c in h6_values:
        atoms.append({"text": f"H6 > {c}", "mask": {state for state in states if state[0] > c}, "cost": (0, c)})
        atoms.append({"text": f"H6 = {c}", "mask": {state for state in states if state[0] == c}, "cost": (1, c)})
    for b in (False, True):
        atoms.append({"text": f"E = {b}", "mask": {state for state in states if state[1] == b}, "cost": (2, int(b))})
    for c in h6_values:
        for b in (False, True):
            atoms.append({
                "text": f"H6 = {c} and E = {b}",
                "mask": {state for state in states if state[0] == c and state[1] == b},
                "cost": (3, c, int(b)),
            })

    best = {}
    for atom in atoms:
        if not atom["mask"] or len(atom["mask"]) == len(states):
            continue
        key = frozenset(atom["mask"])
        if key not in best or atom["cost"] < best[key]["cost"]:
            best[key] = atom
    return list(best.values())


def solve_minimal_decision_list(state_to_label):
    states = sorted(state_to_label)
    index = {state: i for i, state in enumerate(states)}
    labels = {index[state]: state_to_label[state] for state in states}
    full = (1 << len(states)) - 1

    pure_atoms = []
    for atom in guard_atoms(states):
        mask_bits = 0
        atom_labels = set()
        for state in atom["mask"]:
            i = index[state]
            mask_bits |= 1 << i
            atom_labels.add(labels[i])
        if len(atom_labels) == 1:
            pure_atoms.append({
                "text": atom["text"],
                "mask_bits": mask_bits,
                "label": next(iter(atom_labels)),
            })

    @lru_cache(maxsize=None)
    def best_for(remaining_bits):
        if remaining_bits == 0:
            return ()
        remaining_labels = {labels[i] for i in range(len(states)) if remaining_bits & (1 << i)}
        if len(remaining_labels) == 1:
            return ({"text": "DEFAULT", "label": next(iter(remaining_labels)), "mask_bits": remaining_bits},)

        best = None
        best_cost = None
        for atom in pure_atoms:
            take = remaining_bits & atom["mask_bits"]
            if take == 0 or take == remaining_bits:
                continue
            tail = best_for(remaining_bits & ~take)
            if tail is None:
                continue
            candidate = ({"text": atom["text"], "label": atom["label"], "mask_bits": take},) + tail
            cost = (
                len(candidate) - 1,
                [step["text"] for step in candidate[:-1]],
                candidate[-1]["label"],
            )
            if best is None or cost < best_cost:
                best = candidate
                best_cost = cost
        return best

    solution = best_for(full)
    if solution is None:
        raise ValueError("no exact decision list found")
    return states, solution


def build_report():
    state_to_label = quotient_state_map()
    states, solution = solve_minimal_decision_list(state_to_label)

    decision_list = [f"if {step['text']} then {step['label']}" for step in solution[:-1]]
    decision_list.append(f"else {solution[-1]['label']}")

    state_rows = []
    for state in states:
        state_rows.append({
            "H6": state[0],
            "E": state[1],
            "label": state_to_label[state],
        })

    return {
        "tier": "descriptive_oracle",
        "oracle_dependent": True,
        "discovery_domain": "minimal exact decision-list compilation of the repaired `(holdout_6_hits, num_eq[4])` verifier quotient",
        "holdout_domain": "same weighted 5x5 and 6x6 score coordinates used in v15 through v23",
        "survivor": "repaired verifier compiler frontier",
        "frontier_size": 7104,
        "quotient_state_count": len(states),
        "state_rows": state_rows,
        "guard_count": len(solution) - 1,
        "decision_list": decision_list,
        "logic_formulas": [
            "Let E(x) := p1_4(x) = p2_4(x).",
            "Safe(x) ↔ H6(x) = 876",
            "Fail_13116(x) ↔ H6(x) = 869",
            "Fail_1915(x) ↔ H6(x) = 865 ∨ (H6(x) = 859 ∧ ¬E(x))",
            "Fail_828(x) ↔ ¬Safe(x) ∧ ¬Fail_13116(x) ∧ ¬Fail_1915(x)",
        ],
        "strongest_claim": (
            "After repairing the `holdout_6_hits` quotient with `E(x) := p1_4(x) = p2_4(x)`, the verifier side compiles to a minimal exact bounded decision list with 4 guards: "
            "`H6 = 859 ∧ E = False`, `H6 = 865`, `H6 = 869`, and `H6 > 869`, with default `fail_828`. "
            "So the repaired quotient is not only exact, it is compiler-small."
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
