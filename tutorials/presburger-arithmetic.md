---
title: "Presburger arithmetic: the decidable island"
layout: docs
kicker: Tutorial 16
description: What Presburger arithmetic is, how to read its formulas, why it is decidable, and how that decidability powers real verification tools for high-assurance software.
---

What if every yes-or-no question you could ask about addition had a guaranteed algorithmic answer?

Not "probably correct." Not "works on the examples we tested." A genuine guarantee: give me any sentence about natural numbers and addition, and I will tell you, in finite time, whether it is true or false.

That guarantee exists. It is called Presburger arithmetic, and it was proved in 1929 by Mojżesz Presburger, a student in Warsaw, two years before Gödel showed that full arithmetic cannot have this property.

The trick is not magic. It is scope. Presburger arithmetic talks about natural numbers with addition and nothing else. No multiplication, no exponentiation, no general recursion. By giving up those operations, the language stays small enough that every question in it is algorithmically decidable.

This tutorial builds Presburger arithmetic from scratch: the numbers, the axioms, the formulas, and the decision procedure. It ends with the reason this matters in practice: the fragment that powers array-bounds checking, loop analysis, and high-assurance verification in real tools is, at bottom, Presburger arithmetic.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope and assumptions</p>
  <ul>
    <li><strong>Assumption A (language):</strong> The language of Presburger arithmetic is {0, S, +, =} with the usual logical connectives and quantifiers over natural numbers.</li>
    <li><strong>Assumption B (standard model):</strong> "True" means true in the standard model (ℕ, 0, S, +). Presburger's completeness theorem ensures this matches derivability from the axioms.</li>
    <li><strong>Assumption C (decidability):</strong> Decidable means there exists an algorithm that always terminates and always gives the correct answer.</li>
    <li><strong>Assumption D (bounded demos):</strong> Interactive demos use bounded search over finite ranges. The actual theory covers all natural numbers; induction and quantifier elimination handle the infinite case.</li>
  </ul>
</div>

## Part I: building numbers from nothing

Presburger arithmetic starts with two primitives:

1. A constant: $0$ (zero).
2. A function: $S$ (successor), which takes a number and returns the next one.

That is all.

Every natural number is built by applying $S$ some number of times to $0$:

$$
\begin{aligned}
0 &= 0 \\
1 &:= S(0) \\
2 &:= S(S(0)) \\
3 &:= S(S(S(0))) \\
4 &:= S(S(S(S(0)))) \\
&\;\;\vdots
\end{aligned}
$$

The symbols $1, 2, 3, \ldots$ are shorthand. They are not primitive. The only things that actually exist in the language are $0$ and $S$.

This is not an arbitrary choice. It is a design decision with a payoff: because every number is built from the same two pieces, proofs about all numbers can proceed by induction on the structure of $S$.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Why successor notation matters</p>
  <p>
    Successor notation is not just pedantry. It makes the internal structure of each number visible. When you see <code>S(S(S(0)))</code>, you can literally count the layers. When a proof peels off one <code>S</code> at a time, you can see exactly which axiom applies at each step. That transparency is what makes mechanical checking possible.
  </p>
</div>

<div class="fp-diagram">
  {% include diagrams/presburger-successor-tower.svg %}
</div>

Try building numbers yourself:

<figure class="fp-figure">
  <p class="fp-figure-title">Interactive: build numbers with successor</p>
  <iframe
    src="{{ '/presburger_explorer.html' | relative_url }}"
    title="Interactive Presburger arithmetic explorer"
    style="width: 100%; min-height: 820px; border: 0; border-radius: 16px; background: transparent;"
    loading="lazy"></iframe>
  <figcaption class="fp-figure-caption">
    Use the "Build Numbers" tab to watch successor notation grow. The "Addition Stepper" tab shows how Presburger computes addition axiom by axiom. The "Formula Playground" evaluates real Presburger sentences and shows whether they are true or false.
  </figcaption>
</figure>

## Part II: the five axioms

Presburger arithmetic is defined by five axioms (the fifth is actually an axiom schema, meaning it generates infinitely many axioms, one for each formula in the language).

