---
title: "Microkernels, micro-models, and compositional correctness"
layout: docs
kicker: Tutorial 14
description: Why small trusted kernels and small local formal models can cover more of a real system, using seL4 as a case study in compositional assurance.
---

This tutorial is about a practical scaling trick in formal verification:

> do not try to prove one giant thing all at once if the system can be cut into a small trusted core plus a set of small local models with explicit interfaces.

That is the microkernel idea at the system level, and the micro-model idea at the proof level.

The two ideas fit each other naturally:

- a **microkernel** shrinks the trusted computing base,
- a **micro-model** shrinks one proof obligation,
- explicit interfaces let those local claims compose into wider system assurance.

The case study is **seL4**, which the official project describes as a "high-assurance, high-performance operating system microkernel" that is unique for its comprehensive formal verification (seL4 Project, 2026).

This tutorial makes three scoped claims:

1. Smaller trusted cores make stronger proof obligations tractable.
2. Small local models can capture more system surface area than one monolithic proof attempt, if their interfaces are explicit and checked.
3. Composition is not automatic. Correctness does not snap together by proximity. It requires typed connectors: assumptions, guarantees, initialization conditions, and composition checks.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene for this tutorial</p>
  <ul>
    <li><strong>Assumption A (what "micro-model" means here):</strong> A micro-model is a small formal model, local proof artifact, or narrow invariant ledger for one layer, interface, or component.</li>
    <li><strong>Assumption B (scope of the seL4 case study):</strong> This page uses the official seL4 project pages for high-level proof statements and assumptions, not a full reconstruction of the underlying proof papers.</li>
    <li><strong>Assumption C (composition):</strong> Local correctness does not automatically imply whole-system correctness. Composition requires discharged assumptions between parts.</li>
    <li><strong>Assumption D (surface area):</strong> "Capturing more surface area" means more of the deployed system's behavior is covered by explicit claims, not that every behavior has been fully proved.</li>
  </ul>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Lego, but typed</p>
  <p>
    The Lego metaphor is useful only if it is corrected. Ordinary Lego bricks connect because the plastic geometry matches. Formal components connect only when the assumptions and guarantees match. The studs are contracts, not vibes.
  </p>
</div>

<figure class="fp-figure">
  <p class="fp-figure-title">How small kernels and small models widen assurance</p>
  {% include diagrams/microkernel-micromodel-stack.svg %}
  <figcaption class="fp-figure-caption">
    A small verified kernel anchors the stack. Local models for initialization, access control, protocols, and components expand the covered surface area, but only through checked connectors.
  </figcaption>
</figure>

## Part I: why monolithic verification stalls

One reason full-system verification feels impossible is that large systems entangle too many concerns at once:

- low-level memory behavior,
- scheduling,
- access control,
- IPC and shared resources,
- device interaction,
- initialization,
- application logic,
- deployment configuration.

A monolithic proof attempt asks one formal artifact to carry all of that structure at once. The state space explodes, the assumptions become muddy, and counterexamples become hard to localize.

Microkernels and micro-models attack that problem from two sides.

The system move is:

- keep the kernel small,
- push more services outside the kernel,
- make the kernel's guarantees explicit.

The proof move is:

- prove narrow local claims,
- make their interfaces explicit,
- compose only through checked boundaries.

This does not make verification easy. It makes it decomposable.

## Part II: what a microkernel buys

A microkernel is a small kernel that keeps only the most central mechanisms in the trusted core and pushes more policy and service logic into less trusted space.

That architectural choice matters for verification because proof effort grows quickly with hidden interactions. A smaller kernel means:

- fewer lines of trusted code,
- fewer internal states to model,
- fewer privileged interactions,
- cleaner boundaries between mechanism and policy.

This is exactly why seL4 is such a useful case study. On the official seL4 site, the project emphasizes two points together:

- seL4 is a microkernel,
- seL4 has machine-checked proofs from high-level specifications down to binary code for supported configurations.

That pairing is not an accident. The architectural choice made the proof story stronger.

## Part III: what seL4 proves, at a high level

The official seL4 verification pages describe a proof stack with several top-level properties:

- **functional correctness,**
- **binary correctness,**
- **security enforcement** (integrity, availability, confidentiality),
- **capability distribution** through capDL,
- **initialization correctness,**
- and supporting layers such as design, invariants, and semantics.

The useful teaching point is that this already looks like a collection of micro-models rather than one single flat proof.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Terminology guardrail</p>
  <p>
    The seL4 project does not present these layers under the label "micro-models". That label is this tutorial's teaching lens. The point is not to rename the seL4 proof stack. The point is to show that the stack is layered, local, and interface-sensitive rather than one undifferentiated proof blob.
  </p>
