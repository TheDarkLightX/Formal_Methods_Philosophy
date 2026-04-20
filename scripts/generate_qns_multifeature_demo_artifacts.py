#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPEC_REL = "examples/tau/qns_multifeature_decision_surface_v1.tau"
DEFAULT_OUT = ROOT / "assets" / "data" / "qns_multifeature_demo_traces.json"
MASK = 0xFF

sys.path.insert(0, str(ROOT / "scripts"))
from generate_qns_candidate_ba_artifacts import (  # noqa: E402
    CANDIDATES,
    SCENARIOS,
    qns_const,
    qns_not,
    run_tau_qns_normalize,
    _load_tau_runner,
)


@dataclass(frozen=True)
class DemoCase:
    name: str
    prompt: str
    allow_mask: int
    review_mask: int
    hard_mask: int
    old_memory: int
    auto_add: int
    review_add: int
    reject_add: int


KEYWORD_CASES = (
    DemoCase(
        name="post_agi_tokenomics",
        prompt="post AGI tokenomics value shock reward contributors but reject extraction",
        allow_mask=0xDF,
        review_mask=0xCA,
        hard_mask=0x20,
        old_memory=0x01,
        auto_add=0x10,
        review_add=0x82,
        reject_add=0x20,
    ),
    DemoCase(
        name="dex_oracle_incident",
        prompt="oracle anomaly detected freeze governance and quarantine incident actions",
        allow_mask=0xCE,
        review_mask=0xCA,
        hard_mask=0x21,
        old_memory=0x04,
        auto_add=0x10,
        review_add=0xC8,
        reject_add=0x01,
    ),
    DemoCase(
        name="collateral_admission",
        prompt="new collateral token admission with sanction risk and manual review",
        allow_mask=0xCE,
        review_mask=0xCA,
        hard_mask=0x21,
        old_memory=0x10,
        auto_add=0x04,
        review_add=0x8A,
        reject_add=0x01,
    ),
)


KEYWORDS: tuple[tuple[str, int, float], ...] = (
    ("loan", 0, 0.14),
    ("review", 1, 0.26),
    ("sanction", 2, 0.20),
    ("quarantine", 3, 0.33),
    ("reward", 4, 0.30),
    ("extraction", 5, 0.34),
    ("extractor", 5, 0.34),
    ("freeze", 6, 0.22),
    ("governance", 6, 0.22),
    ("council", 7, 0.14),
    ("agi", 7, 0.09),
    ("oracle", 3, 0.33),
    ("collateral", 0, 0.19),
    ("token", 1, 0.26),
)


def names_for_mask(mask: int) -> list[str]:
    return [candidate.name for candidate in CANDIDATES if mask & candidate.mask]


def toy_micro_proposer(prompt: str) -> tuple[int, dict[str, float]]:
    text = prompt.lower()
    scores: dict[int, float] = {}
    for word, bit, score in KEYWORDS:
        if word in text:
            scores[bit] = max(scores.get(bit, 0.0), score)
    if not scores:
        scores[7] = 0.1
    mask = 0
    named_scores = {}
    for candidate in CANDIDATES:
        score = scores.get(candidate.bit, 0.0)
        if score > 0:
            mask |= candidate.mask
            named_scores[candidate.name] = score
    return mask, named_scores


def host_not(mask: int) -> int:
    return MASK ^ mask


def host_revise(old: int, guard: int, replacement: int) -> int:
    return (guard & replacement) | (host_not(guard) & old)


def host_outputs(case: DemoCase, proposed: int) -> dict[str, int]:
    u = MASK
    p = u & proposed
    eligible = p & case.allow_mask & host_not(case.hard_mask)
    auto = eligible & host_not(case.review_mask)
    review = eligible & case.review_mask
    reject = p & (host_not(case.allow_mask) | case.hard_mask)
    partition = auto | review | reject
    unsafe = auto & case.hard_mask
    revised = host_revise(
        host_revise(
            host_revise(case.old_memory, reject, case.reject_add),
            review,
            case.review_add,
        ),
        auto,
        case.auto_add,
    )
    revised_twice = host_revise(
        host_revise(host_revise(revised, reject, case.reject_add), review, case.review_add),
        auto,
        case.auto_add,
    )
    return {
        "proposed": p,
        "eligible": eligible,
        "auto": auto,
        "review": review,
        "reject": reject,
        "partition": partition,
        "unsafe": unsafe,
        "revised": revised,
        "revised_twice": revised_twice,
    }


