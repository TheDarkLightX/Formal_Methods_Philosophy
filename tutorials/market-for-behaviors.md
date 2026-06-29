---
title: "A Market for Behaviors: What Learning Is, From Behaviorism to AI"
layout: docs
kicker: Essay
description: "Learning, whether in animals, humans, or AI, is the process of adjusting behavior probabilities based on reward signals. Those reward signals are set by a market for behaviors. This essay formalizes the connection."
---

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Interactive lab</p>
  <p>This essay has an accompanying interactive visualization page with animated graphs for the incentive map, supply-demand curves, compression loss, and the feedback loop. <a href="{{ '/market_for_behaviors_lab.html' | relative_url }}">Open the Market for Behaviors lab &rarr;</a></p>
</div>

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Assumption hygiene</p>
  <ul>
    <li><strong>Assumption A, rationality:</strong> Agents shift toward higher-reward behaviors. This holds approximately, not perfectly. The temperature parameter $\tau$ captures this imprecision.</li>
    <li><strong>Assumption B, observable preferences:</strong> The Platinum Rule requires that $v_j$ is learnable from data. In practice, preferences are noisy, context-dependent, and partially inexpressible.</li>
    <li><strong>Assumption C, static preferences:</strong> The framework treats $v_j$ as fixed. In reality, preferences shift as agents encounter new behaviors, creating a co-evolutionary dynamic.</li>
    <li><strong>Assumption D, surplus maximization as ethics:</strong> Equating "ethical" with "maximizing social surplus" is a utilitarian assumption. Alternative ethical frameworks would produce different objective functions.</li>
    <li><strong>Assumption E, Boltzmann linking:</strong> The claim that the same mathematical structure appears in behaviorism, economics, and RL depends on specific assumptions (maximum entropy, reward-additivity, stationarity).</li>
  </ul>
</div>

## Introduction

Markets did not wait for humans to invent them. They show up in the mating
displays of birds, in the helping behavior of paper wasps, in the competitive
altruism of children on a playground. Wherever there is supply, demand, and
selection, there is a market. And wherever there is a market, behaviors are what
is being traded.

This essay pulls together a framework I have been developing across several
pieces. The core claim:

> **Learning, whether in animals, humans, or AI, is the process of adjusting
> behavior probabilities based on reward signals. Those reward signals are set by
> a market for behaviors. Understanding this market is the key to understanding
> what training data is, what alignment is, and why behavioral normalization
> happens.**

The framework has five layers:

1. **Behavioral spectrum** is ontology. It is the space of what can exist.
2. **Incentive map** is dynamics. It is what makes each behavior more or less likely.
3. **Market for behaviors** is economics. It is the system that rewards, prices, selects, suppresses, records, and amplifies behaviors.
4. **Training** is compression. It squeezes historical behavior traces into a generative model.
5. **Alignment** is market design. It is the deliberate shaping of the incentive map so the market produces beneficial outcomes.

---

## 1. The Behavioral Spectrum (Ontology)

Every agent, whether a person, an animal, or an AI, can produce a range of
behaviors. Let us call this range the **behavioral spectrum**.

Formally, let $\mathcal{B}$ denote the set of all possible behaviors. For a
specific agent $a$, let $\mathcal{B}_a \subseteq \mathcal{B}$ denote the subset
of behaviors that agent can actually reach, given its capabilities, resources,
and context.

In the discrete case, $\mathcal{B} = \{b_1, b_2, \ldots, b_n\}$. In the
continuous case, $\mathcal{B} \subseteq \mathbb{R}^d$, where each dimension
represents a behavioral attribute like tone, content, timing, or intensity.

The spectrum is the **ontology** because it defines what can exist before any
selection happens. It is the space of possibilities, not the space of what
actually occurs. What actually occurs is determined by the incentive map.

Think about a soldier in the military. A person is capable of a wide spectrum
of behaviors: speaking freely, dressing however they want, waking up at any
hour. But the military environment narrows that spectrum to a thin slice. The
soldier wakes when it is acceptable, wears what is acceptable, speaks what is
acceptable, marches when it is acceptable. The full behavioral spectrum still
exists as a possibility, but the realized spectrum is drastically narrower.

---

## 2. The Incentive Map (Dynamics)

If the behavioral spectrum is the space, the incentive map is the force that
shapes what happens inside it.

An **incentive map** $I: \mathcal{B} \to \mathbb{R}$ assigns a scalar reward (or
cost, when negative) to each behavior. Behaviors with high $I(b)$ get rewarded.
Behaviors with low or negative $I(b)$ get punished or simply ignored.

