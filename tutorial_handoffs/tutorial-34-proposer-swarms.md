# Tutorial 34 Handoff

## Scope

This tutorial is about:

- proposer swarms in formal-gated systems
- bounded role specialization before an exact gate
- deterministic shortlist construction
- replayable denial witnesses
- why compressed local models make swarms practical

This tutorial is not for:

- claiming that multi-agent voting creates truth
- replacing Tau, validators, or proof kernels with a swarm
- generic autonomous-agent enthusiasm

## Current public-facing structure

This tutorial is not public yet.

If it becomes public, it should teach one clean ladder:

1. one proposer and one exact gate
2. why one proposer is often too narrow
3. role-specialized swarms
4. deterministic merger and shortlist construction
5. exact gate invariants
6. replayable denial witnesses
7. how MPRD and ZenoDEX fit the pattern
8. why model compression changes the economics

The tutorial should read as architecture, not as a general agent survey.

## Strongest local results to preserve

1. The architecture only makes sense if execution authority remains local to
   the exact gate.

2. The right slogan is:
   - many proposers widen bounded search
   - one exact gate keeps authority narrow

3. The swarm should be role-specialized, not merely cloned:
   - explorer
   - conservative proposer
   - critic
   - summarizer
   - denial explainer

4. The merger should remain deterministic when possible:
   - canonicalize
   - deduplicate
   - rank
   - build `top-k`

5. The key invariant is still:

```text
Execute(state, action) => action in Shortlist(state) and Allowed(state, action)
```

6. MPRD is the clearest teaching case because it already has:
   - untrusted proposer
   - trusted policy layer
   - guarded execution

7. ZenoDEX is the next case because it already has:
   - bounded candidate production
   - Tau-facing validator logic
   - exact runtime kernels

## Key concepts that must be explained in the tutorial

1. **Proposer**
   - an untrusted bounded component that emits candidates
   - not an execution authority

2. **Swarm**
   - several proposers with different jobs
   - not a pile of cloned chat models

3. **Exact gate**
   - the trusted decision layer
   - examples in this repo:
     - Tau policy
     - validator graph
     - proof checker
     - deterministic admissibility predicate

4. **Shortlist**
   - the bounded set of candidates that survive merger and deduplication

5. **Witness replay**
   - denial or failure must leave a replayable artifact:
     - denied clause
     - failing validator
     - counterexample trace
     - failed proof obligation

6. **Role specialization**
   - why a swarm is useful at all:
     - explorer widens search
     - conservative proposer protects approval rate
     - critic predicts denial risk
     - summarizer compresses shared context
     - explainer helps repair after denial

7. **Bounded interface**
   - the swarm must emit finite, typed candidate objects
   - not arbitrary free-form execution requests

## Source packet

Repo-specific architecture sources:

- MPRD repository:
  - https://github.com/TheDarkLightX/MPRD
- ZenoDEX repository:
  - https://github.com/TheDarkLightX/ZenoDEX
- Tutorial 6, `tutorials/mprd-and-algorithmic-ceo.md`
- Tutorial 17, `tutorials/software-shapes-and-zenodex.md`
- Tutorial 33, `tutorials/formal-neural-networks.md`

Supporting external papers:

- Self-consistency:
  - https://arxiv.org/abs/2203.11171
- Mixture-of-Agents:
  - https://arxiv.org/abs/2406.04692

The tutorial should use the external papers only for the narrow claim that
multiple reasoning paths or agent roles can improve bounded search quality.
They do not justify execution authority by themselves.

## Current experiment packet

The immediate experiment is not "prove that swarms are always better".
The immediate experiment is:

- use compressed local models as bounded role-specialized proposers
- run them before an exact gate
- measure shortlist quality and approval quality

### Minimal swarm shape

Roles:

- explorer
- conservative proposer
- critic
- summarizer

Required interfaces:

```text
Explorer(state) -> [candidate]
Conservative(state) -> [candidate]
Critic(state, candidate) -> deny_risk
Summarizer(raw_state) -> bounded_facts
Merge(candidates, deny_risks, bounded_facts) -> shortlist
Gate(state, candidate) -> allow | deny + witness
```

### Core invariants

These must stay explicit:

```text
Execute(state, action) => action in Shortlist(state)
Execute(state, action) => Allowed(state, action)
Denied(state, action) => exec = skipped
```

### Minimal metrics

For each run, record:

- number of unique candidates emitted
- shortlist size
- approval count
- denial count
- denial reasons by type
- latency per role
- total gate calls
- one replayable witness per denial class

### First useful comparison

Compare:

1. one proposer
2. one proposer plus critic
3. four-role swarm

The question is not only:

- "which one gets the best answer?"

The more useful questions are:

- which one wastes fewer gate calls?
- which one gets higher approval rate?
- which one produces better denial witnesses?

## Known mistakes or drift to avoid

1. Do not describe the swarm as a democratic truth engine.
2. Do not imply that more agents automatically means more safety.
3. Do not let the merger quietly become the true authority layer.
4. Do not forget witness replay. A denial log with no refinement loop is not
   the intended architecture.
5. Do not bury the compression link. The swarm becomes practical only because
   local models are getting much cheaper.

## Next honest frontiers

- quantify when diversity helps enough to justify extra gate calls
- define a clean cost model for swarm breadth versus shortlist quality
- build one bounded swarm experiment on laptop hardware with a real exact gate

## Source range

- `tutorial_drafts/proposer-swarms.md`
- `tutorials/mprd-and-algorithmic-ceo.md`
- `tutorials/software-shapes-and-zenodex.md`
- `tutorials/formal-neural-networks.md`
