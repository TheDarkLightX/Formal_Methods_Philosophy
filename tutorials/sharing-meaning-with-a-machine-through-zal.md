---
title: "Sharing Meaning with a Machine Through ZAL"
layout: docs
kicker: Research essay
description: "ZAL sentences, symbols, functions, and diagrams make the assumptions behind two small machines visible."
---

I use ZAL, the Zeno Abstraction Language. ZAL allows for a human like me, to capture my mental model and translate it into a formal mathematical representation. I can start with a plain English sentence to the LLM assistant which can translate it into unambiguous controlled English. I can also simply type: `f(x)=y` and most LLMs know my intent and can translate that into deeper more meaningful visual representations. This can be Lambda calculus, it can be ZAL notation, or any custom representation, without losing any accuracy.

I inspect the controlled English and glyphs, ask questions, and revise it. The assistant proposes; I oversee meaning; checkers answer the encoded questions. This shared meaning can also be lowered down the abstraction ladder, once ambiguity is removed. Plain English requirements can become controlled English. Controlled English can become a semantic contract, a formal specification, and from there synthesized to a program, or compiled.

An assistant's interpretation is a proposal: `f(x)=y` alone does not specify the domain or what the function and variables represent. I can supply and review those details. A translation preserves meaning when the necessary distinctions can be expressed and the relationship between views has been checked. Program generation and compilation depend on the ZAL profile and the artifacts it supports.

## Multiple views, same meaning

Consider this ZAL sentence:

> For every state x, there exists exactly one state y such that x advances to y.

Its symbolic reading is **∀x ∈ D : ∃!y ∈ D : Step(x, y)**.

Here **∀** means “for every,” **∃!** means “there exists exactly one,” `D` is the set of states, and `Step(x, y)` means that `x` can advance to `y`. The same ZAL formula also has an ASCII spelling:

```text
forall x in D: exists1 y in D: Step(x, y)
```

[![The unique-successor statement in ZAL glyphs]({{ '/assets/images/zal-machine-discovery/unique-successor.png' | relative_url }})]({{ '/assets/images/zal-machine-discovery/unique-successor.png' | relative_url }})

*The brackets bind variables. Dashed lines connect their uses; solid lines connect the parts of the formula.*

The English sentence and the symbolic formula are two views of the same statement: every state has a next state, and there is only one possible next state.

To evaluate that statement, the names `D` and `Step` need an **interpretation**: a choice of what counts as a state and which steps are possible. A model supplies those choices. For any one model, the English and symbolic views ask the same question. The following examples apply that question to two different models:

| Interpretation of state and step | Result |
| --- | --- |
| In the first-in, first-out (FIFO) cache model, `D` contains the queues `ADC`, `DCB`, and `BAD`. A step executes the complete request sequence `ABCD`. | **TRUE** |
| In the Toffoli model, `D` contains sixteen four-bit patterns. A step can use any of twelve Toffoli instructions, without recording which instruction was chosen. | **FALSE** |

In the FIFO model, the steps are `ADC → DCB`, `DCB → BAD`, and `BAD → ADC`. Every state has exactly one successor, so the statement is true. In the Toffoli model, state `3` has three possible successors: `3`, `7`, and `11`. One state with more than one successor is enough to make the statement false.

The words “every” and “exactly one” keep their meaning in both interpretations. What changes is the set of states and the steps available between them. Because those choices differ, the same statement can have a different result in each model.

For the first model, imagine a FIFO cache with three slots and four possible keys, `A`, `B`, `C`, and `D`. “First in, first out” means that when the cache is full, a new key replaces the key that was added earliest. A request for a key already in the cache is a hit and leaves the queue unchanged; a miss adds the requested key. Reading each queue from oldest to newest, repeated requests of `ABCD` produce the cycle `ADC → DCB → BAD → ADC`.

[![The FIFO three-state cycle in ZAL notation]({{ '/assets/images/zal-machine-discovery/fifo-trit.png' | relative_url }})]({{ '/assets/images/zal-machine-discovery/fifo-trit.png' | relative_url }})

*Each displayed step is the whole request sequence `ABCD`. The unique-successor sentence holds for these three queue states; separate checks establish the cycle.*

Repeating any one request leaves the cache state unchanged after the first request. The hit or miss response can still change: a first request can miss and the repeated request can hit. The model above tracks queue states, not those responses.

## State-machine, function, and lambda-calculus views

The FIFO state-machine view and its function view are equivalent descriptions of the same transitions. The state-machine view draws an arrow from one queue to the next; the function view maps each queue to its successor:

| State-machine view | Function view |
| --- | --- |
| `ADC → DCB` | `f(ADC) = DCB` |
| `DCB → BAD` | `f(DCB) = BAD` |
| `BAD → ADC` | `f(BAD) = ADC` |

