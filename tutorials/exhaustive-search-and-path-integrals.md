---
title: "Exhaustive search and path integrals: why 'all paths' is not proof search"
layout: docs
kicker: Tutorial 15
description: Compare proof by exhaustive search with Feynman's sum-over-histories, and separate finite checking from interference over amplitudes.
---

This tutorial starts from a tempting analogy:

- exhaustive search checks every candidate,
- the path-integral picture says light contributes along every path,
- both seem to range over "all possibilities."

The analogy is useful up to a point. It is also easy to overread.

This page makes three scoped claims:

1. Proof by exhaustive search and path integrals do share a surface pattern: both aggregate over many alternatives.
2. They use different mathematical objects and different combination rules.
3. Because of that difference, light interference is not itself a proof, and it is not ordinary search.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene (scope first)</p>
  <ul>
    <li><strong>Assumption A (physics model):</strong> This page uses the path-integral presentation of quantum mechanics as a model of slit experiments. For many optical setups, classical wave optics gives the same observable interference pattern.</li>
    <li><strong>Assumption B (what "proof" means):</strong> A proof is a finite, checkable object licensed by explicit rules, or a finite exhaustive search together with a valid checker.</li>
    <li><strong>Assumption C (what "all paths" means):</strong> "Light takes every path" is treated here as shorthand for "the formalism sums contributions from all allowed histories." It is not used as a literal claim that a single classical trajectory is physically traversed in the ordinary sense.</li>
    <li><strong>Assumption D (program analogy):</strong> If light is compared to a program, the comparison is about formal description, not about claiming that physics is secretly performing textbook proof search.</li>
  </ul>
</div>

## Part I: what exhaustive search actually proves

Start with the clean mathematical case.

Let $C$ be a finite set of candidates, and let

$$
V : C \to \{0,1\}
$$

be a checker.

If the goal is existential, the search asks whether

$$
\exists c \in C.\; V(c) = 1
$$

and a witness $c$ with $V(c) = 1$ can certify success.

If the goal is universal, the search asks whether

$$
\forall c \in C.\; P(c)
$$

and exhaustive checking can certify the claim when every case in the finite domain has been covered.

This is why truth tables count as proofs. The domain is finite, every row is checked, and the checking rule is explicit.

Two features matter:

1. The alternatives are discrete candidates.
2. The combining rule is logical or arithmetical, not phase-sensitive.

For example, one can count satisfying cases by summing indicators:

$$
N_{\text{good}} = \sum_{c \in C} \mathbf{1}[V(c)=1]
$$

There is no destructive cancellation here. A valid candidate does not stop being valid because another candidate was added.

That monotonicity is a major clue.

## Part II: what the path-integral picture computes

Now change the algebra.

In Feynman's sum-over-histories picture, the transition amplitude from an initial condition $a$ to a final condition $b$ is written schematically as

$$
K(b,a) = \int_{\gamma : a \to b} e^{iS[\gamma]/\hbar}\,\mathcal{D}\gamma
$$

where each allowed history $\gamma$ contributes a complex phase determined by the action $S[\gamma]$.

The observable probability is not the integral itself, but the squared magnitude:

$$
P(b \mid a) = |K(b,a)|^2
$$

For a slit experiment, a coarse-grained version often looks like

$$
\Psi(x) = \sum_{j \in S} A_j(x),
\qquad
P(x \mid S) = |\Psi(x)|^2
$$

where $S$ is the set of open slits and $A_j(x)$ is the amplitude contribution from slit $j$ to screen point $x$.

For two slits,

$$
P_{12}(x) = |A_1(x) + A_2(x)|^2
$$

which expands to

$$
|A_1|^2 + |A_2|^2 + 2\operatorname{Re}(A_1^*A_2).
$$

That last term is the interference term.

Unlike exhaustive search, adding an extra alternative can reduce the final value at a point. If $A_1(x) = 1$ and $A_2(x) = -1$, then

$$
|A_1 + A_2|^2 = 0.
$$

Opening the second path can make a bright point dark. That cannot happen in ordinary proof search over valid witnesses.

## Part III: the same outer shape, different inner algebra

The easiest way to keep the analogy honest is to line up the pieces.

| Question | Exhaustive search | Path integral / interference |
|---|---|---|
| Alternatives | finite candidates or cases | histories or amplitudes over alternatives |
| Local contribution | boolean, integer, or cost value | complex amplitude |
| Combination rule | logical aggregation, counting, min/max, or bounded recursion | complex addition followed by squared magnitude |
| Failure mode | a candidate fails the checker | amplitudes cancel by phase |
| Output | proof, witness, certificate, or counterexample | probability distribution over outcomes |

The outer shape, "range over alternatives and combine the results," is real.

The inner mechanism is different enough that the word "proof" stops fitting.

Proof search asks: which cases satisfy the rule?

Interference asks: how do complex contributions combine?

Those are different questions.

## Part IV: the three-slit thought experiment

A useful stress test is to keep adding openings.

With three slits in the coarse amplitude model,

$$
\Psi(x) = A_1(x) + A_2(x) + A_3(x),
\qquad
P(x) = |\Psi(x)|^2.
$$

With five slits, more terms appear. With many evenly spaced slits, the pattern sharpens into the familiar diffraction-grating picture. In a continuous-aperture limit, the pattern is controlled by the Fourier transform of the aperture.

The key point is unchanged:

- the formalism still sums amplitudes,
- the output is still a probability distribution,
- no slit is being "certified as the correct path" in the proof-theoretic sense.

