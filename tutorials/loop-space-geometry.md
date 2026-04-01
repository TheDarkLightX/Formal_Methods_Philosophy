---
title: "Loop-space geometry"
layout: docs
kicker: Tutorial 29
description: "Map neuro-symbolic loops into witness languages, quotients, separator policies, label bases, and compiled artifacts, then study the bounded results that show why some loops are structurally stronger than others."
---

<details open>
<summary><strong>Road map</strong></summary>

This tutorial asks what really changes when one neuro-symbolic loop is stronger
than another.

- **Parts I-II**: the basic geometry, witness language, stored state, ambiguity quotient, separator language, label basis, and target artifact
- **Parts III-IV**: the requirements-discovery case study and the cleanest bounded quotient-first loop
- **Parts V-VI**: graph-side regime compilers and the newer low-edge concentration mechanism
- **Part VII**: what these bounded results have already established

</details>

## The motivating question

Two loops can solve the same task and still be very different.

One loop might:

- ask the verifier again
- collect one more example
- and continue almost unchanged

Another loop might:

- change the witness basis
- collapse the task into ambiguity classes
- and then run a much smaller controller on what remains

That difference is the reason to talk about loop-space geometry.

The best current bounded results suggest that the strongest loops are usually
not just:

- better prompts
- larger models
- or a bigger verifier budget

They are stronger because they reshape the remaining search problem.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Working Vocabulary</p>
  <ul>
    <li><strong>Witness</strong> means a small concrete object that exposes structure, for example a counterexample, signature, trace, or parameter choice. It does not mean eyewitness testimony.</li>
    <li><strong>Quotient</strong> means a grouping of cases that the current loop cannot distinguish. If two hidden targets induce the same stored state, they land in the same quotient class.</li>
    <li><strong>Residue</strong> means what is still unresolved after that grouping. It is the smaller problem that remains after the first compression.</li>
    <li><strong>Controller</strong> means a compact symbolic rule for what to do next, for example route, ask, accept, reject, or refine. It does not mean a hardware controller.</li>
    <li><strong>Frontier</strong> means the best checked tradeoff or best checked value on a named bounded family. It does not mean an unexplored frontier in the loose everyday sense.</li>
    <li><strong>Carve</strong> means make an initial coarse split of the family, or restrict attention to a smaller subfamily, before using a finer second-stage language.</li>
    <li><strong>Star</strong> means the graph-theory shape with one hub vertex connected to several leaves. A <strong>star forest</strong> is a disjoint union of those shapes.</li>
    <li><strong>Repair</strong> in the nearby verifier and software-repair tutorials means a structured correction object that fixes a mixed or failing case, not just informal cleanup.</li>
  </ul>
</div>

## Part I: the main axes of loop space

A neuro-symbolic loop can be factored into at least six axes.

- **Witness language**: what counts as an admissible failure, trace, or local certificate
- **Stored state**: what the loop keeps after collecting evidence
- **Ambiguity quotient**: which hidden targets still look the same after that state is stored
- **Separator language**: what extra questions, tests, or residual policies are allowed above the quotient
- **Label basis**: the coordinates in which the loop names outcomes
- **Target artifact**: what reusable symbolic object the loop is trying to compile

That factorization is useful because it separates changes that are often mixed
together in informal descriptions.

<figure class="fp-figure">
  <p class="fp-figure-title">Loop-space geometry map</p>
  {% include diagrams/loop-space-geometry-map.svg %}
  <figcaption class="fp-figure-caption">
    A loop gets stronger when it changes witness geometry first, then compiles
    or controls only the smaller residue that survives.
  </figcaption>
</figure>

The cleanest mental model is a sequence of compressions:

1. observe failures or witnesses
2. store them in a state
3. collapse the hidden family into ambiguity classes
4. run the smallest separator policy needed above that quotient
5. compile the surviving structure into a controller, question policy, or regime law

This is not only about speed.

It is about changing the shape of what remains to be searched.

## Part II: the first big correction

The simplest story says:

- collect counterexamples
- repair the missing part
- ask a stakeholder when needed

The bounded results correct that story.

After saturated witness collection, the right object is not a bag of examples.
It is an observation map:

```text
O_W(M) = {S in W | S ⊆ M}
```

where:

- `W` is a witness library
- `M` is the hidden target, for example a missing requirement set

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Quick Logic Refresher</p>
  <ul>
    <li><strong>`S ⊆ M`</strong> means the witness signature <code>S</code> is fully contained inside the hidden target <code>M</code>.</li>
    <li><strong>`O_W(M)`</strong> is the set of all witnesses from <code>W</code> that fit inside <code>M</code>.</li>
    <li><strong>`M ~ M'`</strong> means the loop cannot currently tell <code>M</code> and <code>M'</code> apart. Here <code>~</code> means indistinguishable under the current observation state, not vague similarity.</li>
  </ul>
</div>

That moves the loop from example collection to quotient construction.

Two hidden targets are equivalent for the loop when they induce the same
observation state:

```text
M ~ M'  iff  O_W(M) = O_W(M')
```

A plain direct controller acts on the raw target family.
A geometry-changing loop acts on this quotient first, then controls only the
residue.

## Part III: the requirements-discovery case study

The requirements case study is the clearest worked example.

Its core question is:

When a counterexample exposes a missing requirement, how much of the repair is
already determined by witness structure, and how much still needs follow-up
questions?

Three bounded corrections matter here.

### 1. Pure recovery is not only about singleton witnesses

The first step says direct recovery works when every missing requirement has a
singleton witness. That is real, but it is not the whole story.

Even without singleton witnesses, pure recovery can still succeed if the full
observation map is injective on the omission family.

So the real question is not only:

- does a singleton witness exist?

It is:

- does the stored state already separate the hidden targets?

### 2. Scope matters sharply

On unrestricted omission families, singleton witnesses remain a global
bottleneck.

On scoped families, especially pair-lobotomy families, oracle help becomes
strictly stronger.

That means requirements discovery is not one monolithic task. The omission
family changes the loop geometry.

### 3. Pair basis plus good separators is a real hybrid

Once the witness library contains all pairs:

- the residual ambiguity collapses to singleton uncertainty
- the remaining difficulty moves to separator language

Then the bounded ladder becomes:

- pair-subset queries, no help
- singleton-membership queries, linear depth
- block-intersection queries, logarithmic depth

That is the first clean example of a loop becoming stronger by changing
geometry first and only then using a stronger residual controller.

<figure class="fp-figure">
  <p class="fp-figure-title">Counterexamples, quotient, then separator policy</p>
  {% include diagrams/requirements-loop-ladder.svg %}
  <figcaption class="fp-figure-caption">
    The pair basis collapses the hidden family to a much smaller singleton
    residue. Only then do block questions do the remaining work.
  </figcaption>
</figure>

**Interactive labs**

- [Requirements Loop Geometry Lab]({{ '/requirements_loop_geometry_lab.html' | relative_url }})
- [Hybrid Loop Comparison Lab]({{ '/hybrid_loop_comparison_lab.html' | relative_url }})

## Part IV: temporal labels are also part of loop space

Loop-space geometry is not only about witnesses and separators.

It also includes the label basis.

The temporal-label result shows a small but important result:

- raw monitor-cell labels are strictly finer than flat two-step trace labels on the full family
- after the right first coarse split, the richer temporal basis stops buying a finer partition

That means a stronger basis is not always the right global basis. Sometimes it
is the right second-stage basis.

The easiest analogy is coordinates in geometry.

Polar coordinates can be the right language for one subproblem and the wrong
language for another. Temporal labels behave the same way in this bounded loop
setting.

## Part V: graph-side compilers

The corrected graph line teaches a different lesson.

At first it looked like a large collection of unrelated graph families. After
the corrected total-domination metric, the analysis compressed much more sharply.

The stable bounded survivors now include:

- complete multipartite families on the corrected frontier
- repaired multipartite additivity
- exact low-edge and repaired-block optimizers
- a corrected small-domain single-block compiler
- a structurally explained point correction at `(7, 9)`
- a full-star-plus-low-edge family compiler
- and a wider two-family overlap compiler on the checked high band

So loop space does not only contain:

- question policies
- verifier front-ends
- and witness languages

It also contains exact regime compilers.

<figure class="fp-figure">
  <p class="fp-figure-title">Corrected graph regime map</p>
  {% include diagrams/graph-regime-overlap.svg %}
  <figcaption class="fp-figure-caption">
    The corrected graph line is easiest to understand as a regime map. Low
    budgets live on the left. Higher budgets enter an overlap band where two
    exact structural families compete.
  </figcaption>