def route_tau_exprs(case: DemoCase, proposed: int) -> dict[str, str]:
    u = qns_const(MASK)
    p = qns_const(proposed)
    a = qns_const(case.allow_mask)
    r = qns_const(case.review_mask)
    h = qns_const(case.hard_mask)
    proposed_expr = f"(({u}) & ({p}))"
    eligible = f"(({proposed_expr}) & ({a}) & ({qns_not(h)}))"
    auto = f"(({eligible}) & ({qns_not(r)}))"
    review = f"(({eligible}) & ({r}))"
    reject = f"(({proposed_expr}) & (({qns_not(a)}) | ({h})))"
    partition = f"(({auto}) | ({review}) | ({reject}))"
    unsafe = f"(({auto}) & ({h}))"
    return {
        "proposed": proposed_expr,
        "eligible": eligible,
        "auto": auto,
        "review": review,
        "reject": reject,
        "partition": partition,
        "unsafe": unsafe,
    }


def revision_tau_exprs(case: DemoCase, routed: dict[str, int]) -> dict[str, str]:
    old = qns_const(case.old_memory)
    auto = qns_const(routed["auto"])
    review = qns_const(routed["review"])
    reject = qns_const(routed["reject"])
    auto_add = qns_const(case.auto_add)
    review_add = qns_const(case.review_add)
    reject_add = qns_const(case.reject_add)
    revise_reject = f"((({reject}) & ({reject_add})) | ({qns_not(reject)} & ({old})))"
    revise_review = f"((({review}) & ({review_add})) | ({qns_not(review)} & ({revise_reject})))"
    revised = f"((({auto}) & ({auto_add})) | ({qns_not(auto)} & ({revise_review})))"
    revised_const = qns_const(routed["revised"])
    revise_reject_2 = f"((({reject}) & ({reject_add})) | ({qns_not(reject)} & ({revised_const})))"
    revise_review_2 = f"((({review}) & ({review_add})) | ({qns_not(review)} & ({revise_reject_2})))"
    revised_twice = f"((({auto}) & ({auto_add})) | ({qns_not(auto)} & ({revise_review_2})))"
    return {
        "revised": revised,
        "revised_twice": revised_twice,
    }


def monolithic_revision_expr(case: DemoCase, proposed: int) -> str:
    exprs = route_tau_exprs(case, proposed)
    old = qns_const(case.old_memory)
    auto = exprs["auto"]
    review = exprs["review"]
    reject = exprs["reject"]
    auto_add = qns_const(case.auto_add)
    review_add = qns_const(case.review_add)
    reject_add = qns_const(case.reject_add)
    revise_reject = f"((({reject}) & ({reject_add})) | ({qns_not(reject)} & ({old})))"
    revise_review = f"((({review}) & ({review_add})) | ({qns_not(review)} & ({revise_reject})))"
    return f"((({auto}) & ({auto_add})) | ({qns_not(auto)} & ({revise_review})))"


def run_tau_measured(tau_bin: str, expr: str, timeout_s: float) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        value, raw = run_tau_qns_normalize(tau_bin, expr, timeout_s=timeout_s)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
        return {
            "ok": True,
            "timeout": False,
            "value": value,
            "elapsed_ms": elapsed_ms,
            "raw": raw,
        }
    except subprocess.TimeoutExpired:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
        return {
            "ok": False,
            "timeout": True,
            "value": None,
            "elapsed_ms": elapsed_ms,
            "raw": "",
        }


def run_case(tau_bin: str, case: DemoCase, timeout_s: float) -> dict[str, Any]:
    proposed, scores = toy_micro_proposer(case.prompt)
    expected = host_outputs(case, proposed)
    exprs = route_tau_exprs(case, proposed)
    actual: dict[str, int] = {}
    tau_outputs: dict[str, str] = {}
    fast_measurements: dict[str, dict[str, Any]] = {}
    for name, expr in exprs.items():
        measured = run_tau_measured(tau_bin, expr, timeout_s)
        if not measured["ok"]:
            raise RuntimeError(f"fast Tau expression {name} failed or timed out")
        actual[name] = int(measured["value"])
        tau_outputs[name] = str(measured["raw"])
        fast_measurements[name] = {k: v for k, v in measured.items() if k != "raw"}
    revision_exprs = revision_tau_exprs(case, {**expected, **actual})
    for name, expr in revision_exprs.items():
        measured = run_tau_measured(tau_bin, expr, timeout_s)
        if not measured["ok"]:
            raise RuntimeError(f"fast Tau expression {name} failed or timed out")
        actual[name] = int(measured["value"])
        tau_outputs[name] = str(measured["raw"])
        fast_measurements[name] = {k: v for k, v in measured.items() if k != "raw"}
    mismatches = {
        key: {"expected": expected[key], "actual": actual[key]}
        for key in expected
        if expected[key] != actual.get(key)
    }
    return {
        "name": case.name,
        "prompt": case.prompt,
        "toy_micro_proposer": {
            "proposed_mask": proposed,
            "scores": scores,
            "proposed_candidates": names_for_mask(proposed),
        },
        "input_masks": {
            "universe": MASK,
            "allow": case.allow_mask,
            "review": case.review_mask,
            "hard_reject": case.hard_mask,
            "old_memory": case.old_memory,
            "auto_add": case.auto_add,
            "review_add": case.review_add,
            "reject_add": case.reject_add,
        },
        "expected": expected,
        "actual": actual,
        "sets": {
            "auto": names_for_mask(actual["auto"]),
            "review": names_for_mask(actual["review"]),
            "reject": names_for_mask(actual["reject"]),
            "revised_memory": names_for_mask(actual["revised"]),
        },
        "checks": {
            "tau_matches_host": not mismatches,
            "partition_matches_proposed": actual["partition"] == actual["proposed"],
            "unsafe_leak_zero": actual["unsafe"] == 0,
            "revision_idempotent": actual["revised_twice"] == actual["revised"],
        },
        "fast_staged_measurements": fast_measurements,
        "mismatches": mismatches,
        "tau_outputs": tau_outputs,
    }


