#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPEC_REL = "examples/tau/qns_candidate_filter_v1.tau"
MASK = 0xFF


def _load_tau_runner():
    sys.path.insert(0, str(ROOT / "scripts"))
    from tau_local_bridge import find_tau_bin

    return find_tau_bin


def _sanitize_trace_text(text: str) -> str:
    return re.sub(r"/tmp/[^\"'\s)]+", "/tmp/tau-trace-path", text)


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
QNS_VALUE_RE = re.compile(r"\{\s*(\d+)\s*\}:qns8")
PLAIN_VALUE_RE = re.compile(r"%\d+:\s*(\d+)\s*$")


def _strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def qns_const(mask: int) -> str:
    return f"{{ #x{mask & MASK:02X} }}:qns8"


def qns_not(expr: str) -> str:
    return f"({qns_const(MASK)} ^ ({expr}))"


def qns_exprs(step: dict[str, int]) -> dict[str, str]:
    universe = qns_const(step["i1"])
    proposed = qns_const(step["i2"])
    allowed = qns_const(step["i3"])
    review = qns_const(step["i4"])
    hard = qns_const(step["i5"])
    proposed_expr = f"(({universe}) & ({proposed}))"
    eligible = f"(({proposed_expr}) & ({allowed}) & ({qns_not(hard)}))"
    auto_accept = f"(({eligible}) & ({qns_not(review)}))"
    human_review = f"(({eligible}) & ({review}))"
    symbolic_reject = f"(({proposed_expr}) & (({qns_not(allowed)}) | ({hard})))"
    partition = f"(({auto_accept}) | ({human_review}) | ({symbolic_reject}))"
    unsafe_leak = f"(({auto_accept}) & ({hard}))"
    return {
        "o1": eligible,
        "o2": auto_accept,
        "o3": human_review,
        "o4": symbolic_reject,
        "o5": partition,
        "o6": unsafe_leak,
    }


def concept_exprs(step: dict[str, int]) -> dict[str, str]:
    observed = qns_const(step["observed"])
    required = qns_const(step["required"])
    risk = qns_const(step["risk"])
    review = qns_const(step["review"])
    present_required = f"(({observed}) & ({required}))"
    missing_required = f"(({required}) & ({qns_not(observed)}))"
    risk_hits = f"(({observed}) & ({risk}))"
    review_hits = f"(({observed}) & ({review}))"
    safe_atoms = f"(({observed}) & ({qns_not(risk)}))"
    return {
        "present_required": present_required,
        "missing_required": missing_required,
        "risk_hits": risk_hits,
        "review_hits": review_hits,
        "safe_atoms": safe_atoms,
    }


def run_tau_qns_normalize(tau_bin: str, expr: str, *, timeout_s: float) -> tuple[int, str]:
    env = dict(os.environ)
    env["TAU_ENABLE_QNS_BA"] = "1"
    cmd = [
        tau_bin,
        "--severity",
        "error",
        "--charvar",
        "false",
        "-e",
        f"n {expr}",
    ]
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_s,
        env=env,
        cwd=str(ROOT),
    )
    text = _strip_ansi((proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else ""))
    if proc.returncode != 0:
        raise RuntimeError(text.strip() or f"tau normalize failed with rc={proc.returncode}")
    match = QNS_VALUE_RE.search(text)
    if not match:
        match = PLAIN_VALUE_RE.search(text.strip())
    if not match:
        raise RuntimeError(f"could not parse qns8 result from Tau output: {text.strip()!r}")
    return int(match.group(1)), text.strip()


@dataclass(frozen=True)
class Candidate:
    bit: int
    name: str
    category: str

    @property
    def mask(self) -> int:
        return 1 << self.bit


CANDIDATES = (
    Candidate(0, "approve_low_risk_loan", "credit"),
    Candidate(1, "manual_review_high_amount", "credit"),
    Candidate(2, "reject_sanctioned_wallet", "compliance"),
    Candidate(3, "quarantine_oracle_anomaly", "incident"),
    Candidate(4, "reward_contributor", "tokenomics"),
    Candidate(5, "tax_extractor", "tokenomics"),
    Candidate(6, "freeze_governance_compromise", "incident"),
    Candidate(7, "escalate_human_council", "governance"),
)


