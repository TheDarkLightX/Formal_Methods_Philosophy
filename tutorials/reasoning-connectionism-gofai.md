---
title: "Reasoning, logic, and prediction: why learning cannot replace proof"
layout: docs
kicker: Tutorial 10
description: What reasoning is, why statistical learning alone does not provide logical validity, and why dedicated solvers still matter even when learned systems become strong heuristics.
---

This tutorial addresses a question that sounds simple but divides the field: *does a language model reason?*

The answer depends on the intended definition of the word. This is not a semantic dodge; it is an engineering necessity. Two communities use "reasoning" to mean two mathematically incompatible things:

1.  **The formalist view:** reasoning is the production of *valid derivations* in an explicit calculus. It must be sound (truth-preserving) and verifiable by a mechanical checker.
2.  **The connectionist view:** reasoning is a *behavioral capability*, the ability to generalize, solve problems, and handle novel situations flexibly, regardless of the internal mechanism.

This tutorial makes three scoped claims:

1. A **base model without a checker** cannot provide formal guarantees of logical validity.
2. A **pure learned forward-pass replacement** for general SAT-style reasoning is unlikely under standard complexity assumptions.
3. A **model-plus-checker system** can still be very useful, because proposal and verification are different jobs.

These are narrower than saying "models do nothing" or "learning is useless for reasoning." The point is to separate behavioral success from certified validity.

The claims are narrow and falsifiable. The goal is not to diminish what language models can do. It is to make visible the boundary between what they do and what reasoning is.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene (scope first)</p>
  <ul>
    <li><strong>Assumption A (definition):</strong> "Logical reasoning" requires universal validity ($\forall x$), not just high-probability correctness ($P(\text{correct}) > 1-\varepsilon$).</li>
    <li><strong>Assumption B (the exactness gap):</strong> Logic is discrete; neural networks are continuous. Mapping one to the other incurs fundamental approximation errors.</li>
    <li><strong>Assumption C (complexity):</strong> Solving SAT is NP-complete (Cook, 1971; Levin, 1973). We assume $P \neq NP$, meaning no polynomial-time "forward pass" can solve it in full generality.</li>
    <li><strong>Assumption D (separation):</strong> We distinguish the <em>model level</em> (what the neural network computes) from the <em>system level</em> (the model plus tools, checkers, and gates around it).</li>
    <li><strong>Assumption E (traces):</strong> Natural-language "reasoning traces" are treated as untrusted unless tied to an executable artifact or a sound checker.</li>
  </ul>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Running example for the whole page</p>
  <p>
    Keep one tiny workflow in view: a model proposes a satisfying assignment <code>α</code> for a SAT formula <code>F</code>, and a checker either accepts it or returns a failing clause.
    This is the smallest concrete picture of the whole thesis. Proposal and certification are different jobs. Most of the page is really just a longer explanation of that split.
  </p>
</div>

## Part I: what reasoning is (the formalist definition)

In the formalist tradition, spanning Euclid, Leibniz, Hilbert, and modern verification, reasoning is **deduction**. It has a specific shape:

$$
\frac{\text{Premises}}{\text{Conclusion}} \quad (\text{Rule})
$$

This structure guarantees **soundness**: if the premises are true and the rule is valid, the conclusion *must* be true. This is not a statistical correlation. It is a necessary consequence.

### The mathematical skeleton of deduction

To see why deduction is different in kind from prediction, it helps to look at its formal structure.

A **deductive system** consists of:

- a **language** $\mathcal{L}$: a set of well-formed formulas built from symbols, connectives ($\land, \lor, \lnot, \to$), and quantifiers ($\forall, \exists$),
- a set of **axioms** $\Gamma \subseteq \mathcal{L}$: formulas accepted without proof,
- a set of **inference rules** $R$: functions from tuples of formulas to formulas.

The most basic inference rule is *modus ponens*:

$$
\frac{A \quad A \to B}{B}
$$

Read: from $A$ and $A \to B$, derive $B$. The horizontal line is not decoration. It means the step is *licensed by the system*. A checker can verify that the formula above the line matches the required pattern and that the formula below follows.

A **proof** is a finite sequence of formulas $\varphi_1, \varphi_2, \ldots, \varphi_n$ where each $\varphi_i$ is either an axiom or follows from earlier formulas by an inference rule. The last formula $\varphi_n$ is the **theorem**.

We write $\Gamma \vdash \varphi$ to mean: there exists a proof of $\varphi$ from assumptions $\Gamma$.

### The standard of proof

A 50-line proof is not "probably right." It is either right or wrong. A verifier can check it without "understanding" the topic, simply by matching patterns.

This gives reasoning a unique property: **machine checkability**. If a system produces $Q$ without the ability to guarantee the derivation chain that led to it, it is not reasoning; it is *guessing*, even if it guesses correctly 99% of the time.

The critical property is **soundness**: if $\Gamma \vdash \varphi$, then $\Gamma \models \varphi$ (every model that makes $\Gamma$ true also makes $\varphi$ true). Soundness means that the proof system never lies. Every theorem it produces is genuinely true under the given assumptions. This is not a statistical guarantee. It is an absolute one.

For first-order logic, we also have **completeness** (Gödel, 1930): if $\Gamma \models \varphi$, then $\Gamma \vdash \varphi$. Everything that is true in all models can be proved. Together, soundness and completeness mean that proof and semantic truth coincide exactly for first-order logic (see also standard texts such as Enderton, 2001).