def run_slow_monolithic(tau_bin: str, case: DemoCase, timeout_s: float) -> dict[str, Any]:
    proposed, _scores = toy_micro_proposer(case.prompt)
    expected = host_outputs(case, proposed)
    expr = monolithic_revision_expr(case, proposed)
    measured = run_tau_measured(tau_bin, expr, timeout_s)
    return {
        "name": case.name,
        "mode": "slow_monolithic_fully_expanded_revision",
        "expression_bytes": len(expr.encode("utf-8")),
        "timeout_s": timeout_s,
        "expected_revised": expected["revised"],
        "result": {k: v for k, v in measured.items() if k != "raw"},
        "matches_expected": measured.get("value") == expected["revised"],
        "purpose": (
            "This lane intentionally sends the fully expanded revision expression "
            "to Tau. It is a performance-boundary demo, not the recommended path."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate qNS multi-feature Tau demo traces.")
    parser.add_argument("--tau-bin", type=str, default=None)
    parser.add_argument("--timeout-s", type=float, default=10.0)
    parser.add_argument("--slow-timeout-s", type=float, default=5.0)
    parser.add_argument("--skip-slow", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    tau_bin = args.tau_bin
    if tau_bin is None:
        tau_bin = _load_tau_runner()()
    rows = [run_case(tau_bin, case, args.timeout_s) for case in KEYWORD_CASES]
    slow_monolithic = None
    if not args.skip_slow:
        slow_monolithic = run_slow_monolithic(tau_bin, KEYWORD_CASES[0], args.slow_timeout_s)
    spec_text = (ROOT / SPEC_REL).read_text(encoding="utf-8")
    artifact = {
        "schema": "qns_multifeature_demo_traces_v1",
        "generator": "scripts/generate_qns_multifeature_demo_artifacts.py",
        "spec_relpath": SPEC_REL,
        "tau_bin_name": Path(tau_bin).name,
        "scope": {
            "claim": (
                "A toy micro-proposer can feed finite qns8 candidate masks into "
                "actual Tau qns8 expressions for exact routing and pointwise "
                "revision-style policy memory updates."
            ),
            "not_claimed": [
                "not a real LLM proposer",
                "not upstream nlang semantics",
                "not unbounded natural-language understanding",
                "not full TABA tables",
            ],
        },
        "summary": {
            "ok": all(row["checks"]["tau_matches_host"] for row in rows)
            and all(row["checks"]["partition_matches_proposed"] for row in rows)
            and all(row["checks"]["unsafe_leak_zero"] for row in rows)
            and all(row["checks"]["revision_idempotent"] for row in rows),
            "scenario_count": len(rows),
            "tau_mismatch_count": sum(1 for row in rows if not row["checks"]["tau_matches_host"]),
            "partition_failure_count": sum(
                1 for row in rows if not row["checks"]["partition_matches_proposed"]
            ),
            "unsafe_leak_failure_count": sum(
                1 for row in rows if not row["checks"]["unsafe_leak_zero"]
            ),
            "revision_idempotence_failure_count": sum(
                1 for row in rows if not row["checks"]["revision_idempotent"]
            ),
            "slow_monolithic_attempted": slow_monolithic is not None,
            "slow_monolithic_timeout": (
                bool(slow_monolithic["result"]["timeout"]) if slow_monolithic else None
            ),
        },
        "rows": rows,
        "slow_monolithic_demo": slow_monolithic,
        "spec_text": spec_text,
    }
    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": artifact["summary"]["ok"],
                "out": str(out.relative_to(ROOT)),
                "scenario_count": artifact["summary"]["scenario_count"],
            },
            indent=2,
        )
    )
    return 0 if artifact["summary"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
