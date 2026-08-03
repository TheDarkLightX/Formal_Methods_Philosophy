from __future__ import annotations

import copy
import gzip
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from examples.layered_q_tables import wordnet_snapshot
from examples.layered_q_tables.knowledge_q_table import (
    canonical_json_bytes,
    canonicalize_snapshot,
    validate_snapshot,
)
from examples.layered_q_tables.wordnet_snapshot import (
    WordNetSnapshotError,
    build_snapshot,
    load_seed_pack,
    validate_seed_pack,
)

ROOT_ID = "oewn-00000001-n"
CHILD_ID = "oewn-00000002-n"
THIRD_ID = "oewn-00000003-n"
FOURTH_ID = "oewn-00000004-n"


def deterministic_gzip(xml: str | bytes) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", mtime=0) as handle:
        handle.write(xml.encode("utf-8") if type(xml) is str else xml)
    return output.getvalue()


def fixture_xml(
    *,
    entries_first: bool = True,
    reverse_records: bool = False,
    reverse_relations: bool = False,
    version: str = "2025",
    license_uri: str = "https://creativecommons.org/licenses/by/4.0",
    extra_root_relation: tuple[str, str] | None = None,
) -> str:
    entries = [
        '<LexicalEntry id="entry-root"><Lemma writtenForm="Root" /></LexicalEntry>',
        '<LexicalEntry id="entry-child"><Lemma writtenForm="Child" /></LexicalEntry>',
        '<LexicalEntry id="entry-third"><Lemma writtenForm="Third" /></LexicalEntry>',
    ]
    relation_rows = [
        ("hypernym", CHILD_ID),
        ("also", THIRD_ID),
        ("similar", FOURTH_ID),
    ]
    if extra_root_relation is not None:
        relation_rows.append(extra_root_relation)
    if reverse_relations:
        relation_rows.reverse()

    def synset(
        synset_id: str,
        members: str,
        definition: str,
        relations: list[tuple[str, str]],
    ) -> str:
        relation_xml = "".join(
            f'<SynsetRelation relType="{relation}" target="{target}" />'
            for relation, target in relations
        )
        return (
            f'<Synset id="{synset_id}" members="{members}" '
            f'partOfSpeech="n" ili="i{synset_id[-10:-2]}" lexfile="noun.artifact">'
            f"<Definition>{definition}</Definition>{relation_xml}</Synset>"
        )

    synsets = [
        synset(ROOT_ID, "entry-root", "root definition", relation_rows),
        synset(
            CHILD_ID,
            "entry-child",
            "child definition",
            [("hypernym", ROOT_ID), ("also", THIRD_ID)],
        ),
        synset(THIRD_ID, "entry-third", "third definition", []),
        synset(FOURTH_ID, "", "fourth definition", []),
    ]
    if reverse_records:
        entries.reverse()
        synsets.reverse()
    body_parts = entries + synsets if entries_first else synsets + entries
    body = "".join(body_parts)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Lexicon id="oewn" label="Open English WordNet" language="en" '
        f'license="{license_uri}" version="{version}" '
        'url="https://en-word.net/static/english-wordnet-2025.xml.gz">'
        f"{body}</Lexicon>"
    )


class WordNetSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.directory = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def pack_for(self, source_bytes: bytes) -> dict[str, object]:
        return {
            "schema": "glassmind-wordnet-seeds-v1",
            "source": {
                "name": "Open English WordNet",
                "version": "2025",
                "url": "https://en-word.net/static/english-wordnet-2025.xml.gz",
                "license": "CC-BY-4.0",
                "expected_sha256": hashlib.sha256(source_bytes).hexdigest(),
            },
            "seed_synsets": [
                {"id": ROOT_ID, "label": "root", "role": "fixture root"}
            ],
            "goal_synsets": [],
            "relations": ["also", "hypernym", "similar"],
            "assumptions": ["The fixture relation is a directed lexical link."],
            "quarantined_proposals": [
                {
                    "proposal": "Treat a lexical edge as a proof.",
                    "reason": "The converter preserves navigation nonclaims.",
                }
            ],
        }

    def source_and_pack(
        self,
        xml: str | bytes,
        *,
        pack: dict[str, object] | None = None,
        source_name: str = "source.xml.gz",
    ) -> tuple[Path, dict[str, object], bytes]:
        source_bytes = deterministic_gzip(xml)
        source_path = self.directory / source_name
        source_path.write_bytes(source_bytes)
        selected_pack = self.pack_for(source_bytes) if pack is None else pack
        return source_path, selected_pack, source_bytes

    def build_fixture(
        self,
        xml: str | bytes | None = None,
        *,
        pack: dict[str, object] | None = None,
        max_nodes: int = 8,
        min_nodes: int = 1,
        max_depth: int = 3,
        max_relations_per_node: int = 8,
    ) -> dict[str, object]:
        source_path, selected_pack, _ = self.source_and_pack(
            fixture_xml() if xml is None else xml, pack=pack
        )
        return build_snapshot(
            source_path,
            selected_pack,
            retrieved_at="2026-01-01T00:00:00Z",
            max_nodes=max_nodes,
            min_nodes=min_nodes,
            max_depth=max_depth,
            max_relations_per_node=max_relations_per_node,
        )

    def cli_args(self, source_path: Path, pack_path: Path, output_path: Path) -> list[str]:
        return [
            "--source",
            str(source_path),
            "--seed-pack",
            str(pack_path),
            "--output",
            str(output_path),
            "--retrieved-at",
            "2026-01-01T00:00:00Z",
            "--max-nodes",
            "8",
            "--min-nodes",
            "1",
            "--max-depth",
            "3",
            "--max-relations-per-node",
            "8",
        ]

    def test_fixture_gzip_bytes_are_deterministic_with_zero_mtime(self) -> None:
        xml = fixture_xml()
        self.assertEqual(deterministic_gzip(xml), deterministic_gzip(xml))

    def test_source_hash_is_checked_before_xml_parsing(self) -> None:
        source_path, pack, source_bytes = self.source_and_pack("<Lexicon>")
        pack["source"]["expected_sha256"] = hashlib.sha256(
            deterministic_gzip(fixture_xml())
        ).hexdigest()
        with mock.patch.object(
            wordnet_snapshot.ET,
            "iterparse",
            side_effect=AssertionError("XML parser must not run before hash validation"),
        ), self.assertRaisesRegex(WordNetSnapshotError, "source hash does not match"):
            build_snapshot(
                source_path,
                pack,
                retrieved_at="2026-01-01T00:00:00Z",
                max_nodes=8,
                min_nodes=1,
                max_depth=1,
                max_relations_per_node=2,
            )
        self.assertEqual(
            pack["source"]["expected_sha256"],
            hashlib.sha256(deterministic_gzip(fixture_xml())).hexdigest(),
        )
        self.assertNotEqual(source_bytes, deterministic_gzip(fixture_xml()))

    def test_seed_pack_requires_exact_release_and_license(self) -> None:
        source_bytes = deterministic_gzip(fixture_xml())
        for field, value, message in (
            ("version", "2024", "release version"),
            ("license", "CC0-1.0", "license"),
        ):
            pack = self.pack_for(source_bytes)
            pack["source"][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(
                WordNetSnapshotError, message
            ):
                validate_seed_pack(pack)

    def test_xml_release_and_license_must_match_exact_values(self) -> None:
        for version, license_uri, message in (
            ("2024", "https://creativecommons.org/licenses/by/4.0", "release version"),
            ("2025", "https://creativecommons.org/licenses/by/3.0", "license"),
        ):
            xml = fixture_xml(version=version, license_uri=license_uri)
            with self.subTest(message=message), self.assertRaisesRegex(
                WordNetSnapshotError, message
            ):
                self.build_fixture(xml)

    def test_root_label_is_checked_case_insensitively_and_mismatches_fail(self) -> None:
        pack = self.pack_for(deterministic_gzip(fixture_xml()))
        self.assertEqual(self.build_fixture(pack=pack)["graph"]["nodes"][0]["label"], "Root")

        wrong_pack = copy.deepcopy(pack)
        wrong_pack["seed_synsets"][0]["label"] = "not root"
        with self.assertRaisesRegex(WordNetSnapshotError, "does not identify"):
            self.build_fixture(pack=wrong_pack)

    def test_xml_order_does_not_change_labels_or_canonical_graph(self) -> None:
        first = self.build_fixture(
            fixture_xml(entries_first=False, reverse_records=False, reverse_relations=False)
        )
        second = self.build_fixture(
            fixture_xml(entries_first=False, reverse_records=True, reverse_relations=True)
        )
        self.assertEqual(first["graph"], second["graph"])
        self.assertEqual(first["counts"], second["counts"])
        self.assertEqual(
            first["provenance"]["canonical_graph_sha256"],
            second["provenance"]["canonical_graph_sha256"],
        )

    def test_cycles_terminate_and_relation_cap_is_deterministic(self) -> None:
        snapshot = self.build_fixture(
            max_nodes=3,
            max_depth=20,
            max_relations_per_node=2,
        )
        node_ids = [node["id"] for node in snapshot["graph"]["nodes"]]
        self.assertEqual(node_ids, [ROOT_ID, CHILD_ID, THIRD_ID])
        self.assertEqual(len(node_ids), len(set(node_ids)))
        root_edges = [
            edge for edge in snapshot["graph"]["edges"] if edge["source"] == ROOT_ID
        ]
        self.assertEqual([edge["relation"] for edge in root_edges], ["also", "hypernym"])
        self.assertTrue(snapshot["truncated"])
        self.assertTrue(
            all(
                edge["source_direction"] == "oewn_synset_relation_source_to_target"
                for edge in snapshot["graph"]["edges"]
            )
        )

    def test_exact_integer_bounds_reject_booleans(self) -> None:
        parameters = {
            "max_nodes": 8,
            "min_nodes": 1,
            "max_depth": 3,
            "max_relations_per_node": 8,
        }
        for name in parameters:
            invalid = dict(parameters)
            invalid[name] = True
            with self.subTest(name=name), self.assertRaises(WordNetSnapshotError):
                self.build_fixture(**invalid)

    def test_seed_pack_is_closed_and_rejects_malformed_nested_values(self) -> None:
        source_bytes = deterministic_gzip(fixture_xml())
        mutations = []

        extra_field = self.pack_for(source_bytes)
        extra_field["unexpected"] = True
        mutations.append(extra_field)

        unhashable_relation = self.pack_for(source_bytes)
        unhashable_relation["relations"] = [["hypernym"]]
        mutations.append(unhashable_relation)

        bad_assumption = self.pack_for(source_bytes)
        bad_assumption["assumptions"] = [1]
        mutations.append(bad_assumption)

        bad_quarantine = self.pack_for(source_bytes)
        bad_quarantine["quarantined_proposals"] = [{"proposal": "missing reason"}]
        mutations.append(bad_quarantine)

        bad_root = self.pack_for(source_bytes)
        bad_root["seed_synsets"][0]["role"] = True
        mutations.append(bad_root)

        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(
                WordNetSnapshotError
            ):
                validate_seed_pack(mutation)

        seed_path = self.directory / "duplicate-keys.json"
        seed_path.write_text(
            '{"schema":"glassmind-wordnet-seeds-v1","schema":"duplicate"}',
            encoding="utf-8",
        )
        with self.assertRaises(WordNetSnapshotError):
            load_seed_pack(seed_path)

    def test_malformed_xml_and_truncated_gzip_are_normalized(self) -> None:
        malformed_xml = fixture_xml().replace("</Lexicon>", "", 1)
        with self.assertRaisesRegex(
            WordNetSnapshotError, "not valid bounded gzip XML"
        ):
            self.build_fixture(malformed_xml)

        source_path, pack, source_bytes = self.source_and_pack(fixture_xml())
        truncated_path = self.directory / "truncated.xml.gz"
        truncated_bytes = source_bytes[:-8]
        truncated_path.write_bytes(truncated_bytes)
        pack["source"]["expected_sha256"] = hashlib.sha256(truncated_bytes).hexdigest()
        with self.assertRaisesRegex(
            WordNetSnapshotError, "not valid bounded gzip XML"
        ):
            build_snapshot(
                truncated_path,
                pack,
                retrieved_at="2026-01-01T00:00:00Z",
                max_nodes=8,
                min_nodes=1,
                max_depth=3,
                max_relations_per_node=8,
            )
        self.assertTrue(source_path.exists())

    def test_source_os_failures_are_normalized(self) -> None:
        source_path, pack, _ = self.source_and_pack(fixture_xml())
        with mock.patch.object(
            Path, "open", side_effect=OSError("fixture read failure")
        ), self.assertRaises(WordNetSnapshotError):
            build_snapshot(
                source_path,
                pack,
                retrieved_at="2026-01-01T00:00:00Z",
                max_nodes=8,
                min_nodes=1,
                max_depth=3,
                max_relations_per_node=8,
            )

    def test_dtd_and_entity_declarations_are_rejected(self) -> None:
        xml = (
            '<?xml version="1.0"?><!DOCTYPE Lexicon '
            '[<!ENTITY fixture_label "Root">]>'
            '<Lexicon id="oewn" label="Open English WordNet" language="en" '
            'license="https://creativecommons.org/licenses/by/4.0" version="2025" '
            'url="https://en-word.net/static/english-wordnet-2025.xml.gz">'
            '<LexicalEntry id="entry-root"><Lemma writtenForm="&fixture_label;" />'
            '</LexicalEntry><Synset id="oewn-00000001-n" members="entry-root">'
            '<Definition>root</Definition></Synset></Lexicon>'
        )
        with self.assertRaisesRegex(WordNetSnapshotError, "DTD/entity"):
            self.build_fixture(xml)

        with self.assertRaisesRegex(WordNetSnapshotError, "DTD/entity"):
            self.build_fixture(xml.encode("utf-16"))

        external = fixture_xml().replace(
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<!DOCTYPE LexicalResource SYSTEM "https://example.invalid/evil.dtd">',
            1,
        )
        with self.assertRaisesRegex(WordNetSnapshotError, "DTD/entity"):
            self.build_fixture(external)

    def test_exact_published_oewn_external_doctype_is_allowed(self) -> None:
        xml = fixture_xml().replace(
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<!DOCTYPE LexicalResource SYSTEM '
            '"http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd">',
            1,
        )
        snapshot = self.build_fixture(xml)
        self.assertEqual(snapshot["counts"]["nodes"], 4)

    def test_small_uncompressed_bound_rejects_oversized_decompression(self) -> None:
        xml = fixture_xml()
        with mock.patch.object(
            wordnet_snapshot, "MAX_UNCOMPRESSED_BYTES", len(xml.encode("utf-8")) - 1
        ), self.assertRaisesRegex(WordNetSnapshotError, "uncompressed"):
            self.build_fixture(xml)

    def test_source_counts_bound_unfiltered_synsets_and_relations(self) -> None:
        with mock.patch.object(
            wordnet_snapshot, "MAX_SOURCE_SYNSETS", 3
        ), self.assertRaisesRegex(WordNetSnapshotError, "synset count"):
            self.build_fixture()

        xml = fixture_xml(extra_root_relation=("not_allowed", CHILD_ID))
        with mock.patch.object(
            wordnet_snapshot, "MAX_SOURCE_EDGES", 5
        ), self.assertRaisesRegex(WordNetSnapshotError, "relation count"):
            self.build_fixture(xml)

    def test_canonical_snapshot_hash_counts_and_directed_nonclaims(self) -> None:
        snapshot = self.build_fixture()
        validate_snapshot(snapshot)
        self.assertEqual(snapshot, canonicalize_snapshot(snapshot))
        self.assertEqual(snapshot["counts"]["nodes"], len(snapshot["graph"]["nodes"]))
        self.assertEqual(snapshot["counts"]["edges"], len(snapshot["graph"]["edges"]))
        self.assertEqual(
            snapshot["provenance"]["canonical_graph_sha256"],
            hashlib.sha256(canonical_json_bytes(snapshot["graph"])).hexdigest(),
        )
        self.assertIn(
            "Reverse graph browsing does not assert an inverse lexical predicate.",
            snapshot["provenance"]["nonclaims"],
        )

    def test_cli_failure_keeps_output_untouched_and_normalizes_output_os_errors(self) -> None:
        source_path, pack, source_bytes = self.source_and_pack(fixture_xml())
        pack_path = self.directory / "seed-pack.json"
        pack_path.write_text(json.dumps(pack), encoding="utf-8")
        output_path = self.directory / "snapshot.json"
        output_path.write_bytes(b"existing output")

        source_path.write_bytes(source_bytes[:-8])
        return_code = wordnet_snapshot._main(
            self.cli_args(source_path, pack_path, output_path)
        )
        self.assertEqual(return_code, 2)
        self.assertEqual(output_path.read_bytes(), b"existing output")

        valid_source_path, valid_pack, _ = self.source_and_pack(
            fixture_xml(), source_name="valid.xml.gz"
        )
        valid_pack_path = self.directory / "valid-seed-pack.json"
        valid_pack_path.write_text(json.dumps(valid_pack), encoding="utf-8")
        output_directory = self.directory / "output-directory"
        output_directory.mkdir()
        return_code = wordnet_snapshot._main(
            self.cli_args(valid_source_path, valid_pack_path, output_directory)
        )
        self.assertEqual(return_code, 2)
        self.assertTrue(output_directory.is_dir())


if __name__ == "__main__":
    unittest.main()
