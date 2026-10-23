---
title: "ZenoFCIS 2.5: From Requirements to Verified Programs"
description: "How abstraction, synthesis, and proof turn intent into working software."
og_title: "ZenoFCIS 2.5: From Requirements to Verified Programs"
kicker: "Tutorial 77"
layout: docs
---

A requirement becomes useful software only when its meaning is explicit and the resulting behavior can be checked. This tutorial moves from mathematical models to bounded synthesis, runtime conformance, and the evidence needed at the boundary of an application.

**Release scope.** ZenoFCIS 2.5.0 was officially released on 22 October 2026. This tutorial keeps two records distinct: an educational application built from a public development source revision, and a separate check of the signed 2.5.0 Linux release binary.

Read the main path first, then expand the examples, proofs, and evidence notes as useful.

## A limit is not a stopping condition

![A geometric sequence approaches one while Goodstein seed 3 reaches zero]({{ '/assets/images/zenofcis-2-5/figure-01.png' | relative_url }})

*Figure 1. Convergence asks about a limit. Termination asks whether a stopping condition is reached after finitely many transitions.*

Walking halfway to a wall, then half the remaining distance, gives 1/2, 3/4, 7/8, … . After n steps the position is 1−2⁻ⁿ. It approaches 1 but never equals it in exact arithmetic. A tolerance-based stopping rule can finish; “wait until exactly 1” cannot.

A sequence is an ordered family of values. A program generates a sequence of states, but a simple next-step rule need not make its long-term behavior easy to prove.

<details id="zeno-depth">
<summary>Go deeper: the limit exists even when the loop never ends</summary>

