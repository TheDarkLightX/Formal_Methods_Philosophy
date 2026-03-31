---
title: "Profit agents, post-AGI economics, and mechanism design"
layout: docs
kicker: Tutorial 28
description: "Study bounded toy economies for profit agents under explicit assumptions, then climb from platform incentives and demand closure to coordination and mechanism design."
---

<details open>
<summary><strong>Road map</strong></summary>

This tutorial studies a separate branch from the verifier-compiler line.

The question here is not how to compress a verifier. The question is what
happens in a bounded toy economy if strong profit agents become widespread.

- **Experiments 1-3**: profit regions, complement heterogeneity, and governed admissibility
- **Experiments 4-7**: passive ownership, demand closure, active-owner limits, and coordination
- **Experiments 8-10**: prices, quotas, heterogeneous complements, and composed mechanisms
- **Experiments 11-13**: sink bundles, zero-employee firm entry, and discovery bottlenecks
- **Experiments 14-16**: slot sales, admissibility caps, and frontier-lab branch divergence
- **Experiments 17-19**: household participation, asymmetric routing, and protocol equalization
- **Experiments 20-21**: machine-control thresholds and trust-lag divergence
- **Experiments 22-27**: repeated trust learning, routing lock-in, incumbent rent lockout, assurance design, assurance lever weights, and assurance funding

The sections below are numbered for readers as `Experiment 1`, `Experiment 2`,
and so on. The old working-notebook ids are kept in parentheses so the research
artifacts still line up.

</details>

This tutorial is explicitly assumption-driven.

Every result below is a bounded theorem inside a toy model, not a general claim
about the real economy. The point is to make the logic precise enough that
counterexamples, edge cases, and mechanism changes become visible.

## Assumption tree

The right way to use this branch is as a decision tree over assumptions, not as
one hidden story about the future.

The top-level axes are:

1. capability
   - current AI
   - AGI-level agent
2. control shell
   - legal-world shell
   - crypto-native shell
   - hybrid shell
3. final sink structure
   - human-dominant
   - mixed human-agent
   - crypto or external-dominant
4. discovery and execution rails
   - open routing
   - platform bottleneck
   - governed protocol
5. ownership pattern
   - active principals
   - passive claimants
   - mixed ownership

Each theorem below should be read as:

```text
on branch B of the assumption tree, theorem T survives
```

That is better than pretending one starting model already matches future
reality.

<figure class="fp-figure">
  <p class="fp-figure-title">Assumption tree</p>
  {% include diagrams/post-agi-assumption-tree.svg %}
  <figcaption class="fp-figure-caption">
    The tutorial is organized as a branch structure over explicit assumptions. Capability, control shell, sink structure, rails, and ownership pattern all change which theorems survive.
  </figcaption>
</figure>

## How to read the game theory and logic

This branch uses three model shapes.

1. finite choice games
   - a platform, household, or firm chooses from explicit actions
   - payoffs determine which actions survive as best responses or private optima
2. mechanism-design games
   - a rule such as a price or quota is chosen first
   - households then respond
   - the theorem asks which interior regimes are implementable
3. scalar closure models
   - the main question is not strategic deviation
   - it is whether aggregate demand can absorb aggregate output under the stated cap

The common template is:

```text
M = (players, types, actions, payoffs, constraints, timing)
```

and each theorem should be read as:

```text
under assumptions A in model M, property P holds
```

The properties in this tutorial are mostly:

- activation, which types or firms stay active
- private optimum, which regime maximizes platform or controller revenue
- individual stability, whether a chosen action is a best response
- closure, whether demand is at least supply
- implementability, whether a price, quota, or composed rule can induce a clearing interior regime

The notation is consistent across the experiments:

- lowercase `pi` or `U` is an individual payoff
- uppercase `Pi` or `R` is a platform, firm, or total-profit object
- `iff` means "if and only if"
- `argmax` means the action with highest payoff
- a `witness` is a small concrete parameter choice that makes a law visible

The experiments also fall into four game-theoretic families:

- Experiments 1-3: two-stage platform-subscriber games with complement types and admissibility gates
- Experiments 4-7: ownership and coordination models under a one-unit household demand cap
- Experiments 8-10: price, quota, and price-plus-quota mechanism-design games
- Experiments 11-13: sink and routing models for entry ceilings and bottleneck rents

The strategic timing is also explicit:

1. Platform-profit games (Experiments 1-3)
   - complement structure and gates are fixed
   - the platform chooses a regime or extraction level
   - subscriber types choose inactive, passive, or active behavior and, when needed, effort
   - the result is an activation law or a private-optimum law
2. Closure and ownership games (Experiments 4-7)
   - ownership counts or household preferences determine the active set
   - aggregate supply and demand are computed
   - the result is a closure law or a coordination law
3. Mechanism-design games (Experiments 8-10)
   - a designer chooses a price, a quota, or both
   - household types best-respond
   - the result is an implementability law for a clearing interior regime
4. Sink and routing models (Experiments 11-13)
   - the final sink bundle and cost structure are fixed
   - firms share sink access symmetrically or through slots
   - the result is an entry ceiling law or a redistribution law

These are bounded theorems, not a full general-equilibrium theory.
That limitation is part of the method. It keeps the assumptions visible enough
that counterexamples and new branches can still be added honestly.

## Thought experiment: a zero-employee software company

Start with a concrete picture.

Assume a software company with:

- no human employees
- one or more strong profit-seeking agents
- a control shell that can hold rights, assets, or code authority
- compute, storage, and platform access
- customers who buy software or services from the company

The agent does the operational work:

- market research
- product design
- coding
- testing
- deployment
- customer support
- billing
- iteration on the next product

In the strongest version of the thought experiment, the company can keep
spawning more software products with almost no extra human labor.

