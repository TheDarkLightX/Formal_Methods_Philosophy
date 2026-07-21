---
title: "Data as Programs, Graphs as Computation: What Learning Does"
layout: docs
kicker: Tutorial
description: "A tutorial connecting equations, computation graphs, coding rate reduction, and the fight against entropy. Learning discovers programs that compress similarities and contrast differences, turning unpredictable observations into predictable structure."
---

# Data as Programs, Graphs as Computation: What Learning Does

An equation is three things at once. It is a fact about the world. It is a procedure for computing one value from others. And it is a compression scheme that lets a reviewer store less information. These three roles seem distinct until a simple example shows them converging.

This tutorial develops that convergence into a precise picture of what learning does. The claim is scoped: learning, in the sense developed here, is the discovery of representations that compress recurring structure while preserving meaningful differences. The MCR² principle (Maximal Coding Rate Reduction) makes this precise. The tutorial connects that principle to equations, computation graphs, entropy, and the distinction between computation and intelligence.

## How to read this tutorial

For the equation and compression picture, read Sections 1 and 2. For the entropy argument, read Sections 2 and 3. For the data-as-program duality, read Sections 4 and 5. For the MCR² objective and ReduNet, read Sections 6 and 7. For the computation-versus-intelligence distinction, read Section 8. For limits and honest non-claims, read Section 9.

## 1. The equation that compresses

Consider observations with three coordinates: `x`, `y`, and `z`. Without any known structure, each observation is a point in a three-dimensional space. Encoding one observation at precision `epsilon` requires encoding three independent values.

Now suppose the data satisfies:

```text
z = x + y
```

This equation is a constraint. It says that `z` is not independent. Once `x` and `y` are known, `z` is determined. The observations no longer fill a three-dimensional volume. They lie on a two-dimensional surface inside it.

```text
before:  3 apparent dimensions, 3 degrees of freedom
after:   3 apparent dimensions, 2 degrees of freedom
```

The equation compresses. Instead of encoding `x`, `y`, and `z` separately, a reviewer encodes `x`, `y`, and the rule `z = x + y`. The rule costs a small, fixed amount. Each observation then costs two values plus the shared rule, instead of three values.

The equation is simultaneously:

- **a fact**: a statement about how these variables relate;
- **a program**: given `x` and `y`, compute `z` by addition;
- **a compression scheme**: encode two coordinates and the rule, instead of three coordinates.

These three roles are not metaphors for each other. They are literal descriptions of what the equation does in different contexts. Section 4 develops the duality between the first two roles. This section develops the third.

### The residual

The equation does not eliminate `z`. It makes `z` predictable from `(x, y)`. If the equation is exact, the residual is zero. If the equation is approximate, the residual is the part of `z` that the rule does not explain:

```text
observation = predictable structure + unpredictable residual
```

The residual is what remains after compression. A good equation makes the residual small. A perfect equation makes it zero. A bad equation leaves most of the observation unexplained, compressing almost nothing.

This split is the foundation for the rest of the tutorial. Learning discovers the predictable structure. The unpredictable residual is either genuine noise, structure not yet discovered, or structure outside the chosen model class.

## 2. Learning as a fight against entropy

On a fixed finite set of possible outcomes, entropy measures unpredictability. The uniform distribution has maximum entropy: every outcome is equally likely, so no prediction is better than any other. A deterministic distribution has zero entropy: one outcome is certain, so prediction is trivial.

Learning exposes a reduction in uncertainty when a discovered rule supplies useful side information. The joint distribution already determines `H(z)` and `H(z | x, y)`. Learning discovers a predictor that can use the dependence.

```text
without side information:  H(z)
with x and y:               H(z | x, y)
reduction:                  H(z) - H(z | x, y) = I(z ; x, y)
```

The uncertainty reduction can support compression. Under a declared source distribution and coding model, Shannon's source-coding theorem connects entropy to the best achievable expected code length. Lower conditional entropy can therefore lower the expected cost of encoding `z` when `x` and `y` are available to the decoder.

### The fight is selective

A naive reading says: learning reduces entropy, so more learning means less entropy, and the ideal is zero entropy. This is wrong for two reasons.

First, collapsing everything to a single point achieves zero entropy and zero information. A representation that maps every input to the same output has no entropy and no usefulness. It cannot distinguish, classify, or act.