<figure class="fp-figure">
  <p class="fp-figure-title">The five axioms at a glance</p>
  <img
    src="{{ '/presburger_axiom_overview.svg' | relative_url }}"
    alt="Five cards showing each axiom of Presburger arithmetic with formal notation and plain English."
    class="fp-diagram">
  <figcaption class="fp-figure-caption">
    Axioms 1–2 govern successor. Axioms 3–4 define addition. Axiom 5 is induction restricted to the Presburger language. That restriction is the key to decidability.
  </figcaption>
</figure>

### Axiom 1: zero is not a successor

$$
\forall x.\; S(x) \neq 0
$$

**In English:** No number has zero as its successor. Zero is the beginning of the line, not a place you can reach by counting forward.

**What it rules out:** Without this axiom, the number line could loop. Some number's successor could be zero, creating a cycle. This axiom forces the chain to be one-directional.

### Axiom 2: successor is injective

$$
\forall x.\,\forall y.\; S(x) = S(y) \;\rightarrow\; x = y
$$

**In English:** If two numbers have the same successor, they are the same number. The successor function never merges two different numbers into one.

**What it rules out:** Without this axiom, the number line could branch backward: two different numbers could both have the same next number. Injectivity says the line never converges.

Together, Axioms 1 and 2 ensure the natural numbers form a single, infinite, non-looping, non-merging chain starting at zero.

### Axiom 3: additive identity

$$
\forall x.\; x + 0 = x
$$

**In English:** Adding zero to any number gives back the same number.

**What it provides:** The base case for defining addition. Every recursive computation of $x + y$ will eventually reach $x + 0$ and stop.

### Axiom 4: addition recurses through successor

$$
\forall x.\,\forall y.\; x + S(y) = S(x + y)
$$

**In English:** Adding the successor of $y$ to $x$ is the same as first adding $y$ to $x$ and then taking the successor. Addition peels one $S$ off the second argument at each step.

**What it provides:** The recursive step. Together with Axiom 3, this completely determines the value of $x + y$ for any two natural numbers: apply Axiom 4 repeatedly until the second argument is $0$, then apply Axiom 3.

### Axiom 5: induction (restricted)

For every formula $\varphi(x)$ in the language $\{0, S, +\}$:

$$
\bigl[\varphi(0) \;\wedge\; \forall x.\,(\varphi(x) \rightarrow \varphi(S(x)))\bigr] \;\rightarrow\; \forall x.\,\varphi(x)
$$

**In English:** If a property holds for zero, and whenever it holds for a number it also holds for that number's successor, then it holds for every natural number.

**The critical restriction:** The formula $\varphi$ must be expressible in the language of Presburger arithmetic: it can only mention $0$, $S$, $+$, $=$, and the logical connectives. It cannot mention multiplication, exponentiation, or any other operation.

This restriction is what separates Presburger from Peano arithmetic. Peano allows induction over any first-order formula, including those that mention multiplication. That extra power is exactly what makes Peano arithmetic undecidable.

## Part III: cheatsheet — reading logic formulas

Logic notation can look alien on first contact. This reference card covers every symbol used in Presburger arithmetic.

| Symbol | Name | Read as | Example |
|---|---|---|---|
| $\forall$ | Universal quantifier | "for every" | $\forall x.\; x + 0 = x$ |
| $\exists$ | Existential quantifier | "there exists" | $\exists x.\; x + x = S(S(0))$ |
| $\rightarrow$ | Implication | "if … then" | $S(x) = S(y) \rightarrow x = y$ |
| $\wedge$ | Conjunction | "and" | $\varphi(0) \wedge \forall x.(\varphi(x) \rightarrow \varphi(S(x)))$ |
| $\vee$ | Disjunction | "or" | $P \vee Q$ |
| $\neg$ | Negation | "not" | $\neg(S(x) = 0)$ |
| $S(x)$ | Successor | "the number after $x$" | $S(0) = 1$ |
| $0$ | Zero | "zero" | The starting point |
| $+$ | Addition | "plus" | $x + S(y) = S(x + y)$ |
| $=$ | Equality | "equals" | $S(S(0)) + S(0) = S(S(S(0)))$ |

### How to read a formula aloud

Start from the outside and work inward. Quantifiers set the stage; the body makes the claim.

**Example 1:**

$$
\forall x.\; x + 0 = x
$$

Read: "For every $x$, $x$ plus zero equals $x$." This is Axiom 3.

