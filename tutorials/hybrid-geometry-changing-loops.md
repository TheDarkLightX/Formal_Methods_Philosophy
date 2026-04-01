---
title: "Hybrid geometry-changing loops"
layout: docs
kicker: Tutorial 31
description: "Study loops that first change ambiguity geometry and then compile or control the residue, rather than only learning a front-end for a verifier."
---

## The motivating contrast

Verifier-compilers are one important neuro-symbolic loop family.

They try to learn a reusable symbolic front-end for an exact verifier.

But they are not the only strong loops.

Another family works in two stages:

1. a front stage changes the geometry of the task space
2. a back stage controls or compiles only the residue

That is a different design pattern.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Vocabulary Note</p>
  <ul>
    <li><strong>Quotient</strong> means a partition of the task family into cases the current loop cannot yet tell apart.</li>
    <li><strong>Residue</strong> means the smaller leftover problem after that first partition.</li>
    <li><strong>Controller</strong> means the compact symbolic rule that handles that leftover problem.</li>
    <li><strong>Frontier</strong> means the best checked tradeoff on a named bounded family.</li>
  </ul>
</div>

The front stage might use:

- a witness basis
- a quotient map
- a temporal basis change
- or a structural regime decomposition

The back stage might use:

- a question policy
- a small controller
- a residual verifier
- or a direct amount compiler

<figure class="fp-figure">
  <p class="fp-figure-title">Direct control versus hybrid control</p>
  {% include diagrams/hybrid-loop-comparison.svg %}
  <figcaption class="fp-figure-caption">
    The decisive difference is not only controller size. The hybrid loop pays
    for front-stage geometry change, settles a large mass of cases early, then
    uses a smaller residual controller.
  </figcaption>
</figure>

## Part I: the cleanest bounded example

The clearest example so far comes from requirements discovery.

On exact missing-set identification with the same block-query language:

- a direct raw-family controller needs depth `n`
- a pair-basis plus block-separator residual controller needs
  `ceil(log2 n)`

That is a real structural win on the controller side.

The gain comes from changing geometry first.

The loop is stronger because the pair basis turns the raw family into a much
smaller singleton residue before the residual controller starts.

## Part II: why cost models matter

That does not mean the hybrid loop is automatically better in every regime.

Witness acquisition still costs something.

The bounded comparison line introduced a cleaner way to talk about that:

```text
U = alpha * pure_resolved_mass + beta * depth_saving - gamma * acquisition
```

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Formula Refresher</p>
  <ul>
    <li><strong>`alpha`</strong> weights how much value is assigned to cases settled early.</li>
    <li><strong>`beta`</strong> weights how much value is assigned to a smaller residual decision process.</li>
    <li><strong>`gamma`</strong> weights the cost of collecting the front-stage structure.</li>
    <li>The formula is a scored tradeoff, not a universal law of nature. It says which loop wins under the chosen cost model.</li>
  </ul>
</div>

This matters because “better” becomes conditional.

- some loops are unit-weight best
- some become best only when acquisition is expensive

So the right comparison is always relative to a cost model: which loop wins
under the stated weights, not which loop looks smarter in the abstract.

**Interactive lab**

- [Hybrid Loop Comparison Lab]({{ '/hybrid_loop_comparison_lab.html' | relative_url }})

## Part III: graph-side regime compilers

The corrected graph line suggests a second kind of hybrid loop.

The direct compiler there does not come from one monolithic family. It comes
from taking the maximum of several exact regimes:

- balanced star forests
- repaired multipartite structure
- and, on the checked small domain, one explicit point correction

That is already a geometry-changing loop.

Instead of learning one front-end for one verifier, it decomposes the frontier
into exact regions and compiles those regions directly.

On the checked high band, the overlap itself compresses into a piecewise
compiler:

- low plateau
- middle interval delegated to the star-plus-leaf family
- near-top multipartite peak
- top tie

That is stronger than an atlas of cases. It is a direct compiler for the
competition between the two structural families.

