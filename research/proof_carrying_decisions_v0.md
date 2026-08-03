# Proof-Carrying Decisions v0

Status: proposed tutorial foundation and bounded implementation profile.

This document defines a small proof-carrying decision (PCD) protocol. A receipt
records why a bounded decision was considered applicable, which alternatives
were considered, which resolution was selected, and which deterministic checks
accepted the record. The receipt is evidence for a verifier. It is not an
authority by itself.

The current demonstrator for this lane is the pinned Open English WordNet 2025
knowledge-Q planner. It uses bounded directed lexical snapshots, exact-size
required-decision packs, and finite deterministic Q planning. The separate
GlassMind synthetic receipt remains an illustrative_only fixture, so its old
synthetic grid is not the current knowledge-Q demonstrator. In both profiles, a
model, a Q table, a language model, or a knowledge base may propose facts,
rules, rankings, or alternatives. A deterministic verifier owns acceptance.

## Current bounded evidence

The current evidence is a set of pinned, finite artifacts. It is not a claim
that the source statements are true in the world, that lexical relations have
normative force, or that a PCD receipt has passed S1 or S2.

| Artifact | Current fact | Boundary |
| --- | --- | --- |
| Pinned source | Open English WordNet 2025, [source URL](https://en-word.net/static/english-wordnet-2025.xml.gz), license CC-BY-4.0, compressed source SHA-256 `9ca6d1dcb75f822fdd66617f7d9da48142ace38dd544d6ad5e2feca1674ad3fe` | The source hash identifies the pinned compressed release. It does not establish authenticity or semantic truth. |
| Adapter and public graph | `glassmind-oewn-lmf-adapter-v1`; 256 nodes, 500 directed lexical edges, canonical graph SHA-256 `755450aea529f9dc19754bb4e56ab38a8ecd817927891a274881c0cf67cc37e1`, `truncated=true` | The graph hash identifies this bounded extracted graph, not the compressed source release. |
| Full bounded graph | 1024 nodes, 2157 directed lexical edges, canonical graph SHA-256 `8524f26bf9d2ccc63993382e5625d05c5260af583471c631fca9d6b242119b5d`, `truncated=true` | The graph hash identifies this other bounded extracted graph, not the complete WordNet source or the world. |
| Snapshot time and roots | Both graphs use `retrieved_at` `2026-08-02T00:20:57Z` and contain all ten declared roots listed in the current demonstrator section. | A root being present does not make its lexical neighborhood complete. |
| ESSO finite adapter | Model file SHA-256 `78e5d57a463365d21741045a64a556176427963eb81aae0c0a8d48e0ee56b270`; canonical ESSO IR SHA-256 `0fed6db3d9a4a1927cda867e0683c5a257c9feb9471452f7eb5621820900b965` | This is evidence for the finite ESSO adapter model and its declared invariants under its sequential bounded environment. |
| ESSO verify-multi | Z3 4.15.4 and CVC5 1.1.2, timeout 10,000 ms, fixed solver seed 0, `fail_closed=true`, inductive `k=1`; Z3 and CVC5 agreed UNSAT on 7/7 queries: `init_implies_inv`, `normal_obligation`, `prohibition`, `explicit_permission`, `conditional_conflict`, `abstention_allowed_unresolved`, and `fail_closed_escalation`; `failed_queries=0`, `inconclusive_queries=0`, `disagreements=[]`, deterministic over two trials | This does not establish premise truth, WordNet truth, deontic completeness, moral correctness, Q optimality, explanation fidelity, source freshness, safe external effects, or correctness of an unmodeled compiler or host. |
| Synthetic deontic problem bank v0 | Historical integrity run: exactly 65,536 records, 65,536 semantic signatures, corpus root `708a66e9585754bdfb71da172d166e498a230876e6e61ca0946eb285837d7fe1`, and byte-identical output over two clean generations. The later [v0 audit](synthetic_deontic_kb_luna_audit_v0.md) assigned **NO-GO** for semantic promotion. | Identity and replay checks did not establish behavioral diversity or a sound acceptance boundary. This remains a generated hostile-regression fixture, not an authoritative norm, legal corpus, moral theory, world model, or population sample. Raw-record SMT, ESSO, Tau, Lean, and HOL checks remain `SKIP`. |
| Luna v1 status and raw-corpus oracle | Promotion label exactly **`QUARANTINED_CORPUS`**. The [raw report](../assets/data/glassmind_synthetic_deontic_luna_v1_65536.verify.json) accepted 65,536 records and rejected zero generated records. Its internal digest is `04f51f5102c5c35b0ccb80b4911ffc084ab5773030921c3b2fd516d6d4b87150`; the complete file SHA-256 is `38b6b3fd208e89c6cba7d4c3911f74326325e628b513d3fef217d75b5590460a`. | G08, G09, and G14 are `PASS`; G00-G07 and G10-G13 are `SKIP`; G15 is `FAIL`. Zero rejection applies to the generated corpus, not a complete hostile mutation set. See the [v1 report](synthetic_deontic_knowledge_base_v1.md). |
| Luna v1 finite reference lane | Exact enumeration produced 65,536 cases, 322 normalized dispositions, outcome totals `8480/18576/38480`, and 393,216 one-axis classifications: 177,600 `EFFECT`, 215,616 `INVARIANT`, with 3,072 declared spanning-effect witnesses. Two exhaustive executions reproduced receipt-set root `9ccf9ae8d13c9b4fb12cee0503af4010a35ac73c75b3457c4fda528c21a0c2ab`. | This is bounded model evidence, not raw-file authenticity, semantic novelty, population frequency, law, ethics, world truth, or a durable G07/G10 receipt corpus. One measured run took 915.148 seconds, so routine exhaustive iteration still has performance debt. |
| Luna v1 rebuild observation | A local replay comparison matched manifest SHA-256 `62968f1afad2b65fccb951032b5cc1396b8de3f3410205cf8347c757080e0565` and all 16 gzip shards byte-for-byte. | The comparison was not retained as a bound two-clean-build receipt with a second full oracle report. G12 remains `SKIP`. |
| Luna v1 external bindings | The reducer preserved explicit nonclaims, and the project-local negative-knowledge outbox retains v0 and v1 failures for later import. | Decision-kernel, SMT, ESSO, Tau, Lean, HOL, and configured research-tool lanes are all `SKIP` for this exact profile. Julia and ZenoFCIS have no run receipt. Results from the separate WordNet adapter run cannot be inherited. This is not PCD-S1, PCD-S2, kernel parity, formal proof, production readiness, or external-effect authority. |
| Tau | Status exactly `specified_not_run` | No Tau execution result is claimed. |

The Q planner has exactly two model-local discovery bits. Bit 0, integer 1,
records traversal of a source-directed lexical edge. Bit 1, integer 2, records
reverse browsing of a directed lexical edge. Integer 3 requires both. These
bits report discovery channels only. They do not report proposition truth,
reliability, logical entailment, moral force, or proof. A reverse browse does
not create an inverse fact. An absent path in either truncated graph proves
nothing about the full source or the world.

## Scope and assumption hygiene

The v0 profile is deliberately finite. It handles:

- ground typed facts;
- a small deontic vocabulary;
- finite defeasible rules with explicit priorities and exceptions;
- required decisions with an explicit resolution, including abstention or
  escalation when the policy permits either;
- content-addressed evidence and proof nodes;
- a deterministic replay and revocation check.

The following assumptions are model choices, not facts about the world:

1. **A1, bounded state.** The verifier is given a finite set of normalized
   facts, norms, alternatives, and proof nodes. A result is only about that
   set and its declared validity interval.
2. **A2, trusted authority registry.** The verifier has an independently
   configured mapping from issuer identifiers to authority scopes. An issuer
   field inside a receipt does not create authority.
3. **A3, finite action vocabulary.** Action identifiers and any
   mutually-exclusive action groups come from a checked profile. A string that
   merely looks like an action is not executable code.
4. **A4, replayable inputs.** A source or model is replayable only when its
   revision and content hash can be recovered. A label supplied by a proposer
   is not an independently recomputed hash.
5. **A5, fail-closed uncertainty.** An unknown safety-relevant fact is not
   silently changed to false, and an unknown permission is not silently
   changed to true.

These assumptions are quarantined in the receipt through provenance,
coverage limits, review triggers, and nonclaims. A future profile may replace
an assumption only by adding a checked interface and a regression corpus.

### Model choices and derived claims

The following are v0 model choices:

- PCD-DL-V0 is a finite, three-valued, defeasible rule profile rather than
  unrestricted standard deontic logic.
- pcd-cjson-v0 is the named canonical JSON profile.
- integer selection ranks are used only after safety and applicability checks;
  they do not make an inadmissible alternative admissible;
- an explicit abstain or escalate alternative is a resolution, while no
  decision record at all is omission;
- a proof node is a hash-bound rule-trace claim, not automatically a proof of
  all modal consequences.

The following are conditional claims that a verifier may derive:

- If two values have the same accepted pcd-cjson-v0 representation, their
  canonical bytes and SHA-256 content hash are equal.
- If an accepted receipt contains a required decision with
  omission_admissible = false, the receipt contains an explicit chosen
  resolution. It does not contain permission to omit the decision.
- If every premise, rule, priority, exception, and alternative check in a
  bounded trace is accepted, the verifier may report that the chosen
  alternative satisfies the checked v0 obligations and violates no checked
  prohibition. This is a statement about the checked finite model, not a
  proof of unrestricted deontic semantics.

The last claim is a verifier result only when the deterministic rule evaluator
has actually run. The illustrative JSON receipt in this lane marks its
synthetic hashes and declared checks so that it cannot be confused with an
independently recomputed run.

## Terminology

The terms below are intentionally separate.

| Term | v0 meaning |
| --- | --- |
| Obligation | A norm requiring a proposition or resolution in a stated context. O(phi) means that phi is required when the norm is applicable. |
| Required decision | A procedural record that requires an explicit resolution of a decision point. Its omission_admissible field is false. It may be discharged by a permitted action, abstention, or escalation, depending on its alternatives. |
| Decision outcome | The selected resolution record. It points to one alternative and records whether the result is an action, abstention, or escalation. |
| Action | A candidate operation in the profile, such as routing through an edge. An action can be proposed without being admissible or executable. |
| Evidence | A normalized fact, source revision, counterexample, negative-knowledge item, or other checkable input that supports or limits a claim. Evidence is not automatically a proof. |
| Proof receipt | The content-addressed envelope containing the decision, evidence references, proof DAG, rule trace, verifier profile, and explicit nonclaims. It is a portable claim about a verifier run, not a side-effect authorization. |

An action can be one component of an outcome, but an outcome also has a
selection status and an authority boundary. Evidence can support an
alternative without selecting it. A proof receipt binds the references and
the declared checks without making the referenced sources truthful by
assertion.

## Deontic vocabulary

The v0 vocabulary is small.

- O(phi) is an obligation. When applicable, the checked model requires
  phi.
- F(a) is a prohibition. It says that action a is forbidden. In this
  profile it is an operational abbreviation for an obligation not to select
  a; that equivalence is a profile convention, not a theorem about every
  deontic logic.
- P(a) is a permission. It says that a is allowed under the stated
  conditions. P(a) does not imply O(a), and a permission does not by itself
  create a required decision.
- O(phi | C) is a conditional obligation. It is active only when condition
  C is established as true by the bounded fact and rule trace.
- O_by(t, phi) is a deadline obligation. It requires phi no later than
  the checked step or timestamp t.
- O(repair | violation(phi)) is a contrary-to-duty (CTD) repair obligation.
  It is activated by evidence that the primary obligation was violated. A
  repair obligation does not erase or retroactively satisfy the primary
  violation.

The JSON receipt stores O and F records in obligations, and P records
in permissions. Each record has an explicit condition, priority, exception
references, deadline slot, repair slot, status, and provenance reference.
Unconditional, conditional, deadline, and CTD forms are distinct record
values.

An obligation can be compiled into a required decision:

~~~text
required_decision =
  (id, applicable_when, allowed_resolution_kinds,
   omission_admissible = false, obligation_refs, enforcement_refs)
~~~

This compilation adds a procedural requirement to produce a resolution. It
does not turn every permission into an obligation. If abstention is allowed,
an abstain outcome is still an explicit resolution. Silence, absence of a
receipt, or an unrecorded timeout remains omission.

## Semantic profile and its limits

PCD-DL-V0 uses the following semantic objects:

1. A finite set of ground predicates with values true, false, or
   unknown.
2. A finite set of norm records.
3. A finite rule trace whose premises are facts, norm records, alternatives,
   or earlier trace conclusions.
4. Integer priorities and explicit exception references.
5. A finite alternative set and a declared deterministic selection policy.

This is a defeasible, trace-oriented profile. It is useful for showing which
bounded claims were checked, but it is not a complete modal semantics.

Naive unrestricted standard deontic logic is not enough for this engineering
problem. A basic modal vocabulary does not by itself specify:

- which revision of a fact is current;
- how exceptions defeat a general norm;
- how two active norms conflict;
- how deadlines are evaluated against a clock;
- how a violated primary obligation activates a CTD repair;
- how unknown observations should affect a safety decision;
- how an outcome is selected among several admissible alternatives; or
- how a proof object is serialized, replayed, revoked, and bound to an issuer.

The v0 profile therefore treats modal symbols as typed records interpreted by
a finite evaluator. A future richer logic can be attached to the same receipt
boundary, but it must state its semantics and add an independent conformance
checker.

### Logic-profile registry

There is no universally best deontic logic for every application. The active
logic is therefore a versioned input, not a hidden implementation choice. This
follows the experimental-infrastructure approach of [Benzmüller, Parent, and
van der Torre](https://xavierparent.github.io/pdf/C69.pdf), which supports
comparing multiple deontic formalisms through higher-order logic rather than
assuming one formalism fits every normative problem. Temporal obligations are
also first-class because [Priya and Rao](https://arxiv.org/pdf/2501.05765)
show how deontic and temporal operators can be combined for bounded system
verification. These papers motivate the registry. They do not certify this
v0 protocol or its example.

Every registered profile has a profile identifier, exact semantics hash,
translation hash, checker and version, supported operators, finite or temporal
bounds, CTD policy, conflict policy, proof-object format, and countermodel
format. A receipt binds the selected profile. Changing any of those fields
creates a different profile hash.

The initial registry permits these profile families:

| Family | Appropriate use | Required caution |
| --- | --- | --- |
| PCD-DL-V0 | Finite typed rule traces with explicit priorities, exceptions, and escalation | This is the bounded demo profile, not a complete modal calculus. |
| SDL/HOL | A baseline embedding of standard deontic logic in higher-order logic | Naive CTD encoding can produce paradoxical or explosive consequences. It must not settle a CTD case by explosion. |
| DDL/HOL | Dyadic conditional obligations and CTD-sensitive experiments | The chosen dyadic semantics and embedding must be hash-bound and checked. |
| Input/output logic | Detaching normative outputs from separately supplied facts and norms | Permission, conflict, and reparation operations vary by profile and must be named. |
| TDL/HOL | Obligations over time or finite traces | The trace bound, temporal semantics, and model-checking complexity must be explicit. |

For an explicitly enumerated deterministic transition system with horizon H,
state count S, and action count A, the layered dynamic-programming pass checks
H * S * A action transitions. This does not give a universal complexity bound
for HOL proof search, SMT solving, or a richer temporal logic. Each backend run
must report its finite domains, trace bound, explored states, solver limits,
timeout policy, and proof or countermodel status. Finite means decidable in the
declared model, not necessarily inexpensive.

For input/output logic, the input facts and the normative system remain
separate. A constitutive rule can derive an institutional fact, such as
blocked_route(edge-7), from checked observations. A prescriptive rule can then
detach an output such as F(use(edge-7)). Every rule is reified with its issuer
authority, jurisdiction, validity interval, revision, priority, and exceptions.
No rule obtains authority merely by appearing in the receipt.

A semantic backend returns one of proved, refuted, countermodel-found,
unknown, timeout, or not-run for a named query. Its checker proof object or
countermodel is stored separately from the human explanation. A fluent
explanation can help a reader, but it is not replay evidence and cannot replace
the checker object.

### Normative compilation into layered Q tables

The normative profile constrains which actions may enter optimization. The
outcome model ranks only the actions that survive those constraints:

~~~text
source adapters -> canonical directed fact graph
canonical facts + Tau or ESSO policy + logic profile -> O/F/P trace
O/F/P trace -> deterministic admissible-action mask
transition model + bounded utility model -> rewards on admissible actions
finite-horizon dynamic programming -> layered Q bytes
replay verifier -> proof-carrying decision receipt
~~~

The current WordNet knowledge-Q demonstrator is a bounded source-adapter and
planner profile within this larger design. Its public pack has six required
decisions and its full pack has sixteen. The public records are an exact
semantic subset of the full records. Applicability is expressed with OEWN
node IDs, and each goal is a bounded lexical-review goal. The planner currently
compiles each record to the generic `resolve` action or
`abstain_or_escalate`. The goal's resolution alternatives are declarative
audit metadata; they are not sixteen separately optimized Q actions.

WordNet supplies source-attributed lexical and navigation links only. It does
not supply the O/F/P trace in the design above. A supplied deontic adapter or
ESSO/Tau policy remains the normative boundary, and the host must bind its
inputs. The current Q planner's evidence bits describe discovery channels,
not premise truth or norm justification.

In the v0 compiler, an active F(a) masks action a. An active O(a) removes
omission and incompatible alternatives. P(a) can admit a when no stronger
obligation or prohibition defeats it, but P(a) does not require a. Unknown
premises, unresolved conflicts, incomplete action coverage, or an empty
admissible set force an allowed abstain or escalate resolution. Utility never
overrides the normative mask.

The receipt binds the hashes of every decision-relevant stage: each source
snapshot, the canonical fact graph, canonicalizer, logic semantics,
normative policy, utility function, transition model, generator, admissibility
mask, and Q-table artifact. A reason trace that omits one of these bindings is
not replay-complete for this compiler profile.

ESSO is one conforming decision-kernel backend. Its ESSO-IR model uses finite
domains, explicit observables, guarded actions, emitted effects, and an
optional deterministic canonicalizer. O, F, P, priorities, exceptions, and
escalation are compiled into that bounded model. Verification treats a solver
timeout or unknown result as failure and preserves concrete counterexamples.
The current finite ESSO adapter evidence is the pinned model and canonical IR
hashes in the current-evidence table, plus the two-trial Z3/CVC5 result shown
there. It is evidence for that finite adapter and declared invariant set only,
not an integrated PCD receipt acceptance result.
Multi-solver checking can be requested with repository-relative commands such
as:

~~~bash
python3 -m ESSO validate path/to/pcd_policy.yaml
python3 -m ESSO verify path/to/pcd_policy.yaml \
  --reference path/to/reference_policy.yaml
python3 -m ESSO verify-multi path/to/pcd_policy.yaml \
  --reference path/to/reference_policy.yaml --solvers z3,cvc5
~~~

An exported Tau gate can check the final Boolean admissibility contract, while
the host remains responsible for computing and binding its input flags. ESSO's
shell lint and dynamic shell verification can check effect wiring. These are
conforming backend options, not evidence that this repository executed the
integration. The separate illustrative v0 receipt records the ESSO and Tau
integration as specified-not-run. For the current WordNet knowledge-Q
demonstrator, Tau also remains exactly `specified_not_run`; the bounded ESSO
evidence does not imply that Tau executed or that PCD S1/S2 receipt acceptance
was recomputed.

ESSO or Tau may own formal decision authority relative to the supplied finite
model. They do not establish that the premises are true, complete, current, or
morally adequate. That separation is part of the authority boundary rather
than a defect in the decision engine.

### Bounded utility and alignment assumptions

A tutorial-sized outcome model can use scaled integer utility. For example,
for an admissible route a:

~~~text
U(a) = -sum_i weight_i * (predicted_harm_i(a) + delay_cost_i(a))
~~~

The index i ranges only over the stakeholder groups explicitly listed in the
profile. Rights and safety rules are applied as normative side constraints
before this sum. Catastrophic outcomes receive a separately checked bound or
force escalation rather than being hidden inside an average.

This is bounded utilitarian aggregation, not proof of ethical alignment. Its
validity depends on stakeholder coverage, weights, aggregation rules,
uncertainty calibration, time horizon, rights and side constraints,
catastrophic-tail treatment, and resistance to proxy failure. A missing group,
unstable estimate, tail beyond the declared bound, or reward proxy that can be
gamed activates review and fail-closed escalation.

### Source-neutral canonical fact graphs

The protocol accepts multiple source adapters. The current bounded tutorial
demonstrator uses the pinned [Open English WordNet 2025
release](https://en-word.net/static/english-wordnet-2025.xml.gz) under
CC-BY-4.0 through `glassmind-oewn-lmf-adapter-v1`. [Wikidata structured
data](https://www.wikidata.org/wiki/Wikidata:Licensing) under CC0 can optionally
enrich a future snapshot, but it is not part of the current evidence above.
Each source binding records its adapter and version, dataset revision, license,
payload hash, extraction hash, issuer, validity interval, and coverage limits.

The compressed source SHA-256 and the public/full canonical graph SHA-256
values have different scopes. The first identifies the pinned compressed
release. Each graph hash identifies one canonical bounded extraction from that
release. Neither graph hash is a substitute for the source hash, and neither
bounded graph is the complete source.

Canonical graph facts preserve predicate direction. A source assertion
subject --predicate-> object remains directed even when a navigator creates a
reverse browsing edge. The reverse edge is labelled browse-only and is never
treated as an inverse fact, implication, proof, or permission. Merging source
identifiers requires an explicit mapping record with provenance and may remain
quarantined when the identity claim is uncertain.

### Facts, conditions, and three-valued evaluation

A normalized fact has:

- a stable fact identifier;
- a typed predicate name;
- ordered, typed arguments;
- a truth value;
- a validity interval;
- provenance references; and
- a status such as asserted, derived, or quarantined.

Predicate arguments have declared types such as state-id, edge-id,
action-id, integer, string, boolean, timestamp, or sha256.
Predicate names and argument order are part of the normalized meaning. For
example, edge_status(edge-7, "blocked") is not interchangeable with
edge_status("blocked", edge-7).

The profile does not use a closed-world assumption. The absence of
edge_status(edge-7, "blocked") is not evidence that the edge is open.
unknown remains a first-class value. A condition that requires a true fact
does not fire on unknown; a safety check that depends on that condition
becomes unresolved and must use an allowed fail-closed resolution.

## Required-decision records

A required-decision record is the procedural core of a receipt. It contains:

- required_decision_id and a human-readable title;
- applicability conditions and rule references;
- allowed_resolution_kinds, chosen from action, abstain, and escalate;
- omission_admissible, which is false for this v0 record;
- references to the obligations that compile into the decision;
- enforcement references naming the deterministic checks that must run; and
- review-trigger references.

The enclosing decision record adds:

- a decision identity and validity interval;
- an applicability result and its trace references;
- at least two alternatives;
- an action descriptor for each alternative;
- an admissibility status;
- rationale and tradeoffs for every alternative;
- obligation effects such as satisfies, avoids, violates, or unknown;
- a deterministic selection policy and bounded integer rank;
- the chosen outcome;
- evidence references;
- an uncertainty and fail-closed policy; and
- review-trigger references.

The chosen outcome must reference exactly one listed alternative. Its
external_effect_authorized value is false. A separate trusted executor
must re-check policy and current state before any external effect.

### Alternatives and selection

An alternative is a candidate resolution, not an action authorization.
abstain means that the system deliberately declines to choose an action.
escalate means that it deliberately hands the unresolved or high-risk case
to a named channel. Both are explicit outcomes when listed by the required
decision.

The v0 selection policy is:

1. remove alternatives that violate an applicable F norm;
2. remove alternatives that fail a required O claim or fail the declared
   required-decision resolution contract;
3. if a safety-relevant premise is unknown, select an allowed abstain or
   escalate alternative, or report unresolved when neither is allowed;
4. among the remaining alternatives, use the declared bounded integer rank;
5. for equal ranks, use ascending alternative identifier only when there is
   no unresolved norm conflict; and
6. if applicable highest-priority norms still conflict, report an unresolved
   conflict rather than using a ranking to conceal it.

Ranks can be proposed by a Q table or another model, but a rank never repairs
an F violation. A verifier may accept the ranking only when the declared
selection policy and its source revision are valid. A future profile may
replace integer rank with a replayed deterministic Q-table comparison.

## Defeasibility, priorities, exceptions, and conflicts

Every applicable norm has an integer priority. Higher priority wins only under
the explicit priority rule recorded by the profile. A lower-priority norm is
defeated only when the trace identifies the higher-priority norm and the
defeat relation. Priority is not inferred from prose, source order, or model
confidence.

Exceptions are explicit references to rules or norms. A general condition is
not defeated merely because a proposer believes an exception exists. The
exception must be valid, in scope, and supported by a true fact or an earlier
accepted trace conclusion.

The verifier detects at least these conflicts:

- an applicable O(a) and F(a) pair;
- two applicable obligations requiring mutually exclusive actions;
- a chosen alternative that violates an applicable prohibition;
- a required decision with no allowed resolution; and
- inconsistent facts at the same revision when no checked priority resolves
  them.

For a conflict, the verifier applies explicit priorities and exception rules.
If the highest-priority active claims still conflict, the result is
unresolved with PCD-E014-CONFLICT. It must not silently pick the first
record, the highest Q value, or a language-model preference. If the conflict
can be handled by an allowed escalation or abstention, that outcome must be
recorded and the trace must show why it is fail-closed.

## Provenance, revisions, validity, and revocation

Each fact and norm points to one or more provenance records. A provenance
record contains:

- source kind and stable source reference;
- issuer identifier and declared authority scope;
- revision identifier, sequence, parent revision, and change summary;
- a lower-inclusive, upper-exclusive validity interval;
- a content hash of the source payload; and
- revocation status and an optional revocation reference.

Issuer authority is an external verifier configuration. A receipt cannot
grant an issuer a new scope by naming that scope. In v0, a content hash
provides identity and change detection. It does not provide authenticity
unless the verifier also trusts a source registry or signature mechanism.

Revision changes create a new content address. Silent in-place mutation is
not a revision. A receipt is valid only if its issue time is inside the
relevant intervals and its source revisions are active at the decision time.

Replay has two modes:

- **Historical replay** uses the receipt's declared revisions and the
  historical validity interval. It reports what the old receipt claimed at
  that time.
- **Current replay** loads the current source and revocation registry,
  re-evaluates the facts, norms, alternatives, and proof trace, and produces
  a new verifier result. An old acceptance is not current authorization.

A revocation effective before execution makes a receipt unusable for current
execution, even if historical replay still confirms that it was once
well-formed. A revocation effective after the decision does not rewrite the
historical record, but it triggers review before a future side effect. An
unknown revocation status on a safety-relevant source is fail-closed.

## Content-addressed proof DAG

The proof field contains:

- a DAG version;
- a node-hash scope;
- one or more root node identifiers;
- the node count and edge count;
- a maximum-depth bound; and
- a finite list of proof nodes.

Each node contains a statement, kind, premise node identifiers, claim
references, a rule reference, and a status. A node identifier is the
lowercase SHA-256 digest of the canonical node object with its own
node_id field omitted. Premise references point from a conclusion to
earlier premises. The verifier rejects duplicate identifiers, missing
premises, cycles, depth overrun, and roots that do not reach the decision
claim.

The DAG is a compact dependency record. It is proof-carrying in the
operational sense that the decision carries the claims and dependencies
needed by the bounded verifier. It does not prove arbitrary propositions
about an unbounded world or substitute for a soundness theorem for a future
deontic calculus.

The receipt content hash is computed over the entire canonical top-level
object with only content_hash omitted. The proof node identifiers remain
inside that top-level object, so changing a node or its reference changes the
receipt hash.

## Counterfactual alternatives and negative knowledge

A material alternative that was considered and rejected is recorded as a
counterfactual. It states:

- the assumption under which it was evaluated;
- its rejection or unresolved result;
- the rule, proof, or fact references that caused the result; and
- the negative-knowledge references that preserve the reason.

The phrase "counterfactual" means a checked alternative under a declared
bounded state. It does not mean that an unobserved real-world branch was
experimentally executed.

Negative knowledge is first-class evidence. It includes counterexamples,
unknowns, excluded domains, quarantined proposals, stale revisions, and
failed alternatives. Each item has a statement, evidence references, and a
consequence for acceptance or review. A clean positive trace does not erase
the limits represented by these items.

For GlassMind, a useful negative item is a counterexample showing that
selecting a blocked edge violates the active prohibition. Another is an
excluded-domain statement that the frozen synthetic grid does not establish
behavior after a map or hazard-model change.

For the current WordNet planner, useful negative items include missing
traversal coverage, an ambiguous lexical mapping, a changed source or adapter
hash, and an absent path in a truncated graph. None of these items is silently
converted into a false proposition. Each one preserves the bounded reason for
abstention or escalation.

## Uncertainty and fail-closed abstention

Uncertainty can arise from an unknown fact, an out-of-interval source, an
unreplayed model revision, an unresolved norm conflict, or a missing proof
premise. The verifier distinguishes these cases from a proved false claim.

If uncertainty affects safety or applicability:

1. the uncertain claim is retained as unknown or unresolved;
2. the verifier does not accept an ordinary action merely because it has the
   highest model or Q-table rank;
3. an explicitly allowed abstain or escalate alternative may be selected;
4. otherwise the verifier returns unresolved with a failure code; and
5. the review trigger is activated.

An abstain outcome is not the same as omission. It is a recorded resolution
whose admissibility and consequence must be checked. A system that cannot
record the resolution has not discharged the required decision.

## Canonicalization and hashing

The named v0 profile is pcd-cjson-v0. Ordinary JSON object serialization is
not inherently canonical. Two serializers can differ in object-key order,
whitespace, escaping, number spelling, duplicate-key handling, or Unicode
encoding while representing similar source text. The verifier must parse and
re-encode under the named profile.

pcd-cjson-v0 has these rules:

1. Input is UTF-8 without a byte-order mark. The parser rejects trailing
   non-whitespace content and duplicate object names.
2. JSON objects are encoded with keys sorted by ascending Unicode scalar
   value sequence. Arrays preserve their declared order.
3. No insignificant whitespace is emitted. The canonical byte stream has no
   trailing newline.
4. Strings use JSON escaping for quotation mark, reverse solidus, and control
   characters U+0000 through U+001F. The five short escapes are used for
   backspace, form feed, newline, carriage return, and tab. Other control
   characters use uppercase JSON Unicode escapes. Other Unicode scalar values are
   emitted as UTF-8.
5. v0 numbers are integers only. They use an optional minus sign followed by
   0 or a nonzero digit and digits. Leading zeroes, negative zero, decimal
   points, exponents, NaN, and infinity are rejected.
6. Booleans and null use their JSON literals.
7. A SHA-256 identifier is exactly 64 lowercase hexadecimal characters, with
   no sha256: prefix.

The hashes are:

~~~text
node_id     = hex_lower(SHA-256(CanonicalJSON(node_without_node_id)))
content_hash = hex_lower(SHA-256(CanonicalJSON(receipt_without_content_hash)))
~~~

Source provenance hashes use the same SHA-256 and lowercase-hex rules over
the source payload declared by the source adapter. A source adapter must
record its input encoding and revision before hashing.

## Deterministic verifier

The verifier runs these checks in order. It stops at the first fatal error,
but may retain later diagnostics for debugging. A receipt is accepted only
when every required check passes and the result is not illustrative.

| Order | Check | Failure code |
| ---: | --- | --- |
| 1 | Parse one JSON value, reject duplicate keys and trailing content | PCD-E001-PARSE |
| 2 | Validate JSON Schema 2020-12 and required core fields | PCD-E002-SCHEMA |
| 3 | Require the supported canonicalization profile and value restrictions | PCD-E003-CANONICAL-PROFILE |
| 4 | Recompute the receipt content hash | PCD-E004-RECEIPT-HASH |
| 5 | Resolve all logical and content references | PCD-E005-REFERENCE |
| 6 | Check provenance authority, revision ancestry, intervals, and source hashes | PCD-E006-PROVENANCE |
| 7 | Check current and historical revocation status | PCD-E007-REVOCATION |
| 8 | Check typed fact normalization and same-revision fact consistency | PCD-E008-FACT-TYPE |
| 9 | Evaluate norm applicability, exceptions, deadlines, and priorities | PCD-E009-NORM-APPLICABILITY |
| 10 | Recompute proof-node hashes and validate node bodies | PCD-E010-PROOF-HASH |
| 11 | Check DAG acyclicity, roots, edge count, and depth bound | PCD-E011-PROOF-CYCLE |
| 12 | Check ordered rule-trace steps and their premise and conclusion links | PCD-E012-TRACE |
| 13 | Check required-decision applicability, alternatives, chosen outcome, and omission rule | PCD-E013-REQUIRED-DECISION |
| 14 | Check prohibition violations, obligation satisfaction, and unresolved conflicts | PCD-E014-CONFLICT |
| 15 | Apply fail-closed treatment to unknown safety-relevant state | PCD-E015-UNKNOWN-STATE |
| 16 | Replay the declared model and source revisions for the selected profile | PCD-E016-REPLAY-STALENESS |
| 17 | Reject an unsupported or falsely broadened verifier profile | PCD-E017-UNSUPPORTED-PROFILE |
| 18 | Reject any attempt to use the receipt as external-effect authorization | PCD-E018-EXTERNAL-AUTHORIZATION |
| 19 | Recompute the selected logic semantics and translation hashes, CTD policy, and temporal bound | PCD-E019-LOGIC-PROFILE |
| 20 | Recompute every normative Q-pipeline binding from source graph through Q artifact | PCD-E020-COMPILATION-BINDING |
| 21 | Validate the proof or countermodel object separately from the human explanation | PCD-E021-SEMANTIC-RESULT |
| 22 | Check source licenses, adapter revisions, and directed-predicate preservation | PCD-E022-SOURCE-DIRECTION |

The core algorithm is:

~~~text
parse_and_schema(receipt)
check_profile_and_canonical_bytes(receipt)
check_receipt_hash(receipt)
resolve_references(receipt)
check_provenance_and_revocation(receipt)
check_typed_facts(receipt)
evaluate_norms_with_exceptions_and_priorities(receipt)
check_proof_node_hashes_and_dag(receipt)
check_ordered_rule_trace(receipt)
check_required_decision_and_selection(receipt)
check_conflicts_and_unknowns(receipt)
replay_profile_inputs(receipt)
check_logic_profile_and_translation(receipt)
check_normative_compilation_bindings(receipt)
check_semantic_result_object(receipt)
check_source_adapters_and_direction(receipt)
reject_external_effect_authorization(receipt)

if any fatal check failed:
    result = rejected or unresolved
else:
    result = accepted
~~~

rejected means a checked invariant is false, such as a bad hash or
prohibition violation. unresolved means the available evidence cannot
deterministically settle a safety-relevant question, such as a same-priority
conflict or unknown current revocation. The caller must not treat either
result as permission to execute an action.

An illustrative_only result is reserved for fixtures such as
examples/layered_q_tables/example_decision_receipt.json whose synthetic
values demonstrate structure but whose hashes were not independently
recomputed. It is not an acceptance result.

## Threat model and trust boundary

The verifier treats the receipt, model output, Q table, scenario pack,
knowledge-base export, and natural-language explanation as untrusted input.
Threats include:

- a proposer inventing or omitting a fact;
- a model ranking an unsafe alternative above a safe one;
- a stale or revoked source being presented as current;
- duplicate keys or alternate number spellings hiding a different hash input;
- a proof DAG with a missing, duplicated, cyclic, or mismatched node;
- an exception asserted without authority;
- a counterexample being discarded after a positive result; and
- a caller treating a receipt as an execution token.

The deterministic verifier owns acceptance, failure codes, canonical hashes,
conflict handling, and replay status. Models, Q tables, and knowledge bases
may propose or rank. They do not own acceptance.

The verifier does not automatically trust an issuer merely because an issuer
name appears in the receipt. It needs a separate authority registry, and
future deployments may additionally require signatures. Canonical hashing
detects changed content; it does not establish who authored that content.

A proof receipt must not itself authorize an external side effect. A separate
trusted executor must check the policy, current state, revocation status,
freshness, action allowlist, and its own operational limits immediately before
execution. The executor must reject a receipt whose result is illustrative,
rejected, unresolved, stale, revoked, or outside its authority scope.

## Conformance levels

| Level | Required guarantee | What it does not establish |
| --- | --- | --- |
| PCD-S0-STRUCTURE | The JSON Schema fields, types, identifiers, and core additional-property restrictions are satisfied. | It does not recompute hashes or validate meaning. |
| PCD-S1-INTEGRITY | pcd-cjson-v0 is applied, receipt and proof hashes are recomputed, references resolve, and provenance intervals and revocation are checked. | It does not prove that source statements are true in the world. |
| PCD-S2-BOUNDED-RULE-TRACE | Typed facts, finite norms, exceptions, priorities, alternatives, conflicts, counterfactuals, and the ordered rule trace are checked by a deterministic evaluator. | It does not prove unrestricted modal or deontic semantics. |
| GLASSMIND-LAYERED-Q-TABLE-DEMO-V0 | The separate bounded GlassMind receipt is structurally shaped for an explicit synthetic rule trace and is marked illustrative_only. | Its synthetic hashes are not recomputed acceptance evidence, and it does not prove a full deontic logic, real emergency-routing safety, Q-table generalization, or external execution authority. |
| OEWN-KNOWLEDGE-Q-PLANNER-V0 | The pinned OEWN adapter, bounded graph records, six-record public pack, sixteen-record full pack, and finite Q planner provide bounded source and discovery-channel evidence. | This does not constitute recomputed PCD S1/S2 receipt acceptance, source or premise truth, deontic completeness, moral correctness, Q optimality, or external-effect authorization. |
| PCD-S3-NORMATIVE-KERNEL | A semantics-hashed profile is compiled into a finite ESSO or Tau decision kernel, its observables and effects are checked fail-closed, and proof or countermodel output is bound to the receipt. | It establishes model-relative conformance only. It does not establish premise truth, moral completeness, or safe shell execution. |
| PCD-FUTURE-SEMANTIC | A future profile may add a formally specified deontic semantics and a soundness theorem for its checked fragment. | No such theorem is claimed by v0. |

The example receipt is structurally shaped for the GlassMind profile, but its
status is illustrative_only and its hashes are synthetic placeholders. A
live S1 or S2 verifier must replace those values with recomputed hashes and a
record of the actual run.

## Required design decisions for future implementers

Every implementation must record the following decisions in its profile or
design review. Each item has the requested applicability, alternatives,
tradeoffs, enforcement reference, and review trigger.

### D1. Norm semantics

- **Applicability:** Any profile that interprets O, F, P, deadlines, or CTD repairs.
- **Alternatives:** Keep the finite PCD-DL-V0 trace semantics; use a named finite model checker; or adopt a formally specified deontic logic with a translation proof.
- **Tradeoffs:** The finite trace is easy to replay but covers fewer formulas. A richer logic can express more cases but needs a soundness boundary and more tooling.
- **Enforcement reference:** PCD-E009-NORM-APPLICABILITY, PCD-E014-CONFLICT, and the obligations and permissions schema definitions.
- **Review trigger:** Add a new modal operator, temporal connective, exception kind, or CTD form.

### D2. Canonical bytes and identifiers

- **Applicability:** Any profile that hashes a receipt, source, or proof node.
- **Alternatives:** Retain pcd-cjson-v0; adopt a standard canonical JSON profile after compatibility tests; or use a different typed serialization with an explicit migration.
- **Tradeoffs:** The v0 integer-only rule reduces ambiguity but excludes decimal values. A broader number grammar increases convenience and parser risk.
- **Enforcement reference:** PCD-E003-CANONICAL-PROFILE, PCD-E004-RECEIPT-HASH, PCD-E010-PROOF-HASH, and the canonicalization object.
- **Review trigger:** A serializer, number type, Unicode policy, or hash algorithm changes.

### D3. Issuer authority and authenticity

- **Applicability:** Any receipt used outside a local tutorial or test fixture.
- **Alternatives:** A configured issuer registry; signed source manifests; or a hardware or service attestation layer.
- **Tradeoffs:** A registry is simple but operationally centralized. Signatures improve portability but require key lifecycle and revocation handling.
- **Enforcement reference:** PCD-E006-PROVENANCE, PCD-E007-REVOCATION, and the issuer schema definition.
- **Review trigger:** A new issuer scope, key, source adapter, or trust domain is introduced.

### D4. Conflict and tie policy

- **Applicability:** Any decision with more than one applicable norm or more than one admissible alternative.
- **Alternatives:** Priority plus explicit exceptions; lexicographic policy only; or unresolved conflict with mandatory escalation.
- **Tradeoffs:** Priority is expressive but can encode a bad policy. Lexicographic choice is predictable but weak. Escalation preserves safety at the cost of availability.
- **Enforcement reference:** The selection procedure, PCD-E014-CONFLICT, selection_policy, and selection_rank.
- **Review trigger:** A same-priority conflict, new mutually-exclusive action group, or changed rank source appears.

### D5. Uncertainty and omission

- **Applicability:** Any safety-relevant fact, provenance status, model input, or required decision.
- **Alternatives:** Fail-closed abstention or escalation; fail-open best effort; or block until a human supplies evidence.
- **Tradeoffs:** Fail-closed behavior limits unsafe automation but may reduce availability. Fail-open behavior is simpler but cannot support the v0 safety claim.
- **Enforcement reference:** PCD-E015-UNKNOWN-STATE, uncertainty, allowed_resolution_kinds, and omission_admissible.
- **Review trigger:** A policy permits action under unknown state or changes the meaning of abstention.

### D6. Replay and revocation

- **Applicability:** Any receipt whose decision may be replayed, cached, or executed later.
- **Alternatives:** Historical replay only; current replay before every execution; or both with explicit result labels.
- **Tradeoffs:** Historical replay preserves auditability. Current replay better reflects present state but can invalidate an old operational plan.
- **Enforcement reference:** PCD-E006-PROVENANCE, PCD-E007-REVOCATION, PCD-E016-REPLAY-STALENESS, and revocation.
- **Review trigger:** A source revision, validity interval, revocation event, or clock policy changes.

### D7. Executor boundary

- **Applicability:** Any use of a receipt near a real or value-moving side effect.
- **Alternatives:** Keep the receipt advisory; add a separate trusted executor; or bind the receipt to a formally checked command capability.
- **Tradeoffs:** Advisory receipts are safer to deploy but require another decision layer. A bound capability can reduce ambiguity but expands the trusted computing base.
- **Enforcement reference:** PCD-E018-EXTERNAL-AUTHORIZATION, chosen_outcome.external_effect_authorized, and the explicit nonclaims.
- **Review trigger:** Any caller proposes to execute an action from a receipt without a fresh policy and state check.

### D8. Counterfactual coverage

- **Applicability:** Any bounded alternative set or model-generated proposal language.
- **Alternatives:** Enumerate all alternatives in a finite action set; sample and record coverage limits; or use a verified generator with a completeness certificate.
- **Tradeoffs:** Enumeration is easier to falsify but can grow quickly. Sampling scales better but cannot support a completeness claim without additional evidence.
- **Enforcement reference:** negative_knowledge, counterfactual, PCD-E012-TRACE, and the GlassMind challenge corpus boundary.
- **Review trigger:** The action vocabulary, state abstraction, or challenge bound changes.

### D9. Logic profile and CTD semantics

- **Applicability:** Any receipt that interprets a modal, dyadic, input/output, or temporal formula.
- **Alternatives:** SDL/HOL, DDL/HOL, input/output logic, TDL/HOL, or PCD-DL-V0.
- **Tradeoffs:** No profile is uniformly strongest for conflicts, CTD cases, time, automation, and explanation. SDL is a useful baseline but must not resolve a CTD case through explosion.
- **Enforcement reference:** logic_profile, semantic_result, PCD-E009-NORM-APPLICABILITY, and PCD-E017-UNSUPPORTED-PROFILE.
- **Review trigger:** The semantics hash, translation, operator set, temporal bound, checker, or CTD policy changes.

### D10. Normative decision backend

- **Applicability:** Any deployment that claims model-relative formal decision authority.
- **Alternatives:** Finite ESSO-IR with verify or verify-multi; an exported Tau Boolean gate; an HOL checker; or bounded PCD-DL-V0 replay.
- **Tradeoffs:** ESSO supports finite state, counterexamples, explicit observables, and effect checks. Tau can provide a small deterministic policy gate. Both still rely on correct compilation and host inputs.
- **Enforcement reference:** normative_compilation, semantic_result, PCD-E012-TRACE, and PCD-E018-EXTERNAL-AUTHORIZATION.
- **Review trigger:** The backend, solver portfolio, compiler, observable set, effect adapter, or host flag computation changes.

### D11. Knowledge-source and graph semantics

- **Applicability:** Any decision that uses a lexical or knowledge-graph snapshot.
- **Alternatives:** Open English WordNet 2025 as an offline CC BY 4.0 source; Wikidata as optional CC0 enrichment; or another versioned adapter.
- **Tradeoffs:** Offline snapshots improve replay. Enrichment improves coverage but adds mapping, revision, licensing, and contradiction obligations.
- **Enforcement reference:** knowledge_sources, provenance, fact_graph_hash, and PCD-E006-PROVENANCE.
- **Review trigger:** A source, adapter, license, revision, identity mapping, extraction rule, or direction policy changes.

### D12. Utility and alignment model

- **Applicability:** Any compiler that turns admissible alternatives into rewards or Q values.
- **Alternatives:** Bounded utilitarian integer aggregation; lexicographic objectives; constrained optimization; or no automatic ranking with escalation.
- **Tradeoffs:** Aggregation is transparent and replayable but can omit stakeholders, hide tails, or reward a proxy. Lexicographic and constrained models protect side constraints but still need justified ordering and coverage.
- **Enforcement reference:** normative_compilation.utility_model, transition_model_hash, utility_function_hash, and the negative-knowledge ledger.
- **Review trigger:** Stakeholders, weights, uncertainty model, horizon, side constraints, catastrophic-tail bound, or proxy definition changes.

## Current knowledge-Q demonstrator

The current end-to-end bounded lane is the Open English WordNet knowledge-Q
planner. Its stages are:

1. The seed pack names seven source synsets and three goal synsets. The roots
   are `oewn-05736438-n` (data structure), `oewn-06175882-n` (deontic logic),
   `oewn-06197264-n` (utilitarianism), `oewn-05855965-n` (algorithm),
   `oewn-01132241-n` (obligation), `oewn-06702042-n` (permission),
   `oewn-05149888-n` (welfare), `oewn-06175539-n` (modal logic),
   `oewn-05734541-n` (arrangement), and `oewn-05952149-n` (doctrine).
2. The adapter reads the pinned Open English WordNet 2025 compressed release,
   checks its source hash and CC-BY-4.0 metadata, and emits a canonical
   directed graph under explicit node, edge, and traversal bounds. The public
   and full snapshots use the same `retrieved_at` value and contain all ten
   roots, but both are truncated.
3. The public pack in
   `examples/layered_q_tables/planner_required_decisions_public.json` has six
   required decisions. The full pack in
   `examples/layered_q_tables/planner_required_decisions_full.json` has
   sixteen. The public records, including IDs and canonical field values, are
   an exact semantic subset of the full records. The full profile adds the
   four remaining single-root reviews and six bounded cross-root reviews.
4. Each applicability value names one or more of the ten roots. A required
   evidence value of 1 asks for source-directed discovery, 2 asks for
   reverse-browse discovery, and 3 asks for both. These are model-local
   discovery-channel requirements. A source-directed edge remains directed,
   and reverse browsing never creates an inverse fact.
5. The planner compiles each record to one generic `resolve` terminal action
   or one `abstain_or_escalate` terminal action. The listed goal alternatives
   are declarative audit metadata, not sixteen separately optimized Q
   actions. Missing traversal coverage, a missing root, an ambiguous lexical
   mapping, a changed source or adapter hash, or an attempted promotion of a
   lexical link into normative or logical authority must activate review and
   fail-closed abstention or escalation.

The graph hashes in the current-evidence table identify the public and full
canonical extracted graphs. The compressed source hash identifies the pinned
release from which they were extracted. An absent path in either bounded graph
is not evidence that the path is absent from the complete source or the world.
The ESSO result in the table is finite-adapter invariant evidence, not a
recomputed PCD S1/S2 receipt result. Tau remains exactly
`specified_not_run`.

## Explicit nonclaims

Version 0 does not claim:

- that a valid schema instance proves the truth of its facts;
- that a SHA-256 hash proves authenticity, authority, or semantic correctness;
- that O, F, or P records implement all of standard deontic logic;
- that a proof DAG proves full modal semantics or real-world causality;
- that a Q table or language model understands obligations;
- that one deontic logic is best for every normative domain;
- that an ESSO or Tau PASS proves the truth or completeness of its premises;
- that a human explanation is a checker proof object;
- that a WordNet edge or Q evidence bit proves a proposition, rule, obligation,
  permission, ethical conclusion, or norm justification;
- that reverse graph browsing proves an inverse predicate;
- that a bounded utilitarian reward is complete ethical alignment;
- that a higher rank makes an unsafe alternative acceptable;
- that a bounded GlassMind grid generalizes to real emergency routing;
- that the current OEWN knowledge-Q planner has already produced recomputed
  PCD S1 or S2 receipt acceptance;
- that a receipt authorizes an external side effect;
- that historical acceptance remains current after revocation or state change;
- that an enumerated alternative set is complete outside its declared bound; or
- that the illustrative example has independently recomputed hashes.

## Separate illustrative synthetic receipt

examples/layered_q_tables/example_decision_receipt.json describes one
bounded synthetic routing case:

1. The normalized facts place the agent at s000005, mark edge-7 blocked,
   mark edge-8 open, record one remaining step, and show that a dispatcher
   escalation channel is available.
2. A conditional obligation requires avoiding the blocked edge, and a
   conditional prohibition forbids selecting it. A deadline obligation
   requires an explicit routing resolution by step 1. A permission allows
   escalation through the available dispatcher channel.
3. Four alternatives are listed: route through the safe eastern edge, route
   through the blocked edge, abstain, and escalate. The blocked-edge
   counterfactual is rejected by the prohibition trace. Abstain and escalate
   remain explicit fail-closed alternatives.
4. The safe eastern route is selected because it is admissible, satisfies the
   checked obligations, and has the highest declared rank among admissible
   alternatives. The chosen outcome explicitly sets
   external_effect_authorized to false.
5. The proof DAG links fact normalization, norm activation, rejected
   counterfactual, safe alternative, selection, and the no-conflict claim.
   The rule trace names those same links.
6. The receipt records active provenance, a not-revoked check, a review trigger
   for map or policy changes, negative knowledge, a canonicalization profile,
   and explicit nonclaims.
7. The receipt binds the source graph, canonicalizer, PCD-DL-V0 semantics,
   policy, utility, transition model, generator, admissibility mask, and Q table.
8. The ESSO kernel, Tau export, and semantic query are marked not-run. The
   human explanation is stored separately from any future checker proof or
   countermodel.

The receipt contains repeated-character 64-character hexadecimal values as
synthetic placeholders. Its demo_status and verifier fields state that
the values were not independently recomputed. The file is therefore useful
for schema and reference review, while a live verifier must recompute every
hash before reporting S1 or S2 acceptance.
