#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "assets" / "data" / "qns_ontology_compiler_traces.json"
WORD_RE = re.compile(r"[a-z0-9_]+")
TOP8 = 0xFF


@dataclass(frozen=True)
class Atom:
    bit: int
    name: str
    phrases: tuple[str, ...]

    @property
    def mask(self) -> int:
        return 1 << self.bit


ATOMS = (
    Atom(0, "registry_verified", ("registry verified", "registered", "registry exists")),
    Atom(1, "liquidity_deep", ("deep liquidity", "liquidity deep", "liquid market")),
    Atom(2, "token_old_enough", ("old token", "aged token", "token old enough")),
    Atom(3, "provenance_clean", ("clean provenance", "provenance clean", "clean history")),
    Atom(4, "governance_separated", ("separated governance", "governance separated")),
    Atom(5, "oracle_stable", ("stable oracle", "oracle stable")),
    Atom(6, "sanction_risk", ("sanction risk", "sanctioned", "blacklisted")),
    Atom(7, "human_review_required", ("human review", "manual review", "review required")),
)

AMBIGUOUS_PHRASES = {
    "review": ("human_review_required", "sanction_risk"),
    "risk": ("sanction_risk", "human_review_required"),
    "oracle": ("oracle_stable",),
    "governance": ("governance_separated",),
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "appears",
    "are",
    "as",
    "audited",
    "but",
    "claimed",
    "evidence",
    "exists",
    "for",
    "is",
    "language",
    "market",
    "of",
    "phrase",
    "precise",
    "required",
    "requested",
    "the",
    "token",
    "without",
    "with",
}

CASES = (
    {
        "name": "clean_collateral_report",
        "text": (
            "Registry verified, deep liquidity, old token, clean provenance, "
            "separated governance, stable oracle."
        ),
    },
    {
        "name": "ambiguous_risk_report",
        "text": (
            "Registry exists, liquidity is deep, review is requested, and risk "
            "language appears without a precise audited phrase."
        ),
    },
    {
        "name": "unknown_term_report",
        "text": (
            "Registry verified and stable oracle, but quantum sentiment and vibe "
            "momentum are claimed as evidence."
        ),
    },
)


def normalize(text: str) -> str:
    return " ".join(WORD_RE.findall(text.lower()))


def atom_by_name() -> dict[str, Atom]:
    return {atom.name: atom for atom in ATOMS}


def compile_text(text: str) -> dict[str, Any]:
    norm = normalize(text)
    atoms = atom_by_name()
    observed_mask = 0
    matched_phrases: list[dict[str, Any]] = []
    occupied_tokens: set[str] = set()
    for atom in ATOMS:
        for phrase in atom.phrases:
            if phrase in norm:
                observed_mask |= atom.mask
                matched_phrases.append({"phrase": phrase, "atom": atom.name})
                occupied_tokens.update(phrase.split())
                break
    ambiguous_mask = 0
    ambiguous_rows = []
    for phrase, names in AMBIGUOUS_PHRASES.items():
        phrase_tokens = set(phrase.split())
        covered_by_exact_match = phrase_tokens <= occupied_tokens
        if (
            phrase in norm
            and not covered_by_exact_match
            and not any(row["phrase"] == phrase for row in matched_phrases)
        ):
            mask = 0
            for name in names:
                mask |= atoms[name].mask
            ambiguous_mask |= mask
            ambiguous_rows.append({"phrase": phrase, "candidate_atoms": list(names), "mask": mask})
            occupied_tokens.update(phrase.split())
    tokens = WORD_RE.findall(text.lower())
    unknown_terms = sorted(
        {
            token
            for token in tokens
            if token not in STOP_WORDS and token not in occupied_tokens
            and not any(token in phrase.split() for atom in ATOMS for phrase in atom.phrases)
        }
    )
    unknown_quarantine = len(unknown_terms) > 0
    exact_mask = observed_mask & (TOP8 ^ ambiguous_mask)
    review_mask = ambiguous_mask | ((1 << 7) if unknown_quarantine else 0)
    return {
        "text": text,
        "normalized": norm,
        "observed_mask": observed_mask,
        "ambiguous_mask": ambiguous_mask,
        "exact_mask": exact_mask,
        "review_mask": review_mask,
        "unknown_quarantine": unknown_quarantine,
        "unknown_terms": unknown_terms,
        "matched_phrases": matched_phrases,
        "ambiguous_phrases": ambiguous_rows,
        "observed_atoms": [atom.name for atom in ATOMS if observed_mask & atom.mask],
        "exact_atoms": [atom.name for atom in ATOMS if exact_mask & atom.mask],
        "review_atoms": [atom.name for atom in ATOMS if review_mask & atom.mask],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile controlled ontology text to qNS masks.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = []
    for case in CASES:
        compiled = compile_text(case["text"])
        rows.append({"name": case["name"], **compiled})
    artifact = {
        "schema": "qns_ontology_compiler_traces_v1",
        "generator": "scripts/compile_qns_ontology_masks.py",
        "scope": {
            "claim": (
                "A deterministic audited ontology compiler can map bounded text "
                "phrases into qns8 masks while quarantining ambiguity and unknown "
                "terms before Tau reasoning."
            ),
            "not_claimed": [
                "not general natural-language understanding",
                "not upstream nlang semantics",
                "not semantic correctness outside the audited phrase table",
                "not a replacement for human ontology governance",
            ],
        },
        "atom_universe": [
            {"bit": atom.bit, "name": atom.name, "phrases": list(atom.phrases)}
            for atom in ATOMS
        ],
        "ambiguous_phrases": {
            phrase: list(names) for phrase, names in AMBIGUOUS_PHRASES.items()
        },
        "summary": {
            "ok": True,
            "case_count": len(rows),
            "ambiguous_case_count": sum(1 for row in rows if row["ambiguous_mask"] != 0),
            "unknown_quarantine_count": sum(1 for row in rows if row["unknown_quarantine"]),
            "total_unknown_terms": sum(len(row["unknown_terms"]) for row in rows),
            "exact_mask_nonzero_count": sum(1 for row in rows if row["exact_mask"] != 0),
        },
        "rows": rows,
    }
    out = args.out if args.out.is_absolute() else ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": artifact["summary"]["ok"],
                "out": str(out.relative_to(ROOT)),
                "case_count": artifact["summary"]["case_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
