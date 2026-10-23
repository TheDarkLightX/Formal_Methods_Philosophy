---
title: "ZenoFCIS 2.5: From Requirements to Verified Programs"
description: "How meaning, search, and proof turn a requirement into a program whose behavior can be checked."
og_title: "ZenoFCIS 2.5: From Requirements to Verified Programs"
kicker: "Tutorial 77"
layout: docs
---

A requirement becomes dependable software only when its meaning is explicit and the program's behavior can be checked against that meaning. This tutorial builds that path one distinction at a time: from limits and proofs, through program search, to a running application and the evidence that ties them together.

**Release scope.** ZenoFCIS 2.5.0 was released on 22 October 2026. The tutorial draws on two separate records: an educational application built from a public development revision of the source, and an installation check of the signed 2.5.0 Linux binary. The two are kept apart throughout.

The main text carries the argument. The “Go deeper” panels hold the worked examples, proofs, and evidence.

**How this tutorial was made.** Human curated, edited, and refined, with neuro-symbolic AI assistance. Language models drafted the text and offered alternative wordings; a human editor reviewed every paragraph and chose the final text. Symbolic tools produced the recorded evidence and checked that every link, hash, and command survived editing.

## Getting close is not getting there

![A geometric sequence approaches one while Goodstein seed 3 reaches zero]({{ '/assets/images/zenofcis-2-5/figure-01.png' | relative_url }})

*Figure 1. Left: the partial sums approach 1 and never reach it. Right: the Goodstein sequence from 3 reaches 0 after five steps.*

Walk halfway to a wall, then half the remaining distance, and keep going. The positions are 1/2, 3/4, 7/8, …, and after n steps the position is 1 − 2⁻ⁿ. The walk gets as close to the wall as we like, but in exact arithmetic it never arrives. So a loop that stops once it is within some tolerance of the wall finishes, and a loop that waits to reach the wall exactly never does.

Mathematics asks whether a sequence has a limit. A program needs to know whether a stopping condition is ever met. These are different questions, and they can have different answers.

<details id="zeno-depth">
<summary>Go deeper: the limit exists even when the loop never ends</summary>