**Example 2:**

$$
\exists x.\; x + x = S(S(S(S(0))))
$$

Read: "There exists an $x$ such that $x$ plus $x$ equals four." This asks whether 4 is even. It is true: $x = 2$ is a witness.

**Example 3:**

$$
\forall x.\,\exists y.\; x + y = S(S(S(S(S(0)))))
$$

Read: "For every $x$, there exists a $y$ such that $x$ plus $y$ equals five." Is this true? No. When $x = 6$, no natural number $y$ satisfies $6 + y = 5$.

**Example 4:**

$$
\exists x.\; S(x) = 0
$$

Read: "There exists an $x$ whose successor is zero." This is false by Axiom 1.

<div class="fp-callout fp-callout-warn">
  <p class="fp-callout-title">Free variables vs. sentences</p>
  <p>
    A <strong>sentence</strong> is a formula with no free variables — every variable is bound by a quantifier. Only sentences have definite truth values. A formula with free variables, like <code>x + 0 = x</code>, is a template that becomes true or false depending on what <code>x</code> is.
  </p>
  <p>
    Decidability applies to sentences. Given any sentence in the language, the decision procedure returns TRUE or FALSE.
  </p>
</div>

## Part IV: addition, step by step

Axioms 3 and 4 together make addition a purely mechanical process. Here is $2 + 3 = 5$ derived line by line.

$$
\begin{aligned}
2 + 3
&= S(S(0)) + S(S(S(0)))
  &&\text{expand shorthand} \\[4pt]
&= S\bigl(S(S(0)) + S(S(0))\bigr)
  &&\text{Axiom 4: } x + S(y) = S(x + y) \\[4pt]
&= S\bigl(S\bigl(S(S(0)) + S(0)\bigr)\bigr)
  &&\text{Axiom 4 again} \\[4pt]
&= S\bigl(S\bigl(S\bigl(S(S(0)) + 0\bigr)\bigr)\bigr)
  &&\text{Axiom 4 again} \\[4pt]
&= S\bigl(S\bigl(S\bigl(S(S(0))\bigr)\bigr)\bigr)
  &&\text{Axiom 3: } x + 0 = x \\[4pt]
&= S(S(S(S(S(0)))))
  &&\text{simplify nesting} \\[4pt]
&= 5
  &&\text{shorthand}
\end{aligned}
$$

Each line applies exactly one axiom. Three applications of Axiom 4 peel the three $S$'s from the second argument. Then Axiom 3 resolves the base case. The result accumulates as nested $S$'s around the first argument.

This is not hand-waving. It is a derivation: every step is licensed by a specific rule, and a machine could check each step mechanically. That is the difference between arriving at an answer and proving one.

The interactive "Addition Stepper" tab in the demo above lets you watch this process unfold for any pair of small numbers.

### Addition as a program

The axioms are also a program. Here is a Python implementation that follows the axioms exactly:

```python
def add(x, y):
    """Presburger addition, axiom by axiom."""
    if y == 0:
        return x          # Axiom 3: x + 0 = x
    else:
        return add(x, y - 1) + 1  # Axiom 4: x + S(y) = S(x + y)
```

The recursion peels $S$ off the second argument, exactly as the axioms prescribe. The base case returns $x$ unchanged, exactly as Axiom 3 says. This is not an analogy. The program and the derivation are the same computation.

## Part V: what you can say in Presburger arithmetic

The language is small — just $0$, $S$, and $+$ — but it can express more than it first appears.

### Ordering

The relation $x < y$ is not primitive, but it is definable:

$$
x < y \;\;\stackrel{\text{def}}{\iff}\;\; \exists z.\; x + S(z) = y
$$

"$x$ is less than $y$ if and only if there exists a positive number $z$ such that $x + (z + 1) = y$." This works because $S(z)$ is always at least 1.

### Evenness

$$
\text{even}(x) \;\;\stackrel{\text{def}}{\iff}\;\; \exists y.\; x = y + y
$$

"$x$ is even if and only if there exists a $y$ such that $x$ equals $y$ plus $y$." Since there is no multiplication symbol, we write $2y$ as $y + y$.

### Divisibility by a fixed constant

For any fixed $n$, "$n$ divides $x$" is expressible:

