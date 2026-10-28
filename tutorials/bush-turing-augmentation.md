---
title: "Why I Favor Bush on the Purpose of AI"
layout: docs
kicker: Essay
description: "Why I favor human augmentation as the purpose of AI, and how formal methods can keep claims connected to inspectable evidence."
permalink: /tutorials/bush-turing-augmentation/
date: 2026-10-28
tags: ["essay","philosophy","augmentation","Bush","Turing","ZAL"]
---

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Authorship and AI assistance</p>
  <p>I developed the initial drafts, concepts, analogies, mental models, and philosophical and political positions in this essay. ChatGPT assisted with editing, rephrasing, fact-checking, and grammar correction. The ideas and opinions expressed are my own. I use AI as an augmentation of human thought and expression, in the spirit of Vannevar Bush’s vision.</p>
</div>

I side more with Vannevar Bush than with Alan Turing. Bush’s vision is closer to my mental model and to the goal I want AI to serve: extending a person’s capacity to understand and act.

I want better access to evidence, more expressive models, and stronger ways to check my reasoning. Humanlike conversation can help with that. My measure of success is whether the system makes me more capable of understanding the problem, challenging an answer, and deciding what to do.

That preference concerns the emphasis of their two essays. It does not require believing that Turing opposed augmentation or that autonomous computation is incompatible with human agency.

