---
title: "Fuzzy lookup tables or neural networks?"
layout: docs
kicker: Essay
description: "Neural networks as programmable computations, from programming by example to compiled weights and checked table networks in Tau."
og_title: "Fuzzy lookup tables or neural networks?"
permalink: /tutorials/fuzzy-lookup-tables-or-neural-networks/
date: 2026-11-02
author: Dana Edwards
tags: ["essay", "neural networks", "lookup tables", "program synthesis", "Tau"]
---

**Dana Edwards · 2 November 2026**

I have always regarded artificial neural networks as computations implemented in software. An artificial “neuron” is a computational unit. The name does not make it a biological neuron. I reached this view by studying neural networks at several levels of abstraction: as functions, as compositions of functions, and as implementations using numerical parameters.

At the level of a function such as f(x,y), inputs are mapped to an output. Describing a language model this way directs attention to the computation being constructed. Its architecture determines the available operations and connections; its parameters help determine the resulting mapping. I have long regarded training as a way of programming that computation through examples and an objective.

Programming by example is already an established approach within program synthesis, the automatic construction of programs from requirements. Examples can serve as those requirements, although a limited set usually leaves several possible programs consistent with them.<sup><a href="#source-4">4</a></sup> Neural parameter fitting and the search for a program expression use different representations and algorithms. I see both as ways of constructing computational behaviour. In this sense, the language of “training” can anthropomorphize a process that is also understandable as automated programming.

The familiar principle of “garbage in, garbage out” applies to both. Misleading examples, unsuitable objectives or flawed assumptions can produce unreliable behaviour. Good examples alone do not guarantee a correct result either: the architecture, search procedure and checks still matter. Calling the process training does not remove these engineering responsibilities.

In *Sparks of Weight-Space Programming*, Rikiya Takehi, Jayden Teoh, Alex Zhang and Omar Khattab report experiments in which a language model generates or edits another network's numerical weights directly. Some small game networks were generated without running them during construction; other experiments allowed limited evaluations. These edits did not use gradient descent, the usual process of adjusting parameters using calculated directions of improvement.<sup><a href="#source-5">5</a></sup> The language model producing the edits had itself already been trained.

QwenPU supplies a second route: compilation. Its documentation describes additional network layers whose weights encode a processor and a unit for operations on groups of numbers, while the base model's weights remain unchanged. A small language model runs as a program on this constructed processor, with its own weights loaded as data into the processor's memory. The project reports execution checks against a reference implementation.<sup><a href="#source-6">6</a></sup>

Training, direct editing and compilation are different ways to construct a computation. A weight array can be the result of an optimization procedure or the output of a compiler. A neural architecture can execute deliberately specified operations. I describe that mechanism as programmed computation. Calling it “thinking” adds an interpretation; these demonstrations establish programmability, without settling every philosophical definition of thought.

The big deal in these experiments is the concrete demonstration of a view I already held. Learned computations can be represented by small lookup tables, connected in layers and executed in Tau Language. The resulting functions can be examined, and stated properties can be checked.

A lookup table lists an output for each input. Any deterministic function on a finite domain, meaning a finite set of permitted inputs, can be represented this way. If a computation accepts a fixed number of bits and returns a fixed result for each combination, its complete behaviour has a table representation. This also applies to a neural network with fixed parameters and precisely specified execution rules. Any relevant memory or randomness must be fixed or included among the inputs.

Weights, together with the network's operations, determine a function. A complete table can encode exactly that function on the permitted finite inputs. The equivalence concerns the outputs computed, while storage and execution costs can differ substantially. The mathematical statement is general; an experiment checks particular implementations of it.

A mathematical function over arbitrary real numbers does not generally fit into a finite table. Even when a table is finite, it can be impossibly large to store. Representability is a statement about what can be written down in principle, not a claim that doing so is practical.

One enormous table can sometimes be replaced by many small tables whose outputs feed into other tables. Consider a function that reports whether a string of 64 bits contains an odd number of ones. A complete table needs 2⁶⁴ rows. The same function can be computed by 63 two-input XOR tables, each with four rows. XOR returns one when its two inputs differ. Arranged as a balanced tree, those tables need only six layers. Their wiring must also be stored, but the difference in representation is enormous.

That example uses a known construction rather than a learned one. For learned tables, a training procedure selects or adjusts their entries using examples and an objective, such as reducing prediction errors. This is the programming-by-example perspective in action: search for a useful computation within the available architecture. Merely adding layers does not make that search happen or guarantee that it succeeds.

A conventional neural network can approximate a desired mapping, which motivates the “fuzzy lookup table” analogy. It usually evaluates a compact mathematical rule. Numerical weights scale incoming values, and activation functions transform the intermediate results. Training adjusts this computation rather than storing a separate answer for every input. Its behaviour on inputs absent from the training set depends on the resulting function. Interpolation, estimating values between examples, is one possible description of that behaviour, but sensible interpolation is not guaranteed.

A complete lookup table also contains inputs absent from the training set. “Unseen during training” and “missing from the table” are different conditions. Enumerating a trained network records its answers to every permitted input, including answers that may be wrong. The table preserves the learned function; it does not supply missing truth.

