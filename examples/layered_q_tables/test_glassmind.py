from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

from examples.layered_q_tables.glassmind import (
    Config,
    ACTIONS,
    _rollout,
    build_environment,
    canonicalize_proposals,
    expand_challenge_corpus,
    file_sha256,
    generate_table,
    load_scenario_pack,
    search_counterexamples,
    verify_table,
)


class GlassMindTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = Config(
            layers=32,
            width=16,
            height=12,
            goal_spacing_x=64,
            goal_spacing_y=64,
        )

    def test_environment_is_deterministic_and_bounded(self) -> None:
        first = build_environment(self.config)
        second = build_environment(self.config)
        np.testing.assert_array_equal(first.risk, second.risk)
        np.testing.assert_array_equal(first.next_states, second.next_states)
        np.testing.assert_array_equal(first.rewards, second.rewards)
        self.assertTrue(np.all(first.next_states >= 0))
        self.assertTrue(np.all(first.next_states < self.config.states))
        self.assertEqual(first.next_states.shape, (self.config.states, len(ACTIONS)))
        self.assertGreater(int(np.count_nonzero(first.goals)), 0)

    def test_canonicalizer_deduplicates_and_quarantines_proposals(self) -> None:
        pack = load_scenario_pack()
        _, evidence = canonicalize_proposals(self.config, pack)
        self.assertEqual(evidence["canonical_state_count"], 2)
        self.assertEqual(evidence["duplicate_state_proposals"], 1)
        self.assertEqual(evidence["quarantined_state_or_trajectory_proposals"], 2)
        self.assertEqual(evidence["canonical_actions"], list(ACTIONS))
        self.assertEqual(evidence["invalid_action_proposals"], 1)
        self.assertEqual(
            [state["key"] for state in evidence["canonical_states"]],
            ["s000000", "s000017"],
        )

    def test_generated_table_passes_full_bellman_replay(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "table.npy"
            generate_table(path, self.config, progress=False)
            result = verify_table(path, self.config, progress=False)
            self.assertTrue(result["passed"])
            self.assertEqual(result["max_abs_bellman_error"], 0.0)
            self.assertGreater(result["challenge_corpus"]["canonical_unique_state_count"], 0)
            self.assertEqual(len(result["coverage"]["motif_activity"]), 5)
            self.assertTrue(all(item["active_cell_count"] > 0 for item in result["coverage"]["motif_activity"]))
            self.assertEqual(path.stat().st_size, self.config.data_bytes + 128)

    def test_challenge_corpus_and_motif_activity_are_reported(self) -> None:
        env = build_environment(self.config)
        pack = load_scenario_pack()
        corpus = expand_challenge_corpus(self.config, env, pack)
        self.assertGreater(corpus["canonical_unique_state_count"], 0)
        self.assertGreater(corpus["duplicate_expanded_rows"], 0)
        self.assertLessEqual(corpus["quarantined_challenge_proposals"], 1)
        self.assertEqual(len(pack["accepted_motifs"]), 5)

    def test_corrupted_q_value_is_caught_by_replay_and_probe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "table.npy"
            generate_table(path, self.config, progress=False)
            corrupted = np.load(path, mmap_mode="r+")
            corrupted[3, 2, 1] += np.float32(0.25)
            corrupted.flush()
            result = verify_table(path, self.config, progress=False)
            self.assertFalse(result["passed"])
            self.assertGreater(result["max_abs_bellman_error"], 0.0)
            self.assertFalse(result["counterexample_search"]["passed"])
            self.assertGreater(result["counterexample_search"]["contradiction_count"], 0)

    def test_counterexample_search_reports_clean_sparse_probe(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "table.npy"
            generate_table(path, self.config, progress=False)
            table = np.load(path, mmap_mode="r")
            result = search_counterexamples(
                table, self.config, build_environment(self.config)
            )
            self.assertTrue(result["passed"])
            self.assertGreater(result["candidate_state_count"], 0)
            self.assertGreater(result["checked_q_values"], 0)

    def test_generation_is_byte_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.npy"
            second = Path(directory) / "second.npy"
            generate_table(first, self.config, progress=False)
            generate_table(second, self.config, progress=False)
            self.assertEqual(file_sha256(first), file_sha256(second))

    def test_long_horizon_policy_reaches_the_small_map_goal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "table.npy"
            generate_table(path, self.config, progress=False)
            table = np.load(path, mmap_mode="r")
            env = build_environment(self.config)
            result = _rollout(table, self.config, env, 0, self.config.layers)
            self.assertTrue(result["reached_goal"])
            self.assertLessEqual(result["steps_taken"], self.config.layers)


if __name__ == "__main__":
    unittest.main()
