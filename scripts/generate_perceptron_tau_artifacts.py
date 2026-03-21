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
    text = re.sub(r"Tau Language Framework version ([^)]+)\)", r"Tau Language Framework version \1)", text)
    return text


def _unsigned_score(step: dict[str, int]) -> int:
    return (step["i1"] * step["i3"]) + (step["i2"] * step["i4"]) + step["i5"]


def _signed_decode(value: int) -> int:
    return value - 127


def _signed_score(step: dict[str, int]) -> int:
    return (
        _signed_decode(step["i1"]) * _signed_decode(step["i3"])
        + _signed_decode(step["i2"]) * _signed_decode(step["i4"])
        + _signed_decode(step["i5"])
    )


def _internal_score(step: dict[str, int]) -> int:
    return (step["i1"] * 4) + (step["i2"] * 5) + 1


def _case_bundle(name: str, spec_rel: str, steps: list[dict[str, int]]) -> dict[str, Any]:
    return {
        "name": name,
        "spec_relpath": spec_rel,
        "steps": steps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate replayable perceptron Tau artifacts using a local Autonomous Tau DEX checkout."
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
        default=ROOT / "assets" / "data" / "perceptron_tau_traces.json",
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
            "unsigned_external_weights",
            "examples/tau/perceptron_2input_single_output_v1.tau",
            [
                {"i1": 2, "i2": 3, "i3": 4, "i4": 5, "i5": 1, "i6": 20, "i7": 1},
                {"i1": 2, "i2": 1, "i3": 1, "i4": 2, "i5": 0, "i6": 10, "i7": 0},
            ],
        ),
        _case_bundle(
            "signed_offset_external_weights",
            "examples/tau/perceptron_2input_signed_offset_v1.tau",
            [
                {"i1": 129, "i2": 130, "i3": 131, "i4": 132, "i5": 128, "i6": 127, "i7": 1},
                {"i1": 125, "i2": 124, "i3": 131, "i4": 132, "i5": 127, "i6": 127, "i7": 0},
            ],
        ),
        _case_bundle(
            "internal_parameters",
            "examples/tau/perceptron_2input_internal_weights_v1.tau",
            [
                {"i1": 2, "i2": 3, "i3": 20, "i4": 1},
                {"i1": 2, "i2": 1, "i3": 15, "i4": 0},
            ],
        ),
    ]

    trace_bundle: dict[str, Any] = {
        "generator": "scripts/generate_perceptron_tau_artifacts.py",
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
        data: dict[str, Any] = {
            "spec_relpath": case["spec_relpath"],
            "steps": case["steps"],
            "outputs_by_step": outputs,
            "stdout": _sanitize_trace_text(stdout),
            "stderr": _sanitize_trace_text(stderr),
            "repl_script": _sanitize_trace_text(repl_script),
        }
        if case["name"] == "unsigned_external_weights":
            data["derived"] = [
                {
                    "score": _unsigned_score(step),
                    "threshold": step["i6"],
                    "actual_class": 1 if _unsigned_score(step) >= step["i6"] else 0,
                    "claimed_class": step["i7"],
                }
                for step in case["steps"]
            ]
        elif case["name"] == "signed_offset_external_weights":
            data["derived"] = [
                {
                    "decoded": {
                        "x1": _signed_decode(step["i1"]),
                        "x2": _signed_decode(step["i2"]),
                        "w1": _signed_decode(step["i3"]),
                        "w2": _signed_decode(step["i4"]),
                        "bias": _signed_decode(step["i5"]),
                        "threshold": _signed_decode(step["i6"]),
                    },
                    "score": _signed_score(step),
                    "actual_class": 1 if _signed_score(step) >= _signed_decode(step["i6"]) else 0,
                    "claimed_class": step["i7"],
                }
                for step in case["steps"]
            ]
        elif case["name"] == "internal_parameters":
            data["derived"] = [
                {
                    "internal_weights": {"w1": 4, "w2": 5, "bias": 1},
                    "score": _internal_score(step),
                    "threshold": step["i3"],
                    "actual_class": 1 if _internal_score(step) >= step["i3"] else 0,
                    "claimed_class": step["i4"],
                }
                for step in case["steps"]
            ]
        trace_bundle["cases"][case["name"]] = data

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(trace_bundle, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
