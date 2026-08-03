from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from examples.layered_q_tables.horizon_quotient_table import (
    HorizonQuotientError,
    build_horizon_quotient,
    query_horizon_quotient,
    verify_horizon_quotient,
)
from examples.layered_q_tables.knowledge_q_table import canonical_json_bytes


class HorizonQuotientTableTests(unittest.TestCase):
    def _paths(self, directory: str) -> tuple[Path, Path, Path, Path]:
        root = Path(directory)
        return (
            root / "source.npy",
            root / "quotient.npy",
            root / "manifest.json",
            root / "verify.json",
        )

    def test_fixed_point_tail_is_stored_once_and_replays_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, quotient, manifest, report = self._paths(directory)
            table = np.zeros((6, 3, 2), dtype="<f4")
            table[1] = 1
            table[2:] = 2
            np.save(source, table, allow_pickle=False)

            built = build_horizon_quotient(source, quotient, manifest)
            self.assertEqual(
                built["mapping"]["logical_to_physical"], [0, 1, 2, 2, 2, 2]
            )
            self.assertEqual(built["mapping"]["physical_layers"], 3)
            self.assertEqual(built["mapping"]["fixed_point_representative_horizon"], 2)
            self.assertEqual(built["mapping"]["first_aliased_tail_horizon"], 3)
            self.assertEqual(built["savings"]["stored_fraction"], 0.5)

            checked = verify_horizon_quotient(
                source, quotient, manifest, report_path=report, state_chunk=2
            )
            self.assertTrue(checked["passed"])
            self.assertEqual(checked["logical_values_checked"], table.size)
            self.assertEqual(
                checked["final_horizon_diversity"],
                {
                    "exact": True,
                    "reason": None,
                    "state_count": 3,
                    "unique_action_value_rows": 1,
                    "greedy_action_counts": [3, 0],
                },
            )
            self.assertEqual(query_horizon_quotient(quotient, manifest, 5, 2, 1), 2.0)

    def test_nonconsecutive_duplicate_layer_is_also_quotiented(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, quotient, manifest, _ = self._paths(directory)
            table = np.zeros((3, 2, 2), dtype="<f4")
            table[1] = 7
            table[2] = table[0]
            np.save(source, table, allow_pickle=False)
            built = build_horizon_quotient(source, quotient, manifest)
            self.assertEqual(built["mapping"]["logical_to_physical"], [0, 1, 0])
            self.assertIsNone(built["mapping"]["fixed_point_representative_horizon"])

    def test_mutated_quotient_is_rejected_by_hash(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, quotient, manifest, _ = self._paths(directory)
            table = np.arange(16, dtype="<f4").reshape(2, 4, 2)
            np.save(source, table, allow_pickle=False)
            build_horizon_quotient(source, quotient, manifest)
            changed = np.load(quotient, mmap_mode="r+")
            changed[0, 0, 0] += 1
            changed.flush()
            del changed
            with self.assertRaisesRegex(HorizonQuotientError, "quotient SHA-256"):
                verify_horizon_quotient(source, quotient, manifest)
            with self.assertRaisesRegex(HorizonQuotientError, "quotient SHA-256"):
                query_horizon_quotient(quotient, manifest, 0, 0, 0)

    def test_invalid_canonical_layer_map_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, quotient, manifest, _ = self._paths(directory)
            np.save(source, np.zeros((2, 2, 2), dtype="<f4"), allow_pickle=False)
            build_horizon_quotient(source, quotient, manifest)
            value = json.loads(manifest.read_text(encoding="utf-8"))
            value["mapping"]["logical_to_physical"][0] = 99
            manifest.write_bytes(canonical_json_bytes(value))
            with self.assertRaisesRegex(HorizonQuotientError, "invalid index"):
                verify_horizon_quotient(source, quotient, manifest)

    def test_wrong_dtype_and_nonfinite_values_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source, quotient, manifest, _ = self._paths(directory)
            np.save(source, np.zeros((2, 2, 2), dtype="<f8"), allow_pickle=False)
            with self.assertRaisesRegex(HorizonQuotientError, "dtype"):
                build_horizon_quotient(source, quotient, manifest)
            bad = np.zeros((2, 2, 2), dtype="<f4")
            bad[1, 1, 1] = np.nan
            np.save(source, bad, allow_pickle=False)
            with self.assertRaisesRegex(HorizonQuotientError, "non-finite"):
                build_horizon_quotient(source, quotient, manifest)


if __name__ == "__main__":
    unittest.main()