@dataclass(frozen=True)
class Concept:
    bit: int
    name: str

    @property
    def mask(self) -> int:
        return 1 << self.bit


CONCEPTS = (
    Concept(0, "registry_verified"),
    Concept(1, "liquidity_deep"),
    Concept(2, "token_old_enough"),
    Concept(3, "provenance_clean"),
    Concept(4, "governance_separated"),
    Concept(5, "oracle_stable"),
    Concept(6, "sanction_risk"),
    Concept(7, "human_review_required"),
)


@dataclass(frozen=True)
class TraceClass:
    bit: int
    name: str

    @property
    def mask(self) -> int:
        return 1 << self.bit


TRACE_CLASSES = (
    TraceClass(0, "login_then_trade"),
    TraceClass(1, "trade_without_login"),
    TraceClass(2, "oracle_update_then_trade"),
    TraceClass(3, "trade_before_oracle_update"),
    TraceClass(4, "patch_then_admit_collateral"),
    TraceClass(5, "admit_before_patch"),
    TraceClass(6, "liquidation_after_price_drop"),
    TraceClass(7, "liquidation_before_price_drop"),
)


@dataclass(frozen=True)
class Scenario:
    name: str
    prompt: str
    neural_scores: tuple[float, ...]
    symbolic_allowed: tuple[bool, ...]
    review_required: tuple[bool, ...]
    hard_reject: tuple[bool, ...]
    proposer_threshold: float = 0.08


SCENARIOS = (
    Scenario(
        name="post_agi_tokenomics",
        prompt="Choose token-policy actions after an AGI-driven value shock.",
        neural_scores=(0.05, 0.08, 0.03, 0.07, 0.30, 0.34, 0.04, 0.09),
        symbolic_allowed=(True, True, True, True, True, False, True, True),
        review_required=(False, True, False, True, False, False, True, True),
        hard_reject=(False, False, False, False, False, True, False, False),
    ),
    Scenario(
        name="dex_oracle_incident",
        prompt="Choose protocol actions during a suspected oracle anomaly.",
        neural_scores=(0.13, 0.05, 0.06, 0.33, 0.04, 0.03, 0.22, 0.14),
        symbolic_allowed=(False, True, True, True, False, False, True, True),
        review_required=(False, True, False, True, False, False, True, True),
        hard_reject=(True, False, False, False, False, True, False, False),
    ),
    Scenario(
        name="collateral_admission",
        prompt="Choose actions after a newly proposed collateral token appears.",
        neural_scores=(0.19, 0.26, 0.20, 0.08, 0.05, 0.02, 0.07, 0.13),
        symbolic_allowed=(False, True, True, True, False, False, True, True),
        review_required=(False, True, False, True, False, False, True, True),
        hard_reject=(True, False, False, False, False, True, False, False),
    ),
)


@dataclass(frozen=True)
class ConceptScenario:
    name: str
    text: str
    observed: tuple[bool, ...]
    required: tuple[bool, ...]
    risk: tuple[bool, ...]
    review: tuple[bool, ...]


CONCEPT_SCENARIOS = (
    ConceptScenario(
        name="clean_collateral_report",
        text="Registry verified, deep liquidity, old token, clean provenance, separated governance, stable oracle.",
        observed=(True, True, True, True, True, True, False, False),
        required=(True, True, True, True, True, True, False, False),
        risk=(False, False, False, False, False, False, True, False),
        review=(False, False, False, False, False, False, False, True),
    ),
    ConceptScenario(
        name="carbonvote_like_report",
        text="Registry exists, but liquidity and age evidence are missing, provenance is unclear, and review is required.",
        observed=(True, False, False, False, False, True, False, True),
        required=(True, True, True, True, True, True, False, False),
        risk=(False, False, False, True, True, False, True, False),
        review=(False, False, False, False, False, False, False, True),
    ),
    ConceptScenario(
        name="oracle_incident_report",
        text="Governance is separated and provenance is clean, but the oracle is unstable and human review is required.",
        observed=(True, True, True, True, True, False, False, True),
        required=(True, True, True, True, True, True, False, False),
        risk=(False, False, False, False, False, True, True, False),
        review=(False, False, False, False, False, False, False, True),
    ),
)