$$
\begin{aligned}
2 \mid x &\;\iff\; \exists y.\; x = y + y \\
3 \mid x &\;\iff\; \exists y.\; x = y + y + y \\
n \mid x &\;\iff\; \exists y.\; x = \underbrace{y + y + \cdots + y}_{n \text{ copies}}
\end{aligned}
$$

This is a crucial pattern: while Presburger arithmetic has no multiplication function, it can express divisibility by any fixed constant using repeated addition. The constant must be fixed in the formula — you cannot quantify over divisors.

### Modular arithmetic

Congruence modulo a fixed constant is also expressible:

$$
x \equiv r \pmod{n} \;\;\iff\;\; \exists q.\; x = \underbrace{q + q + \cdots + q}_{n} + \underbrace{S(S(\cdots S(0) \cdots))}_{r}
$$

This is important because the decision procedure reduces every formula to combinations of linear inequalities and divisibility constraints.

### Some example sentences and their truth values

| Sentence | English | True? |
|---|---|---|
| $\forall x.\; x + 0 = x$ | Zero is an additive identity | Yes (Axiom 3) |
| $\exists x.\; x + x = S(S(S(S(0))))$ | Is 4 even? | Yes ($x = 2$) |
| $\exists x.\; x + x = S(S(S(0)))$ | Is 3 even? | No |
| $\exists x.\; S(x) = 0$ | Is 0 a successor? | No (Axiom 1) |
| $\forall x.\;\exists y.\; x = y + y \;\vee\; x = S(y + y)$ | Every number is even or odd | Yes |
| $\forall x.\;\exists y.\; x + y = S(S(S(S(S(0)))))$ | Can every number reach 5? | No ($x = 6$ fails) |
| $\exists x.\;\exists y.\; S(S(S(0))) + x = y + y$ | Is some number ≥ 3 even? | Yes ($x = 1$, $y = 2$) |

Every one of these questions has a definite, algorithmically computable answer. That is decidability.

## Part VI: what "decidable" actually means

A theory is **decidable** if there exists an algorithm that:

1. takes any sentence in the language as input,
2. always terminates (no infinite loops, no timeouts, no "try harder"),
3. correctly outputs TRUE or FALSE.

Presburger arithmetic is decidable. Mojżesz Presburger proved this in 1929, presenting his result at the First Congress of Mathematicians of Slavic Countries in Warsaw.

This means there is a machine — not a heuristic, not a best-effort search, but a terminating algorithm — that can answer every question expressible in the language $\{0, S, +\}$.

The algorithm does not need to be fast. Presburger's decision procedure has high worst-case complexity (at least doubly exponential in the length of the formula). But it always finishes, and it is always right. For finite or bounded queries, modern implementations are practical.

<div class="fp-diagram">
  {% include diagrams/presburger-decidability-landscape.svg %}
</div>

### What decidability is not

Decidability does not mean the theory is trivial. It means the theory is tame enough that a machine can navigate it exhaustively.

Decidability does not mean every proof is short. Some true sentences have only very long proofs. But the decision procedure always finds one.

Decidability does not mean every question is easy to answer quickly. The worst-case complexity is very high. But "always terminates with the right answer, eventually" is still a vastly stronger guarantee than "might loop forever" or "might give the wrong answer."

### The contrast with Peano arithmetic

Peano arithmetic extends Presburger arithmetic by adding multiplication and allowing induction over all formulas.

That extension destroys decidability:

1. **Gödel's first incompleteness theorem (1931):** There exist sentences in Peano arithmetic that are true in $\mathbb{N}$ but not provable from the axioms.
2. **Undecidability:** No algorithm can decide all sentences of Peano arithmetic.
3. **Encoding power:** With multiplication, you can encode Turing machines, and the halting problem reduces to arithmetic truth.

Presburger arithmetic avoids all three of these. Its completeness and decidability come precisely from excluding multiplication.

## Part VII: the boundary — what multiplication destroys

The difference between Presburger and Peano arithmetic is exactly one operation: $\times$.

| Feature | Presburger ($0, S, +$) | Peano ($0, S, +, \times$) |
|---|---|---|
| Complete | Yes | No (Gödel) |
| Decidable | Yes | No |
| Can express primality | No | Yes |
| Can encode computation | No | Yes |
| Induction scope | Formulas in $\{0, S, +\}$ | All first-order formulas |

