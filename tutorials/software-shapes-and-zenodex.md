---
title: "Software shapes and ZenoDEX: from arcade common sense to formal assurance"
layout: docs
kicker: Tutorial 17
description: How humans recognize software shapes before learning formal methods, how to turn those shapes into states and invariants, and how ZenoDEX makes one shape explicit across Tau, TLA+, Lean, and runtime code.
---

A child drops a token into an arcade cabinet and learns, without any formal training, one of the deepest patterns in computing: some actions do nothing until the right gate has been passed.

The child does not know the phrase "state machine." But after two rounds the child acts on a precise set of rules -- and the rules turn out to be correct.

This tutorial is about that moment of recognition. Humans build working models of machines -- gates, phases, transitions, resets -- long before they encounter the notation. Formal methods do not invent these structures. They make implicit structures explicit, communicable, and checkable.

The concrete vehicle is ZenoDEX, a decentralized exchange whose design is spread across four logic layers: Tau boundary guards, TLA+ temporal models, Lean algebraic proofs, and exact integer runtime code. Before we reach ZenoDEX, we start where the intuition starts: at an arcade, an ATM, an elevator, and a vending machine.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Scope and assumptions</p>
  <ul>
    <li><strong>Shape</strong> means an abstraction of states, transitions, invariants, and selection rules. Two systems share a shape without sharing implementation details.</li>
    <li><strong>Source posture:</strong> ZenoDEX observations are based on the public repository surface inspected on March 19, 2026, plus a shape memo prepared for this tutorial. The snapshot exposed Tau specs, TLA+ shadows, Lean proofs, runtime code, and public assurance scripts.</li>
    <li><strong>Teaching examples</strong> (ATM, arcade, elevator, vending machine) are intentionally simplified -- they abstract away hardware failure, networking, and social edge cases to reveal the common interaction shape.</li>
    <li><strong>Evidence tags:</strong> <code>PROVED</code> = inspected Lean theorem. <code>TLA_SHADOW</code> = inspected TLA+ model. <code>TAU_CONTRACT</code> = inspected Tau guard. <code>IMPLEMENTED</code> = inspected runtime code. <code>TESTED_DISCOVERY</code> = inspected discovery code, not promoted to theorem.</li>
  </ul>
</div>

## Part I: four ordinary machines that already contain formal structure

Formal methods often sound abstract because they begin with symbols. Human understanding usually begins elsewhere -- with light, sound, timing, and expectation.

That is not a weakness. It is the first compression step.

Imagine a single outing. A parent and child leave an apartment building. The elevator arrives with a soft chime. In the lobby, the parent stops at the ATM for cash. Later, at the arcade, the child feeds tokens into a cabinet and learns which buttons matter before credit and which matter after. At the end, thirsty and overstimulated, the child stands in front of a humming vending machine, money in hand, waiting for the moment a drink selection becomes real.

These scenes feel mundane to an adult. To a child, they are thick with pattern. The child is not merely seeing metal, glass, and buttons -- the child is learning when a system is ready, what counts as a valid move, what causes rejection, and what completion feels like.

### 1. The arcade cabinet

The arcade is loud before anyone reasons about it. The carpet is patterned to hide spills. Cabinets pulse in saturated reds and blues. Sound effects overlap. Somewhere in the background there is the metallic click of tokens, the plastic tap of buttons, a short celebratory chirp that means one machine has accepted a credit.

A child needs one or two interactions to learn the machine.

Pressing the start button before inserting a token does nothing meaningful. The button physically moves, the cabinet may flash, but the system has not accepted the action. After the token drops, the cabinet changes. The screen shifts. A selection becomes meaningful. The machine that ignored input a moment ago now treats the same button press as admissible. Once the game begins, the "insert token" phase is over and a play phase with different rules takes its place. When the game ends -- scores shown, tickets printed, lights returning to attract mode -- the machine settles back to the state that waits for the next coin.

That whole experience already contains a rule system:

- no credit → no valid start,
- credit accepted → menu or start enabled,
- game executing → different controls meaningful,
- game over → payout or score displayed,
- reset to idle.

