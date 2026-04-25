#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
import re
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "tau" / "indexed-factor-sparse-impact-demo.patch"
DEFAULT_SPEC = ROOT / "examples" / "tau" / "sparse_impact_factor_speedup_demo.tau"
DEFAULT_REPORT = ROOT / "results" / "tau_sparse_impact_demo_report.json"
SOLVE_RE = re.compile(r"^\[indexed_factor_solve\]\s+(?P<body>.*)$", re.MULTILINE)
PROFIT_RE = re.compile(r"^\[indexed_factor_profit\]\s+(?P<body>.*)$", re.MULTILINE)


def run(
    argv: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        argv,
        cwd=cwd,
        env=merged_env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )


def find_tau_checkout(arg: str | None) -> Path:
    candidates = []
    if arg:
        candidates.append(Path(arg))
    env = os.environ.get("TAU_LANG_CHECKOUT")
    if env:
        candidates.append(Path(env))
    candidates.extend(
        [
            ROOT.parent / "TauLang-Experiments" / "external" / "tau-lang-latest",
            ROOT / "external" / "tau-lang-latest",
            Path.cwd(),
        ]
    )
    for candidate in candidates:
        path = candidate.expanduser().resolve()
        if (path / "src" / "repl_evaluator.tmpl.h").exists():
            return path
    raise SystemExit(
        "Could not find a Tau checkout. Pass --tau-checkout or set "
        "TAU_LANG_CHECKOUT to a directory containing src/repl_evaluator.tmpl.h."
    )


def patch_already_applied(tau_checkout: Path) -> bool:
    source = tau_checkout / "src" / "repl_evaluator.tmpl.h"
    text = source.read_text(encoding="utf-8")
    required = [
        "TAU_INDEXED_FACTOR_SOLVE_STATS",
        "emit_factor_profit_stats",
        "impacted_factor_or_ratio_spread_x1000",
        "impacted_residual_support_component_count",
    ]
    return all(marker in text for marker in required)


def apply_patch(tau_checkout: Path) -> str:
    if patch_already_applied(tau_checkout):
        return "already_applied"
    if not PATCH.exists():
        raise SystemExit(f"Missing patch artifact: {PATCH.relative_to(ROOT)}")
    check = run(
        ["git", "apply", "--unidiff-zero", "--check", str(PATCH)],
        tau_checkout,
        timeout=60,
    )
    if check.returncode != 0:
        raise SystemExit(
            "Patch did not apply cleanly. The checkout may already be modified "
            "or not match the expected Tau source.\n\n"
            + check.stdout[-4000:]
        )
    applied = run(
        ["git", "apply", "--unidiff-zero", str(PATCH)],
        tau_checkout,
        timeout=60,
    )
    if applied.returncode != 0:
        raise SystemExit("Patch apply failed:\n\n" + applied.stdout[-4000:])
    return "applied"


def build_tau(tau_checkout: Path) -> None:
    build = run(["cmake", "--build", "build-Release", "--target", "tau", "-j2"], tau_checkout, timeout=600)
    if build.returncode != 0:
        raise SystemExit("Tau build failed:\n\n" + build.stdout[-4000:])


def balanced_term(
    variables: list[str],
    leaves: int,
    rng: random.Random,
    required: str | None,
) -> str:
    nodes = [rng.choice(variables) for _ in range(leaves)]
    if required is not None:
        nodes[0] = required
        rng.shuffle(nodes)
    while len(nodes) > 1:
        next_nodes = []
        for idx in range(0, len(nodes), 2):
            if idx + 1 == len(nodes):
                next_nodes.append(nodes[idx])
                continue
            op = rng.choice(["&", "|"])
            next_nodes.append(f"({nodes[idx]} {op} {nodes[idx + 1]})")
        nodes = next_nodes
    return nodes[0]


def make_demo_command() -> str:
    rng = random.Random(52052)
    factors = []
    next_var = 0
    factor_count = 24
    impacted_count = 3
    for idx in range(factor_count):
        impacted = idx < impacted_count
        support_size = 3 if impacted else 2
        variables = ["d0"] if impacted else []
        while len(variables) < support_size:
            variables.append(f"v{next_var}")
            next_var += 1
        term = balanced_term(
            variables,
            64,
            rng,
            "d0" if impacted else None,
        )
        factors.append(f"({term} != 0)")
    rng.shuffle(factors)
    return "solve --tau (" + " && ".join(factors) + ")"