The loss of decidability is not gradual. It is a sharp boundary. The moment you can write $x \times y = z$ as a formula, you can encode arbitrary computation, and the halting problem infects the theory.

This is why Presburger arithmetic's limitation is actually its greatest strength. By staying on the decidable side of the boundary, every question has a guaranteed answer. For high-assurance software, that guarantee is worth more than the ability to talk about multiplication.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Multiplication by a constant is fine</p>
  <p>
    Presburger arithmetic cannot express general multiplication <code>x × y</code> where both operands are variables. But it can express multiplication by any fixed constant: <code>3 × x</code> is just <code>x + x + x</code>. The key distinction is between variable-times-variable (undecidable) and constant-times-variable (decidable).
  </p>
</div>

## Part VIII: how the decision procedure works

The core technique is **quantifier elimination**: transform any formula into an equivalent formula with no quantifiers.

### The idea

Every Presburger formula, no matter how deeply nested its quantifiers, is equivalent to a Boolean combination of:

- linear inequalities ($a_1 x_1 + a_2 x_2 + \cdots \geq c$), and
- divisibility constraints ($d \mid (a_1 x_1 + \cdots + c)$).

Once all quantifiers are removed, what remains is a finite Boolean expression that can be evaluated directly.

### Cooper's algorithm (sketch)

The standard modern procedure is due to D. C. Cooper (1972). Here is the high-level shape:

1. **Normalize** the formula so that quantified variables appear in standard positions.
2. **Eliminate one quantifier at a time**, starting from the innermost.
3. To eliminate $\exists x.\,\psi(x)$:
   - Collect all constraints on $x$ from $\psi$.
   - Identify finitely many candidate values for $x$ from the lower bounds.
   - Replace $\exists x.\,\psi(x)$ with a disjunction: $\psi(c_1) \vee \psi(c_2) \vee \cdots$
4. Universal quantifiers are handled dually: $\forall x.\,\psi(x) \equiv \neg\exists x.\,\neg\psi(x)$.
5. After all quantifiers are eliminated, evaluate the resulting ground expression.

### Worked example: "Is 4 even?"

The formula:

$$
\exists x.\; x + x = S(S(S(S(0))))
$$

Step 1 — rewrite in terms of integers: $\exists x.\; 2x = 4$.

Step 2 — solve: $x = 2$. This is a natural number, so the existential is satisfied.

Result: **TRUE**, with witness $x = 2$.

### Worked example: "Is 3 even?"

$$
\exists x.\; x + x = S(S(S(0)))
$$

Step 1 — rewrite: $\exists x.\; 2x = 3$.

Step 2 — solve: $x = 1.5$. This is not a natural number.

Result: **FALSE**. No witness exists.

### Worked example: "Can every number reach 5?"

$$
\forall x.\;\exists y.\; x + y = S(S(S(S(S(0)))))
$$

Step 1 — eliminate the inner $\exists y$: $y = 5 - x$. This is a natural number only when $x \leq 5$.

Step 2 — the formula reduces to $\forall x.\;(x \leq 5)$.

Step 3 — this is false ($x = 6$ is a counterexample).

Result: **FALSE**.

### A formula evaluator in Python

```python
def successor_notation(n):
    """Display n in Presburger's successor notation."""
    if n == 0:
        return "0"
    return f"S({successor_notation(n - 1)})"

def decide_exists_even(n):
    """Decide: ∃x. x + x = n"""
    for x in range(n + 1):
        if x + x == n:
            return True, x     # TRUE with witness
    return False, None         # FALSE, no witness

# Run the decision procedure
for n in range(7):
    result, witness = decide_exists_even(n)
    status = f"TRUE (x = {witness})" if result else "FALSE"
    print(f"∃x. x+x = {successor_notation(n)}  →  {status}")
```

Output:

```
∃x. x+x = 0           →  TRUE (x = 0)
∃x. x+x = S(0)        →  FALSE
∃x. x+x = S(S(0))     →  TRUE (x = 1)
∃x. x+x = S(S(S(0)))  →  FALSE
∃x. x+x = S(S(S(S(0))))        →  TRUE (x = 2)
∃x. x+x = S(S(S(S(S(0)))))     →  FALSE
∃x. x+x = S(S(S(S(S(S(0))))))  →  TRUE (x = 3)
```