</div>

| Layer or micro-model | Main question | High-level property |
|---|---|---|
| **Specification model** | What should the kernel do? | abstract behavioral contract |
| **C correctness model** | Does the C implementation match the specification? | functional correctness |
| **Binary correctness model** | Does machine code implement the proved C behavior? | binary correctness |
| **Access-control / information-flow model** | Can components interfere or leak information without authorization? | integrity, availability, confidentiality |
| **capDL model** | Is capability distribution configured as intended? | static access-control structure |
| **Initializer model** | Does boot-time setup actually realize the intended configuration? | initialization correctness |

That table is the central lesson of the tutorial. Micro-models are not separate because they are cute. They are separate because each one answers a different question at a different boundary.

## Part IV: one tiny worked composition

The key idea becomes clearer with a tiny system.

Imagine two user-space components on top of seL4:

- a `Sensor` component that collects samples,
- a `Logger` component that stores them.

The desired system property is:

> `Sensor` may send data to `Logger`, but it must not be able to overwrite `Logger` memory directly.

Now split that claim into three local artifacts:

1. **Initialization model `I`:** the capDL configuration gives `Sensor` send rights to endpoint `E`, but no write capability to `LoggerMem`.
2. **Kernel guarantee `K`:** if a component lacks the relevant capability, the kernel will not let it access that object; IPC only follows the rights encoded in capabilities.
3. **Protocol model `P`:** `Logger` updates `LoggerMem` only when it receives a well-formed message on endpoint `E`.

Write the three local claims as:

$$
I \;\vdash\; \neg WriteCap(Sensor, LoggerMem)
$$

$$
K \;\vdash\; \neg WriteCap(c, o) \Rightarrow \neg CanWrite(c, o)
$$

$$
P \;\vdash\; Receive(Logger, E, m) \land WellFormed(m) \Rightarrow Append(LoggerMem, m)
$$

Now the composition steps are visible:

- From `I` and `K`, infer that `Sensor` cannot directly write `LoggerMem`.
- From `I`, `K`, and `P`, infer that any allowed change to `LoggerMem` must come through the approved IPC path and the logger's local protocol.

That is the "Lego" idea in its safe form. No single micro-model proves the whole story. The end-to-end claim appears only after the connectors line up:

- initialization rights,
- kernel enforcement,
- component protocol.

This is also the right way to understand the seL4 case study. The kernel proof is the anchor, not the whole deployment argument.

## Part V: why this captures more surface area

Imagine trying to prove only one theorem:

> "The whole deployed system is correct."

That is too big to be useful unless it is immediately decomposed.

Now compare a layered approach:

1. prove the kernel behaves exactly as specified,
2. prove the binary implements the proved source behavior,
3. prove the access-control model prevents unauthorized interference,
4. prove initialization creates the intended capability layout,
5. then, outside the kernel proof stack itself, prove local component protocols under those kernel guarantees.

Each new local model covers another slice of actual deployed behavior.

That is what "capturing more surface area" should mean here. Not a marketing claim, but a ledger:

- more of the boot path is covered,
- more of the access-control story is covered,
- more of the cross-component isolation story is covered,
- more of the application protocol story is covered.

The important thing is that the surface area grows by adding checked local claims, not by making one theorem statement more ambitious.

## Part VI: the composition rule (why the Lego metaphor needs repair)

This is the point where many explanations go soft.

Micro-models do **not** compose into correctness just because they are small. They compose when their contracts line up.

The abstract shape is assume-guarantee reasoning:

$$
M_1 \models A_1 \Rightarrow G_1
$$

$$
M_2 \models A_2 \Rightarrow G_2
$$

and the composition step needs bridge obligations such as:

$$
G_1 \Rightarrow A_2
\qquad
\text{and}
\qquad
G_2 \Rightarrow A_1
$$

Plain English:

- model 1 guarantees something model 2 needs,
- model 2 guarantees something model 1 needs,
- the wiring is checked rather than assumed.

That is what makes the Lego metaphor safe. The blocks do not snap together because they are small. They snap together because the connector types match.

## Part VII: seL4 as a worked case of compositional assurance

The official seL4 pages make this especially vivid in the move from kernel proofs to system setup.

The security claims are strong, but they are conditional:

- components must be configured correctly,
- isolated components must not be given write access to each other if integrity is desired,
- confidentiality is stated relative to the modeled scheduler and the modeled channels,
- initialization has to realize the intended configuration.