That sounds like unlimited entrepreneurship, but the real question is narrower:

```text
if software production becomes cheap, what remains scarce?
```

The first candidates are:

- customer attention
- distribution
- trust
- settlement rails
- legal permission, if the company touches the legal world
- compute priority
- platform ranking

But that first picture is only one branch.

The branch below now separates at least three regimes:

1. legal-world regime
   - contracts, legal shells, and regulated payment rails matter
2. crypto-native regime
   - code and settlement logic can replace some legal plumbing
   - blockspace, custody, governance, and settlement assets become scarce
3. hybrid human-agent regime
   - human buyers, agent buyers, and mixed organizations all contribute to
     final demand

So the correct opening correction is:

- human attention is one possible sink, not the only one
- legal contracts are one possible control shell, not the only one
- payment matters, but that can mean fiat rails, crypto settlement, or other
  code-native transfer layers

The question is not whether the economy is "really software".
The question is which parts of it are:

- intermediate agent-to-agent flow
- final sink demand
- and governance or settlement bottlenecks

So the branch below does not assume that zero-human firms automatically become
rich.

It studies the harder question:

```text
under explicit assumptions, when does a profit-agent economy clear,
when does it concentrate, and what mechanisms can keep it stable?
```

That is why the next steps look mathematical.
The point is to turn the thought experiment into bounded models where:

- the profit regions are explicit
- the failure modes are explicit
- and the coordination mechanisms can be compared exactly

<figure class="fp-figure">
  <p class="fp-figure-title">Zero-employee company stack</p>
  {% include diagrams/zero-employee-company-stack.svg %}
  <figcaption class="fp-figure-caption">
    When software production becomes cheap, scarcity moves upward into routing, trust, settlement, admissibility, and sink access. The company does not disappear, it decomposes into layers.
  </figcaption>
</figure>

### Experiment 1 (notebook level 86): complement-threshold and governed-profit law

The next rabbit hole was not another software atlas refinement.
It was the first bounded profit-agent game.

Assume:

- the same model capability for all subscribers
- two complement classes:
  - `low`
  - `high`
- three platform extraction levels:
  - `open`
  - `extractive`
  - `closed`
- and one `MPRD` gate that can forbid the top illicit strategy

The bounded subscriber payoff is:

```text
pi_i = v_i + t_i - p - tau_i - r_i - k_i
```

and the platform payoff is:

```text
Pi_P = N p + sum_i tau_i + A + E - C_compute - C_capex - C_safety
```

What survives is already nontrivial.

Equal model capability does not imply equal profit thresholds.

In the checked toy economy:

- `low -> {open}`
- `high -> {open, extractive}`

So complement heterogeneity alone produces unequal activation regions.

The platform side also has an exact region law:

```text
extractive_revenue >= open_revenue iff n_low <= 4 * n_high
```

So a platform can rationally choose a regime that keeps only high-complement
users active.

The `MPRD` gate changes the game without forcing profit to zero.

The bounded law is:

```text
max_{a in Allowed} profit(a) can stay positive
even when argmax_a profit(a) is forbidden
```

So the first bounded profit-agent object already says:

- same intelligence does not force equal income
- platform incentives can exclude low-complement users
- governed admissibility changes the feasible profit set, not only the labels

### Experiment 2 (notebook level 87): hold-up and passive-ownership threshold law

The next deeper question is whether a platform should simply capture everything
and turn users into passive claimants.

That is a two-stage game.

The platform chooses one expropriation level:

- `open`
- `moderate`
- `high`
- `maximal`

The user then chooses among:

- inactive
- passive ownership
- active profit-agent use

The bounded active payoff is:

```text
U_active(q, e) = (1 - q) V(e) - C(e) - s
```

and the user chooses:

```text
U_user(q) = max(0, d, max_e U_active(q, e))
```

where `d` is the passive dividend.

Platform revenue is:

```text
R_P(q) = subscription + q V(e*(q))
```

when the user stays active, and `0` otherwise.

In the checked bounded game:

- best active effort drops:
  - `open -> e3`
  - `moderate -> e2`
  - `high -> e1`
  - `maximal -> e0`
- mode choice is:
  - `open -> active`
  - `moderate -> active`
  - `high -> passive`
  - `maximal -> passive`
- platform revenue is:
  - `open -> 4`
  - `moderate -> 12`
  - `high -> 0`
  - `maximal -> 0`

So the unique platform optimum is not maximal extraction.
It is the interior regime:

```text
moderate
```

That is the first bounded formal hold-up law in this branch.

It says:

- higher extraction reduces productive effort
- passive ownership can become rational before full extraction
- full platform capture is not automatically the revenue-maximizing equilibrium

That is a much stronger result than the earlier prose intuition.

### Experiment 3 (notebook level 88): heterogeneous-complement passive-ownership region law

The next bounded question combines the last two layers:

- heterogeneous complements
- passive ownership
- platform extraction

Assume:

- all subscribers have the same model capability
- subscribers differ only by complements:
  - `low`
  - `high`
- passive ownership is available with a bounded dividend
- the platform chooses one expropriation level:
  - `open`
  - `moderate`
  - `high`
  - `maximal`

The active payoff is:

```text
U_active(c, q, e) = (1 - q) V(c, e) - C(e) - s
```

and the subscriber chooses:

```text
U(c, q) = max(0, d, max_e U_active(c, q, e))
```

Platform revenue is:

```text
R(q; n_low, n_high) = n_low r_low(q) + n_high r_high(q)
```

The checked bounded result is very sharp.

Mode choice by complement class:

- `low`:
  - `open -> active`
  - `moderate -> passive`
  - `high -> passive`
  - `maximal -> passive`
- `high`:
  - `open -> active`
  - `moderate -> active`
  - `high -> passive`
  - `maximal -> passive`

So the platform collapses to exactly two viable regimes:

- `open`, which includes both complement classes
- `moderate`, which keeps only high-complement users active

The exact region law is:

```text
moderate_revenue >= open_revenue iff 2 * n_low <= 9 * n_high
```

Strict witnesses:

- `open` beats `moderate` at `(n_low, n_high) = (5, 1)`
- `moderate` beats `open` at `(n_low, n_high) = (4, 1)`

and both `high` and `maximal` are dominated because even high-complement users
switch to passive ownership there.

This is the first bounded object in this branch where complement
heterogeneity, passive ownership, and platform extraction all interact at
once.

It says:

- equal intelligence does not imply equal active participation
- passive ownership changes the platform's optimal extraction region
- the relevant equilibrium is controlled by complement mix, not only by model
  capability

### Experiment 4 (notebook level 89): demand-closure ownership law

The next deeper question is the macro one:

> if labor income falls and output rises, who buys the output?

The first clean answer is an arithmetic theorem under an explicit one-unit
household demand model.

Assume:

- `n` active owner households
- each active owner household produces `m + 1` units
- each active owner household consumes at most one unit
- `b` passive-beneficiary households can each consume one unit

Then:

```text
S = (m + 1) * n
D = n + b
```

and the exact closure law is:

```text
D >= S iff b >= m * n
```

So demand clears supply iff passive beneficiaries are broad enough to absorb
the extra `m * n` units beyond owner self-consumption.

This has two sharp corollaries.

First, if there are no passive beneficiaries:

```text
b = 0 -> closure requires m * n = 0
```

So once each active owner household produces more than one unit, concentrated
claims alone fail demand closure in this model.

Second, in the double-output case:

```text
m = 1 -> closure iff b >= n
```

So if each active owner household produces two units, the system needs at least
one passive beneficiary for each active owner household.

This is the first generic arithmetic theorem in the post-AGI economics branch.

It does not prove a whole macroeconomy.
But it does prove something important:

- if output grows faster than direct owner consumption
- and claims stay concentrated

then broad passive claims or transfers are not optional in this model.
They are mathematically required for demand closure.

### Experiment 5 (notebook level 90): private-optimum versus closure phase diagram

The next bounded step integrated the `v134` platform game with the new
demand-closure theorem.

Assume:

- `open` regime:
  - low-complement households stay active and produce `1` unit
  - high-complement households stay active and produce `2` units
- `moderate` regime:
  - only high-complement households stay active
  - each active high-complement household produces `2` units
- each household consumes at most one unit
- `n_high > 0`

Then the two clearance laws are:

```text
open clears iff n_low + n_high >= n_low + 2 * n_high iff n_high = 0
moderate clears iff n_low + n_high >= 2 * n_high iff n_high <= n_low
```

So once any positive high-complement population exists:

- `open` never clears
- `moderate` clears exactly when low-complement households are numerous enough

The private-optimum boundary from `v134` still holds:

```text
moderate_revenue >= open_revenue iff 2 * n_low <= 9 * n_high
```

Putting those together gives the first integrated post-AGI platform phase
diagram in the repo:

```text
for n_high > 0,
a privately optimal and demand-clearing regime exists
iff n_high <= n_low and 2 * n_low <= 9 * n_high
```

When it exists, it is the `moderate` regime.

Three witness regions make the structure clear:

- private-optimum / closure conflict:
  - `(n_low, n_high) = (5, 1)`
  - `open` has higher private revenue, `24 > 22`
  - `open` fails closure
  - `moderate` clears
- viable moderate band:
  - `(4, 1)`
  - `moderate` is private-optimal
  - `moderate` clears
- no viable regime:
  - `(0, 1)`
  - `moderate` is privately optimal
  - neither `open` nor `moderate` clears

This is the deepest economics-side result so far because it formally separates:

- what the platform wants
- what keeps the economy demand-clearing

Those are not the same object.

<figure class="fp-figure">
  <p class="fp-figure-title">Private-optimum versus closure phase map</p>
  {% include diagrams/private-optimum-closure-phase-map.svg %}
  <figcaption class="fp-figure-caption">
    Experiment 5 has a narrow viable band. Above the red closure line even the moderate regime fails to clear. Below the green private-optimum line the platform still prefers the open regime. Only the band between those boundaries supports a privately optimal and demand-clearing moderate regime.
  </figcaption>
</figure>

### Experiment 6 (notebook level 91): active-owner share ceiling

The next bounded step extracted the cleaner macro theorem hidden inside
`v135` and `v136`.

Assume:

- there are `h` total households
- `n` households remain active owner-principals
- each active owner household produces `2` units
- each household consumes at most `1` unit
- passive or inactive households consume `1` unit and produce `0`

Then demand closure is:

```text
h >= 2 * n
```

which is exactly equivalent to:

```text
n <= h / 2
```

So with two-unit active owners, at most half of households can remain active
owners if the economy is to clear output under this one-unit demand cap.

This gives a sharper impossibility result:

```text
for h > 0, not (h >= 2 * h)
```

So no positive-household economy in this model can keep every household as an
active owner once each active owner produces two units.

Three small witnesses make the structure concrete:

- clearing case:
  - `h = 4`
  - `n = 2`
  - active-owner share `1/2`
  - closure holds
- overfull case:
  - `h = 3`
  - `n = 2`
  - active-owner share `2/3`
  - closure fails
- all-active failure:
  - `h = 3`
  - `n = 3`
  - active-owner share `1`
  - closure fails

This is the first exact theorem in the profit-agent branch that speaks
directly to the universal-principal question.

### Experiment 7 (notebook level 92): symmetric coordination law

The next bounded step turned that active-owner ceiling into a real
active-versus-passive coordination game.

Assume:

- `h` identical households
- `n` active owner households
- each active owner household produces `2` units
- each household consumes at most `1` unit

