---
title: "Software shapes and ZenoDEX: from arcade common sense to formal assurance"
layout: docs
kicker: Tutorial 17
description: How humans recognize software shapes before learning formal methods, how to turn those shapes into states and invariants, and how ZenoDEX makes one DEX shape explicit across Tau, TLA+, Lean, and runtime code.
---

This tutorial starts from a claim that sounds unorthodox only because it is usually left implicit:

> human engineers often understand the shape of a system before they know the formal language for that shape.

A child in an arcade, a parent using an ATM, and a person buying a drink from a vending machine all build a world model very quickly:

- some actions are allowed only after a gate passes,
- a menu or choice appears only in the right phase,
- a resource is moved or dispensed only under specific conditions,
- the machine resets and becomes ready for the next session.

Most people do not call that a finite state machine. They still track it.

This tutorial makes four scoped claims:

1. Human "common sense" about machines often has the structure of states, transitions, and invariants.
2. Formal methods do not create that structure from nothing. They make it explicit, communicable, and checkable.
3. ZenoDEX is best understood as a software shape expressed across several logic layers, not just as one codebase.
4. Parameter synthesis and software synthesis are different because one searches within a fixed shape, while the other searches over shapes or programs.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene for this tutorial</p>
  <ul>
    <li><strong>Assumption A (what "shape" means):</strong> A shape is an abstraction of states, allowed transitions, invariants, and selection rules. Two systems can share a shape without sharing implementation details.</li>
    <li><strong>Assumption B (source posture):</strong> This page uses the public ZenoDEX repository surface inspected on March 19, 2026, plus an author-supplied shape memo. The public repo snapshot inspected for this tutorial exposed Tau specs, TLA+ shadows, Lean proofs, runtime code, and public assurance scripts, but not the exact <code>docs/zenodex/SHAPING_FORMULAS*.md</code> paths named in the author memo.</li>
    <li><strong>Assumption C (teaching examples):</strong> ATM, arcade, and vending examples are intentionally simplified. They abstract away hardware failure, networking, cash-loading logistics, and social edge cases to reveal the common interaction shape.</li>
    <li><strong>Assumption D (same shape):</strong> "Same shape" means "admits a common abstraction or refinement map", not "is literally the same machine."</li>
  </ul>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Evidence tags used in this tutorial</p>
  <ul>
    <li><code>PROVED</code>: backed by an inspected Lean theorem or algebraic structure.</li>
    <li><code>TLA_SHADOW</code>: backed by an inspected TLA+ shadow model or invariant.</li>
    <li><code>TAU_CONTRACT</code>: backed by an inspected Tau guard or policy contract.</li>
    <li><code>IMPLEMENTED</code>: backed by inspected executable runtime code.</li>
    <li><code>TESTED_DISCOVERY</code>: backed by inspected discovery or experimental code, but not promoted here as a theorem unless explicitly stated.</li>
  </ul>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Compression ladder for this page</p>
  <ul>
    <li><strong>Level 1:</strong> sensory story, what it feels like to use the machine</li>
    <li><strong>Level 2:</strong> abstract phases such as idle, authorized, executing, delivered</li>
    <li><strong>Level 3:</strong> explicit invariants and transition formulas</li>
    <li><strong>Level 4:</strong> refinement maps showing that concrete machines share one shape</li>
    <li><strong>Level 5:</strong> ZenoDEX as a high-assurance instance of the same abstraction move</li>
  </ul>
</div>

## Part I: four ordinary stories that already contain formal structure

Formal methods often sound abstract because they begin with symbols. Human understanding usually begins elsewhere, with light, sound, timing, touch, and expectation.

That is not a weakness. It is the first compression step.

Imagine one ordinary outing.

A parent and child leave an apartment building. The elevator arrives with a soft chime and a brief gust of conditioned air. In the lobby there is a walk to the ATM, where the parent withdraws cash. Later, at the arcade, the child feeds tokens into a cabinet and learns which buttons matter before credit and which matter after. At the end, thirsty and overstimulated, the child stands in front of a humming vending machine, money in hand, waiting for the moment when a drink selection becomes real.

To an adult reader, these scenes feel mundane. To a child, they are thick with pattern. The child is not merely seeing metal, glass, screens, and buttons. The child is learning when a system is ready, what counts as a valid move, what causes a machine to reject, and what completion feels like.

### 1. The arcade

The arcade is loud before anyone reasons about it. The carpet is patterned to hide spills. The cabinets pulse in saturated reds and blues. Music and sound effects overlap. Somewhere in the background there is the metallic click of tokens, the plastic tap of buttons, the short celebratory chirp that means one machine has accepted a credit.

A child does not need the phrase "state transition system" to learn the machine. One or two interactions are enough.

