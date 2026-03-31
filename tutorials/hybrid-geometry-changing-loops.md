---
title: "Hybrid geometry-changing loops"
layout: docs
kicker: Tutorial 31
description: "Study loops that first change ambiguity geometry and then compile or control the residue, rather than only learning a front-end for a verifier."
---

<details open>
<summary><strong>Road map</strong></summary>

This tutorial asks why some strong loops are not best described as
verifier-compilers at all.

- **Parts I-II**: direct control versus hybrid geometry-changing loops
- **Parts III-IV**: the clean bounded requirements example and the weighted comparison law
- **Parts V-VI**: graph-side regime compilers and the newer low-edge concentration branch
- **Part VII**: what this branch has actually achieved, and what still needs work

</details>

## The motivating contrast

Verifier-compilers are one important neuro-symbolic loop family.

They try to learn a reusable symbolic front-end for an exact verifier.

But they are not the only strong loops.

Another family works in two stages:

1. a front stage changes the geometry of the task space
2. a back stage controls or compiles only the residue

That is a different design pattern.

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

The bounded comparison branch introduced a cleaner way to talk about that:

```text
U = alpha * pure_resolved_mass + beta * depth_saving - gamma * acquisition
```

This matters because “better” becomes conditional.

- some loops are unit-weight best
- some become best only when acquisition is expensive

So the right comparison is not:

- which loop looks smarter?

It is:

- which loop wins under the stated cost model?

**Interactive lab**

- [Hybrid Loop Comparison Lab]({{ '/hybrid_loop_comparison_lab.html' | relative_url }})

## Part III: graph-side regime compilers

The corrected graph branch suggests a second kind of hybrid loop.

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
  <p class="fp-figure-title">High-band overlap on the corrected graph branch</p>
  {% include diagrams/graph-regime-overlap.svg %}
  <figcaption class="fp-figure-caption">
    The high checked band is now a genuine overlap zone. The exact compiler
    chooses between star-plus-low-edge and repaired multipartite rather than
    treating the branch as one monolithic family.
  </figcaption>
</figure>

**Interactive lab**

- [Graph Regime Compiler Lab]({{ '/graph_regime_compiler_lab.html' | relative_url }})

## Part IV: the low-edge proof branch

The newer rabbit hole changed character again.

On the low-edge side, the branch no longer has only a family compiler. It now
has a proof-shaped hybrid:

1. starify each connected component
2. balance the resulting star sizes

The first stage survives in a surprisingly clean form on the checked tree
branch:

- an improving pendant-subtree move can always be chosen so that it moves a
  one-branch pendant subtree toward a hub
  - hub-target survives
  - leaf-only fails
  - pendant-star-only fails

The second stage is exact balancing on the star-family side.

So the low-edge branch is another hybrid, but of a different kind:

- a concentration stage
- followed by an exact balancing stage

The newer composition result says that this is not only an interpretation. On
the checked low-edge forest branch, that is the surviving mechanism.

<figure class="fp-figure">
  <p class="fp-figure-title">Low-edge concentration and balancing</p>
  {% include diagrams/low-edge-concentration.svg %}
  <figcaption class="fp-figure-caption">
    The low-edge branch is a hybrid too. It first concentrates component
    shape, then applies an exact size-balancing law.
  </figcaption>
</figure>

## Part V: what this means for loop search

The strongest future loop candidates are unlikely to be single-stage loops.

The current bounded evidence points toward patterns like:

- quotient stage plus residual controller
- regime decomposition plus direct compiler
- concentration stage plus exact balancing stage

That is the strongest current reason to think there are useful loop families
beyond plain verifier-compilation.

The common idea is simple:

- reshape first
- solve the smaller residue second

## Part VI: what this branch has achieved

This branch can now teach four stable lessons.

1. **Geometry change can beat direct control**
   - the pair-basis plus block-separator line is the cleanest example
2. **Weighted comparison matters**
   - witness acquisition and residual savings must be priced honestly
3. **Exact regime compilers are real loop objects**
   - the graph branch is not only a classifier atlas
4. **Some hybrids are concentration processes**
   - the low-edge branch now has a real two-stage mechanism

That is enough to justify hybrid geometry-changing loops as a tutorial line in
their own right.

## Related tutorials

- [Tutorial 27: Verifier-compiler loops]({{ '/tutorials/verifier-compiler-loops/' | relative_url }})
- [Tutorial 29: Loop-space geometry]({{ '/tutorials/loop-space-geometry/' | relative_url }})
- [Tutorial 30: Counterexample-guided requirements discovery]({{ '/tutorials/counterexample-guided-requirements-discovery/' | relative_url }})

## Next honest frontiers

This branch is strong enough to teach, but not finished.

- a clearer family taxonomy across quotient loops, regime compilers, and
  concentration loops
- stronger weighted comparisons on the corrected graph metric
- proofs for the newer concentration laws, not only checked scans

Those frontiers are already narrower than the original question. That is part
of the achievement.