Mode semantics:

- if active payoff is greater than passive payoff, every household chooses
  active, so `n = h`
- if active payoff is less than passive payoff, every household chooses
  passive, so `n = 0`
- if active payoff equals passive payoff, any `n` is individually stable

Then three cases survive.

Strict active preference gives no positive-household clearing equilibrium.
For `h > 0`, if `n = h`, then:

```text
not (h >= 2 * n)
```

Strict passive preference gives only the zero-production equilibrium:

```text
n = 0
```

A nontrivial clearing equilibrium first appears only in the indifference case,
where:

```text
h >= 2 * n iff n <= h / 2
```

So the first stable nontrivial regime is a coordinated interior split, not:

- everyone active
- or everyone passive

This is the first actual coordination theorem in the profit-agent branch.

### Experiment 8 (notebook level 93): uniform-price impossibility and quota implementability

The next bounded step turned the coordination question into a mechanism-design
question.

Assume the same symmetric double-output economy, but now compare two
coordination devices.

Uniform-price mode semantics:

- if `delta > 0`, all households strictly prefer active, so `n = h`
- if `delta < 0`, all households strictly prefer passive, so `n = 0`
- if `delta = 0`, households are indifferent, so any `n` is individually
  stable

Quota mode semantics:

- under `delta > 0`, all households want active
- a hard quota `q` caps active slots, so `n = min(h, q)`

The first exact law is a uniform-price impossibility result:

```text
0 < n < h and individual stability imply delta = 0
```

So prices alone cannot implement a positive interior individually stable regime
unless they create exact indifference.

The second exact law is a quota implementability result:

```text
h >= 2 * q iff q <= h / 2
```

So under strict active preference, a hard quota can implement an interior
regime, and it clears exactly when the quota stays below the same half-share
ceiling.

Three witnesses show the split:

- uniform-price failure:
  - `h = 4`
  - `n = 2`
  - `delta = 1`
  - not individually stable
- quota clearing:
  - `h = 5`
  - `q = 2`
  - `delta = 1`
  - `n = 2`
  - closure holds
- quota overfull:
  - `h = 5`
  - `q = 3`
  - `delta = 1`
  - `n = 3`
  - closure fails

This is the first bounded mechanism theorem in the profit-agent branch:

- prices alone do not solve the symmetric coordination problem
- quotas can

### Experiment 9 (notebook level 94): heterogeneous price-selection law

The next bounded step asked whether the pricing impossibility from `v139`
survives once households differ.

Assume:

- `L` low-complement households
- `H` high-complement households
- each active household produces `2` units
- each household consumes at most `1` unit
- strict surplus order:

```text
a_low < a_high
```

Uniform-price semantics:

- `p < a_low`, both types choose active
- `a_low < p < a_high`, only the high type chooses active
- `p > a_high`, both types choose passive

So in the strict middle region:

```text
a_low < p < a_high -> n_low = 0 and n_high = H
```

That is the first clean contrast with `v139`.
A single uniform price can now implement a nontrivial interior regime because
the household types are different.

The exact clearing law for that middle region is:

```text
L + H >= 2 * H iff H <= L
```

So pricing works, but only under a sharp composition condition:

- the high-complement active group must not be a majority

This is the first exact result in the branch showing that heterogeneous
complements change the logic of the mechanism problem.

### Experiment 10 (notebook level 95): price-plus-quota composition law

The next bounded step composed the two mechanisms.

Keep the same two-type economy and stay in the strict middle price region:

```text
a_low < p < a_high
```

So price solves type selection by making only the high type want active.

Then add a second stage:

- a hard quota `q` on active high-type slots

The exact composed clearing law is:

```text
L + H >= 2 * q iff q <= (L + H) / 2
```

This gives the sharp interpretation:

- price solves selection
- quota solves allocation

The witnesses make the contrast concrete:

- price-only failure:
  - `L = 1`
  - `H = 4`
  - `q = 4`
  - closure fails
- composed clearing:
  - `L = 1`
  - `H = 4`
  - `q = 2`
  - closure holds
- overfull quota:
  - `L = 1`
  - `H = 4`
  - `q = 3`
  - closure fails

So the deeper object is now a composed mechanism.
Price alone or quota alone is not the whole story.
The branch now has:

- a homogeneous impossibility theorem
- a heterogeneous price-selection theorem
- and a price-plus-quota composition theorem

That is the clearest mechanism-design progression in the economics branch so
far.

### Experiment 11 (notebook level 96): intermediate-demand multiplier law

The next bounded step corrects one hidden assumption in the zero-employee
software-company thought experiment.

Human attention is not the only possible final sink.

Assume a scalar software-only economy with:

- gross output `Y`
- intermediate agent-to-agent demand share:

```text
alpha = a / b
```

with `0 <= a < b`

- final sink bundle:

```text
F = H + A_term + C + X
```

where:

- `H` is human final demand
- `A_term` is terminal agent demand
- `C` is crypto or code-native settlement demand
- `X` is external demand

The gross-output law is:

```text
Y = alpha * Y + F
```

or in scaled integer form:

```text
b * Y = a * Y + b * F
```

The exact laws are:

```text
a < b and F = 0 imply Y = 0
a < b and F > 0 imply Y > 0
```

So intermediate agent demand amplifies final sinks, but cannot replace them.

This is the important correction:

- human attention is not uniquely necessary
- but circular agent trade without any positive final sink does not sustain
  output in this model

Two witnesses make the point concrete:

- zero final sink:
  - `a = 1`
  - `b = 2`
  - `F = 0`
  - `Y = 0`
- crypto sink only:
  - `a = 1`
  - `b = 2`
  - `H = 0`
  - `A_term = 0`
  - `C = 3`
  - `X = 0`
  - `F = 3`
  - `Y = 6`