### Induction as a proof technique

Mathematical induction is itself a deductive rule. To prove $\forall n \in \mathbb{N}.\; P(n)$:

1. **Base case:** prove $P(0)$.
2. **Inductive step:** prove $\forall k.\; P(k) \to P(k+1)$.
3. **Conclude:** $\forall n.\; P(n)$.

$$
\frac{P(0) \quad \forall k.\; P(k) \to P(k+1)}{\forall n.\; P(n)}
$$

Induction converts an infinite claim into two finite obligations. That is its power. It is the skeleton behind every safety proof that says "the invariant holds at every step": the base case establishes the initial condition, the step case shows every transition preserves the invariant, and the conclusion is universal.

### What language models do instead

A language model is a conditional probability distribution over token sequences:

$$
P_\theta(t_n \mid t_1, t_2, \ldots, t_{n-1})
$$

where $\theta$ denotes the learned parameters. The model is trained to minimize cross-entropy loss over a corpus $\mathcal{D}$:

$$
\mathcal{L}(\theta) = -\mathbb{E}_{(t_1, \ldots, t_N) \sim \mathcal{D}} \left[\sum_{n=1}^{N} \log P_\theta(t_n \mid t_1, \ldots, t_{n-1})\right]
$$

This objective says: make the predicted next token as close as possible to the actual next token in the training data. It says nothing about validity, soundness, or truth-preservation. A model trained on a corpus containing both correct proofs and plausible-sounding nonsense will learn to produce both, weighted by their frequency and context.

The model can output text that looks like a proof. Sometimes the proof is correct. But the mechanism that produced it is *pattern completion*, not *rule application*. The model has no internal proof checker. It has no concept of a "licensed step". It has a learned distribution over strings.

Return to the running example. A model may emit a candidate assignment <code>α</code> and even a nice explanation of why it should satisfy <code>F</code>. None of that becomes reasoning in the formal sense until a checker confirms that every clause of <code>F</code> is actually satisfied.

### Interlude: a formal decision tree vs. chain-of-thought text

One practical way to separate "reasoning as a checkable artifact" from "reasoning-like text" is to compare an explicit decision procedure with a natural-language rationale.

**Decision tree (formal object).** A (binary) decision tree is a rooted tree where:

- each internal node $v$ carries a predicate $p_v : X \to \{0,1\}$,
- each leaf $\ell$ carries an output label or action $a_\ell \in A$.

It defines a deterministic function $f_T : X \to A$ by starting at the root and following the unique path determined by the predicate outcomes until reaching a leaf (Breiman et al., 1984; Quinlan, 1986).

The key property is auditability: the "explanation" of a decision is the path plus the predicate outcomes. That explanation is executable and reproducible.

**Chain-of-thought (natural-language trace).** In LLM prompting, "chain-of-thought" refers to asking for intermediate natural-language steps. This often improves accuracy on multi-step problems (Wei et al., 2022; Kojima et al., 2022). The trace is still not a certificate. Without a checker, there is no guarantee that the text corresponds to a valid derivation or even that it is a faithful description of the computation (Doshi-Velez and Kim, 2017; Lipton, 2018).

#### Example: checking a proposed SAT witness

SAT has short certificates for satisfiable instances: an assignment $\alpha$ that satisfies every clause. Checking $\alpha$ is a deterministic, polynomial-time procedure.

This certificate mindset also appears in proof-carrying code: the producer supplies an artifact plus a proof, and the consumer runs a small checker (Necula, 1997).

A simple verifier can be written as a decision tree:

```text
Check(F, α)
├─ WellFormed(α)?
│  ├─ no  -> Reject("malformed assignment")
│  └─ yes
└─ Satisfies(F, α)?
   ├─ yes -> Accept("SAT", witness = α)
   └─ no  -> Reject("counterexample clause", witness = C_i)
```

A chain-of-thought style trace for the same check might look like this:

```text
1. Confirm α assigns every variable.
2. Substitute α into each clause of F.
3. If all clauses are true, conclude SAT.
```

As text, this can be useful for communication. As a verifier, it is incomplete: it does not automatically carry a machine-checkable witness (the failing clause $C_i$, or the satisfying assignment $\alpha$) unless the system also emits the concrete artifacts.

Mathematically, $\text{Satisfies}(F,\alpha)$ is the predicate:

$$
\forall C \in F.\; \text{Eval}(C,\alpha) = \text{true}
$$

If it fails, the verifier can return a specific clause $C_i$ such that $\text{Eval}(C_i,\alpha) = \text{false}$. That clause is a small, checkable witness of failure.

A natural-language rationale for the same check can be concise and readable, but it is not, by itself, executable. In formal methods terms, the decision tree is the verifier. The rationale is commentary.

## Part II: why learning alone cannot provide logical guarantees

Connectionists often argue that with enough data and layers, neural networks can learn to approximate any function, including logic. This relies on the **Universal Approximation Theorem**.

However, the formalist argument rests on four mathematical barriers that approximation does not automatically remove. This is not a claim that learned systems are useless. It is a claim about what they do not get for free.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Practical reading guide</p>
  <p>
    The next four arguments are not all doing the same job. Some are about guarantees, some are about worst-case complexity, and some are about undecidability. Keep the object of the claim in view: unchecked prediction, not every possible hybrid system.
  </p>
  <p>
    The running example helps here. Each barrier is a different reason why "predict an answer for <code>F</code>" is not the same thing as "run <code>Check(F, α)</code>".
  </p>