An arrow from `x` to `y` appears exactly when `f(x) = y`. Each view can be recovered from the other, so they describe the same three-state transition behavior. This connection is standard in automata theory: [Cornell's notes on deterministic finite automata](https://www.cs.cornell.edu/courses/cs2800/2017fa/lectures/lec21-dfa.html) relate each arrow in a transition diagram to a transition-function value.

More generally, when the unique-successor sentence holds, the step relation describes a **total** function `f` from states to states. “Total” means that `f` gives an output for every state in `D`. The sentence requires both a successor for every state and no more than one successor per state. Determinism alone can mean at most one successor, allowing a state with none; see Leslie Lamport's discussion of [state machines and next-state relations](https://lamport.azurewebsites.net/pubs/state-machine.pdf).

In this FIFO example, the complete request sequence `ABCD` is fixed as one step, so the current state is the only input to `f`. If a machine takes a varying input `i` on each step, the function can include it: `f(x, i) = y`. A complete description must also carry any initial states, outputs, or action labels that the model includes. The FIFO transition views here track queue states; they do not include the hit or miss responses.

Machines with several possible next states can have functional views too. The function can return the **set of possible successors**: `F(x) = {y : Step(x, y)}`. For the Toffoli model, `F(3) = {3, 7, 11}`. Keeping the chosen instruction as another input gives a function for each labelled step; omitting that label recovers the combined relation. [Carnegie Mellon's state-machine notes](https://www.cs.cmu.edu/afs/cs/academic/class/15671-f95/www/handouts/sm-basics/node4.html) discuss relations and set-valued functions as ways to describe such choices.

Lambda calculus offers a way to describe functions by naming their inputs and expressions. The following lambda term represents the **unique-successor property** itself when supplied with suitable finite-domain operations:

```text
λall.λone.λr. all (λx. one (λy. r x y))
```

In this term, `r` is a relation such as `Step`. The operation `all` checks whether a predicate holds for every state in `D`, and `one` checks whether a predicate holds for exactly one state in `D`. Applying the term to those operations and `Step` asks whether, for every `x`, exactly one `y` satisfies `Step(x, y)`. These operations have to be defined for the domain; the names alone do not define them.

[![ZAL lambda diagram for the unique-successor property]({{ '/assets/images/zal-machine-discovery/unique-successor-lambda.svg' | relative_url }})]({{ '/assets/images/zal-machine-discovery/unique-successor-lambda.svg' | relative_url }})

*ZAL rendered the lambda term as a diagram. Upper horizontal bars introduce variables, vertical lines lead to their uses, and lower horizontal joins show applications of functions. The diagram displays the term; it does not by itself prove agreement with another view.*

The FIFO **transition function** also has a lambda representation. Assign the three queue states to three selectors:

```text
Q0 = λa.λb.λc.a    (ADC: choose the first argument)
Q1 = λa.λb.λc.b    (DCB: choose the second argument)
Q2 = λa.λb.λc.c    (BAD: choose the third argument)

f = λq. q Q1 Q2 Q0
```

The names `Q0`, `Q1`, and `Q2` abbreviate the terms above. For example, `f Q0` applies the first selector to `Q1`, `Q2`, and `Q0`, producing `Q1`. In the same way, `f Q1` produces `Q2`, and `f Q2` produces `Q0`. This is the same three-state cycle as the FIFO table.

I constructed these lambda terms from the recorded ZAL property and transition table. ZAL parsed the terms, rendered the property diagram, and reduced the FIFO transition on all three states; each result matched the recorded successor. The finite `all` and `one` operations were also checked in parts: the FIFO relation passed, while examples with no successor or two successors failed. The combined property expression exceeded the reducer's size limit, so this is a finite comparison, not an automatic general translation or a general equivalence proof.

## A reversible machine that cannot hide zero

The Toffoli model supports a different question. A positive-control Toffoli instruction flips one target bit when two distinct control bits are both `1`; otherwise it leaves the bits unchanged. This model has four bits, distinct controls and target, and no extra bits or constants. A step may use any of the twelve legal instructions.

> For every frozen state x, for every state y, if x advances to y, then x equals y.

The symbolic reading is **∀x ∈ D : Frozen(x) ⇒ (∀y ∈ D : Step(x, y) ⇒ x = y)**.

[![The frozen-state statement in ZAL glyphs]({{ '/assets/images/zal-machine-discovery/frozen-family.png' | relative_url }})]({{ '/assets/images/zal-machine-discovery/frozen-family.png' | relative_url }})

Here `D` contains all sixteen four-bit patterns. `Frozen` identifies the five states `{0, 1, 2, 4, 8}`. Each has at most one bit set to `1`, so no instruction can have both controls set to `1`. Every legal instruction therefore leaves each of these states unchanged.

ZAL recovered the formula from the controlled sentence and glyph model, then evaluated it over the stated finite model. The result was **TRUE**. A separate argument extends this result from one instruction to any finite sequence: if each instruction leaves a state unchanged, applying another instruction still leaves it unchanged.

One eight-instruction example met the local S-box criteria chosen for the experiment. An S-box is a small substitution of bit patterns, often used in cryptography. Even so, every legal instruction sequence maps `0` to `0`, including every sequence selected by a key. The selected example also fixes state `12`. Passing chosen local criteria does not by itself establish cryptographic security. This structural restriction is known mathematics: see [Shende and colleagues, Theorem 22](https://arxiv.org/pdf/quant-ph/0207001).

## From meaning to machines

These examples show several views of a mathematical object and questions about its behavior. A view can preserve a complete meaning, while an abstraction can deliberately leave details out; the latter needs an explicit account of what was forgotten. In the FIFO example, observing only the three queue states leaves out hit and miss responses.

ZAL also has separate executable finite-state profiles that can generate contracts and Rust programs. The relational property sentences in this essay followed a different route: controlled English was parsed into C², a two-variable logic with counting, and evaluated on finite models. Those checks did not produce implementations of the machines described here.

The investigation involved proposals, searches, counterexamples, and revisions. For example, a proposed way to obtain all six permutations of the three FIFO states failed: for the chosen encoding and fixed request sequences, only three rotations were available. Review also found and corrected a mismatch between one visual view and its formula.

These bounded examples establish neither a real software vulnerability nor cryptographic security. A checker can test the statement that was written, but a person still has to decide whether that statement expresses the intended requirement.
