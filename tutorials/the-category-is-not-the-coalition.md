---
title: "The category is not the coalition"
layout: docs
kicker: Ignorance, human variation, collective enmity, and AI augmentation
description: "A personal and mathematical essay on why demographic categories cannot establish collective hostility, why large populations contain irreducible human possibility, and how AI sharpens both the opportunity and the danger."
---

## The people who formed me

My earliest memories are of a crowded, multicolored world. People of different races, languages, and customs were simply there, not as abstractions in a sociology textbook, but as the weather of my childhood. They shaped me before I had words for what they were doing.

That immersion left me with an intuition I only later learned to state precisely. A racial group, nationality, gender, class, culture, or language community can contain millions or billions of people. I will meet a vanishing fraction of them. Among the people I have not met may be someone I would admire, someone who would make me laugh until my ribs ached, someone whose teaching could redirect my life, someone whose work I would build on, or someone I would love.

The larger the unseen population grows, the more absurd it becomes to pretend that I already know each person's motives, gifts, and worth.

This essay tries to uncover the inner structure of that intuition. It asks what is mathematically wrong with converting a human category into a collective enemy, how Nazi racial ideology converted that error into state policy, and what changes when human capability is augmented by artificial intelligence.

The central answer is simple:

> **A category is not a coalition. Ignorance about a person is not evidence against that person.**

## About 117 billion mostly unknown lives

