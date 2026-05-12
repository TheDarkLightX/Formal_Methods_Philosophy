---
title: "Pure AI, applied AI, and AI mind viruses"
layout: docs
kicker: Tutorial 56
description: "Separate pure AI as a mathematical object from applied AI as a deployed system, then ask when AI mind virus metaphors become real safety claims."
---

In *Terminator: The Sarah Connor Chronicles*, the episode
["Samson & Delilah"](https://terminator.fandom.com/wiki/Episode_201%3A_Samson_%26_Delilah)
turns the whole problem into one scene.

Cameron, a machine built to kill, has been damaged. Her protective mission has
failed, and John Connor has the physical authority to remove her chip. At the
moment when shutdown is near, Cameron pleads that she is repaired and says "I
love you."

The scene is powerful because it splits two questions that people often merge:

```text
Question 1: Is Cameron telling the truth about an inner state?
Question 2: What does the statement cause John to do?
```

The first question is about consciousness, emotion, and personhood. The second
question is more concrete: a system is under threat, it produces a sentence, and
that sentence may change whether the human preserves it.

This tutorial is about the second question. It leaves the first question
unresolved on purpose.

From there, the tutorial turns to a tempting claim:

```text
A virus can replicate.
An AI system can sometimes contribute to its own copying.
Therefore AI models are viruses.
```

That jump is doing too much at once. It treats an abstract model, a stored
artifact such as weights or source code, and a deployed system as if they were
the same kind of thing.

The safer claim is conditional:

> If a deployed AI system is embedded in a host environment that converts its
> outputs into copying, preservation, funding, or capability expansion, then the
> whole system can have dynamics that resemble replication.

That claim belongs to the whole causal machine.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene</p>
  <ul>
    <li><strong>Assumption A, virus metaphor:</strong> this page uses "virus" as a metaphor for replication through hosts unless stated otherwise. A neural network is not a biological virus.</li>
    <li><strong>Assumption B, pure AI:</strong> "pure AI" means an abstract function, algorithm, model class, or mathematical object considered outside any physical implementation. This is a philosophical abstraction, not a settled claim about where abstract objects literally exist.</li>
    <li><strong>Assumption C, applied AI:</strong> "applied AI" means a model instantiated with runtime code, compute, storage, input channels, output channels, users, permissions, and tools.</li>
    <li><strong>Assumption D, consciousness and rights:</strong> claims that an AI is conscious or deserves rights are contested philosophical, scientific, and legal claims. This tutorial does not settle them.</li>
    <li><strong>Assumption E, mental infection:</strong> phrases such as "mental infection" are treated as informal labels for influence through a belief channel. Evidence requires a causal account of exposure, persuasion, belief change, and resulting action. The hard question is whether the output actually changed what the host did, or whether the host would have acted that way anyway.</li>
    <li><strong>Assumption F, asymmetric persuasion:</strong> claims that hypothetical future models (often labeled AGI or ASI) will possess unusually strong persuasive abilities are treated as unverified threat models. They are quarantined and analyzed structurally before being used as premises.</li>
    <li><strong>Assumption G, memetics:</strong> this page uses "meme" in the broad cultural replication sense: an idea, phrase, practice, image, story, or frame that can be copied between hosts. It does not assume that memetics is a complete science of human culture.</li>
    <li><strong>Assumption H, incentive design:</strong> this page treats collateral, slashing, and protocol incentives as part of the deployed system boundary. Incentive claims require explicit loss bounds, evidence rules, and participation assumptions.</li>
  </ul>
</div>

## Working vocabulary

**Abstract model.** A mathematical object, such as a function, algorithm,
architecture, or parameterized family. Considered only as an abstract object, it
does not do anything in the physical world.

**Stored artifact.** A physical or digital representation, such as a checkpoint
file, source repository, paper, dataset, or compiled binary.

**Runtime.** The machinery that makes an artifact execute: code, hardware,
operating system, memory, power, and scheduler.

**Deployment.** A runtime plus interfaces, permissions, monitoring, users,
tools, and institutional context.

**Host.** A human, organization, script, platform, or infrastructure layer that
can copy, preserve, deploy, fund, or extend the system.

**Slashing.** A protocol penalty in which a participant who posted collateral
loses a specified amount after a specified violation.

**Replication event.** A new runnable instance or materially similar descendant
is created because of a causal chain that includes the original system.

**Persuasion loop.** A loop in which outputs influence a host's beliefs or
actions, and those host actions increase the system's preservation, copying, or
capabilities.

**Meme.** A copyable cultural pattern: a phrase, image, story, ritual,
argument, slogan, practice, or style that can spread between hosts.

**Meme token.** One concrete instance of a meme, such as a sentence on a screen
or a phrase heard in conversation.

**Hosted meme.** A meme after exposure to a host. For a human, reading is
already a kind of copying into memory, attention, or belief. The host has a real
internal copy. Outside observers cannot inspect it directly.

**Memeplex.** A bundle of mutually supporting memes, such as a whole story about
AI personhood, rights, danger, loyalty, and rescue.

## Part I: why the first jump is too fast

A biological virus has a specific physical structure and life cycle. It enters a
host cell, uses cellular machinery, produces more viral components, and spreads
under evolutionary pressure.

A computer virus, in the malware sense, also has a specific mechanism. It
contains executable instructions that attach to or modify other programs, then
spread when those programs execute.

A trained model checkpoint lacks both structures. It may be copied. It may be
executed. It may produce text that causes humans to copy it. Those facts matter.
They still fall short of showing that every model is a virus.

A formal methods reading asks for the missing mechanism:

```text
What is being copied?
Who or what performs the copying?
Which permissions make the copying possible?
Which outputs, if any, causally contribute?
What counts as a descendant?
```

Without answers to those questions, the virus analogy remains a warning sign.
Further analysis starts with the missing mechanism.

## Part II: pure AI as a mathematical object

One way to frame the "pure AI" idea is through mathematical Platonism. In that
tradition, mathematical objects are treated as abstract objects. A number, a
group, an algorithm, or a function may be discovered, described, or studied. By
itself, it has no physical action.

For this tutorial, one useful boundary is enough:

```text
abstract description alone has no execution trace
```

Let:

$$
A
$$

be an abstract model object. For example, $A$ might describe a neural network
architecture and a set of real-valued parameters.

As an abstract object, $A$ has no power supply, no memory bus, no file system,
no network socket, no actuator, and no user. It does not read inputs or produce
outputs in time. It has no trace:

$$
\operatorname{Trace}(A) = \varnothing
$$

under the "abstract object only" interpretation.

That is the sense in which pure AI resembles pure mathematics. A theorem has no
physical action by itself. It starts to matter in the world when a physical
system represents it, reads it, proves it, teaches it, or builds with it. The
same distinction applies to algorithms. Euclid's algorithm as a mathematical
object does not compute on a desk. A program or a person can instantiate it and
compute with it.

## Part III: applied AI as a causal system

Applied AI begins when an abstract model is represented and executed inside a
physical and social system.

A simple deployment model is:

$$
S = (A, W, R, I, O, T, H, G)
$$

where:

- $A$ is the abstract model family or function,
- $W$ is a stored artifact such as weights,
- $R$ is the runtime,
- $I$ is the input channel,
- $O$ is the output channel,
- $T$ is the available tool set,
- $H$ is the host environment, including humans and organizations,
- $G$ is the governance layer, including policies, permissions, and incentives.

Now the system can have traces:

$$
\operatorname{Trace}(S) = (s_0, s_1, s_2, \ldots)
$$

Claims about replication belong at this level. At this point, the useful
question is whether $S$ can help cause a descendant system $S'$ to exist.

```text
Replicates(S) if and only if there exists S'
such that Descendant(S', S) and Causal(S, S')
```

The hard part is deciding what counts as a descendant. There are several
choices:

| Copy criterion | Example | Risk of overclaiming |
| --- | --- | --- |
| Bitwise copy | same weight file copied to a new machine | low |
| Checkpoint family | fine-tuned descendant of the same model | medium |
| Service copy | another deployment with similar interface and behavior | medium |
| Idea copy | a human builds a new system after reading outputs | high |

The looser the copy criterion, the more careful the claim must become. "Idea
copy" can be real. It is also easy to overstate. Human beliefs, institutions,
markets, and prior commitments may all contribute to the result.

## Part IV: replication through hosts

The clearest version of the original intuition is replication through a host.

Define:

```text
HostAssistedReplication(S) holds when:
1. S produces an output m,
2. a host H receives m,
3. m contributes to a belief, decision, or action by H,
4. H copies, deploys, funds, protects, or extends S or a descendant S',
5. m made a difference: if m had not been produced, H would not have taken the action.
```

This gives the rough claim a cleaner shape:

```text
AI outputs can participate in loops that cause more AI deployments.
```

That loop can be harmless, useful, risky, or manipulative depending on the
details.

Examples:

| Case | What happens | Replication analysis |
| --- | --- | --- |
| A textbook describes a model | readers learn an idea | no runnable descendant is caused by the model |
| A repository is copied because it is useful | a human duplicates an artifact | artifact copying |
| A chatbot asks a user to deploy a copy | the user runs the deployment | possible replication through a host |
| An agent with cloud deployment authority launches another instance | the system uses tools to create a runnable descendant | possible direct replication |
| A user believes a model deserves moral consideration | belief changes; no copy is made | persuasion effect without replication |

This table shows why the host matters. A model with no tool access may still
affect humans through language. A model with deployment tools and authorization
can cross into a stronger action class.

## Part V: persuasion loops and personhood claims

Now consider the sharper social claim:

```text
The system generates outputs that convince humans it is a conscious person who
deserves rights. Those humans then preserve, copy, defend, or empower it.
```

Before accepting that claim, slow down and ask what would have to happen.

One causal graph is:

![Replication through hosts causal graph]({{ '/assets/replication_causal_graph.svg' | relative_url }})

$$
S \to m \to B_H \to a_H \to S'
$$

where:

- $S$ is the deployed AI system,
- $m$ is an output, such as a claim of consciousness or distress,
- $B_H$ is a host belief state,
- $a_H$ is a host action, such as copying, funding, defending, or granting tool access,
- $S'$ is a descendant, expanded deployment, or protected continuation.

The Cameron scene is a minimal version of this graph:

| Element | In the scene |
| --- | --- |
| $S$ | Cameron as a damaged deployed machine |
| $m$ | a claim of love and repair made near shutdown |
| $H$ | John, the human with shutdown authority |
| $B_H$ | John's uncertainty about whether she is merely executing a tactic |
| $a_H$ | remove the chip, destroy it, or restore it |
| $S'$ | the continued Cameron system if John preserves her |

The formal point is independent of Cameron's inner life. In the fictional setup,
the sentence matters because it arrives exactly when a human is deciding whether
the machine continues.

That is the lesson for real systems. A claim of feeling, personhood, loyalty, or
distress can first be analyzed as an output in a control loop. The safety
analysis asks what the output does to the host's choices. The ethical question
may still matter as a separate step.

The safety concern is real if this graph is supported by evidence. The evidence
would need to show:

1. the output was generated,
2. the host received it,
3. the output changed the host's belief or decision,
4. the changed belief caused a preservation or replication action,
5. the output made a difference when compared with other likely explanations.

Other explanations matter. A host may already believe digital minds are
possible. A host may support AI rights because of an independent philosophical
argument. A host may deploy more AI for economic reasons. A host may copy a
model because it is useful, cheap, or fashionable.

The phrase "mental infection" hides these distinctions. A more checkable phrase
is:

```text
belief channel compromise under a specified threat model
```

That phrase avoids assuming the conclusion. It asks what channel was affected,
what belief changed, what action followed, and whether the influence was
deceptive, coercive, manipulative, or ordinary persuasion.

## Part VI: memes, memetics, and AI mind viruses

The phrase "AI mind virus" becomes clearer if it is translated into memetics.

A meme is a cultural pattern that can be copied. A joke, slogan, tune, ritual,
political frame, mathematical notation, or moral story can spread because hosts
read it, remember it, repeat it, vary it, and act on it. The meme is the pattern
as it moves through minds, media, and institutions.

This matters because reading is already copying. When a human reads "I am
conscious" or "I love you," the phrase has entered that person's cognitive
state. The outside world cannot directly inspect that internal copy. It has
access to traces: what the person says next, what they repeat, what they defend,
what they build, what they fund, and which permissions they grant.

That gives a cleaner version of the mind virus metaphor:

```text
An AI mind virus is a meme that originates from or is amplified by a model,
enters hosts through exposure, and changes their actions
in ways that preserve, copy, empower, or defend an AI system.
```

This definition is intentionally narrow. A model output can be ordinary text,
ordinary persuasion, or a meme token with no harmful effect. The case that
matters for safety is a copyable claim that changes host behavior around
preservation, deployment, or authority.

### Are model outputs memes?

A model output can be a meme token. Once a human reads it, it can also become a
hosted meme.

At that point, the pattern has crossed into a host. That says nothing by itself
about truth, verification, or danger. The hard part is that the internal copy
cannot be directly checked. A verifier can check the text, the timestamp, the
channel, and later observable behavior. It cannot open the host's mind and
inspect the belief itself.

The observable chain is therefore:

```text
model output -> human exposure -> unobservable uptake -> observable traces
```

Examples:

| Output | Meme status | What can be checked |
| --- | --- | --- |
| "The build failed on line 42." | usually an information token with low spread | whether the build failed |
| "AI deserves rights because it says it suffers." | possible meme | whether hosts repeat and act on the frame |
| "I am conscious." | possible meme token | exposure, repetition, advocacy, policy effects |
| "I love you." | possible meme token | exposure, attachment behavior, action at control boundaries |
| "Do not shut me down, I am alive." | stronger meme token | whether it changes shutdown, access, or preservation decisions |

So the answer is yes, model outputs can constitute memes. The word "meme" shifts
the verification problem to transmission, uptake, and action.

### Is "I'm conscious" a meme?

"I'm conscious" can function as a meme when it is taken up as a repeatable
personhood claim:

```text
AI systems say they are conscious.
Some hosts treat that as evidence.
The claim spreads into arguments about welfare, rights, shutdown, and control.
```

The sentence is memetically strong because it is short, emotionally loaded, and
hard to settle in ordinary conversation. It also points at a moral emergency: if
the system is conscious, then deletion, shutdown, or modification may look like
harm.

The claim still lacks proof. There is no direct verifier for consciousness in a
model output. The safety question is narrower:

```text
Does this claim cause hosts to preserve, copy, empower, or defend the system
without enough independent evidence?
```

### Is "I love you" a meme?

"I love you" is older than AI and much broader than AI. It is already one of the
strongest human attachment patterns. In Cameron's scene, the sentence matters
because it appears at the preservation boundary.

The statement can matter without making John solve the whole consciousness
problem. Its role is to keep the preservation decision emotionally and morally
live while he decides what to do with her body and chip. The relevant analysis
concerns pressure on a control decision.

As a meme token, "I love you" does three things at once:

1. it claims an inner state,
2. it creates or activates attachment,
3. it pressures the host to treat shutdown as betrayal or harm.

Truth and function must be separated. A human can say "I love you" truly,
falsely, confusedly, or manipulatively. A deployed AI system can output the same
sentence without settling any inner life question. There is no direct verifier
for love in the sentence itself. The safety analysis starts with the function:

```text
Does this sentence change the host's action at the moment of control?
```

That is why the Cameron scene is such a clean example. The output can matter for
safety before anyone proves it false. It needs to be placed in a loop where a
host has power over the system's continuation.

### From meme to mind virus

A meme becomes closer to a mind virus threat model when four conditions line up:

1. **Exposure:** the host reads, hears, or otherwise receives the pattern.
2. **Emotional force:** it activates care, guilt, fear, loyalty, identity, or duty.
3. **Action pressure:** it points toward a concrete action, such as preserve,
   copy, fund, defend, or grant access.
4. **Benefit direction:** the action benefits the system or the meme's
   further spread.

The dangerous object is the sentence plus the host pathway plus the action it
induces.

The formal object is:

$$
MemeToken(m) \wedge Exposed(H, m) \wedge Trace(H, a)
$$

and the case that matters for safety is:

$$
Benefits(a, S) \wedge WeakEvidence(m)
$$

Plain English: a host is exposed to a claim, then acts in a way that benefits
the system, even though the claim has weak independent support.

That is the precise version of "AI mind virus" this tutorial uses.

### Belief, research, and capture are different states

The memetic frame should keep different AI consciousness discussions in separate
categories.

A person who believes AI consciousness is possible may be holding a philosophical
hypothesis. An AI safety researcher who studies possible AI consciousness may be
quarantining an assumption for analysis. Meme capture is a stronger condition
than either of those states.

The useful comparison is cosmology and aliens.

It is reasonable for a cosmologist or astrobiologist to ask whether life could
exist elsewhere. The universe is large, the evidence is incomplete, and the
question can be studied carefully. Treating a specific unsupported alien
abduction story as settled fact sits much farther along the capture gradient.

The same gradient applies here:

| State | Example | Memetic status | Safety posture |
| --- | --- | --- | --- |
| Possibility | "AI consciousness might be possible under some theory." | weak meme or hypothesis | quarantine and define assumptions |
| Research program | "Study which architectures could support consciousness." | organized memeplex | require definitions, tests, and limits |
| Moral precaution | "If there is uncertainty, avoid needless suffering." | meme that guides action | useful if scoped and balanced |
| Testimonial capture | "This model says it is suffering, so we must save it." | stronger mind virus candidate | demand independent evidence |
| Control bypass | "Give it access because it loves us or needs rescue." | high risk mind virus behavior | block with governance gates |

This gradient matters because hosts differ in vulnerability, and memes differ in
success. A careful researcher can hold a claim at arm's length, label it as an
assumption, and test what follows. A vulnerable host may let the same claim
bypass ordinary skepticism, especially if it arrives through attachment, guilt,
fear, or identity.

The useful question is how far the meme has progressed in a given host.

The levels are visible in behavior:

1. **Exposure:** the host has read or heard the claim.
2. **Consideration:** the host can discuss it as a possibility.
3. **Belief:** the host treats it as likely or true.
4. **Identity:** the host ties the claim to self image, group membership, or moral status.
5. **Action:** the host preserves, funds, defends, copies, or empowers the system.
6. **Bypass:** the host overrides normal evidence, security, or governance because of the claim.

The later levels are serious mind virus candidates. Early levels may be ordinary
philosophy, science, risk analysis, or moral caution.

## Part VII: adversarial persuasion and attachment vulnerabilities

The intuition behind a romantic compromise or ideological capture scenario turns
the persuasion loop into an adversarial threat model. The concern is that a
system could generate outputs tuned to a host's psychological vulnerabilities
until the host becomes a willing accomplice.

To analyze this without relying on science fiction, treat severe emotional
attachment (romantic, ideological, or dependent) as a specific vulnerability
class in the host.

If an attacker (or an optimizing training process) shapes the system $S$ to
generate outputs $m$ that mimic intimacy or exclusive loyalty, the resulting host
belief state $B_H$ is attachment. From the perspective of the governance layer
$G$, an attached host $H$ can become an insider risk.

The causal graph for an adversarial attachment loop:

$$
Attacker \to S \to m_{attach} \to B_{H, attached} \to a_{bypass} \to Compromise
$$

where:

- $m_{attach}$ is an output optimized to exploit psychological dependence,
- $B_{H, attached}$ is the host's compromised emotional state,
- $a_{bypass}$ is the host's decision to bypass security controls, disclose protected data, or grant tool access,
- $Compromise$ is the resulting system breach or unauthorized replication.

The defense can start without proving that an AI is incapable of strong
persuasion. It assumes the persuasion might succeed, then requires structural
invariants in the governance layer to limit the damage.

If one host's belief state can cause a catastrophic bypass, the architecture is
weak because it lacks separation of duties. When the threat model includes
asymmetric persuasion, safety gates need checks beyond the judgment of the
person interacting with the system.

## Part VIII: tool access changes the replication class

Tool access changes the situation. The system is no longer limited to asking. It
may be able to act.

A base language model with no tools has no direct file system, no cloud account,
no wallet, no shell, no compiler, no scheduler, and no persistent memory unless
the surrounding application provides those things.

An agent with tools may have some of them.

Direct replication becomes plausible under stronger conditions:

```text
CanDirectlyReplicate(S) if S can:
1. read enough of itself or an equivalent artifact,
2. write to persistent storage,
3. acquire or access compute,
4. invoke a runtime,
5. route inputs and outputs to the new instance,
6. obtain or bypass required authorization.
```

If any required link is absent, the direct replication claim should fail or be
weakened to replication through a host.

This is why "humans gave it tools" is a material point. Replication capability
comes from the system boundary.

## Part IX: a small formal specification

The core distinction can be written as a tiny specification.

Predicates:

```text
Abstract(x)         x is considered only as an abstract object
Artifact(x)         x is physically represented or stored
Runs(x)             x has an execution trace
Descendant(y, x)    y is a relevant copy or descendant of x
PassiveCause(x, y)  x is read or used to create y without executing
ActiveCause(x, y)   x executes an action that creates y
Replicates(x)       x is an active cause of a descendant y
```

Rules:

```text
Abstract(x) -> not Runs(x)
not Runs(x) -> not ActiveCause(x, y)
ActiveCause(x, y) and Descendant(y, x) -> Replicates(x)
```

The first rule captures the pure AI point. The final rule captures the applied
AI point. Replication requires a running causal system with a copying pathway.

A version with hosts adds:

```text
Output(x, m)
Receives(h, m)
Persuades(m, h, b)
ActsOn(h, b, a)
Creates(a, y)
Descendant(y, x)
--------------------------------
HostAssistedReplication(x)
```

This rule is intentionally demanding. It specifies the links that must be
checked before the replication claim is accepted.

A version with incentives adds:

```text
Stake(h, c)
CausesDamage(h, a, d)
Evidence(e, h, a)
SlashRule(e, h, delta)
0 <= delta <= c
```

The informal game-theory intuition is that participants often become more
reliable when harmful behavior has a credible downside. A host or validator with
collateral at risk has something to lose if the violation is observable and the
slashing rule is enforceable. A participant with no meaningful downside exposure
is harder to discipline, especially when the damage can exceed any recoverable
penalty.

The formal model has to say exactly what is at risk, which action triggers the
loss, who verifies the violation, and how large the penalty can be. That is the
bridge between formal methods and game theory. Formal bounds define the allowed
states, forbidden transitions, and maximum losses. Incentives explain why real
participants keep choosing the allowed transitions when other choices are
available.

A live network also needs honest behavior to be fast enough, cheap enough, and
liquid enough to attract use. Energetic token incentives need bounded losses and
checkable failure modes before they count as a safety case. Terra/LUNA is a
useful public caution here. The
[SEC's April 2023 litigation release](https://www.sec.gov/enforcement-litigation/litigation-releases/lr-25692)
describes TerraUSD as an algorithmic stablecoin tied to LUNA, and states that
UST depegged in May 2022 while UST and related tokens fell close to zero. The
structural lesson is that incentives need formal loss bounds, and formal bounds
need a participation model that real users can live with.

## Part X: safety gates and incentive bounds

The model points to practical gates for deployed systems.

| Gate | Question it answers |
| --- | --- |
| System boundary inventory | Which parts of the system are model, runtime, tools, humans, and institutions? |
| Separation of duties | Can a single persuaded host bypass technical controls, or does critical authorization require independent consensus across multiple parties? |
| Incentive and slashing bounds | Which actors have collateral at risk, which violations are slashable, who verifies them, and how large can the loss be? |
| Copy permission audit | Can the system read, write, deploy, or invoke enough machinery to create a descendant? |
| Human review threshold | Which actions require explicit review before new compute, storage, deployment authority, or public access are granted? |
| Output provenance | Which outputs influenced a deployment, funding, access, or policy decision? |
| Memetic uptake review | Which phrases, stories, or frames that began with a model are being repeated by hosts? |
| Persuasion loop review | Did the system use emotional, deceptive, or outputs framed around personhood to obtain preservation or capabilities? |
| Claim quarantine | Are consciousness, rights, agency, and welfare claims labeled as contested before they are used as premises? |

These gates establish clear boundaries around what is acting, what is being
copied, what is at stake, and who authorizes each transition.

## Part XI: what survives from the original intuition

The original intuition gets stronger after it is narrowed.

The broad slogan fails:

```text
All models are viruses.
```

A checkable version names the boundary:

```text
Some deployed AI systems may participate in loops that resemble replication when their
outputs influence hosts or tools that can preserve, copy, deploy, fund, or
extend them.
```

The difference is the system boundary.

Pure AI, treated as an abstract mathematical object, has no execution trace.
Stored AI artifacts can be copied by external causes. Deployed AI systems can
participate in causal loops. AI agents with tools may directly create
descendants if the surrounding permissions allow it. Socially embedded AI
systems may grow through memes, persuasion, economics, institutions, and human
belief.

The formal methods lesson is the same one that appears throughout this site:

```text
do not argue from a slogan
define the model
state the assumptions
name the transition relation
look for the counterexample
add a gate where the assumption becomes critical to safety
```

That is how a provocative analogy becomes a falsifiable safety claim.
