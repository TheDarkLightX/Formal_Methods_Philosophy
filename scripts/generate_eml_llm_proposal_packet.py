#!/usr/bin/env python3
"""Create and validate an LLM proposal packet for EML formula search.

The model is not trusted. This script only prepares a prompt and validates the
returned candidate JSON against the tiny EML grammar used by the qNS demo.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_eml_neurosymbolic_loop_demo import ParseError, parse_tree_expr  # noqa: E402


def build_feedback_section(feedback: dict[str, Any] | None) -> str:
    if feedback is None:
        return ""
    if feedback.get("schema") != "eml_reproposal_feedback_v1":
        raise ValueError("feedback schema must be eml_reproposal_feedback_v1")
    lines: list[str] = [
        "",
        "Previous checked feedback:",
        "",
        "Use this only as steering information. It is not proof evidence.",
        "",
    ]
    for target in feedback.get("targets", []):
        lines.append(f"Target: {target.get('target')}")
        accepted = target.get("accepted", [])
        if accepted:
            lines.append("Accepted formulas:")
            for item in accepted[:4]:
                lines.append(f"- {item.get('expr')} -> {item.get('normalized_expr')}")
        diagnostics = target.get("counterexample_diagnostics", [])
        if diagnostics:
            lines.append("Diagnostic points to satisfy:")
            for item in diagnostics[:4]:
                if item.get("kind") == "domain":
                    lines.append(f"- {item.get('expr')} failed domain at x={item.get('x')}")
                else:
                    lines.append(
                        "- "
                        f"{item.get('expr')} had absolute error {item.get('absolute_error')} "
                        f"at x={item.get('x')}"
                    )
        constraints = target.get("next_constraints", [])
        if constraints:
            lines.append("Constraints:")
            for item in constraints[:5]:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def build_prompt(targets: list[str], candidate_count: int, feedback: dict[str, Any] | None = None) -> str:
    target_lines = "\n".join(f"- {target}" for target in targets)
    feedback_section = build_feedback_section(feedback)
    return f"""You are proposing symbolic formulas for a checked EML/qNS loop.

Return JSON only. Do not include Markdown fences.

Allowed grammar:

T ::= x | 1 | eml(T,T)

Meaning:

eml(a,b) = exp(a) - ln(b)

Real-domain boundary:

Every ln argument must remain positive on the checked positive-real domain.

Targets:

{target_lines}

Task:

Propose at most {candidate_count} candidate EML formulas. Include both compact
candidates and diverse alternatives, but do not use constants other than 1.

Required JSON schema:

{{
  "schema": "eml_candidate_proposals_v1",
  "candidates": [
    {{
      "target": "exp(x)",
      "origin": "llm",
      "expr": "eml(x,1)",
      "note": "brief reason"
    }}
  ]
}}

The checker will reject malformed expressions. The checker may also reject
well-formed expressions that fail domain, sample, holdout, interval, or proof
receipt checks.
{feedback_section}
"""


def extract_json_object(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("no JSON object found in model output")
    return json.loads(text[start : end + 1])


def validate_candidate_file(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("schema") != "eml_candidate_proposals_v1":
        raise ValueError("schema must be eml_candidate_proposals_v1")
    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list")
    rows = []
    for index, item in enumerate(candidates):
        if not isinstance(item, dict):
            rows.append({"index": index, "parse_ok": False, "reason": "candidate is not an object"})
            continue
        expr = item.get("expr")
        if not isinstance(expr, str):
            rows.append({"index": index, "parse_ok": False, "reason": "expr is not a string"})
            continue
        try:
            tree = parse_tree_expr(expr)
        except ParseError as exc:
            rows.append(
                {
                    "index": index,
                    "expr": expr,
                    "target": item.get("target"),
                    "parse_ok": False,
                    "reason": str(exc),
                }
            )
            continue
        rows.append(
            {
                "index": index,
                "expr": expr,
                "canonical_expr": tree.pretty(),
                "target": item.get("target"),
                "origin": item.get("origin", "llm"),
                "parse_ok": True,
            }
        )
    return {
        "schema": "eml_candidate_validation_v1",
        "candidate_count": len(candidates),
        "parse_ok_count": sum(1 for row in rows if row["parse_ok"]),
        "parse_reject_count": sum(1 for row in rows if not row["parse_ok"]),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", action="append", default=["exp(x)", "ln(x)"])
    parser.add_argument("--candidate-count", type=int, default=12)
    parser.add_argument(
        "--prompt-out",
        type=Path,
        default=ROOT / "results" / "local" / "eml-llm-proposal-prompt.md",
    )
    parser.add_argument(
        "--candidate-out",
        type=Path,
        default=ROOT / "results" / "local" / "eml-llm-proposals.json",
    )
    parser.add_argument(
        "--validation-out",
        type=Path,
        default=ROOT / "results" / "local" / "eml-llm-proposal-validation.json",
    )
    parser.add_argument("--llm-output", type=Path, help="Existing model JSON output to validate.")
    parser.add_argument("--llm-command", help="Optional command to call with the prompt on stdin.")
    parser.add_argument(
        "--feedback-json",
        type=Path,
        help="Optional checked feedback packet from a previous EML/qNS run.",
    )
    args = parser.parse_args()

    feedback = None
    if args.feedback_json is not None:
        feedback = json.loads(args.feedback_json.read_text(encoding="utf-8"))
    prompt = build_prompt(args.target, args.candidate_count, feedback)
    args.prompt_out.parent.mkdir(parents=True, exist_ok=True)
    args.prompt_out.write_text(prompt, encoding="utf-8")

    data: dict[str, Any] | None = None
    if args.llm_output is not None:
        data = json.loads(args.llm_output.read_text(encoding="utf-8"))
    elif args.llm_command:
        proc = subprocess.run(
            shlex.split(args.llm_command),
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300,
        )
        if proc.returncode != 0:
            raise SystemExit(proc.stderr)
        data = extract_json_object(proc.stdout)

    if data is None:
        print(json.dumps({"ok": True, "prompt": str(args.prompt_out.relative_to(ROOT))}, indent=2))
        return 0

    validation = validate_candidate_file(data)
    args.candidate_out.parent.mkdir(parents=True, exist_ok=True)
    args.candidate_out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    args.validation_out.parent.mkdir(parents=True, exist_ok=True)
    args.validation_out.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "candidate_count": validation["candidate_count"],
                "parse_ok_count": validation["parse_ok_count"],
                "parse_reject_count": validation["parse_reject_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