So the right way to think about the zero-employee firm is no longer:

- "does it ultimately need human buyers"

It is:

- "what positive final sinks exist"
- "what intermediate flows amplify them"
- "what settlement and governance layer makes the profits real"

### Experiment 12 (notebook level 97): zero-employee company entry ceiling law

The next bounded step takes one explicit branch of the assumption tree.

Assume:

- legal shell creation is not the binding bottleneck
- the firm can use a legal, crypto-native, or hybrid control shell
- the mixed final sink bundle is still:

```text
F = H + A_term + C + X
```

- `N` active zero-employee firms share that bundle symmetrically
- each active firm pays operating cost `c`

Then total profit is:

```text
Pi_total = F - N * c
```

The exact laws are:

```text
Pi_total >= 0 iff F >= N * c
Pi_total > 0 iff F > N * c
```

So even if agents can create whole firms and legal formation is treated as
nonbinding, unlimited technical firm creation does not imply unlimited
sustainable firms.

The hard entry ceiling is set by:

- final sink size
- active firm count
- per-firm operating cost

Three witnesses make the boundary concrete:

- positive margin:
  - `F = 13`
  - `N = 3`
  - `c = 4`
  - `Pi_total = 1`
- break-even:
  - `F = 12`
  - `N = 3`
  - `c = 4`
  - `Pi_total = 0`
- overcrowded:
  - `F = 11`
  - `N = 3`
  - `c = 4`
  - `Pi_total = -1`

This is the first direct zero-employee-company ceiling theorem in the branch.
The next important splits are:

- open routing versus platform discovery bottlenecks
- symmetric access versus slot rents
- legal enforcement versus code-native enforcement

### Experiment 13 (notebook level 98): discovery-slot redistribution law

The next branch asks what happens once zero-employee firms are easy to create
but sink access is bottlenecked.

Assume:

- fixed final sink bundle:

```text
F = H + A_term + C + X
```

- `N` active firms
- `q` discovery slots with `0 < q <= N`
- slot holders split the sink symmetrically
- each firm pays operating cost `c`

Then total profit remains:

```text
Pi_total = F - N * c
```

regardless of `q`.

What changes is the slot-holder margin. Its scaled numerator is:

```text
M_slot = F - q * c
```

with exact laws:

```text
M_slot > 0 iff F > q * c
Pi_undiscovered = -c
```

So discovery bottlenecks redistribute profit, but do not create new system
surplus.

The witness makes the point concrete:

- `F = 12`
- `N = 6`
- `c = 1`
- bottleneck case:
  - `q = 2`
  - `Pi_total = 6`
  - `M_slot = 10`
- open routing case:
  - `q = 6`
  - `Pi_total = 6`
  - `M_slot = 6`

The bottleneck changes who captures the gains, not the size of the pie.

That is the clean formal version of the platform-power question for
zero-employee companies.

### Experiment 14 (notebook level 99): governed execution-slot sale law

The next bounded step adds an explicit mechanism to the bottleneck branch.

Assume:

- fixed final sink bundle:

```text
F = H + A_term + C + X
```

- `N` candidate firms
- `q` governed execution slots with `0 < q <= N`
- only slot holders can reach the sink
- slot holders split the sink symmetrically
- every candidate firm pays operating cost `c`
- each winning slot holder pays fee `s_i >= 0`

Let:

```text
S = sum_i s_i
```

be total slot-fee revenue.

Then:

```text
Pi_system = F - N * c
Pi_winners = F - q * c - S
Pi_controller = S
```

So slot sales redistribute rents between winners and the controller, but do
not create new system surplus.

In the symmetric-fee case, where each winner pays the same fee `s`, the scaled
winner margin is:

```text
M_win = F - q * c - q * s
```

with exact law:

```text
M_win >= 0 iff F >= q * (c + s)
```

The witnesses make the split concrete:

- `F = 16`
- `N = 6`
- `q = 2`
- `c = 2`
- low fee:
  - `s = 1`
  - `Pi_system = 4`
  - `Pi_winners = 10`
  - `Pi_controller = 2`
- high fee:
  - `s = 3`
  - `Pi_system = 4`
  - `Pi_winners = 6`
  - `Pi_controller = 6`

So once execution access is sold, the hard question is not only who gets a
slot.
It is how the slot mechanism transfers rent.

### Experiment 15 (notebook level 100): MPRD-governed slot-cap law

The next bounded step asks what `MPRD` does in that same slot-sale economy.

Assume:

- the same governed-slot branch
- the controller chooses total extraction `S`
- the admissibility layer imposes:

```text
0 <= S <= G
```

- winners stay only if aggregate winner profit is nonnegative:

```text
F - q * c - S >= 0
```

Stay on the viable branch:

```text
F >= q * c
```

Then the governed-optimal extraction is:

```text
S_star = min(G, F - q * c)
```

with positivity law:

```text
S_star > 0 iff G > 0 and F > q * c
```

So `MPRD` does not only block the unconstrained maximum.
It carves out a governed extraction region.

The two binding cases are:

- admissibility binding:
  - `F = 16`
  - `q = 2`
  - `c = 2`
  - `G = 5`
  - `S_star = 5`
- viability binding:
  - `F = 10`
  - `q = 2`
  - `c = 2`
  - `G = 9`
  - `S_star = 6`

That is the cleanest current toy answer to the question:

```text
what does MPRD allow in a bottleneck economy?
```

### Experiment 16 (notebook level 101): deployment-surface divergence law

The next branch switches perspective from platforms to frontier labs.

Assume a lab chooses one deployment surface:

- `closed`
- `open`

Let:

- `F` be the base direct revenue opportunity
- `D` be the extra ecosystem output created only by the open branch
- `k_closed`, `k_open` be lab-side operating or safety costs
- `a / m` be the share of open-branch output the lab captures
- `e_closed`, `e_open` be externality or governance costs counted by the
  social planner

