from __future__ import annotations

import ast
import copy
import unittest
from pathlib import Path

from examples.layered_q_tables.synthetic_deontic_kb import (
    EXPECTED_RECORD_COUNT,
    SyntheticDeonticError,
    generate_record,
    load_template_bank,
    rank_coordinate,
    unrank_ordinal,
)
from examples.layered_q_tables.synthetic_deontic_oracle import (
    OracleError,
    validate_record,
)

ROOT = Path(__file__).resolve().parent
TEMPLATE_BANK = ROOT / "synthetic_deontic_templates.json"


class SyntheticDeonticCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = load_template_bank(TEMPLATE_BANK)

    def test_exact_lattice_round_trip(self) -> None:
        probes = [0, 1, 2, 255, 256, 4095, 4096, 32767, 65534, 65535]
        probes.extend(range(0, EXPECTED_RECORD_COUNT, 257))
        for ordinal in probes:
            with self.subTest(ordinal=ordinal):
                self.assertEqual(rank_coordinate(unrank_ordinal(ordinal)), ordinal)
        with self.assertRaises(SyntheticDeonticError):
            unrank_ordinal(-1)
        with self.assertRaises(SyntheticDeonticError):
            unrank_ordinal(EXPECTED_RECORD_COUNT)

    def test_independent_oracle_agrees_on_cross_axis_witnesses(self) -> None:
        witnesses = [0, 1, 2, 3, 15, 31, 63, 255, 4096, 8192, 24576, 32768, 49152, 65535]
        for ordinal in witnesses:
            with self.subTest(ordinal=ordinal):
                record = generate_record(self.bank, ordinal)
                summary = validate_record(record)
                self.assertEqual(summary["ordinal"], ordinal)
                self.assertEqual(
                    summary["semantic_signature_sha256"],
                    record["semantic_signature_sha256"],
                )

    def test_every_axis_changes_the_semantic_signature(self) -> None:
        origin = (0, 0, 0, 0, 0, 0, 0)
        origin_signature = generate_record(
            self.bank, rank_coordinate(origin)
        )["semantic_signature_sha256"]
        for index, size in enumerate((8, 8, 4, 8, 4, 4, 2)):
            changed = list(origin)
            changed[index] = 1 % size
            signature = generate_record(
                self.bank, rank_coordinate(changed)
            )["semantic_signature_sha256"]
            with self.subTest(axis=index):
                self.assertNotEqual(signature, origin_signature)

    def test_mutated_candidate_label_is_killed(self) -> None:
        record = generate_record(self.bank, 0)
        mutant = copy.deepcopy(record)
        mutant["generator_candidate_result"]["status"] = "unresolved"
        with self.assertRaisesRegex(OracleError, "candidate result"):
            validate_record(mutant)

    def test_authority_escalation_is_killed(self) -> None:
        record = generate_record(self.bank, 0)
        mutant = copy.deepcopy(record)
        mutant["authority"]["may_authorize_external_effects"] = True
        with self.assertRaisesRegex(OracleError, "authority"):
            validate_record(mutant)

    def test_semantic_mutation_invalidates_signature(self) -> None:
        record = generate_record(self.bank, 0)
        mutant = copy.deepcopy(record)
        mutant["semantic_core"]["world"]["facts"][1]["truth"] = "F"
        with self.assertRaisesRegex(OracleError, "signature"):
            validate_record(mutant)

    def test_oracle_source_does_not_import_generator(self) -> None:
        oracle_path = ROOT / "synthetic_deontic_oracle.py"
        tree = ast.parse(oracle_path.read_text(encoding="utf-8"))
        imported = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        self.assertFalse(
            any(name.endswith("synthetic_deontic_kb") for name in imported)
        )


if __name__ == "__main__":
    unittest.main()