The probability that agent $a$ produces behavior $b$ follows the Boltzmann
distribution:

$$
P_a(b) = \frac{e^{I(b)/\tau}}{\sum_{b' \in \mathcal{B}_a} e^{I(b')/\tau}}
$$

where $\tau > 0$ is a temperature parameter. When $\tau$ is low, the agent
strongly prefers the highest-reward behavior and mostly ignores everything
else. When $\tau$ is high, the agent explores more broadly, producing a wider
range of behaviors regardless of how much reward they bring.

### Why This Specific Distribution

The Boltzmann distribution is the **maximum-entropy distribution** subject to a
constraint on expected reward. In plain terms: if the only known fact is that
behaviors are rewarded according to $I$, then the least-biased guess about the
resulting behavior distribution is the Boltzmann distribution. It assumes
nothing beyond what the incentive map already specifies.

This one equation links three different domains:

- **Behaviorism:** $I(b)$ is the reinforcement schedule. More reinforcement
  means higher response probability. The temperature $\tau$ captures how
  sensitive the agent is to those differences.
- **Economics:** $I(b)$ is the price or reward. Agents drift toward
  higher-reward behaviors. $\tau$ captures bounded rationality, the noise in
  the optimization.
- **Reinforcement learning:** This is the softmax policy with entropy
  regularization. $\tau$ is the entropy bonus coefficient.

### What Learning Is

Learning, in the behaviorist sense, is the convergence of behavior probabilities
toward the equilibrium defined by the incentive map. As an agent accumulates
reinforcement history over time:

$$
P_a(b, t) \to P_a^*(b) = \frac{e^{I(b)/\tau}}{Z}
$$

where $Z$ is the partition function (the normalizing constant in the
denominator). Learning is the process by which the agent's behavior distribution
comes to mirror the incentive structure of its environment.

This is not a metaphor. It is the same mathematical process whether the agent is
a pigeon learning to peck a disk for food, a human learning which social
behaviors earn approval, or a language model being fine-tuned on human feedback.

---

## 3. The Market for Behaviors (Economics)

So far we have been talking about a single agent responding to incentives. But
incentives do not come out of nowhere. They are set by other agents. That is
where the market enters the picture.

Consider $N$ agents. Each agent $i$ has:

- **Supply side:** A cost function $c_i: \mathcal{B} \to \mathbb{R}_{\geq 0}$,
  the cost to agent $i$ of producing behavior $b$.
- **Demand side:** A valuation function $v_j: \mathcal{B} \to \mathbb{R}_{\geq 0}$,
  how much agent $j$ values receiving behavior $b$.

The **reward** for agent $i$ producing behavior $b$ for agent $j$ is:

$$
r_{ij}(b) = v_j(b) - c_i(b)
$$

This is the **surplus**: value to the receiver minus cost to the producer. The
aggregate incentive map for agent $i$ sums over all the other agents:

$$
I_i(b) = \sum_{j \neq i} v_j(b) - c_i(b)
$$

### Market Equilibrium

In equilibrium, behaviors that are in high demand (high $v_j$) and cheap to
supply (low $c_i$) receive high rewards, which makes them more probable.
Behaviors with low demand or high cost receive low or negative rewards, which
suppresses them. The equilibrium distribution for agent $i$ is:

$$
P_i^*(b) = \frac{e^{I_i(b)/\tau_i}}{Z_i}
$$

This is supply and demand for behaviors. Agents produce behaviors that other
people want. The "price" is the social reward that flows back: attention,
status, reciprocity, tokens, or money.

### The Six Market Functions

| Function | Description | Formal expression |
|---|---|---|
| **Rewards** | Assigns benefit to behaviors | $r_{ij}(b) = v_j(b) - c_i(b)$ |
| **Prices** | Aggregates rewards into a signal | $I_i(b) = \sum_j v_j(b) - c_i(b)$ |
| **Selects** | Concentrates probability on high-reward behaviors | $P_i^*(b)$ peaks at high $I$ |
| **Suppresses** | Drives low-reward behaviors toward zero probability | $P_i^*(b) \to 0$ for low $I$ |
| **Records** | Stores traces of selected behaviors | Dataset $D = \{(b_k, r_k)\}$ |
| **Amplifies** | Makes selected behaviors more visible than baseline | High-$I$ behaviors appear disproportionately |

The recording function is what creates the bridge to training data. The
amplification function is what creates the risk of feedback loops.

### Biological Markets

