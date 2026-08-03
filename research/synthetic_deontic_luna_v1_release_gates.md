# Synthetic Deontic Luna v1 Release Gates

Status: proposed fail-closed release contract.

These gates apply to the v1 corpus with exact factorization:

```text
16 typed domains
  x 16 topology-local deontic programs
  x 4 evidence values
  x 4 topology-local state variants
  x 4 resolution variants
  x 4 defeater variants
  = 65,536 records
```

The gates distinguish input count from causal and behavioral diversity. A
unique hash is not evidence of a unique decision. A tool name in a report is
not evidence that the tool ran.

The concrete v0 falsifiers motivating this contract are recorded in the
[v0 audit](synthetic_deontic_kb_luna_audit_v0.md).

## Result meanings

Every gate and tool lane must use one of these statuses:

- **PASS** means the named check executed against the exact pinned inputs,
  satisfied every stated threshold, and produced a replayable receipt. PASS is
  scoped to that check.
- **FAIL** means the check executed and found at least one counterexample,
  mismatch, missing case, surviving mandatory mutant, or threshold violation.
  Any mandatory FAIL vetoes promotion.
- **SKIP** means the check did not execute, was unavailable, timed out before a
  result, or was outside the selected release profile. SKIP is never positive
  evidence. A mandatory SKIP vetoes promotion. An optional SKIP forbids only
  the corresponding optional claim.

An internal exception, malformed tool output, missing receipt, or unknown
status is recorded separately for diagnosis and treated as FAIL by the
promotion reducer. It must never be converted to PASS or silently dropped.

## Canonical metric definitions

### Normalized disposition

The normalized disposition erases domain names, topology names, record IDs,
ordinals, hashes, evidence IDs, and cosmetic labels. It maps actors, actions,
facts, and norms to structural roles. It retains:

- resolved or unresolved status;
- required, forbidden, and permitted structural action roles;
- abstain or escalate fallback;
- active, defeated, satisfied, and violated norm roles;
- activated repair roles;
- conflict, deadline, uncertainty, inconsistency, and defeat categories in the
  proof trace.

Normalization itself is versioned, independently tested, and bound into the
release receipt. Adding a distinct label without changing this structure does
not create a new behavior class.

### One-axis pair

A one-axis pair contains two valid records that differ in exactly one of the
four variation axes and agree on domain, topology, and the other three
variation axes. Each four-valued axis contributes six unordered value pairs per
fiber.

The exact v1 total is:

```text
4 axes x (65,536 / 4 fibers per axis) x C(4, 2)
  = 4 x 16,384 x 6
  = 393,216 unordered one-axis pairs
```

Each pair is classified by execution as:

- `EFFECT`, when its normalized disposition or proof trace changes; or
- `INVARIANT`, when the independently recomputed results are equal.

No pair may be classified from a generator declaration alone.

### Causal spanning witness

A connected graph on four axis values needs at least three edges. For every
domain, topology, and variation axis, v1 declares a deterministic three-edge
spanning tree. Every edge has an application predicate and at least one valid
target among the remaining axis values.

The minimum effect-witness count is therefore:

```text
16 domains x 16 topologies x 4 axes x 3 spanning edges = 3,072
```

This denominator is derived from the declared product. It is not a sampled
coverage target.

## Mandatory release gates

### G00: frozen subject and evidence coverage

PASS requires one canonical release-subject record containing:

- candidate revision and clean release-tree status;
- template, schema, generator, oracle, normalization, manifest, verification,
  replay, and corpus-root digests;
- profile IDs and format versions;
- interpreter and compression versions;
- exact commands and exit statuses for every mandatory gate; and
- a checker-coverage proof that every authority-bearing source and schema file
  is included.

All digests must be recomputed from bytes by the release checker. Merely
checking that a declared digest is hexadecimal fails this gate. Any source edit
after receipt generation fails this gate.

### G01: exact product, identity, and coverage

PASS requires all of the following:

- exactly 65,536 accepted records;
- a bijection between ordinals and the full `16*16*4*4*4*4` coordinate
  product;