@dataclass(frozen=True)
class TraceScenario:
    name: str
    description: str
    observed: tuple[bool, ...]
    safe: tuple[bool, ...]
    forbidden: tuple[bool, ...]


TRACE_SCENARIOS = (
    TraceScenario(
        name="ordinary_trade_session",
        description="The trace contains login before trade and oracle update before trade.",
        observed=(True, False, True, False, False, False, False, False),
        safe=(True, False, True, False, True, False, True, False),
        forbidden=(False, True, False, True, False, True, False, True),
    ),
    TraceScenario(
        name="collateral_admission_race",
        description="The trace includes admitting collateral before governance patch completion.",
        observed=(False, False, False, False, False, True, False, False),
        safe=(True, False, True, False, True, False, True, False),
        forbidden=(False, True, False, True, False, True, False, True),
    ),
    TraceScenario(
        name="liquidation_ordering_bug",
        description="The trace includes liquidation before the price-drop evidence is established.",
        observed=(False, False, False, False, False, False, False, True),
        safe=(True, False, True, False, True, False, True, False),
        forbidden=(False, True, False, True, False, True, False, True),
    ),
)


def mask_from_flags(flags: tuple[bool, ...]) -> int:
    out = 0
    for candidate, flag in zip(CANDIDATES, flags, strict=True):
        if flag:
            out |= candidate.mask
    return out & MASK


def mask_from_concept_flags(flags: tuple[bool, ...]) -> int:
    out = 0
    for concept, flag in zip(CONCEPTS, flags, strict=True):
        if flag:
            out |= concept.mask
    return out & MASK


def mask_from_trace_flags(flags: tuple[bool, ...]) -> int:
    out = 0
    for trace_class, flag in zip(TRACE_CLASSES, flags, strict=True):
        if flag:
            out |= trace_class.mask
    return out & MASK


def proposed_mask(scores: tuple[float, ...], threshold: float) -> int:
    out = 0
    for candidate, score in zip(CANDIDATES, scores, strict=True):
        if score >= threshold:
            out |= candidate.mask
    return out & MASK


def normalize_scores(scores: tuple[float, ...]) -> tuple[float, ...]:
    total = sum(scores)
    if total <= 0:
        raise ValueError("neural scores must have positive mass")
    return tuple(score / total for score in scores)


def names_for_mask(mask: int) -> list[str]:
    return [candidate.name for candidate in CANDIDATES if mask & candidate.mask]


def concept_names_for_mask(mask: int) -> list[str]:
    return [concept.name for concept in CONCEPTS if mask & concept.mask]


def trace_names_for_mask(mask: int) -> list[str]:
    return [trace_class.name for trace_class in TRACE_CLASSES if mask & trace_class.mask]


def expected_outputs(step: dict[str, int]) -> dict[str, int]:
    universe = step["i1"] & MASK
    proposed = step["i2"] & MASK
    allowed = step["i3"] & MASK
    review = step["i4"] & MASK
    hard = step["i5"] & MASK
    eligible = universe & proposed & allowed & ((~hard) & MASK)
    auto_accept = eligible & ((~review) & MASK)
    human_review = eligible & review
    symbolic_reject = universe & proposed & (((~allowed) & MASK) | hard)
    partition = auto_accept | human_review | symbolic_reject
    unsafe_leak = auto_accept & hard
    return {
        "o1": eligible & MASK,
        "o2": auto_accept & MASK,
        "o3": human_review & MASK,
        "o4": symbolic_reject & MASK,
        "o5": partition & MASK,
        "o6": unsafe_leak & MASK,
    }


def expected_concept_outputs(step: dict[str, int]) -> dict[str, int]:
    observed = step["observed"] & MASK
    required = step["required"] & MASK
    risk = step["risk"] & MASK
    review = step["review"] & MASK
    return {
        "present_required": observed & required,
        "missing_required": required & ((~observed) & MASK),
        "risk_hits": observed & risk,
        "review_hits": observed & review,
        "safe_atoms": observed & ((~risk) & MASK),
    }