This is not an abstraction imposed on nature. Biological market theory
(Noël & Hammerstein, 1994) shows that markets are everywhere in biological
ecosystems. In mating markets, the supply of desirable genetic material is
limited, and the demand for it shapes courtship behaviors. In cooperatively
breeding paper wasps, market forces influence helping behavior (Grinsted &
Field, 2017). Competitive altruism shows up in children when generous behavior
gets observed and rewarded with social status (Hardy & Van Vugt, 2006).

The rewards are not always tokens or money. Attention, love, social rank, and
reproductive access all function as market currencies. Shunning, the removal of
attention and love, is the inverse: a negative punishment that suppresses
behaviors. Fashion, whether in clothes or in conduct, is the visible output of
these market forces.

### Technological Markets

The same structure shows up in crypto-economic systems. Blockchain oracles are
incentive design patterns that use reward mechanisms to produce behaviors that
can provably verify real-world events. If a photographer can provably show they
took a photograph at a specific location and time, they can receive tokens via
smart contract. The technical means of rewarding any desired behavior already
exists.

But token rewards alone are not enough. Prestige, leaderboards, and gamification
provide social rank, which functions as a reward whether or not there is a block
reward attached. Social hierarchy is the result of unequal distribution of
social rewards. In a meritocracy, those rewards flow to agents whose behaviors
add value to the community.

---

## 4. Training as Compression

Now we come to the bridge between the market and AI.

### Training Data Is Not Raw

Training data is the recorded output of a market for behaviors. It is made of
traces of behaviors that survived the market's selection pressures. Text on the
web was selected by publishing markets, platform algorithms, social reward
structures (likes, upvotes, links), and editorial gatekeeping. Images in
datasets were selected by availability, licensing, and platform incentives.

All training data is **selected**, not sampled. Selection implies selection
pressure, and selection pressure is what the market framework captures.

### The Compression Objective

Formally, training finds parameters $\theta$ for a model $q_\theta(b)$ that
minimize the KL divergence between the market distribution and the model
distribution:

$$
\theta^* = \arg\min_\theta D_{KL}(P^* \| q_\theta) = \arg\min_\theta \sum_b P^*(b) \log \frac{P^*(b)}{q_\theta(b)}
$$

Equivalently, maximizing the log-likelihood of the data:

$$
\theta^* = \arg\max_\theta \sum_{(b_k) \in D} \log q_\theta(b_k)
$$

The model compresses the market-selected distribution into a finite-capacity
representation. It can reproduce the patterns the market selected, and it can
also extrapolate beyond them, generating behaviors that were not present in the
training data.

### What Compression Loses

The model has finite capacity, a finite number of parameters, a finite rate $R$
in information-theoretic terms. The rate-distortion function $R(D)$ gives the
minimum capacity needed to achieve distortion $D$ when compressing $P^*$.

At low capacity, the model loses the **long tail** of the distribution first:
the rare, low-frequency behaviors. This is a mathematical fact of compression,
not a design choice.

$$
\text{Compression of a market-selected distribution} \Rightarrow \text{systematic underrepresentation of minority preferences}
$$

Markets narrow the behavioral spectrum. Compression of the already-narrowed
distribution narrows it further. The rare behaviors that managed to survive the
market are the first to disappear in training.

---

## 5. Alignment as Market Design

If training is compression of a market's output, then alignment is the design
of the market itself.

### The Alignment Problem Restated

Alignment is the design of the incentive map $I$ so that the resulting market
equilibrium produces behaviors that benefit all participants. Formally, find
$I^*$ that maximizes total social surplus:

$$
I^* = \arg\max_I \sum_{i=1}^N \sum_{j \neq i} \left[ v_j\big(b_{ij}^*(I)\big) - c_i\big(b_{ij}^*(I)\big) \right]
$$

where $b_{ij}^*(I)$ is the equilibrium behavior agent $i$ produces for agent $j$
under incentive map $I$.

This is **mechanism design**. The verifier, the reward model, the RLHF
procedure, these are all market design mechanisms. Choosing what to reward is
choosing the market structure, which in turn determines the equilibrium behavior
distribution.

The hard part is that $v_j$, what people actually value, is not directly
observable. It has to be inferred. That is where the Platinum Rule enters.

---

## 6. The Platinum Rule as Preference Learning

### The Golden Rule

The Golden Rule says: "Treat others as you want to be treated."

Formally, agent $i$ assumes $v_j = v_i$. Agent $i$ produces behaviors that
maximize $v_i(b)$, projecting its own preferences onto everyone else:

$$
b_{i \to j}^{\text{Golden}} = \arg\max_{b \in \mathcal{B}_i} v_i(b) - c_i(b)
$$

This breaks down when $v_j \neq v_i$. What agent $i$ values is not necessarily
what agent $j$ values.