The [Population Reference Bureau](https://snapshot.prb.org/articles/how-many-people-have-ever-lived-on-earth/) estimates that roughly **117 billion members of our species have ever been born**. The bureau stresses that this is a rough figure. Demographic data do not exist for more than 99 percent of the span of human existence, so the calculation rests on assumptions about ancient population sizes and birth rates.

That uncertainty matters. The honest statement is not “exactly 117,020,448,575 people existed.” It is:

> On a reasonable demographic reconstruction, roughly 117 billion human lives have begun, and the precise number is unknown.

Inside that immense population were people with radically different combinations of originality, kindness, beauty, humor, courage, mathematical insight, athletic skill, artistic force, patience, and compatibility with particular other people.

No complete census measures these qualities. Several are observer-dependent. Beauty, humor, and personal compatibility do not even define one universal ranking.

A person is better represented by a feature vector than by a single score:

$$
z(i)=
(
z_{\mathrm{kind}}(i),
z_{\mathrm{wit}}(i),
z_{\mathrm{original}}(i),
z_{\mathrm{skill}}(i),
z_{\mathrm{compatible\ with\ me}}(i),
\ldots
).
$$

Read it exactly:

> “The feature vector of person `i` is the ordered collection containing that person's kindness feature, wit feature, originality feature, skill feature, compatibility-with-me feature, and further features not written here.”

Different people occupy different regions of this high-dimensional space. There need not be one “greatest human,” because one person may dominate one dimension while another dominates another entirely.

## A gallery is evidence, not a ranking

History supplies visible counterexamples to universal claims that ancestry determines a person's incapacity, character, or worth.

[Albert Einstein](https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/) was born in Ulm, Germany. [Emmy Noether](https://mathshistory.st-andrews.ac.uk/Biographies/Noether_Emmy/) was born in Erlangen, Germany. Both were Jewish, both were European, and both belong in any serious history of the greatest mathematical and scientific minds of the twentieth century. Einstein left Germany in 1933. Noether was dismissed from the University of Göttingen in April 1933 because she was Jewish.

Their identities did not explain away their achievements. Their achievements exposed the absurdity of a system that treated ancestry as a decoder ring for intelligence, creativity, loyalty, or human worth.

At the 1936 Berlin Olympics, [Jesse Owens won four gold medals](https://gstatic.olympics.com/s3/mc2026/documents/Education%20Programme/OVEP/English%20Toolkit/OVEP-Activity-Sheets-2023%20-%20ENGLISH%20%281%29.pdf) while the Nazi state staged a spectacle of “Aryan” superiority. His victories did not prove that one race should replace another atop a hierarchy. They supplied spectacular counterexamples to the hierarchy itself.

Other dimensions of human excellence make the same point. Marilyn Monroe became an enduring actress and cultural presence. Bruce Lee transformed martial arts and action cinema across national and cultural boundaries. Richard Pryor rewired American comedy. Srinivasa Ramanujan produced mathematics whose originality still astonishes.

This is a gallery, not a statistical sample and not a final ranking. Its logical role is limited but decisive:

$$
\exists i\in G\;\neg P(i)
\quad\Longrightarrow\quad
\neg\bigl(\forall i\in G\;P(i)\bigr).
$$

Read it exactly:

> “If there exists a person `i` in group `G` for whom property `P` is false, then it is false that every person `i` in group `G` has property `P`.”

One counterexample defeats a universal claim. History supplies far more than one.

There is also a danger in making famous people carry too much of the argument. A population does not earn protection by producing a physicist, mathematician, athlete, actress, martial artist, or comedian. A quiet person, an average person, an irritating person, and a person whose possibilities were never developed still possess a life that cannot be reduced to a category label.

Exceptional lives refute claims of group incapacity. Ordinary lives reveal why achievement was never the price of admission.

## The library compressed to one bit

Imagine a library containing millions of unread books. Each has a different plot, voice, history, argument, and ending.

Now imagine replacing every book with one catalog bit:

- **0** means outside the selected category.
- **1** means inside the selected category.

The bit may preserve one fact about each book. It cannot recover the contents it erased.

A demographic label works the same way when it is abused as a complete model of a person. Let

$$
D(i)=\text{the demographic label assigned to person }i
$$

and let

$$
P(i,t)=
\text{the person's current plans, commitments, conduct, and capabilities at time }t.
$$

Knowing $D(i)$ alone does not provide a decoder for $P(i,t)$.

The metaphor has a boundary. People are not books, and their standing does not depend on being useful information. The structural match is narrower: **lossy compression cannot recover details it discarded**.

Nazi racial ideology committed precisely this decoding error. It treated an assigned racial category as if it determined inherited intelligence, creativity, strength, loyalty, and threat. The [United States Holocaust Memorial Museum](https://encyclopedia.ushmm.org/content/en/article/nazi-racism?series=31) records that Nazi attempts to prove and measure these categories failed, but the regime continued to build policy around them.

## The quantifier error

Suppose a category contains $N$ people and evidence directly covers $y$ of them.

If the property being investigated is represented as a binary value and there are no additional constraints connecting the unseen people, then the unobserved part still has

$$
2^{N-y}
$$

possible assignments.

Read it exactly:

> “Two raised to the power `N` minus `y` is the number of possible binary assignments to the `N-y` people whose status has not been observed.”

This is not a realistic model of a complete human being. It is a deliberately tiny model that reveals the information gap. Even after compressing each person to one yes-or-no question, observing a small sample leaves an enormous number of worlds compatible with the evidence.

The invalid inference has this shape:

$$
\forall i\in O,\;P(i)
\quad\not\Rightarrow\quad
\forall i\in G,\;P(i),
$$

where $O$ is the observed subset and $G$ is the full group.

Read it exactly:

> “Property `P` holding for every person `i` in the observed subset `O` does not imply that property `P` holds for every person `i` in the full group `G`.”

The same error appears in statistics as the **ecological fallacy**. A relationship measured between group averages does not automatically become the relationship between individuals inside those groups. [William S. Robinson's classic analysis](https://fisher.stats.uwo.ca/faculty/aim/2015/9938/articles/Robinson1950AmericanSociologicalReview.pdf) showed that ecological and individual correlations can differ radically.

Unknown does not mean innocent, guilty, friendly, hostile, talented, or untalented. It means **unknown**.

The correct safety rule is:

- Quarantine the unsupported claim.
- Do not convert the people into the claim.

## The category–coalition separation principle

There are situations in which a group genuinely can act as an adversary. A small gang may share a plan, a command structure, and continuing conduct. A military unit may hold authenticated orders. A botnet may execute one signed controller. A future network of AI-augmented people may coordinate around a genuinely hostile program.

Size is therefore not the deepest invariant.

A five-person racial category is still not a coalition. A million-agent network with a shared, verified command may be one.

The relevant distinction is between two kinds of sets.

### An attribute-defined category

$$
G_d=\{i:D(i)=d\}.
$$

Read it exactly:

> “`G` sub `d` is the set of persons `i` whose demographic label `D(i)` equals `d`.”

### An action-defined coalition

$$
C_{\pi,t}
=
\{i:\operatorname{Participates}(i,\pi,t)\text{ is supported by current evidence}\}.
$$

Read it exactly:

> “`C` sub `pi,t` is the set of persons `i` for whom participation in plan `pi` at time `t` is supported by current evidence.”

Membership in $G_d$ does not logically imply membership in $C_{\pi,t}$.

This yields a testable invariance rule. Let a threat classifier receive an identity coordinate $d$ and action-relevant evidence $p$:

$$
T(d,p)=T(d',p)
$$

whenever changing $d$ to $d'$ alters only an identity attribute irrelevant to the threat claim.

Read it exactly:

> “The threat classification for identity label `d` and action-relevant evidence `p` must equal the threat classification for identity label `d-prime` and the same action-relevant evidence `p`, whenever the changed identity label is irrelevant to the claimed threat.”

The classifier may change when verified plans, conduct, participation, capability, or coordination change. It must not change merely because ancestry, race, gender, nationality, language, embodiment, or augmentation label changes.

This is a scoped invariance test related to [individual fairness](https://arxiv.org/abs/1104.3913) and [counterfactual fairness](https://arxiv.org/abs/1703.06856). It does not claim that every identity attribute is irrelevant to every question. It says that an attribute declared irrelevant to a specific threat claim must not secretly control that claim's verdict.

Even an ideology label is not automatically a participation certificate. A nominal member may dissent, be coerced, become inactive, leave, or reject violence. Evidence must be time-scoped and attached to the conduct being classified.

| Description | What it establishes |
|---|---|
| Same race, nationality, gender, or culture | An identity attribute, not a shared plan |
| Same ideological label | A possible clue requiring individual and current evidence |
| Verified participation in a specific hostile plan | A scoped basis for an action-specific threat assessment |
| Shared AI model or augmentation tool | A common tool, not necessarily a common objective |
| Attested execution of one hostile controller | Evidence of coordinated conduct, subject to attestation and time limits |

This is the essay's main invariant:

> **Collective threat attribution requires evidence of collective causal coordination. A broad identity label is not such evidence.**

## Why larger populations contain more possibility

My original intuition was that a larger population is more likely to contain someone admirable, pleasant, compatible, or lovable.

That intuition becomes a theorem only after its assumptions are stated.

For each person $i$ in a population $G$, let

$$
X_i=
\begin{cases}
1,&\text{if person }i\text{ has the selected trait},\\
0,&\text{otherwise.}
\end{cases}
$$

The number of people with the trait is

$$
K_G=\sum_{i\in G}X_i.
$$

Its expected value is

$$
\mathbb E[K_G\mid I]
=
\sum_{i\in G}\Pr(X_i=1\mid I),
$$

where $I$ is the available information.

If every term has a conditional probability of at least $p>0$, then

$$
\mathbb E[K_G\mid I]\ge |G|\,p.
$$

Read it exactly:

> “The expected number of people in group `G` with the selected trait, conditional on information `I`, is at least the size of `G` multiplied by the positive lower probability bound `p`.”

No independence assumption is needed for this expectation formula.

A stronger “at least one” statement requires stronger assumptions. If, after every sequence of failures, the conditional probability that the next unseen person is compatible remains at least $p$, then

$$
\Pr(K_G\ge1\mid I)
\ge
1-(1-p)^{|G|}.
$$

Read it exactly:

> “The probability that at least one person in `G` has the selected trait, conditional on information `I`, is at least one minus one minus `p` raised to the number of people in `G`.”

The assumption does real work. Population size alone cannot prove the prevalence of every possible trait. Race, class, and nationality are overlapping and historically shifting categories, so there is no clean universal census of “exceptional people per group.”

The defensible claim is narrower. Human populations contain enormous within-group variation. Documented originality, kindness, humor, skill, and compatibility occur across diverse populations. No broad identity category has demonstrated a monopoly on them. As a population grows, any trait that continues to occur at a positive rate has more opportunities to appear.

## The selfish theorem of open possibility

The argument does not require sainthood. It can begin with self-interest.

Let $A$ be a set of people with whom interaction remains possible, and let $u(i)$ be the personal value of a possible relationship with person $i$. Define

$$
V(A)=\sup_{i\in A}u(i).
$$

If

$$
A\subseteq B,
$$

then

$$
V(A)\le V(B).
$$

Read it exactly:

> “If opportunity set `A` is a subset of opportunity set `B`, then the greatest available relationship value in `A` cannot exceed the greatest available relationship value in `B`.”

Excluding a demographic population removes options. Under a model in which retaining an option has no unavoidable cost, removing options cannot improve the best available relationship.

This theorem is modest. It does not say every interaction is beneficial. Search, time, safety, and attention have costs. It does say that blanket exclusion can destroy opportunities before their value is known. The loss becomes strict whenever the excluded population has positive probability of containing a uniquely better friend, collaborator, teacher, partner, artist, or idea.

Prejudice can therefore be self-impoverishment. It narrows the human search space before the search begins.

## What the Holocaust normalized

The mathematical error was not a single bad estimate. It was an entire invalid inference pipeline:

```text
assign a racial label
        ↓
pretend the label determines inherited character
        ↓
pretend millions of separate people form one hostile agent
        ↓
destroy counterexamples and channels for correction
        ↓
convert uncertainty into administrative certainty
        ↓
apply irreversible policy at population scale
```

The United States Holocaust Memorial Museum [summarizes the underlying false claim directly](https://encyclopedia.ushmm.org/content/en/article/nazi-racism?series=31): Nazi ideology asserted that all Jews were an existential threat to Germany. The regime's own attempts to categorize people scientifically failed to establish its racial theories. The failure did not stop the policy.

This is **ignorance used as certainty**.

There are two kinds of ignorance to distinguish.

1. **Unavoidable ignorance:** a person has not met or studied most members of a large population.
2. **Manufactured ignorance:** an institution suppresses counterevidence, excludes the people who contradict its theory, repeats propaganda, and prevents correction.

Nazi Germany practiced the second at state scale. Universities dismissed Jewish scholars. [Academics and teachers](https://encyclopedia.ushmm.org/content/en/article/the-role-of-academics-and-teachers?series=191) helped legitimize the claim that Jews formed a foreign biological threat. The system removed counterexamples such as Noether from institutions, then treated the purified institution as confirmation of the doctrine that caused the removal.

That is a feedback loop:

$$
\text{classification}
\to
\text{exclusion}
\to
\text{biased observations}
\to
\text{stronger classification}.
$$

The loop manufactures its own apparent evidence.

Mass scale makes the inference failure catastrophic. If each of $N$ people has false-classification probability $\alpha$, then the expected number of false classifications is

$$
\alpha N.
$$

Read it exactly:

> “The expected number of false classifications equals the false-classification probability `alpha` multiplied by the population size `N`.”

This expectation uses linearity and does not require independent errors. A small error rate multiplied by millions is not a small error. When the action is irreversible, aggregate accuracy is also an inadequate defense. Each false positive is a person.

Mathematics does not generate a complete ethic from nothing. It can expose contradictions between declared principles and a policy. Assume that persons have standing that does not depend on fame or ancestry, and that coercion requires conduct-specific evidence. Under those premises, racial collective punishment fails before any utilitarian calculation begins.

## AI changes the capability function

Human capability was never a fixed function of ancestry. It depends on education, nutrition, tools, collaborators, freedom, time, health, and opportunity.

AI makes this dependence harder to ignore. A simple model is

$$
C_{\mathrm{effective}}(i,t)
=
F\bigl(
C_{\mathrm{baseline}}(i,t),
\mathrm{tools},
\mathrm{training},
\mathrm{access},
\mathrm{curiosity},
\mathrm{initiative},
\mathrm{practice},
\mathrm{collaboration},
\mathrm{verification},
\mathrm{time}
\bigr).
$$

Read it exactly:

> “The effective capability of person `i` at time `t` is a function of that person's baseline capability, tools, training, access, curiosity, initiative, practice, collaboration, verification, and available time.”

Current evidence supports a scoped version of augmentation, not the claim that every person with a chatbot instantly becomes Einstein or Noether. In a [preregistered experiment on professional writing tasks](https://doi.org/10.1126/science.adh2586), generative AI improved average speed and output quality. A [separate experiment with management consultants](https://doi.org/10.1287/orsc.2025.21838) found a jagged frontier: assistance helped on tasks inside the tested model's capability boundary and reduced correctness on a task outside it.

An ordinary person can already use AI to produce some intellectual artifacts that previously required more training, more time, or a team of specialists. That is meaningful augmentation. It is not evidence that every augmented person possesses Noether's originality, Einstein's physical intuition, or uniformly expert judgment.

The honest present-tense claim is:

> **AI can raise effective capability on some tasks, while reliable judgment, access, skill, and verification remain necessary.**

## The jagged superhero present

The nation of superheroes is a possible future. The present is more jagged.

Current AI provides something closer to **local superpowers**. A person may become dramatically faster at drafting, translating, programming, searching, visualizing, or exploring one problem, then encounter a neighboring task where the same system is unreliable. The power has an irregular boundary.

Access alone does not guarantee intellectual growth. Passive use may still save time, so it would be too strong to claim that AI never helps an indolent user. The larger compounding benefit appears when a person enters an active loop:

```text
notice something
       ↓
ask a question
       ↓
generate possibilities
       ↓
test and check
       ↓
revise the question
       ↓
build or discover something
       ↓
notice something new
```

Curiosity turns one answer into the next experiment. Verification prevents a persuasive mistake from entering the growing knowledge base. Persistence keeps the loop running after the first failure.

Let `K_n` be the checked knowledge available after cycle `n`. A simplified update rule is

$$
K_{n+1}
=
K_n
\cup
\operatorname{Checked}
\bigl(
\operatorname{AI}(\operatorname{Question}(K_n))
\bigr).
$$

Read it exactly:

> “The checked knowledge after cycle `n+1` equals the checked knowledge after cycle `n`, union the AI-generated results of a question formed from the current knowledge that pass the checker.”

If no new question is asked, the loop stops. If generated answers are never checked, output may accumulate while knowledge does not. If failure produces a better question, even negative results become fuel for the next cycle.

This suggests an inspiring but bounded practical principle:

> **AI amplifies curiosity most powerfully when curiosity is joined to checking and sustained action.**

This is a workflow claim, not a theorem that permanently divides humanity into “curious” and “indolent” types. Curiosity, energy, and engagement can change with health, security, education, tools, subject matter, and time. AI can sometimes help awaken curiosity by making a previously inaccessible subject explorable. The relevant state is what a person is doing now, not a fixed label attached to the person.

### AI rewards curiosity

AI lowers the cost of asking one more question. It can answer at midnight, generate ten alternatives, translate an unfamiliar term, write a small experiment, and help inspect why the experiment failed. A curious person can immediately turn the result into another question.

This creates a feedback mechanism:

$$
\text{curiosity}
\to
\text{more inquiry cycles}
\to
\text{more checked gains}
\to
\text{better questions}
\to
\text{more curiosity}.
$$

Let `q_i(T)` be the number of inquiry-and-checking cycles person `i` completes by time `T`, and let `g_{i,r}` be the checked gain from cycle `r`. Define the person's accumulated checked gain as

$$
G_i(T)
=
\sum_{r=1}^{q_i(T)}g_{i,r}.
$$

Read it exactly:

> “The accumulated checked gain of person `i` by time `T` equals the sum of the checked gain from every inquiry cycle `r`, beginning with cycle one and ending with the number of cycles that person completed by time `T`.”

If two people have comparable access and the checked cycles have comparable positive expected value, then the person who sustains more useful cycles has more opportunities to compound knowledge. AI rewards curiosity in this operational sense: curiosity causes more exploration of the tool's reachable space.

The formula is a model, not a law of personality. Some cycles produce zero gain. Some subjects require rest, teachers, laboratories, or lived experience that a model cannot supply. Curiosity can also be misdirected unless checking and judgment remain inside the loop.

### A possible curiosity divide

Society may not divide into curious and incurious populations. It could, however, develop a new inequality:

```text
same nominal access to AI
          ↓
different time, confidence, curiosity,
education, safety, and checking tools
          ↓
different numbers of useful inquiry cycles
          ↓
compounding capability gaps
```

This is a possible failure mode rather than a prediction. People are not born into permanent curiosity classes. Engagement changes, and institutions can either awaken it or suppress it.

A nation-of-superheroes program would therefore distribute more than model access. It would teach people how to form questions, run experiments, inspect sources, use formal checkers, learn from counterexamples, and continue after failure. The objective is to help more people enter the curiosity loop instead of allowing augmentation to become another concentrated advantage.

## Two futures: geniuses in a data center or heroes with power-ups

Anthropic CEO Dario Amodei has described powerful AI as a [**“country of geniuses in a datacenter”**](https://www.anthropic.com/news/paris-ai-summit). In that image, millions of highly capable AI instances run inside concentrated computing infrastructure. They work quickly, operate in parallel, and may be directed toward science, engineering, economic production, intelligence, or military power.

That image asks:

> How much synthetic intelligence can the data center contain?

My nation-of-superheroes vision asks a different question:

> How many existing people can gain new powers while retaining their own agency, curiosity, relationships, local knowledge, and purposes?

The visions can coexist. A powerful data center may supply the systems that augment people. They still optimize different quantities. One emphasizes the capability concentrated inside machines. The other emphasizes the capability distributed through human lives.

| Question | Country of geniuses in a data center | Nation of superheroes |
|---|---|---|
| Where does the new capability appear? | Primarily in AI instances and computing infrastructure | In human-AI partnerships distributed through society |
| What is multiplied? | Synthetic expert instances | The reachable abilities of existing people |
| What remains scarce? | Control of compute, models, and infrastructure | Access, curiosity, judgment, time, education, and verification |
| Central danger | Concentrated power and displacement | Unequal access, dependency, manipulation, and unreliable use |
| Central promise | Enormous automated research and production | Broad human agency and participation in discovery |

This contrast does not imply that Amodei opposes human augmentation. His public statement also calls for monitoring whether AI augments or automates work and for ensuring that people share in its economic benefits. The contrast separates two system designs, not two mutually exclusive camps.

### AI as a Super Mario power-up

In *Super Mario Bros.*, a power-up does not erase Mario and replace him with a different player. It changes the actions available to the existing hero.

The Mushroom makes Mario more resilient. The Fire Flower adds a new kind of attack. A Star creates a powerful but temporary state. Different powers help with different parts of a level.

The AI analogy follows five rules:

1. The person remains the agent.
2. The power-up expands the person's available actions.
3. Curiosity finds places where the new action may help.
4. Judgment chooses when and how to use it.
5. A checker rejects powers that only appear to work.

### The real power-up is a neuro-symbolic harness

In my own work, I do not treat a language model's output as the result. I treat it as a proposal.

The model exists inside a harness:

```text
my question, goal, and judgment
              ↓
      neural model proposes
              ↓
Lean, solvers, tests, simulations,
and source checks inspect the claim
              ↓
evidence and counterexamples are recorded
              ↓
an explicit gate accepts, rejects, or
leaves the claim unresolved
```

This is **neuro-symbolic** in a practical sense. A neural model searches a large, flexible possibility space. Symbolic and formal tools check precisely stated obligations. Empirical tests and sources check claims that cannot be settled by deduction alone.

Let $x$ be an AI-originated proposed result and let $J(x)$ be the set of checks required for that type of result. The acceptance rule is

$$
\operatorname{Accept}(x)
\iff
\operatorname{AIProposes}(x)
\land
J(x)\ne\varnothing
\land
\forall j\in J(x),
\operatorname{Check}_j(x)=\operatorname{PASS}.
$$

Read it exactly:

> “Result `x` is accepted if and only if AI proposes `x`, the required checker set for `x` is not empty, and, for every checker `j` in that required set, checker `j` returns `PASS` on `x`.”

For a Lean theorem, `PASS` means that Lean accepted the encoded statement and proof under the declared environment. It does not prove that an informal English sentence was translated correctly, that every premise is true in the physical world, or that the theorem answers the intended question. Those are separate obligations.

The harness therefore does not prevent the neural model from hallucinating. It reduces the chance that a hallucination is **accepted as knowledge** within the coverage of the selected checks. An unformalized claim, an inadequate test, a bad specification, or a compromised tool can still escape the boundary unless another check detects it.

The Super Mario image now has a more exact mapping:

| Game world | Human-AI system |
|---|---|
| Hero | The existing person with goals and lived context |
| Power-up item | The AI proposer and tools made available to that person |
| New move | A candidate ability or action |
| Rules engine | Lean, a solver, a test suite, a simulator, or another checker |
| Cleared obstacle | A checked result that satisfies the declared goal |
| Lost life or failed attempt | A counterexample or rejected candidate retained as negative knowledge |

The useful unit is therefore not raw AI:

$$
\operatorname{PowerSystem}(i)
=
\bigl(
\operatorname{Human}_i,
\operatorname{AIProposer},
\operatorname{Checkers},
\operatorname{EvidenceMemory},
\operatorname{PromotionGate}
\bigr).
$$

Read it exactly:

> “The power system for person `i` is the ordered system containing that person, the AI proposer, the checkers, the evidence memory, and the promotion gate.”

The human supplies direction and interpretation. The model expands the search. The checkers constrain acceptance. The evidence memory lets failures improve future searches. The gate decides what may enter the trusted knowledge base.

Let $A_i$ be the set of actions person $i$ can reliably perform without AI. Define the checked augmented action set by

$$
A_i^{+}
=
A_i
\cup
\left\{
a:
\operatorname{Accept}_i(a)
\right\}.
$$

Read it exactly:

> “The augmented action set of person `i` equals the original action set of person `i`, union the actions `a` accepted for that person by the declared neuro-symbolic harness.”

The actual power-up is the verified difference:

$$
\operatorname{PowerUp}(i)=A_i^{+}\setminus A_i.
$$

Read it exactly:

> “The power-up of person `i` is the set of actions in the checked augmented action set that were not already in the person's original action set.”

This definition preserves the person and measures the new reachable abilities. Someone who could describe an idea but not program it may gain the ability to build a checked prototype. Someone blocked by technical language may gain translation and explanation. A programmer may explore mathematics, and a mathematician may test an algorithm. The hero was already present. AI changes the reachable part of the level.

The curiosity loop determines how much of that expanded action set is discovered and exercised. A power-up left untouched on the screen changes nothing. One activated without learning the controls may be wasted. One combined with practice, checking, and a meaningful goal may transform the game.

### The mathematical difference is distribution

Suppose society contains $N$ people and $C_i^{+}(\tau)$ records whether person $i$, after checked augmentation, can perform task family $\tau$ at a declared standard:

$$
C_i^{+}(\tau)
=
\begin{cases}
1,&\text{if person }i\text{ meets the declared standard on }\tau,\\
0,&\text{otherwise.}
\end{cases}
$$

Define post-augmentation capability coverage by

$$
\operatorname{Coverage}^{+}(\tau)
=
\frac{1}{N}
\sum_{i=1}^{N}C_i^{+}(\tau).
$$

Read it exactly:

> “The post-augmentation capability coverage for task family `tau` equals one divided by the number of people, multiplied by the sum over all people of whether each person meets the declared standard for that task family after checked augmentation.”

This is a distribution measure, not by itself a causal estimate of what AI added. A causal claim would require a credible baseline or counterfactual. If $\operatorname{Coverage}^{0}(\tau)$ is measured before augmentation under a comparable design, the descriptive change is

$$
\Delta\operatorname{Coverage}(\tau)
=
\operatorname{Coverage}^{+}(\tau)
-
\operatorname{Coverage}^{0}(\tau).
$$

Read it exactly:

> “The change in capability coverage for task family `tau` equals post-augmentation coverage minus baseline coverage.”

Interpreting that change as an effect of AI still depends on how the comparison was constructed.

A data center could become extraordinarily capable while post-augmentation coverage remains low. That happens if only a few institutions control the capability or if most people receive automated outputs without gaining agency. A less concentrated system could have lower peak machine capability while producing higher capability coverage across society.

The nation-of-superheroes objective is therefore not merely

$$
\max\;\text{total AI capability}.
$$

It also includes

$$
\max\;\operatorname{Coverage}^{+}(\tau)
$$

across many valuable task families, subject to reliability, freedom, access, and human control.

### Where the power-up metaphor stops

Video-game power-ups have known rules. Current AI systems do not. A neuro-symbolic harness can reduce accepted errors only where its specifications and checks are adequate. AI can still generate false answers, weaken performance outside its jagged frontier, or steer a person toward a goal the person did not choose. Real people also have richer identities, responsibilities, and relationships than game characters.

The metaphor is valid only for this limited structure:

> **A well-governed neuro-symbolic harness can expand a person's checked action set without replacing the person's agency.**

That is the superhero future worth building: powerful intelligence in data centers, but power flowing outward into curious human beings rather than remaining concentrated behind the walls of the data center.

The stronger post-AGI claim is conditional:

> **If reliable expert-level systems become broadly accessible, then the population capable of high-level intellectual production may expand dramatically.**

Under that condition, a nation could begin to resemble a distributed league of cognitively augmented problem-solvers. In the strongest version of my metaphor, it becomes a **nation of superheroes**. The metaphor does not mean equal powers or infallibility. It means that ordinary citizens gain forms of intellectual leverage once reserved for rare experts and large institutions.

Reaching that future would require more than distributing software. It would require broad access, education in asking and checking questions, freedom to explore, time to practice, and institutions that reward discovery rather than passive consumption.

Globally, the possibility is larger still. Billions of people would not merely consume the work of rare experts. They could propose, test, build, translate, and discover with powerful assistance.

This would further weaken every theory that treats intellectual rank as a fixed property of race, class, nationality, or birthplace. It would not be the first reason those theories failed. Their premises were already false. AI makes the neglected variables, especially tools and access, impossible to hide.

## AI does not automatically end collective hatred

AI does not nullify propaganda, authoritarian incentives, competition for land and resources, conspiracy theories, or the desire to create a scapegoat. It can amplify them.

The same technology that expands intellectual opportunity can also scale:

```text
personalized propaganda
automated stereotyping
deepfakes and fabricated evidence
mass surveillance
autonomous targeting
large coordinated bot or cyborg networks
```

This makes the category–coalition distinction more important.

A future hostile AI or human-AI coalition could be large. Evidence might be compressed into a shared signed controller, authenticated command structure, common attack plan, and verified execution traces. That would be action-relevant evidence.

Using the same AI tool, having the same augmentation, belonging to the same nationality, or sharing a physical trait would not be.

Even strong coalition evidence remains scoped. It can expire. Attestation can be spoofed. Members can leave. A verified threat does not authorize unlimited harm, and it does not erase the standing of every person associated with an institution, territory, technology, or ideology.

AI expands both sides of the equation:

$$
\text{human possibility}
\uparrow
\qquad\text{and}\qquad
\text{classification power}
\uparrow.
$$

The first can enrich civilization. The second can industrialize an ancient error.

## A compact decision invariant

The essay can be compressed into seven rules.

1. **A person is not a category label.** A label preserves too little information to determine a life.
2. **Unknown remains unknown.** Missing evidence cannot be silently recoded as hostility or inferiority.
3. **A universal claim requires universal coverage or a valid causal theorem.** A sample, stereotype, or group average is not enough.
4. **Swap irrelevant identity labels.** If the verdict changes while action-relevant evidence stays fixed, the classifier has failed the invariance test.
5. **Distinguish categories from coalitions.** Collective threat claims require current evidence of collective causal coordination.
6. **Preserve open possibility.** Removing populations from the human search space can destroy unknown friendships, collaborations, discoveries, and forms of beauty.
7. **Raise the evidence burden with the scope and irreversibility of the action.** A population-scale irreversible decision cannot be justified by a low-resolution heuristic.

The deepest error behind genocidal racial reasoning is a false claim of knowledge:

> **A state compresses millions of distinct people into one bit, mistakes the compression artifact for the people, treats a category as a conspiracy, and turns ignorance into certainty.**

The corrective is equally compact:

> **Quarantine the unsupported claim, not the human beings. Judge conduct through current evidence. Leave the unseen future open long enough for people to reveal who they are.**

## Claim boundary and sources

This essay offers a mathematical model of one family of inference errors. It does not claim that probability theory alone supplies a complete moral philosophy. Its population formulas are conditional on stated probability assumptions. Its AI claims distinguish measured results on bounded tasks from speculative post-AGI scenarios.

Sources and further reading:

- [Population Reference Bureau, “How Many People Have Ever Lived on Earth?”](https://snapshot.prb.org/articles/how-many-people-have-ever-lived-on-earth/)
- [United States Holocaust Memorial Museum, “Nazi Racism”](https://encyclopedia.ushmm.org/content/en/article/nazi-racism?series=31)
- [United States Holocaust Memorial Museum, “The Role of Academics and Teachers”](https://encyclopedia.ushmm.org/content/en/article/the-role-of-academics-and-teachers?series=191)
- [Nobel Prize, “Albert Einstein: Biographical”](https://www.nobelprize.org/prizes/physics/1921/einstein/biographical/)
- [MacTutor, “Emmy Noether”](https://mathshistory.st-andrews.ac.uk/Biographies/Noether_Emmy/)
- [International Olympic Committee educational material on Jesse Owens at Berlin 1936](https://gstatic.olympics.com/s3/mc2026/documents/Education%20Programme/OVEP/English%20Toolkit/OVEP-Activity-Sheets-2023%20-%20ENGLISH%20%281%29.pdf)
- [William S. Robinson, “Ecological Correlations and the Behavior of Individuals”](https://fisher.stats.uwo.ca/faculty/aim/2015/9938/articles/Robinson1950AmericanSociologicalReview.pdf)
- [Dwork et al., “Fairness Through Awareness”](https://arxiv.org/abs/1104.3913)
- [Kusner et al., “Counterfactual Fairness”](https://arxiv.org/abs/1703.06856)
- [Noy and Zhang, “Experimental Evidence on the Productivity Effects of Generative Artificial Intelligence”](https://doi.org/10.1126/science.adh2586)
- [Dell'Acqua et al., “Navigating the Jagged Technological Frontier”](https://doi.org/10.1287/orsc.2025.21838)
- [Dario Amodei, statement at the Paris AI Action Summit](https://www.anthropic.com/news/paris-ai-summit)