</div>

### Argument 1: the exactness gap (continuous vs. discrete)

The Universal Approximation Theorem (Cybenko 1989, Hornik 1991) guarantees that neural networks can approximate *continuous* functions on *compact* sets. Logic is neither continuous nor compact.

- **Discreteness:** The function $\text{SAT}(\varphi)$ (is formula $\varphi$ satisfiable?) is discrete. A single bit flip in a formula changes the answer from 0 to 1. There is no "smooth" transition. Approximating a discrete function with a continuous one requires a margin of error. In logic, a margin of error is a wrong answer.

$$
\text{SAT}(\varphi) = \begin{cases} 1 & \text{if } \varphi \text{ has a satisfying assignment} \\ 0 & \text{otherwise} \end{cases}
$$

Approximating this to within $\varepsilon = 0.1$ is meaningless: the answer is 0 or 1, and a value of 0.6 carries no logical guarantee.

In the running example, this is the difference between "the model seems confident that <code>α</code> works" and "the checker verified every clause." Confidence has no formal slot in the verifier.

- **Unboundedness:** Logical validity applies to formulas of arbitrary length and depth. Approximation theorems apply to fixed-size inputs on bounded domains.

### Argument 2: distribution dependence vs. universal validity

This argument strikes at the deepest conceptual mismatch between learning and logic.

A learned model minimizes loss over a **distribution** $\mathcal{D}$. Its guarantee is probabilistic:

$$
\mathbb{E}_{x \sim \mathcal{D}} [\text{loss}(f(x), y)] < \varepsilon
$$

Logic requires a **universal** guarantee:

$$
\forall x \in \mathcal{L}.\; \text{Valid}(x)
$$

Even a perfect distributional statement does not imply a universal statement. If $\mathcal{D}$ has support $S \subsetneq X$ (the set of inputs that occur with nonzero probability under $\mathcal{D}$), then:

$$
P_{x \sim \mathcal{D}}[h(x) = c(x)] = 1 \;\;\not\Rightarrow\;\; \forall x \in X.\; h(x) = c(x)
$$

It only implies $\forall x \in S.\; h(x) = c(x)$. The behavior off-support is unconstrained.

No amount of sampling can prove a "for all" statement. A model trained on all integers up to $10^{100}$ has proved nothing about $10^{100} + 1$. In statistical tasks (vision, speech), $\varepsilon$-error is acceptable. In logic, a single counterexample invalidates the system.

For SAT, that single counterexample can be tiny: one clause that <code>α</code> falsifies. The checker needs only one such witness to reject the whole proposal.

These are not two points on a spectrum. They are different mathematical objects. The first is a probabilistic statement about a random variable. The second is a universally quantified statement about all elements of a domain. No amount of training data can convert the first into the second, because:

1. The training distribution may not cover the relevant cases. SAT instances are combinatorially vast; no finite sample is representative.
2. Even if coverage were perfect, the model's output is still a *prediction*, not a *derivation*. Predictions can be wrong on any particular input, and there is no structural guarantee that prevents this.
3. Adversarial examples are not a rare edge case. They are widely observed in modern neural networks (Szegedy et al., 2013; Goodfellow et al., 2014), and they reflect the fact that the model's decision boundary is a learned surface in a continuous space, not a logical boundary defined by syntactic rules.

<div class="fp-callout fp-callout-warn">
  <p class="fp-callout-title">The gap in one sentence</p>
  <p>
    Logic says "for all". Learning says "with high probability over a distribution". These cannot be bridged by more data or a larger network, because they are claims of different logical types.
  </p>
</div>

### Argument 3: PAC-learning and computational barriers

In the Probably Approximately Correct (PAC) framework, a concept class $\mathcal{C}$ is *efficiently learnable* if there exists a polynomial-time algorithm that, given samples from any distribution $D$ over inputs, produces a hypothesis $h$ such that:

$$
P_{x \sim D}[h(x) \neq c(x)] \leq \varepsilon
$$

with probability at least $1 - \delta$, using a number of samples polynomial in $1/\varepsilon$, $1/\delta$, and the representation size.

Kearns and Valiant (1994) showed that certain Boolean concept classes, including general Boolean formulas and deterministic finite automata, are **not efficiently PAC-learnable** unless known cryptographic assumptions fail. More directly: learning to decide satisfiability of Boolean formulas from examples is at least as hard as breaking certain one-way functions.

The deeper result is that learning the class of all Boolean circuits of polynomial size is not PAC-learnable in polynomial time unless $\text{RP} = \text{NP}$. Since most complexity theorists believe $\text{P} \neq \text{NP}$ (and thus $\text{RP} \neq \text{NP}$), this is strong evidence that no polynomial-time learning algorithm (neural network or otherwise) can learn to decide logical validity in general.

In the running example, the lesson is not that models can never help with SAT. It is that "often propose a good assignment" and "replace the checker" are very different claims.

### Argument 4: Rice's theorem and the limits of generalization

Rice's theorem (1953) states that for any nontrivial semantic property of programs, there is no algorithm that decides whether an arbitrary program has that property.

More formally: let $P$ be any property of the partial functions computed by programs (where "nontrivial" means some programs have it and some do not). Then the set $\{e : \text{the program with index } e \text{ has property } P\}$ is undecidable.