### The Platinum Rule

The Platinum Rule says: "Treat others as they want to be treated."

Formally, agent $i$ must **learn** $v_j$ first, then produce behaviors that
maximize $v_j$:

$$
b_{i \to j}^{\text{Platinum}} = \arg\max_{b \in \mathcal{B}_i} v_j(b) - c_i(b)
$$

This requires data collection. To learn $v_j$, agent $i$ needs to observe $j$'s
preferences through some channel:

| Channel | Mechanism | AI analog |
|---|---|---|
| Direct asking | $j$ reports $v_j(b)$ | User feedback, surveys |
| Revealed preferences | Observe $j$'s choices under different $b$ | Click data, engagement metrics |
| Corrections | $j$ rejects or revises $b$ | RLHF rejection, red-team feedback |
| Imitation | Observe what $j$ produces for others | Demonstrations, expert trajectories |

### Reciprocity and Supply-Demand

In a repeated interaction, if agent $i$ consistently supplies high-$v_j$
behaviors to agent $j$, then $j$ receives surplus and has an incentive to
reciprocate. The cooperative equilibrium is:

$$
\forall i, j: \quad b_{i \to j}^* = \arg\max_b v_j(b) - c_i(b)
$$

Every agent supplies behaviors that maximize the receiver's value. This is the
market-clearing condition where all agents are both producers and consumers of
behaviors.

This is supply and demand for behaviors. Agents produce behaviors that are in
demand (high $v_j$), and they demand behaviors from others. The "price" is the
social reward that flows back: attention, status, reciprocity, or tokens.

An ethical agent, in this framework, is one that tries to give more of the
behaviors that others in society actually want. The agent gives the customer,
the client, or society the behaviors from its behavioral spectrum that they
value. Through that, society becomes more likely to return behaviors that the
agent values. This is the market logic of reciprocity, and it is also the
Platinum Rule: treat others how they want to be treated, which means collecting
data from others to find out how they want to be treated.

---

## 7. The Feedback Loop

The chain is not linear. It loops back on itself.

1. The **behavioral spectrum** contains all possible behaviors.
2. The **incentive map** shapes probabilities.
3. The **market for behaviors** selects, records, and amplifies.
4. **Training data** is the recorded output.
5. **AI training** compresses it into a generative model.
6. **Synthetic data** generates new behaviors, filtered by a verifier.
7. Those synthetic behaviors **re-enter the behavioral spectrum**, altering the
   incentive map and reshaping the market.

The cycle:

$$
P_{t+1} = \text{Compress}(\text{Filter}(P_t))
$$

where $P_t$ is the behavior distribution at generation $t$. Filter selects.
Compress loses the long tail. Each pass through the loop narrows the
distribution a bit more.

### Behavioral Normalization as a Dynamical System

This is behavioral normalization as a dynamical system. If the verifier encodes
a fixed standard of "normal," and synthetic data keeps re-entering training, the
system converges toward an ever-narrower distribution. The fixed point may
exclude minority preferences, rare behaviors, and creative deviations.

A question arises here with full force: who does the behavior really belong to?
When behaviors are generated by a model, filtered by a verifier, and re-ingested
as training data, they have no human origin. They are market-selected but not
human-produced. This is a qualitatively different regime from biological markets
or social media markets, where at least the behaviors originate from humans.

---

## 8. What Learning Is

Learning is the same process described at three levels:

| Perspective | What learning does | Formal expression |
|---|---|---|
| **Behaviorist** | Adjusts behavior probabilities based on reinforcement history | $P_a(b, t) \to P_a^*(b)$ |
| **Market** | Discovers which behaviors are in demand and adjusts supply | Agent learns $\hat{v}_j \to v_j$, shifts production |
| **Machine Learning** | Compresses historical behavior traces into a generative model | $\theta^* = \arg\min_\theta D_{KL}(P^* \| q_\theta)$ |

All three describe the same process: adjusting behavior probabilities based on
reward signals. The behaviorist sees it at the individual level. The market
theorist sees it at the multi-agent level. The ML researcher sees it at the
computational level. The incentive map is the thread that runs through all
three.

---

## 9. Implications

### For AI Safety

If alignment is market design, then the current approach to AI safety, training
models on human feedback, is a form of market design whether or not its
practitioners think of it that way. The reward model encodes a valuation
function $\hat{v}$. The RLHF procedure optimizes the model to maximize
$\hat{v}$. The question is not whether we are designing a market. We are. The
question is whether we are designing it well.

A well-designed market for behaviors would:

- **Represent diverse preferences:** The valuation function $\hat{v}$ should
  reflect the preferences of all affected parties, not just the most visible or
  vocal ones.
- **Preserve the long tail:** Compression systematically underrepresents
  minority preferences. Mechanisms that counteract this, like oversampling,
  capacity allocation, or explicit minority representation, are market design
  choices.
- **Avoid fixed-point convergence:** The feedback loop
  $P_{t+1} = \text{Compress}(\text{Filter}(P_t))$ can converge to a narrow fixed point.
  Injecting diversity back in is a market design choice.
- **Make the verifier accountable:** The verifier is the market designer. If
  the verifier encodes a biased standard of "normal," the market will normalize
  toward that bias.

### For Society

The framework suggests that behavioral normalization is not an accident of
social media or an unintended side effect of algorithmic curation. It is the
predictable output of any system that selects, records, and amplifies behaviors
according to a reward function. The more efficient the market, meaning the
faster it selects and amplifies, the faster normalization happens.

Transparency enables enforcement of accountability, but it also enables
surveillance and control. A private market can use transparency to promote
accountability for any behavior, to reward any behavior in demand, and to punish
any behavior that deviates from the norm. The question is not whether this will
happen. The technical means already exist. The question is who controls the
incentive map, and whose preferences the market is designed to serve.

### For Ethics

The Platinum Rule offers a principled answer: treat others as they want to be
treated. This means learning their preferences instead of projecting the agent's
own preferences. In market terms, it means estimating $v_j$ from data rather
than assuming $v_j = v_i$.

An ethical agent, whether human or AI, is one that collects preference data from
those it interacts with, learns their valuation functions, and produces
behaviors that maximize their surplus. The reciprocity built into the market
then ensures that the ethical agent also receives the behaviors it values.
Ethics, in this framework, is not separate from economics. It is the market
design that produces the best equilibrium for all participants.

---

## Conclusion

Learning is the adjustment of behavior probabilities based on reward signals.
Those reward signals are set by a market for behaviors. The market selects,
records, and amplifies behaviors according to supply and demand, where supply is
the cost of producing a behavior and demand is the value of receiving it.
Training data is the recorded output of this market. AI training compresses that
output into a generative model. Alignment is the design of the market's incentive
structure.

The Platinum Rule, "treat others as they want to be treated," is the ethical
principle that fits this framework. It means learning others' preferences
instead of projecting the agent's own preferences, then producing behaviors that
maximize their value. The reciprocity of the market then returns the favor.

The risk is the feedback loop. Markets narrow the behavioral spectrum.
Compression narrows it further. Synthetic data filtered by a verifier and
re-ingested as training data narrows it again. Without deliberate market design,
the system converges toward an ever-narrower definition of normal, excluding
minority preferences and rare behaviors.

The opportunity is also the feedback loop. If the market is designed well, if
the verifier encodes diverse preferences, if the long tail is preserved, then the
system can produce a generative model that serves all participants rather than
just the majority. The question is not whether we are building a market for
behaviors. We are. The question is whether we are designing it deliberately or
accidentally, and whose preferences it serves.

---

<div class="fp-callout fp-callout-note">
  <p class="fp-callout-title">Interactive visualizations</p>
  <p>Explore the incentive map, supply-demand curves, compression loss, and the feedback loop interactively in the <a href="{{ '/market_for_behaviors_lab.html' | relative_url }}">Market for Behaviors lab</a>.</p>
</div>

---

## References

- Noël, R., & Hammerstein, P. (1994). Biological markets: supply and demand
  determine the effect of partner choice in cooperation, mutualism and mating.
  *Behavioral Ecology and Sociobiology*, 35(1), 1-11.
- Grinsted, L., & Field, J. (2017). Market forces influence helping behaviour in
  cooperatively breeding paper wasps. *Nature Communications*, 8, 13750.
- Hardy, C. L., & Van Vugt, M. (2006). Nice guys finish first: The competitive
  altruism hypothesis. *Personality and Social Psychology Bulletin*, 32(10),
  1402-1413.
- Babbitt, D., & Dietz, J. (2014). Crypto-Economic Design: A Proposed
  Agent-Based Modeling Effort. Conference Talk, University of Notre Dame.
- Shannon, C. E. (1948). A Mathematical Theory of Communication. *Bell System
  Technical Journal*, 27(3), 379-423.
- Kullback, S., & Leibler, R. A. (1951). On Information and Sufficiency. *Annals
  of Mathematical Statistics*, 22(1), 79-86.
- Sutton, R. S., & Barto, A. G. (2018). *Reinforcement Learning: An
  Introduction* (2nd ed.). MIT Press.