- exactly 4,096 records per domain and per topology;
- exactly 256 records per domain-topology block;
- exactly 16,384 records for every value of each four-valued axis;
- exactly 64 records for every axis value inside each domain-topology block;
- 65,536 unique full-length stable IDs and semantic signatures;
- no duplicate canonical record bytes, ordinal, stable ID, or semantic
  signature;
- exact shard count, file set, compressed and uncompressed sizes and digests;
  and
- independently recomputed corpus and semantic-set roots.

Any extra shard or unlisted corpus file is a FAIL, not ignored packaging data.

### G02: closed canonical IR

PASS requires all 65,536 records to decode through one versioned closed schema.
Every nested object has an exact field set and exact JSON type. The decoder
rejects:

- unknown, missing, duplicate, reordered where order is canonical, and
  malformed-present fields;
- Boolean and integer aliases, numeric strings, non-finite numbers, duplicate
  JSON keys, trailing data, and noncanonical encodings;
- unknown enum values, unsupported schema versions, and excessive resource
  bounds; and
- records whose canonical re-encoding differs from the admitted bytes.

The checker must return a typed rejection or corpus FAIL for every malformed
input. An uncaught parser or validation exception fails this gate.

### G03: typed references and admissibility

PASS requires:

- every actor, action, fact, norm, evidence, clock, exception, repair,
  conflict, priority, revision, and proof-trace reference to resolve in the
  correct registry and sort;
- every norm subject to own its action or carry an explicit checked delegation;
- every evidence reference to bind a typed proposition, source kind, revision,
  and truth status;
- every domain raw-state value to satisfy its declared type and bound;
- every topology-local variant to satisfy the topology admissibility predicate;
  and
- every declared application-target set to be nonempty.

The invalid-combination generator is derived from the schema. For every
reference occurrence it substitutes every registered ID of the wrong sort and
one unknown ID. It also enumerates every combination rejected by the topology
admissibility matrix. PASS requires rejection of 100% of these cases with the
declared rejection class.

### G04: adversarial mutation effectiveness

The release harness derives its mandatory mutant set from the v1 schema and
requirements. It includes:

1. deletion of every required field;
2. insertion of an unknown sibling into every object shape;
3. every incompatible JSON type for every leaf field;
4. Boolean/integer and numeric-string aliases;
5. duplicate, dangling, wrong-sort, and wrong-owner references;
6. unknown condition, temporal, exception, repair, revision, and topology
   variants;
7. candidate-result, negative-knowledge, proof-trace, coordinate, stable-ID,
   record-hash, shard, root, source-hash, and replay-receipt mutations;
8. canonical-order and duplicate-key mutations; and
9. every hostile record retained from the v0 audit.

The receipt records the derived mutant count by family. PASS requires 100%
kill of this mandatory set, zero surviving critical mutants, and the intended
typed rejection for every mutant. An aggregate score cannot compensate for one
surviving authority, schema, source-binding, or semantic mutant.

### G05: finite semantic totality and safety laws

The generator candidate and independent oracle must return the same complete
result for 65,536 of 65,536 valid records. PASS also requires these laws on
every applicable record:

- evaluation is total and deterministic;
- unknown or inconsistent evidence cannot become a resolved permission or
  obligation;
- unknown performance when a deadline has been reached produces unresolved
  escalation;
- timely and late performance are distinguished by explicit evidence;
- an active relevant priority cycle produces unresolved escalation;
- a primary violation remains in the trace when a CTD repair activates;
- a CTD repair is not treated as an exclusive primary action unless an
  explicit topology relation says so;
- an unresolved decision has no executable required or permitted actions;
- prohibited actions never appear in the permitted set;
- defeated or revoked norms cannot authorize an action; and
- every fallback and reason category is derived from the same checked result.

Each law needs at least one named positive witness and one named breaker where
the law has a meaningful negation. All witnesses are retained as canonical
records, not prose examples.

### G06: domain causality and non-renaming

Each of the 16 domains must expose:

- a closed typed raw-state schema;
- derived predicates with explicit dependency edges from raw fields;
- norm and admissibility consumers for every derived predicate; and
- at least two single-field mutation families capable of changing a normalized
  disposition.

PASS requires:

- at least `16*2 = 32` executed domain-mutation effect receipts;
- a nonempty application set for every mutation family;
- the raw field, derived predicate, and consumed norm to change as declared;
- the normalized disposition to change for every retained effect witness;
- 100% of declared raw fields to reach a derived predicate or be explicitly
  rejected as dead schema; and
- 16 distinct domain dependency-and-mutation fingerprints after identifiers
  and display strings are alpha-normalized.

A domain that differs only by actor, action, predicate, or relation names fails.

### G07: variation-axis causal coverage

For each of the 16 domains, 16 topologies, and four variation axes, the content
specification must declare a three-edge spanning tree over the four values.
Every edge has a machine-checkable application predicate.

PASS requires:

- all 393,216 unordered one-axis pairs to execute and receive exactly one
  `EFFECT` or `INVARIANT` classification;
- at least 3,072 retained `EFFECT` receipts, one for every declared spanning
  edge in every domain-topology-axis triple;
- zero empty spanning-edge application sets;
- the changed-axis proof to show that all non-axis semantic input fields are
  equal; and
- every `INVARIANT` receipt to bind equal independently recomputed results,
  rather than a prediction that a value may be inert.

Unconditional active-fiber and pairwise-influence rates are reported for each
axis. They are diagnostics, not substitutes for the complete application-aware
gate.

### G08: normalized behavior and topology diversity

PASS requires:

- at least 64 distinct normalized dispositions across the corpus;
- at least four distinct normalized dispositions within every topology;
- 16 distinct alpha-normalized topology program digests;
- 16 distinct topology behavior fingerprints over the 256 variation
  coordinates; and
- for every pair of topologies, at least 16 differing normalized dispositions
  among the 256 common variation coordinates in every domain.

The global lower bound of 64 is derived from 16 topology programs with at least
four topology-local behavior classes. The pairwise distance of 16 is one full
two-axis slice of the four-by-four variation grid. Distinct reason strings,
record IDs, or topology labels cannot satisfy either threshold.

The report must include both the 65,536 semantic-signature count and the
normalized behavior count. It must not call the former behavioral diversity.

### G09: outcome balance

Each domain-topology block contains 256 records. PASS requires every block to
contain at least:

- 16 resolved decisions;
- 16 unresolved decisions with abstention; and
- 16 unresolved decisions with escalation.

These local requirements imply at least 4,096 records in each family globally.
No one normalized disposition may occupy more than 192 of the 256 records in a
domain-topology block. The 16-record floor is one sixteenth of a block. The
192-record ceiling leaves at least one full four-valued-axis share outside a
dominant class.

The exact counts and percentages for every domain, topology, and
domain-topology block must be recomputed from raw records. They are synthetic
coverage measurements, not estimates of real-world prevalence.

### G10: executed negative knowledge

PASS requires a content-addressed receipt for every one-axis pair. Each receipt
binds:

- schema, semantics, normalization, generator-profile, and oracle digests;
- canonical source and target stable IDs and record hashes;
- the single changed axis and its before and after values;
- the application predicate and its evaluated inputs;
- full before and after result hashes;
- observed normalized delta;
- `EFFECT` or `INVARIANT` classification; and
- checker status and rejection data, if any.

All 393,216 pair receipts must verify. Every negative-knowledge claim in a
record must cite one or more verified receipt IDs. Statements such as
`may_change` without an executed target and result are experiment proposals and
do not count as knowledge.

Every minimized v0 and v1 counterexample remains in an append-only regression
set with first-seen profile, current status, and the test that kills it.

### G11: independent oracle and mutation independence

PASS requires:

- an import and call-graph receipt showing no generator module, template
  loader, generator evaluator, or generator coordinate helper in the oracle
  dependency closure;
- raw canonical bytes to be parsed directly by the oracle;
- coordinates, semantic results, proof traces, negative receipts, coverage,
  identities, shard digests, and roots to be independently recomputed;
- full-result agreement on 65,536 of 65,536 valid records;
- 100% kill of the G04 mandatory mutants by the oracle boundary; and
- a coverage receipt proving every release-critical source and schema file is
  checked.

Separate authorship or a different model may reduce correlated mistakes, but
it is not a substitute for these executable checks. Agreement between two
implementations can reproduce a shared bad specification, so requirements and
semantic counterexamples remain separate gates.