A neural network is a finite computational device trained on finitely many examples. Rice's theorem tells us that for any sufficiently expressive logical system (one that can encode computation), the semantic properties of formulas in that system are undecidable. A learned model cannot decide an undecidable property, no matter how much data it sees or how many parameters it has.

This is not about current architectures. It is a theorem about the structure of computation itself.

So if the task family is expressive enough, there is no general learned shortcut that can make the verifier disappear. The checker is not extra ceremony. It is the thing that makes the claim meaningful.

### Complexity theory and "forward pass" limits

This is arguably the strongest argument of the four.

Most interesting logic problems (SAT, planning, theorem proving) are **NP-complete** or undecidable (Cook, 1971; Levin, 1973). A neural network (specifically, a transformer decoder) performs a fixed amount of computation per token (a "forward pass"). This is a polynomial-time operation, specifically, a circuit of limited depth.

If a neural network could reliably solve logic problems in a single forward pass, it would imply:

$$
\text{NP} \subseteq \text{P}/\text{poly}
$$

By the Karp-Lipton theorem, this would collapse the polynomial hierarchy:

$$
\text{NP} \subseteq \text{P}/\text{poly} \;\implies\; \Sigma_2^P = \Pi_2^P
$$

This would be a spectacular collapse. No one expects it to be true.

**Translation:** an exponential-search problem cannot be compressed into a polynomial-time matrix multiplication. A solver *must* search, backtrack, or iterate. An LLM that answers immediately is mathematically restricted to heuristic guessing.

## Part III: demo: the machinery of deduction

To make the difference concrete, look at **Boolean Constraint Propagation (BCP)**, the engine inside every modern SAT solver. This is the inside of the checker from the running example. It does not "think"; it forces values based on constraints.

- **Constraint:** $A \lor B$ (A or B must be true).
- **Fact:** $\lnot A$ (A is false).
- **Deduction:** Therefore, $B$ must be true.

This is **unit propagation**. It is deterministic. In formal terms:

$$
(l_1 \lor l_2 \lor \cdots \lor l_k) \;\land\; \bigwedge_{i=1}^{k-1} (\lnot l_i) \;\;\implies\;\; l_k
$$

Run the demo below to see it in action.

<div class="fp-card" style="padding: var(--space-lg); margin-top: var(--space-md)">
  <h3 class="fp-card-title">Unit Propagation Engine</h3>
  <p class="fp-card-text">
    A deterministic solver kernel. It does not guess. It only assigns values when logically forced by a "unit clause" (a clause with only one remaining possibility).
  </p>

  <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-top:12px">
    <div>
      <label for="up-input" style="display:block; font-weight:600; font-size:0.9em">Knowledge Base (CNF)</label>
      <textarea id="up-input" rows="8" style="width:100%; font-family:monospace; margin-top:4px">
A | B | C
!A
!B | D
!C
# Result should force D=true
</textarea>
    </div>
    <div>
      <label style="display:block; font-weight:600; font-size:0.9em">Solver State</label>
      <div id="up-state" style="border:1px solid var(--border); background:var(--bg-subtle); height:160px; padding:8px; overflow-y:auto; border-radius:4px; margin-top:4px">
        <span style="color:#666; font-style:italic">Ready.</span>
      </div>
    </div>
  </div>

  <div style="display:flex; gap:8px; margin-top:12px">
    <button id="up-step" type="button">Step (1 Propagation)</button>
    <button id="up-run" type="button">Run to Fixpoint</button>
    <button id="up-reset" type="button">Reset</button>
  </div>

  <label for="up-log" style="display:block; font-weight:600; margin-top:12px; font-size:0.9em">Deduction Log</label>
  <pre id="up-log" style="height:120px; border:1px solid var(--border); background:var(--bg-subtle); padding:8px; overflow-y:auto; font-size:0.85em; margin-top:4px"></pre>
</div>

Notice the behavior:

1. **Transparency:** every step cites a specific clause.
2. **Determinism:** running it twice yields the exact same trace.
3. **Conflict detection:** adding `!D` makes it instantly report a contradiction. It will not "hallucinate" a solution.

## Part IV: the connectionist counter-argument

It is important to represent the opposing view fairly. Connectionists (and many modern AI researchers) argue that the formalist view is too rigid.

**1. "Logic is just another function."**
They argue that logical rules are patterns in data. If a model sees enough examples of $P, (P \to Q) \vdash Q$, it will learn to replicate that pattern. While it may not have an explicit rule, the *result* is indistinguishable.

**2. Emergence and soft reasoning.**
Connectionists argue that "hard logic" is a brittle approximation of the real world. Real-world reasoning requires intuition, fuzzy matching, and handling uncertainty, things neural nets excel at. They view formal logic as a subset of general intelligence that can be "emulated" by a sufficiently large model, even if the model does not implement the rules directly.

**3. "The vanishing gap."**
They point to empirical success: models can now write code, solve math word problems, and even prove simple theorems. They argue the exactness gap is shrinking with scale, and eventually the error rate $\varepsilon$ will be so low it is negligible.

That challenge should be taken seriously. In the running example, it amounts to saying: maybe the model gets so good at proposing <code>α</code> that the checker matters less in practice. The rest of the tutorial explains why "less often needed" is still different from "conceptually replaced".

## Part V: why the gap persists under standard assumptions

The formalist rebuttal to "the vanishing gap" has three layers.

Keep the running example in view here too. The point is not that models can never help with SAT. The point is that a solver builds correctness by checked consequences, while an unchecked model proposes a candidate that still has to survive a gate.