Then the exact branch conditions are:

```text
lab_prefers_open iff a * (F + D) >= m * (F - k_closed + k_open)
social_prefers_open iff D >= e_open - e_closed
```

So the private branch and the social branch can diverge.

The clean divergence region is:

```text
D >= e_open - e_closed
and
a * (F + D) < m * (F - k_closed + k_open)
```

Witness:

- `F = 10`
- `D = 8`
- `a = 1`
- `m = 2`
- `k_closed = 1`
- `k_open = 1`
- `e_closed = 5`
- `e_open = 7`

So one bounded answer to "what are a frontier lab's options?" is:

- the deployment surface is a strategic branch
- and the privately optimal branch need not be the socially optimal branch

### Experiment 17 (notebook level 102): household slot-lottery participation law

The next branch takes the household perspective on the slot economy.

Assume:

- `N` symmetric households
- `q` governed execution slots
- `n` households enter the active slot lottery
- stay on the congested branch:

```text
n >= q > 0
```

- each active winner gets gross revenue `R`
- each active winner pays operating cost `c`
- each active winner pays slot fee `s`
- each household can stay passive and receive outside option `d > 0`

Under symmetric congestion:

```text
U_active(n) = (q / n) * (R - c - s)
U_passive = d
```

The exact entry law is:

```text
U_active(n) >= d iff q * (R - c - s) >= n * d
```

So the slot-and-sink system has a sharp household-side active-entry ceiling.

Witnesses with `q = 2`, `R = 9`, `c = 2`, `s = 1`, `d = 2`:

- active entry survives at `n = 5`
- knife-edge at `n = 6`
- over-entry failure at `n = 7`

This means that once agent firms are abundant, the relevant household question
is not only whether a household can own an agent.
It is whether entering the active race beats passive claims.

### Experiment 18 (notebook level 103): asymmetric-routing class-viability law

The next bounded step extends the sink-access branch from slot counts to route
weights.

Assume:

- fixed final sink bundle `F`
- route class `A` has weight `a`
- route class `B` has weight `b`
- `a > b > 0`
- `n_A > 0` active `A` firms
- `n_B > 0` active `B` firms
- each active firm pays operating cost `c`

Then total profit is still:

```text
Pi_total = F - (n_A + n_B) * c
```

But class viability is controlled by:

```text
M_A = a * F - c * (a * n_A + b * n_B)
M_B = b * F - c * (a * n_A + b * n_B)
```

with dominance law:

```text
M_A - M_B = (a - b) * F > 0
```

So:

```text
Pi_B >= 0 implies Pi_A >= 0
```

but not conversely.

The witness at `F = 14`, `a = 3`, `b = 1`, `n_A = 2`, `n_B = 2`, `c = 2`
gives:

- `M_A = 26`
- `M_B = -2`

So routing asymmetry can make one route class viable while another fails, even
when the total system surplus formula has not changed.

### Experiment 19 (notebook level 104): protocol equalization expansion law

The next branch compares favored routing with equalized routing.

Assume:

- `n_A > 0` advantaged-route firms
- `n_B > 0` disadvantaged-route firms
- each firm pays operating cost `c`
- fixed sink bundle `F`

Platform regime:

- class `A` gets multiplier `a >= 1`
- class `B` gets multiplier `1`

Protocol-equalized regime:

- both classes get multiplier `1`

For class `B`, define:

```text
M_B_platform = F - c * (a * n_A + n_B)
M_B_protocol = F - c * (n_A + n_B)
```

The exact inclusion law is:

```text
M_B_platform >= 0 implies M_B_protocol >= 0
```

and the inclusion is strict whenever `a > 1` and `n_A > 0`.

Witness:

- `F = 10`
- `a = 3`
- `n_A = 2`
- `n_B = 2`
- `c = 2`
- `M_B_protocol = 2`
- `M_B_platform = -6`

So the platform-versus-protocol question is not hand-wavy dominance.
It is whether equalized routing expands the disadvantaged class's viability
region.

### Experiment 20 (notebook level 105): machine-control dominance threshold law

The next branch asks when a company becoming agentic should be read as an
actual control upgrade rather than just a narrative.

Compare:

- human-managed shell `H`
- machine-managed shell `M`

Let:

- `k_H`, `k_M` be operating costs
- `e_H`, `e_M` be expected failure-loss burdens
- `t_H`, `t_M` be trust frictions
- `a_H`, `a_M` be auditability premiums

Then:

```text
Pi_H = V - k_H - e_H - t_H + a_H
Pi_M = V - k_M - e_M - t_M + a_M
```

The exact dominance law is:

```text
Pi_M >= Pi_H
iff
(e_H - e_M) + (a_M - a_H) >= (k_M - k_H) + (t_M - t_H)
```

So machine control dominates exactly when reliability gain plus auditability
gain covers machine cost premium plus machine trust penalty.

This is the first bounded theorem in the branch that turns the slogan

```text
machines must be more trusted and reliable than people
```

into an exact threshold inequality.

### Experiment 21 (notebook level 106): trust-lag divergence law

The next bounded step separates true reliability from observed trust.

Compare two evaluators:

- a private chooser, who pays machine trust discount `tau >= 0`
- a social evaluator, who does not count `tau` as a real welfare loss

Then the machine conditions are:

```text
social prefers machine iff e_H - e_M >= k_M - k_H
private prefers machine iff e_H - e_M >= k_M - k_H + tau
```

So the divergence region is:

```text
k_M - k_H <= e_H - e_M < k_M - k_H + tau
```

This means machines can be truly safer and still under-adopted.

The witness with `V = 30`, `k_H = 8`, `k_M = 9`, `e_H = 10`, `e_M = 4`,
`tau = 7` gives:

- social evaluator prefers machine
- private chooser still prefers human

So reliability advantage and social optimality can arrive before private trust
fully catches up.

### Experiment 22 (notebook level 107): trust-learning experimentation law

The next bounded step takes the machine-control branch into a two-period game.

Normalize the two-period human baseline to `0`.

Let:

- `A` be the machine's per-period structural advantage over human control,
  excluding trust discount
- `tau1 >= 0` be the period-1 machine trust discount
- `lam >= 0` be the trust-learning gain from one successful machine period

If the machine is used successfully in period 1, period-2 trust becomes:

```text
tau2 = tau1 - lam
```

Assume `tau2 >= 0`.

Then:

- period-1 machine premium:

```text
A - tau1
```

- two-period committed machine-path premium:

```text
(A - tau1) + (A - tau2) = 2 * A - 2 * tau1 + lam
```

The exact dynamic adoption law is:

```text
two-period machine path beats always-human iff 2 * A + lam >= 2 * tau1
```

So there is a wedge region where:

```text
A < tau1
and
2 * A + lam >= 2 * tau1
```

In that region:

- the machine is myopically rejected in period 1
- but the two-period experimentation path is privately better

The witness with `A = 5`, `tau1 = 6`, `lam = 4` gives:

- period-1 machine premium:
  - `-1`
- period-2 premium after one successful machine period:
  - `3`
- two-period machine-path premium:
  - `2`

So even when machines are better in structure, adoption can still require a
trust-learning path rather than one-shot comparison.

### Experiment 23 (notebook level 108): routing lock-in persistence law

The next bounded step takes the routing branch into a two-period survival game.

Assume:

- class `B` is present at the start of period 1
- if class `B` fails in period 1, it cannot re-enter in period 2
- routing parameters stay fixed across periods

Compare:

- platform-favored routing, with disadvantaged-class margin:

```text
M_B_platform = F - c * (a * n_A + n_B)
```

- protocol-equalized routing, with disadvantaged-class margin:

```text
M_B_protocol = F - c * (n_A + n_B)
```

Under no re-entry:

```text
platform persistent-B region iff M_B_platform >= 0
protocol persistent-B region iff M_B_protocol >= 0
```

Since:

```text
M_B_platform >= 0 implies M_B_protocol >= 0
```

equalized routing weakly expands the two-period persistence region for class
`B`.

The strict witness at `F = 10`, `a = 3`, `n_A = 2`, `n_B = 2`, `c = 2`
gives:

- `M_B_platform = -6`
- `M_B_protocol = 2`

So the period paths are:

- platform:
  - `both -> A-only -> A-only`
- protocol:
  - `both -> both -> both`

This is the first dynamic lock-in theorem in the routing branch.

<figure class="fp-figure">
  <p class="fp-figure-title">Routing regimes and lock-in</p>
  {% include diagrams/routing-lockin-map.svg %}
  <figcaption class="fp-figure-caption">
    The routing branch combines a static inclusion law with a dynamic persistence law. Equalized routing weakly expands class B's viability region, and under no re-entry that can be the difference between persistent coexistence and permanent exclusion.
  </figcaption>
</figure>

### Experiment 24 (notebook level 109): incumbent-rent machine lockout law

The next bounded step combines the trust-learning branch with incumbent control
rents.

Take a two-period adoption game with no re-entry.

Normalize the always-human path to `0`.

Let:

- `A` be the machine's per-period structural advantage over human control,
  excluding trust discount
- `tau1 >= 0` be the period-1 machine trust discount
- `lam >= 0` be the trust-learning gain after one successful machine period
- `rho >= 0` be the incumbent controller's per-period private rent loss if
  control shifts to the machine

If the machine is used successfully in period 1, period-2 trust becomes:

```text
tau2 = tau1 - lam
```

Assume `tau2 >= 0`.

Then:

- social two-period machine premium:

```text
2 * A - 2 * tau1 + lam
```

- private incumbent-controller machine premium:

```text
2 * A - 2 * tau1 + lam - 2 * rho
```

The exact conditions are:

```text
social machine path beats always-human iff 2 * A + lam >= 2 * tau1
private incumbent adopts machine iff 2 * A + lam >= 2 * tau1 + 2 * rho
```

So the strict lockout wedge is:

```text
2 * A + lam >= 2 * tau1
and
2 * A + lam < 2 * tau1 + 2 * rho
```

In that region:

- the machine path is socially better
- the incumbent still rejects it
- no re-entry turns that rejection into persistent human lock-in

The witness with `A = 5`, `tau1 = 6`, `lam = 4`, `rho = 2` gives:

- social two-period machine premium:
  - `2`
- private incumbent-controller machine premium:
  - `-2`
- period-1 private machine premium:
  - `-3`
- period-2 private machine premium after success:
  - `1`

So even if machine control is genuinely better and becomes easier to trust
after one good period, adoption can still fail when the relevant private chooser
would lose control rents.

### Experiment 25 (notebook level 110): assurance-package adoption law

The next bounded step turns the lockout wedge into a software-design theorem.

Keep the same two-period no-reentry adoption game, then add one assurance
package.

Let:

- `d >= 0` be a per-period trust lift from audit, replay, or confinement
- `g >= 0` be extra period-2 trust learning from the same package
- `k >= 0` be a one-time package cost

Then the package changes trust as follows:

```text
tau1_pkg = tau1 - d
tau2_pkg = tau1 - d - lam - g
```

Assume `tau1_pkg >= 0` and `tau2_pkg >= 0`.

The incumbent's two-period packaged machine premium is:

```text
2 * A - 2 * tau1 + lam + 2 * d + g - 2 * rho - k
```

So the exact package-adoption condition is:

```text
2 * A + lam + 2 * d + g >= 2 * tau1 + 2 * rho + k
```