Second, meaningful learning reduces entropy *where structure exists* and preserves it *where differences matter*. A dog classifier that compresses all dog images into one vector has reduced within-class entropy. If it also compresses all cat images into the same vector, it has destroyed the between-class information that makes classification possible.

The selective principle is:

```text
reduce entropy within recurring structures (compression)
preserve entropy between distinct structures (contrast)
```

This is the principle that MCR² formalizes in Section 6. The formalization makes "where structure exists" and "where differences matter" precise through the partition of observations into classes and the coding rate gap between the whole and its parts.

### What learning does not eliminate

Learning never makes everything predictable. An honest model identifies three kinds of residual:

1. **Irreducible uncertainty under the declared observation model**: this may include quantum measurement noise under a chosen interpretation, thermal noise at the modeled scale, or deterministic chaos made unpredictable by finite-precision initial conditions.
2. **Unmeasured causes**: the observation depends on variables the model does not capture. The residual is predictable in principle, if the missing variables were observed.
3. **Model mismatch**: the true structure is outside the chosen model class. A linear model cannot capture a nonlinear constraint, no matter how much data is available.

Good learning identifies which kind of residual remains. Uncertainty awareness, knowing when not to trust a prediction, is part of the learning process, not a separate concern.

## 3. Degrees of freedom and the geometry of compression

The equation `z = x + y` reduces degrees of freedom from three to two. This geometric picture generalizes.

An observation with `d` coordinates lives in a `d`-dimensional space. Without structure, it can occupy any point in that space. Near a regular point, `k` independent smooth equality constraints whose Jacobian has rank `k` reduce the local dimension by `k`. The observations then lie on a lower-dimensional surface inside the full space.

```text
d dimensions, k independent constraints
=>  d - k degrees of freedom
=>  observations lie on a (d - k)-dimensional surface
```

Such a lower-dimensional surface has zero ambient `d`-dimensional volume. The useful comparison is at finite precision: a bounded regular surface can be covered by fewer `epsilon`-scale cells than a full-dimensional region because it has fewer directions in which a point can vary.

This is the geometric-information-theoretic equivalence:

```text
constraint            <=>  fewer degrees of freedom
fewer degrees of freedom  <=>  smaller effective volume
smaller effective volume  <=>  lower coding rate
lower coding rate      <=>  fewer bits at precision epsilon
```

Each discovered independent constraint can reduce effective volume under the regularity conditions above. A reduction in finite-precision volume can yield compression. Intelligence, in the sense of this tutorial, is the process of discovering constraints that reduce volume where structure recurs and preserve volume where differences matter.

### Why not collapse to a point

A zero-vector representation has zero degrees of freedom, zero volume, and zero coding rate under the formula in Section 6. It is the maximum compression. It is also useless, because it cannot represent variation.

A useful representation preserves enough dimensions to capture meaningful variation within a class while eliminating dimensions that merely encode noise or redundancy. A dog subspace needs enough dimensions to represent different breeds, poses, and lighting conditions. It does not need the thousands of dimensions of raw pixel space, most of which encode redundant or irrelevant variation.

The principle is:

```text
same kind  =>  shared low-dimensional structure
different kinds  =>  different structures
```

"Low-dimensional" is relative to the full space, not zero. Each class subspace retains the dimensions that carry meaningful within-class variation.

## 4. Data as programs

The equation `z = x + y` can be encoded as data: a string of symbols that can be written, stored, copied, and transmitted. Oriented from `x` and `y` to `z` and paired with arithmetic semantics, it defines a program that produces `z` by addition.

This duality is not a metaphor. It is a basic structure of computation. A Turing machine can be encoded as a description that specifies a computation. A lambda expression can be represented as syntax and evaluated under language semantics. A neural network's weights and architecture can be encoded as data and interpreted to compute outputs.

This is **code-data duality**. Homoiconicity is a stronger, language-specific case in which a program's primary representation is also a data structure in the language, as in Lisp. The common thread is that an encoded representation can be studied as data and interpreted as a procedure.

### The shortest program

Kolmogorov complexity measures the information content of a string by the length of the shortest program that produces it on a fixed universal machine. By a counting argument, most `n`-bit strings cannot be shortened by more than a constant. A string with regular structure may have a much shorter program that encodes the rule and generates the string from it.

```text
Kolmogorov complexity of s  =  length of shortest program P such that P() = s
```

