# Synthetic Deontic Knowledge Base v0

Status: historical candidate, **NO-GO for semantic promotion**.

The original integrity checks below are reproducible, but a later Luna-Max
falsification pass found that they were not strong enough to establish the
claimed semantic diversity or oracle boundary. The decisive findings are in
the [v0 audit](synthetic_deontic_kb_luna_audit_v0.md). This file is retained as
negative knowledge and as a regression target, not as a promoted knowledge
base.

This document specifies a large deontic problem bank for testing bounded
decision systems. It contains exactly 65,536 generated records. Each record is
a finite decision problem with typed actors, actions, facts, norms, conflicts,
time, priority, exceptions, revision state, a candidate result, and explicit
negative knowledge.

The artifact is not a legal, ethical, or factual authority. Its frequencies do
not measure how common any norm or outcome is in the world. It cannot authorize
an external effect.

## Why this is not a lexical knowledge base

Luna-Max research lanes proposed two semantic lattices and an adversarial
release protocol. The reducer selected the lattice with more deontic failure
modes:

```text
8 typed domains
  x 8 norm graphs
  x 4 premise values
  x 8 temporal states
  x 4 priority states
  x 4 exception states
  x 2 revision states
  = 65,536 records
```

The domains bind different actor, action, and relation types. The other six
axes alter the normalized rule graph, fact value, clock, defeat relation,
exception evidence, or norm revision. Changing only wording cannot create a
new semantic signature.

The premise values are true, false, unknown, and inconsistent. The time axis
contains atemporal, before-window, deadline, after-deadline, performed,
unperformed, unknown-clock, and contradictory-clock cases. The norm graphs
cover obligations, prohibitions, permissions, same-action conflicts,
exclusive obligations, deadlines, and contrary-to-duty repairs.

## Stable identity and sharding

For each record, the generator first constructs a closed `semantic_core`.
Coordinates, display labels, candidate results, and hashes are not part of
that core. The semantic signature is:

```text
SHA-256(canonical-json(semantic_core))
```

The stable ID contains the full 256-bit digest. The record hash separately
binds the candidate result, negative knowledge, authority boundary, and
projection status. This separation prevents an ordinal or a fluent label from
hiding duplicate semantics.

Records are assigned to 16 shards by the first hexadecimal character of the
full semantic signature. The manifest binds every shard's compressed and
uncompressed byte length and SHA-256 digest. It also binds a corpus root over
`(ordinal, record_hash)` pairs and a set root over sorted semantic signatures.

## Independent oracle boundary

The release oracle does not import the generator, template loader,
canonicalizer, or candidate evaluator. It independently:

1. parses strict canonical JSON and rejects duplicate keys;
2. validates the closed record shape and all actor, action, fact, norm,
   conflict, priority, exception, repair, and clock references;
3. derives all seven coordinates from the semantic IR;
4. recomputes semantic signatures, record hashes, shard hashes, and roots;
5. evaluates the named four-valued finite semantics;
6. compares the full result, not one classification label;
7. derives negative-knowledge and current-kernel projection labels; and
8. recomputes every coverage count from raw records.

The semantics are deliberately bounded. Unknown or inconsistent
safety-relevant premises, clocks, or exception evidence escalate. A true
exception defeats only its named norm. Revoked norms do not detach. Priority
resolves only an explicit conflict edge and a cycle or equal unresolved rank
escalates. A deadline violation can activate a contrary-to-duty repair, but
the repair does not erase the primary violation.

## Historical integrity result

The original build and oracle run reported the following integrity metrics:

| Check | Result |
| --- | ---: |
| Records checked | 65,536 |
| Unique ordinals | 65,536 |
| Unique stable IDs | 65,536 |
| Unique semantic signatures | 65,536 |
| Independent-oracle errors | 0 |
| Resolved fixtures | 6,944 |
| Unresolved fixtures | 58,592 |
| Exact current-kernel projections | 1,152 |
| Explicitly quarantined projections | 64,384 |
| Negative-knowledge items | 285,056 |
| Compressed corpus size | about 9.3 MiB |

The high unresolved count is intentional. The lattice systematically includes
unknown facts, inconsistent facts, clock uncertainty, conflicts, cycles,
revocation, unsupported current-kernel features, and empty positive outcomes.
It is not an estimate of real-world decision failure.

The corpus root is:

```text
708a66e9585754bdfb71da172d166e498a230876e6e61ca0946eb285837d7fe1
```

The semantic-set root is:

```text
8c6cb124b06ca37dc2dc8964e4a5187898880948fede34002c4034a3dbb69912
```

A second clean generation produced a byte-identical manifest and all 16
byte-identical compressed shards.

These measurements establish deterministic construction and identity coverage
only. They do not rescue v0's semantic claim. The later audit found only 49
role-normalized behaviors, accepted re-sealed hostile records, incorrect
contrary-to-duty behavior, deadline ambiguity, dormant variation axes, and
counterfactual claims that had not been executed. The v0 promotion verdict is
therefore withdrawn.

## Reproduce the corpus

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

## What remains unverified

The independent Python oracle passed, but no raw-record SMT translator was run.
Z3 and CVC5 therefore remain `SKIP` for this corpus. ESSO remains `SKIP`
because no ESSO model was compiled directly from raw corpus rules. Tau, Lean,
and HOL also remain `SKIP`.

The current GlassMind deontic kernel treats priority, exceptions, temporal
reasoning, and contrary-to-duty semantics as unsupported metadata. The corpus
retains these cases for future PCD work, but marks their current-kernel
projection `unsupported_quarantine`. The 65,536 records must be streamed or
sharded; they are not one deontic pack and not 65,536 planner decisions.

The historical promotion label must not be used. The corpus remains useful as
a deterministic hostile-regression fixture, but semantic promotion requires a
new profile whose causal effects, invariants, mutations, and independent
receipt boundary are executed and retained.