### G12: deterministic rebuild and replay binding

PASS requires two clean builds in distinct empty temporary directories under
the pinned environment. For both trials:

- generation exits successfully;
- the independent oracle passes all 65,536 records;
- the manifest is byte-identical;
- every named shard is byte-identical;
- corpus and semantic-set roots agree;
- there are no missing, differing, or unexpected artifact files; and
- source, schema, profile, interpreter, and compression digests agree.

The replay receipt includes the exact command arguments, environment versions,
per-trial source and artifact digests, oracle reports, and comparison result.
The replay verifier recomputes the receipt. Mutation of any bound field must
fail a retained replay-receipt test.

### G13: synthetic authority boundary

PASS requires all 65,536 records, the template bank, manifest, verification
report, replay receipt, and tutorial-facing summary to state
`synthetic_non_authoritative` and preserve these nonclaims:

- not law;
- not ethics;
- not factual or world truth;
- not population frequency;
- not complete deontic logic;
- not authorization for an external effect; and
- not production readiness.

Exact Boolean checks must reject integer aliases. Every mutation that changes
an authority flag, issuer, jurisdiction, source kind, truth status, or nonclaim
must fail. PASS requires zero authority-leaking records and 100% kill of the
authority mutation family.

### G14: kernel and external-tool claim boundary

The release report contains an explicit PASS, FAIL, or SKIP row for each
configured lane, including:

- the mounted decision kernel;
- Z3 and CVC5;
- ESSO;
- Tau, Lean, and HOL;
- Research Kernel and PopperPad export;
- LEAP, Morph, ZAG, or other research tools used during content discovery.

The base v1 corpus label does not require optional formal or research tools to
PASS. An optional SKIP is allowed only when the corresponding claim is absent.

A tool lane may report PASS only when it executed against the exact v1 schema,
profile, source digests, and raw records named in its receipt. Tool availability,
successful candidate generation, metadata projection, or a prior-version run
does not count.

Kernel parity is a separate refinement claim. It requires execution of the
mounted kernel on an exact declared subset, comparison of the complete result
and rejection behavior, and a digest of that subset. `kernel_projection`
metadata cannot establish parity. If no such run occurs, kernel status is SKIP
and no parity statement may appear.

### G15: fail-closed promotion reduction

The reducer, not the generator, assigns the release label.

`BOUNDED_VERIFIED_SYNTHETIC_DEONTIC_CORPUS_V1` requires PASS on G00 through G13
and a complete, honest G14 status table. A FAIL, internal error, missing receipt,
unknown result, or mandatory SKIP produces `QUARANTINED_CORPUS`.

Optional augmented labels require their own executed evidence:

- `KERNEL_REFINEMENT_CHECKED_V1` requires the kernel lane to PASS;
- `SMT_CROSS_CHECKED_V1` requires the named solver lanes to PASS with agreement;
- `FORMALLY_PROVED_COMPONENT_V1` requires an exact theorem and checker receipt,
  and applies only to the theorem's stated component; and
- `RESEARCH_LEDGER_EXPORTED_V1` requires successful replayable Research Kernel
  or PopperPad export, without changing scientific support status.

No optional label upgrades the corpus to legal, ethical, factual, complete,
production-ready, or externally authoritative.

## Required release receipt

The canonical reducer input contains at least:

```text
release_subject
  schema and profile versions
  source and artifact digests
  corpus and semantic-set roots
  exact factorization and coverage

gate_results[G00..G15]
  status: PASS | FAIL | SKIP
  checker ID and digest
  command profile
  checked count and threshold
  counterexample or error IDs
  evidence receipt digests
  residual nonclaims

diversity
  normalized-disposition schema digest
  distinct normalized dispositions
  topology fingerprints and pairwise distances
  domain causal fingerprints
  per-axis fiber and pairwise influence

counterfactuals
  expected unordered pairs: 393216
  checked unordered pairs
  effect and invariance counts
  spanning effect witnesses: at least 3072

tools
  one explicit PASS, FAIL, or SKIP row per configured lane

promotion
  reducer digest
  assigned label
  veto reasons
```

The receipt is evidence about this finite synthetic model only. It does not
inherit authority from the agents or tools that helped create it.