The child may never say any of this aloud. The child still acts as if it is true.

### 2. The ATM

The ATM teaches the same lesson in a quieter register. There is the card slot, the keypad, the brief pause after insertion, the muted beep after each digit. The screen refuses to show the useful menu too early. The machine does not dispense cash because someone is standing in front of it. It dispenses cash only after a specific gate sequence has succeeded: card, PIN, account selection, amount confirmation.

Then the machine whirs, counts notes, presents cash, optionally prints a receipt, returns the card, and ends the session.

A parent standing at the ATM is tracking more than a list of steps. The parent has a working model of what *must not* happen:

- cash must not come out before authentication,
- the main menu must not appear before the card and PIN are accepted,
- a wrong PIN must not advance the machine to the withdrawal phase,
- the machine must return to a neutral state when the session ends or times out.

That is already a set of safety invariants, even if it is never written in that language.

### 3. The elevator

The elevator removes payment but preserves the shape of guarded phases. There is the hallway button, the arrival chime, the sliding doors, the pause, the slight bodily shift as the cabin begins to move, and the silence between floors that means the system is in transit and unavailable for arbitrary transitions.

Almost nobody needs formal training to internalize the rules:

- moving and doors-open do not normally coexist,
- floor selection matters only after entry,
- the car does not jump from one arbitrary configuration to another,
- arrival enables a different set of actions than motion does,
- eventually the system returns to an idle waiting state.

The elevator feels different from the ATM because the visible resources are different. But the human mind still extracts a stateful control shape from the experience.

### 4. The vending machine

The vending machine brings the pattern into sharpest focus because it sits between the toy-like quality of the arcade cabinet and the transactional seriousness of the ATM. There is the fluorescent hum, the cool glass front, the spiral coils behind it, the clunk of coins or the short electronic tone of a successful card tap. A selection button may be physically pressable at any time, but before credit is accepted the system treats that press as meaningless. After credit is accepted, the exact same button becomes meaningful.

Then one of three things happens: the machine accepts the choice and vends, it rejects because the credit is insufficient, or it rejects because the slot is empty. If the vend succeeds, there is the spiral turn, the drop, the thud in the tray, maybe change returned, and then the machine resets to idle for the next customer.

The sequence is sensory. The understanding is structural.

Try it yourself -- this interactive vending machine shows the formal specification behind every button press:

<figure class="fp-figure">
  <p class="fp-figure-title">Interactive: a vending machine with live state and formulas</p>
  <iframe
    src="{{ '/vending_machine_explorer.html' | relative_url }}"
    title="Interactive vending machine with state machine and formula display"
    data-fp-resize="true"
    data-fp-min-height="900"
    style="width: 100%; min-height: 900px; border: 0; border-radius: 16px; background: transparent;"
    loading="lazy"></iframe>
  <figcaption class="fp-figure-caption">
    Insert coins, select a product, and watch the state machine highlight which phase you are in.
    The active formulas and invariants update in real time, connecting the sensory experience to its formal skeleton.
  </figcaption>
</figure>

### What these four stories already taught

These machines are not the same device. They do not move the same resource, run on the same hardware, or fail in the same way.

Yet a person who has used all four has already learned a shared control pattern:

- there is an idle state,
- some gate moves the machine into an enabled state,
- only then does choice become meaningful,
- execution changes the admissible actions,
- delivery or completion follows execution,
- reset returns the machine to a reusable baseline.

That is why ordinary experience so often precedes formal notation. The shape is learned first; the mathematical language arrives later.

## Part II: the shared shape under the sensory detail

The stories above differ in texture, but they share a common abstraction. The diagram below shows the skeleton; the table fills in what each machine puts into each slot.

<div class="fp-diagram">
  {% include diagrams/software-shapes-gated-transaction.svg %}
</div>

| Machine | Gate | Choice phase | Execution | Delivery | Reset |
|---|---|---|---|---|---|
| **Arcade** | token accepted | game or mode select | live gameplay | score or prize | return to attract mode |
| **ATM** | card + PIN accepted | account and amount | withdrawal processing | cash, receipt, card return | session close |
| **Elevator** | call accepted, entry | floor selection | motion between floors | arrival, doors open | idle at floor |
| **Vending** | coin/card accepted | item selection | motor turn, vend attempt | item drop, change return | credit cleared |

