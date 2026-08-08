#!/usr/bin/env python3
"""Independently enumerate the Boolean witnesses used in the Tau peer review."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections.abc import Callable, Iterable


Valuation = dict[str, bool]
Formula = Callable[[Valuation], bool]


def valuations(names: Iterable[str]) -> list[Valuation]:
    ordered = tuple(names)
    return [
        dict(zip(ordered, values, strict=True))
        for values in itertools.product((False, True), repeat=len(ordered))
    ]


def satisfiable(formulas: Iterable[Formula], names: Iterable[str]) -> bool:
    selected = tuple(formulas)
    return any(all(formula(v) for formula in selected) for v in valuations(names))


def equivalent(left: Formula, right: Formula, names: Iterable[str]) -> bool:
    return all(left(v) == right(v) for v in valuations(names))


def minimal_unsatisfiable(formulas: tuple[Formula, ...], names: tuple[str, ...]) -> bool:
    if satisfiable(formulas, names):
        return False
    return all(
        satisfiable(formulas[:index] + formulas[index + 1 :], names)
        for index in range(len(formulas))
    )


def check() -> dict[str, object]:
    p = lambda v: v["x"] or v["y"]
    q = lambda v: v["x"] or not v["y"]
    r = lambda v: not v["x"]

    higher_order = {
        "pq_satisfiable": satisfiable((p, q), ("x", "y")),
        "pr_satisfiable": satisfiable((p, r), ("x", "y")),
        "qr_satisfiable": satisfiable((q, r), ("x", "y")),
        "pqr_unsatisfiable": not satisfiable((p, q, r), ("x", "y")),
    }

    a = lambda v: v["x"]
    b = lambda v: (not v["x"]) or v["y"]
    c = lambda v: not v["y"]
    d = lambda v: (not v["x"]) or v["z"]
    e = lambda v: not v["z"]

    overlapping_cores = {
        "abc_minimal_unsatisfiable": minimal_unsatisfiable(
            (a, b, c), ("x", "y", "z")
        ),
        "ade_minimal_unsatisfiable": minimal_unsatisfiable(
            (a, d, e), ("x", "y", "z")
        ),
        "shared_member": "A",
    }

    left = lambda v: (not v["floor"]) and v["right"] and v["replacement"]
    right = lambda v: (not v["floor"]) and v["replacement"]
    order_dependence = {
        "left_satisfiable": satisfiable(
            (left,), ("floor", "right", "replacement")
        ),
        "right_satisfiable": satisfiable(
            (right,), ("floor", "right", "replacement")
        ),
        "outcomes_unequal": not equivalent(
            left, right, ("floor", "right", "replacement")
        ),
    }

    aci = {
        "commutative_and_associative_instance": all(
            ((c_value and a_value) and b_value)
            == ((c_value and b_value) and a_value)
            for c_value, a_value, b_value in itertools.product(
                (False, True), repeat=3
            )
        ),
        "idempotent_instance": all(
            ((c_value and a_value) and a_value) == (c_value and a_value)
            for c_value, a_value in itertools.product((False, True), repeat=2)
        ),
    }

    boolean_checks = [
        *higher_order.values(),
        overlapping_cores["abc_minimal_unsatisfiable"],
        overlapping_cores["ade_minimal_unsatisfiable"],
        *order_dependence.values(),
        *aci.values(),
    ]
    passed = all(value is True for value in boolean_checks)

    return {
        "schema": "formal-philosophy.consensus-review-boolean-witnesses.v1",
        "higher_order_conflict": higher_order,
        "overlapping_minimal_cores": overlapping_cores,
        "satisfiable_order_dependence": order_dependence,
        "conjunction_aci": aci,
        "valuations_exhaustively_enumerated": {
            "two_variables": 4,
            "three_variables": 8,
        },
        "passed": passed,
        "claim_boundary": (
            "This checker independently validates the finite Boolean witnesses. "
            "It does not validate Tau implementation semantics or a network protocol."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    receipt = check()
    if args.json:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    else:
        print(
            "Consensus-decomposition Boolean witnesses: "
            f"{'PASS' if receipt['passed'] else 'FAIL'}"
        )
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