The decision procedure separates even from odd, correctly and mechanically, for every input.

## Part IX: programs are proofs

There is a deep correspondence between logic and computation discovered independently by Haskell Curry and William Howard.

### The Curry-Howard correspondence (informal)

| Logic | Programming |
|---|---|
| Proposition | Type |
| Proof | Program |
| $A \rightarrow B$ | Function from $A$ to $B$ |
| $A \wedge B$ | Pair $(A, B)$ |
| $\exists x.\,\varphi(x)$ | A pair: the witness $x$ and a proof that $\varphi(x)$ holds |
| $\forall x.\,\varphi(x)$ | A function that, given any $x$, produces a proof of $\varphi(x)$ |

Under this correspondence:

- A proof of $\exists x.\,\varphi(x)$ is a program that **computes** the witness $x$.
- A proof of $\forall x.\,P(x) \rightarrow Q(x)$ is a program that **transforms** any proof of $P(x)$ into a proof of $Q(x)$.

### What this means for Presburger arithmetic

Presburger's decision procedure is constructive. When it proves an existential sentence $\exists x.\,\varphi(x)$, it does not merely assert that some $x$ exists. It produces the actual value.

That production is program synthesis:

- **Input:** a logical specification (a Presburger formula).
- **Output:** a concrete value satisfying the specification (the witness), together with a proof that it works.

The decision procedure is therefore a synthesizer: you state what you want as a formula, and the procedure either hands you a solution or proves no solution exists.

```python
def synthesize_additive_inverse(target, x):
    """
    Spec: ∃y. x + y = target
    Synthesize y if it exists.
    """
    if x <= target:
        y = target - x
        # Proof obligation: x + y = target
        assert x + y == target, "certificate check failed"
        return y, f"Witness y = {y}, verified: {x} + {y} = {target}"
    else:
        return None, f"No solution: {x} > {target}"

# Synthesize
for x in range(8):
    result, explanation = synthesize_additive_inverse(5, x)
    print(f"  x={x}: {explanation}")
```

Output:

```
  x=0: Witness y = 5, verified: 0 + 5 = 5
  x=1: Witness y = 4, verified: 1 + 4 = 5
  x=2: Witness y = 3, verified: 2 + 3 = 5
  x=3: Witness y = 2, verified: 3 + 2 = 5
  x=4: Witness y = 1, verified: 4 + 1 = 5
  x=5: Witness y = 0, verified: 5 + 0 = 5
  x=6: No solution: 6 > 5
  x=7: No solution: 7 > 5
```

Notice the structure: for each input, the program either synthesizes a witness and verifies it, or proves impossibility. There is no "maybe" and no timeout. That is the programs-are-proofs principle applied to a decidable theory.

### The deeper point

In undecidable theories, program synthesis from specifications is not always possible. Some specs have no algorithm that reliably finds a satisfying program.

In Presburger arithmetic, synthesis always works. Every satisfiable existential formula yields a witness. Every unsatisfiable one yields a refutation. The theory is tame enough to be fully mechanized.

This is why decidable fragments matter for engineering: they are the fragments where "prove it correct" and "synthesize it automatically" are the same operation.

## Part X: high-assurance software

Presburger arithmetic is not a classroom curiosity. It is the engine behind a large portion of automated software verification.

### SMT solvers: the linear arithmetic theory

Modern SMT (Satisfiability Modulo Theories) solvers like Z3 and CVC5 include a theory called **Linear Integer Arithmetic (LIA)**. LIA is essentially Presburger arithmetic presented for solver consumption.

When a verification tool asks "is this integer constraint satisfiable?", the LIA solver answers using a decision procedure descended from Presburger and Cooper. This happens inside:

- **Program analysis tools** (abstract interpreters, static analyzers),
- **Proof assistants** (Isabelle, Lean, Coq — all delegate integer subgoals to arithmetic solvers),
- **Model checkers** (CBMC, SPARK — for bounded and unbounded verification of C, Ada, and other code).

### Array bounds checking

The question "is `arr[i]` always within bounds?" typically reduces to:

$$
\forall i.\; (0 \leq i \;\wedge\; i < n) \;\rightarrow\; (0 \leq i \;\wedge\; i < \text{len})
$$