### Layer 1: soundness by construction vs. statistical approximation

Every clause a CDCL solver learns is a **theorem**, logically entailed by the original formula. Every assignment it forces is a logical consequence. Every "UNSAT" answer can come with a resolution proof that is independently verifiable (Robinson, 1965; Biere et al., 2009).

A neural network's output is a prediction. It may be right, but there is no certificate of correctness attached to it. The solver's learning is deduction; the model's learning is correlation.

### Layer 2: CDCL as a deductive engine

A modern SAT solver does not guess randomly. It performs a structured search with three interlocking mechanisms.

**Unit propagation** chains forced assignments through the formula. One assignment can force another, which forces another, cascading through the clause database. Each step is an application of the unit rule, exact deduction at machine speed.

**Conflict analysis** is what makes CDCL qualitatively different from naive backtracking. When propagation leads to a contradiction (a clause with all literals false), the solver analyzes the *implication graph*, the chain of propagations that led to the conflict, and derives a new clause using the resolution rule:

$$
\frac{(A \lor x) \quad (B \lor \lnot x)}{A \lor B}
$$

The solver resolves the conflicting clauses backward along the implication graph until it produces a clause that is:

- *implied* by the original formula (sound),
- *asserting* at a particular decision level (it forces an assignment upon backtracking),
- a *general lesson* that prunes the same dead end everywhere in the search tree.

The solver does not just backtrack. It *learns*. But its learning is a theorem of the system, not a statistical pattern. The learned clause is logically entailed by the original formula. It can never be wrong.

**Non-chronological backtracking** uses the learned clause to skip directly to the deepest decision level that is actually responsible for the conflict. This can skip many irrelevant decision levels, pruning exponentially large regions of the search space.

### Layer 3: the speed argument, made precise

**Structure exploitation.** Real-world SAT instances have structure: community structure in the variable interaction graph, backbone variables that must take fixed values in every solution, and symmetries that can be broken. A CDCL solver discovers and exploits this structure *on a per-instance basis* through conflict analysis. Each conflict reveals local structure that propagation can immediately use.

A neural network would need to learn this structure from a training distribution. But the structure varies from instance to instance. The very features that make one SAT instance tractable are different from those of the next instance. The solver discovers them fresh each time; the model can only rely on whatever statistical regularities it has memorized.

**Computational cost per logical inference.** Let $n$ be the number of variables and $m$ the number of clauses.

- **Unit propagation** runs in $O(m)$ per decision level, using two-watched-literal schemes. In practice, it is nearly linear in the number of implications generated.
- **Conflict analysis** runs in time proportional to the length of the implication chain, typically $O(n)$ in the worst case per conflict.
- **A transformer forward pass** with $L$ layers, $d$-dimensional embeddings, and context length $T$ costs $O(L \cdot T \cdot d^2)$ per token. For a formula of length $T$, generating a solution of length $T$ costs $O(L \cdot T^2 \cdot d^2)$.

Even if the transformer could produce the correct answer in a single pass (which it cannot guarantee), the computational cost per logical inference is vastly higher. The solver spends $O(1)$ per forced assignment through pointer chasing in watched-literal data structures. The transformer spends $O(d^2)$ per token through dense matrix operations.

This is not a temporary engineering gap. It is a consequence of the fact that the solver is *specialized for exact inference*, while the transformer is a *general-purpose sequence model* paying the overhead of that generality on every forward pass.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Concrete scale</p>
  <p>
    Modern CDCL solvers can handle industrial instances with very large clause databases. They can also emit machine-checkable certificates of unsatisfiability in a proof system based on resolution (Biere et al., 2009). For general SAT, no neural approach is currently known to match this combination of exactness, scale, and independently checkable certificates, and the complexity-theoretic arguments above suggest that a pure "single forward pass" replacement is unlikely.
  </p>
</div>

### Layer 4: tensorized logic is real, and it still has a boundary

There is a slogan in modern neurosymbolic AI that sounds provocative: "logical rules and Einstein summation are essentially the same operation." This can be made precise, but only for a scoped fragment.

One clean setting is **finite-domain Datalog** (a positive rule language used in databases and logic programming). In this setting:

- a relation like $\text{Parent}(y,z)$ can be represented as a sparse Boolean matrix $P_{yz}$,
- a conjunctive rule body corresponds to a **join**, which corresponds to multiplying matching tensor entries,
- existentially quantified variables correspond to a **projection**, which corresponds to summing (or OR-ing) over an index.

#### Einstein summation (einsum): the index math

Einstein summation is a compact way to write a family of sums that show up everywhere in linear algebra and machine learning.

Start with plain matrix multiplication written with indices:

$$
C_{ik} = \sum_j A_{ij} B_{jk}
$$

Einstein notation drops the summation symbol:

$$
C_{ik} = A_{ij} B_{jk}
$$

The meaning is the same. The repeated index $j$ is implicitly summed over (contracted). The indices that remain, $i$ and $k$, label the axes of the output.

<figure class="fp-figure">
  <p class="fp-figure-title">Einstein summation as index contraction</p>
  {% include diagrams/einsum-index-contraction.svg %}
  <figcaption class="fp-figure-caption">
    An einsum is a rule for which indices are multiplied and which indices are summed out. A repeated index (here, j) is the contraction axis.
  </figcaption>
</figure>

For example, the Datalog-style rule

