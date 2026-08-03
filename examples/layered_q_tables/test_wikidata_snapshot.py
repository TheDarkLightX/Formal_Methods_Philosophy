import json
import unittest

from examples.layered_q_tables.wikidata_snapshot import SnapshotError, build_snapshot, traverse


def entity(qid, label, claims=None, lastrevid=1, modified="2026-01-01T00:00:00Z"):
    return {
        "id": qid,
        "labels": {"en": {"language": "en", "value": label}},
        "descriptions": {
            "en": {"language": "en", "value": f"Description of {label}"}
        },
        "lastrevid": lastrevid,
        "modified": modified,
        "claims": claims or {},
    }


def claim(pid, target, rank="normal"):
    return {"rank": rank, "mainsnak": {"snaktype": "value", "datavalue": {"type": "wikibase-entityid", "value": {"id": target}}}}


class FixtureFetch:
    endpoint = "https://www.wikidata.org/w/api.php"

    def __init__(self, entities):
        self.entities = entities
        self.calls = []

    def __call__(self, qids):
        self.calls.append(qids)
        return {"entities": {qid: self.entities[qid] for qid in qids if qid in self.entities}}


class WikidataSnapshotTests(unittest.TestCase):
    def test_canonicalization_duplicate_edges_and_deprecated_claims(self):
        data = {
            "Q1": entity("Q1", "One", {"P31": [claim("P31", "Q2"), claim("P31", "Q2"), claim("P31", "Q3", "deprecated")] }),
            "Q2": entity("Q2", "Two"),
        }
        result = traverse(("Q1",), ("P31",), {"max_nodes": 5, "max_requests": 5, "max_depth": 1, "batch_size": 2}, FixtureFetch(data))
        self.assertEqual(result["edges"], [{"source": "Q1", "pid": "P31", "target": "Q2"}])
        self.assertEqual([node["qid"] for node in result["nodes"]], ["Q1", "Q2"])

    def test_invalid_ids_are_rejected(self):
        with self.assertRaises(SnapshotError):
            traverse(("q1",), ("P31",), {}, lambda _: {"entities": {}})
        with self.assertRaises(SnapshotError):
            traverse(("Q1",), ("P0",), {}, lambda _: {"entities": {}})

    def test_api_error_envelope_is_not_classified_as_missing_data(self):
        with self.assertRaisesRegex(SnapshotError, "Wikidata API error maxlag"):
            traverse(
                ("Q1",),
                ("P31",),
                {},
                lambda _: {
                    "error": {
                        "code": "maxlag",
                        "info": "replica is temporarily lagged",
                    }
                },
            )

    def test_deterministic_bytes_with_frozen_timestamp(self):
        pack = {"schema_version": 1, "seed_qids": ["Q1"], "goal_proposals": [], "relation_pids": ["P31"]}
        raw = json.dumps(pack, sort_keys=True).encode()
        data = {"Q1": entity("Q1", "One", {"P31": [claim("P31", "Q2")]}), "Q2": entity("Q2", "Two")}
        first = build_snapshot(pack, raw, limits={"max_nodes": 5, "max_requests": 5, "max_depth": 1, "batch_size": 2}, fetch=FixtureFetch(data), retrieved_at="2026-01-01T00:00:00Z")
        second = build_snapshot(pack, raw, limits={"max_nodes": 5, "max_requests": 5, "max_depth": 1, "batch_size": 2}, fetch=FixtureFetch(data), retrieved_at="2026-01-01T00:00:00Z")
        self.assertEqual(json.dumps(first, sort_keys=True, separators=(",", ":")), json.dumps(second, sort_keys=True, separators=(",", ":")))
        self.assertEqual(first["provenance"]["canonical_graph_sha256"], second["provenance"]["canonical_graph_sha256"])
        self.assertEqual(first["graph"]["nodes"][0]["description"], "Description of One")

    def test_bounded_traversal_records_truncation_and_filters_edges(self):
        data = {"Q1": entity("Q1", "One", {"P31": [claim("P31", "Q2"), claim("P31", "Q3")]}), "Q2": entity("Q2", "Two"), "Q3": entity("Q3", "Three")}
        fetcher = FixtureFetch(data)
        result = traverse(("Q1",), ("P31",), {"max_nodes": 2, "max_requests": 1, "max_depth": 2, "batch_size": 1}, fetcher)
        self.assertTrue(result["truncated"])
        self.assertLessEqual(len(result["nodes"]), 2)
        self.assertLessEqual(result["request_count"], 1)
        self.assertTrue(all(edge["target"] in {node["qid"] for node in result["nodes"]} for edge in result["edges"]))

    def test_degree_cap_is_deterministic_and_marks_truncation(self):
        data = {
            "Q1": entity(
                "Q1",
                "One",
                {
                    "P31": [
                        claim("P31", "Q2"),
                        claim("P31", "Q3"),
                        claim("P31", "Q4"),
                    ]
                },
            ),
            "Q2": entity("Q2", "Two"),
            "Q3": entity("Q3", "Three"),
            "Q4": entity("Q4", "Four"),
        }
        result = traverse(
            ("Q1",),
            ("P31",),
            {
                "max_nodes": 4,
                "max_requests": 4,
                "max_depth": 1,
                "batch_size": 4,
                "max_targets_per_entity": 2,
            },
            FixtureFetch(data),
        )
        self.assertTrue(result["truncated"])
        self.assertEqual(
            result["edges"],
            [
                {"source": "Q1", "pid": "P31", "target": "Q2"},
                {"source": "Q1", "pid": "P31", "target": "Q3"},
            ],
        )

    def test_invalid_timestamp_and_duplicate_seed_fail_closed(self):
        pack = {
            "schema_version": 1,
            "seed_qids": ["Q1"],
            "goal_proposals": ["Q1"],
            "relation_pids": ["P31"],
        }
        with self.assertRaises(SnapshotError):
            build_snapshot(
                pack,
                b"{}",
                limits={},
                fetch=FixtureFetch({}),
                retrieved_at="not-a-time",
            )

        pack["goal_proposals"] = []
        with self.assertRaises(SnapshotError):
            build_snapshot(
                pack,
                b"{}",
                limits={},
                fetch=FixtureFetch({}),
                retrieved_at="2026-01-01T00:00:00+01:00",
            )

    def test_minimum_coverage_and_required_seed_gate(self):
        pack = {
            "schema_version": 1,
            "seed_qids": ["Q1"],
            "goal_proposals": ["Q2"],
            "relation_pids": ["P31"],
        }
        fetcher = FixtureFetch({"Q1": entity("Q1", "One")})
        with self.assertRaisesRegex(SnapshotError, "below min_nodes"):
            build_snapshot(
                pack,
                b"{}",
                limits={"min_nodes": 2},
                fetch=fetcher,
                retrieved_at="2026-01-01T00:00:00Z",
            )

        with self.assertRaisesRegex(SnapshotError, "missing required seed QIDs"):
            build_snapshot(
                pack,
                b"{}",
                limits={"require_all_seeds": True},
                fetch=FixtureFetch({"Q1": entity("Q1", "One")}),
                retrieved_at="2026-01-01T00:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
