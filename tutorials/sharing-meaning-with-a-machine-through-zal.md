---
title: "Sharing Meaning with a Machine Through ZAL"
layout: docs
kicker: Research essay
description: "Actual ZAL sentences and glyphs expose a FIFO cycle and fixed states in a reversible machine."
---

I use ZAL, the Zeno Abstraction Language, as a shared formal representation of mathematical meaning: domain, vocabulary, assumptions, and observations. I inspect its controlled English and glyphs, ask questions, and revise it. The assistant proposes; I oversee meaning; checkers answer the encoded questions.

These controlled-English sentences parse to formal structure. Changing presentation preserves the bound object; forgetting information through abstraction needs a separate checked map.

## One sentence with two interpretations

> For every state x, there exists exactly one state y such that x advances to y.

```text
forall x in D: exists1 y in D: Step(x, y)
```

[![The unique successor statement in actual ZAL glyphs]({{ '/assets/images/zal-machine-discovery/unique-successor.png' | relative_url }})]({{ '/assets/images/zal-machine-discovery/unique-successor.png' | relative_url }})

*Brackets bind variables. Dashed wires connect their uses; solid wires connect formula operands.*

**Operation:** parse the same formula, then evaluate it against an explicit model.

| Meaning of state and step | Result |
| --- | --- |
| Three encoded FIFO queues; each step executes the complete request word `ABCD`. | **TRUE** |
| Sixteen bit patterns; a step may use any of twelve Toffoli instructions, without retaining which one. | **FALSE** |

In the second model, decimal `3` has successors `3`, `7`, and `11`. The sentence has not changed. The interpretation has.

The FIFO host has three slots and four request keys. Hits preserve its queue; misses append and evict the oldest key when full. Repeating `ABCD` cycles `ADC → DCB → BAD → ADC`, although each individual request is state-idempotent. Hit/miss responses are not idempotent.

[![The FIFO trit cycle in actual ZAL notation]({{ '/assets/images/zal-machine-discovery/fifo-trit.png' | relative_url }})]({{ '/assets/images/zal-machine-discovery/fifo-trit.png' | relative_url }})

*One displayed step is the complete word. The unique-successor sentence checks determinism; the separate transition and map checks establish this cycle and its arithmetic interpretation.*

## A reversible machine that cannot hide zero

> For every frozen state x, for every state y, if x advances to y, then x equals y.

```text
∀x ∈ D : Frozen(x) ⇒ (∀y ∈ D : Step(x, y) ⇒ x = y)
```

[![The frozen state statement in actual ZAL glyphs]({{ '/assets/images/zal-machine-discovery/frozen-family.png' | relative_url }})]({{ '/assets/images/zal-machine-discovery/frozen-family.png' | relative_url }})

Here `D` is the sixteen-state domain. `Frozen` means `{0,1,2,4,8}`, the common fixed states of all twelve legal positive-control Toffoli instructions. Controls and target are distinct; there are no extra bits or constants. `Step` is their combined transition relation.

**What ZAL does:** recovers the same formula from the sentence and glyph model, then evaluates it. **Result: TRUE.** The separate composition argument extends primitive fixedness to every finite instruction sequence.

An eight-instruction witness meets the chosen local S-box metrics. Yet every legal program key gives `E_k(0)=0`: the invariant survives every key choice. The selected witness also fixes decimal `12`. This structural restriction is known mathematics. [Shende and colleagues, Theorem 22](https://arxiv.org/pdf/quant-ph/0207001)

## From meaning to machines

Supported executable finite-state ZAL profiles have a separate factory route from controlled-English programs to contracts and generated Rust, which can be compiled to machine code. These relational property sentences instead followed **controlled English → C² → native finite-model evaluation**. They did not generate implementations satisfying the properties. Language rungs are views, not compiler stages.

The loop was proposals, exact search, counterexamples, revised meanings. The stronger FIFO conjecture of all six trit permutations failed: only three rotations were available for fixed words on that encoding. Review also caught and repaired a visual/formal binding mismatch.

I share an inspectable object, not an unspoken intention. These bounded synthetic experiments establish neither a real vulnerability nor cryptographic security. A checker result does not supply human agreement.