Our source for Zeno's argument is Aristotle, who reports that the moving thing “must arrive at the half-way stage before it arrives at the goal” (*Physics* VI.9). These are Aristotle's words about Zeno, not a quotation from Zeno himself. [1](https://classics.mit.edu/Aristotle/physics.6.vi.html)

The modern answer is a statement about limits. For any positive tolerance ε, enough steps make the remaining distance 2⁻ⁿ smaller than ε, so the sequence converges to 1. That settles a question about a mathematical sequence. It says nothing about whether a program told to “repeat forever” ever finishes. Floating-point rounding can make such a loop appear to arrive, but that is a different arithmetic model, not evidence that the infinite sequence reached its limit.

Formally, a sequence indexed by the natural numbers is a function a: ℕ → X. Its values might be distances, integers, program states, requests, or security decisions. A recurrence defines each value from earlier ones. Not every mathematical sequence has a computable rule, and knowing a rule does not make its long-run behavior easy to prove; the next section shows how hard that can be. To reason about a program, we track its complete state and its transition rule, not only the values it displays, and an interactive program can produce many different traces depending on its inputs.

</details>

## A simple rule, a hard proof

Goodstein sequences show how hard a simple rule can be to reason about. Write a number in hereditary base notation, raise the base everywhere, then subtract one, and repeat. Starting at 4 gives 4, 26, 41, 60, 83, …, and the values keep growing for an astronomically long time. Yet every Goodstein sequence eventually reaches zero.

The proof does not follow the numbers. It follows an ordinal, a different measure that decreases at every step, even while the number grows. Since no infinite strictly decreasing sequence of ordinals exists, the process must stop. The ordinal is a tool of the proof, not storage the program needs. Kirby and Paris showed that this theorem, stated for every starting value, cannot be proved in first-order Peano arithmetic, assuming that theory is consistent. A one-line rule can need mathematics stronger than ordinary arithmetic to show where it ends. [2](https://fa.ewi.tudelft.nl/~hart/37/onderwijs/verzamelingenleer/materiaal/goodstein.pdf), [3](https://www.cs.tau.ac.il/~nachumd/term/Kirbyparis.pdf)

![Goodstein sequence from 4: the values 4, 26, 41, 60, 83 rise while the matching ordinals fall from omega to the omega down to omega squared times 2 plus omega plus 5]({{ '/assets/images/zenofcis-2-5/figure-goodstein-ordinal.png' | relative_url }})

*Figure 2. Starting from 4, the number grows at every step while its ordinal falls. The two rows do not share a numerical scale.*

<details id="goodstein-depth">
<summary>Go deeper: compute the first steps and watch the ordinal fall</summary>

Start with a natural number and write it in hereditary base 2. “Hereditary” means the exponents are also written in base 2, and their exponents too, all the way down. Then replace every occurrence of the base 2 by 3 and subtract one. Repeat with the base raised to 4, then 5, and so on, one step at a time.

The first step from 4 shows how this works. In hereditary base 2, 4 = 2^(2^1). Replacing each 2 by 3 gives 3^(3^1) = 27, and subtracting one gives 26. This is not a change of notation: ordinary base conversion keeps a number's value, while Goodstein's step changes it. Continuing gives 41, 60, and 83.

For a sequence short enough to finish on the page, start at 3. The values are 3, 3, 3, 2, 1, 0, with bases 2, 3, 4, 5, 6, 7. The first three values look the same, but the states differ because the base has changed. A program that forgot the base could not compute the next step.

Why must every sequence end? Track a different quantity. Take the hereditary representation and replace the base by ω, the first infinite ordinal. The resulting ordinal decreases at every step, even when the integer grows, and there is no infinite strictly decreasing sequence of ordinals. Starting from 4, the ordinals are ω^ω, then ω²·2 + ω·2 + 2, ω²·2 + ω·2 + 1, ω²·2 + ω·2, and ω²·2 + ω + 5. Notice the last step: the number rises from 60 to 83 while its ordinal falls. (Coefficients are written on the right because ordinal multiplication is not commutative.) Here ω is an ordinal, not a very large integer. [2](https://fa.ewi.tudelft.nl/~hart/37/onderwijs/verzamelingenleer/materiaal/goodstein.pdf), [3](https://www.cs.tau.ac.il/~nachumd/term/Kirbyparis.pdf)

Gödel's incompleteness theorems already show that some true statements of arithmetic cannot be proved in Peano arithmetic. The Kirby–Paris result is different in kind: it identifies a specific, natural statement about a simple numerical process, and it needed its own proof.

Each Goodstein step is a finite, effective computation on a finite integer. The ordinal belongs to the reasoning about the process; the program never stores an infinite quantity or consults one at run time. Finite ordinal expressions such as ω²·2 + ω + 5 can themselves be handled as ordinary syntax, and the well-foundedness of the ordinals supplies the justification. [2](https://fa.ewi.tudelft.nl/~hart/37/onderwijs/verzamelingenleer/materiaal/goodstein.pdf), [3](https://www.cs.tau.ac.il/~nachumd/term/Kirbyparis.pdf)

Checking a proof and finding one are different tasks. In an ordinary proof calculus, a proposed proof can be checked mechanically, while searching for a proof of an arbitrary sentence may never finish. For any single starting value, the run terminates and its finite trace could, in principle, be checked step by step.

</details>

## Code, behavior, and intent

A program can be studied at three levels. Its **text** can be encoded as a number, so programs can be stored, searched, and passed to other programs. Its **semantics** says what it does. Its **specification** says what it should do. Verification compares what a program does with what it should do; the encoding alone tells us neither.

Two ideas connect behavior to proof. An **invariant** is a property that holds in every reachable state. It can establish safety, though by itself it never shows that a program finishes. The **Curry–Howard correspondence** goes further: in suitable typed languages, a proposition is a type and a proof is a program of that type. A function whose type promises “a result r together with evidence that r = n²” carries its correctness claim in its type, which an ordinary “number to number” type cannot do. [20](https://www.lem12.uksw.edu.pl/images/1/15/AssigningMeanings1967.pdf), [21](https://www.cs.cmu.edu/~crary/819-f09/Howard80.pdf), [22](https://www.cs.cmu.edu/~crary/819-f09/Martin-Lof80.pdf)

Encoding also explains universality. Turing wrote that “it is possible to invent a single machine which can be used to compute any computable sequence.” His universal machine does this by interpreting encoded descriptions of other machines. Running every machine is not the same as answering every question about them. [4](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)

<details id="logic-depth">
<summary>Unpack the logic: encodings, invariants, and Curry–Howard</summary>

Start with a deliberately plain encoding. Give each token an integer, include delimiters or lengths, and encode the resulting finite sequence as a single natural number. Richer encodings preserve syntax trees and variable binding. Either way, every finite program can be represented by a number.

### From representation to meaning

An encoding is one mathematical view of a program. Semantics gives another: the program as a function, a state-transition system, or a set of permitted execution traces. Logic then states properties of that behavior. The representation, the behavior, and the property are related, but they are not interchangeable.

An invariant is a predicate on program states. An invariant map attaches one to each point in the program: what must be true of the stored values whenever execution reaches that point. Formally it is a map A: Location → (Store → Prop). Floyd's foundational treatment assigns such assertions to the connections in a flowchart and checks the obligation each command creates between them. This makes the program's logical structure visible, rather than merely numbering its text. [20](https://www.lem12.uksw.edu.pl/images/1/15/AssigningMeanings1967.pdf)

For a transition system, an **inductive invariant** I holds in the initial state and is preserved by every permitted transition. If I also implies the desired safety property, induction on the length of an execution establishes that property in every reachable state. The square loop below works through one example, with n − i as its separate termination measure. Hoare logic organizes this reasoning around preconditions, commands, and postconditions. [6](https://www.cs.cmu.edu/~crary/819-f09/Hoare69.pdf)

The Curry–Howard correspondence makes a second connection. In suitable typed calculi, propositions correspond to types, and proofs correspond to the terms that inhabit them. A proof of “A implies B” behaves like a function that turns evidence for A into evidence for B, and applying the function corresponds to using the implication. For example, the function that swaps the two parts of a pair has type A × B → B × A, and it is also a proof that “A and B” implies “B and A”. [21](https://www.cs.cmu.edu/~crary/819-f09/Howard80.pdf)

An ordinary type such as “natural number to natural number” does not say that a function computes a square. A dependent type can: for each natural number n, return a natural number r together with evidence that r = n². The claim becomes part of the type instead of a comment. Connecting such a type to an imperative implementation still requires the program's semantics. [22](https://www.cs.cmu.edu/~crary/819-f09/Martin-Lof80.pdf)

The rules of the proof system matter. A nonterminating program is not automatically a proof, and ordinary type checking cannot establish a requirement nobody stated. Proofs need a termination or normalization discipline, or an explicit account of partiality and effects. Assumptions, admitted gaps, and the trusted checker all remain part of the assurance boundary. Mechanically checking a supplied proof does not solve the harder problem of finding one.

</details>

## Defining a machine does not build it

An abstract machine fixes its states, its transitions, and what counts as a result. Finite automata, counter machines, and the lambda calculus organize computation in different ways. A Turing machine's tape has no fixed size, but any run that finishes uses only finitely many cells.

Stronger machines are easy to define. An oracle machine can be handed the answer to the halting problem; an infinite-time machine can be allowed to continue past infinitely many steps. Defining that power does not build it. These models earn their place by making assumptions explicit and by suggesting restrictions that can actually be built. [15](https://doi.org/10.1147/rd.32.0114), [16](https://www.wolframscience.com/prizes/tm23/images/Minsky.pdf), [17](https://www.cis.upenn.edu/~cis5110/Church-UnsolvableProblemElementary-1936.pdf), [18](https://people.math.ethz.ch/~halorenz/4students/Literatur/TuringOrdinalLogic.pdf), [19](https://arxiv.org/html/math/9808093)

The **Edwards Contract Machine**, a teaching construction proposed here, makes the gap concrete. Ideally, it accepts a candidate program p only when p meets a requirement R on every input in a domain X. That defines success; it does not say how to find p. A buildable version searches a finite set of candidates against a finite domain D. Success then covers exactly D, and running out of candidates means only that this search found nothing, not that no program exists.

![Two panels: the ideal Edwards machine defines success from a contract, while the buildable machine searches finite candidates against a finite domain and returns a passing candidate or UNKNOWN]({{ '/assets/images/zenofcis-2-5/figure-edwards-machine.png' | relative_url }})

*Figure 3. The ideal machine defines success but gives no algorithm. The buildable machine searches finite candidates against a finite domain, and each answer covers only what was searched.*

A standalone Python example applies the construction to moving fictional credits between nonnegative balances. The search finds t = min(a, max(r, 0)) and checks it on every input in a finite domain; a separate short proof then covers every integer request under the same balance preconditions. The panel below works through both.

<details id="machines-depth">
<summary>Build the Edwards machine, from ideal contract to finite search</summary>

A finite automaton remembers only which of finitely many states it is in. Two states are enough to track whether the number of 1s read so far is even or odd: reading 1 switches state, reading 0 does not. Limited memory makes some tasks impossible, but it also makes many questions about the machine's behavior decidable. The restriction is part of what makes it useful. [15](https://doi.org/10.1147/rd.32.0114)

A counter machine looks different. Its finite program increments natural-number counters, tests them for zero, decrements them, and branches. Suitable counter machines can compute whatever a Turing machine can. The tape has disappeared from the description, but the unbounded storage has moved into the counters. How a model looks and what it can compute are separate questions. A single instruction on an arbitrarily large number also need not correspond to one cheap physical operation. [16](https://www.wolframscience.com/prizes/tm23/images/Minsky.pdf)

Church's lambda calculus presents computation as expressions and substitution rather than a tape. An evaluator can give those expressions a machine semantics. Comparing such models separates a change in notation from a change in what can be computed. [17](https://www.cis.upenn.edu/~cis5110/Church-UnsolvableProblemElementary-1936.pdf)

The unbounded tape deserves a careful reading. Every finite run uses finitely much tape, so a finite device with enough storage can simulate any single run. What no fixed storage allowance provides is room for every possible run. The idealization is useful even though it is never built in full. [4](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)

### Stronger assumptions, stronger machines

Now strengthen the machine. Give it an oracle that answers whether an ordinary Turing machine eventually halts. Relative to that oracle, the halting question becomes decidable. The definition is mathematically sound, but it has moved the hard part into an assumption; nobody has built the oracle. Oracle machines make such dependencies explicit, and they have undecidable questions of their own. [18](https://people.math.ethz.ch/~halorenz/4students/Literatur/TuringOrdinalLogic.pdf)

Infinite-time Turing machines are another disciplined example. Their computations pass through ordinal-indexed stages, and the definition states what happens at limit stages. That rule is essential: steps lasting 1/2, 1/4, 1/8, … seconds add up to a finite duration, but nothing says what state the machine is in at the limit, or how anyone could read off its answer. The theory defines a mathematical model, not an engineering design. [19](https://arxiv.org/html/math/9808093)

This brings us back to Zeno without rejecting abstraction. A geometric limit, an infinite-time transition rule, and a physically observable computation are different objects; each can be studied, provided we say which one supports a conclusion. Turing's analysis does not by itself prove every imaginable physical hypercomputer impossible, and naming an oracle or postulating infinitely many stages does not produce a working one.

### The Edwards Contract Machine

*The Edwards Contract Machine is a teaching construction introduced here. Its ideal relation defines success; its finite procedure shows one way to search for it.*

Give the machine a contract: an input domain X, an output domain Y, a family P of total candidate programs, and a relation R(x, y) saying which outputs are acceptable. Its ideal transition goes from “ready with this contract” to “done with program p” exactly when p belongs to P and R(x, p(x)) holds for every x in X.

This is a specification of success, not an algorithm. It does not say how to find a valid program, promise that one will be found, or decide that none exists. Even the assumption that every candidate is total belongs to the ideal model; for arbitrary code it is not decidable.

A finite version can be built. Choose a finite candidate set G, for example every syntax tree up to a stated size in some grammar, and a finite domain D. Try each candidate on every input in D, and return one that passes them all; otherwise return UNKNOWN. Everything involved is finite, so the procedure always terminates. If D is the whole intended domain, a returned candidate satisfies the whole finite contract; if D only samples an infinite domain, the result holds only on D; and exhausting G says nothing about candidates outside it. The machine is allowed to say UNKNOWN, and that is what keeps it buildable.

For a worked example, use fictional balances. A source holds a ≥ 0 credits, a destination holds b ≥ 0, and r is a signed request. A request of zero or less should transfer nothing. A positive request should transfer the amount requested if the source has it, and otherwise everything that remains. The search uses expressions built from a, r, zero, min, and max.

The search found:

```text
t = min(a, max(r, 0))
a_next = a - t
b_next = b + t
```

The search checked the complete domain of 126 pairs, a = 0, …, 8 and r = −3, …, 10, and found this expression in the five-node grammar; the smaller three-node grammar returned UNKNOWN. A separate finite check confirmed the behavior, nonnegative balances, and conservation of credits over 1,134 combinations of balances and requests. Both results come from the accompanying standalone Python example.

A short argument goes beyond those checks. Since a and max(r, 0) are nonnegative, 0 ≤ t ≤ a. If r ≤ 0, then t = 0; if 0 < r ≤ a, then t = r; if r > a, then t = a. So the required behavior holds for every integer input that meets the preconditions. Moreover, (a − t) + (b + t) = a + b, and both new balances stay nonnegative. This universal conclusion comes from the case analysis, not from extrapolating the 126 checks. The Python script does not certify this argument, and fixed-width machine arithmetic would need its own overflow conditions.

Why not strengthen the Edwards machine so it always returns a correct program or correctly reports that none exists? That would be a new and much stronger assumption. Take a single candidate that always returns zero, and let the requirement at input n say that some fixed ordinary machine has not halted within its first n steps. Each individual check is finite. But deciding whether the candidate meets the requirement for every n is deciding whether that machine ever halts. An always-terminating, always-correct oracle for such contracts would therefore exceed ordinary effective computation. Defining it does not implement it.

</details>

## A shared object of thought

My aim with the Zeno Abstraction Language (ZAL) is to let a human and a machine work on the same object of thought. We should be able to point at a condition, a state transition, an assumption, or a claim about eventual progress, and ask whether we mean the same thing. The meeting point is the abstraction itself: something both sides can inspect, question, and refine.

Controlled English is one way into that abstraction, not the abstraction itself. Controlled languages can have formal semantics and several views of their own; what distinguishes ZAL is that the shared model sits at the center. The goal is not to restrict English until a parser accepts it. Each view exposes something the others hide. A formula shows a quantifier that a sentence leaves implicit. A typed view shows that two uses of “balance” mean different things. A plain-language view shows when a consistent formula says something nobody wanted.

Think of the model as a shared workbench. A person asks, “Does this mean every request must eventually complete?” The machine points to the request domain, the completion predicate, and the missing assumption about the environment. A counterexample then shows exactly where the stated meaning departs from the intended one. Each exchange changes the shared model instead of trusting that two private interpretations happen to agree.

Human and machine need not reason the same way. They need a stable object, explicit views of it, and a way to expose disagreement before deployment. ZAL provides symbolic, typed, and language views of one explicit model. Its renderings are deterministic, so a change of view changes the presentation and keeps the declared proposition fixed.

## How a synthesizer searches

Program synthesis takes two inputs: a **specification** of acceptable behavior and a **language of allowed programs**. The synthesizer searches that language for a program that meets the specification. A specification may consist of examples, logical conditions, or both; examples alone often leave several answers open. [23](https://ceur-ws.org/Vol-4008/SMT_paper11.pdf), [25](https://arxiv.org/html/2504.18943v1)

Take a small target: add two mathematical integers. Allow expressions built from x, y, addition, and multiplication, with no overflow, and require the result to equal x + y for every pair of inputs.

![Original bottom-up enumeration diagram showing two leaves eight size-three expressions and selected size-five expressions]({{ '/assets/images/zenofcis-2-5/figure-05.png' | relative_url }})

*Figure 4. Bottom-up enumeration builds 2 expressions of size one, 8 of size three, and 64 of size five; four of the size-five expressions are shown.*

Start with x and y. Combine them into x + y, x × y, and the other size-three expressions; then combine those again into larger candidates. This is **bottom-up enumeration**: build larger programs from smaller ones already in hand, and evaluate each candidate to see whether it meets the requirement.

## Same answers, different programs

![At input two-two sum and product share output four while input two-three separates their output vectors]({{ '/assets/images/zenofcis-2-5/figure-06.png' | relative_url }})

*Figure 5. One observation puts x + y and x × y in the same class; a second observation splits them. The inputs adapt a published sum-versus-product example and are not output from a CE-graph or COGS run.*

At the input (2, 2), x + y and x × y both return 4. On that one example they are **observationally equivalent**, so a synthesizer can keep one representative and skip duplicate work. But the grouping must stay open to revision.

At (2, 3) the answers are 5 and 6, and multiplication fails the addition requirement. A verifier can return (2, 3) as a **counterexample**, which splits candidates that looked identical a moment ago. Passing examples nominates a candidate; only a check over the specification's full domain can accept it.

Recent research organizes this search more efficiently; the panel below compares three approaches. Later sections follow a real synthesis task through its recorded checks and into a running application.

<details id="synthesis-depth">
<summary>Go deeper: what a synthesizer receives, and how research speeds it up</summary>

### What the synthesizer receives

Verification checks the correctness condition for a given candidate; execution only runs a candidate on particular inputs. A successful run says nothing about inputs that were not tried.

Restricting the language changes what examples can decide. If candidates must have the form f(x) = ax + b with integer parameters, then f(0) = 1 and f(2) = 5 force b = 1 and a = 2. Those two examples are decisive within that family. They would not pin down a program in an unrestricted language.

Indeed, 2x + 1 and 2x + 1 + x(x − 1)(x − 2) both fit the examples (0, 1), (1, 3), and (2, 5), but they disagree at x = 3, giving 7 and 13. This is why the grammar and the specification must be stated together. [5](https://www.microsoft.com/en-us/research/wp-content/uploads/2013/05/fmcad13.pdf)

### Counting the candidates

Our grammar has two leaves, x and y, and two binary operators. Counting syntax-tree nodes gives 2 terms of size one, 8 of size three, and 64 of size five. The last count includes both placements of a leaf and a size-three subtree around each operator. These are ordered trees, so x + y and y + x count separately even though they compute the same integer function.

The accompanying data lists all 74 terms through size five. Size counts nodes, not tree depth, and changing the grammar or the arithmetic changes the search problem. Multiplication is included to make accidental agreement easy to see.

### Observation classes

On the single input (2, 2), sum and product have the same output vector `[4]`. Adding (2, 3) gives `[4,5]` for the sum and `[4,6]` for the product. These vectors summarize behavior on the chosen observations and nothing more. By contrast, x + y and y + x agree on every integer input.

Keeping one representative per class and discarding the rest can lose a program that a later counterexample would have needed. So the optimization carries a duty: keep enough structure to regroup when new evidence separates the members.

### Three research approaches

The 2025 CE-graph proposal builds a graph conditioned on each new counterexample and combines it with the existing graph, keeping only the equivalences both support. The operation resembles an intersection, not an ordinary e-graph union; Figure 5's split is a teaching picture, not this operation. The represented terms may still need to grow; the graph does not automatically contain the whole grammar. [23](https://ceur-ws.org/Vol-4008/SMT_paper11.pdf)

The later COGS paper keeps explicit lists of observed values and refines classes by separating members that new observations distinguish. Its signature diagram shows the old and new observations side by side. [24](https://repositum.tuwien.at/handle/20.500.12708/230505)

The GPU paper synthesizes finite-trace temporal formulas that accept positive example traces and reject negative ones. For each candidate formula it stores a bit-vector recording whether the formula holds at every position of every trace; recording only the first position would lose what temporal operators need. New formulas are evaluated by operations on these bit-vectors, many candidates at once. This changes the cost of search, not what the examples establish. A formula that fits the examples need not capture the intended behavior on unseen traces, and faster enumeration does not supply missing requirements. [25](https://arxiv.org/html/2504.18943v1)

</details>

## Small questions, complete answers

Some questions can be answered completely. To compute n² without multiplication, keep a counter i and a running total s, start at (0, 0), and maintain the invariant s = i² with 0 ≤ i ≤ n. Because (i + 1)² = i² + 2i + 1, each step adds 2i + 1 to s and 1 to i. When the loop exits with i = n, the invariant gives s = n². The quantity n − i falls by one on every step, which proves termination. Machine overflow needs its own condition.

Finite checking can be complete too: it can cover every input in a declared domain, not just a sample. Its value then depends on whether that domain and its semantics capture the real requirement. Before accepting the word “verified”, ask five questions:

- What exact artifact was checked?
- What property was checked?
- Over which inputs and states?
- Using which semantics, assumptions, and checker?
- What connects that artifact to the program actually deployed?

<details id="bounds-depth">
<summary>Derive the square loop, step by step</summary>

![A square accumulator maintains s equals i squared at successive states]({{ '/assets/images/zenofcis-2-5/figure-07.png' | relative_url }})

*Figure 6. The first four states of the square loop. The figure illustrates the rule; the algebra below proves it preserves the invariant.*

Why add 2i + 1? Moving from i to i + 1, the next square is (i + 1)² = i² + 2i + 1, and s already equals i². So the update is the simultaneous assignment (i, s) := (i + 1, s + 2i + 1). In a sequential language, update s before incrementing i, or save the old i.

Four obligations make the argument complete:

- **Initialization:** 0 = 0².
- **Preservation:** the algebra above keeps s = i².
- **Exit:** when i = n, the invariant gives s = n².
- **Termination:** n − i is a nonnegative integer that decreases by one on each iteration while i < n.

The first three give **partial correctness**: if the program stops, its answer is right. Adding termination gives **total correctness**. Neither says the computation is fast enough for its purpose.

Machine arithmetic adds an obligation of its own. Hoare warned that “computer arithmetic is not the same as the arithmetic familiar to mathematicians”. A proof over unbounded integers does not cover a machine type that can overflow; the bounds or the modular semantics must be chosen and stated. [6](https://www.cs.cmu.edu/~crary/819-f09/Hoare69.pdf)

### Why useful boundaries are an advantage

Practical systems make progress by choosing boundaries. They restrict the language, bound the inputs, synthesize only a small decision kernel, require an explicit contract, or use a proof system with stated assumptions. These choices are engineering decisions, not embarrassing footnotes. They define which claims the machinery can actually support.

Over a finite input domain D, a checker can establish a property for every x in D, by exhaustive evaluation, a symbolic decision procedure, or another justified method. That is stronger than testing a handful of examples. It is also narrower than a theorem for unbounded integers, arbitrary networks, or every possible environment.

</details>

## Safety is not progress

“Always keep the reserve” forbids a bad state. “Eventually complete every request” demands progress. A system that freezes satisfies the first and fails the second. The first is a safety requirement and the second a liveness requirement, and they need different evidence.

On a finite trace, the ending matters. In the semantics used here, “eventually” includes the present: the trace [false, false, true] satisfies “eventually p” at its start, and the completed trace [false, false] does not. Strong “next” is false at the last position, because there is no next observation. A real-time deadline also needs a clock and timing assumptions, and unbounded progress may depend on an explicit fairness assumption. A guarantee about a system must cover every admitted execution under its assumptions; one successful trace is not enough.

<details id="temporal-depth">
<summary>Why a finite ending changes what is true</summary>

![Finite eventuality outcomes depend on whether a witness occurs before the trace ends]({{ '/assets/images/zenofcis-2-5/figure-08.png' | relative_url }})

*Figure 7. Three completed traces, each evaluated at t = 0. A witness at the current position counts for “eventually”; a trace that ends without one fails.*

Return to the two sequences at the start. “Eventually reach 1” is false for the exact partial sums of the halfway walk. “Eventually reach 0” is true for every Goodstein sequence. Both statements promise a future witness, and neither gives a practical deadline: even when the stopping point exists, it may lie far beyond any available resources.

Temporal logic makes such distinctions part of the specification. A state property asks what is true now; a temporal property asks how truth is arranged along a trace. A single observed breach refutes “always keep the reserve”, which makes it a safety property. “Eventually resolve every pending order” is a liveness property: it asks for progress over an ongoing execution, not just the absence of a bad state.

A wall-clock deadline needs more than the word “eventually”: it needs a clock model, a deadline, and assumptions linking logical steps to time. Progress can also depend on the environment. Does the scheduler eventually run an enabled action? Does a user eventually approve? Does a remote service eventually respond? These are fairness and environment assumptions to state explicitly; a language does not acquire them by having temporal operators.

The public 2.5 release includes a separate `.zeno` v1 temporal-claim facility, with finite-trace operators such as `eventually`, `always`, `next`, and `until`. It is distinct from the Boolean ZAL state-machine grammar described in the next section, which has no temporal operators. [13](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TEMPORAL_LOGIC_V1.md), [12](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/GRAMMAR.md#L89-L107)

The documentation gives this syntax:

```text
claim 500 stable cvc5 finite 4 = always atom(post.100 >= 0);
claim 501 stable_forever lean unbounded = always atom(post.100 >= 0);
```

The two claims look alike but ask different questions. `finite 4` ranges over nonempty traces of length one through four; the 4 counts logical observations, not seconds. `unbounded` creates a Lean proof obligation, and the facility has no finite evaluator that could certify an infinite future. [13](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TEMPORAL_LOGIC_V1.md)

Within the finite semantics, `eventually p` holds when p is true at the current position or a later one still in the trace. The evaluator never appends an imagined future witness. An empty trace, a missing observation, an arithmetic failure, or an exceeded limit can make the claim indeterminate, which blocks it.

The other operators handle endings just as explicitly. Strong `next p` is false at the final position, because there is no next observation. `always p` needs p at every remaining position. Strong `p until q` requires q to occur, with p holding at every position before it. These rules keep everyday English from hiding what happens at the end of a trace. [13](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TEMPORAL_LOGIC_V1.md)

Unbounded claims are different: each carries a proof obligation that must be discharged under an explicit kernel and axiom policy. In the public 2.5.0 CLI, the ordinary Lean-export route reports UnsupportedMode, so this tutorial presents no unbounded temporal claim as proved. The finite examples illustrate trace semantics; they do not establish fairness or the behavior of a running application. [14](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-cli/src/main.rs#L1360-L1405)

</details>

## One model, two notations

The v2.5.0 source includes an optional research prototype of Boolean ZAL, profile `zal/finite-fsm/1`, which is outside the released API and CLI. Its grammar pairs each symbolic rule with a sentence in controlled English: [12](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/README.md)

```text
rule approve_order: pending + approve [authorized] -> accept approved;

Rule approve_order: when the state is pending and the event is approve,
if authorized, move to approved.
```

Both forms denote the same canonical model, and the grammar fixes what each word means, so no language model is asked to improvise an equivalent policy. The `authorized` Boolean is an input observation; authenticating an actual person is the surrounding application's job. The grammar has no temporal operators, so a progress requirement can be recorded only as an unresolved placeholder, which is reported, not checked. [12](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/GRAMMAR.md#L75-L107)

<details id="zal-depth">
<summary>Why a safe state graph can still wait forever</summary>

![ZAL order states allow a pending order to keep rejecting without progress]({{ '/assets/images/zenofcis-2-5/figure-10.png' | relative_url }})

*Figure 8. An order can stay pending forever if every approval is unauthorized. Every state is safe, yet nothing resolves.*

A finite-state machine has a finite state graph but can run for arbitrarily long. Checking an invariant on every reachable state therefore establishes that property throughout executions of any length. It does not show that a desired event will ever happen; an endless self-loop is the simplest counterexample.

The prototype can keep a progress requirement as readable text:

```text
unresolved liveness: every pending order eventually resolves;
```

This line has no executable meaning. If the other checks pass, the prototype keeps it and reports the result as unsupported; it never checks whether progress happens. [12](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/GRAMMAR.md#L75-L87)

</details>

## Next: ZAL-T and the meaning of “eventually”

A temporal statement is easy to misread once a formula is separated from its assumptions. ZAL-T, a direction beyond the 2.5 release, presents one claim through several views: its formula, its typed meaning, a precise English reading, an intuitive explanation, a plain paraphrase, and a question that exposes any missing premise. The views should clarify one claim, never quietly replace it with another. This section illustrates the idea; it is not a shipped capability.

Consider a request whose matching completion must occur at or after the request:

```text
forall trace in Traces: Environment(trace) =>
  forall request in Requests:
    always(requested(request) => eventually(completed(request)))
```

The same request identity matters throughout: completing a different request is not a witness. The environment premise matters too, because an ongoing liveness guarantee can depend on a scheduler, a keeper, or a remote service continuing to act. A finite replay can illustrate the formula; it cannot prove an infinite environment premise.

For a bounded version, define `within(k, P)` to mean that `P` holds at the current observation or one of the next `k`. The offsets count discrete events, not seconds; a wall-clock deadline also needs a clock model and assumptions relating events to time. A short completed trace without a matching witness fails the bounded requirement. It does not prove the event could never happen in the live system.

These distinctions show what ZAL-T aims to preserve: one declared meaning across notations and explanations. It is separate from the released `.zeno` temporal-claim facility and from the Boolean ZAL prototype. A readable presentation does not by itself establish runtime behavior, authentication, authorization, or deployment authority.

### Example: a withdrawal queue

A useful requirement shape: when a request is admitted and the modeled window is still open, a matching completion is queued within a finite number of events. The claim is conditional on the event source continuing, on request identity being preserved, and on the model's definition of “queued”. It says nothing about delivery, settlement, or elapsed seconds; those are separate outcomes with separate obligations.

## A proposal is not permission

ZenoFCIS separates a **functional core**, which decides, from an **imperative shell**, which acts. Applications supply declarative programs and inputs. The core evaluates each proposed decision against the application's laws; the shell persists the authorized results and delivers their effects. A proposal never authorizes itself. [7](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/ARCHITECTURE.md)

Trust then rests on an evidence chain: the contract, the source revision, the generated artifact, the checks, and the running code, each identified by a hash. Evidence also comes in different strengths, and finite exhaustive checks, attested solver answers, and kernel-checked proofs are recorded as distinct categories. Within the core, the shared executable evaluation, law checking, and Authority operations are formally verified against their stated specifications; the surrounding system keeps obligations of its own. [26](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/verification/verus/authority_v2.rs#L1-L19)

<details id="factory-depth">
<summary>Trace the trust boundary: core, shell, authority, and evidence</summary>

![Candidate generation is separate from checking and refinement]({{ '/assets/images/zenofcis-2-5/figure-15.png' | relative_url }})

*Figure 9. Generate, check, interpret, refine. Proposing candidates can be creative; accepting one is a separate, disciplined step with its own evidence.*

Each handoff raises a concrete review question. Does the contract express the requirement? Does its domain cover the intended inputs? Does the running application use the checked artifact, through the intended interface?

The architecture earns trust by making those handoffs visible and testable. An evidence record should say which specification, source revision, parameters, generated output, and checks belong together. Hashes tie the record's files together; the checks and the runtime binding explain why those files matter.

The pinned architecture document describes the core and the shell in detail. The core works with bounded values and decisions, and Authority operations belong to it. The shell obtains outside inputs, persists authorized results, and delivers effects, under its own assumptions. Dependencies run in rings, from values and canonical encodings through schemas, transitions, laws, synthesis, and evidence, out to authority types and external adapters; lower rings do not import higher ones. [7](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/ARCHITECTURE.md)

The architecture also keeps judgments apart. An exhaustive finite check, an unchecked solver report, and a kernel-checked proof are not interchangeable. In particular, an external solver's “unsatisfiable” answer that is not rechecked is recorded as attested, not as proved. A synthesis result of “no solution” depends on how the search enumerated candidates. The stated trusted base includes interpreters, compilers, target runtimes, and, on the relevant proof route, the Lean kernel and the translation into Lean. [7](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/ARCHITECTURE.md)

The Verus verification unit for Authority imports the actual resource, canonical, evaluation, execution_v2, and value modules. Executable Authority functions carry contracts connecting their results to model transitions, and composed execution connects law evaluation to its specification. This verifies shared executable core code; project laws, adapter contracts, and deployment assumptions govern how an application relies on it. [26](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/verification/verus/authority_v2.rs#L1-L19)

</details>

## From contract to running code

The source-built demonstration uses fictional credits: a balance from 0 to 6, a request from 1 to 3, and an approval flag of 0 or 1, giving **42 inputs**. It accepts exactly when approval is given and at least 2 credits would remain; otherwise it keeps the balance and produces no effect. The tutorial supplies the contract and the sketch explicitly.

![Four steps of the demonstration: a contract with 42 inputs, synthesis after 3 evaluated assignments, a runtime check passing 42 of 42 inputs, and a shell passing 6 of 6 scripted checks]({{ '/assets/images/zenofcis-2-5/figure-demo-handoffs.png' | relative_url }})

*Figure 10. The demonstration as four handoffs. Each leaves its own record, and each record supports a different claim.*

![Actual synthesis transcript with a selected result and first counterexample]({{ '/assets/images/zenofcis-2-5/evidence-source-synthesis.png' | relative_url }})

*Figure 11. The recorded synthesis result: a finite domain of 42 inputs, three evaluated assignments, and a counterexample that rejected an earlier candidate.*

The search rejected a candidate that dipped into the reserve, then selected a valid assignment. Runtime conformance then bound the emitted Python files to the expected artifacts and checked their outputs against the interpreter and the contract on all 42 inputs. The receipt establishes conformance over the complete declared domain and records `authority: none`. [27](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-cli/src/synth/runner.rs#L331-L374)

![Recorded application execution after switching to the checked optimized core]({{ '/assets/images/zenofcis-2-5/evidence-source-app.png' | relative_url }})

*Figure 12. The source-built application running on the checked replacement core, with simulated effects.*

The shell really calls the generated core. It rejects unapproved spending, accepts permitted spending, preserves the reserve, and refuses requests outside the domain. Its effects are simulated, and the approval flag is an input, not authenticated permission.

A separate transformation loop refuted an unsafe edit, accepted an equivalent smaller program, and replayed the result. The accepted replacement was emitted, checked on all 42 inputs, and selected as the module this shell uses. The measured improvement is in representation size, from 10 nodes to 9. The candidate edits were proposed outside the loop; the loop itself made no model calls.

<details id="install-depth">
<summary>Reproduce the source build and published-binary installation</summary>

### Build the exact tool under test

![Actual transcript showing the installed ZenoFCIS version]({{ '/assets/images/zenofcis-2-5/evidence-source-version.png' | relative_url }})

*Figure 13. Recorded transcript: the source-built CLI reports its version.*

The initial recorded run built the source at commit `98da3707af0fb238c4bc1604ea6209382f829dfb` with Rust 1.97.1, using `cargo +1.97.1 build --locked -p zeno-fcis-cli`. The build succeeded and the CLI reported version 2.5.0. This source build is the executable used for the recorded run.

To reproduce it, install Rust 1.97.1 from the official Rust distribution, clone [the project repository](https://github.com/TheDarkLightX/ZenoFCIS), check out the pinned commit, and build with the lockfile:

```sh
git clone https://github.com/TheDarkLightX/ZenoFCIS.git source
cd source
git checkout 98da3707af0fb238c4bc1604ea6209382f829dfb
git rev-parse HEAD
cargo +1.97.1 build --locked -p zeno-fcis-cli
./target/debug/zeno-fcis --version
```

For the finite transformation loop, build the optimized executable with `cargo +1.97.1 build --release --locked -p zeno-fcis-cli` and use `target/release/zeno-fcis`.

That is the source-build record. The published-binary check below is tied to release source `8e9c33e86f376a4431641159a8e5225af9271431`; it is separate evidence and does not replace this demonstration's receipts.

<h3 id="install-published-binary">Install the published 2.5.0 binary</h3>

The official [v2.5.0 release](https://github.com/TheDarkLightX/ZenoFCIS/releases/tag/v2.5.0) was published on 22 October. On an isolated Linux x86-64 host with glibc 2.41, we downloaded its six release assets, verified the signed checksums and the signed tag, installed the binary, and confirmed `zeno-fcis 2.5.0` and `describe`. The CLI then generated a fresh `agent-treasury-guard` template with no application code supplied separately, rejected an unsafe candidate with a counterexample, and selected a Python function after eight assignments. A separate runtime check under Python 3.13.5 passed all 6,144 admitted inputs. [28](https://github.com/TheDarkLightX/ZenoFCIS/releases/tag/v2.5.0)

This adds a real path from download to installation to a generated template. The running budget application and its durable Rust journey remain separate evidence from the source-build demonstration. The release check was deliberately narrow: it did not rerun the 42-input application, the durable-application flow, or the full release acceptance suite. Its receipt says `authority: none`, so it is not evidence of deployment or authorization for a real financial action.

<details id="binary-install-depth">
<summary>Release provenance, replay commands, and compatibility notes</summary>

The release was published at 05:19:21 UTC on 22 October 2026; the recorded commands ran from 06:09 to 06:11 UTC. The tested archive is `x86_64-unknown-linux-gnu`, run on Linux x86-64 with glibc 2.41; the archive requires glibc 2.39 or newer. The release assets included no macOS or Windows binary, so macOS installation remains untested.

- Archive SHA-256: `dd0240e9f114c2e42b24fa8297cc3ef0d31d27ec3d77ed44dd93cbfa7a72b0f6`. Every entry in `DOWNLOADS.sha256` passed, and OpenSSH verified its signature in the `file` namespace.
- The signed `v2.5.0` tag passed Git verification and resolves to source `8e9c33e86f376a4431641159a8e5225af9271431`. The extracted CLI's SHA-256 is `e1d35ca35bd1e0ae11ac3de5d50638f1c13c4020d6c2e2bf3c81bb7be6584004`.
- The signing-key fingerprint `SHA256:dIlSeZjogR21GU3QVYyoBoW2LqLyiUosSLvuEqcFWGw` matched the fingerprint recorded during the earlier 2.4 check. This supports key continuity and the signature check; it is not a fresh, independent, out-of-band authentication of the maintainer's identity.
- The tutorial application's source-build pin is `98da3707af0fb238c4bc1604ea6209382f829dfb`, not this release source; keep its receipts labeled as the source-built run.
- Existing 2.4 contracts and stores need the matching 2.4 CLI and runtime. Re-adopting them under 2.5 creates a new store rather than migrating the old one; this isolated check opened no existing store.
- The emitted-function check establishes agreement with the reviewed relation on those 6,144 admitted inputs. The receipt states `authority: none`, and the template's historical synthesized scalar function is distinct from its normal V2 Authority runtime. It does not qualify the whole generated application or approve a financial action.

<figure>
  <img src="{{ '/assets/images/zenofcis-2-5/release-verification-excerpt.png' | relative_url }}" alt="Excerpt from the recorded 2.5.0 verification log showing successful checksum signature verification and release asset checks." />
  <figcaption>Excerpt from the recorded 2.5.0 installation and verification run.</figcaption>
</figure>

<h4 id="reproduce-published-binary-smoke">Reproduce the download, installation, and synthesis check</h4>

From a fresh Linux x86-64 workspace with glibc 2.39 or newer, fetch the official assets and the matching source, verify them, and run the commands below. Before trusting the signature, compare the release key's fingerprint with the previously recorded value; the `ssh-keygen -lf` line does this.

```sh
mkdir -p downloads bin evidence
base=https://github.com/TheDarkLightX/ZenoFCIS/releases/download/v2.5.0
for file in DOWNLOADS.sha256 DOWNLOADS.sha256.sig RELEASE-SIGNING-KEY.pub SBOM.cdx.json zeno-fcis-2.5.0-x86_64-unknown-linux-gnu.tar.gz zeno-fcis-rustdoc-2.5.0.tar.gz; do
  curl --fail --location --silent --show-error "$base/$file" -o "downloads/$file"
done
test "$(ssh-keygen -lf downloads/RELEASE-SIGNING-KEY.pub | cut -d' ' -f2)" = SHA256:dIlSeZjogR21GU3QVYyoBoW2LqLyiUosSLvuEqcFWGw
printf 'TheDarkLightX ' > allowed-signers
cat downloads/RELEASE-SIGNING-KEY.pub >> allowed-signers
ssh-keygen -Y verify -f allowed-signers -I TheDarkLightX -n file -s downloads/DOWNLOADS.sha256.sig < downloads/DOWNLOADS.sha256
(cd downloads && sha256sum --check DOWNLOADS.sha256)
git clone --depth 1 --branch v2.5.0 https://github.com/TheDarkLightX/ZenoFCIS.git source
test "$(git -C source rev-parse HEAD)" = 8e9c33e86f376a4431641159a8e5225af9271431
git -C source -c gpg.ssh.allowedSignersFile="$PWD/allowed-signers" verify-tag v2.5.0
tar -xzf downloads/zeno-fcis-2.5.0-x86_64-unknown-linux-gnu.tar.gz -C bin
cli=bin/zeno-fcis-2.5.0-x86_64-unknown-linux-gnu/zeno-fcis
"$cli" --version
"$cli" describe
"$cli" new generated-treasury --template agent-treasury-guard --source "$PWD/source"
"$cli" synth run generated-treasury/synthesis.json --target python --out synthesized-python
"$cli" synth verify generated-treasury/synthesis.json --target python --out synthesized-python --tool /usr/bin/python3 --receipt evidence/python-conformance.json
```

The evidence bundle keeps six numbered logs: download, source checkout, signature and hash verification, extraction and `describe`, template creation and synthesis, and runtime conformance. `record.py` only records transcripts; it is not application logic. The bundle deliberately omits the downloaded binary, the full source checkout, and the toolchains. To regenerate, use a fresh checkout so the template can find its source tree.

</details>

</details>

<details id="app-depth">
<summary>Go deeper: every handoff from contract to application</summary>

### A contract that demands useful behavior

The admitted input is `(balance, request, approved)`, so there are 7 × 3 × 2 = 42 input tuples. The reserve is 2 fictional credits.

Accept if and only if approval is 1 and balance minus request is at least 2. On acceptance, subtract exactly the request and ask for one simulated effect. On rejection, keep the balance and ask for no effect. The wrapper must refuse values outside the declared domain.

The phrase “if and only if” matters. A program that rejects everything never overspends, but it fails this contract: with balance 6, request 2, and approval 1, acceptance is required. The positive obligation stops “safe” from meaning “does nothing”.

The supplied sketch has four possible assignments: a reserve of 0 or 2, and either honoring or bypassing approval. The search is small enough to inspect by eye. The check relates the emitted program to the supplied contract; whether that contract captures the intended behavior is a question for reviewing the contract itself.

### A counterexample rejects the wrong candidate

From the demonstration directory, the recorded command was:

```sh
zeno-fcis --no-kb synth run app/budget.json --target python --out app/generated-python
```

The result was `selected`, with `semantic: complete-finite` and `input_coverage: 42`, after evaluating three assignments. The recorded first counterexample was input `[1,1,1]` with candidate output `[1,0,1]`: accept a one-credit request from a balance of 1, leave 0, and request an effect. That breaks the two-credit reserve.

The emitted artifacts include `transition.py`, the encoded program, test vectors, and a manifest linking their identities. The output says `authority: none` and, at first, `runtime_conformance: not-run`. Selecting a program is one milestone; checking the emitted function at runtime is another.

### Check the exact emitted function

```sh
zeno-fcis --no-kb synth verify app/budget.json --target python --out app/generated-python --receipt evidence/python-conformance.json
```

This run returned `status: passed` and `inputs_checked: 42`. The stated claim is that the exact emitted function agrees with the interpreter and the reviewed relation on every admitted input, where “reviewed relation” names the relation supplied in the receipt. The recorded runtime was Python 3.12.14. The receipt's identity scope leaves dynamic dependencies and compiler correctness as explicit external premises, and it records `authority: none`.

### Call the checked function from a small shell

The application starts at a balance of 6. An unapproved request for 2 is rejected, leaving 6. An approved request for 2 is accepted, leaving 4. A request for 3 is then rejected because it would breach the reserve. An approved request for 2 leaves exactly 2. Further spending is rejected, and a request for 99 is refused as outside the admitted domain. All six scripted checks passed.

The tutorial's shell is a small wrapper written for this demonstration, not synthesized by ZenoFCIS; it imports the generated `transition.py` and takes the approval flag as input. The tests below exercise its behavior. The project's V2 Authority and durable SQLite shell are separate components; this example uses a small local wrapper so the call into the generated function is easy to inspect.

Additional tests checked all 42 tuples against a separately written restatement of the rule, ten malformed or out-of-domain inputs, all 1,296 request-and-approval sequences of length four from the starting balance, and three deliberately faulty variants. Concrete inputs refuted each faulty variant: reject-all, bypass-approval, and drop-reserve. These tests are useful corroboration, but the restatement was prepared in the same session as the tutorial and could share a mistaken reading.

JavaScript emission was checked too. The first attempt refused Node 24, because the supported runtime was Node 22. After installing the required Node 22.23.1, the same 42-input conformance check passed. The evidence keeps the initial refusal alongside the successful run on the qualified runtime.

</details>

<details id="repair-depth">
<summary>Why a smaller program still needs a check</summary>

A candidate is useful only if it preserves the contract. In the educational source-build run, a deliberately unsafe edit accepted a request that would breach the fictional reserve, and the checker produced a concrete witness. A later candidate removed a redundant expression while preserving the same finite relation.

The lesson does not depend on the search tool: being smaller says nothing about being equivalent. Check the candidate against the reviewed relation on the declared domain, then bind the checked artifact to the code the application actually calls. This experiment belongs to the source build, not to the separate release-binary check.

</details>

## A correct rule still needs a secure path

Tau Language supports logical specifications, reactive synthesis, an interpreter, and ahead-of-time compilation. ZenoFCIS's optional Tau bridge accepts finite pointwise specifications, and Tau Network provides a broader distributed setting for the complementary architecture discussed below. [8](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/README.md), [9](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TAU_KIT.md), [10](https://tau.net/), [11](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/LICENSE.md)

For agent security, a correct decision gate helps only if privileged actions cannot bypass it and untrusted input cannot rewrite its policy. Least privilege, authentication, protected configuration, controlled effects, and audit records are separate obligations. A checked reserve rule does not make data honest or delivery reliable.

<details id="tau-depth">
<summary>Where Tau connects, and what the bridge refuses</summary>

Tau Language offers a declarative way to express relationships between inputs and outputs over time, with facilities for reasoning and reactive synthesis. Its current source documents both an interpreter and ahead-of-time generation and compilation through `tau gen` and `tau compile`. A comparison that casts Tau as an interpreter and ZenoFCIS as a compiler misses the real overlap. [8](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/README.md)

The useful comparison is where each places the boundary. Tau emphasizes executable logical specifications and temporal relationships. ZenoFCIS emphasizes bounded decision construction, explicit evidence categories, and an FCIS authority path between proposed decisions and effects. Both need a precise account of semantics, supported fragments, trusted implementations, and what failure means. Tau's documented compilation covers a subset of interpreter behavior, and some searches have caps. Reaching a cap, or returning UNKNOWN, proves nothing about the proposition. [7](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/ARCHITECTURE.md), [8](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/README.md)

The ZenoFCIS source already has a restricted bridge. Its optional Tau kit imports a complete pointwise decision ladder through the native contract compiler. Generic import accepts flat scalar records, fixed streams, current-time projections, same-width unsigned comparisons, Boolean operations, and modular addition or subtraction, within documented width bounds. Temporal history and future constructs, among many others, are refused. Together these rules define the fragment the bridge supports. The native representation adds a zero genesis state, diagnostic rejection reasons, and a state-domain law. [9](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TAU_KIT.md)

Export produces per-rule queries and deterministic samples of native Authority decisions; export alone runs neither Tau nor SMT. A separate local runner checks pinned executable hashes, keeps transcripts, requires Tau and the paired SMT results to agree, and includes negative controls. Timeouts, errors, unknown results, or disagreement leave the run incomplete. The documentation classes a successful run as attested evidence about those queries. It is not kernel-checked proof, authentication, authorization, or whole-domain replay. The Tau revision the kit supports is distinct from the current Tau source used for the capability comparison. [9](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TAU_KIT.md)

Scaling a 256-bit source down to a three-bit study domain also changes the question. The small version supports an experiment, not equivalence over the original 256-bit domain. The same caution applies whenever a demonstration becomes tractable by narrowing its inputs.

Tau Network is a broader proposed distributed setting, not another name for Tau Language. Its official site describes rule-chain, wallet, and agent-account directions, presents a waitlist, and distinguishes the ERC-20 placeholder from the described mainnet features. This section examines the documented pointwise bridge and one possible network composition. [10](https://tau.net/)

A plausible complementary architecture would let participants express and examine policy in an agreed Tau fragment, translate the supported part into a native ZenoFCIS contract, check both sides against pinned artifacts, and admit the policy through the application's authority boundary. A network adapter would then supply authenticated observations and submit authorized effects. This composition is a proposal that builds on the documented pointwise bridge.

The hard work is at the joins: preserving meaning during translation, authenticating observations, handling replay and finality, bounding stale oracle data, and delivering effects safely. Tau also has a custom license, whose terms need review before redistribution or deployment. [11](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/LICENSE.md)

</details>

<details id="security-depth">
<summary>A correct gate still needs an unbypassable path</summary>

![Nested rings: the verified core inside the surrounding system and its environment, with bridge obligations on the core's boundary]({{ '/assets/images/zenofcis-2-5/figure-24.png' | relative_url }})

*Figure 14. Inside the boundary, verified components meet their stated specifications. Outside it, and at the bridges into it, other obligations remain.*

An agent can choose actions, but a separate enforcement boundary should decide which actions are permitted. The separation matters most when the agent reads untrusted documents, web pages, messages, or tool outputs, any of which may carry instructions meant to redirect it.

A decision gate can check a narrow property, such as “this modeled action must leave the simulated reserve at or above the stated threshold”. If the domain, arithmetic, and implementation are right, that property is useful. It does not show that the action is wise, that a price feed is honest, that a remote service will honor the request, or that every route to execution passes through the gate.

For security, ask where the authority lives. If the agent can bypass the gate and call a privileged API directly, a correct gate secures nothing. If an untrusted message can rewrite the contract, the checker will faithfully enforce the attacker's policy. If secrets leak into logs or side channels, a budget invariant does not protect them.

A practical defense therefore pairs a small checkable policy with an enforcement design: least privilege, explicit authorization, protected configuration, input validation, controlled tool access, audit records, and a safe failure path. Each contributes a different assurance. None of them should be quietly credited to arithmetic synthesis.

A proof is best read as a carefully scoped conditional: under these assumptions and this semantics, this artifact has this property. Better security comes from proving useful conditions and shrinking the unchecked assumptions those proofs depend on.

</details>

## Where this leads

One direction beyond 2.5 is an examples-first path from intent to a reviewed contract: make the proposed rules explicit, ask questions that separate competing interpretations, test the supplied examples, and only then build the application around the contract. Each stage needs its own evidence. Passing examples does not show complete coverage, and generating code does not show that the contract captured the intended requirement.

The synthesis walkthrough above already shows these layers: a counterexample rejects an unsafe candidate, an exact runtime check establishes agreement over a declared finite domain, and the shell still needs its own authorization, persistence, and delivery checks. Future work should keep each handoff reviewable, so that a readable paraphrase never implies stronger evidence than the checked artifact supplies.

### What to carry forward

- **Zeno:** approaching a value is not arriving at it.
- **Goodstein:** a simple rule can need strong mathematics to show where it ends.
- **Encoding:** representing a computation is not answering every question about it.
- **Abstract machines:** defining a power does not build it.
- **Synthesis:** search proposes candidates; a check over a stated domain decides.
- **Temporal claims:** safety is not progress, and where a trace ends changes what is true.
- **Architecture:** a proposal is not permission, and every guarantee holds only within its stated scope.

## Sources and further reading

The references below point to primary papers, public project documentation, and the official release record.

<details id="sources-depth">
<summary>Read the primary papers and public implementation sources</summary>

1. Aristotle, *Physics* VI.9, Hardie and Gaye translation. [Ancient account of Zeno](https://classics.mit.edu/Aristotle/physics.6.vi.html).
2. R. L. Goodstein, “On the Restricted Ordinal Theorem,” *Journal of Symbolic Logic* 9 (1944), 33–41. [Original paper](https://fa.ewi.tudelft.nl/~hart/37/onderwijs/verzamelingenleer/materiaal/goodstein.pdf).
3. L. Kirby and J. Paris, “Accessible Independence Results for Peano Arithmetic,” *Bulletin of the London Mathematical Society* 14 (1982), 285–293, Theorem 1. [Primary paper](https://www.cs.tau.ac.il/~nachumd/term/Kirbyparis.pdf).
4. A. M. Turing, “On Computable Numbers, with an Application to the Entscheidungsproblem,” §§5–6, especially printed p. 241. [Primary paper](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf).
5. R. Alur et al., “Syntax-Guided Synthesis,” FMCAD 2013. [Primary paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2013/05/fmcad13.pdf).
6. C. A. R. Hoare, “An Axiomatic Basis for Computer Programming,” *Communications of the ACM* 12 (1969), 576–580, §2. [Primary paper](https://www.cs.cmu.edu/~crary/819-f09/Hoare69.pdf).
7. ZenoFCIS, *Architecture*, 2.5.0 release source. [Architecture and evidence categories](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/ARCHITECTURE.md).

8. Tau Language, README at revision dad02cdbdd239f5b169e1256045c57d8f7efca3d. [Interpreter synthesis compilation and current limits](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/README.md).
9. ZenoFCIS, *Optional finite Tau kit*, pinned 2.5 source. [Supported translation and evidence boundaries](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TAU_KIT.md).
10. Tau, official product website, accessed 23 October 2026. [Network direction and stated availability](https://tau.net/).
11. Tau Language, license at the inspected revision. [Applicable license text](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/LICENSE.md).

12. ZenoFCIS, optional ZAL finite-FSM research prototype, outside the released API. [Prototype README](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/README.md); [grammar and controlled-English pairing](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/GRAMMAR.md).
13. ZenoFCIS, *Temporal logic version 1*. [Temporal modes and operator semantics](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TEMPORAL_LOGIC_V1.md).

14. ZenoFCIS, current CLI Lean routing. [UnsupportedMode in the inspected source](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-cli/src/main.rs#L1360-L1405).

15. [M. O. Rabin and D. Scott, “Finite Automata and Their Decision Problems” (1959)](https://doi.org/10.1147/rd.32.0114).

16. [M. Minsky, “Recursive Unsolvability of Post’s Problem of Tag and Other Topics in Theory of Turing Machines” (1961)](https://www.wolframscience.com/prizes/tm23/images/Minsky.pdf).

17. [A. Church, “An Unsolvable Problem of Elementary Number Theory” (1936)](https://www.cis.upenn.edu/~cis5110/Church-UnsolvableProblemElementary-1936.pdf).

18. [A. M. Turing, “Systems of Logic Based on Ordinals” (1939)](https://people.math.ethz.ch/~halorenz/4students/Literatur/TuringOrdinalLogic.pdf).

19. [J. D. Hamkins and A. Lewis, “Infinite Time Turing Machines”](https://arxiv.org/html/math/9808093).

20. [R. W. Floyd, “Assigning Meanings to Programs” (1967)](https://www.lem12.uksw.edu.pl/images/1/15/AssigningMeanings1967.pdf).

21. [W. A. Howard, “The Formulae-as-Types Notion of Construction” (1980)](https://www.cs.cmu.edu/~crary/819-f09/Howard80.pdf).

22. [P. Martin-Löf, Intuitionistic Type Theory (1984), notes by Giovanni Sambin](https://www.cs.cmu.edu/~crary/819-f09/Martin-Lof80.pdf).

23. Guy Frankel, Rudi Schneider, Michel Steuwer, and Elizabeth Polgreen, “Syntax-Guided Synthesis with Counterexample-Guided E-graphs: A Work-in-Progress Report,” SMT 2025, pp. 77–90. [Primary paper](https://ceur-ws.org/Vol-4008/SMT_paper11.pdf).
24. Guy Frankel, Rudi Schneider, Michel Steuwer, and Elizabeth Polgreen, “Synthesis with Counterexample Guided Observational Equivalence Graphs,” FMCAD 2026, pp. 349–361. [Published paper record and full text](https://repositum.tuwien.at/handle/20.500.12708/230505).

25. Martin Berger, Nathanaël Fijalkow, and Mojtaba Valizadeh, “GPU accelerated program synthesis: Enumerate semantics, not syntax!”, arXiv:2504.18943v1 (26 April 2025). [Versioned paper](https://arxiv.org/html/2504.18943v1).


26. ZenoFCIS, shared executable-core verification. [Verus verification-unit imports](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/verification/verus/authority_v2.rs#L1-L19); [executable evaluation contracts](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-synthesis/src/finite/execution_v2/authority/bound.rs#L123-L135).

27. Public synthesis and runtime conformance. [Finite synthesis](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-synthesis/src/finite/mod.rs#L695-L849); [canonical assignment search](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-synthesis/src/lib.rs#L421-L488); [emission and exact-artifact verification](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-cli/src/synth/mod.rs#L182-L340); [complete-domain output validation](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-cli/src/synth/runner.rs#L331-L374).

28. ZenoFCIS, official v2.5.0 release metadata and assets. [Signed release page](https://github.com/TheDarkLightX/ZenoFCIS/releases/tag/v2.5.0).

</details>
