#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "generated" / "report.json"
REPO_ROOT = ROOT.parent.parent


def load_module(rel_path: str, name: str):
    path = REPO_ROOT / rel_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


V276 = load_module("experiments/math_object_innovation_v276/run_cycle.py", "v276_run_cycle")


def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def periodic_cos(t: int) -> int:
    return {0: 1, 1: 0, 2: -1, 3: 0}[t % 4]


def periodic_sin(t: int) -> int:
    return {0: 0, 1: 1, 2: 0, 3: -1}[t % 4]


def coeff_a(r: int) -> Fraction:
    return Fraction(14 * ((3 * (2**r)) - 1), 5)


def coeff_b(r: int) -> Fraction:
    return Fraction(7 * ((8 * (2**r)) - 1), 5)


def coeff_c(r: int) -> Fraction:
    return Fraction(14 * ((2**r) - 2), 5)


def td_bft_closed_form(r: int, t: int) -> int:
    value = (
        coeff_a(r) * fib(t)
        + coeff_b(r) * fib(t + 1)
        + coeff_c(r) * periodic_cos(t)
        + coeff_a(r) * periodic_sin(t)
    )
    assert value.denominator == 1
    return value.numerator


def td_star(r: int, t: int) -> int:
    return (2 ** (r + t + 5)) - 1


def delta_closed_form(r: int, t: int) -> int:
    return td_star(r, t) - td_bft_closed_form(r, t)


def characteristic_factorization_matches() -> bool:
    # (x^2 + 1)(x^2 - x - 1) = x^4 - x^3 - x - 1
    lhs = [1, 0, 1]
    rhs = [1, -1, -1]
    product = [0] * 5
    for i, a in enumerate(lhs):
        for j, b in enumerate(rhs):
            product[i + j] += a * b
    return product == [1, -1, 0, -1, -1]


def star_forcing_term(r: int, t: int) -> int:
    return td_star(r, t) - td_star(r, t - 1) - td_star(r, t - 3) - td_star(r, t - 4)


def build_report() -> dict[str, object]:
    rows = []
    all_bft_closed_forms_match = True
    all_delta_closed_forms_match = True
    all_star_forcing_terms_match = True
    all_delta_recurrences_explained = True

    for r in range(2, 8):
        bft_rows = []
        delta_rows = []
        for t in range(1, 11):
            actual_bft = V276.td_bft(r, t)
            expected_bft = td_bft_closed_form(r, t)
            bft_matches = actual_bft == expected_bft
            all_bft_closed_forms_match = all_bft_closed_forms_match and bft_matches
            bft_rows.append(
                {
                    "t": t,
                    "td": actual_bft,
                    "expected_td": expected_bft,
                    "matches": bft_matches,
                }
            )

            actual_delta = td_star(r, t) - actual_bft
            expected_delta = delta_closed_form(r, t)
            delta_matches = actual_delta == expected_delta
            all_delta_closed_forms_match = all_delta_closed_forms_match and delta_matches

            if t >= 5:
                forcing = star_forcing_term(r, t)
                expected_forcing = (5 * (2 ** (r + t + 1))) + 2
                forcing_matches = forcing == expected_forcing
                all_star_forcing_terms_match = all_star_forcing_terms_match and forcing_matches

                explained_delta = (
                    delta_closed_form(r, t - 1)
                    + delta_closed_form(r, t - 3)
                    + delta_closed_form(r, t - 4)
                    + expected_forcing
                )
                explained_matches = expected_delta == explained_delta
                all_delta_recurrences_explained = all_delta_recurrences_explained and explained_matches
            else:
                forcing = None
                expected_forcing = None
                forcing_matches = None
                explained_delta = None
                explained_matches = None

            delta_rows.append(
                {
                    "t": t,
                    "delta": actual_delta,
                    "expected_delta": expected_delta,
                    "delta_matches": delta_matches,
                    "forcing_term": forcing,
                    "expected_forcing_term": expected_forcing,
                    "forcing_matches": forcing_matches,
                    "explained_delta": explained_delta,
                    "explained_matches": explained_matches,
                }
            )

        rows.append(
            {
                "r": r,
                "coefficients": {
                    "A_r": str(coeff_a(r)),
                    "B_r": str(coeff_b(r)),
                    "C_r": str(coeff_c(r)),
                },
                "bft_rows": bft_rows,
                "delta_rows": delta_rows,
            }
        )

    return {
        "tier": "direct_amount_compiler",
        "claim_tier": "direct_amount_compiler",
        "oracle_dependent": False,
        "discovery_domain": {
            "family": "anomaly-route Fibonacci-periodic decomposition",
            "checked_r_values": list(range(2, 8)),
            "checked_t_values": list(range(1, 11)),
            "max_checked_n": 23,
        },
        "holdout_domain": None,
        "strongest_claim": (
            "On the checked bridge-fan-tail strip 2 <= r <= 7, 1 <= t <= 10, the feeder amount separates exactly into a Fibonacci term plus a period-4 term, and the whole route deficit equals the exponential star target minus that feeder term. The forcing term in v277 is exactly the exponential residue of the star sequence against the feeder recurrence."
        ),
        "theorem_checks": {
            "characteristic_factorization_matches": characteristic_factorization_matches(),
            "all_checked_bft_closed_forms_match": all_bft_closed_forms_match,
            "all_checked_delta_closed_forms_match": all_delta_closed_forms_match,
            "all_checked_star_forcing_terms_match": all_star_forcing_terms_match,
            "all_checked_delta_recurrences_explained": all_delta_recurrences_explained,
        },
        "rows": rows,
    }


def main() -> int:
    report = build_report()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
