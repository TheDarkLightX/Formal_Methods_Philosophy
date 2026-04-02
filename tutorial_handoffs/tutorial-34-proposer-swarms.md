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
