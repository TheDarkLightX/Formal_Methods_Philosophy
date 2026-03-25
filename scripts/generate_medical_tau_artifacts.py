#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TAU_DEX_ROOT = ROOT.parent / "Autonomous Tau DEX"


def _load_tau_runner(tau_dex_root: Path):
    sys.path.insert(0, str(tau_dex_root))
    from src.integration.tau_runner import find_tau_bin, run_tau_spec_steps_with_trace

    return find_tau_bin, run_tau_spec_steps_with_trace


def _sanitize_trace_text(text: str) -> str:
    text = re.sub(r"/tmp/[^\"'\s)]+", "/tmp/tau-trace-path", text)
    return text


def _case_bundle(
    *,
    name: str,
    family: str,
    spec_relpath: str,
    explanation: str,
    steps: list[dict[str, int]],
) -> dict[str, Any]:
    return {
        "name": name,
        "family": family,
        "spec_relpath": spec_relpath,
        "explanation": explanation,
        "steps": steps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate replayable Tau trace artifacts for the medical MPRD tutorial."
    )
    parser.add_argument(
        "--tau-dex-root",
        type=Path,
        default=DEFAULT_TAU_DEX_ROOT,
        help="Path to the Autonomous Tau DEX checkout that contains src/integration/tau_runner.py",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "assets" / "data" / "medical_tau_traces.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    tau_dex_root = args.tau_dex_root.resolve()
    if not tau_dex_root.exists():
        raise SystemExit(f"Autonomous Tau DEX root not found: {tau_dex_root}")

    find_tau_bin, run_tau_spec_steps_with_trace = _load_tau_runner(tau_dex_root)
    tau_bin = find_tau_bin(tau_dex_root)
    if not tau_bin:
        raise SystemExit("Tau binary not found. Build it in the Autonomous Tau DEX checkout first.")

    cases = [
        _case_bundle(
            name="wellness_publish_ok",
            family="wellness",
            spec_relpath="examples/tau/medical_wellness_deficit_gate_v1.tau",
            explanation="All required facts are present and the proposal stays inside the computed ceiling, so the publish-plan action is allowed.",
            steps=[{"i1": 1, "i2": 1, "i3": 1, "i4": 1, "i5": 1, "i6": 1, "i7": 1, "i8": 0, "i9": 1}],
        ),
        _case_bundle(
            name="wellness_escalate_on_missing_evidence",
            family="wellness",
            spec_relpath="examples/tau/medical_wellness_deficit_gate_v1.tau",
            explanation="The model proposes escalation because the request is not safely auto-actionable, and that escalation action is allowed.",
            steps=[{"i1": 1, "i2": 1, "i3": 1, "i4": 1, "i5": 0, "i6": 0, "i7": 0, "i8": 1, "i9": 1}],
        ),
        _case_bundle(
            name="wellness_bad_publish_blocked",
            family="wellness",
            spec_relpath="examples/tau/medical_wellness_deficit_gate_v1.tau",
            explanation="The model proposes a publish action even though the safety gate is closed, so Tau denies execution.",
            steps=[{"i1": 1, "i2": 1, "i3": 1, "i4": 1, "i5": 0, "i6": 0, "i7": 1, "i8": 0, "i9": 1}],
        ),
        _case_bundle(
            name="lab_watch_ok",
            family="lab",
            spec_relpath="examples/tau/medical_lab_followup_gate_toy_v1.tau",
            explanation="Normal toy follow-up case, complete data, no red flags, no abnormal flag, so watch is allowed.",
            steps=[{"i1": 1, "i2": 0, "i3": 0, "i4": 1, "i5": 0, "i6": 0, "i7": 1}],
        ),
        _case_bundle(
            name="lab_repeat_ok",
            family="lab",
            spec_relpath="examples/tau/medical_lab_followup_gate_toy_v1.tau",
            explanation="Abnormal but non-red-flag toy case, complete and in scope, so repeat-lab is allowed.",
            steps=[{"i1": 1, "i2": 0, "i3": 1, "i4": 0, "i5": 1, "i6": 0, "i7": 1}],
        ),
        _case_bundle(
            name="lab_human_review_ok",
            family="lab",
            spec_relpath="examples/tau/medical_lab_followup_gate_toy_v1.tau",
            explanation="A red flag is present, so the only permitted execution-class action is human review.",
            steps=[{"i1": 1, "i2": 1, "i3": 1, "i4": 0, "i5": 0, "i6": 1, "i7": 1}],
        ),
        _case_bundle(
            name="refill_ok",
            family="refill",
            spec_relpath="examples/tau/medical_refill_gate_toy_v1.tau",
            explanation="All bounded refill safety flags are true, so the refill action is allowed.",
            steps=[{"i1": 1, "i2": 1, "i3": 1, "i4": 1, "i5": 1, "i6": 1, "i7": 1, "i8": 0, "i9": 1}],
        ),
        _case_bundle(
            name="refill_hold_and_review_ok",
            family="refill",
            spec_relpath="examples/tau/medical_refill_gate_toy_v1.tau",
            explanation="The automatic refill lane is closed, so the bounded hold-and-review action is the permitted path.",
            steps=[{"i1": 1, "i2": 1, "i3": 0, "i4": 1, "i5": 0, "i6": 1, "i7": 0, "i8": 1, "i9": 1}],
        ),
        _case_bundle(
            name="refill_bad_refill_blocked",
            family="refill",
            spec_relpath="examples/tau/medical_refill_gate_toy_v1.tau",
            explanation="The model asks for an automatic refill even though the refill lane is closed, so Tau denies it.",
            steps=[{"i1": 1, "i2": 1, "i3": 0, "i4": 1, "i5": 0, "i6": 1, "i7": 1, "i8": 0, "i9": 1}],
        ),
    ]

    trace_bundle: dict[str, Any] = {
        "generator": "scripts/generate_medical_tau_artifacts.py",
        "tau_dex_root_name": tau_dex_root.name,
        "tau_bin_name": Path(str(tau_bin)).name,
        "cases": {},
    }

    for case in cases:
        spec_path = ROOT / case["spec_relpath"]
        outputs, stdout, stderr, repl_script = run_tau_spec_steps_with_trace(
            tau_bin=tau_bin,
            spec_path=spec_path,
            steps=case["steps"],
            timeout_s=60.0,
        )
        trace_bundle["cases"][case["name"]] = {
            "family": case["family"],
            "spec_relpath": case["spec_relpath"],
            "explanation": case["explanation"],
            "steps": case["steps"],
            "outputs_by_step": outputs,
            "stdout": _sanitize_trace_text(stdout),
            "stderr": _sanitize_trace_text(stderr),
            "repl_script": _sanitize_trace_text(repl_script),
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(trace_bundle, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