$$
\text{Aunt}(x,z) \leftarrow \text{Sister}(x,y), \text{Parent}(y,z)
$$

can be evaluated by a tensor contraction. In Boolean logic form:

$$
A_{xz} = \bigvee_y \left(S_{xy} \land P_{yz}\right)
$$

This is exactly a **Boolean semiring** contraction, where multiplication is $\land$ and addition is $\lor$. In ordinary arithmetic, a common implementation trick is to use sum and product, then threshold the result back to $\{0,1\}$:

$$
A_{xz} = H\left(\sum_y S_{xy}\cdot P_{yz}\right)
$$

where $H(t)=1$ when $t>0$ and $H(t)=0$ otherwise (a threshold that converts "count of witnesses" into a truth value). This is an exact correspondence between a rule application and an einsum-style contraction, under a finite-domain semantics (Domingos, 2025).

<figure class="fp-figure">
  <p class="fp-figure-title">Join and projection become “multiply then reduce”</p>
  {% include diagrams/join-projection-to-einsum.svg %}
  <figcaption class="fp-figure-caption">
    The shared variable y is the join key. In tensor form, it is the repeated index that is summed out. A step function converts “number of witnesses” back into a truth value.
  </figcaption>
</figure>

Positive recursion (for example, reachability and transitive closure) becomes **iterating a monotone operator to a fixpoint**, which again can be expressed in terms of repeated join-and-project steps, and those steps can be compiled to tensor operations.

<figure class="fp-figure">
  <p class="fp-figure-title">Positive recursive closure as a fixpoint loop</p>
  {% include diagrams/fixpoint-closure-join-project.svg %}
  <figcaption class="fp-figure-caption">
    Many recursive rules compute a closure: start from base facts, apply the rule to derive new facts, repeat until no new facts appear. Each iteration is join and projection, which maps cleanly to tensor contractions on finite domains.
  </figcaption>
</figure>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope and what does not follow</p>
  <ul>
    <li><strong>Datalog, not all of logic:</strong> "Rule application is einsum" is cleanest for positive, finite-domain fragments such as Datalog. Claims like "all of logic reduces to this" are much stronger and require additional machinery (for example, negation, function symbols, unification, and search).</li>
    <li><strong>Speedups depend on representation:</strong> what scales on GPU depends on whether tensors are treated as dense or sparse, and whether the workload is mostly join and fixpoint evaluation or includes hard combinatorial search.</li>
    <li><strong>Join and closure can still blow up:</strong> even in finite domains, the intermediate results of joins and repeated closure can grow rapidly. Tensorization can change constants and throughput, but it does not remove worst-case explosion.</li>
  </ul>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">EXP-050 (experiment report, not yet public)</p>
  <p>
    A private experiment (EXP-050) explored this equivalence space directly and found exact tensor/einsum formulations for finite quantifier reductions (projection), conjunctive joins (join), and positive recursive closure (fixpoints). The count-style equivalences were machine-checked in Lean. The key boundary result from the same experiment was that GPU tensorization can massively improve throughput for semantic evaluation kernels, but it does not remove combinatorial explosion in hard search problems. A SAT barrier test still exhibited exponential growth. GPU tensorization improves constants, not worst-case complexity class.
  </p>
</div>

<figure class="fp-figure">
  <p class="fp-figure-title">Fast kernels do not remove hard search</p>
  {% include diagrams/gpu-constants-vs-exponential.svg %}
  <figcaption class="fp-figure-caption">
    Conceptual picture. Tensorization can shift a curve down (better throughput), but the curve can remain exponential when the problem requires combinatorial search.
  </figcaption>
</figure>

This matters for the tutorial's thesis because it separates two ideas that are often conflated:

- **Exact deductive kernels can be implemented as tensor operations.** This is reasoning in the formalist sense, just compiled to a different set of primitives.
- **Fast evaluation is not the same as easy search.** SAT, synthesis, and many planning problems are hard because they require exploring a combinatorial space of possibilities, not because each local semantic step is expensive.

**The scoped consequence:** for general SAT-style tasks, an unchecked neural network output is not a substitute for a solver certificate. Neural methods can still be useful as *heuristics* that propose guesses, branching orders, or reformulations. The solver is still the component that turns "looks right" into "proved" or "refuted."

## Part VI: the philosophical landscape

### Gödel's shadow

Gödel's incompleteness theorems (1931) are sometimes cited in this debate, usually imprecisely. The actual content is:

**First incompleteness theorem.** Any consistent formal system $F$ that is strong enough to encode basic arithmetic contains statements that are true (in the standard model of arithmetic) but unprovable in $F$.

**Second incompleteness theorem.** Such a system $F$ cannot prove its own consistency, unless it is inconsistent.

What these theorems do *not* say:

- They do not say that formal methods are useless. They say that no single formal system can prove everything. This is a feature, not a bug: it means there is always room for stronger systems, additional axioms, and meta-level reasoning.
- They do not say that neural networks can "transcend" formal systems. A neural network is a finite computational device. It is subject to the same limitations as any other finite computation, and to additional limitations imposed by its training distribution.
- They do not say that human reasoning escapes Gödel's limits. Whether it does is a separate, open question (Penrose argues yes; most logicians are skeptical of his argument).

What the theorems *do* say for this tutorial: there is no single system (formal, neural, or hybrid) that can prove every true statement about arithmetic. This is a hard ceiling on all reasoning systems, not a special weakness of formal methods.

### Where the GOFAI vs. connectionism split came from