The equation `z = x + y` gives a short conditional program for generating `z` from `(x, y)`:

```text
K(z | x, y) <= length(addition program) + O(1)
```

It need not be the shortest program, and Kolmogorov complexity is not computable in general. The description becomes especially economical when the same rule applies across many observations, because the rule cost can be amortized.

Minimum description length (MDL) is a statistical development of the same idea: select a model by minimizing the combined description of the model and the data encoded with it. Solomonoff induction assigns greater prior weight to shorter programs and predicts with a mixture over programs consistent with the observations.

All three traditions share the claim: **compression is discovery.** Finding a shorter description is finding structure. The equation that reduces dimensions is the same act as the program that is shorter than the data it generates.

### The continuous analogue

Kolmogorov complexity is defined over discrete programs and strings. For real-valued observations at finite precision, the coding rate introduced in Section 6 plays an analogous role for representation code length. It does not include the description length of the model or program itself.

## 5. Graphs as computation

An equation is a one-step computation. A computation graph makes the steps visible.

```text
equation:      z = x + y

graph:         x ──┐
                   ├──( + )──► z
               y ──┘
```

Under the declared left-to-right orientation and arithmetic semantics, the graph and the equation describe the same computation. The graph shows data flowing from inputs through an operation to an output. The equation states the same relationship in a single line.

A deep neural network is a multi-step computation graph:

```text
input ──► [layer 1] ──► [layer 2] ──► ... ──► [layer L] ──► representation
```

Each layer applies a transformation (typically a linear map followed by a nonlinearity) to its input and passes the result to the next layer. The full network is a composition of these transformations. The weights of the network are the program's parameters. The architecture is the program's structure.

The network is simultaneously:

- **data**: a set of matrices and biases, stored on disk, serializable to a file;
- **a program**: a specification of how values flow from inputs through operations to outputs;
- **a learned model**: the result of optimizing an objective over training data; its intermediate or final activations form learned representations of particular inputs.

This is the same triple role as the equation. The equation is the simplest case (one operation, one constraint). The network is the general case (many operations, many learned parameters, a complex transformation).

### Programs and computation graphs

Many computations can be represented as graphs whose nodes are operations and whose edges are data dependencies. Straight-line differentiable programs have a particularly direct graph representation. Full programs may also require control flow, cycles, state, or graphs constructed dynamically at runtime.

The relationship is:

```text
program  --represented by-->  computation graph  --encoded as-->  data
```

A serialized model file is data. Loading it constructs a computation graph. Running a forward pass executes the graph. Training optimizes the graph's parameters to minimize (or maximize) an objective. The cycle from data to graph to execution to optimization is the cycle of learning.

## 6. The coding rate

The coding rate used here estimates the number of bits needed to encode a set of representations at a given precision under the finite-sample model in the MCR² paper. It is analogous to program length, but it does not count the representation function itself.

For a representation matrix `Z` with `d`-dimensional features and `m` samples, the coding rate at precision `epsilon` is:

```text
R(Z, epsilon) = (1/2) log_2 det(I + (d / (m * epsilon^2)) * Z * Z^T)
```

The base-2 logarithm gives bits. A natural logarithm would give nats. Here `Z * Z^T` is an uncentered second-moment matrix; it is proportional to a covariance matrix only when the features have been centered.

The determinant measures the effective volume occupied by the representation. The key relationships are:

```text
correlated data  =>  concentrated in fewer directions  =>  smaller volume  =>  lower rate
spread-out data  =>  occupies more directions           =>  larger volume   =>  higher rate
```

Data concentrated in a low-dimensional subspace has a small determinant because most eigenvalues of `Z * Z^T` are near zero. The identity term keeps the determinant positive, while the factor containing `epsilon` sets the precision scale.

### Why the log-determinant

The determinant of a positive-definite scatter or covariance matrix is proportional to the squared volume of its associated ellipsoid. Taking the log converts the multiplicative volume scale into an additive quantity. Under the finite-sample coding model used to derive this formula, the factor `1/2` matches the corresponding Gaussian volume calculation.

More generally, a bounded regular set with intrinsic dimension `k` needs on the order of `k * log(1/epsilon)` bits to identify an `epsilon`-scale cell, up to constants and modeling assumptions. A comparable full-dimensional set scales with `d * log(1/epsilon)`. The log-determinant captures this subspace-like scaling for the representation model used here.