Differentiable logic gate networks use a smooth approximation during training and select exact logical operations for execution.<sup><a href="#source-1">1</a></sup> NeuraLUT, by Marta Andronic and George A. Constantinides, trains parts of a neural network and converts their behaviour on permitted inputs into tables for configurable chips. Deeper training networks can become shallower table networks during execution. Its hardware results also show that table-based execution need not be the slower option.<sup><a href="#source-2">2</a></sup>

My interest is in what happens when this meets formal methods: techniques for expressing requirements precisely and checking them mathematically. In the experiments described in my paper, learned tables are encoded as formulas over bits and executed in Tau. The larger networks are divided into smaller specifications, with an external program passing results between them. Tau performs the specified computation within each part.<sup><a href="#source-3">3</a></sup>

A network of 40 tables was trained to decide whether one integer was at least as large as another. Each integer ranged from 0 to 15, giving 256 input pairs. The frozen network, meaning its table values were fixed after training, was checked in both Tau and ZenoFCIS against a separate implementation of the same fixed tables across that complete input domain.

The implementations agreed. They also preserved an error: for A = 0 and B = 1, the network returned the answer corresponding to A ≥ B. It executed the learned function faithfully and gave the wrong answer to the task.<sup><a href="#source-3">3</a></sup>

Those checks establish exact agreement for the frozen table network on the complete tested domain. They do not claim that the smooth approximation used during training and the final discrete tables always have identical outputs. That conversion is a separate comparison. The finite-function result explains why exact tabulation is possible; the experiment records which actual representations were checked.

Deterministic execution and correctness remain different claims. The same specified input and state can reproducibly produce a wrong result. Conventional neural networks can also execute deterministically. A table-based classifier has a restricted set of outputs, such as labels or moves, but restricting the output format does not establish prediction accuracy. Exact conversion of a text generator into tables would preserve its erroneous outputs too. Table representation alone therefore does not eliminate hallucinations.

What attracts me is the possibility of checking a precise requirement over a stated domain. A game policy might be required to select only legal moves. A stronger requirement might be that it never loses from a specified starting position against any legal opposing play. Those are different claims and need different evidence. A proof only establishes the property actually checked, under the assumptions used in the check.

A table can implement an agent's policy: the function that maps an observation, and any required stored state, to an action. The surrounding system supplies observations, maintains state and carries out actions. This description makes agency a question about the system's role and interaction, without attributing human experience to its computational parts.

There is no universal best number of layers. More depth can help represent some functions compactly, while also making training or execution harder. My next useful comparison would hold the total table budget fixed and test different depths, measuring prediction accuracy, execution time and the cost of checking requirements separately. Another direction is to use a failing input returned by a checker to guide a repair, then check the revised system again. These are research proposals, not established results of the current experiments.

My philosophical position remains the one I started with: neural networks are computations, and training is a way of constructing those computations. The table experiments supply concrete implementations and checks consistent with that view. I want to find out how far this approach can go while keeping the representation, the required behaviour and the evidence explicit.

## Sources

1. <a id="source-1"></a> Felix Petersen, Christian Borgelt, Hilde Kuehne and Oliver Deussen. [Deep Differentiable Logic Gate Networks](https://arxiv.org/abs/2210.08277), 2022.
2. <a id="source-2"></a> Marta Andronic and George A. Constantinides. [NeuraLUT: Hiding Neural Network Density in Boolean Synthesizable Functions](https://arxiv.org/abs/2403.00849v2), version 2, 2024. Sections III and IV.
3. <a id="source-3"></a> Dana Edwards. *How Far Can Layered Lookup Tables Go? Learning and checking networks of tables in Tau with execution checks in Tau and ZenoFCIS*. Version 4 manuscript, 2 November 2026. See “Checking one model in Tau and ZenoFCIS” and “Limitations.” The pilot results here refer to that manuscript. The [public preprint record](https://zenodo.org/records/23881061) contained the earlier V1 file when checked on 2 November 2026.
4. <a id="source-4"></a> Sumit Gulwani. [Synthesis from Examples](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/wambse12.pdf), based on the WAMBSE 2012 keynote. Section 1 explains synthesis from example specifications and the ambiguity of incomplete examples.
5. <a id="source-5"></a> Rikiya Takehi, Jayden Teoh, Alex Zhang and Omar Khattab. [Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights](https://rikiyat.github.io/blog/weight-space-programming/), 2 November 2026. Preliminary experiments, with [released logs](https://github.com/RikiyaT/lm_understand-logs). Results are the authors' reports and were not independently reproduced for this essay.
6. <a id="source-6"></a> Divyansh Agrawal. [QwenPU project documentation](https://github.com/divagr18/QwenPU/blob/5af1fc0e0722ad1cc0d983394410c7fc331e08f2/README.md), revision `5af1fc0e0722ad1cc0d983394410c7fc331e08f2`, 31 October 2026. The described execution checks are project-reported; this essay did not rerun them.

## Authorship and AI assistance

The questions, initial concepts and philosophical framing are mine. AI systems generated and revised portions of the prose and assisted with technical source checking. The underlying research also used neurosymbolic tools, which combine learned components with explicit logic. I am responsible for the final text and its interpretation. No AI system is credited as an author.
