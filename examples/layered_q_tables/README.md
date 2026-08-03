# GlassMind-256

GlassMind-256 is the reproducible example for Tutorial 71. Its primary
demonstrator compiles a pinned lexical knowledge graph, a bounded deontic
action gate, a declared utility model, and a deterministic Bellman recurrence
into 256 horizon-indexed Q layers.

The checked architecture is:

```text
LLM seed proposals + pinned source
  -> bounded canonical knowledge snapshot
  -> O/F/P action mask
  -> declared utility and transition model
  -> layered Q bytes
  -> exhaustive replay and reason receipt
```

The language model proposes seeds and challenge ideas. It does not own source
facts, normative acceptance, rewards, table values, or verification labels.

## Exact profiles

| Profile | Shape | Raw float32 data |
| --- | --- | ---: |
| Public | `(256, 6144, 8)` | 50,331,648 bytes, exactly 48 MiB |
| Full local | `(256, 65536, 8)` | 536,870,912 bytes, exactly 512 MiB |

The public table factors its states as six required decisions, 256 graph-node
slots, and four two-bit evidence masks. The full table uses 16 decisions and
1,024 graph-node slots. Table generation is memory-mapped and chunked.

## Files

- `wordnet_seed_proposals.json` contains bounded, quarantined source proposals.
- `wordnet_snapshot.py` converts one hash-pinned Open English WordNet release
  into a canonical directed graph without network access.
- `planner_required_decisions_public.json` and
  `planner_required_decisions_full.json` declare the planner decision records.
- `deontic_kernel.py` implements a finite input/output-style O/F/P profile.
- `knowledge_q_table.py` compiles the graph, deontic mask, utility, and Q layers.
- `policy_profile_demo.py` shows two declared utility profiles producing
  different Q bytes under the same facts, transitions, and hard norm mask.
- `proof_carrying_decision.schema.json` defines the next-stage receipt envelope.
- `synthetic_deontic_templates.json` contains Luna-proposed semantic seed
  families for a 65,536-record non-authoritative problem bank.
- `synthetic_deontic_kb.py` expands the finite lattice, while
  `synthetic_deontic_oracle.py` independently checks its historical integrity
  run. The later v0 audit, not that integrity scan, owns the current NO-GO
  assessment.
- `synthetic_deontic_luna_v1_templates.json` defines the repaired 16-domain,
  16-topology causal lattice. `synthetic_deontic_luna_v1.py` expands it, and
  `synthetic_deontic_luna_v1_oracle.py` reconstructs raw records without
  importing the generator.

Open English WordNet 2025 is CC-BY 4.0. The source used here has SHA-256:

```text
9ca6d1dcb75f822fdd66617f7d9da48142ace38dd544d6ad5e2feca1674ad3fe
```

## Reproduce the public table

Download the pinned source into the ignored local artifact directory:

```bash
mkdir -p artifacts/local/sources
curl -L \
  https://en-word.net/static/english-wordnet-2025.xml.gz \
  -o artifacts/local/sources/english-wordnet-2025.xml.gz
sha256sum artifacts/local/sources/english-wordnet-2025.xml.gz
```

Build the 256-node canonical snapshot:

```bash
python3 -m examples.layered_q_tables.wordnet_snapshot \
  --source artifacts/local/sources/english-wordnet-2025.xml.gz \
  --seed-pack examples/layered_q_tables/wordnet_seed_proposals.json \
  --output assets/data/glassmind_wordnet_256.json \
  --retrieved-at 2026-08-02T00:20:57Z \
  --max-nodes 256 --min-nodes 256 \
  --max-depth 6 --max-relations-per-node 12
```

Build and replay the Q table:

```bash
python3 -m examples.layered_q_tables.knowledge_q_table build \
  --profile public \
  --snapshot assets/data/glassmind_wordnet_256.json \
  --decisions examples/layered_q_tables/planner_required_decisions_public.json \
  --evidence-deontic \
  --deontic-logic-semantics bounded-finite-detachment-v1 \
  --deontic-logic-semantics-sha256 1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df \
  --deontic-profile neutral-evidence-completion-v1 \
  --deontic-profile-sha256 4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa \
  --esso-evidence-hash model_sha256=78e5d57a463365d21741045a64a556176427963eb81aae0c0a8d48e0ee56b270 \
  --esso-evidence-hash ir_sha256=0fed6db3d9a4a1927cda867e0683c5a257c9feb9471452f7eb5621820900b965 \
  --output assets/data/glassmind_knowledge_256_50mb.npy \
  --manifest assets/data/glassmind_knowledge_256_50mb.manifest.json

python3 -m examples.layered_q_tables.knowledge_q_table verify \
  --profile public \
  --snapshot assets/data/glassmind_wordnet_256.json \
  --decisions examples/layered_q_tables/planner_required_decisions_public.json \
  --evidence-deontic \
  --deontic-logic-semantics bounded-finite-detachment-v1 \
  --deontic-logic-semantics-sha256 1a95da0066a4bdb8a8fb6cfde4629eab95ac35d3b814bfcaf21e10328ed355df \
  --deontic-profile neutral-evidence-completion-v1 \
  --deontic-profile-sha256 4046ef1d6377f9eed77d86b76f7f813268d51bef6af8b2fd5a93c355b8c51efa \
  --esso-evidence-hash model_sha256=78e5d57a463365d21741045a64a556176427963eb81aae0c0a8d48e0ee56b270 \
  --esso-evidence-hash ir_sha256=0fed6db3d9a4a1927cda867e0683c5a257c9feb9471452f7eb5621820900b965 \
  --table assets/data/glassmind_knowledge_256_50mb.npy \
  --manifest assets/data/glassmind_knowledge_256_50mb.manifest.json \
  --report assets/data/glassmind_knowledge_256_50mb.verify.json
```

Build the 512 MiB local profile by replacing `public`, the snapshot, decision
pack, output, and report names with the full-profile names shown in the
tutorial. The large NPY file belongs under `artifacts/local/`, which is ignored
by Git.

## Deontic boundary

The production-named evidence adapter is fail-closed:

- padded graph slots allow only `abstain_or_escalate`;
- a real non-target or evidence-incomplete state permits navigation and
  abstention but forbids resolution;
- a complete target state makes `resolve` obligatory and exclusive;
- missing or malformed adapters, premature resolution, and empty terminal
  action sets reject compilation.

The ESSO run checks finite adapter invariants, not the full Python program or a
universal deontic logic. The Q recurrence ranks only actions admitted by the
mask. WordNet links remain source-attributed lexical relations, not proofs. The
exhaustive replay shares planner and Bellman helpers with generation, so it is
a deterministic consistency check rather than an independent implementation.

## Synthetic deontic problem bank, Luna v1 QUARANTINED_CORPUS

Status: **`QUARANTINED_CORPUS`**. The exact label comes before the measurements
because the measurements do not override missing release evidence.

V1 replaces the behaviorally shallow global v0 axes with topology-local state,
resolution, and defeater variants:

```text
16 domains x 16 topology programs x 4 evidence values
           x 4 local states x 4 resolutions x 4 defeaters
         = 65,536 records
```

The durable raw-corpus analyzer accepted all 65,536 records, found 322 normalized
dispositions, classified all 393,216 one-axis pairs, and observed all 3,072
declared spanning-effect witnesses. It counted 177,600 effects and 215,616 checked
invariants. The counterfactual receipt-set root is
`9ccf9ae8d13c9b4fb12cee0503af4010a35ac73c75b3457c4fda528c21a0c2ab`.

These results do not promote the artifact. The reducer assigned
**`QUARANTINED_CORPUS`** because mandatory release bindings, the complete
schema-derived mutation campaign, retained receipt bodies, an independent
call-graph receipt, and a complete two-build replay receipt remain missing.
All configured formal and research-tool lanes are `SKIP` for this exact
profile. See the
[`v1 evidence report`](../../research/synthetic_deontic_knowledge_base_v1.md)
and [release gates](../../research/synthetic_deontic_luna_v1_release_gates.md).
The canonical [raw JSON report](../../assets/data/glassmind_synthetic_deontic_luna_v1_65536.verify.json)
contains the exact gate rows and residual nonclaims.

Build and analyze the candidate in a fresh ignored directory. Both commands
are no-overwrite by design:

```bash
mkdir -p artifacts/local
run_dir="$(mktemp -d artifacts/local/sdk-luna-v1.XXXXXX)"

python3 -m examples.layered_q_tables.synthetic_deontic_luna_v1 \
  build \
  --template-bank examples/layered_q_tables/synthetic_deontic_luna_v1_templates.json \
  --semantics-spec research/synthetic_deontic_luna_v1_semantics.md \
  --output-dir "$run_dir/corpus" \
  --manifest "$run_dir/manifest.json"

python3 -m examples.layered_q_tables.synthetic_deontic_luna_v1_oracle \
  --template examples/layered_q_tables/synthetic_deontic_luna_v1_templates.json \
  --semantics research/synthetic_deontic_luna_v1_semantics.md \
  --release-gates research/synthetic_deontic_luna_v1_release_gates.md \
  analyze "$run_dir/corpus" \
  --report "$run_dir/verify.json"
```

The stored report has SHA-256
`38b6b3fd208e89c6cba7d4c3911f74326325e628b513d3fef217d75b5590460a`.
The 16 gzip shards total 20,852,762 bytes. The uncompressed JSONL records total
500,934,455 bytes. These sizes measure packaging, not knowledge or
intelligence.

## Legacy synthetic deontic problem bank, v0 NO-GO

The companion corpus expands a mathematically exact semantic lattice:

```text
8 domains x 8 norm graphs x 4 premise values x 8 time states
          x 4 priority states x 4 exception states x 2 revisions
        = 65,536 records
```

This was intended as semantic fixture generation rather than lexical
paraphrasing. The records cover four-valued premises, O/F/P combinations,
conflicts, deadlines, contrary-to-duty repairs, priorities, exceptions, and
revocation. Every record states that it is synthetic, non-authoritative, not
law, and unable to authorize external effects.

Build and independently check the corpus:

```bash
python3 -m examples.layered_q_tables.synthetic_deontic_kb build \
  --template-bank examples/layered_q_tables/synthetic_deontic_templates.json \
  --output-dir assets/data/glassmind_synthetic_deontic_65536 \
  --manifest assets/data/glassmind_synthetic_deontic_65536.manifest.json

python3 -m examples.layered_q_tables.synthetic_deontic_oracle \
  --corpus-dir assets/data/glassmind_synthetic_deontic_65536 \
  --manifest assets/data/glassmind_synthetic_deontic_65536.manifest.json \
  --report assets/data/glassmind_synthetic_deontic_65536.verify.json
```

The historical oracle checked all 65,536 records and found 65,536 unique
semantic signatures, but those facts are not evidence of 65,536 behaviors. A
later Luna-Max audit assigned v0 **NO-GO** after finding only 49
role-normalized behaviors, accepted re-sealed hostile records, incorrect
contrary-to-duty behavior, ambiguous deadlines, dormant axes, and unexecuted
counterfactual claims. See
[`synthetic_deontic_kb_luna_audit_v0.md`](../../research/synthetic_deontic_kb_luna_audit_v0.md).
The artifact is retained as a regression corpus. SMT, ESSO, Tau, Lean, and HOL
checks have not been run on its raw records.

## Policy counterfactual

Generate the small profile comparison:

```bash
python3 -m examples.layered_q_tables.policy_profile_demo \
  --output assets/data/glassmind_policy_comparison.json
```

It keeps facts, transitions, and hard norms fixed. A latency-weighted profile
chooses `inspect -> publish`; a synthetic equal-stakeholder-sum profile chooses
`inspect -> redact -> publish`. This demonstrates policy-relative compilation.
It does not establish the stakeholder list, scores, weights, or utilitarianism
as morally correct.

## Legacy synthetic-grid baseline

`glassmind.py` and `glassmind_scenario_pack.json` preserve the earlier
synthetic emergency-routing baseline. That implementation is still useful for
testing LLM proposals against a fully deterministic simulator and a challenge
grammar. Its files use four actions and a different state factorization. They
must not be confused with the knowledge and deontic artifacts above.

## Tests

```bash
PYTHONPATH=. pytest -q examples/layered_q_tables
ruff check examples/layered_q_tables
python3 -m compileall -q examples/layered_q_tables
```

The `ruff` installation path varies by machine. Run it from the active
environment or install it as a development dependency.

## Nonclaims

"Deterministic thinker" is an engineering nickname. The verified claim is
exact finite-horizon planning in the declared finite model. The artifacts do
not establish general intelligence, real-world ethical correctness, WordNet
truth, temporal-deontic completeness, or authority to execute external
effects.