This is a Presburger formula (variables, addition, ordering, fixed constants). The solver decides it in one pass.

### Loop invariant verification

A loop invariant like "the counter stays between 0 and MAX" is:

$$
\forall t.\; (0 \leq \text{counter}_t) \;\wedge\; (\text{counter}_t \leq \text{MAX})
$$

When the loop body only increments or decrements by constants, the invariant and the transition relation are both in Presburger arithmetic. Verification is decidable.

### Compiler optimizations

The **polyhedral model** for loop optimization (used in LLVM's Polly, GCC's Graphite, and research compilers) represents loop iteration spaces as integer polyhedra. Dependence analysis, tiling, interchange, and parallelization all reduce to Presburger queries:

- "Do these two array accesses alias?" is an integer linear constraint check.
- "Can this loop nest be tiled?" is parametric integer programming.
- "Is this schedule valid?" is checking that all dependences are satisfied.

### seL4 and kernel verification

The seL4 microkernel's formal verification includes thousands of subgoals about pointer arithmetic, capability indices, and memory layout. Many of these subgoals are pure Presburger formulas, decided automatically by the arithmetic tactics in Isabelle/HOL.

### The pattern

The common thread is this: real systems deal with integers, indices, offsets, and counters. When the operations are limited to addition, subtraction, comparison, and divisibility by constants — and they often are — the problem lives in Presburger arithmetic, and decidability gives you a guarantee that no heuristic can match.

That is the practical payoff of Presburger's 1929 theorem: a fragment of arithmetic that is powerful enough to express most integer reasoning in software, and tame enough that a machine can always give the right answer.

## Where to go deeper

This tutorial covers the core ideas. Several directions lead further.

**Automata-theoretic decision procedures.** Büchi (1960) showed that a subset of $\mathbb{N}^k$ is Presburger-definable if and only if it is recognizable by a finite automaton when numbers are written in a suitable base. This gives an alternative decision procedure: translate the formula to an automaton, then check emptiness or universality.

**Complexity.** The decision problem for Presburger arithmetic is at least doubly exponential in the worst case (Fischer and Rabin, 1974). This is the cost of full generality. But many practically occurring formulas have much lower effective complexity, and modern solvers exploit structure aggressively.

**Extensions that stay decidable.** Some extensions of Presburger arithmetic preserve decidability: adding the divisibility predicates $n \mid x$ explicitly, adding bounded quantifiers, or combining with other decidable theories via the Nelson-Oppen method in SMT solvers.

**The Curry-Howard correspondence in full.** The connection between proofs and programs runs much deeper than the sketch in Part IX. Martin-Löf type theory, the Calculus of Constructions (the foundation of Coq and Lean), and homotopy type theory all develop this correspondence into a full-scale foundation for mathematics and verified programming.

## References

- Presburger, M. (1929) *Über die Vollständigkeit eines gewissen Systems der Arithmetik ganzer Zahlen, in welchem die Addition als einzige Operation hervortritt*. Comptes Rendus du I Congrès des Mathématiciens des Pays Slaves, Warsaw, 92–101.
- Cooper, D. C. (1972) *Theorem Proving in Arithmetic without Multiplication*. Machine Intelligence 7, Edinburgh University Press, 91–99.
- Büchi, J. R. (1960) *Weak Second-Order Arithmetic and Finite Automata*. Zeitschrift für mathematische Logik und Grundlagen der Mathematik 6, 66–92.
- Fischer, M. J. and Rabin, M. O. (1974) *Super-Exponential Complexity of Presburger Arithmetic*. SIAM-AMS Proceedings 7, 27–41.
- Gödel, K. (1931) *Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I*. Monatshefte für Mathematik und Physik 38, 173–198.
- de Moura, L. and Bjørner, N. (2008) *Z3: An Efficient SMT Solver*. TACAS 2008, Springer LNCS 4963, 337–340.
- Howard, W. A. (1980) *The Formulae-as-Types Notion of Construction*. In: To H. B. Curry: Essays on Combinatory Logic, Lambda Calculus and Formalism. Academic Press, 479–490.
- Klein, G. et al. (2009) *seL4: Formal Verification of an OS Kernel*. SOSP 2009, ACM, 207–220.
