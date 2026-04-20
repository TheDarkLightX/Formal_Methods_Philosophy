---
title: "Bounded game tables in Tau Language"
layout: docs
kicker: Tutorial 46
description: "A Tau Language enhancement experiment: feature-gated game-table syntax, bounded strategic-profile classification, and profitable-deviation pruning."
---

This tutorial is about a Tau Language enhancement experiment: bounded game
tables.

The proposed feature is not "Tau solves all of game theory." The proposed
feature is smaller and more useful: Tau gets a table-shaped way to classify a
finite strategic surface, and the table lowers to ordinary Tau guarded-choice
terms.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope</p>
  <p>This is a community research experiment, not an official IDNI or Tau Language game-theory feature. The main enhancement lives as a feature-gated Tau patch in TauLang-Experiments. The ordinary-Tau file in this repo is a fast fallback layer, not the feature itself.</p>
</div>

## The Tau enhancement

The enhancement is a table expression:

```tau
post_agi_tokenomics_table(
  contribute,extract,exit,reward,tax,quarantine,
  safe_nash,unsafe_extract,nash_but_not_desired,not_nash,invalid_profile
) : tau :=
  table {
    when profile_contribute_reward(...) => safe_nash;
    when profile_extract_reward(...) => unsafe_extract;
    when profile_contribute_tax(...) => nash_but_not_desired;
    else => invalid_profile
  }.
```

This is the Tau-language object the tutorial is about.

The table is not magic. It is compiled to a raw guarded-choice expression:

$$
\operatorname{table}(G_1\mapsto A_1,\ldots,G_n\mapsto A_n,D)
\equiv
(G_1\wedge A_1)
\vee
(G_1'\wedge G_2\wedge A_2)
\vee
\cdots
\vee
(G_1'\wedge\cdots\wedge G_n'\wedge D).
$$

<strong>Standard reading.</strong>
The table expression with ordered guards $G_1,\ldots,G_n$, row values
$A_1,\ldots,A_n$, and default value $D$ is equivalent to the nested
guarded-choice expression that selects the first matching row and otherwise
selects $D$.

<strong>Plain English.</strong>
Earlier rows win. If no row guard holds, the default value is used.

<strong>Trap.</strong>
This is ordered priority-table semantics, not an unordered set of cases. If two
guards overlap, the earlier row controls the overlapping region.

The patched Tau demo checks:

```text
solve --tau (post_agi_tokenomics_table(...) != post_agi_tokenomics_raw(...))
```

The result is:

```text
no solution
```

That means Tau cannot find an assignment where the table form and the raw
guarded-choice form differ.

## How to run it

There are two runnable layers, and they should not be confused.

The main Tau-native layer lives in:

<a href="https://github.com/TheDarkLightX/TauLang-Experiments">TauLang-Experiments</a>

The public reproduction path is:

```bash
git clone https://github.com/TheDarkLightX/TauLang-Experiments.git
cd TauLang-Experiments
./scripts/run_game_table_demo.sh --accept-tau-license
```

That command downloads official Tau Language from the IDNI repository, applies
the community research patches locally, regenerates Tau's parser, builds Tau,
enables `TAU_ENABLE_SAFE_TABLES=1`, and runs the game-table equivalence check.

Inside an existing checkout, run:

```bash
./scripts/run_game_table_demo.sh --accept-tau-license
```

The fast fallback layer in this site uses ordinary Tau with no patch:

```text
examples/tau/post_agi_tokenomics_game_gate_v1.tau
```

Generate the checked trace with:

```bash
python3 scripts/generate_game_table_tau_artifacts.py
```

The generated artifact is:

```text
assets/data/game_table_tau_traces.json
```

The current trace reports:

```text
profiles checked:                 9
profiles after pruning:           3
safe profile:                     contribute/reward
Tau output matches Python model:  true
finite checker proof:             builds
```

The fallback exists for speed and pedagogy. It is not the feature. The feature
is the Tau-native table syntax in the patch repo.

## What the table classifies

The demo classifies a bounded listed game. A bounded listed game contains:

- a finite list of players,
- a finite list of candidate profiles,
- for each player and profile, a finite list of unilateral deviations,
- an admissibility predicate,
- a payoff function.

The best-response predicate is:

$$
\operatorname{BestResponse}_i(p)
:\Longleftrightarrow
\forall q\in \operatorname{Dev}_i(p).\,
\operatorname{Allowed}(q)
\Longrightarrow
u_i(q)\le u_i(p).
$$

<strong>Standard reading.</strong>
The best-response predicate for player $i$ and profile $p$ holds exactly when
every listed unilateral deviation $q$ from $p$ has this property: if $q$ is
allowed, then player $i$'s payoff at $q$ is less than or equal to player
$i$'s payoff at $p$.

<strong>Plain English.</strong>
Player $i$ has no listed allowed unilateral move from $p$ that improves player
$i$'s payoff.

<strong>Trap.</strong>
The word "listed" is part of the theorem. If a deviation is missing from the
list, the checker does not infer it.

The Nash predicate is:

$$
\operatorname{Nash}(p)
:\Longleftrightarrow
\operatorname{Allowed}(p)
\wedge
\forall i\in \operatorname{Players}.\,
\operatorname{BestResponse}_i(p).
$$

<strong>Standard reading.</strong>
The Nash predicate for profile $p$ holds exactly when $p$ is admissible and,
for every listed player $i$, the best-response predicate for player $i$ and
profile $p$ holds.

<strong>Plain English.</strong>
The profile is allowed, and no listed player has a listed allowed profitable
deviation.

The safe target predicate is:

$$
\operatorname{SafeNash}(p)
:\Longleftrightarrow
\operatorname{Nash}(p)
\wedge
\operatorname{Safe}(p)
\wedge
\operatorname{Desired}(p).
$$

<strong>Standard reading.</strong>
The safe-Nash predicate for profile $p$ holds exactly when $p$ is Nash, $p$
satisfies the safety predicate, and $p$ satisfies the desired-outcome
predicate.

<strong>Plain English.</strong>
The profile is strategically stable inside the bounded model, passes the
safety gate, and is one of the intended outcomes.

## The Tau game gate

The table syntax classifies the symbolic profile surface. The ordinary-Tau
fallback checks the same relationships as Boolean flags.

For a profile $p$, the gate computes:

$$
\operatorname{GateNash}(p)
:=
\operatorname{WellFormed}(p)
\wedge
\operatorname{Allowed}(p)
\wedge
\operatorname{BestResponse}(p).
$$

<strong>Standard reading.</strong>
The Tau gate for Nash status at profile $p$ is defined as the conjunction of
three predicates: $p$ is well formed, $p$ is allowed, and $p$ is a best
response in the finite listed game.

<strong>Plain English.</strong>
Tau accepts the Nash flag only when the profile is well formed, allowed, and a
best response in the finite listed game.

The safe profile flag is:

$$
\operatorname{GateSafeNash}(p)
:=
\operatorname{GateNash}(p)
\wedge
\operatorname{Desired}(p).
$$

<strong>Standard reading.</strong>
The Tau gate for safe-Nash status at profile $p$ is defined as the conjunction
of the Tau Nash gate at $p$ and the desired-outcome predicate at $p$.

<strong>Plain English.</strong>
The profile is accepted as the target outcome only if it is stable and desired.

The profitable-deviation consistency check is:

$$
\operatorname{Consistent}(p)
:=
\neg\operatorname{ProfDev}(p)
\vee
\neg\operatorname{BestResponse}(p).
$$

<strong>Standard reading.</strong>
The consistency predicate for profile $p$ is defined as the disjunction of two
claims: there is no profitable-deviation certificate for $p$, or $p$ is not a
best response.

<strong>Plain English.</strong>
If there is certified profitable-deviation evidence, the same profile cannot
also be accepted as a best response.

<strong>Trap.</strong>
Tau is checking the symbolic classification layer. Payoff enumeration and
coverage of the bounded game are separate obligations.

The classification code is:

$$
\operatorname{Class}(p)=
\begin{cases}
1,& \operatorname{GateSafeNash}(p),\\
2,& \operatorname{UnsafeExtract}(p),\\
3,& \operatorname{GateNash}(p)\wedge\neg\operatorname{Desired}(p),\\
4,& \operatorname{Allowed}(p)\wedge\neg\operatorname{GateNash}(p),\\
0,& \text{otherwise.}
\end{cases}
$$

<strong>Standard reading.</strong>
The classification function sends profile $p$ to code $1$ in the safe-Nash
case, code $2$ in the unsafe-extract case, code $3$ in the Nash-but-not-desired
case, code $4$ in the allowed-but-not-Nash case, and code $0$ in all remaining
cases.

<strong>Plain English.</strong>
The demo turns each bounded profile into one audit label.

## The pruning theorem

The optimization law starts with profitable-deviation evidence:

$$
\operatorname{ProfDev}(p)
:\Longleftrightarrow
\exists i\in\operatorname{Players}.\,
\exists q\in\operatorname{Dev}_i(p).\,
\operatorname{Allowed}(q)
\wedge
u_i(p)<u_i(q).
$$

<strong>Standard reading.</strong>
The profitable-deviation predicate for profile $p$ holds exactly when there is
a listed player $i$ and a listed unilateral deviation $q$ from $p$ such that
$q$ is allowed and player $i$'s payoff at $q$ is strictly greater than player
$i$'s payoff at $p$.

<strong>Plain English.</strong>
Some listed player has an allowed move that pays more.

The first pruning theorem is:

$$
\operatorname{ProfDev}(p)\Longrightarrow \neg\operatorname{Nash}(p).
$$

<strong>Standard reading.</strong>
The pruning theorem says that profitable-deviation evidence for profile $p$
entails that $p$ is not Nash.

<strong>Plain English.</strong>
A profile with certified profitable-deviation evidence cannot be Nash.

The search-preservation theorem is:

$$
\operatorname{ExistsSafeNash}(\operatorname{Prune}_{\operatorname{ProfDev}}(P))
\Longleftrightarrow
\operatorname{ExistsSafeNash}(P).
$$

<strong>Standard reading.</strong>
The search-preservation theorem says that the pruned candidate-profile set
contains a safe Nash profile exactly when the original candidate-profile set
contains a safe Nash profile, under the condition that pruning removes only
profiles with profitable-deviation evidence.

<strong>Plain English.</strong>
Removing profiles that cannot be Nash does not remove any safe Nash solution.

<strong>Trap.</strong>
This is not permission to prune by intuition. Each removed profile needs the
profitable-deviation certificate.

## Verification layer

This tutorial is Tau-first, but the experiment still needs a proof receipt.
The proof layer checks the finite search theorem:

$$
\operatorname{existsSafeNashCheck}(g,\operatorname{safe},\operatorname{desired},P)
=\operatorname{true}
\Longleftrightarrow
\exists p\in P.\,
\operatorname{SafeNash}(g,\operatorname{safe},\operatorname{desired},p).
$$

<strong>Standard reading.</strong>
The finite-search theorem says that the Boolean checker returns true exactly
when there exists a profile $p$ in the listed candidate-profile set $P$ such
that $p$ satisfies the safe-Nash predicate for game $g$ together with the
declared safety and desired-outcome predicates.

<strong>Plain English.</strong>
The finite checker finds exactly the safe Nash profiles that are present in
the finite candidate list.

<strong>Boundary.</strong>
This proof is not the tutorial's main feature. It is the evidence layer that
keeps the Tau enhancement honest.

## The post-AGI tokenomics demo

The demo uses one agent action and one protocol action.

Agent actions:

```text
contribute, extract, exit
```

Protocol actions:

```text
reward, tax, quarantine
```

The target outcome is:

```text
contribute/reward
```

The model checks all nine profiles. Six have profitable-deviation evidence and
can be pruned. The remaining three are the contribute profiles:

```text
contribute/reward
contribute/tax
contribute/quarantine
```

Only `contribute/reward` is both Nash and desired.

## What this gives Tau

This is useful because many protocol questions can be reduced to small bounded
games:

- Can an agent profit by extracting instead of contributing?
- Does quarantine remove the profitable deviation?
- Which profiles are stable and still safe?
- Which candidate mechanisms can be pruned before solving?

The feature does not make Tau a general game-theory engine. It gives Tau a
proof-backed finite strategic-profile checker, a local Boolean gate that runs
in ordinary Tau, and a pruning law that reduces candidate profiles when
profitable-deviation evidence is available.
