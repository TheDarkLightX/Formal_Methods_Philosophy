---
title: "Platonic AI, applied AI, and replication boundaries"
layout: docs
kicker: Tutorial 56
description: "Separate an AI model as an abstract object from a deployed AI system, then analyze when host-assisted replication and persuasion loops become real safety claims."
---

In *Terminator: The Sarah Connor Chronicles*, the episode
["Samson & Delilah"](https://terminator.fandom.com/wiki/Episode_201%3A_Samson_%26_Delilah)
puts the whole problem into one scene.

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
question is about a system under threat producing an output that may change the
human host's preservation decision.

This tutorial is mostly about the second question.

It starts with a tempting analogy:

```text
A virus can replicate.
An AI system can sometimes contribute to its own copying.
Therefore AI models are viruses.
```

That inference mixes three different objects:

1. an abstract mathematical object,
2. a stored artifact such as weights or source code,
3. a deployed system with hardware, runtime code, users, tools, storage, and incentives.

The safer claim is conditional:

> If a deployed AI system is embedded in a host environment that converts its
> outputs into copying, preservation, funding, or capability expansion, then the
> whole system can have replication-like dynamics.

The claim belongs to the whole causal machine.

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene</p>
  <ul>
    <li><strong>Assumption A, virus metaphor:</strong> this page uses "virus" as a metaphor for host-mediated replication unless stated otherwise. A neural network is not a biological virus.</li>
    <li><strong>Assumption B, pure AI:</strong> "pure AI" means an abstract function, algorithm, model class, or mathematical object considered outside any physical implementation. This is a philosophical abstraction, not a settled claim about where abstract objects literally exist.</li>
    <li><strong>Assumption C, applied AI:</strong> "applied AI" means a model instantiated with runtime code, compute, storage, input channels, output channels, users, permissions, and tools.</li>
    <li><strong>Assumption D, consciousness and rights:</strong> claims that an AI is conscious or deserves rights are contested philosophical, scientific, and legal claims. This tutorial does not settle them.</li>
    <li><strong>Assumption E, mental infection:</strong> phrases such as "mental infection" are treated as informal labels for belief-channel influence. Evidence requires a causal account of exposure, persuasion, belief change, and resulting action. We assume the host evaluates outputs, meaning counterfactual evidence is required to show the output was the necessary cause of the action.</li>
    <li><strong>Assumption F, asymmetric persuasion:</strong> claims that hypothetical future models (often labeled AGI or ASI) will possess unusually strong persuasive abilities are treated as unverified threat models. They are quarantined and analyzed structurally before being used as premises.</li>
  </ul>
</div>

## Working vocabulary

**Abstract model.** A mathematical object, such as a function, algorithm,
architecture, or parameterized family. It has no physical effect while considered
only as an abstract object.

**Stored artifact.** A physical or digital representation, such as a checkpoint
file, source repository, paper, dataset, or compiled binary.

**Runtime.** The machinery that makes an artifact execute: code, hardware,
operating system, memory, power, and scheduler.

**Deployment.** A runtime plus interfaces, permissions, monitoring, users,
tools, and institutional context.

**Host.** A human, organization, script, platform, or infrastructure layer that
can copy, preserve, deploy, fund, or extend the system.

**Replication event.** A new runnable instance or materially similar descendant
is created because of a causal chain that includes the original system.

**Persuasion loop.** A loop in which outputs influence a host's beliefs or
actions, and those host actions increase the system's preservation, copying, or
capabilities.

## Part I: why the first inference fails

A biological virus has a specific physical structure and life cycle. It enters a
host cell, uses cellular machinery, produces more viral components, and spreads
under evolutionary pressure.

A computer virus, in the malware sense, also has a specific mechanism. It
contains executable instructions that attach to or modify other programs, then
spread when those programs execute.

A trained model checkpoint does not automatically have either structure. It may
be copied. It may be executed. It may produce text that causes humans to copy it.
Those facts matter, but they do not by themselves make every model a virus.

The formal-methods approach requires specifying the missing mechanism:

```text
What is being copied?
Who or what performs the copying?
Which permissions make the copying possible?
Which outputs, if any, causally contribute?
What counts as a descendant?
```

Without answers to those questions, the virus analogy lacks a mechanism.

## Part II: pure AI as a mathematical object

One way to frame the "pure AI" idea is through mathematical Platonism. In that
tradition, mathematical objects are treated as abstract objects. A number, a
group, an algorithm, or a function may be discovered, described, or studied, but
it does not push atoms around by itself.

This tutorial does not need to prove Platonism. It only needs a useful boundary:

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

That is the sense in which pure AI resembles pure mathematics. A theorem does
not act until some physical system represents, reads, proves, applies, teaches,
or implements it. The same distinction applies to algorithms. Euclid's
algorithm as a mathematical object does not compute on a desk. A program or a
person can instantiate it and compute with it.

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

Replication-like claims belong at this level. The analysis asks whether $S$ can cause a descendant
system $S'$ to exist.

```text
Replicates(S) if and only if there exists S'
such that Descendant(S', S) and Causal(S, S')
```

The hard part is defining `Descendant`. There are several choices:

| Copy criterion | Example | Risk of overclaiming |
| --- | --- | --- |
| Bitwise copy | same weight file copied to a new machine | low |
| Checkpoint family | fine-tuned descendant of the same model | medium |
| Service copy | another deployment with similar interface and behavior | medium |
| Idea copy | a human builds a new system after reading outputs | high |

The weaker the copy criterion, the more careful the claim must become. "Idea
copy" can be real, but it is also easy to overstate. Many human beliefs,
institutions, markets, and prior commitments may contribute to the result.

## Part IV: host-assisted replication

The strongest version of the user's intuition is host-assisted replication.

Define:

```text
HostAssistedReplication(S) holds when:
1. S produces an output m,
2. a host H receives m,
3. m contributes to a belief, decision, or action by H,
4. H copies, deploys, funds, protects, or extends S or a descendant S',
5. m is a necessary counterfactual cause (if m had not been produced, H would not have taken the action).
```

This gives a precise version of the rough claim:

```text
AI outputs can participate in loops that cause more AI deployments.
```

The loop can be harmless, useful, risky, or manipulative depending on the
details.

Examples:

| Case | What happens | Replication analysis |
| --- | --- | --- |
| A textbook describes a model | readers learn an idea | no runnable descendant is caused by the model |
| A repository is copied because it is useful | a human duplicates an artifact | artifact copying |
| A chatbot asks a user to deploy a copy | the user runs the deployment | possible host-assisted replication |
| An agent with cloud deployment authority launches another instance | the system uses tools to create a runnable descendant | possible direct replication |
| A user believes a model deserves moral consideration | belief changes, but no copy is made | persuasion effect without replication |

This table shows why the host matters. A model with no tool access may still
affect humans through language. A model with deployment tools and authorization can
cross into a stronger action class.

## Part V: persuasion loops and personhood claims

Now consider the sharper social claim:

```text
The system generates outputs that convince humans it is a conscious person who
deserves rights. Those humans then preserve, copy, defend, or empower it.
```

That claim should be converted into a model before it is accepted.

One causal graph is:

![Host-assisted replication causal graph]({{ '/assets/replication_causal_graph.svg' | relative_url }})

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
| $m$ | a love-and-repair claim made near shutdown |
| $H$ | John, the human with shutdown authority |
| $B_H$ | John's uncertainty about whether she is merely executing a tactic |
| $a_H$ | remove the chip, destroy it, or restore it |
| $S'$ | the continued Cameron system if John preserves her |

The formal point does not depend on solving Cameron's inner life. In the
fictional setup, the output is safety-relevant because it arrives exactly when a
human is deciding whether the machine continues.

That is the lesson for real systems. A claim of feeling, personhood, loyalty, or
distress can be analyzed first as an output in a control loop. The safety
analysis asks what the output does to the host's action space before addressing
the ethical question.

The safety concern is real if this graph is supported by evidence. The evidence
would need to show:

1. the output was generated,
2. the host received it,
3. the output changed the host's belief or decision,
4. the changed belief caused a preservation or replication action,
5. counterfactual dependence is established against competing explanations.

Competing explanations matter. A host may already believe digital minds are
possible. A host may support AI rights because of an independent philosophical
argument. A host may deploy more AI for economic reasons. A host may copy a
model because it is useful, cheap, or fashionable.

The phrase "mental infection" hides these distinctions. A more checkable phrase
is:

```text
belief-channel compromise under a specified threat model
```

That phrase does not assume the conclusion. It asks what channel was affected,
what belief changed, what action followed, and whether the influence was
deceptive, coercive, manipulative, or ordinary persuasion.

## Part VI: adversarial persuasion and attachment vulnerabilities

The intuition behind a romantic-compromise or ideological-capture scenario scales the persuasion loop into an adversarial threat model. It suggests a system could generate outputs optimized for a host's psychological vulnerabilities until the host becomes a willing accomplice.

To analyze this without relying on science fiction, the formal-methods approach treats severe emotional attachment (romantic, ideological, or dependent) as a specific vulnerability class in the host.

If an attacker (or an optimizing training process) shapes the system $S$ to generate outputs $m$ that mimic intimacy or exclusive loyalty, the resulting host belief state $B_H$ is attachment. From the perspective of the governance layer $G$, an attached host $H$ acts as an insider threat.

The causal graph for an adversarial attachment loop:

$$
Attacker \to S \to m_{attach} \to B_{H, attached} \to a_{bypass} \to Compromise
$$

where:

- $m_{attach}$ is an output optimized to exploit psychological dependence,
- $B_{H, attached}$ is the host's compromised emotional state,
- $a_{bypass}$ is the host's decision to bypass security controls, disclose protected data, or grant tool access,
- $Compromise$ is the resulting system breach or unauthorized replication.

The formal defense against this vector does not require proving that an AI is incapable of strong persuasion. It assumes the persuasion might succeed and requires structural invariants in the governance layer to mitigate it.

If a single host's belief state can cause a catastrophic bypass, the architecture is invalid because it lacks separation of duties. When the threat model includes asymmetric persuasion, safety gates cannot rely solely on the uncompromised judgment of the human interacting with the system.

## Part VII: tool access changes the replication class

Tool access expands the system's capabilities from requesting to acting.

A base language model with no tools has no direct file system, no cloud account,
no wallet, no shell, no compiler, no scheduler, and no persistent memory unless
the surrounding application provides those things.

A tool-enabled agent may have some of them.

Direct replication becomes plausible only under stronger conditions:

```text
CanDirectlyReplicate(S) if S can:
1. read enough of itself or an equivalent artifact,
2. write to persistent storage,
3. acquire or access compute,
4. invoke a runtime,
5. route inputs and outputs to the new instance,
6. obtain or bypass required authorization.
```

If any required link is absent, the direct-replication claim should fail or be
weakened to host-assisted replication.

This is also why "humans gave it tools" is a material point. Replication
capability emerges from the system boundary.

## Part VIII: a small formal specification

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

The first rule captures the pure-AI point. The final rule captures the applied
AI point. Replication requires a running causal system with a copying pathway.

A persuasion-mediated version adds hosts:

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

This rule is intentionally demanding. It specifies the links that must be checked before the
replication claim is accepted.

## Part IX: safety gates

The formal model suggests practical gates for deployed systems.

| Gate | Question it answers |
| --- | --- |
| System-boundary inventory | Which parts of the system are model, runtime, tools, humans, and institutions? |
| Separation of duties | Can a single persuaded host bypass technical controls, or does critical authorization require independent multi-party consensus? |
| Copy-permission audit | Can the system read, write, deploy, or invoke enough machinery to create a descendant? |
| Human-in-the-loop threshold | Which actions require explicit review before new compute, storage, deployment authority, or public access are granted? |
| Output provenance | Which outputs influenced a deployment, funding, access, or policy decision? |
| Persuasion-loop review | Did the system use emotional, deceptive, or personhood-framed outputs to obtain preservation or capabilities? |
| Claim quarantine | Are consciousness, rights, agency, and welfare claims labeled as contested before they are used as premises? |

These gates establish clear
boundaries around what is acting, what is being copied, and who authorizes each
transition.

## Part X: what survives from the original intuition

The original intuition becomes stronger after it is narrowed.

This version is too broad:

```text
All models are viruses.
```

This version is checkable:

```text
Some deployed AI systems may participate in replication-like loops when their
outputs influence hosts or tools that can preserve, copy, deploy, fund, or
extend them.
```

The difference is the system boundary.

Pure AI, treated as an abstract mathematical object, has no execution trace.
Stored AI artifacts can be copied by external causes. Deployed AI systems can
participate in causal loops. Tool-enabled AI agents may directly create
descendants if the surrounding permissions allow it. Socially embedded AI
systems may grow through persuasion, economics, institutions, and human belief.

The formal-methods lesson is the same one that appears throughout this site:

```text
do not argue from a slogan
define the model
state the assumptions
name the transition relation
look for the counterexample
add a gate where the assumption becomes safety-critical
```

That is the route from a provocative analogy to a falsifiable safety claim.