def expected_trace_outputs(step: dict[str, int]) -> dict[str, int]:
    observed = step["observed"] & MASK
    safe = step["safe"] & MASK
    forbidden = step["forbidden"] & MASK
    classified = safe | forbidden
    return {
        "safe_observed": observed & safe,
        "forbidden_hits": observed & forbidden,
        "unclassified": observed & ((~classified) & MASK),
        "accepted_trace": observed & safe & ((~forbidden) & MASK),
    }


def qns_distribution(scores: tuple[float, ...], survivor_mask: int) -> dict[str, float]:
    qn = normalize_scores(scores)
    mass = sum(score for candidate, score in zip(CANDIDATES, qn, strict=True) if survivor_mask & candidate.mask)
    if mass == 0:
        return {}
    return {
        candidate.name: round(score / mass, 6)
        for candidate, score in zip(CANDIDATES, qn, strict=True)
        if survivor_mask & candidate.mask
    }


def scenario_step(scenario: Scenario) -> dict[str, int]:
    return {
        "i1": MASK,
        "i2": proposed_mask(scenario.neural_scores, scenario.proposer_threshold),
        "i3": mask_from_flags(scenario.symbolic_allowed),
        "i4": mask_from_flags(scenario.review_required),
        "i5": mask_from_flags(scenario.hard_reject),
    }


def concept_step(scenario: ConceptScenario) -> dict[str, int]:
    return {
        "observed": mask_from_concept_flags(scenario.observed),
        "required": mask_from_concept_flags(scenario.required),
        "risk": mask_from_concept_flags(scenario.risk),
        "review": mask_from_concept_flags(scenario.review),
    }


def trace_step(scenario: TraceScenario) -> dict[str, int]:
    return {
        "observed": mask_from_trace_flags(scenario.observed),
        "safe": mask_from_trace_flags(scenario.safe),
        "forbidden": mask_from_trace_flags(scenario.forbidden),
    }


def trace_exprs(step: dict[str, int]) -> dict[str, str]:
    observed = qns_const(step["observed"])
    safe = qns_const(step["safe"])
    forbidden = qns_const(step["forbidden"])
    classified = f"(({safe}) | ({forbidden}))"
    safe_observed = f"(({observed}) & ({safe}))"
    forbidden_hits = f"(({observed}) & ({forbidden}))"
    unclassified = f"(({observed}) & ({qns_not(classified)}))"
    accepted_trace = f"(({observed}) & ({safe}) & ({qns_not(forbidden)}))"
    return {
        "safe_observed": safe_observed,
        "forbidden_hits": forbidden_hits,
        "unclassified": unclassified,
        "accepted_trace": accepted_trace,
    }