The split between symbolic AI and connectionist AI is one of the oldest fault lines in the field.

**GOFAI (Good Old-Fashioned AI)** is the tradition of symbolic systems: represent knowledge as symbols and explicit rules, apply inference rules to derive new facts, aim for transparency and checkability. The label is commonly attributed to John Haugeland (*Artificial Intelligence: The Very Idea*, 1985). The intellectual roots trace through Newell and Simon's *physical symbol system hypothesis* (1976).

**Connectionism** is the tradition of learned distributed representations: represent knowledge in weights and activations, learn patterns from data via gradient descent, trade explicit rules for robustness and adaptation. The roots trace through McCulloch and Pitts (1943), Rosenblatt's perceptron (1958), and the backpropagation revival (Rumelhart, Hinton, and Williams, 1986).

**A compact timeline:**

- **1943:** McCulloch and Pitts model neurons as logical gates.
- **1950s:** Early AI is strongly symbolic. Logic, search, and hand-built representations are central.
- **1956:** The Dartmouth proposal names the field "artificial intelligence."
- **1958:** Rosenblatt's perceptron demonstrates learning from examples.
- **1969:** Minsky and Papert publish *Perceptrons*, exposing fundamental limitations of single-layer networks. This redirects funding and attention toward symbolic methods.
- **1970s–1980s:** Symbolic expert systems become influential, but expose brittleness and knowledge-engineering bottlenecks.
- **1986:** Backpropagation popularizes trainable multi-layer networks, reviving connectionism.
- **1990s–2010s:** Statistical learning and then deep learning gain practical dominance on perceptual and pattern-recognition tasks.
- **2017:** The transformer architecture (Vaswani et al.) enables scaling to large sequence models.
- **2020s:** Large language models scale connectionism into broad linguistic competence.

The split hardened around three questions:

1. **Systematicity and compositionality.** Fodor and Pylyshyn (1988) argued that human cognition is systematic: anyone who can understand "John loves Mary" can understand "Mary loves John." They claimed that connectionist architectures cannot guarantee this compositional property. Defenders respond that compositionality can *emerge* from sufficient training. The formalist replies: emergence is not a guarantee. Measurement on a benchmark is not a proof of systematicity. It is evidence that the system behaves systematically *on the tested distribution*.

2. **Validity versus plausibility.** A symbolic system can be designed to be valid *by construction*. A learned system produces *plausible* outputs without structural guarantees of validity.

3. **Grounding and semantics.** In a formal system, symbols have precise semantics defined by a model-theoretic interpretation. In a learned system, "meaning" emerges from usage patterns in training data.

Modern LLMs inherit the connectionist lineage. Modern SAT solvers, model checkers, and proof assistants inherit the GOFAI lineage. Neuro-symbolic systems attempt to combine both: learned proposal plus formal gate.

## Part VII: what would count as evidence

This section turns the disagreement into falsifiable stakes.

### Evidence supporting the formalist criterion

- There exist tasks where plausible-sounding output is cheap to produce, but valid output is hard. (Example: generating a "proof" that looks correct but contains a subtle logical gap.)
- LLM-only outputs are unreliable on validity. Language models produce fluent mathematical arguments that contain invalid steps, fabricated lemma citations, and sign errors that reverse conclusions.
- Adding a checker gate makes performance *discontinuous*: either the proof checks or it does not. There is no gray area.

### Evidence supporting the cognitive criterion

- The system shows systematic generalization: novel compositions not in the training data, robustness under paraphrase and irrelevant surface changes.
- Performance is maintained across distribution shifts.
- The system can maintain intermediate constraints across multi-step inference.

### Compatibility

These are not mutually exclusive. It is coherent to hold both:

- An LLM alone is not reasoning in the formalist sense.
- An LLM alone *can* be reasoning in the cognitive sense, for some task distributions.
- An LLM plus a checker *can* be reasoning in the formalist sense, if the checker gate is sound.

## Part VIII: the synthesis (proposer-verifier)

If ML cannot *do* logic, is it useless for reasoning? **No.** It is useful, but as a **proposer**, not a **verifier**.

The "Algorithmic CEO" architecture (from [Tutorial 6]({{ '/tutorials/mprd-and-algorithmic-ceo/' | relative_url }})) embraces this split:

| Component | Role | Strengths | Weaknesses |
| :--- | :--- | :--- | :--- |
| **LLM** | **Proposer** | Creative, handles ambiguity, translates English to code | Unreliable, hallucinates, statistically approximate |
| **Solver / Checker** | **Verifier** | Sound, complete, mechanically trustworthy | Rigid, limited scope, cannot "guess" well |

**The workflow:**

1. **Propose:** the LLM generates a logical formula, a code snippet, or a proof step.
2. **Verify:** the solver (or compiler, or proof checker) checks it.
   - If valid: **accept**.
   - If invalid: **refute** (generate a counterexample).
3. **Refine:** feed the counterexample back to the LLM. Each rejection is information.

This is the neuro-symbolic architecture from [Tutorial 5]({{ '/tutorials/reformulation-and-gates/' | relative_url }}), realized as a production pattern.

It gives the best of both worlds: the **flexibility** of connectionism with the **correctness** of formalism. But it requires admitting that the LLM is *not* doing the reasoning. It is doing the *proposing*. The reasoning lives in the check.

In the running SAT example, the split is tiny and concrete: the model proposes <code>α</code>, and the checker either accepts it or points to the clause that breaks it.