### The equation as a rate reduction

Return to `z = x + y`. Under a bounded regular-support approximation, unconstrained triples `(x, y, z)` have dimension 3, while triples satisfying the equation lie on a 2-dimensional surface. The precision-dependent description length therefore changes from roughly `3 * log(1/epsilon)` to `2 * log(1/epsilon)`, up to additive constants.

The equation is a rate reduction. It reduces the coding rate by one dimension's worth of bits. The discovered constraint is the discovered compression.

## 7. Compress similarities, contrast differences

Minimizing the total coding rate `R(Z, epsilon)` is not enough. A representation that maps every input to the zero vector achieves the minimum: `Z * Z^T` is zero, so the rate is zero. This representation is useless because it cannot distinguish anything.

The MCR² principle, introduced by Yaodong Yu, Kwan Ho Ryan Chan, Chong You, Chaobing Song, and Yi Ma in [Learning Diverse and Discriminative Representations via the Principle of Maximal Coding Rate Reduction](https://arxiv.org/abs/2006.08558), refines the objective. Instead of minimizing the total rate, it maximizes the gap between the total rate and the partitioned rate:

```text
Delta R = R(Z, epsilon) - R^c(Z, epsilon | Pi)
```

where:

- `Z` is the learned representation;
- `R(Z, epsilon)` is the coding rate of all features considered together;
- `R^c(Z, epsilon | Pi)` is the weighted sum of coding rates after partitioning the features into classes or groups according to a partition `Pi`;
- `epsilon` is the desired encoding precision.

The objective is:

```text
max Delta R
```

The comparison assumes declared feature-normalization or energy constraints. Without scale control, rate values from different representations are not directly comparable.

### What the two terms do

**Within each class**, MCR² wants the coding rate to be low:

```text
R(Z_j, epsilon) should be small
```

Similar examples within a class should become correlated and describable by a compact, low-dimensional structure. Dog images should occupy a dog subspace with fewer dimensions than the full pixel space.

**Across all classes**, MCR² wants the total coding rate to be high:

```text
R(Z, epsilon) should be large
```

Different class structures should occupy distinct directions and remain discriminable. Under the paper's idealized subspace conditions, the class subspaces become orthogonal.

The gap `Delta R` measures how much second-order geometric structure the chosen encoder, partition, and precision reveal. A large gap means separate coding exposes more structure than joint coding under this model. A small gap means this partition does not expose much additional structure at the chosen precision.

### The principle in one line

```text
within-group compression + between-group expansion
```

Or:

```text
compress similarities, preserve differences
```

"Preserve differences" is more precise than "separate differences." The goal is not to maximize arbitrary distance between classes. The goal is to make distinct class structures incoherent enough to distinguish at the given precision. Under ideal conditions, orthogonality is sufficient. More separation than that is wasted capacity.

### Why not compress each class to a point

MCR² does not force every dog image into one identical vector. It tries to place dog images in a relatively low-dimensional dog subspace while preserving meaningful variation within that subspace. The theory encourages each class subspace to retain maximal useful dimension with roughly isotropic variation, rather than collapsing to one dimension.

```text
same kind     =>  shared low-dimensional structure (not a point)
different kinds  =>  different subspaces (orthogonal in the ideal case)
```

A point has zero dimensions and zero information. A subspace has enough dimensions to represent within-class variation while being compact relative to the full space. The compression is relative, not absolute.

### ReduNet: the discovered program

ReduNet derives a layered architecture by unrolling iterative gradient-ascent-style updates on `Delta R`. One update becomes one layer; its operators are constructed layer by layer and may later be fine-tuned.

```text
input ──► [ReduNet layer 1] ──► [ReduNet layer 2] ──► ... ──► representation Z
                                                              maximizing Delta R
```

The graph is the program. Construction or training is the discovery process. The objective defines what makes a discovery good. Each layer is intended to move the representation toward greater rate reduction; a strict increase depends on the update and step-size assumptions.

This is analogous to discovering equations. Under the bounded-support approximation, `z = x + y` removes one effective dimension. A ReduNet update is designed to improve the rate-reduction gap by compressing within classes while preserving distinctions across them. Both use compression as evidence of discovered structure.

## 8. Computation versus intelligence

The distinction between computation and intelligence is a distinction between two roles, not two substances.

**Computation** is the execution of a fixed program. Given a computation graph and its parameters, transform inputs to outputs. This is deterministic (or stochastic with fixed seeds), reproducible, and fully specified. Running a trained classifier on a new image is computation. Evaluating `z = x + y` for given `x` and `y` is computation.

**Intelligence** is the discovery of a good program. Given observations, find a computation graph and parameters that compress similarities and contrast differences. This is a search over a space of possible programs, guided by an objective. Training a classifier is intelligence. Discovering that `z = x + y` is intelligence. Both find structure that was not known before.

```text
computation:   execute a fixed graph to transform inputs into outputs
intelligence:  search for a graph that compresses and contrasts well
```

### The distinction matters

Collapsing the two leads to two traps.

The first trap says intelligence is fundamentally different from computation, perhaps non-computational. The search for a good program is itself a computation: gradient descent, evolutionary search, or brute-force enumeration are all computational processes. The distinction is about role, not capability. Intelligence is the role of discovery; computation is the role of execution. The discovery process is computational, but its product, the learned program, is what we call intelligence.

The second trap says intelligence is merely computation, so the distinction is uninteresting. Execution and discovery have different guarantees, different costs, and different failure modes. A fixed program that classifies well on seen data is not the same as a system that can discover good classifiers for new problems. The former is a tool; the latter is closer to what we mean by intelligence. A program that memorizes training data executes perfectly but discovers nothing: it makes the seen predictable without making the unseen predictable.

### What makes a discovery good

MCR² provides one precise answer: a good discovery maximizes `Delta R`. It compresses within classes and preserves differences across classes. A trivial discovery (identity transformation) does not compress. A degenerate discovery (constant function) compresses everything but preserves no differences. The intelligent discovery is the one that finds the specific transformation that does both.

This is one formalization of one strand of intelligence. Reasoning, planning, language, and goal-directed behavior are not directly captured by coding rate reduction. Section 9 returns to this limit.

### Learning makes the unpredictable predictable

The entropy framing from Section 2 connects here. Learning can discover a representation or rule that lowers conditional uncertainty or description length within classes. The discovered structure is a set of constraints (equations, transformations) that makes observations more predictable from fewer inputs.

```text
without the rule:  uncertainty is H(observation)
using the rule:     uncertainty is H(observation | rule inputs)
remaining residual = irreducible uncertainty under the model
                     + unmeasured causes
                     + model mismatch
```

Learning makes the surprising less surprising. It does so by finding the rules that render the surprising predictable. The rules are programs. The programs are graphs. The graphs are data. The cycle closes.

Memorization makes the seen predictable by storing it verbatim. Deeper learning seeks rules that also predict unseen cases. Compression can support generalization when the same regularity persists beyond the training sample, but a short rule is not sufficient evidence by itself. Held-out predictive performance provides a separate test.

### Learning, behavior, and effective freedom

Learning can be understood as what makes reality more predictable. If a model captures a regularity in data, its predictive gain can be written as:

```text
Delta L = L(data) - L(data | model)
```

The model explains the part of the data removed from the conditional description. If the model itself was learned from the same data, complete accounting also includes the model cost:

```text
Delta L_net = L(data) - [L(model) + L(data | model)]
```

The useful test is predictive. A model has learned a reusable regularity when it shortens the description of new observations, not only the observations from which it was constructed.

Intelligence can then be framed as increasing effective freedom: preserving valuable futures that remain reachable despite uncertainty and disturbance. One goal-relative definition is:

```text
EffectiveFreedom(s; G)
  = sum over s' in Reach(s) of
      value_G(s') * robustness(s')
```

`Reach(s)` contains the states available from `s` under admissible behavior. `value_G(s')` measures how useful a reachable state is relative to goal `G`. `robustness(s')` measures whether the option survives plausible perturbations. This is a measure of reachable options, not the geometric dimension discussed in Section 3. A finite horizon, a state granularity, and a perturbation model are needed to make it computable.

These definitions are declarative. They state what successful learning and effective action do before choosing how to implement them. Once the desired behavior is precise, the definition becomes a target for discovering a mechanism or algorithm:

```text
declarative objective
  -> candidate mechanism
  -> measured behavior
  -> comparison with the objective
  -> algorithm update
```

The same perspective applies to behavior. A behavior can be understood as a bid placed into reality. An action commits time, energy, attention, money, reputation, or opportunity cost in exchange for an uncertain result. The environment acts as a market for behavior by returning benefits, costs, and a successor state:

```text
a_t ~ pi_t(a | s_t)

(s_t, a_t)
  -> (benefits_t, costs_t, s_(t+1))

r_t = benefits_t - costs_t
```

The comparison between benefits and costs is relative to the agent's goals. A policy `pi_t(a | s)` distributes behavioral probability across the actions available in a state. Behaviorism emphasizes that consequences reshape this distribution:

```text
P(a | s) increases when a is reinforced in s
```

This is a selection principle, not an automatic one-step rule. Delayed outcomes, uncertain transitions, and competing actions create a credit-assignment problem. A learning procedure must determine which behavior deserves the update:

```text
pi_(t+1)
  = Update(pi_t, s_t, a_t, r_t, s_(t+1))
```

The behavioral loop is:

```text
goal
  -> behavior
  -> environmental feedback
  -> prediction or reward error
  -> algorithm update
```

Repeated interaction can support a second loop:

```text
reinforcement
  -> regularity discovery
  -> world model
  -> planning
```

The first loop changes which actions are likely. The second learns how actions transform states, allowing consequences to be predicted before acting.

In reinforcement learning, the behavior that works is defined relative to an optimal policy. For discounted reward:

```text
J(pi)
  = E_pi[sum from t = 0 to infinity of gamma^t r_t]

pi* in argmax_pi J(pi)
```

The action-value function records the expected future return from choosing `a` in `s` and then following policy `pi`:

```text
Q^pi(s, a)
  = E[r_t + gamma r_(t+1) + gamma^2 r_(t+2) + ...
      | s_t = s, a_t = a, pi]

pi*(s) selects actions in argmax_a Q*(s, a)
```

This defines what successful behavior does. The engineering problem is to find an algorithm that implements or approximates `pi*` under the available observations, data, computation, and safety constraints.

For agentic training, the natural evidence unit is often a behavior trajectory rather than an isolated response:

```text
tau = (s_0, a_0, r_0, s_1, a_1, r_1, ..., s_T, a_T, r_T, s_(T+1))

Return(tau)
  = sum from t = 0 to T of gamma^t r_t
```

Some trajectories produce better measurable outcomes than others. Training can compare complete action sequences, assign credit to the decisions that changed the outcome, and increase the probability of policies that produce better trajectories. This is especially important when success depends on ordering, tool use, recovery, or delayed consequences.

The best observed trajectory is not automatically the best policy. A sequence may succeed through luck or fail after a small change in state. Agentic evaluation therefore needs repeated rollouts, held-out tasks, robustness checks, and explicit rejection of unsafe trajectories. The falsifiable claim is that trajectory-level training should improve long-horizon outcomes and recovery compared with training on isolated responses under matched data and computation.

## 9. Limits and honest non-claims

Several assumptions in this framing need explicit scoping.

### MCR² is not a complete theory of intelligence

MCR² formalizes one aspect of intelligence: discovering representations that compress within classes and discriminate between classes. Reasoning, planning, language understanding, and goal-directed behavior are not directly captured by coding rate reduction. The tutorial presents MCR² as a precise formalization of one strand, not as the whole story.

### The partition is given, not discovered

In the basic MCR² formulation, the class partition `Pi` is part of the input. The classes are known before learning begins. Unsupervised variants exist, but the core theory assumes the partition is given. This is a significant limit: intelligence often involves discovering what the relevant groupings are, rather than compressing within groupings that are already known.

### The subspace model is idealized

MCR² assumes each class lies near a linear subspace. Real data, including images, text, and audio, may lie on nonlinear manifolds. ReduNet extends to nonlinear cases through its network architecture, but the theoretical guarantees are strongest under the subspace assumption.

### The equation analogy is approximate

A learned network does not produce a clean equation like `z = x + y`. It produces a high-dimensional, nonlinear transformation whose compression properties are measured statistically, not symbolically. The equation serves as an intuition pump. The statistical reality of deep representations is messier: the "constraints" are soft, the "residuals" are distributed, and the "degrees of freedom" are effective rather than exact.

### Compression is not always intelligence

A zip file compresses data without understanding it. A hash function reduces arbitrary data to a fixed-length digest without discovering structure. Compression becomes intelligence when the discovered representation generalizes: when the rule that compresses seen data also predicts unseen data. Generalization is the property that separates learning from memorization, and MCR² does not by itself guarantee it. The theory assumes that the rate-reducing representation captures class structure that generalizes, but this depends on the data, the partition, and the model class.

### Entropy reduction has a direction

The "fight against entropy" in this tutorial is selective: reduce uncertainty within classes while preserving distinctions between classes. This is not the same as minimizing total entropy. Minimizing total coding rate alone permits collapse to a point, while preserving all raw variation does not by itself establish compression or learning. The MCR² objective makes the direction precise under its declared representation and partition model.

## 10. Connections

### Minimum description length and Solomonoff induction

The connection between compression and discovery has a long history. Rissanen's MDL principle selects models by combined model and data description length. Solomonoff induction weights shorter generating programs more heavily in a predictive mixture. Kolmogorov complexity measures a finite string by shortest-program length. MCR² has a family resemblance to these ideas, but it optimizes a finite-sample geometric coding-rate gap rather than program description length.

### Rate-distortion theory

The coding rate formula is motivated by rate-distortion theory, which studies the tradeoff between encoding cost and reconstruction fidelity. The precision `epsilon` plays the role of the allowed distortion. Smaller `epsilon` means higher fidelity and higher rate. At a declared `epsilon`, MCR² compares the coding rate of the whole representation with the weighted rates of its parts.

### Information geometry

The log-determinant used here measures volume through a representation's second-moment geometry. Information geometry instead uses objects such as the Fisher information matrix to define a metric on a parametric family of probability distributions. These matrices are different. Any formal connection requires a specified probabilistic model that relates parameter sensitivity to feature covariance.

### Computation graphs and differentiable programming

The data-as-program duality supports differentiable programming. A computation graph built from differentiable operations can be differentiated with respect to its parameters and optimized by gradient methods. This is one mechanism by which discovery is implemented as computational search. The graph structure makes dependencies inspectable and parameters adjustable.

### The free energy principle

The entropy reduction picture connects loosely to Friston's free energy principle, which models adaptive systems as minimizing variational free energy, a tractable upper bound on surprisal under a generative model. The connection is approximate: the free energy principle includes perception, learning, and action selection, while MCR² concerns representation geometry. They should not be treated as the same objective.

## Conclusion

Learning discovers programs that compress. The programs are equations in the simple case and computation graphs in the general case. The compression is selective: it reduces coding rate within recurring structures and preserves it between distinct ones. MCR² makes this selective principle precise through the rate reduction gap.

The discovered programs make observations more predictable under a declared model. The residual, what the programs do not explain, may reflect irreducible uncertainty under that model, unmeasured causes, or model mismatch. Good learning distinguishes these possibilities where the available evidence permits.

Computation executes discovered programs. In the working definition used here, intelligence discovers or improves them. The distinction is about role, not substance. The search for a good program is itself computational, and its product is a representation or policy that improves prediction or effective freedom under stated goals.

## Further reading

- Yaodong Yu, Kwan Ho Ryan Chan, Chong You, Chaobing Song, and Yi Ma. [Learning Diverse and Discriminative Representations via the Principle of Maximal Coding Rate Reduction](https://arxiv.org/abs/2006.08558). The original MCR² paper.
- Kwan Ho Ryan Chan, Yaodong Yu, Chong You, Haozhi Qi, John Wright, and Yi Ma. [ReduNet: A White-box Deep Network from the Principle of Maximizing Rate Reduction](https://arxiv.org/abs/2105.10446). The layered construction derived by unrolling rate-reduction updates.
- Jorma Rissanen. [Modeling by Shortest Data Description](https://doi.org/10.1016/0005-1098(78)90005-5). The MDL principle.
- Ray Solomonoff. [A Formal Theory of Inductive Inference, Part I](https://doi.org/10.1016/S0019-9958(64)90223-2). Solomonoff induction and the shortest-program principle.
- Thomas Cover and Joy Thomas. [Elements of Information Theory](https://doi.org/10.1002/047174882X). Rate-distortion theory and the coding rate.
- Chris Olah. [Neural Networks, Manifolds, and Topology](https://colah.github.io/posts/2014-03-NN-Manifolds-Topology/). A visual introduction to representations as geometric objects.
- Karl Friston. [The Free-Energy Principle: A Unified Brain Theory?](https://doi.org/10.1038/nrn2787). Biological systems as surprise minimizers.
