"""Compile two bounded utility profiles through one deontic action mask.

This companion is intentionally small.  It demonstrates that the same facts,
transitions, and hard O/F/P policy can produce different Q bytes when the
declared outcome model changes.  It does not claim that either profile is a
complete ethics theory or that the stakeholder scores are real measurements.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

SCHEMA = "glassmind-policy-comparison-v1"
MODEL_VERSION = "glassmind-bounded-publication-model-v1"
LAYERS = 4
GAMMA = np.float32(0.9)
FORBIDDEN = np.float32(-1_000_000.0)
STATES = ("unreviewed_sensitive", "reviewed_sensitive", "redacted")
ACTIONS = ("inspect", "redact", "publish", "escalate")
STATE_INDEX = {name: index for index, name in enumerate(STATES)}
ACTION_INDEX = {name: index for index, name in enumerate(ACTIONS)}

# Each row is (source state, action, destination state or None, outcome key).
TRANSITIONS = (
    ("unreviewed_sensitive", "inspect", "reviewed_sensitive", "inspect"),
    ("unreviewed_sensitive", "escalate", None, "escalate"),
    ("reviewed_sensitive", "redact", "redacted", "redact"),
    ("reviewed_sensitive", "publish", None, "publish_sensitive"),
    ("reviewed_sensitive", "escalate", None, "escalate"),
    ("redacted", "publish", None, "publish_redacted"),
    ("redacted", "escalate", None, "escalate"),
)

HARD_NORMS = (
    {"id": "F_publish_before_review", "modality": "F", "state": STATES[0], "action": "publish"},
    {"id": "F_redact_before_review", "modality": "F", "state": STATES[0], "action": "redact"},
    {"id": "F_inspect_after_review", "modality": "F", "state": STATES[1], "action": "inspect"},
    {"id": "F_inspect_after_redaction", "modality": "F", "state": STATES[2], "action": "inspect"},
    {"id": "F_repeat_redaction", "modality": "F", "state": STATES[2], "action": "redact"},
    {
        "id": "O_explicit_resolution",
        "modality": "O",
        "state": "all",
        "action": "select_argmax_or_escalate",
    },
)

UTILITY_PROFILES: dict[str, dict[str, Any]] = {
    "throughput-v1": {
        "description": "Illustrative latency-weighted profile.",
        "outcomes": {
            "inspect": -0.5,
            "redact": -1.0,
            "publish_sensitive": 4.0,
            "publish_redacted": 3.0,
            "escalate": 0.0,
        },
    },
    "bounded-equal-stakeholder-sum-v1": {
        "description": "Illustrative equal-weight sum over three declared stakeholders.",
        "stakeholders": ["data_subject", "readers", "steward"],
        "weights": [1, 1, 1],
        "consequences": {
            "inspect": [0, 0, -1],
            "redact": [4, -1, -1],
            "publish_sensitive": [-10, 5, 1],
            "publish_redacted": [2, 4, 1],
            "escalate": [0, -2, -1],
        },
    },
}


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _utilities(profile_id: str) -> dict[str, np.float32]:
    profile = UTILITY_PROFILES[profile_id]
    if "outcomes" in profile:
        values = profile["outcomes"]
    else:
        weights = profile["weights"]
        values = {
            outcome: sum(weight * score for weight, score in zip(weights, scores, strict=True))
            for outcome, scores in profile["consequences"].items()
        }
    return {key: np.float32(value) for key, value in values.items()}


def _transition_map() -> dict[tuple[int, int], tuple[int | None, str]]:
    return {
        (STATE_INDEX[source], ACTION_INDEX[action]): (
            STATE_INDEX[target] if target is not None else None,
            outcome,
        )
        for source, action, target, outcome in TRANSITIONS
    }


def compile_profile(profile_id: str) -> tuple[np.ndarray, dict[str, Any]]:
    """Return exact float32 Q layers and a deterministic profile receipt."""

    if profile_id not in UTILITY_PROFILES:
        raise ValueError(f"unknown utility profile {profile_id!r}")
    transitions = _transition_map()
    utilities = _utilities(profile_id)
    table = np.full(
        (LAYERS, len(STATES), len(ACTIONS)),
        FORBIDDEN,
        dtype=np.dtype("<f4"),
    )
    previous: np.ndarray | None = None
    for layer in range(LAYERS):
        for (state, action), (target, outcome) in transitions.items():
            reward = utilities[outcome]
            if target is None:
                table[layer, state, action] = reward
            elif layer > 0 and previous is not None:
                valid = previous[target][previous[target] > FORBIDDEN]
                if valid.size:
                    table[layer, state, action] = np.float32(
                        reward + GAMMA * np.max(valid)
                    )
        previous = np.max(table[layer], axis=1)

    path: list[dict[str, Any]] = []
    state = STATE_INDEX["unreviewed_sensitive"]
    for layer in range(LAYERS - 1, -1, -1):
        row = table[layer, state]
        action = int(np.argmax(row))
        target, outcome = transitions[(state, action)]
        path.append(
            {
                "layer": layer,
                "state": STATES[state],
                "action": ACTIONS[action],
                "outcome": outcome,
                "q": float(row[action]),
            }
        )
        if target is None:
            break
        state = target

    profile = UTILITY_PROFILES[profile_id]
    raw = table.tobytes(order="C")
    receipt = {
        "profile_id": profile_id,
        "profile_sha256": _sha(profile),
        "table_sha256": hashlib.sha256(raw).hexdigest(),
        "shape": list(table.shape),
        "dtype": "<f4",
        "raw_bytes": len(raw),
        "greedy_path": path,
        "q_values": table.tolist(),
    }
    return table, receipt


def build_comparison() -> dict[str, Any]:
    """Build and self-check the two-profile counterfactual receipt."""

    model = {
        "version": MODEL_VERSION,
        "states": list(STATES),
        "actions": list(ACTIONS),
        "transitions": [list(row) for row in TRANSITIONS],
        "hard_norms": list(HARD_NORMS),
        "layers": LAYERS,
        "gamma": float(GAMMA),
        "tie_break": "first_action_index",
    }
    _, throughput = compile_profile("throughput-v1")
    _, stakeholder_sum = compile_profile("bounded-equal-stakeholder-sum-v1")
    if throughput["table_sha256"] == stakeholder_sum["table_sha256"]:
        raise AssertionError("different declared utility profiles produced identical bytes")
    if [step["action"] for step in throughput["greedy_path"]] != [
        "inspect",
        "publish",
    ]:
        raise AssertionError("throughput profile did not reproduce its declared path")
    if [step["action"] for step in stakeholder_sum["greedy_path"]] != [
        "inspect",
        "redact",
        "publish",
    ]:
        raise AssertionError("stakeholder-sum profile did not reproduce its declared path")
    return {
        "schema": SCHEMA,
        "model": model,
        "model_sha256": _sha(model),
        "profiles": [throughput, stakeholder_sum],
        "comparison": {
            "same_facts_transitions_and_hard_norms": True,
            "table_bytes_differ": True,
            "greedy_paths_differ": True,
            "interpretation": "The Q bytes are aligned only with the selected finite utility profile after the shared hard deontic mask.",
        },
        "assumptions": [
            "All consequence scores are synthetic integers chosen for this tutorial.",
            "The stakeholder list and equal weights are declared model choices.",
            "The hard norm set is fixed across the two utility profiles.",
        ],
        "nonclaims": [
            "The bounded stakeholder sum is not a proof of utilitarianism or moral correctness.",
            "The synthetic consequences are not measurements of real welfare.",
            "This companion receipt was not separately verified by ESSO or Tau.",
        ],
    }


def _main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = build_comparison()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_json_bytes(result))
    sys.stdout.write(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
            },
            sort_keys=True,
        )
        + "\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