The child sees that pressing the start button before inserting a token does nothing important. The buttons physically move, the machine may flash, but the system has not accepted the action. After the token drops, the cabinet changes behavior. The screen changes. A selection becomes meaningful. The machine that ignored input a second ago now treats the same input as admissible. After the game begins, the "insert token" phase is over and the machine enters a play phase with different rules. When the game ends, scores may be shown, tickets may be printed, lights may return to attract mode, and the machine settles back into the state that waits for the next coin.

That whole experience already contains a rule system:

- no credit, no valid start,
- credit accepted, menu or start enabled,
- game executing, different controls meaningful,
- game over, payout or score displayed,
- reset to idle.

The child may not say any of this aloud. The child still acts as if it is true.

### 2. The ATM

The ATM teaches the same lesson in a quieter register. There is the card slot, the keypad, the brief pause after insertion, the muted beep after each button press, the screen that refuses to reveal the useful menu too early. The machine does not dispense cash because someone is standing in front of it. It dispenses cash only after a very specific gate sequence has succeeded.

Card first. Then PIN. Then account selection. Then withdrawal amount. Then the machine whirs, counts notes, presents cash, optionally prints a receipt, returns the card, and ends the session.

A parent standing at the ATM is tracking much more than a list of steps. The parent has a working model of what must not happen:

- cash must not come out before authentication,
- the main menu must not appear before the card and PIN are accepted,
- a bad PIN does not advance the machine to the withdrawal phase,
- the machine must return to a neutral state after the session ends or times out.

That is already a set of invariants, even if it is not written in that language.

### 3. The elevator

The elevator removes payment, but preserves the shape of guarded phases. There is the soft lamp over the button in the hallway, the arrival chime, the sliding doors, the pause, the slight bodily shift as the cabin begins to move, the silence that means the system is between floors and not available for arbitrary transitions.

Again, almost nobody needs formal training to internalize the rules:

- moving and doors-open do not normally coexist,
- floor selection matters only after entry,
- the car should not jump from one random configuration to another,
- arrival enables a different family of actions than motion does,
- eventually the system returns to an idle waiting condition.

The elevator feels different from the arcade machine and the ATM because the visible resources are different. But the human mind still extracts a stateful control shape from the experience.

### 4. The vending machine

The vending machine brings the pattern into focus because it sits between the toy-like quality of the arcade cabinet and the transactional seriousness of the ATM. There is the fluorescent hum, the cool glass, the spiral coils, the clunk of coins or the short electronic tone that signals a successful card tap. A selection button may be physically pressable at any time, but before credit is accepted the system treats that input as semantically inert. After credit is accepted, the exact same button becomes meaningful.

Then one of three broad things happens:

- the machine accepts the choice and vends,
- the machine rejects the choice because the credit is insufficient,
- the machine rejects the choice because the slot is empty or the item is unavailable.

If the vend succeeds, there is the spiral turn, the drop, the mechanical thud in the tray, maybe the return of change, and then the machine resets to the idle posture in which the next customer starts from scratch.

The sequence is sensory, but the understanding is structural.

### What these stories already taught

These four machines are not the same device. They do not move the same resource. They do not run on the same hardware. Their failure modes differ.

Still, a person who has experienced them has already learned a shared control pattern:

- there is an idle state,
- some gate moves the machine into an enabled state,
- only then does choice become meaningful,
- execution changes the admissible actions,
- delivery or completion happens after execution,
- reset returns the machine to a reusable baseline.

That is why ordinary experience so often precedes formal notation. The shape is learned first; the mathematical language arrives later.

## Part II: the shared shape under the sensory detail

The stories above differ in texture, but they share a common abstraction.

| Concrete machine | Gate | Choice phase | Execution phase | Delivery or completion | Reset |
|---|---|---|---|---|---|
| Arcade cabinet | token or session credit accepted | start or mode select | live gameplay | score, prize, or game over screen | return to attract mode |
| ATM | card plus PIN accepted | account and amount selection | withdrawal or transfer processing | cash, receipt, balance update, card return | session close or timeout |
| Elevator | call accepted, doors open, entry complete | floor button selection | motion between floors | arrival and door open | idle at floor, awaiting next call |
| Vending machine | money or card accepted | item selection | motor turn and vend attempt | item drop, change return, or reject message | credit cleared, ready for next user |

This table is a compression artifact. It throws away:

- cabinet art,
- cash dispenser hardware,
- elevator cable dynamics,
- vending coil geometry,
- all the social and physical context around the machines.

What remains is the shape that matters for the current reasoning question.

This is the first major tutorial claim stated sharply:

> humans often perform a shape-preserving abstraction in their heads long before they can write the abstraction down.

## Part III: turning a shape into states

A generic "gated transaction machine" can be modeled as

$$
M = (Q, q_0, \Sigma, \to, I)
$$

where:

- $Q$ is a set of states,
- $q_0$ is the initial state,
- $\Sigma$ is the set of actions or events,
- $\to$ is the transition relation,
- $I$ is a set of invariants.

For teaching purposes, it helps to make the machine state slightly more explicit. Let the current state record be

$$
\sigma = (\text{state}, \text{authorized}, \text{choice}, \text{resource\_ok}, \text{delivered})
$$

with

$$
\text{state} \in Q_{\text{shape}}.
$$

One useful shared archetype is:

$$
Q_{\text{shape}} =
\{
\text{Idle},
\text{Authorized},
\text{ChoiceReady},
\text{Executing},
\text{Delivered},
\text{Resetting}
\}
$$

with a transition skeleton:

$$
\text{Next}
:=
\text{Authorize}
\vee \text{PresentChoices}
\vee \text{Reject}
\vee \text{Choose}
\vee \text{Execute}
\vee \text{Deliver}
\vee \text{Reset}
$$

The abstract transition clauses can be written more concretely:

$$
\text{Authorize}
:=
(\text{state} = \text{Idle})
\wedge \text{GateSatisfied}
\wedge (\text{state}' = \text{Authorized})
\wedge (\text{authorized}' = 1)
$$

$$
\text{PresentChoices}
:=
(\text{state} = \text{Authorized})
\wedge \text{MenuOrControlSurfaceReady}
\wedge (\text{state}' = \text{ChoiceReady})
$$

$$
\text{Reject}
:=
(\text{state} \in \{\text{Idle}, \text{Authorized}, \text{ChoiceReady}\})
\wedge \text{BadInput}
\wedge (\text{state}' = \text{Idle})
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
\wedge \text{resource\_ok}
\wedge (\text{state}' = \text{Delivered})
$$

$$
\text{Deliver}
:=
(\text{state} = \text{Delivered})
\wedge \text{ResourceTransferred}
\wedge (\text{delivered}' = 1)
$$

$$
\text{Reset}
:=
(\text{state} \in \{\text{Delivered}, \text{Resetting}\})
\wedge (\text{state}' = \text{Idle})
\wedge (\text{authorized}' = 0)
\wedge (\text{delivered}' = 0)
$$

The invariants then look less like vague English and more like reusable laws:

$$
\text{ChooseOnlyWhenReady}
:=
\text{Choose} \rightarrow (\text{state} = \text{ChoiceReady})
$$

$$
\text{AuthorizationPrecedesChoice}
:=
(\text{state} \in \{\text{ChoiceReady}, \text{Executing}, \text{Delivered}, \text{Resetting}\})
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

$$
\text{ResetReturnsToIdle}
:=
\text{Reset} \rightarrow \text{state}' = \text{Idle}
$$

Machine-specific formulas are then obtained by instantiating the generic symbols.

For the arcade cabinet:

$$
\text{StartRequiresCredit}
:=
\text{StartPressed} \rightarrow \text{credit} > 0
$$

For the ATM:

$$
\text{CashOnlyAfterAuth}
:=
\text{cashDispensed} \rightarrow (\text{authenticated} \wedge \text{fundsApproved})
$$

For the elevator:

$$
\text{MovingImpliesDoorsClosed}
:=
\text{moving} \rightarrow \text{doorsClosed}
$$

For the vending machine:

$$
\text{VendOnlyIfPaidAndStocked}
:=
\text{vend} \rightarrow (\text{credit} \ge \text{price}(\text{choice}) \wedge \text{stocked}(\text{choice}))
$$

The distinction between `Authorized` and `ChoiceReady` is deliberate. In many real systems, passing the gate and exposing the usable control surface are not the same event.

- At an ATM, the card and PIN may be accepted before the menu is fully rendered.
- In an elevator, entering the car and having the floor buttons active are close, but still conceptually distinct.
- In a vending machine, credit may be recorded before the machine confirms that a selection is currently available.

Keeping those phases separate makes the shape more expressive without making it large.

Now the three everyday machines become instances of the same archetype:

- **ATM:** authorization is card plus PIN, choice is menu selection, delivery is cash and receipt, reset is session end.
- **Vending machine:** authorization is coin, bill, or card acceptance, choice is product selection, delivery is the dispensed item, reset is credit clearing.
- **Arcade machine:** authorization is token, card, or session credit, choice is game start or selection, delivery is gameplay or prize logic, reset is end-of-session state.

This is the point at which intuition becomes portable. Once the shape has been named, it can be shared, criticized, and reused.

## Part IV: how to prove two machines have the same shape

It is not enough to say "these feel similar." Formal methods need a sharper statement.

Let $A$ be an abstract shape machine, and let $M_1$ and $M_2$ be concrete machines. A useful definition is:

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

This says there is an abstraction map $\alpha$ from concrete states to shape states that preserves:

- the start state,
- the allowed transitions,
- the relevant invariants.

Then a perfectly respectable "same shape" theorem is:

$$
\text{HasShape}(M_1, A) \wedge \text{HasShape}(M_2, A)
\rightarrow
\text{SameShape}(M_1, M_2; A)
$$

That is the formal version of the intuition that ATMs and vending machines "work the same way" at the level that matters for the current reasoning task.

For transition systems, a stronger and more standard formulation uses a refinement or simulation relation. Let

$$
R \subseteq Q_M \times Q_A.
$$

Then

$$
\text{Refines}(M,A;R)
:=
R(q_0^M,q_0^A)
\wedge
\forall q_M,q_M',q_A.\;
\bigl(R(q_M,q_A) \wedge q_M \to_M q_M'\bigr)
\rightarrow
\exists q_A'.\; q_A \to_A q_A' \wedge R(q_M',q_A')
$$

together with invariant lifting:

$$
\forall q_M,q_A.\; R(q_M,q_A) \wedge I_M(q_M) \rightarrow I_A(q_A).
$$

This version makes the teaching point sharper. The claim is not "these two machines feel similar." The claim is:

> every concrete move of the machine can be matched by a move in the abstract shape machine, and every relevant invariant survives the abstraction.

To make that less abstract, here is a toy abstraction map for the vending machine:

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

For the ATM:

$$
\alpha_{\text{atm}}(q) =
\begin{cases}
\text{Idle} & \text{if } q \in \{\text{WelcomeScreen}, \text{CardInserted}\} \\
\text{Authorized} & \text{if } q = \text{PinAccepted} \\
\text{ChoiceReady} & \text{if } q \in \{\text{MainMenu}, \text{AmountMenu}\} \\
\text{Executing} & \text{if } q \in \{\text{AuthorizingWithdrawal}, \text{CountingCash}\} \\
\text{Delivered} & \text{if } q \in \{\text{CashPresented}, \text{ReceiptPresented}\} \\
\text{Resetting} & \text{if } q = \text{SessionClosing}
\end{cases}
$$

For the elevator:

$$
\alpha_{\text{lift}}(q) =
\begin{cases}
\text{Idle} & \text{if } q \in \{\text{WaitingAtFloor}, \text{HallCallLit}\} \\
\text{ChoiceReady} & \text{if } q \in \{\text{DoorsOpen}, \text{FloorButtonsEnabled}\} \\
\text{Executing} & \text{if } q \in \{\text{DoorsClosing}, \text{Moving}, \text{Braking}\} \\
\text{Delivered} & \text{if } q = \text{ArrivedDoorsOpen} \\
\text{Resetting} & \text{if } q = \text{DoorTimeoutReturn}
\end{cases}
$$

These maps are deliberately coarse. That is the point. They show how many concrete states can preserve one abstract shape.

For example:

- many detailed ATM states refine to one abstract `ChoiceReady` phase,
- several elevator control states refine to one abstract `Executing` phase,
- many arcade animation and attract-mode states refine to one abstract `Idle` phase.

This is the mathematical content behind the phrase "same shape."

It also explains why the shape lets one move from intuition to proof. Suppose the abstract machine proves

$$
\text{DeliverOnlyAfterExecute}.
$$

If the vending implementation refines that abstract machine through $\alpha_{\text{vend}}$, then the concrete claim

$$
\text{ItemDropped} \rightarrow \text{PreviouslyMotorTurning}
$$

is no longer just a story about coils and metal spirals. It is a lifted consequence of the shared shape plus the refinement relation.

The shape is not the metal box. The shape is the abstract rule system.

## Part V: compression by abstraction

One reason engineers reach for shapes is compression.

A real machine or codebase may have thousands of implementation details, but a reasoning task usually cares about only some of them. Abstraction compresses the description by forgetting irrelevant detail while preserving the structure needed for the current question.

This is not magic, and it is not free. It is a scoped forgetting operation.

That scope matters. A good abstraction is always relative to a question.

- If the question is "can cash be dispensed before authentication?", the ATM abstraction may erase the printer model and still be excellent.
- If the question is "how does the receipt jam?", the same abstraction is useless.

Compression is therefore not merely shorter description. It is shorter description that still preserves the property under study.

If a concrete system has state space $Q_{\text{concrete}}$ and an abstract shape has state space $Q_{\text{abstract}}$, then a shape-preserving abstraction is a map

$$
\alpha : Q_{\text{concrete}} \to Q_{\text{abstract}}
$$

such that the transitions and invariants that matter are preserved:

$$
q \to_{\text{concrete}} q'
\Rightarrow
\alpha(q) \to_{\text{abstract}} \alpha(q')
$$

and

$$
I_{\text{concrete}}(q)
\Rightarrow
I_{\text{abstract}}(\alpha(q)).
$$

Many concrete states may collapse to one abstract phase. That is exactly what makes the description shorter.

For example, an ATM may have dozens of concrete display and device states:

- card half-inserted,
- card fully read,
- PIN entry first digit entered,
- PIN entry second digit entered,
- balance screen showing,
- printer warming,
- cash cassette spinning,
- receipt offered,
- timeout countdown active.

For one reasoning task, many of these can be collapsed into a much smaller abstract partition such as:

$$
\{
\text{Idle},
\text{Authenticated},
\text{ChoiceReady},
\text{Executing},
\text{Completed}
\}.
$$

The abstraction is powerful because it says: all of those implementation details differ, but for this property they behave as one shape state.

An equivalent way to say this is that abstraction induces an equivalence relation:

$$
q_1 \sim_{\text{shape}} q_2
\iff
\alpha(q_1) = \alpha(q_2)
$$

and the abstract machine is the quotient by that relation.

If $\varphi$ is an abstract property, the whole point of compression is that proving $\varphi$ on the abstract machine should still say something real about the concrete one. A common soundness shape is:

$$
\text{Refines}(M,A;R) \wedge A \models \varphi
\rightarrow
M \models \varphi^\uparrow
$$

where $\varphi^\uparrow$ is the lifting of the abstract property back to the concrete system through the abstraction.

This is the formal reason compression is useful rather than merely pretty.

That is how a large software surface can be compressed into a handful of formulas without becoming meaningless. The abstraction preserves the shape that matters for the current proof obligation.

For the vending-machine family, a large amount of hardware and UI detail can collapse into:

- gated authorization,
- bounded choice,
- controlled execution,
- resource delivery,
- reset.

For ZenoDEX, a much larger software surface can be compressed, for one teaching purpose, into:

$$
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
\text{StablecoinSolvency}.
$$

That does not replace the code. It compresses the code into a shape-preserving description at the right level of abstraction.

This is why a few sentences of logic can sometimes say more, for a particular reasoning task, than a large implementation codebase. The logic is shorter because it has factored out details that do not matter to the selected property.

The danger, of course, is over-compression. If the abstraction forgets the very detail that makes a bug possible, the shape has become too coarse. Good engineering abstraction is therefore a balance:

- compress enough to make reasoning possible,
- preserve enough to keep the claim true.

That balancing act is one of the deepest shared skills between mathematicians, software engineers, and protocol designers.

## Part VI: the ZenoDEX move

ZenoDEX takes this same move and raises the assurance level.

The public repository inspected for this tutorial shows at least these layers directly:

- `TAU_CONTRACT`: boundary guards in `src/tau_specs/recommended/*.tau`
- `TLA_SHADOW`: temporal shadow models in `formal/tla/*.tla`
- `PROVED`: Lean proofs in `lean-mathlib/Proofs/*.lean`
- `IMPLEMENTED`: deterministic runtime arithmetic in `src/core/*.py`

One author-supplied full-shape summary is:

```text
Shape(ZenoDEX)
:= BoundaryValidity
 ∧ TemporalAdmissibility
 ∧ CanonicalWinnerSelection
 ∧ ReserveMonotonicity
 ∧ SettlementCompositionality
 ∧ DeterministicRouting
 ∧ StablecoinSolvency
```

That is a better teaching lens than "it is a DEX with some proofs."

As a teaching surface, each clause can be read as a compressed theorem-shaped target:

$$
\text{BoundaryValidity}
:=
\forall t.\; \text{Accepted}(t) \rightarrow \text{GuardsPass}(t)
$$

$$
\text{TemporalAdmissibility}
:=
\forall s,s'.\; \text{Step}(s,s') \rightarrow \text{AllowedByTemporalModel}(s,s')
$$

$$
\text{CanonicalWinnerSelection}
:=
\forall S.\; \text{Finite}(S) \wedge S \neq \varnothing
\rightarrow
\exists! w \in S.\; \forall x \in S,\; \text{key}(w) \le \text{key}(x)
$$

$$
\text{ReserveMonotonicity}
:=
\forall \text{valid swaps}.\; K_{\text{after}} \ge K_{\text{before}}
$$

$$
\text{SettlementCompositionality}
:=
\forall s_1,s_2.\; \Delta(s_1 \circ_s s_2) = \Delta(s_1) + \Delta(s_2)
$$

$$
\text{DeterministicRouting}
:=
\forall i.\; \exists! r.\; r = \text{BestRoute}(i)
$$

$$
\text{StablecoinSolvency}
:=
\forall v.\; \text{debt}(v)=0 \vee \text{collateral}(v)\cdot \text{price} \ge \text{debt}(v)\cdot 10^8
$$

The point of the compression is that these formulas sit at a level where a reader can still see the system's skeleton. The full repository then refines each clause into more detailed guards, theorems, transition rules, and arithmetic kernels.

It says the system shape is spread across several logic surfaces:

- Tau guards decide which proposed transitions are admissible at the boundary.
- TLA+ shadows describe allowed evolution over time.
- Lean theorems prove algebraic and canonicalization properties.
- Runtime code computes exact integer transitions that must match the guarded and proved surface.

This is why the system is best taught as a stack of linked shapes rather than a bag of modules.

## Part VII: concrete ZenoDEX formulas that show the shape

Four inspected examples are enough to show the pattern.

### 1. Reserve monotonicity (`TAU_CONTRACT`, `IMPLEMENTED`)

From the Tau reserve invariant guard:

$$
K_{\text{after}} \ge K_{\text{before}}
$$

and from the runtime CPMM implementation:

$$
\text{fee\_total} = \left\lceil \frac{\text{amount\_in} \cdot \text{fee\_bps}}{10000} \right\rceil
$$

$$
\text{net\_in} = \text{amount\_in} - \text{fee\_total}
$$

$$ 
\text{amount\_out}
=
\left\lfloor
\frac{\text{reserve\_out} \cdot \text{net\_in}}
{\text{reserve\_in} + \text{net\_in}}
\right\rfloor
$$

$$
\text{reserve\_in}' = \text{reserve\_in} + \text{amount\_in}
\qquad
\text{reserve\_out}' = \text{reserve\_out} - \text{amount\_out}
$$

so that

$$
K_{\text{before}} = \text{reserve\_in}\cdot\text{reserve\_out}
\qquad
K_{\text{after}} = \text{reserve\_in}'\cdot\text{reserve\_out}'.
$$

with post-state reserves satisfying the same monotonicity check.

That is not merely "swap code." It is a shape clause:

> valid swaps must preserve or increase the protected reserve product.

### 2. Temporal admissibility (`TLA_SHADOW`)

From `formal/tla/AutoTraderNonceGuardShadow.tla`:

```text
Next := Accept ∨ RejectStale ∨ RejectGap
```

with

```text
Accept
:= ∃ n.
     n = lastUsedNonce + 1
   ∧ lastUsedNonce' = n
   ∧ accepted' = TRUE
```

and

```text
RejectStale
:= ∃ n.
     n ≤ lastUsedNonce
   ∧ lastUsedNonce' = lastUsedNonce
   ∧ accepted' = FALSE
```

and an invariant such as:

```text
NonceNeverDecreases := lastUsedNonce ≥ prevLastUsedNonce
```

This is the time-evolution version of the same idea. Not every transition is allowed. Some traces are ruled out by construction.

### 3. Settlement compositionality (`PROVED`)

From `lean-mathlib/Proofs/SettlementAlgebra.lean`:

$$
\Delta(s_1 \circ_s s_2) = \Delta(s_1) + \Delta(s_2)
$$

This is a compositionality shape:

> a property of the pieces lifts to a property of the composition.

Once that is proved, reasoning about batches and larger executions becomes much cleaner.

### 4. Canonical winner selection (`PROVED`, `TAU_CONTRACT`, `IMPLEMENTED`)

In ZenoDEX, batch outcomes, routing choices, and certificate-carrying selections are not only valid or invalid. They also need deterministic tie-breaks and canonical winners.

The logic surface behind that can be summarized as:

$$
\exists! k \in S.\; \forall x \in S,\; \text{key}(k) \le \text{key}(x)
$$

implemented concretely through key comparison, lexicographic tie-breaks, and emitted certificates.

In words, the formula says more than "pick a winner." It says:

- the candidate set is finite and nonempty,
- exactly one element is canonical under the chosen order,
- every other candidate loses by an explicit comparison rule.

That is a very different shape from "pick any good enough answer."

This is an important DEX shape because it prevents "same input, many admissible winners" from turning into ambiguity or replay disagreement.

## Part VIII: symbolic representation of shapes as states

A useful way to formalize engineering progress is to treat a system's shape as a state in an assurance space.

Let the property alphabet be:

$$
\mathcal{P}
=
\{
\text{deterministic},
\text{replayable},
\text{partiallyProved},
\text{stronglyGuarded},
\text{canonical},
\text{exact},
\text{valueAware},
\text{proofCarrying},
\text{crossLayerEquivalent},
\text{failClosedEverywhereImportant}
\}
$$

Then define:

$$
\text{ShapeState}(M) \subseteq \mathcal{P}
$$

This says a system's shape can be modeled as the set of currently achieved properties.

A more exact set-theoretic form is:

$$
\text{ShapeState}(M)
:=
\{\, p \in \mathcal{P} \mid p(M) \,\}.
$$

Equivalently, one can spell the shape state as a conjunction of predicates:

$$
\text{ShapeState}(M)
:=
\text{Deterministic}(M)
\wedge
\text{Replayable}(M)
\wedge
\text{PartiallyProved}(M)
\wedge
\text{StronglyGuarded}(M)
\wedge \cdots
$$

For ZenoDEX, the author-supplied current state is:

```text
CurrentShape
:= deterministic
 ∧ replayable
 ∧ partiallyProved
 ∧ stronglyGuarded
```

which can be written predicate-style as

$$
\text{CurrentShape}(Z)
:=
\text{Deterministic}(Z)
\wedge
\text{Replayable}(Z)
\wedge
\text{PartiallyProved}(Z)
\wedge
\text{StronglyGuarded}(Z).
$$

and the target state is:

```text
TargetShape
:= canonical
 ∧ exact
 ∧ valueAware
 ∧ proofCarrying
 ∧ crossLayerEquivalent
 ∧ failClosedEverywhereImportant
```

or, more formally,

$$
\text{TargetShape}(Z)
:=
\text{Canonical}(Z)
\wedge
\text{Exact}(Z)
\wedge
\text{ValueAware}(Z)
\wedge
\text{ProofCarrying}(Z)
\wedge
\text{CrossLayerEquivalent}(Z)
\wedge
\text{FailClosedEverywhereImportant}(Z).
$$

Those larger predicates can themselves be unpacked:

$$ 
\text{ProofCarrying}(Z)
:=
\forall t.\; \text{Accepted}(t) \rightarrow \exists c.\; \text{Cert}(c,t) \wedge \text{Check}(c,t)=1
$$

$$
\text{ValueAware}(Z)
:=
\forall s,\pi.\;
\text{ConservedValue}_{\pi}(s)
\rightarrow
\sum_a \pi(a)\cdot \Delta_a(s) = 0
$$

$$
\text{CrossLayerEquivalent}(Z)
:=
\forall i.\;
\text{Obs}_{\tau}(i)
=
\text{Obs}_{\mathrm{TLA}}(i)
=
\text{Obs}_{\mathrm{Lean}}(i)
=
\text{Obs}_{\mathrm{runtime}}(i)
$$

$$
\text{FailClosedEverywhereImportant}(Z)
:=
\forall t.\; \text{Critical}(t) \wedge \text{UnknownOrAmbiguous}(t) \rightarrow \text{Reject}(t)
$$

These are not just slogans. They suggest concrete engineering work:

- **canonical** means no ambiguous winners,
- **exact** means the arithmetic and certificates line up with the intended semantics,
- **value-aware** means raw token arithmetic is not confused with value conservation,
- **proof-carrying** means execution comes with checkable evidence,
- **cross-layer equivalent** means Tau, TLA+, Lean, and runtime code agree on the same shape,
- **fail-closed important** means unsafe ambiguity shuts the system down or blocks the transition instead of "best-effort" guessing.

That turns "software shaping" into a state-transition problem over assurance properties.

One clean way to express "moving toward the target shape" is with a strength preorder on shape predicates:

$$
S_1 \preceq S_2
\iff
\forall M.\; S_2(M) \rightarrow S_1(M).
$$

Here, $S_2$ is at least as strong as $S_1$ because every machine that satisfies $S_2$ also satisfies $S_1$.

For ZenoDEX, the intended refinement direction can then be written as:

$$
\text{StrengthenedShape}(M)
:=
\text{CurrentShape}(M)
\wedge
\text{Canonical}(M)
\wedge
\text{Exact}(M)
\wedge
\text{ValueAware}(M)
\wedge
\text{ProofCarrying}(M)
\wedge
\text{CrossLayerEquivalent}(M)
\wedge
\text{FailClosedEverywhereImportant}(M)
$$

and then

$$
\text{CurrentShape} \preceq \text{StrengthenedShape}.
$$

In words, adding the target clauses produces a stronger assurance shape, not merely a different slogan. It is strictly stronger if at least one added clause is not already implied by the current shape.

## Part IX: what human thought experiments are doing

When an engineer asks:

- what if the nonce repeats?
- what if the routing tie occurs?
- what if the oracle is stale?
- what if two settlements compose in the wrong order?

the engineer is usually doing one of three things:

1. sampling traces,
2. testing invariants,
3. searching for counterexamples.

That is already a semi-formal activity.

The difference is that informal thought experiments are private and lossy. Formal tools externalize them.

### Tau

Tau turns a boundary condition into an executable guard.

### TLA+

TLA+ turns "what sequences of states are allowed?" into an explicit temporal model.

### Lean

Lean turns algebraic claims such as compositionality, canonicality, or exactness into checkable theorems.

### ICE-style invariant synthesis

ICE-style invariant synthesis sits in between. It tries to infer a formula from examples, counterexamples, and implication constraints. That is a mechanical version of what engineers often do mentally when they say:

> there is clearly some rule here, but the exact invariant is not yet written down.

This is one of the best ways to describe the relationship between intuition and formal methods:

> formal tools do not replace the shape intuition, they stabilize and sharpen it.

### A worked example, double spending

This is easier to see on a famous protocol problem.

A human engineer thinking about Bitcoin-like money quickly lands on a shape rule such as:

$$
\text{NoDoubleSpend}
:=
\forall o.\; \text{SpentCount}(o) \le 1
$$

or, more operationally,

$$
\text{ValidSpend}(tx,o)
\rightarrow
\neg \exists tx' \neq tx.\; \text{ConfirmedSpend}(tx',o).
$$

Before that rule is written formally, the engineer often runs a thought experiment:

- what if the same output is referenced twice?
- what if two conflicting spends race?
- what if one branch confirms and another branch also appears valid locally?

That is already an attack search over traces. In transition-system form, the undesirable state is simply:

$$
\text{Bad}
:=
\exists o,tx_1,tx_2.\;
tx_1 \neq tx_2
\wedge
\text{ConfirmedSpend}(tx_1,o)
\wedge
\text{ConfirmedSpend}(tx_2,o).
$$

Then the engineering problem becomes:

$$
\text{Init} \wedge []\text{Next} \models \neg \text{Bad}.
$$

One can approach that problem informally, by disciplined human reasoning, or mechanically, by model exploration, invariant generation, theorem proving, or synthesis. The mental move is the same. The formal tool simply makes the move public and checkable.

## Part X: the DEX shape and the vending-machine shape

It would be wrong to say that a DEX is "just a vending machine." The state space is much richer, the value semantics are trickier, and the adversarial surface is far larger.

It would be reasonable to say something narrower:

> the same human capacity that recognizes the gated transaction shape of a vending machine can also recognize the higher-assurance transaction shape of a DEX.

The DEX version simply adds:

- adversarial inputs,
- richer canonicalization rules,
- stronger conservation and solvency constraints,
- cross-layer equivalence obligations,
- certificate and replay requirements.

So the everyday machines and the DEX do not share the same *complexity*. They share the same *kind of abstraction move*.

## Part XI: parameter synthesis versus software synthesis

This distinction matters a great deal in high-assurance systems.

### Parameter synthesis

Parameter synthesis assumes the program shape is fixed and searches for values that make it safe or optimal:

$$
\exists \theta \in \Theta.\;
\text{Spec}(P,\theta)
\wedge
\text{Objective}(P,\theta)
$$

In a higher-assurance reading, the quantifier shape is often really:

$$
\exists \theta \in \Theta.\;
\forall \tau \in \text{Traces}(P,\theta),\;
\text{Safe}(\tau)
\wedge
\text{MeetsObjective}(\theta).
$$

The program skeleton is fixed. The transition graph is mostly fixed. The search is over parameters that make the fixed shape behave acceptably.

Examples in a DEX or stablecoin context include:

- fee rates,
- collateral ratios,
- timelock lengths,
- routing caps,
- liquidation penalties,
- bounded registry parameters.

The transition structure is mostly fixed. The search is over numbers.

### Software synthesis

Software synthesis searches over programs or transition systems themselves:

$$
\exists P \in \mathcal{S}.\; \text{Spec}(P)
$$

For safety-critical systems, that usually expands to:

$$
\exists P \in \mathcal{S}.\;
\forall \tau \in \text{Traces}(P),\;
\text{Safe}(\tau)
\wedge
\text{Goal}(\tau).
$$

Here the search space includes control flow, state structure, protocol rules, and sometimes the very shape of the machine.

Examples include:

- inventing a new routing procedure,
- synthesizing a settlement algorithm,
- deriving a new guarded transition policy,
- discovering a better canonicalization rule.

That distinction can be stated plainly:

> parameter synthesis tunes a shape, while software synthesis searches over shapes.

One useful mnemonic is the quantifier boundary:

- parameter synthesis, "find the numbers for this machine,"
- software synthesis, "find the machine."

For ZenoDEX, both matter. Parameter synthesis can improve a verified mechanism without changing its structure. Software synthesis is needed when the structure itself is still under design.

## Takeaway

Humans often learn machine shapes before they learn the language of state machines, temporal logic, or proof assistants. A child at an arcade, a parent at an ATM, and a person at a vending machine already track gates, menus, execution phases, and resets.

Formal methods make that implicit shape public.

ZenoDEX is a useful teaching case because it lets the same idea be seen at several assurance levels at once:

- boundary guards in Tau,
- temporal admissibility in TLA+,
- algebraic and canonical theorems in Lean,
- exact integer execution in runtime code,
- replayable public assurance on top.

That is why "software shape" is not merely a metaphor here. It is an engineering object:

$$
\text{states} + \text{transitions} + \text{invariants} + \text{selection rules} + \text{evidence}
$$

Once that object is explicit, it can be shared, critiqued, proved, synthesized, and improved.