</figure>

## Part VI: the low-edge concentration mechanism

The newest part of the graph line is the clearest “show what was achieved”
story.

It no longer says only:

- a balanced star forest fits the checked frontier

It now has a mechanism.

### Stage 1: starify components

Here "starify" means: turn each connected component into a star-shaped graph,
one hub with several leaves, without changing the bounded objective being
optimized.

On checked connected trees, every non-star class has an improving
pendant-subtree move.

The analysis then compresses further:

- on checked trees with `n in {8, 9}`, the improving move can always be chosen
  so that the reattachment target is a maximum-degree hub
- and on the same checked domain, the moved subtree can be chosen with at most
  one internal fork
  - leaf-only moves fail
  - pure pendant-star moves fail

So the surviving move language is not “some local repair happens somewhere.”
It is:

- move a pendant subtree with one internal fork toward a hub

### Stage 2: balance star sizes

Once component shape is concentrated, the star-family product law can be
optimized exactly by balancing component sizes.

That gives a second clean stage:

- smooth an uneven star profile into the balanced one

### The composed result

The checked low-edge analysis is now a two-stage concentration process:

1. starify components
2. balance star sizes

The newer composition result tightens that from a teaching paraphrase into the
checked mechanism itself. On the checked low-edge forest family, those are the
two surviving stages.

The tree-side subproblem also tightened one step further. On the checked tree
domain, the whole monotone path to the star can stay inside the smaller move
language, repeatedly moving pendant subtrees with one internal fork into hubs.

It tightened once more after that. On the checked tree domain, the path still
survives if each step uses a smallest available hub-target move of that same form.

There is now an exact checked depth cutoff on that local controller. Depth `0`
fails, depth `1` fails, and depth `2` is the smallest surviving bound on the
checked tree domain.

That cutoff also has a named witness family now. On the terminal-cherry ladder
family, the smallest surviving hub-target move of that form has branching depth
exactly `h`. The `h = 2` case is the clean family-level reason depth `1` fails
and depth `2` survives on the checked domain.

The positive side is now exact too. On the same checked domain, every move
selected by that depth-2 controller falls into one finite rooted alphabet:
leaf, cherry, three-leaf star, broom-1, or broom-2. And one more exhaustive
check closes the slack, the full five-template set is the unique surviving
controller subset on the checked domain.

<figure class="fp-figure">
  <p class="fp-figure-title">Low-edge concentration map</p>
  {% include diagrams/low-edge-concentration.svg %}
  <figcaption class="fp-figure-caption">
    The low-edge analysis is no longer only a frontier fit. It is a two-stage
    concentration process with a geometric front stage and an exact balancing
    back stage.
  </figcaption>
</figure>

**Interactive lab**

- [Graph Regime Compiler Lab]({{ '/graph_regime_compiler_lab.html' | relative_url }})

## Part VII: what these bounded results have already achieved

The stable bounded ladder that is now strong enough to teach runs through four
main ideas.

1. **Observation quotients**
   - the loop should be analyzed through the state it stores, not only through
     the examples it sees
2. **Witness-basis and separator ladders**
   - pair bases, separator expressivity, and staged label choices are real loop
     axes
3. **Exact regime compilers**
   - some problems compress into exact piecewise families rather than into one
     monolithic controller
4. **Concentration mechanisms**
   - some strong loops work by reshaping the problem in stages before the final
     exact law is even applied

That is the strongest bounded reason so far to think there are useful
neuro-symbolic loops beyond plain verifier-compilation.

## Related tutorials

- [Tutorial 27: Verifier-compiler loops]({{ '/tutorials/verifier-compiler-loops/' | relative_url }})
- [Tutorial 30: Counterexample-guided requirements discovery]({{ '/tutorials/counterexample-guided-requirements-discovery/' | relative_url }})
- [Tutorial 31: Hybrid geometry-changing loops]({{ '/tutorials/hybrid-geometry-changing-loops/' | relative_url }})
- [Tutorial 32: Temporal label functions and staged bases]({{ '/tutorials/temporal-label-functions-and-staged-bases/' | relative_url }})