This is another good place to compare with exhaustive search.

If a checker has already found a valid witness, adding extra candidates cannot make the witness invalid. In contrast, adding another open path in an interference experiment can create new cancellation and change the observed intensity drastically.

That non-monotonicity is strong evidence that the mechanism is not ordinary proof by cases.

## Part V: if light were described as a program

The cleanest program-like description is:

1. initialize a state $|\psi_0\rangle$,
2. evolve it by a linear operator $U_t$,
3. compute amplitudes for outcomes,
4. sample an observed event according to the Born rule.

In formulas:

$$
|\psi_t\rangle = U_t |\psi_0\rangle,
\qquad
p(x) = |\langle x \mid \psi_t \rangle|^2.
$$

For a slit experiment without which-path measurement:

$$
p(x \mid S) = \left|\sum_{j \in S} A_j(x)\right|^2.
$$

If a which-path measurement is performed, the interference term is removed and the model changes to

$$
p(x \mid S,\text{which-path}) = \sum_{j \in S} |A_j(x)|^2.
$$

That is much closer to a formal specification than to a proof term.

Under an ordinary Curry-Howard reading, proofs are discrete objects whose steps are licensed by rules. They do not carry complex phases and do not cancel each other out. So the direct slogan "light is doing programs-as-proofs" is too strong.

A better statement is narrower:

- a formal system can describe the dynamics of light,
- a proof assistant can prove theorems about that description,
- the physical interference pattern is evidence predicted by the model, not itself the proof object.

## Part VI: state spaces, path spaces, and thought spaces

The analogy becomes more useful when the question changes from "is light doing proof search?" to "what does it mean to evaluate many possibilities at once?"

Three different spaces need to be kept apart.

### 1. State space

A quantum state can be written as

$$
|\psi\rangle = \sum_k \alpha_k |k\rangle.
$$

This says the system is described relative to a basis of possible states $\{|k\rangle\}$. The coefficients $\alpha_k$ are amplitudes.

That is not yet a path integral. It is a description of one state in a high-dimensional state space.

### 2. Path space

The path integral ranges over trajectories, not just instantaneous states:

$$
K(b,a) = \int_{\gamma : a \to b} e^{iS[\gamma]/\hbar}\,\mathcal{D}\gamma.
$$

Here the central quantity is the action

$$
S[q] = \int_{t_0}^{t_1} L(q,\dot q,t)\,dt,
$$

where $L$ is the Lagrangian. In simple mechanical settings, $L = T - V$.

In the classical limit, the paths that matter most are the ones near stationary action:

$$
\delta S = 0.
$$

That statement does not mean nature performs a logical proof. It means the phase contributions from nearby paths align near stationary-action trajectories and cancel more strongly away from them.

### 3. Thought space

For intelligence, the closest analogue is usually not a complex quantum amplitude but a weighted family of candidate futures.

Write a future trajectory as $\tau$, and define a cost functional

$$
J[\tau] = \int_0^T c(x_t,u_t,t)\,dt + \Phi(x_T),
$$

where $c$ is a running cost and $\Phi$ is a terminal cost.

Then a planning system can be written schematically as

$$
P(\tau \mid x_0) \propto e^{-J[\tau]/\lambda}.
$$

This says low-cost futures get more weight. A chosen action can then be derived from the futures that begin with that action.

That is a real mathematical bridge to intelligence:

- keep multiple futures in play,
- weight them by value or cost,
- let the weighted mass guide action.

This is similar to the path-integral picture in outer form, but not in algebra.

The safe comparison is:

- path integrals weight trajectories by complex phase,
- planning systems weight trajectories by cost, value, or probability,
- brains and artificial agents only ever approximate this over a bounded set of internally represented scenarios.

So if a brain "thinks about several scenarios at once," the claim does not need to be mystical. It can mean the system carries a distribution, sample set, or competing population code over possible futures and updates those weights as evidence changes.

That is a useful analogy. It is still not the same as a quantum path integral.

If one wants a substrate analogy, intelligence is also not well described as "just electricity." Electricity is the medium that carries signals. The problem-solving behavior comes from architecture, learned structure, memory, feedback, and the way constraints are propagated through the system.

## Part VII: determinism, randomness, and where the proof analogy fails

Another way to see the mismatch is to separate two layers:

1. **State evolution:** in standard quantum mechanics, the state evolves deterministically under the Schrödinger equation.
2. **Observed event:** a single detector click is modeled probabilistically.

So even the program analogy has two pieces:

- a deterministic evolution rule for amplitudes,
- a probabilistic observation rule for outcomes.

By contrast, proof search normally aims at a checkable yes/no object, or at a witness with a finite certificate.

That is why the closest computational analogue to a path integral is not exhaustive proof search. It is a complex-valued computation with interference.

## Part VIII: takeaway

The temptation behind the analogy is understandable. Both exhaustive search and the path-integral picture range over many alternatives. But they live in different mathematical worlds.

- Exhaustive search is about finite coverage plus a checker.
- Path integrals are about summing amplitudes and letting phases interfere.
- Intelligent planning is often about weighting candidate futures by cost, value, or probability.
- A proof certifies necessity under explicit rules.
- An interference pattern is an empirical outcome explained by a model.

The short version is:

> exhaustive search keeps successful cases, while path integrals let alternatives cancel.

And for the intelligence analogy:

> thought is often better modeled as weighted futures than as literal quantum interference.

Those differences are enough to block the move from "all paths contribute" to either "light is literally doing proof search" or "the brain is literally running a quantum path integral."