This table is a compression artifact. It discards cabinet art, cash-dispenser hardware, elevator cable dynamics, and vending-coil geometry. What remains is the structure that matters for the current reasoning task.

That leads to the first major claim of this tutorial:

> Humans routinely perform shape-preserving abstraction in their heads long before they can write it down in any formal language.

## Part III: turning a shape into states and formulas

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Reading the formulas</p>
  <p>
    A primed variable like <code>state'</code> denotes the value of that variable in the <em>next</em> state.
    So <code>state' = Authorized</code> means "after this transition, the state becomes Authorized."
    The symbol ∧ means "and," ∨ means "or," → means "implies," and ∀ means "for all."
  </p>
</div>

The informal pattern from Part I can be written as a transition system. Let a *gated transaction machine* be

$$
M = (Q, \; q_0, \; \Sigma, \; \to, \; I)
$$

where $Q$ is a set of states, $q_0$ is the initial state, $\Sigma$ is the set of actions, $\to$ is the transition relation, and $I$ is a set of invariants. The current state record is

$$
\sigma = (\text{state}, \; \text{authorized}, \; \text{choice}, \; r_{\mathrm{ok}}, \; \text{delivered})
$$

Here \(r_{\mathrm{ok}}\) means the execution resource check passed.

For the shared archetype from Part I, the abstract state set is:

$$
Q_{\text{shape}} =
\{
\text{Idle},\;
\text{Authorized},\;
\text{ChoiceReady},\;
\text{Executing},\;
\text{Delivered},\;
\text{Resetting}
\}
$$

with a transition skeleton:

$$
\text{Next}
:=
\text{Authorize}
\vee \text{PresentChoices}
\vee \text{Choose}
\vee \text{Execute}
\vee \text{Deliver}
\vee \text{Reset}
\vee \text{Reject}
$$

Four representative transition clauses show the pattern -- each is a precondition on the current state, an action guard, and a postcondition on the next state:

$$
\text{Authorize}
:=
(\text{state} = \text{Idle})
\wedge \text{GateSatisfied}
\wedge (\text{state}' = \text{Authorized})
\wedge (\text{authorized}' = 1)
$$

$$
\text{Choose}
:=
(\text{state} = \text{ChoiceReady})
\wedge \text{ChoiceValid}
\wedge (\text{state}' = \text{Executing})
\wedge (\text{choice}' = \text{requestedChoice})
$$

$$
\text{Execute}
:=
(\text{state} = \text{Executing})
\wedge r_{\mathrm{ok}}
\wedge (\text{state}' = \text{Delivered})
$$

$$
\text{Reset}
:=
(\text{state} \in \{\text{Delivered}, \text{Resetting}\})
\wedge (\text{state}' = \text{Idle})
\wedge (\text{authorized}' = 0)
\wedge (\text{delivered}' = 0)
$$

The remaining clauses -- PresentChoices, Deliver, Reject -- follow the same precondition/action/postcondition pattern.

The invariants now look like reusable laws rather than vague English:

$$
\text{ChooseOnlyWhenReady}
:=
\text{Choose} \rightarrow (\text{state} = \text{ChoiceReady})
$$

$$
\text{AuthorizationPrecedesChoice}
:=
(\text{state} \in \{\text{ChoiceReady}, \text{Executing}, \text{Delivered}\})
\rightarrow
\text{authorized}
$$

$$
\text{ExecuteOnlyWhenAuthorized}
:=
\text{Execute} \rightarrow \text{authorized}
$$

$$
\text{DeliverOnlyAfterExecute}
:=
\text{delivered} \rightarrow (\text{state} \in \{\text{Delivered}, \text{Resetting}\})
$$

These abstract invariants instantiate into concrete rules for each machine:

| Machine | Invariant instance |
|---|---|
| **Arcade** | $\text{StartPressed} \rightarrow \text{credit} > 0$ |
| **ATM** | $\text{cashDispensed} \rightarrow (\text{authenticated} \wedge \text{fundsApproved})$ |
| **Elevator** | $\text{moving} \rightarrow \text{doorsClosed}$ |
| **Vending** | $\text{vend} \rightarrow (\text{credit} \ge \text{price}(\text{choice}) \wedge \text{stocked}(\text{choice}))$ |

The distinction between `Authorized` and `ChoiceReady` is deliberate. In many real systems, passing the gate and exposing the usable control surface are not the same event. At an ATM, the card and PIN may be accepted before the menu finishes rendering. In a vending machine, credit may register before the machine confirms which slots are available. Keeping those phases separate makes the shape more precise without making it large.

## Part IV: proving two machines share a shape

It is not enough to say "these feel similar." Formal methods need a sharper statement.

Let $A$ be an abstract shape machine, and let $M$ be a concrete machine. The claim that $M$ "has shape $A$" means:

$$
\text{HasShape}(M, A)
:=
\exists \alpha : Q_M \to Q_A.\;
\alpha(q_0^M) = q_0^A
\;\wedge\;
(q \to_M q' \Rightarrow \alpha(q) \to_A \alpha(q'))
\;\wedge\;
(I_M(q) \Rightarrow I_A(\alpha(q)))
$$

The function $\alpha$ is an *abstraction map*. It sends each concrete state to an abstract phase, and it preserves three things: the start state, the allowed transitions, and the relevant invariants.

Two machines share a shape when both refine the same abstraction:

$$
\text{HasShape}(M_1, A) \wedge \text{HasShape}(M_2, A)
\rightarrow
\text{SameShape}(M_1, M_2; A)
$$

That is the formal version of the intuition that ATMs and vending machines "work the same way" at the right level of abstraction.

### A worked abstraction map: the vending machine

<div class="fp-diagram">
  {% include diagrams/software-shapes-abstraction-map.svg %}
</div>

To make this concrete, here is an abstraction map from a detailed vending-machine model to the gated-transaction shape:

$$
\alpha_{\text{vend}}(q) =
\begin{cases}
\text{Idle} & \text{if } q \in \{\text{AttractScreen}, \text{AwaitingCoin}, \text{CreditZero}\} \\
\text{ChoiceReady} & \text{if } q \in \{\text{CreditPositive}, \text{SelectionEnabled}\} \\
\text{Executing} & \text{if } q \in \{\text{MotorTurning}, \text{VendAttempt}\} \\
\text{Delivered} & \text{if } q \in \{\text{ItemDropped}, \text{ChangeReturning}\} \\
\text{Resetting} & \text{if } q = \text{ClearingSession}
\end{cases}
$$

The map is deliberately coarse. That is the point. Many concrete states -- attract screen, awaiting coin, credit zero -- collapse into a single abstract `Idle` phase because they behave identically with respect to the property under study.

Similar maps exist for the ATM (where `WelcomeScreen` and `CardInserted` both map to `Idle`, and `MainMenu` and `AmountMenu` both map to `ChoiceReady`) and the elevator (where `DoorsClosing`, `Moving`, and `Braking` all map to `Executing`). The details differ, but the structure is the same: many concrete states refine to a handful of abstract phases.

### Why compression matters

This coarsening is not merely cosmetic. It has a formal payoff. If the abstract machine proves a property $\varphi$, and the concrete machine refines it through $\alpha$, then $\varphi$ lifts back to the concrete system:

$$
\text{HasShape}(M, A) \wedge A \models \varphi
\rightarrow
M \models \varphi^{\uparrow}
$$

where $\varphi^{\uparrow}$ is the lifted property -- the abstract claim rewritten in terms of concrete states.

For example, suppose the abstract machine proves $\text{DeliverOnlyAfterExecute}$. For the vending machine, this lifts to:

$$
\text{ItemDropped} \rightarrow \text{PreviouslyMotorTurning}
$$

That is no longer just a story about coils and spirals. It is a *consequence* of the shared shape plus the refinement relation.

The danger is over-compression. If the abstraction forgets the very detail that makes a bug possible, the shape has become too coarse. Good engineering abstraction is a balance: compress enough to make reasoning feasible, preserve enough to keep the claim true.

## Part V: the ZenoDEX shape

The move from a vending machine to a decentralized exchange is a jump in complexity, not a jump in kind.

It would be wrong to say that a DEX is "just a vending machine." The state space is richer, the value semantics are harder, and the adversarial surface is vastly larger. But it would be fair to say this:

> The same human capacity that recognizes the gated-transaction shape of a vending machine can also recognize the higher-assurance transaction shape of a DEX.

The DEX version adds adversarial inputs, richer canonicalization rules, conservation and solvency constraints, cross-layer equivalence obligations, and certificate requirements. The machines do not share the same *complexity*. They share the same *kind of abstraction move*.

### The assurance stack

ZenoDEX makes this move visible by distributing its shape across four logic layers. Each layer is responsible for a different kind of assurance:

<div class="fp-diagram">
  {% include diagrams/software-shapes-zenodex-stack.svg %}
</div>

- **Tau boundary guards** (`TAU_CONTRACT`): the gatekeepers. A proposed transition either passes or does not -- no ambiguity, no "best effort."
- **TLA+ temporal shadows** (`TLA_SHADOW`): describe how the system is allowed to evolve over time. They catch temporal violations -- stale nonces, ordering anomalies, illegal sequences.
- **Lean algebraic proofs** (`PROVED`): establish structural properties -- compositionality, canonicality, conservation. Mathematical guarantees that hold regardless of input.
- **Runtime integer code** (`IMPLEMENTED`): computes exact transitions that must match the guarded and proved surface. This is where the formulas meet real arithmetic.

The full shape, as summarized in our shape memo, is:

$$
\text{Shape(ZenoDEX)}
:=
\text{BoundaryValidity}
\wedge
\text{TemporalAdmissibility}
\wedge
\text{CanonicalWinnerSelection}
\wedge
\text{ReserveMonotonicity}
\wedge
\text{SettlementCompositionality}
\wedge
\text{DeterministicRouting}
\wedge
\text{StablecoinSolvency}
$$

That is a better teaching lens than "it is a DEX with some proofs." Each clause names a compressed theorem target. The following sections expand four of them from the inspected repository.

### Reserve monotonicity (`TAU_CONTRACT`, `IMPLEMENTED`)

The Tau reserve-invariant guard states:

$$
K_{\text{after}} \ge K_{\text{before}}
$$

The runtime CPMM implements this through exact integer arithmetic:

$$
f_{\mathrm{total}} = \left\lceil \frac{a_{\mathrm{in}} \cdot f_{\mathrm{bps}}}{10000} \right\rceil
\qquad
n_{\mathrm{in}} = a_{\mathrm{in}} - f_{\mathrm{total}}
$$

$$
a_{\mathrm{out}}
=
\left\lfloor
\frac{r_{\mathrm{out}} \cdot n_{\mathrm{in}}}
{r_{\mathrm{in}} + n_{\mathrm{in}}}
\right\rfloor
$$

$$
K_{\text{before}} = r_{\mathrm{in}} \cdot r_{\mathrm{out}}
\qquad
K_{\text{after}} = (r_{\mathrm{in}} + a_{\mathrm{in}})\cdot(r_{\mathrm{out}} - a_{\mathrm{out}})
$$

Here \(a_{\mathrm{in}}\) and \(a_{\mathrm{out}}\) are input and output amounts, \(f_{\mathrm{bps}}\) is the fee rate in basis points, \(f_{\mathrm{total}}\) is the rounded fee, \(n_{\mathrm{in}}\) is net input, and \(r_{\mathrm{in}}, r_{\mathrm{out}}\) are reserves.

This is not merely "swap code." It is a shape clause: valid swaps must preserve or increase the protected reserve product.

### Temporal admissibility (`TLA_SHADOW`)

From `formal/tla/AutoTraderNonceGuardShadow.tla`:

```text
Next := Accept ∨ RejectStale ∨ RejectGap

Accept
:= ∃ n.
     n = lastUsedNonce + 1
   ∧ lastUsedNonce' = n
   ∧ accepted' = TRUE

RejectStale
:= ∃ n.
     n ≤ lastUsedNonce
   ∧ lastUsedNonce' = lastUsedNonce
   ∧ accepted' = FALSE

NonceNeverDecreases := lastUsedNonce ≥ prevLastUsedNonce
```

This is the time-evolution version of the same idea. Not every transition is admissible. Some traces are ruled out by construction -- a stale nonce cannot sneak past a monotonic guard.

### Settlement compositionality (`PROVED`)

From `lean-mathlib/Proofs/SettlementAlgebra.lean`:

$$
\Delta(s_1 \circ_s s_2) = \Delta(s_1) + \Delta(s_2)
$$

This is a compositionality shape: a property of the parts lifts to a property of their combination. Once proved, reasoning about batched settlements becomes much simpler -- verify the pieces, and the composition holds automatically.

### Canonical winner selection (`PROVED`, `TAU_CONTRACT`, `IMPLEMENTED`)

Batch outcomes, routing decisions, and certificate-carrying selections in ZenoDEX must be deterministic. The selection rule is:

$$
\exists! k \in S.\; \forall x \in S,\; \text{key}(k) \le \text{key}(x)
$$

This says more than "pick a winner." It says the candidate set is finite and nonempty, exactly one element is canonical under the chosen order, and every other candidate loses by an explicit comparison rule. That determinism prevents "same input, multiple valid winners" from turning into replay disagreement.

### Where the shape is today, and where it is going

<div class="fp-diagram">
  {% include diagrams/software-shapes-strengthening.svg %}
</div>

The current assurance state is:

$$
\text{CurrentShape}(Z) :=
\text{Deterministic}(Z)
\wedge \text{Replayable}(Z)
\wedge \text{PartiallyProved}(Z)
\wedge \text{StronglyGuarded}(Z)
$$

The target state adds six clauses:

- **Canonical:** no ambiguous winners.
- **Exact:** arithmetic and certificates match intended semantics.
- **Value-aware:** token arithmetic is not confused with value conservation.
- **Proof-carrying:** execution comes with checkable evidence.
- **Cross-layer equivalent:** Tau, TLA+, Lean, and runtime code agree on the same observable behavior.
- **Fail-closed where it matters:** unsafe ambiguity blocks the transition rather than guessing.

Moving from current to target is a *strengthening* -- each added clause imposes a strictly tighter constraint. That turns "software shaping" from a metaphor into a measurable engineering trajectory.

## Part VI: from thought experiments to formal tools

When an engineer asks "what if the nonce repeats?" or "what if two settlements compose in the wrong order?", the engineer is already doing something semi-formal: sampling traces, testing invariants against them, and searching for counterexamples.

The difference is that informal thought experiments are private and lossy. Each formal tool externalizes a different piece of the reasoning:

- **Tau** turns a boundary condition into an executable guard. A proposed transition either passes or does not.
- **TLA+** turns "which sequences of states are allowed?" into an explicit temporal model that can be explored mechanically.
- **Lean** turns algebraic claims -- compositionality, canonicality, exactness -- into theorems that a kernel checks down to its axioms.
- **ICE-style invariant synthesis** sits in between. It tries to infer a formula from examples, counterexamples, and implication constraints -- a mechanical version of what engineers do mentally when they say "there is clearly some rule here, but the exact invariant is not yet written down."

The relationship between intuition and these tools is not replacement. It is stabilization:

> Formal tools do not replace the shape intuition. They stabilize it and make it checkable.

### A worked example: double spending

A human engineer thinking about Bitcoin-like digital money quickly lands on a shape rule:

$$
\text{NoDoubleSpend}
:=
\forall o.\; \text{SpentCount}(o) \le 1
$$

Before writing that formula, the engineer usually runs a thought experiment: what if the same output is referenced twice? What if two conflicting spends race? What if one branch confirms while another also appears locally valid?

That is already an attack search over traces. In transition-system language, the undesirable state is:

$$
\text{Bad}
:=
\exists o,\, tx_1,\, tx_2.\;
tx_1 \neq tx_2
\wedge
\text{ConfirmedSpend}(tx_1,o)
\wedge
\text{ConfirmedSpend}(tx_2,o)
$$

and the engineering problem becomes:

$$
\text{Init} \wedge \Box\,\text{Next} \models \neg \text{Bad}.
$$

One can approach this informally, by disciplined reasoning, or mechanically, by model checking, invariant generation, or theorem proving. The mental move is the same. The formal tool makes the move public, repeatable, and checkable by anyone who reads the spec.

## Part VII: parameter synthesis versus software synthesis

This distinction matters greatly in high-assurance systems, and it is often confused.

### Parameter synthesis: tuning a fixed shape

Parameter synthesis assumes the program shape is fixed and searches for values that make it safe or optimal:

$$
\exists \theta \in \Theta.\;
\forall \tau \in \text{Traces}(P, \theta).\;
\text{Safe}(\tau)
\wedge
\text{MeetsObjective}(\theta)
$$

The program skeleton is fixed. The transition graph is mostly fixed. The search is over numbers: fee rates, collateral ratios, timelock lengths, routing caps, liquidation penalties.

### Software synthesis: searching over shapes

Software synthesis searches over programs or transition systems themselves:

$$
\exists P \in \mathcal{S}.\;
\forall \tau \in \text{Traces}(P).\;
\text{Safe}(\tau)
\wedge
\text{Goal}(\tau)
$$

The search space includes control flow, state structure, and protocol rules. Examples include inventing a new routing procedure, synthesizing a settlement algorithm, or discovering a better canonicalization rule.

### The quantifier boundary

A useful mnemonic is the location of the existential quantifier:

- **Parameter synthesis:** "find the numbers for this machine."
- **Software synthesis:** "find the machine."

For ZenoDEX, both activities matter. Parameter synthesis can improve a verified mechanism without changing its structure. Software synthesis is needed when the structure itself is still under design.

## Part VIII: shape your own system

The interactive explorer below turns the ideas from this tutorial into a choose-your-own-adventure experience. You start with a bare system skeleton and make design choices, each one adds states, transitions, or invariants to the shape. The formulas update as you go, showing how engineering decisions transform a system's formal structure.

<figure class="fp-figure">
  <p class="fp-figure-title">Interactive: shape evolution explorer</p>
  <iframe
    src="{{ '/shape_evolution_explorer.html' | relative_url }}"
    title="Interactive shape evolution explorer, choose your own adventure through formal system design"
    data-fp-resize="true"
    data-fp-min-height="920"
    style="width: 100%; min-height: 920px; border: 0; border-radius: 16px; background: transparent;"
    loading="lazy"></iframe>
  <figcaption class="fp-figure-caption">
    Start with a minimal system and make design choices. Each choice morphs the shape, adding
    states, strengthening invariants, or introducing new formal layers. Watch the transition
    diagram and formula panel evolve as your decisions accumulate.
  </figcaption>
</figure>

## Takeaway

A child at an arcade, a parent at an ATM, a person waiting for an elevator, each one learns the shape of a state machine without ever hearing the term. Gates, phases, transitions, invariants, and resets are not inventions of formal methods. They are patterns that human minds extract from ordinary experience.

Formal methods make those patterns explicit. Once explicit, a shape can be shared across a team, criticized by a reviewer, checked by a solver, and proved by a kernel.

ZenoDEX is a useful teaching case because it lets that same idea be seen at several assurance levels simultaneously: boundary guards in Tau, temporal models in TLA+, algebraic theorems in Lean, and exact integer execution in runtime code. Each layer formalizes a different facet of the same underlying shape.

That is why "software shape" is not a metaphor in this tutorial. It is an engineering object:

$$
\text{states} + \text{transitions} + \text{invariants} + \text{selection rules} + \text{evidence}
$$

Once that object is explicit, it can be shared, critiqued, proved, synthesized, and improved, by anyone, for any machine, at any level of assurance.