This is exactly what a mature proof story looks like. The project does not say "the kernel is proved, therefore every system built on it is correct." It says, more carefully:

- here is what the kernel guarantees,
- here is what the proof stack assumes,
- here is how configuration and initialization enter the story,
- here is where manual scrutiny still matters.

That is a stronger lesson than a cartoon "fully verified system" slogan.

The seL4 assumptions page makes this explicit. The assumptions include items such as:

- assembly code,
- boot code,
- hardware behavior,
- DMA control,
- and, for confidentiality, limits of the hardware model with respect to side channels.

This is not a weakness in the explanation. It is exactly how trust should be handled. A good proof stack shrinks the place where informal trust must still live, and labels it clearly.

## Part VIII: what the microkernel gives "for free," and what it does not

The seL4 verification pages make a strong point about implications:

- under the stated proof assumptions, functional correctness implies the absence of whole classes of common kernel programming errors,
- under the stated configuration conditions, the isolation properties can be used to run critical components alongside untrusted workloads.

Those are real benefits.

But the microkernel does **not** automatically prove:

- the correctness of arbitrary user-space applications,
- the correctness of every device driver outside the proof boundary,
- the correctness of the deployment configuration unless that configuration is itself covered,
- the absence of every side channel under every hardware detail.

This is exactly why micro-models matter. Once the kernel proof is in place, the next move is not to pretend the job is done. The next move is to place more small models around the system:

- protocol models,
- scheduler assumptions,
- initialization proofs,
- resource-allocation invariants,
- access-control ledgers,
- driver wrappers or device-interface models.

That is how the assurance envelope grows.

## Part IX: a practical recipe for micro-model verification

If the goal is to use this style in a real project, the recipe is:

1. **Shrink the trusted core.**
   Ask what absolutely has to run with full authority.
2. **Write the kernel contract first.**
   What does the core guarantee, and under what assumptions?
3. **Make each boundary explicit.**
   IPC, capabilities, memory ownership, initialization, device access, scheduling.
4. **Give each boundary a local model.**
   One model per interface is often better than one model for the whole subsystem.
5. **Track composition obligations.**
   Every local proof should state what it assumes from its neighbors.
6. **Verify setup, not just behavior.**
   Initialization and configuration are part of the proof story.
7. **Keep an assumption ledger.**
   Hardware, DMA, assembly, side channels, operator inputs, boot chain.

This is the proof-theoretic version of good engineering decomposition. Narrow interfaces do not just help coding. They help trust.

## Part X: where the current tutorial set touches this, and where it does not

The current site already has nearby pieces:

- [Tutorial 5: Reformulation and compression]({{ '/tutorials/reformulation-and-gates/' | relative_url }}) covers decomposition and why smaller interfaces shrink search.
- [Tutorial 6: MPRD and the Algorithmic CEO]({{ '/tutorials/mprd-and-algorithmic-ceo/' | relative_url }}) covers a small logic kernel plus policy gates.
- [Tutorial 11: Church's synthesis problem]({{ '/tutorials/church-synthesis-problem/' | relative_url }}) touches compositional synthesis and assume-guarantee style thinking.

But none of those is a dedicated tutorial on microkernels and micro-model composition as a method for widening verified system coverage.

So the honest answer is:

> adjacent ideas were covered, but this specific tutorial was not.

That is why this page exists.

## Part XI: conclusion

The deep idea is simple:

> strong correctness at scale often comes from many small, explicit truths connected through checked interfaces, not from one giant proof blob.

Microkernels help by shrinking the trusted core.

Micro-models help by shrinking each proof obligation.

Composition is the bridge, but only when the connectors are typed:

- assumptions,
- guarantees,
- initialization conditions,
- and explicit checks that the pieces really fit.

That is the real lesson of the seL4 case study. Not that correctness is easy, and not that one proof solves everything. The lesson is that architecture can make proof more local, trust more visible, and system assurance much wider than a monolithic design would allow.

## References

- seL4 Project (2026) <em>What is seL4?</em> https://sel4.systems/About/
- seL4 Project (2026) <em>Verification</em> https://sel4.systems/Verification/
- seL4 Project (2026) <em>The seL4 Proofs</em> https://sel4.systems/Verification/proofs.html
- seL4 Project (2026) <em>What the Proof Implies</em> https://sel4.systems/Verification/implications.html
- seL4 Project (2026) <em>Assumptions</em> https://sel4.systems/Verification/assumptions.html
