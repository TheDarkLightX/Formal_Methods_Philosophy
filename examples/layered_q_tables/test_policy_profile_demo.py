from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from examples.layered_q_tables.policy_profile_demo import (
    ACTION_INDEX,
    FORBIDDEN,
    STATE_INDEX,
    build_comparison,
    canonical_json_bytes,
    compile_profile,
)


class PolicyProfileDemoTests(unittest.TestCase):
    def test_profiles_change_q_bytes_and_greedy_policy(self) -> None:
        throughput_table, throughput = compile_profile("throughput-v1")
        welfare_table, welfare = compile_profile(
            "bounded-equal-stakeholder-sum-v1"
        )
        self.assertNotEqual(throughput["table_sha256"], welfare["table_sha256"])
        self.assertFalse(np.array_equal(throughput_table, welfare_table))
        self.assertEqual(
            [step["action"] for step in throughput["greedy_path"]],
            ["inspect", "publish"],
        )
        self.assertEqual(
            [step["action"] for step in welfare["greedy_path"]],
            ["inspect", "redact", "publish"],
        )

    def test_hard_deontic_mask_forbids_premature_publish(self) -> None:
        table, _ = compile_profile("throughput-v1")
        self.assertTrue(
            np.all(
                table[:, STATE_INDEX["unreviewed_sensitive"], ACTION_INDEX["publish"]]
                == FORBIDDEN
            )
        )

    def test_comparison_is_canonical_and_deterministic(self) -> None:
        first = build_comparison()
        second = build_comparison()
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))
        self.assertTrue(first["comparison"]["same_facts_transitions_and_hard_norms"])
        self.assertTrue(first["comparison"]["table_bytes_differ"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            path.write_bytes(canonical_json_bytes(first))
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), first)

    def test_unknown_profile_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "unknown utility profile"):
            compile_profile("unknown")


if __name__ == "__main__":
    unittest.main()