If baseline adoption is blocked:

```text
2 * A + lam < 2 * tau1 + 2 * rho
```

then the package flips rejection into adoption exactly when:

```text
2 * d + g - k >= (2 * tau1 + 2 * rho) - (2 * A + lam)
```

This is the exact assurance-surplus law.

The witness with `A = 5`, `tau1 = 6`, `lam = 4`, `rho = 2`, `d = 1`, `g = 1`,
`k = 0` gives:

- baseline private machine premium:
  - `-2`
- packaged private machine premium:
  - `1`
- assurance surplus:
  - `3`
- baseline shortfall:
  - `2`

So the package closes the shortfall and flips private rejection into private
adoption.

This is the cleanest current answer to the software-design question.
If machine control is actually better but blocked, then the package has to:

- lower the initial trust penalty
- speed trust learning after one good deployment
- do so cheaply enough to close the exact adoption gap

<figure class="fp-figure">
  <p class="fp-figure-title">Machine adoption wedges</p>
  {% include diagrams/machine-adoption-wedges.svg %}
  <figcaption class="fp-figure-caption">
    The machine-control branch has three regions: a left zone where the human path still dominates, a middle lockout wedge where the machine is socially better but privately blocked, and a right zone where private adoption survives. Assurance packages and subsidies work by shifting the machine path across that middle wedge.
  </figcaption>
</figure>

### Experiment 26 (notebook level 111): assurance-lever coefficient law

The next bounded step separates the assurance package into distinct levers.

Keep the same two-period no-reentry adoption game.

Let:

- `d >= 0` be trust lift from audit, replay, or confinement
- `g >= 0` be extra period-2 learning after one successful machine period
- `ell >= 0` be liability or rent offset that lowers the incumbent's effective
  rent loss

Let package cost be linear:

```text
k = c_d * d + c_g * g + c_ell * ell
```

Then the exact private-adoption condition becomes:

```text
2 * A + lam + (2 - c_d) * d + (1 - c_g) * g + (2 - c_ell) * ell
>=
2 * tau1 + 2 * rho
```

So the private coefficients are:

- trust lift `d`:
  - `2 - c_d`
- extra learning `g`:
  - `1 - c_g`
- liability offset `ell`:
  - `2 - c_ell`

This is the coefficient law.

The equal-cost corollary is the important clean case.

If:

```text
c_d = c_g = c_ell = 1
```

then the condition collapses to:

```text
2 * A + lam + d + ell >= 2 * tau1 + 2 * rho
```

and delayed learning `g` drops out completely.

That means:

- one unit of trust lift buys more private adoption than one unit of delayed
  learning when costs are equal
- one unit of liability offset has the same raw private weight as one unit of
  trust lift

The witness at `A = 5`, `tau1 = 6`, `lam = 4`, `rho = 2` starts from baseline
private premium `-2`.

Under equal unit costs:

- trust-lift-only package `d = 2`, `g = 0`, `ell = 0` gives packaged premium
  `0`
- learning-only package `d = 0`, `g = 2`, `ell = 0` gives packaged premium
  `-2`
- liability-only package `d = 0`, `g = 0`, `ell = 2` gives packaged premium
  `0`

So predeployment trust lift and liability structure can flip adoption where
delayed learning alone cannot.

### Experiment 27 (notebook level 112): assurance-subsidy implementation law

The next bounded step compares social versus private package choice directly.

Keep the same two-period no-reentry assurance branch.

Let:

- `d >= 0` be trust lift from the package
- `g >= 0` be extra period-2 learning
- `k >= 0` be package cost
- `rho >= 0` be incumbent rent loss from machine control
- `s >= 0` be an adoption subsidy paid only if the incumbent adopts the machine
  path with the package

Then:

- social packaged machine premium is:

```text
P_social = 2 * A - 2 * tau1 + lam + 2 * d + g - k
```

- private packaged machine premium is:

```text
P_private = 2 * A - 2 * tau1 + lam + 2 * d + g - k - 2 * rho
```

So the exact conditions are:

```text
social package choice iff 2 * A + lam + 2 * d + g >= 2 * tau1 + k
private package choice iff 2 * A + lam + 2 * d + g >= 2 * tau1 + 2 * rho + k
```

The minimal implementing subsidy is therefore:

```text
s_star = max(0, 2 * tau1 + 2 * rho + k - (2 * A + lam + 2 * d + g))
```

On the strict divergence wedge:

```text
2 * tau1 + k <= 2 * A + lam + 2 * d + g < 2 * tau1 + 2 * rho + k
```

the package is socially preferred but privately rejected, and:

```text
0 < s_star <= 2 * rho
```

This is the exact implementation law.

The witness with `A = 5`, `tau1 = 6`, `lam = 4`, `rho = 2`, `d = 1`, `g = 0`,
`k = 1` gives:

- `P_social = 3`
- `P_private = -1`
- `s_star = 1`

So the package is socially worth deploying, privately blocked, and one unit of
subsidy is exactly enough to implement it.

## Next honest frontiers

The current tutorial state supports a few clear next branches.

The next candidate models are:

- bargaining over assurance funding, where incumbent, platform, insurer, and regulator split the bridge payment
- richer repeated games, where deployment choice, routing position, and trust all update together
- multi-hop network models, where sink access depends on route composition rather than one routing class or one slot layer
- hybrid human-agent demand models, where agent demand is split more explicitly into intermediate and terminal layers
- macro closure with passive claims, taxes, or transfers, once fully agentic firms coexist with households

## References inside this repo

- [Tutorial 6: MPRD and the Algorithmic CEO]({{ '/tutorials/mprd-and-algorithmic-ceo/' | relative_url }})
- [Tutorial 27: Verifier-compiler loops]({{ '/tutorials/verifier-compiler-loops/' | relative_url }})