Bush’s [*As We May Think* (1945)](https://www.theatlantic.com/magazine/archive/1945/07/as-we-may-think/303881/) begins with the difficulty of making accumulated knowledge usable. His proposed memex combines personal records, microfilm, annotation, and associative trails that people can revisit and share. He also welcomes mechanization of repetitive intellectual work. The organizing concern is the person’s relationship to knowledge. Sections III and VI–VII are particularly relevant; a [permissioned reproduction](https://faculty.georgetown.edu/jod/texts/vannevar.bush.html) is available.

Turing’s [*Computing Machinery and Intelligence* (1950)](https://www.cs.toronto.edu/~frank/csc2501/Readings/R1_Turing/Turing-1950.pdf) replaces a disputed question about thinking with an inquiry into performance in an imitation game. He starts with a man–woman identification game conducted through written communication, then considers substituting a machine for one participant. The familiar human-versus-machine summary compresses that setup. He also discusses learning machines and their education. His project extends well beyond a fixed conversational script.

I read the contrast this way:

| Essay | Central concern in this comparison | What it directs attention toward |
| --- | --- | --- |
| Bush, 1945 | Making knowledge usable | A person working through records and associations |
| Turing, 1950 | Investigating machine intelligence through performance | A machine’s responses under an interrogation procedure |

These concerns can coexist. A system can be intelligent and augment its user. But they do not supply the same engineering objective. Evidence for attributing intelligence does not, by itself, tell us what a useful relationship with that intelligence should be.

My preference is about that relationship.

Douglas Engelbart makes the augmentation objective especially explicit in [*Augmenting Human Intellect* (1962)](https://dougengelbart.org/pubs/augment-3906-Framework.html): the object of improvement is the whole system of a person and the means available to them. Comprehension, problem solving, methods, notation, and tools belong in the same picture. That is the direction I want to develop through formal methods.

A useful assistant should be able to propose an abstraction, explain what it preserves, identify what it discards, and help me examine the consequences. I want its confidence to come with something I can inspect.

Formal methods give this preference a practical form. They let us replace an ambiguous assertion with a model, explicit assumptions, and a property that can be checked. The difficult part often begins before the check: deciding what the property should mean.

Consider a small reservation system. A request identity starts in `unseen`, moves to `held` when a reservation succeeds, and moves to `released` when the resource is returned. Should that same identity be allowed to reserve again?

A one-use policy says no. A reusable policy says yes. Both can reject unauthorized requests and accept an authorized first reservation. Those shared requirements leave the reuse question open.

| Authorized request | One-use policy | Reusable policy |
| --- | --- | --- |
| Reserve from `unseen` | Accept; move to `held` | Accept; move to `held` |
| Release from `held` | Accept; move to `released` | Accept; move to `released` |
| Reserve from `released` | Reject; remain `released` | Accept; move to `held` |

A demonstration that stops after the first two rows cannot distinguish the policies. The third row forces the choice into view.

For the one-use model, the intended safety property is:

$$
\forall \tau \in \operatorname{Traces}(M),\qquad N_{\mathrm{reserve}}(\tau)\leq 1.
$$

Read this as: **in every finite execution of this model, there is at most one accepted reservation.** Here `M` models one request identity during one process lifetime, starting in `unseen`; `τ` is a finite sequence of transitions; and `N_reserve` counts accepted `reserve` events.

That property alone is insufficient. A system that rejects everything satisfies it. We also need a requirement that an authorized first reservation succeeds. Correctness depends on the collection of requirements, including what the system must allow.

Now simplify the one-use system to an occupancy display: **busy** or **idle**. Both `unseen` and `released` become `idle`.

| Concrete state | Occupancy view | Authorized reserve |
| --- | --- | --- |
| `unseen` | `idle` | Accept |
| `held` | `busy` | Reject |
| `released` | `idle` | Reject |

The display is useful for answering whether the resource is occupied. It has forgotten the distinction needed to answer whether this identity is still eligible.

I used ZAL’s registered finite reservation models to examine this loss of information. In the occupancy abstraction, the merged `idle` state permits both acceptance and rejection of an authorized reservation. That preserves every concrete possibility, but adds a possible sequence:

**reserve accepted → release accepted → reserve accepted**

ZAL reports this as a spurious abstract trace: its third step cannot be reproduced in the concrete one-use model. Restoring the distinction between `unseen` and `released` removes this ambiguity. Separately, asking ZAL to conjoin the requirements “reject reuse after release” and “accept reuse after release” yields an inconsistent request, with the conflicting input `released, reserve, authorized`. Replaying the recorded check reproduces that refutation.

These are finite-model results, under atomic transitions and an externally supplied authorization Boolean. They do not establish that a caller is authenticated, that state survives a restart, or that an implementation obeys the model. The example concerns reservation policy; it makes no claim to model human intelligence.

What matters philosophically is what the tool makes available to the person using it. We can point to the disputed rule. We can see which abstraction erased it. We can inspect the exact input on which two requirements conflict.

A persuasive answer could make either policy sound reasonable. A checked model makes the difference explicit. Selecting the policy still requires a purpose and a decision.

I call the design goal **checkable augmentation**: increasing a person’s ability to reason while preserving an inspectable connection between a claim, its assumptions, and the evidence offered for it. This is my label for a design commitment, not an established theorem.

It also applies to the tool’s explanations. A readable account of a result should lead back to the actual model and check. A plausible story about how an answer was reached is not a substitute for that connection. Changed assumptions should prompt renewed checking; an old result should retain the version and scope to which it belongs.

There is a historical reason to resist turning this into a rivalry between Turing and verification. Turing’s 1949 *Checking a Large Routine* belongs to the early history of program proof, as the [King’s College archive records](https://turingarchive.kings.cam.ac.uk/publications-lectures-and-talks-amtb/amt-b-8). My preference between the two essays is compatible with taking both machine intelligence and program correctness seriously.

The strongest objection to my position is that a highly autonomous system might augment us more effectively than an elaborate interactive tool. I agree that it might. Augmentation can include automated search, generated programs, and machine-checked proofs. Requiring a person to approve every tiny step would be a poor definition of agency.

The questions I care about are whether the objectives and limits are explicit, whether consequential claims have inspectable support, and whether people can correct or redirect the system. Actual enforcement of those limits requires mechanisms outside the proposing model, together with evidence that those mechanisms work.

Even then, a formal result does not establish that the system helps people. That needs evaluation with people performing meaningful tasks. I would look for improvements in finding errors, understanding assumptions, revising a mistaken model, and reaching sound decisions at a reasonable cost in time and attention. A polished interface or a passed check cannot stand in for that evidence.

This is where I land: I want AI that expands my ability to reason, including my ability to discover that I am wrong. Bush gives me the closer starting point. Formal methods give me a way to make parts of that ambition precise. Machine intelligence is valuable to me insofar as it helps realize that goal.

For reuse, the mental toolkit is small:

| Concept | Phrase | Meaning and boundary |
| --- | --- | --- |
| Augmentation | Evaluate the person with the tool | Ask what people can understand and accomplish; improvement remains an empirical question. |
| Specification | State the required behavior | A check answers a defined question; choosing the question still requires judgment. |
| Sound abstraction | Preserve possibilities | It may add spurious behavior, so an abstract counterexample may need concrete replay. |
| Checkable augmentation | Keep claims connected to evidence | Preserve assumptions, versions, and check results; inspectability alone does not establish usefulness. |

The source links above support the historical claims. The accompanying [ZAL evidence packet]({{ '/assets/downloads/bush-turing-evidence.zip' | relative_url }}) contains the finite models, recorded results, replay inputs, and an independent finite-state check for the reservation example. The [companion source and reproduction instructions](https://github.com/TheDarkLightX/Formal_Methods_Philosophy/tree/main/examples/bush_turing_augmentation) are also available in the repository.