Aristotle, reporting Zeno's argument, says the moving thing “must arrive at the half-way stage before it arrives at the goal.” This is Aristotle's account in *Physics* VI.9, not a quotation recovered directly from Zeno. [1](https://classics.mit.edu/Aristotle/physics.6.vi.html)

Imagine walking halfway across a room, then half the remaining distance, then half again. The successive positions are 1/2, 3/4, 7/8, 15/16, and so on, if the far wall is at 1. Every position falls short. Nevertheless, the distance left over becomes as small as we please.

The calculation is elementary: after n steps the position is 1 − 2⁻ⁿ. Given any positive tolerance ε, enough steps make 2⁻ⁿ smaller than ε. The sequence converges to 1.

That calculation resolves a question about the limit of a mathematical sequence. It does not say that a computer executing “repeat forever” eventually finishes. A program that stops when the remaining distance is less than ε can terminate; one that waits for this exact sequence to equal 1 never does in exact arithmetic. Floating-point rounding is a different model, not a proof that the infinite sequence reached its limit.

A sequence is simply an ordered family of values. Formally, a sequence indexed by natural numbers is a function a: ℕ → X. Its values might be distances, integers, program states, requests, or security decisions. A recurrence specifies a next value from earlier values. A program may generate the sequence, but knowing how to generate it need not make its global behavior easy to prove.

An arbitrary mathematical sequence need not have a computable generating rule. For a program execution, we normally track a complete state and a transition rule, not just the values displayed on screen. Interactive programs may have many possible traces depending on their inputs.

</details>

## Growing numbers, descending proof

Goodstein sequences repeatedly rewrite a number in hereditary base notation, raise the base everywhere, and subtract one. Starting at 4 gives 4, 26, 41, 60, … . Yet every standard Goodstein sequence reaches zero.

The proof tracks a decreasing ordinal while the ordinary number may grow. That ordinal is a proof measure, not infinite physical storage. The uniform termination theorem is unprovable in first-order Peano arithmetic, assuming consistency. This particular independence result needs its own proof; it does not follow merely from PA’s undecidability. [2](https://fa.ewi.tudelft.nl/~hart/37/onderwijs/verzamelingenleer/materiaal/goodstein.pdf), [3](https://www.cs.tau.ac.il/~nachumd/term/Kirbyparis.pdf)

<details id="goodstein-depth">
<summary>Follow 4 to 26, then follow the descending ordinal</summary>

Start with a natural number and express it in hereditary base 2. “Hereditary” means that the exponents are written in the same base, and their exponents too, recursively. Replace every occurrence of the base by 3 and subtract one. Repeat, raising the base each time.

The sequence starting at 4 begins 4, 26, 41, 60, 83. Its first transformation explains why. In full hereditary base 2, 4 is 2^(2^1). Replacing the base everywhere produces 3^(3^1) = 27. Subtracting one gives 26. This is not ordinary positional base conversion: ordinary conversion preserves a number's value. Goodstein's operation changes the expression's value.

For a complete small example, start at 3. The sequence is 3, 3, 3, 2, 1, 0, with successive bases 2, 3, 4, 5, 6, 7. The first three displayed values are equal, but the full state is different because the base changes. Forgetting that base would lose information needed to compute the next step.

The numbers may grow dramatically, yet every standard Goodstein sequence eventually reaches zero. The insight is to track a different measure. Replace the changing finite base in the hereditary representation by the first infinite ordinal, ω. The associated ordinal decreases at every step, even when the ordinary integer grows. There is no infinite strictly decreasing sequence of ordinals. For the prefix above, the first shadows are ω^ω, then ω²·2 + ω·2 + 2, then ω²·2 + ω·2 + 1. The coefficients belong on the right: ordinal multiplication is not commutative. Here ω is an ordinal, not a very large ordinary integer. [2](https://fa.ewi.tudelft.nl/~hart/37/onderwijs/verzamelingenleer/materiaal/goodstein.pdf), [3](https://www.cs.tau.ac.il/~nachumd/term/Kirbyparis.pdf)

Kirby and Paris proved that, assuming Peano arithmetic is consistent, the uniform Goodstein theorem is not provable in that theory. This independence result is distinct from PA’s undecidability: one concerns a specific theory and statement; the other concerns deciding every sentence.

*The ordinal is a proof measure, not a physical storage requirement. The two rows do not share a numerical scale.*

Goodstein's process starts with a finite integer and uses effective finite steps. Its proof tracks an ordinal-valued measure whose descent explains why the arithmetic process cannot continue forever. The ordinal is part of the reasoning; the arithmetic program does not need an oracle that stores an infinite quantity and consults it at runtime. Finite symbolic ordinal expressions can themselves be manipulated as syntax, while the well-foundedness argument supplies the mathematical justification. [2](https://fa.ewi.tudelft.nl/~hart/37/onderwijs/verzamelingenleer/materiaal/goodstein.pdf), [3](https://www.cs.tau.ac.il/~nachumd/term/Kirbyparis.pdf)

Even here, checking a supplied finite proof and finding one are different tasks. In an ordinary effective proof calculus, a proposed PA proof can be checked mechanically; searching for a proof of an arbitrary sentence may never finish. For any fixed start, the standard Goodstein run terminates and its finite trace can in principle be checked.

</details>

## A program is more than its code

Encoding represents a program’s syntax as numbers. Semantics describes what it does. A specification states what it should do. An invariant is proved to hold in every reachable state; when it implies a safety property, it establishes that property, not termination.

Curry–Howard adds another connection: in suitable typed calculi, propositions correspond to types and proofs to terms. A function’s type can include evidence that its result equals n². Ordinary “number to number” typing does not say that, and arbitrary nonterminating code is not automatically a proof. This correspondence connects the structure of a program to the structure of a proof. [20](https://www.lem12.uksw.edu.pl/images/1/15/AssigningMeanings1967.pdf), [21](https://www.cs.cmu.edu/~crary/819-f09/Howard80.pdf), [22](https://www.cs.cmu.edu/~crary/819-f09/Martin-Lof80.pdf)

Turing’s universal machine computes “any computable sequence.” Universality means it can interpret encoded machines, not answer every question about them. [4](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)

<details id="logic-depth">
<summary>Unpack the logic: invariants, Curry–Howard, and universality</summary>

A program is structured text with an interpretation. Before discussing clever synthesis, imagine a very mundane encoding. Assign each token an integer, include delimiters or lengths, and encode the resulting finite sequence as a natural number. More sophisticated encodings preserve syntax trees and binding structure. Either way, finite programs can be represented by numbers.

### From representations to semantics and logic

Numerical encoding is one mathematical view of a program, not the whole process. We can also give the program a semantics: a function, a state-transition system, or a set of permitted execution traces. Logic then states properties of that behavior. The representation, the behavior, and the property are related objects, but they are not interchangeable.

An invariant is a predicate on program states. An invariant map can attach an assertion to each control-flow location: what must be true of the stored values whenever execution reaches that point. Formally, it can be a map from locations to predicates on stores, A: Location → (Store → Prop). Floyd's foundational treatment assigns propositions to control-flow connections and checks the obligations created by the commands between them. This makes the program's logical structure visible rather than merely assigning its text a number. [20](https://www.lem12.uksw.edu.pl/images/1/15/AssigningMeanings1967.pdf)

For a transition system, an inductive invariant I must hold initially and be preserved by every permitted transition. If I also implies the desired safety property, induction on execution length establishes that property for every reachable state. In the square loop developed below, the loop-head assertion is 0 ≤ i ≤ n and s = i². Initialization, preservation, and the exit condition prove the result; the decreasing measure n−i supplies the separate termination argument. Hoare logic organizes this kind of reasoning around preconditions, commands, and postconditions. [6](https://www.cs.cmu.edu/~crary/819-f09/Hoare69.pdf)

The Curry–Howard correspondence supplies another connection. In suitable typed calculi, propositions correspond to types, and proofs correspond to terms inhabiting those types. A proof of “A implies B” behaves like a function that takes evidence for A and constructs evidence for B. Function application corresponds to using the implication. This is a relationship between structures of reasoning, not merely an encoding of symbols. [21](https://www.cs.cmu.edu/~crary/819-f09/Howard80.pdf)

An ordinary type “natural number to natural number” still does not say that a function computes a square. A dependent specification can state: for each natural n, produce a natural result r together with evidence that r=n². The claim is now part of the type, rather than an informal comment. That is propositions-as-types at work. A connection to an imperative implementation still needs to be established through its semantics. [22](https://www.cs.cmu.edu/~crary/819-f09/Martin-Lof80.pdf)

The rules of the proof system matter. Arbitrary nonterminating programs are not automatically proofs, and ordinary type checking does not establish an unstated requirement. Proof fragments need appropriate termination or normalization disciplines, or an explicit account of partiality and effects. Assumptions, admitted holes, and the trusted checker remain part of the assurance boundary. We can mechanize checking a supplied proof without thereby solving the harder problem of finding one.

### Universality and representation

Turing wrote in 1936: “It is possible to invent a single machine which can be used to compute any computable sequence.” The qualifier *computable* matters. His universal machine interprets encoded descriptions; it does not solve every question about the machines described. [4](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)

</details>

## An ideal machine is not yet a mechanism

An abstract machine specifies states, transitions, and observable results. Finite automata, counter machines, and lambda calculus expose different structures. An unbounded Turing tape has no fixed storage ceiling, but each finite run visits only finitely many cells.

We can also define oracle or infinite-time machines. Defining their extra power does not implement it. Their practical value is to clarify assumptions and guide realizable restrictions. [15](https://doi.org/10.1147/rd.32.0114), [16](https://www.wolframscience.com/prizes/tm23/images/Minsky.pdf), [17](https://www.cis.upenn.edu/~cis5110/Church-UnsolvableProblemElementary-1936.pdf), [18](https://people.math.ethz.ch/~halorenz/4students/Literatur/TuringOrdinalLogic.pdf), [19](https://arxiv.org/html/math/9808093)

Our proposed **Edwards Contract Machine** makes this bridge explicit: accept a candidate p only when it meets relation R on every input in domain X. This defines success, not an algorithm or progress guarantee. A realizable version searches a finite candidate set and checks a finite domain D. Success covers D; exhaustion says only that this search found no solution, not that none exists elsewhere.

A standalone Python example finds t=min(a,max(r,0)) for transferring fictional credits between nonnegative balances. Finite checks establish its bounded behavior; a separate proof covers arbitrary integer requests under those balance preconditions. The search and its checks are available in the accompanying standalone example.

<details id="machines-depth">
<summary>Build the Edwards machine: specification, finite search, and proof</summary>

Turing's machine is one way to make computation precise. More generally, an abstract machine specifies its possible states, its legal transitions, its inputs, and what counts as an observable result. If we want to compare efficiency, we also need a cost model. These choices define a mathematical object, not necessarily a blueprint for physical hardware.

A finite automaton remembers only which of finitely many states it occupies. Two states are enough to remember whether the number of 1s read so far is even or odd: reading 1 switches states; reading 0 leaves the state unchanged. Its limited memory makes some tasks impossible, but also makes many questions about its behavior manageable. The restriction is part of its usefulness. [15](https://doi.org/10.1147/rd.32.0114)

A counter machine looks different. A finite program increments natural-number counters, tests for zero, and decrements and branches. Suitable counter-machine models can compute what a Turing machine computes. The tape has disappeared from the description, but unbounded storage has moved into the counters. Computational power and the appearance of the notation are different matters. A unit-cost instruction on an arbitrarily large number also need not correspond to one cheap physical operation. [16](https://www.wolframscience.com/prizes/tm23/images/Minsky.pdf)

Church's lambda calculus offers another presentation: computation through expressions and substitution. It is a computational formalism rather than literally a tape machine; an evaluator can give those expressions a machine semantics. Comparing such models helps us distinguish a change in notation from a change in what can be computed. [17](https://www.cis.upenn.edu/~cis5110/Church-UnsolvableProblemElementary-1936.pdf)

The unbounded tape deserves a careful reading. It imposes no fixed storage ceiling on the mathematical model. It does not mean that a finite Turing-machine computation visits infinitely many cells. Every finite run uses only finitely much tape, so a sufficiently provisioned finite device can simulate that run. What no single fixed storage allowance supplies is room for every possible run. The idealization can therefore be useful without being literally instantiated in its entirety. [4](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf)

### What happens when we strengthen the assumptions

We can invent stronger abstract machinery. Give a machine an oracle that answers whether an ordinary Turing machine eventually halts. Relative to that oracle, the ordinary halting question is decidable. The definition is mathematically meaningful, but it has placed the difficult power in an assumption. It has not built the oracle. Oracle machines make dependencies explicit, and they have their own further undecidable questions. [18](https://people.math.ethz.ch/~halorenz/4students/Literatur/TuringOrdinalLogic.pdf)

Infinite-time Turing machines offer another disciplined example. Their computations can pass through ordinal-indexed stages, and their definition supplies rules for what happens at limit stages. That extra semantics is essential. Saying that successive steps take 1/2, 1/4, 1/8, and so on gives a convergent sum of durations, but does not tell us what machine state exists at the limit or how an observer could obtain its answer. The theory of infinite-time machines specifies a mathematical model; it is not, by itself, a demonstrated engineering design. [19](https://arxiv.org/html/math/9808093)

This brings us back to Zeno without requiring us to reject abstraction. A geometric limit, an infinite-time transition rule, and a physically observable computation are three distinct objects. We can study each, provided we say which one supplies our conclusion. Turing's analysis of effective computation does not by itself prove every imaginable physical hypercomputer impossible. Equally, naming an oracle or postulating infinitely many stages does not establish a working physical hypercomputer.

### An Edwards machine for making the bridge explicit

*The Edwards Contract Machine is a teaching construction introduced here. The ideal relation defines success; the finite procedure explains one way to search for it.*

Let us invent an Edwards machine to make the bridge concrete. Give it a contract consisting of an input domain X, an output domain Y, a family P of total candidate programs, and a relation R(x,y) saying which outputs are acceptable. Its ideal transition is simple to state: from “ready with this contract” to “done with program p,” provided p belongs to P and R(x,p(x)) holds for every x in X.

That is a specification relation, not yet an algorithm. It tells us what a successful transition means. It does not tell us how to find a valid program, guarantee that a transition occurs, or decide that no program exists. Even the totality of every candidate is an assumption of this ideal model, not something automatically decidable for arbitrary code.

We can build a finite version. Choose a finite set G of candidates, for example from a grammar with an explicit syntax-tree size bound, and a finite domain D. Try each candidate and check every input in D. Return a candidate only after it passes them all; otherwise return UNKNOWN. Because the search space, domain, and individual evaluations are finite and terminating, this procedure terminates.

The scope determines what the result means. If D is the whole intended task domain X, a successful result satisfies that whole finite contract. If D is only a sample of an infinite X, it establishes only the restriction to D. Exhausting G says nothing about candidates outside G. The finite procedure implements a bounded contract that permits UNKNOWN; it is not an oracle promising to solve every synthesis problem.

For a working example, use fictional balances. A source has a ≥ 0 credits, a destination has b ≥ 0, and r is a signed request. A nonpositive request should transfer nothing. A positive request should transfer the requested amount if available, otherwise all that remains. Search expressions built from a, r, zero, min, and max.

The executable example found:

```text
t = min(a, max(r, 0))
a_next = a - t
b_next = b + t
```

The recorded finite search checked the complete 126-pair domain a=0,…,8 and r=−3,…,10 and found a satisfying expression in the five-node grammar. A smaller three-node grammar returned UNKNOWN. A separate finite check verified behavior, nonnegative balances, and conservation over 1,134 balance/request combinations. These results come from the accompanying standalone Python example.

We can also prove something beyond those tests, by a separate argument. Since a and max(r,0) are nonnegative, 0 ≤ t ≤ a. If r ≤ 0, t=0; if 0 < r ≤ a, t=r; if r > a, t=a. Therefore the requested behavior holds for every mathematical integer input satisfying the preconditions. Moreover, (a−t)+(b+t)=a+b, and both resulting balances remain nonnegative. This universal conclusion comes from the case analysis, not from extrapolating 126 checks. The Python script is not a proof assistant certifying this general argument, and fixed-width arithmetic would need its own overflow conditions.

Why not strengthen the Edwards machine to always return a correct program or correctly report that none exists? That would be a new assumption. For example, let the only candidate return zero, and let its requirement at n say that some given ordinary machine has not halted in its first n steps. Each individual check is finite. Deciding whether this candidate satisfies the requirement for every n would decide whether that machine ever halts. A universally correct, always-terminating oracle for these contracts would therefore exceed ordinary effective computation. Defining it does not implement it.

</details>

## A shared object of thought

My aim with the Zeno Abstraction Language is to help a human and a machine work on the same object of thought. We should be able to point to a condition, a state transition, an assumption, or a claim about eventual progress, and ask whether we mean the same thing. The useful meeting point is the abstraction itself: something both sides can inspect, question, and refine.

Controlled language is one interface into this machinery, not its whole identity. Controlled languages can themselves have formal semantics and support multiple views; the distinction here is ZAL’s emphasis on a shared abstraction as the central object. The ambition is not simply to restrict English until a parser accepts it. A formula can expose a quantifier that a sentence leaves implicit. A typed view can reveal that two uses of “balance” have different meanings. A plain-language view can reveal that a technically consistent formula says something nobody wanted. Different views help us examine a common declared model from different directions.

Think of the model as a shared workbench. The human can ask, “Does this mean every request must eventually complete?” The machine can identify the request domain, the completion predicate, and the missing environment assumption. A counterexample can then show exactly where the proposed meaning differs from the intended one. The exchange changes the shared artifact, rather than relying on confidence that two opaque interpretations happen to match.

Human and machine need not reason identically; they need a stable object, explicit views, and a way to expose disagreements before deployment.

ZAL makes this aim concrete through symbolic, typed, and language views of an explicit model. Deterministic renderings keep the declared proposition stable while changing how we inspect it. The shared model gives interpretation review a concrete object: we can examine definitions, assumptions, and counterexamples together.

## Search builds possibilities

In program synthesis, we supply a **specification** of acceptable behavior and a **language of allowed programs**; the synthesizer searches that language. A specification may be examples, logical conditions, or both; examples alone can leave several answers possible. [23](https://ceur-ws.org/Vol-4008/SMT_paper11.pdf), [25](https://arxiv.org/html/2504.18943v1)

For a small example, suppose we want to add two mathematical integers. Allow expressions built from x, y, addition, and multiplication, with no overflow. Our requirement is that the result equal x+y for every input pair. This small teaching example makes the search easy to follow.

![Original bottom-up enumeration diagram showing two leaves eight size-three expressions and selected size-five expressions]({{ '/assets/images/zenofcis-2-5/figure-05.png' | relative_url }})

*Figure 2. The grammar E ::= x | y | E+E | E×E builds larger syntax trees from smaller ones; four of the 64 size-five expressions are shown.*

Start with x and y. Combine them to form x+y, x×y, and the other permitted expressions. Keep those pieces and combine them again to form larger candidates. This is **bottom-up enumeration**: construct larger programs from smaller programs already available, then evaluate candidates to see whether they meet the requirement.

## Same answers, different programs

![At input two-two sum and product share output four while input two-three separates their output vectors]({{ '/assets/images/zenofcis-2-5/figure-06.png' | relative_url }})

*Figure 3. These input pairs adapt a published sum-versus-product example; they illustrate observations, not a CEgraph or COGS execution.*

At (2,2), both x+y and x×y return 4. They are **observationally equivalent on that example**. Grouping candidates by their observed results can avoid repeating work, but the group must remain open to correction.

At (2,3), the answers become 5 and 6. Multiplication fails our addition requirement. A verifier can return this input as a **counterexample**, and the search can use it to distinguish candidates that previously looked identical. Passing examples identifies a possible answer; acceptance must depend on what was established over the specification’s full domain.

The papers develop ways to organize and accelerate this search. Later, we follow a concrete synthesis task through its recorded checks and into a running application.

<details id="synthesis-depth">
<summary>Inside the search: constraints, observational reuse, CEgraph, and GPU acceleration</summary>

### What the synthesizer receives

A synthesis problem needs an input domain, an allowed program language, and a correctness condition under explicit semantics. Verification checks that condition for a supplied candidate. Execution evaluates a candidate on particular inputs. A successful execution alone says nothing about untried inputs.

For an arithmetic example, restrict candidates to f(x)=ax+b with integer parameters. Requirements f(0)=1 and f(2)=5 force b=1 and a=2. The small candidate family makes those two examples decisive within that family. They do not uniquely determine a program in an unrestricted language.

Indeed, 2x+1 and 2x+1+x(x−1)(x−2) both fit (0,1), (1,3), and (2,5), but disagree at x=3. This is why the grammar and specification must be stated together. The calculation shows how restricting the candidate family changes what examples determine. [5](https://www.microsoft.com/en-us/research/wp-content/uploads/2013/05/fmcad13.pdf)

### What bottom-up construction counts

Our grammar has two leaves, x and y, and two binary operators. Counting syntax-tree nodes gives two size-one terms, eight size-three terms, and 64 size-five terms. The last count includes both ways of distributing a leaf and a size-three subtree around a binary operator. These are ordered trees: x+y and y+x count separately even though their integer meanings agree.

The associated data lists all 74 terms through size five. Size is not tree depth; changing the grammar or arithmetic changes the search problem. Our illustration uses multiplication to make accidental agreement easy to see.

### What an observation class means

For the single input (2,2), sum and product have the same output vector `[4]`. Adding (2,3) gives `[4,5]` for the sum and `[4,6]` for the product. These vectors summarize behavior on the chosen observations only. By contrast, x+y and y+x agree on every mathematical integer input.

Keeping only one representative without a way to recover discarded alternatives can lose a program needed after refinement. The useful optimization therefore includes a responsibility: preserve enough structure to revise the grouping when new evidence distinguishes its members.

### How the research approaches differ

The 2025 CE-graph proposal constructs a graph conditioned on a new counterexample and joins it with the existing graph, retaining equivalences supported by both. This is an intersection-like refinement, not ordinary e-graph union or a literal split animation. The represented terms may still need to grow; the graph does not automatically contain the whole grammar. [23](https://ceur-ws.org/Vol-4008/SMT_paper11.pdf)

The later COGS paper uses explicit observed-value lists and a refinement procedure that separates classes when new observations distinguish them. The signature diagram makes that distinction between old and new observations visible. [24](https://repositum.tuwien.at/handle/20.500.12708/230505)

The GPU paper synthesizes finite-trace temporal formulas that accept positive traces and reject negative ones. It stores bit-vector summaries of a formula’s truth at every position of the supplied traces. Recording only the starting position would lose information needed by temporal operators. New formulas can then be evaluated through operations on these summaries, with many candidates processed in parallel. This changes the representation and cost of search, not what the examples establish: a formula fitting them need not capture intended behavior on unseen traces. Faster enumeration does not supply missing requirements. [25](https://arxiv.org/html/2504.18943v1)

</details>

## A smaller question can have a complete answer

For the square loop, maintain s=i² and 0≤i≤n. Increasing i by one requires adding 2i+1 to s. The invariant proves the answer at exit; the decreasing integer n−i proves termination. Machine overflow needs a separate condition.

Finite checking can cover every input in a declared domain, not merely a sample. Its strength depends on whether that domain and its semantics capture the real requirement. Always ask: **which artifact, which property, which domain, which assumptions, and which link to the running code?**

<details id="bounds-depth">
<summary>Derive the square loop and ask what “verified” covers</summary>

![A square accumulator maintains s equals i squared at successive states]({{ '/assets/images/zenofcis-2-5/figure-07.png' | relative_url }})

*Figure 4. The selected states illustrate the square-loop rule; the algebra below establishes why it preserves the invariant.*

Suppose we want to compute n² for a natural number n, without multiplication inside the loop. Let the state be (i,s), start at (0,0), and maintain 0 ≤ i ≤ n and s = i², using the guard i < n.

If i increases to i + 1, the next square is (i + 1)² = i² + 2i + 1. Since the current s already equals i², the update must add 2i + 1. Use the simultaneous assignment (i,s) := (i + 1, s + 2i + 1). In a sequential language, update s before incrementing i, or save the old i.

Three obligations make the reasoning explicit. Initialization: 0 = 0². Preservation: the algebra shows that the update keeps s = i². Exit: when i = n, the invariant gives s = n². A fourth obligation establishes termination: n − i is a nonnegative integer that decreases by one on each iteration while i < n.

This derivation distinguishes partial correctness, which says the output is right if the program terminates, from total correctness, which adds termination. Neither claim alone establishes that the computation is fast enough for its intended use.

Machine arithmetic adds another obligation. Hoare warned that “computer arithmetic is not the same as the arithmetic familiar to mathematicians”. A proof over unbounded integers does not automatically establish correctness for a machine type that can overflow. Choose and state the bounds or modular semantics. [6](https://www.cs.cmu.edu/~crary/819-f09/Hoare69.pdf)

### Why useful boundaries are an advantage

Practical systems make progress by choosing boundaries. They may restrict the language, bound inputs, synthesize only a small decision kernel, require an explicit contract, or use a proof system with stated assumptions. These choices are engineering decisions, not embarrassing footnotes. They define the set of claims the machinery can actually support.

For a finite input domain D, a checker may establish a property for every x in D by exhaustive evaluation, a symbolic decision procedure, or another justified method. That conclusion is stronger than testing a handful of examples. It is also narrower than a theorem for all unbounded integers, arbitrary networks, or every possible operating environment.

A useful review habit is to ask five questions before accepting the word “verified”:

- What exact artifact was checked?
- What property was checked?
- Over which inputs and states?
- Using which semantics, assumptions, and checker?
- What connects that artifact to the program actually deployed?

</details>

## Eventually needs a witness

“Always preserve the reserve” forbids a bad state. “Eventually complete every request” demands progress. A system that freezes can satisfy the first and fail the second.

In the finite semantics used here, eventually includes now: [false, false, true] satisfies it at the start; a completed [false, false] fails. Strong next is false at the endpoint. A real-time deadline additionally needs a clock and timing assumptions. Unbounded progress may depend on an explicit fairness assumption. A system-level guarantee must cover every admitted execution under its assumptions; one successful trace is insufficient.

<details id="temporal-depth">
<summary>Why a finite ending changes truth: operators and recorded diagnostics</summary>

![Finite eventuality outcomes depend on whether a witness occurs before the trace ends]({{ '/assets/images/zenofcis-2-5/figure-08.png' | relative_url }})

*Figure 5. Current-position truth counts as an eventual witness; a short completed trace without a witness fails.*

Return to the two sequences at the beginning. “Eventually reach 1” is false for the exact geometric partial sums. “Eventually reach 0” is true for each Goodstein sequence. Both statements concern a future witness, but neither supplies a practical deadline. Even when a terminating index exists, it may be too large to reach with available resources.

Temporal logic makes this distinction part of the specification. A state property asks what is true now. A temporal property asks how truth is arranged across a trace of observations.

“Always keep the reserve” is a safety-shaped requirement. A single observed reserve breach refutes it. “Eventually resolve every pending order” is a liveness-shaped requirement over an ongoing execution. It asks for progress, not just the absence of a bad state. A system that freezes forever can preserve a safety invariant while failing to make progress.

A wall-clock deadline needs more than the word “eventually.” It needs a clock model, a deadline, and assumptions linking logical steps to time. Likewise, progress may depend on the environment: does a scheduler eventually run an enabled action, does a user supply approval, or does a remote service eventually respond? These are fairness or environment assumptions to state, not facts a language acquires simply by having temporal operators.

The public 2.5 release includes a separate `.zeno` v1 temporal-claim facility. It supports finite-trace temporal operators such as `eventually`, `always`, `next`, and `until`. It is distinct from the Boolean ZAL state-machine grammar, which describes finite control-state transitions and has no temporal operators. [13](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TEMPORAL_LOGIC_V1.md), [12](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/GRAMMAR.md#L89-L107)

The documented temporal syntax includes:

```text
claim 500 stable cvc5 finite 4 = always atom(post.100 >= 0);
claim 501 stable_forever lean unbounded = always atom(post.100 >= 0);
```

The formulas resemble one another, but the modes ask different questions. `finite 4` ranges over nonempty traces of lengths one through four. Four is a count of logical observations, not four seconds. `unbounded` creates a Lean proof obligation; it has no built-in finite evaluator that can certify an infinite future. [13](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TEMPORAL_LOGIC_V1.md)

Within the finite semantics, `eventually p` means that p holds at the current position or some later position still in the trace. On the trace false, false, true, it holds at the start. On the completed trace false, false, it fails. The evaluator does not silently append an imagined future witness. An empty trace, missing observation, arithmetic failure, or exceeded limit can instead make the claim indeterminate and block it.

Other operators have similarly explicit endings. Strong `next p` is false at the final position because there is no next observation. `always p` needs p at every remaining position. Strong `p until q` requires q to occur and p at all preceding positions. These rules prevent casual English from hiding end-of-trace assumptions. [13](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TEMPORAL_LOGIC_V1.md)

Unbounded claims are different from finite checks: they carry a proof obligation that must be discharged under an explicit kernel and axiom policy. In the public 2.5.0 CLI, the ordinary Lean-export route reports UnsupportedMode, so this tutorial does not present an unbounded temporal claim as proved. The finite examples above illustrate trace semantics; they do not establish fairness or behavior of a running application. [14](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-cli/src/main.rs#L1360-L1405)

</details>

## Two notations, one declared model

The v2.5.0 source includes an optional Boolean ZAL research prototype, profile `zal/finite-fsm/1`, outside the released API. Its grammar pairs a symbolic rule with controlled English. This example illustrates the source prototype, not a command available in the released CLI. [12](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/README.md)

```text
rule approve_order: pending + approve [authorized] -> accept approved;

Rule approve_order: when the state is pending and the event is approve,
if authorized, move to approved.
```

Both forms describe the same canonical model. The `authorized` Boolean is only an input observation; authentication belongs to the surrounding application. The finite-state grammar excludes temporal operators. Unresolved liveness is a placeholder, not an executable progress check. [12](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/GRAMMAR.md#L75-L107)

<details id="zal-depth">
<summary>See why a safe state graph can still wait forever</summary>

![ZAL order states allow a pending order to keep rejecting without progress]({{ '/assets/images/zenofcis-2-5/figure-10.png' | relative_url }})

*Figure 6. The waiting loop shows why a progress requirement needs more than a state invariant.*

The optional source prototype in v2.5 is `zal/finite-fsm/1`, a Boolean control-state machine, not a released API or packaged CLI command. Its grammar does not include temporal operators. For example, the documented rule is:

```text
rule approve_order: pending + approve [authorized] -> accept approved;
```

Its paired controlled-English form is:

```text
Rule approve_order: when the state is pending and the event is approve, if authorized, move to approved.
```

The grammar fixes what these words mean. This rendering does not ask a language model to improvise an equivalent policy. The `authorized` Boolean is an observation supplied to the model, not evidence that an actual person has been authenticated. [12](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/GRAMMAR.md)

A finite-state machine can have a finite state graph but executions of arbitrary length. Checking an invariant on every reachable state can therefore establish that state property throughout arbitrarily long modeled executions. It does not show that a desired event will eventually happen. An infinite self-loop is the simplest counterexample to that leap.

The prototype can retain an unresolved progress obligation as readable text, for example:

```text
unresolved liveness: every pending order eventually resolves;
```

The obligation has no executable interpretation. If the remaining checks pass, the prototype retains it and reports the result as unsupported; it does not check whether progress occurs. [12](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/zal/GRAMMAR.md#L75-L87)

</details>

## The next direction: ZAL-T and the meaning of “eventually”

A temporal statement is easy to misread when a formula is separated from its assumptions. ZAL-T develops a way to present one claim through its formula, typed meaning, precise English reading, intuitive explanation, plain-language paraphrase, and a question that exposes any missing premise. This direction is beyond the public 2.5 release; it is not part of the released 2.5 API or CLI. This section illustrates the idea, not a shipped capability. These views should clarify one claim, not silently replace it with a different one.

For example, consider a request whose matching completion must occur at or after the request:

```text
forall trace in Traces: Environment(trace) =>
  forall request in Requests:
    always(requested(request) => eventually(completed(request)))
```

The same request identity matters throughout. Completion of a different request is not a witness. The environment premise matters too: an ongoing liveness guarantee can depend on the scheduler, keeper, or remote service continuing to make progress. A finite replay can illustrate the formula, but it cannot prove that an infinite environment premise holds.

For a bounded example, define `within(k, P)` to mean that `P` holds at the current observation or one of the next `k` observations. The offsets are discrete events, not seconds. A wall-clock deadline also needs a clock model and assumptions that relate events to time. A short completed trace without a matching witness fails the finite requirement; it does not prove the event could never happen in the live system.

These distinctions show what ZAL-T aims to preserve: one declared meaning across notation and explanations. The released 2.5 `.zeno` temporal-claim facility described above is separate from ZAL-T, and the Boolean ZAL prototype is a separate finite-state grammar. A readable presentation does not itself establish runtime behavior, authentication, authorization, or deployment authority.

### A withdrawal queue as a scope check

A useful requirement shape is: when a request is admitted and the modeled window remains open, queue a matching completion within a finite number of events. That claim is conditional on the event source continuing, on request identity being preserved, and on the model's definition of “queued.” It says nothing by itself about delivery, settlement, or elapsed seconds. Those are separate outcomes and obligations.

## A proposal is not permission

ZenoFCIS separates a functional decision core from an imperative shell. Applications supply declarative programs and inputs; the core evaluates decisions against its laws, while the surrounding shell persists and interprets outcomes. A proposal does not authorize itself. [7](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/ARCHITECTURE.md)

A useful evidence chain connects the contract, source revision, generated artifact, checks, and runtime. Hashes identify the artifacts in that chain. Finite exhaustive checks, attested solver answers, and kernel-checked proofs are different evidence categories. ZenoFCIS’s formally verified core establishes its specified properties for shared executable evaluation, law-checking, and Authority operations. The surrounding system has additional obligations. [26](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/verification/verus/authority_v2.rs#L1-L19)

<details id="factory-depth">
<summary>Trace the trust boundary: core, shell, authority, and evidence</summary>

![Candidate generation is separate from checking and refinement]({{ '/assets/images/zenofcis-2-5/figure-15.png' | relative_url }})

*Figure 7. A conceptual generate-and-check loop. Candidate generation, checking, and adoption carry distinct responsibilities and evidence.*

Each handoff gives us a concrete review question: does the contract express the requirement, does its domain cover the intended inputs, and does the running application use the checked artifact through the intended interface?

The architecture earns trust by making those transitions visible and testable. An evidence record should answer which specification, source revision, parameters, generated output, and checks belong together. Artifact hashes link the files in that record; the checks and runtime binding explain why those files matter.

ZenoFCIS's pinned architecture describes a functional core and an imperative shell. The core works with bounded values and decisions. The shell obtains outside inputs, persists authorized results, and delivers effects. The dependency structure moves from values and canonical encodings through schemas, transitions, laws, synthesis, and evidence to authority types and external adapters. Lower dependency rings do not import higher ones. [7](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/ARCHITECTURE.md)

Authority operations belong to the verified core. The surrounding shell persists authorized results and delivers effects under its own assumptions.

The architecture also separates judgments. An exhaustive finite check, an unchecked solver report, and a kernel-checked proof are not interchangeable. In particular, an external solver's unsatisfiability answer is recorded as attested when it is not rechecked. A synthesis “no solution” result depends on the search's candidate enumeration. The stated trusted base includes interpreters, compilers, target runtimes, and, for the relevant proof route, the Lean kernel and translation. [7](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/ARCHITECTURE.md)

The Verus authority verification unit imports the actual resource, canonical, evaluation, execution_v2, and value modules. Executable Authority functions carry contracts connecting their results to model transitions; composed execution connects law evaluation to its specification. This is verification of shared executable core code. Project laws, adapter contracts, and deployment assumptions specify how a surrounding application uses those guarantees. [26](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/verification/verus/authority_v2.rs#L1-L19)

</details>

## Close the loop from contract to code

The source-built demo uses fictional credits: balance 0…6, request 1…3, and approval 0 or 1, giving **42 inputs**. Accept exactly when approval holds and the remaining balance is at least 2; otherwise preserve the balance and produce no effect. The tutorial supplies the contract and sketch explicitly.

![Actual synthesis transcript with a selected result and first counterexample]({{ '/assets/images/zenofcis-2-5/evidence-source-synthesis.png' | relative_url }})

*Figure 8. The actual synthesis result records a finite domain of 42 inputs, three evaluated assignments, and a counterexample to an earlier candidate.*

The search rejected a candidate that spent the reserve, then selected a valid assignment. Runtime conformance bound the emitted Python files to the expected artifacts and exhaustively checked their outputs against the interpreter and contract on all 42 inputs. The receipt establishes conformance over the complete declared domain and records `authority: none`. [27](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/crates/zeno-fcis-cli/src/synth/runner.rs#L331-L374)

![Recorded application execution after switching to the checked optimized core]({{ '/assets/images/zenofcis-2-5/evidence-source-app.png' | relative_url }})

*Figure 9. The source-built application uses the checked replacement and simulates its effects.*

The shell really calls the generated core. It rejects unapproved spending, accepts permitted spending, preserves the reserve, and refuses out-of-domain requests. Its effects are simulated; the approval flag is not authenticated permission.

A separate transformation loop refuted an unsafe edit, accepted an equivalent smaller program, and replayed the result. The accepted replacement was emitted, checked on all 42 inputs, and selected as the module used by this shell. The measured improvement is representation size: 10 to 9 nodes. The assistant supplied candidates externally; the loop recorded zero model calls.

<details id="install-depth">
<summary>Reproduce the source build and published-binary installation</summary>

The demonstration uses fictional credits and simulated effects to show the whole path: define a decision, synthesize its arithmetic core, check the emitted code, then call it from an application.

### Install the exact tool you intend to test

![Actual transcript showing the installed ZenoFCIS version]({{ '/assets/images/zenofcis-2-5/evidence-source-version.png' | relative_url }})

*Figure 10. Recorded terminal transcript showing the source-built CLI version.*

The initial recorded run built the source at commit `98da3707af0fb238c4bc1604ea6209382f829dfb` with Rust 1.97.1. The build command was `cargo +1.97.1 build --locked -p zeno-fcis-cli`. It completed successfully and the resulting CLI reported version 2.5.0. This source build is the executable used for the recorded run.

To reproduce the source installation, install Rust 1.97.1 from the official Rust distribution, clone [the project repository](https://github.com/TheDarkLightX/ZenoFCIS), check out the pinned commit, and build with the lockfile:

```sh
git clone https://github.com/TheDarkLightX/ZenoFCIS.git source
cd source
git checkout 98da3707af0fb238c4bc1604ea6209382f829dfb
git rev-parse HEAD
cargo +1.97.1 build --locked -p zeno-fcis-cli
./target/debug/zeno-fcis --version
```

These reproduction instructions accompany the recorded toolchain installation and build output. For the finite transformation loop, build the optimized executable with `cargo +1.97.1 build --release --locked -p zeno-fcis-cli` and use `target/release/zeno-fcis`.

This is the source-build record. The separate published-binary smoke below is tied to release source `8e9c33e86f376a4431641159a8e5225af9271431`; it does not replace this app demo or its historical receipts.

<h3 id="install-published-binary">Install the published 2.5.0 binary</h3>

The official [v2.5.0 release](https://github.com/TheDarkLightX/ZenoFCIS/releases/tag/v2.5.0) went live on 22 October. On an isolated Linux x86-64 host with glibc 2.41, we downloaded its six release assets, verified the signed checksums and signed tag, installed the binary, and confirmed `zeno-fcis 2.5.0` and `describe`. The CLI generated a fresh `agent-treasury-guard` template without a handwritten application implementation. It rejected an unsafe candidate with a counterexample, then selected a Python function after eight assignments. A separate Python 3.13.5 runtime check passed all 6,144 admitted inputs. [28](https://github.com/TheDarkLightX/ZenoFCIS/releases/tag/v2.5.0)

That adds a real download-to-install-to-generated-template path. The running budget app and its durable Rust journey remain separate evidence from the earlier source-build demo. This focused release smoke did not rerun that 42-input app, the durable-app flow, or the full release acceptance suite. Its receipt says `authority: none`, so this is not proof of deployment or authorization for a real financial action.

<details id="binary-install-depth">
<summary>Open the release provenance, replay commands, and compatibility notes</summary>

The release was published at 05:19:21 UTC on 22 October 2026; the recorded commands ran from 06:09 to 06:11 UTC. The tested archive is `x86_64-unknown-linux-gnu`, on Linux x86-64 with glibc 2.41. The archive requires glibc 2.39 or newer. No macOS or Windows binary was present in this release asset set; macOS installation remains untested.

- Archive SHA-256: `dd0240e9f114c2e42b24fa8297cc3ef0d31d27ec3d77ed44dd93cbfa7a72b0f6`. Every entry in `DOWNLOADS.sha256` passed, and OpenSSH verified its signature in the `file` namespace.
- The signed `v2.5.0` tag passed Git verification and resolves to source `8e9c33e86f376a4431641159a8e5225af9271431`. The extracted CLI SHA-256 is `e1d35ca35bd1e0ae11ac3de5d50638f1c13c4020d6c2e2bf3c81bb7be6584004`.
- The signing-key fingerprint `SHA256:dIlSeZjogR21GU3QVYyoBoW2LqLyiUosSLvuEqcFWGw` matched the fingerprint recorded during the earlier 2.4 check. This supports key continuity and signature verification, not fresh, independent out-of-band authentication of the maintainer's identity.
- The original tutorial app's source-build pin is `98da3707af0fb238c4bc1604ea6209382f829dfb`, not this release source. Keep its app receipts labeled as the source-built run.
- Existing 2.4 contracts and stores need their matching 2.4 CLI and runtime. Re-adopting them under 2.5 creates a new store, not a migration; this isolated demonstration opened no existing store.
- The emitted-function check establishes agreement with the reviewed relation on those 6,144 admitted inputs. The receipt states `authority: none`; the template's historical synthesized scalar function is distinct from its normal V2 Authority runtime. It does not qualify the whole generated application or approve a financial action.

<figure>
  <img src="{{ '/assets/images/zenofcis-2-5/release-verification-excerpt.png' | relative_url }}" alt="Excerpt from the recorded 2.5.0 verification log showing successful checksum signature verification and release asset checks." />
  <figcaption>Excerpt from the recorded 2.5.0 installation and verification run.</figcaption>
</figure>

<h4 id="reproduce-published-binary-smoke">Reproduce the download, install, and synthesis smoke</h4>

From a fresh Linux x86-64 workspace with glibc 2.39 or newer, obtain the official assets and matching source, verify them, and run the commands below. First compare the release key fingerprint with the previously recorded value before trusting the signature.

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

The evidence bundle retains six numbered logs: download, source checkout, signature and hash verification, extraction and `describe`, template creation and synthesis, then runtime conformance. `record.py` records transcripts; it is not application logic. The bundle intentionally omits the downloaded binary, full source checkout, and toolchains. Regenerate in a fresh checkout so the template can resolve its source tree.

</details>

</details>

<details id="app-depth">
<summary>Follow every handoff: contract, synthesis, runtime check, application</summary>

### Write a contract that requires useful behavior

The admitted input is `(balance, request, approved)`. Balance ranges from 0 through 6, request from 1 through 3, and approval is 0 or 1. That is 7 × 3 × 2 = 42 input tuples. The reserve is 2 fictional credits.

Accept if and only if approval is 1 and balance minus request is at least 2. On acceptance, subtract exactly the request and ask for one simulated effect. On rejection, preserve the balance and ask for no effect. Values outside the declared domain must be refused by the wrapper.

The phrase “if and only if” matters. A program that rejects everything never overspends, but it fails this contract: with balance 6, request 2, and approval 1, acceptance is required. This tiny positive obligation prevents safety from becoming a vacuous excuse to do nothing.

The supplied sketch contains four possible assignments: choose reserve 0 or 2, and choose whether to honor or bypass approval. This small search is easy to inspect. The check relates the emitted program to the supplied contract; reviewing that contract remains the place to examine intended behavior.

### Let a counterexample reject the wrong candidate

From the demonstration directory, the recorded command was:

```sh
zeno-fcis --no-kb synth run app/budget.json --target python --out app/generated-python
```

The result was `selected`, with `semantic: complete-finite` and `input_coverage: 42`. It evaluated three assignments. The recorded first counterexample was input `[1,1,1]` with candidate output `[1,0,1]`: accept a one-credit request from balance 1, leave balance 0, and request an effect. That violates the two-credit reserve.

The emitted artifacts include `transition.py`, the encoded program, test vectors, and a manifest linking their identities. The output explicitly says `authority: none` and initially `runtime_conformance: not-run`. Selection is one milestone. Checking the emitted runtime function is another.

### Check the exact emitted function

```sh
zeno-fcis --no-kb synth verify app/budget.json --target python --out app/generated-python --receipt evidence/python-conformance.json
```

This run returned `status: passed` and `inputs_checked: 42`. The stated claim is that the exact emitted function agrees with the interpreter and reviewed relation on every admitted input. Here “reviewed relation” names the supplied relation in the receipt. The recorded runtime was Python 3.12.14. The receipt's identity scope expressly leaves dynamic dependencies and compiler correctness as external premises.

The receipt records `authority: none`.

### Put the checked function inside an honest shell

The application starts at balance 6. An unapproved request for 2 is rejected, leaving 6. An approved request for 2 is accepted, leaving 4. A request for 3 is then rejected because it would breach the reserve. An approved request for 2 leaves exactly 2. Further spending is rejected, and a request for 99 is refused as outside the admitted domain. The six scripted checks passed.

The tutorial’s hand-written shell imports the generated `transition.py` and supplies the approval flag as input. Its behavior is exercised by the tests below. The project’s V2 Authority and durable SQLite shell are separate components; this example uses a small local wrapper so the generated-function call is easy to inspect.

Additional tests checked all 42 tuples against a separately written restatement, ten malformed or out-of-domain inputs, all 1,296 request/approval sequences of length four from the starting balance, and three deliberate faulty variants. Reject-all, bypass-approval, and drop-reserve variants were each refuted by concrete inputs. These tests are useful corroboration, but the restatement was prepared in the same tutorial session and can share a mistaken interpretation.

JavaScript emission was also checked. An initial attempt refused Node 24 because the supported runtime was Node 22. After installing the required Node 22.23.1 runtime, the same 42-input conformance check passed. The initial refusal remains in the evidence alongside the successful qualified-runtime run.

</details>

<details id="repair-depth">
<summary>Why a smaller program still needs a check</summary>

A candidate is useful only if it preserves the contract. In the educational source-build run, a deliberately unsafe edit accepted a request that would breach the fictional reserve. The checker produced a concrete witness; a later candidate removed a redundant expression while preserving the same finite relation.

The lesson is independent of the search tool: “smaller” is not evidence of equivalence. Check the candidate against the reviewed relation on the declared domain, then bind the checked artifact to the code that the application actually calls. This source-build experiment is not part of the separate official release-binary smoke.

</details>

## Logic needs a secure path to action

Tau Language supports logical specifications, reactive synthesis, an interpreter, and ahead-of-time compilation. The optional Tau bridge supports finite pointwise specifications. Tau Network supplies a broader distributed context for the complementary architecture explored below. [8](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/README.md), [9](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TAU_KIT.md), [10](https://tau.net/), [11](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/LICENSE.md)

For agent security, a correct decision gate helps only if privileged actions cannot bypass it and untrusted input cannot rewrite its policy. Least privilege, authentication, protected configuration, controlled effects, and audit records remain separate obligations. A checked reserve does not establish honest data or reliable delivery.

<details id="tau-depth">
<summary>Where Tau connects, and what the bridge refuses</summary>

Tau Language offers a declarative way to express relationships between inputs and outputs over time, with reasoning and reactive synthesis facilities. Its current source documents both an interpreter and ahead-of-time generation and compilation through `tau gen` and `tau compile`. A comparison that calls Tau merely an interpreter and ZenoFCIS a compiler would miss the actual overlap. [8](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/README.md)

The useful comparison is the placement of the boundary. Tau emphasizes executable logical specifications and temporal relationships. ZenoFCIS emphasizes bounded decision construction, explicit evidence categories, and an FCIS authority path between proposed decisions and effects. Both need a precise account of semantics, supported fragments, trusted implementations, and the meaning of failure. Tau's documented compilation covers a subset of interpreter behavior, and some searches have caps. Reaching a cap or returning UNKNOWN is not a proof of a proposition. [7](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/ARCHITECTURE.md), [8](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/README.md)

There is already a restricted bridge in the ZenoFCIS source. Its optional Tau kit imports a complete pointwise decision ladder through the native contract compiler. Generic import accepts flat scalar records, fixed streams, current-time projections, same-width unsigned comparisons, Boolean operations, and modular addition or subtraction, within documented width bounds. Temporal history and future, among many other constructs, are refused. These rules define the bridge’s supported pointwise fragment. The native representation also supplies zero genesis, diagnostic rejection reasons, and a state-domain law. [9](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TAU_KIT.md)

Export produces per-rule queries and deterministic samples of native Authority decisions. Export alone does not run Tau or SMT. A separate local runner checks pinned executable hashes, retains transcripts, requires agreement between Tau and paired SMT results, and includes negative controls. Timeouts, errors, unknown results, or disagreement leave the run incomplete. The documentation calls successful corroboration attested evidence about those queries, not kernel-checked proof, authentication, authorization, or whole-domain sampled replay. The supported kit Tau revision is distinct from the current Tau source used for the capability comparison. [9](https://github.com/TheDarkLightX/ZenoFCIS/blob/v2.5.0/docs/TAU_KIT.md)

Scaling a 256-bit source to a three-bit study domain also changes the question. It can support a small experiment but cannot establish equivalence over the original 256-bit domain. The same caution applies whenever a demo becomes tractable by narrowing inputs.

Tau Network is a broader proposed distributed setting, not another name for Tau Language. Its official site describes rule-chain, wallet, and agent-account directions, while presenting a waitlist and distinguishing the ERC-20 placeholder from the described mainnet features. This section examines the documented pointwise bridge and a possible network composition. [10](https://tau.net/)

A plausible complementary architecture would let participants express and examine policy in an agreed Tau fragment, translate the supported part into a native ZenoFCIS contract, check both sides against pinned artifacts, and admit the policy through the application's authority boundary. A network adapter would then supply authenticated observations and submit authorized effects. This proposed composition builds on the documented pointwise bridge.

The hard work is at the joins: preserving meaning during translation, authenticating observations, handling replay and finality, bounding stale oracle information, and delivering effects safely. Tau also has a custom license whose applicable terms need review before redistribution or deployment. [11](https://github.com/IDNI/tau-lang/blob/dad02cdbdd239f5b169e1256045c57d8f7efca3d/LICENSE.md)

</details>

<details id="security-depth">
<summary>A correct gate still needs an unbypassable path</summary>

![Verified core components and separate obligations at their system boundary]({{ '/assets/images/zenofcis-2-5/figure-24.png' | relative_url }})

*Figure 11. Verified core components establish their specified properties; surrounding components have separate obligations. The map distinguishes proof scope from whole-system trust.*

An agent can choose actions, but a separate enforcement boundary should decide which actions are permitted. This separation is particularly important when the agent reads untrusted documents, web pages, messages, or tool outputs. Those inputs may contain instructions designed to redirect it.

A decision gate could check a narrow property such as “this modeled action must leave the simulated reserve at or above the stated threshold.” If the domain, arithmetic, and implementation are correct, that property can be useful. It does not establish that the action is wise, that a price feed is honest, that a remote service will honor the request, or that all routes to execution pass through the gate.

For cybersecurity, ask where the authority lives. If the agent can bypass the gate and invoke a privileged API directly, a correct gate does not secure the system. If an untrusted message can rewrite the contract, a checked contract may enforce the attacker's policy. If secrets appear in logs or side channels, a budget invariant does not protect them.

A practical defense therefore combines a small checkable policy with an enforcement design: least privilege, explicit authorization, protected configuration, input validation, controlled tool access, audit records, and a safe failure path. Each contributes a different assurance. None should be silently credited to arithmetic synthesis alone.

A proof is best read as a carefully scoped conditional: under these assumptions and this semantics, this artifact has this property. Improving security includes proving useful conditions and reducing the number of unchecked assumptions needed to rely on them.

</details>

## From shared meaning to checked construction

A direction for work beyond the 2.5 tutorial is an examples-first path from intent to a reviewed contract: make proposed rules explicit, ask questions that distinguish interpretations, test supplied examples, and only then construct the surrounding application. Each stage needs its own evidence. Passing examples does not show complete input coverage, and generating code does not establish that the contract captures the intended requirement.

The bounded synthesis walkthrough above makes the same boundary concrete: a counterexample can reject an unsafe candidate; an exact runtime check can establish agreement over a declared finite domain; and the surrounding shell still needs its own authorization, persistence, and delivery checks. Those layers are not interchangeable.

A withdrawal-queue requirement illustrates why “eventually” needs careful scope. A bounded claim may require a matching request to be queued within a number of discrete events, provided the modeled event source continues and the request identity is preserved. Queuing is not delivery, and neither statement means a wall-clock duration without an explicit clock model. Any future 2.6 work should make these assumptions and handoffs reviewable rather than allowing a readable paraphrase to imply stronger evidence than the checked artifact supplies.

### What to carry forward

Zeno teaches us to distinguish a limit from a completed computation. Goodstein teaches us that a simple generating rule can require surprisingly strong mathematics to establish its global behavior. Program encoding teaches us to distinguish representing a computation from solving every question about it.

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
