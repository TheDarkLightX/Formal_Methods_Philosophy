"""Exact certificate checker for the tutorial's three-note spotlight family.

The declared family is

    K(x) = a + (1/2) cos(x) + c cos(2x),
    a = 1/2 - c.

With y = cos(x), this becomes

    K_c(y) = (y + 1) (1/2 + 2 c (y - 1)),  -1 <= y <= 1.

Only rational arithmetic is used. This is a checker for this one family, not a
general trigonometric-positivity prover.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from fractions import Fraction

Polynomial = tuple[Fraction, ...]


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _polynomial_text(polynomial: Polynomial) -> list[str]:
    return [_fraction_text(value) for value in polynomial]


def _multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            result[left_degree + right_degree] += left_value * right_value
    return tuple(result)


def _evaluate(polynomial: Polynomial, point: Fraction) -> Fraction:
    result = Fraction(0)
    for coefficient in reversed(polynomial):
        result = result * point + coefficient
    return result


def _counterexample_for_invalid_c(c: Fraction) -> Fraction | None:
    """Return a rational y in (-1, 1) with K_c(y) < 0 when c > 1/8."""

    if c <= Fraction(1, 8):
        return None
    affine_root = Fraction(1) - Fraction(1, 4) / c
    return (Fraction(-1) + affine_root) / 2


def check_certificate(c: Fraction) -> dict[str, object]:
    """Check the factorization and positivity certificate exactly."""

    half = Fraction(1, 2)
    a = half - c
    b = half

    # K_c(y) = (1/2 - 2c) + (1/2)y + (2c)y^2.
    expanded: Polynomial = (half - 2 * c, half, 2 * c)
    first_factor: Polynomial = (Fraction(1), Fraction(1))
    second_factor: Polynomial = (half - 2 * c, 2 * c)
    factored = _multiply(first_factor, second_factor)

    endpoint_at_one = _evaluate(expanded, Fraction(1))
    endpoint_at_minus_one = _evaluate(expanded, Fraction(-1))

    affine_slope = 2 * c
    minimum_endpoint = Fraction(-1) if affine_slope >= 0 else Fraction(1)
    affine_minimum = _evaluate(second_factor, minimum_endpoint)
    positivity_certified = affine_minimum >= 0

    witness = _counterexample_for_invalid_c(c)
    witness_value = _evaluate(expanded, witness) if witness is not None else None

    checks = {
        "factorization_exact": expanded == factored,
        "K_at_y_1_is_1": endpoint_at_one == 1,
        "K_at_y_minus_1_is_0": endpoint_at_minus_one == 0,
        "affine_factor_nonnegative": positivity_certified,
        "classification_matches_c_le_1_over_8": (
            positivity_certified == (c <= Fraction(1, 8))
        ),
        "rejection_witness_is_negative": (
            witness is None
            or (Fraction(-1) < witness < Fraction(1) and witness_value < 0)
        ),
    }

    return {
        "schema": "fourier-three-note-spotlight-certificate-v1",
        "input": {"c": _fraction_text(c)},
        "derived_coefficients": {
            "a": _fraction_text(a),
            "b": _fraction_text(b),
            "c": _fraction_text(c),
        },
        "polynomial_in_y_low_to_high": _polynomial_text(expanded),
        "factorization": {
            "first_factor_low_to_high": _polynomial_text(first_factor),
            "second_factor_low_to_high": _polynomial_text(second_factor),
        },
        "affine_minimum": {
            "endpoint_y": _fraction_text(minimum_endpoint),
            "value": _fraction_text(affine_minimum),
        },
        "counterexample": (
            None
            if witness is None
            else {
                "y": _fraction_text(witness),
                "K_c_y": _fraction_text(witness_value),
            }
        ),
        "checks": checks,
        "accepted": all(checks.values()) and positivity_certified,
    }


def _parse_fraction(text: str) -> Fraction:
    try:
        return Fraction(text)
    except (ValueError, ZeroDivisionError) as error:
        raise argparse.ArgumentTypeError(f"invalid rational number: {text}") from error


def _run_self_test(cases: Iterable[tuple[Fraction, bool]]) -> list[dict[str, object]]:
    reports: list[dict[str, object]] = []
    for c, expected_acceptance in cases:
        report = check_certificate(c)
        if report["accepted"] != expected_acceptance:
            raise AssertionError(
                f"unexpected result for c={_fraction_text(c)}: "
                f"expected accepted={expected_acceptance}, got {report['accepted']}"
            )
        reports.append(report)

    rejected = next(report for report in reports if report["input"]["c"] == "1/7")
    if rejected["counterexample"] != {"y": "-7/8", "K_c_y": "-1/224"}:
        raise AssertionError("the frozen c=1/7 counterexample changed")
    return reports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--c",
        type=_parse_fraction,
        help="check one rational c, for example 1/8 or 1/7",
    )
    arguments = parser.parse_args()

    if arguments.c is not None:
        report = check_certificate(arguments.c)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["accepted"] else 1

    reports = _run_self_test(
        (
            (Fraction(1, 8), True),
            (Fraction(0), True),
            (Fraction(-2), True),
            (Fraction(1, 7), False),
        )
    )
    output = {
        "schema": "fourier-three-note-spotlight-self-test-v1",
        "result": "pass",
        "reports": reports,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