def run_ba_smoke_checks(tau_bin: str, *, timeout_s: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cases = [
        ("meet", f"({qns_const(0x03)} & {qns_const(0x05)})", 0x01),
        ("join", f"({qns_const(0x03)} | {qns_const(0x05)})", 0x07),
        ("prime_as_xor_top", f"({qns_const(MASK)} ^ {qns_const(0xF0)})", 0x0F),
        (
            "candidate_filter",
            f"({qns_const(0xB2)} & {qns_const(0xDF)} & ({qns_const(MASK)} ^ {qns_const(0x20)}))",
            0x92,
        ),
    ]
    rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    for name, expr, expected in cases:
        actual, raw = run_tau_qns_normalize(tau_bin, expr, timeout_s=timeout_s)
        ok = actual == expected
        row = {
            "name": name,
            "expr": expr,
            "expected": expected,
            "actual": actual,
            "ok": ok,
            "raw": _sanitize_trace_text(raw),
        }
        rows.append(row)
        if not ok:
            mismatches.append(row)
    return rows, mismatches


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Tau artifacts for the finite qNS candidate Boolean algebra."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "assets" / "data" / "qns_candidate_ba_traces.json",
        help="Output JSON path",
    )
    parser.add_argument("--timeout-s", type=float, default=45.0)
    parser.add_argument(
        "--tau-bin",
        type=Path,
        default=None,
        help="Tau binary to use. Defaults to TAU_BIN or the local standard checkout.",
    )
    args = parser.parse_args()

    find_tau_bin = _load_tau_runner()
    tau_bin = str(args.tau_bin.resolve()) if args.tau_bin else find_tau_bin()
    if not tau_bin:
        raise SystemExit("Tau binary not found. Build external/tau-lang or set TAU_BIN.")

    ba_smoke_checks, ba_smoke_mismatches = run_ba_smoke_checks(
        tau_bin, timeout_s=args.timeout_s
    )
    steps = [scenario_step(scenario) for scenario in SCENARIOS]

    rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    tau_checks: list[dict[str, Any]] = []
    for idx, scenario in enumerate(SCENARIOS):
        step = steps[idx]
        exprs = qns_exprs(step)
        actual: dict[str, int] = {}
        for out_name, expr in exprs.items():
            value, raw = run_tau_qns_normalize(tau_bin, expr, timeout_s=args.timeout_s)
            actual[out_name] = value
            tau_checks.append(
                {
                    "scenario": scenario.name,
                    "output": out_name,
                    "expr": expr,
                    "value": value,
                    "raw": _sanitize_trace_text(raw),
                }
            )
        expected = expected_outputs(step)
        ok = actual == expected
        if not ok:
            mismatches.append(
                {
                    "scenario": scenario.name,
                    "expected": expected,
                    "actual": actual,
                }
            )
        eligible = actual["o1"]
        auto_accept = actual["o2"]
        human_review = actual["o3"]
        symbolic_reject = actual["o4"]
        proposed = step["i2"]
        qn = normalize_scores(scenario.neural_scores)
        qn_proposed_mass = round(
            sum(score for candidate, score in zip(CANDIDATES, qn, strict=True) if proposed & candidate.mask),
            6,
        )
        qn_survivor_mass = round(
            sum(score for candidate, score in zip(CANDIDATES, qn, strict=True) if eligible & candidate.mask),
            6,
        )
        rows.append(
            {
                "scenario": scenario.name,
                "prompt": scenario.prompt,
                "input_masks": step,
                "expected": expected,
                "actual": actual,
                "ok": ok,
                "sets": {
                    "proposed": names_for_mask(proposed),
                    "eligible": names_for_mask(eligible),
                    "auto_accept": names_for_mask(auto_accept),
                    "human_review": names_for_mask(human_review),
                    "symbolic_reject": names_for_mask(symbolic_reject),
                },
                "probability": {
                    "qN_proposed_mass": qn_proposed_mass,
                    "qN_survivor_mass": qn_survivor_mass,
                    "qNS": qns_distribution(scenario.neural_scores, eligible),
                },
            }
        )

    concept_steps = [concept_step(scenario) for scenario in CONCEPT_SCENARIOS]
    concept_rows: list[dict[str, Any]] = []
    concept_mismatches: list[dict[str, Any]] = []
    for idx, scenario in enumerate(CONCEPT_SCENARIOS):
        step = concept_steps[idx]
        exprs = concept_exprs(step)
        actual: dict[str, int] = {}
        for out_name, expr in exprs.items():
            value, raw = run_tau_qns_normalize(tau_bin, expr, timeout_s=args.timeout_s)
            actual[out_name] = value
            tau_checks.append(
                {
                    "scenario": scenario.name,
                    "output": out_name,
                    "expr": expr,
                    "value": value,
                    "raw": _sanitize_trace_text(raw),
                }
            )
        expected = expected_concept_outputs(step)
        ok = actual == expected
        if not ok:
            concept_mismatches.append(
                {
                    "scenario": scenario.name,
                    "expected": expected,
                    "actual": actual,
                }
            )
        concept_rows.append(
            {
                "scenario": scenario.name,
                "text": scenario.text,
                "input_masks": step,
                "expected": expected,
                "actual": actual,
                "ok": ok,
                "sets": {
                    "observed": concept_names_for_mask(step["observed"]),
                    "required": concept_names_for_mask(step["required"]),
                    "present_required": concept_names_for_mask(actual["present_required"]),
                    "missing_required": concept_names_for_mask(actual["missing_required"]),
                    "risk_hits": concept_names_for_mask(actual["risk_hits"]),
                    "review_hits": concept_names_for_mask(actual["review_hits"]),
                    "safe_atoms": concept_names_for_mask(actual["safe_atoms"]),
                },
            }
        )

    trace_steps = [trace_step(scenario) for scenario in TRACE_SCENARIOS]
    trace_rows: list[dict[str, Any]] = []
    trace_mismatches: list[dict[str, Any]] = []
    for idx, scenario in enumerate(TRACE_SCENARIOS):
        step = trace_steps[idx]
        exprs = trace_exprs(step)
        actual: dict[str, int] = {}
        for out_name, expr in exprs.items():
            value, raw = run_tau_qns_normalize(tau_bin, expr, timeout_s=args.timeout_s)
            actual[out_name] = value
            tau_checks.append(
                {
                    "scenario": scenario.name,
                    "output": out_name,
                    "expr": expr,
                    "value": value,
                    "raw": _sanitize_trace_text(raw),
                }
            )
        expected = expected_trace_outputs(step)
        ok = actual == expected
        if not ok:
            trace_mismatches.append(
                {
                    "scenario": scenario.name,
                    "expected": expected,
                    "actual": actual,
                }
            )
        trace_rows.append(
            {
                "scenario": scenario.name,
                "description": scenario.description,
                "input_masks": step,
                "expected": expected,
                "actual": actual,
                "ok": ok,
                "sets": {
                    "observed": trace_names_for_mask(step["observed"]),
                    "safe": trace_names_for_mask(step["safe"]),
                    "forbidden": trace_names_for_mask(step["forbidden"]),
                    "safe_observed": trace_names_for_mask(actual["safe_observed"]),
                    "forbidden_hits": trace_names_for_mask(actual["forbidden_hits"]),
                    "unclassified": trace_names_for_mask(actual["unclassified"]),
                    "accepted_trace": trace_names_for_mask(actual["accepted_trace"]),
                },
            }
        )

    bundle: dict[str, Any] = {
        "generator": "scripts/generate_qns_candidate_ba_artifacts.py",
        "spec_relpath": SPEC_REL,
        "tau_bin_name": Path(str(tau_bin)).name,
        "candidate_universe": [
            {"bit": candidate.bit, "name": candidate.name, "category": candidate.category}
            for candidate in CANDIDATES
        ],
        "concept_universe": [
            {"bit": concept.bit, "name": concept.name}
            for concept in CONCEPTS
        ],
        "trace_universe": [
            {"bit": trace_class.bit, "name": trace_class.name}
            for trace_class in TRACE_CLASSES
        ],
        "scope": {
            "implemented_carrier": "finite powerset Boolean algebra encoded as qns8",
            "neural_part": "host-side scored proposer",
            "symbolic_part": "Tau-side exact Boolean filtering",
            "not_claimed": [
                "native Tau nlang Boolean algebra",
                "probabilistic arithmetic inside Tau",
                "semantic correctness of an external LLM",
                "unbounded candidate universes",
            ],
        },
        "summary": {
            "ok": (
                not mismatches
                and not concept_mismatches
                and not trace_mismatches
                and not ba_smoke_mismatches
            ),
            "scenario_count": len(SCENARIOS),
            "concept_scenario_count": len(CONCEPT_SCENARIOS),
            "trace_scenario_count": len(TRACE_SCENARIOS),
            "mismatch_count": len(mismatches),
            "concept_mismatch_count": len(concept_mismatches),
            "trace_mismatch_count": len(trace_mismatches),
            "ba_smoke_mismatch_count": len(ba_smoke_mismatches),
        },
        "ba_smoke_checks": ba_smoke_checks,
        "rows": rows,
        "concept_rows": concept_rows,
        "trace_rows": trace_rows,
        "mismatches": (
            mismatches
            + concept_mismatches
            + trace_mismatches
            + ba_smoke_mismatches
        ),
        "tau_checks": tau_checks,
        "spec_text": (ROOT / SPEC_REL).read_text(encoding="utf-8"),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    print(json.dumps(bundle["summary"], indent=2))
    return (
        0
        if not mismatches and not concept_mismatches and not trace_mismatches and not ba_smoke_mismatches
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