<figure class="fp-figure">
  <p class="fp-figure-title">High-band overlap on the corrected graph line</p>
  {% include diagrams/graph-regime-overlap.svg %}
  <figcaption class="fp-figure-caption">
    The high checked band is now a genuine overlap zone. The exact compiler
    chooses between star-plus-low-edge and repaired multipartite rather than
    treating the graph line as one monolithic family.
  </figcaption>
</figure>

**Interactive lab**

- [Graph Regime Compiler Lab]({{ '/graph_regime_compiler_lab.html' | relative_url }})

## Part IV: the low-edge concentration mechanism

The low-edge analysis changed character at this point.

It no longer has only a family compiler. It now has a proof-shaped hybrid with
two distinct stages:

1. starify each connected component
2. balance the resulting star sizes

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Graph Vocabulary Note</p>
  <ul>
    <li><strong>Star</strong> means the graph-theory shape with one hub vertex and several leaf vertices attached to it.</li>
    <li><strong>Starify</strong> means reshape a component into that star form.</li>
    <li><strong>Balance star sizes</strong> means redistribute leaves so the component stars are as even in size as the model allows.</li>
  </ul>
</div>

The first stage survives in a surprisingly clean form on the checked tree
domain:

- an improving pendant-subtree move can always be chosen so that it moves a
  pendant subtree with one internal fork toward a hub
  - hub-target survives
  - leaf-only fails
  - pendant-star-only fails

The second stage is exact balancing on the star-family side.

### The composed two-stage result

The low-edge line is another hybrid, but of a different kind:

- a concentration stage
- followed by an exact balancing stage

The newer composition result says that this is not only an interpretation. On
the checked low-edge forest family, that is the surviving mechanism.

And on the checked tree-side subproblem, the concentration path itself can stay
inside the smaller local move language. The method does not need to fall back
to arbitrary pendant-subtree moves after the first step.

The newest checked refinement is stronger again: the path survives even if each
step is restricted to a smallest available hub-target move of that same form.

And that controller now has an exact checked depth cutoff. On the checked tree
domain, the smallest surviving branching-depth bound is `2`.

The cutoff is not arbitrary. A terminal-cherry ladder family now witnesses it:
the `h = 2` case is exactly the shape that forces depth `2`.

The positive side is exact too. On the checked tree domain, every move selected
by that depth-2 controller belongs to one finite rooted alphabet:

- leaf
- cherry
- three-leaf star
- broom-1
- broom-2

And that finite alphabet is already minimal on the checked domain. No proper
subset survives.

<figure class="fp-figure">
  <p class="fp-figure-title">Low-edge concentration and balancing</p>
  {% include diagrams/low-edge-concentration.svg %}
  <figcaption class="fp-figure-caption">
    The low-edge analysis is a hybrid too. It first concentrates component
    shape, then applies an exact size-balancing law.
  </figcaption>
</figure>

## Part V: what this means for loop search

The strongest future loop candidates are unlikely to be single-stage loops.

The current bounded evidence points toward patterns like:

- quotient stage plus residual controller
- regime decomposition plus direct compiler
- concentration stage plus exact balancing stage

Those patterns share a common idea, and it connects back to the cost formula
from Part II: the front stage pays an acquisition cost to reshape the problem,
while the back stage reaps the savings on a smaller residue.

- reshape first
- solve the smaller residue second

## Part VI: what these bounded results have achieved

This tutorial line can now teach four stable lessons.

1. **Geometry change can beat direct control**
   - the pair-basis plus block-separator line is the cleanest example
2. **Weighted comparison matters**
   - witness acquisition and residual savings must be priced honestly
3. **Exact regime compilers are real loop objects**
   - the graph line is not only a classifier atlas
4. **Some hybrids are concentration processes**
   - the low-edge line now has a real two-stage mechanism

Together, these justify hybrid geometry-changing loops as a tutorial line in
their own right.

## Related tutorials

- [Tutorial 27: Verifier-compiler loops]({{ '/tutorials/verifier-compiler-loops/' | relative_url }})
- [Tutorial 29: Loop-space geometry]({{ '/tutorials/loop-space-geometry/' | relative_url }})
- [Tutorial 30: Counterexample-guided requirements discovery]({{ '/tutorials/counterexample-guided-requirements-discovery/' | relative_url }})