def write_demo_spec(path: Path, command: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(command + "\n", encoding="utf-8")


def parse_fields(output: str, regex: re.Pattern[str], label: str) -> dict[str, str]:
    matches = list(regex.finditer(output))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {label} line, got {len(matches)}")
    fields = {}
    for part in matches[0].group("body").split():
        if "=" not in part:
            raise RuntimeError(f"malformed {label} field: {part!r}")
        key, value = part.split("=", 1)
        fields[key] = value
    return fields


def run_demo_once(tau_bin: Path, tau_checkout: Path, command: str) -> dict[str, Any]:
    env = {
        "TAU_INDEXED_FACTOR_SOLVE_STATS": "1",
        "TAU_INDEXED_FACTOR_PROFIT_STATS": "1",
        "TAU_INDEXED_IMPACT_DELTA": "d0",
        "TAU_INDEXED_FACTOR_SOLVE_ORDER": "full_first",
    }
    proc = run(
        [
            str(tau_bin),
            "--charvar",
            "false",
            "--severity",
            "error",
            "--color",
            "false",
            "--status",
            "false",
            "--evaluate",
            command,
        ],
        tau_checkout,
        env=env,
        timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError("Tau demo run failed:\n\n" + proc.stdout[-4000:])
    solve = parse_fields(proc.stdout, SOLVE_RE, "indexed_factor_solve")
    profit = parse_fields(proc.stdout, PROFIT_RE, "indexed_factor_profit")
    if solve.get("scan_equals_indexed") != "1":
        raise RuntimeError("scan and indexed impacted-factor selection disagreed")
    if solve.get("full_errors") != "0" or solve.get("indexed_errors") != "0":
        raise RuntimeError("solver errors were reported")
    return {
        "speedup": int(solve["speedup_x1000"]) / 1000.0,
        "full_solve_ms": float(solve["full_solve_ms"]),
        "indexed_solve_ms": float(solve["indexed_solve_ms"]),
        "full_impacted_cost_ratio_x1000": int(solve["full_impacted_cost_ratio_x1000"]),
        "factors": int(solve["factors"]),
        "impacted_indexed": int(solve["impacted_indexed"]),
        "saved_factors": int(profit["saved_factors"]),
        "impact_ratio_x1000": int(profit["impact_ratio_x1000"]),
        "support_impact_ratio_x1000": int(profit["support_impact_ratio_x1000"]),
        "term_impact_ratio_x1000": int(profit["term_impact_ratio_x1000"]),
        "recommended": profit["recommended"] == "1",
        "route": profit["route"],
        "reason": profit["reason"],
    }


def display_path(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Patch Tau with the sparse impacted-factor demo hook and run a measured demo."
    )
    parser.add_argument("--tau-checkout", help="Path to a Tau checkout. Defaults to TAU_LANG_CHECKOUT or a sibling TauLang-Experiments checkout.")
    parser.add_argument("--skip-patch", action="store_true", help="Assume the Tau checkout is already patched.")
    parser.add_argument("--skip-build", action="store_true", help="Skip the Tau rebuild step.")
    parser.add_argument("--repeats", type=int, default=3, help="Number of measured demo runs.")
    parser.add_argument("--spec-out", type=Path, default=DEFAULT_SPEC, help="Where to write the generated demo solve command.")
    parser.add_argument("--report-out", type=Path, default=DEFAULT_REPORT, help="Where to write the JSON result report.")
    args = parser.parse_args()

    tau_checkout = find_tau_checkout(args.tau_checkout)
    tau_bin = tau_checkout / "build-Release" / "tau"
    patch_state = "skipped" if args.skip_patch else apply_patch(tau_checkout)
    if not args.skip_build:
        build_tau(tau_checkout)
    if not tau_bin.exists():
        raise SystemExit(f"Tau binary not found: {tau_bin}")

    command = make_demo_command()
    write_demo_spec(args.spec_out, command)
    runs = [run_demo_once(tau_bin, tau_checkout, command) for _ in range(args.repeats)]
    speedups = [run["speedup"] for run in runs]
    report = {
        "status": "passed",
        "patch_state": patch_state,
        "tau_checkout": "provided_or_detected_checkout",
        "spec": display_path(args.spec_out),
        "repeats": args.repeats,
        "median_speedup": statistics.median(speedups),
        "min_speedup": min(speedups),
        "max_speedup": max(speedups),
        "runs": runs,
        "scope": "sparse top-level conjunction with 24 factors and 3 factors impacted by d0",
        "non_claim": "This does not prove arbitrary Tau formula acceleration.",
    }
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "patch_state": patch_state,
        "spec": display_path(args.spec_out),
        "report": display_path(args.report_out),
        "median_speedup": report["median_speedup"],
        "min_speedup": report["min_speedup"],
        "max_speedup": report["max_speedup"],
        "scope": report["scope"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