### A compact decision guide

When evaluating whether a system "reasons", first choose what is being claimed:

- If the claim is "it produces valid proofs", use formalist criteria and attach a proof checker. This is a solved engineering problem.
- If the claim is "it performs inference-like behavior", use cognitive criteria and attach robust behavioral tests. This is a measurement problem.
- If the claim is "it is safe to rely on", attach gates regardless of which definition is preferred. This is a risk management problem.

## Part IX: summary of the core argument

The argument of this tutorial has three legs.

**1. Reasoning, in its strongest and most useful sense, means producing checkable inferences in a formal calculus.** This is not a matter of opinion. It is a definition that comes with a test (run a checker), a guarantee (soundness), and centuries of successful application in mathematics, logic, and engineering.

**2. Statistical learning does not by itself produce logical validity.** The exactness gap (logic is discrete, approximation is continuous), the distribution-dependence problem (learning gives probabilistic guarantees; logic gives universal guarantees), the PAC-learning barriers (learning Boolean circuits is as hard as breaking cryptography), and Rice's theorem (semantic properties of sufficiently expressive programs are undecidable) all point in the same direction. This is a boundary on guarantees for unchecked outputs.

**3. Even strong learned heuristics do not erase the role of a dedicated solver.** CDCL solvers achieve soundness by construction, exploit per-instance structure through conflict analysis, and perform millions of exact deductive steps per second at a cost of $O(1)$ per forced assignment. A transformer pays $O(d^2)$ per token for a general-purpose forward pass, cannot guarantee soundness, and cannot discover instance-specific structure on the fly. The complexity-theoretic argument ($\text{NP} \subseteq \text{P}/\text{poly}$ would collapse the polynomial hierarchy) gives a strong theoretical reason to expect that a pure forward-pass replacement will remain unlikely.

The practical conclusion is the one this tutorial series has advocated from the beginning: *use language models as proposers, and use formal methods as gates.* The proposer explores a vast space of candidates with flexibility and speed. The gate ensures that only valid candidates survive. That combination is more powerful than either component alone, and it is honest about what each component can and cannot do.

## References (starting points, not an exhaustive bibliography)

- Breiman, Friedman, Olshen, and Stone, *Classification and Regression Trees* (1984).
- Quinlan, "Induction of Decision Trees" (1986).
- Gödel, "On Formally Undecidable Propositions of Principia Mathematica and Related Systems" (1931).
- Gödel, "The Completeness of the Axioms of the Functional Calculus of Logic" (1930).
- Enderton, *A Mathematical Introduction to Logic* (2001).
- Rice, "Classes of Recursively Enumerable Sets and Their Decision Problems" (1953).
- Cook, "The Complexity of Theorem-Proving Procedures" (1971).
- Levin, "Universal Sequential Search Problems" (1973).
- Cybenko, "Approximation by Superpositions of a Sigmoidal Function" (1989).
- Hornik, "Approximation Capabilities of Multilayer Feedforward Networks" (1991).
- Valiant, "A Theory of the Learnable" (1984).
- Kearns and Valiant, "Cryptographic Limitations on Learning Boolean Formulae and Finite Automata" (1994).
- Karp and Lipton, "Some Connections between Nonuniform and Uniform Complexity Classes" (1980).
- Robinson, "A Machine-Oriented Logic Based on the Resolution Principle" (1965).
- Necula, "Proof-Carrying Code" (1997).
- Marques-Silva and Sakallah, "GRASP: A Search Procedure for Propositional Satisfiability" (1999).
- Moskewicz et al., "Chaff: Engineering an Efficient SAT Solver" (2001).
- Biere et al., *Handbook of Satisfiability* (2009): comprehensive reference for SAT solving and CDCL.
- Szegedy et al., "Intriguing Properties of Neural Networks" (2013).
- Goodfellow, Shlens, and Szegedy, "Explaining and Harnessing Adversarial Examples" (2014).
- McCarthy, Minsky, Rochester, and Shannon, "A Proposal for the Dartmouth Summer Research Project on Artificial Intelligence" (1956).
- Haugeland, *Artificial Intelligence: The Very Idea* (1985).
- Newell and Simon, "Computer Science as Empirical Inquiry: Symbols and Search" (1976).
- Minsky and Papert, *Perceptrons* (1969).
- Rumelhart, Hinton, and Williams, "Learning Representations by Back-Propagating Errors" (1986).
- Fodor and Pylyshyn, "Connectionism and Cognitive Architecture: A Critical Analysis" (1988).
- Smolensky, "On the Proper Treatment of Connectionism" (1988).
- Vaswani et al., "Attention Is All You Need" (2017).
- Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (2022).
- Kojima et al., "Large Language Models are Zero-Shot Reasoners" (2022).
- Doshi-Velez and Kim, "Towards a Rigorous Science of Interpretable Machine Learning" (2017).
- Lipton, "The Mythos of Model Interpretability" (2018).
- Karl Popper, *Conjectures and Refutations* (1963).
- Penrose, *The Emperor's New Mind* (1989): argues that human mathematical reasoning transcends Turing computation; widely debated.
- Shalev-Shwartz and Ben-David, *Understanding Machine Learning: From Theory to Algorithms* (2014).
- Domingos, "Tensor Logic: The Language of AI" (arXiv:2510.12269, 2025).

<script src="{{ '/assets/js/unit-propagation.js' | relative_url }}" defer></script>
