# The Lament Configuration and Making Bad States Impossible

Read the essay: https://thedarklightx.github.io/Formal_Methods_Philosophy/tutorials/lament-configuration/


Companion evidence for a standalone essay in Formal Methods Philosophy, with a deliberately small, invented model inspired by Clive Barker's fictional puzzle box.

## Files

- model.json: the invented original and redesigned transition tables, input/output domains, encoding, and assumptions.
- check_model.py: a standard-library-only Python checker.
- check-results.json: its observed output.
- zal-evidence.json: complete structured ZAL results, including source identity and exact recorded checks.
- replay-requests.json: the remote check requests in dependency order.
- SHA256SUMS.json: hashes of every other file in this packet.

Run the local check with:

    python3 check_model.py

## Exact model

The original has four states: Closed, Aligned, Reward, Summon.
The redesign has three valid states: Closed, Aligned, Reward.
The actions are Twist, Slide, Reset.
Every action consumes one atomic step.
Reward is a harmless goal in this invented toy, not the original fiction's promised supernatural experience.
The effect domain of the redesign is None or Enjoy.

The original reaches Summon via Twist, Slide, Twist.
The redesign reaches Reward via Twist, Slide.
A Twist from Reward in the redesign is blocked: it retains Reward and emits None.
All nine redesigned state/action cases preserve safe states and effects.
Every state of the redesign is reachable, so the closure check is not hiding a dangerous unreachable row.

The mutation keeps every state name safe but emits Summon on Reward + Twist. The checker detects this, demonstrating why a state-only invariant is insufficient for an effectful implementation.

## What ZAL checked

The current registered ZAL profiles do not accept an arbitrary custom transition graph. ZAL was used to check a representation boundary with its supported byte-interval profile. A separate local checker enumerates the custom graph.

Code 0 means Closed, 1 means Aligned, 2 means Reward, and 3 means Summon.
ZAL's observed interval semantics are lower-inclusive and upper-exclusive.
The specification is [0, 3), accepting exactly 0, 1, and 2.

The intentionally faulty candidate [0, 4) was refuted on byte 3, with exactly one mismatch among all 256 inputs.
The candidate [0, 3) matched all 256 inputs.
Both records matched remote replay.

ZAL source identity:
138294e67be19ba662069d3cbd713176eafe63f32c369a2262505075993664e9

Final context identity:
c92c43551a2c0d12a9e2764e69dae7427f2d4784ce7087c30b94a0cb6d3e6a84

Use replay-requests.json through the ZAL connector. A changed source may invalidate an old record. Do not transfer this evidence to an edited definition or silently weaken the version checks.

## What follows and what does not

Initial membership and closure of all allowed transitions support an induction over any finite sequence of actions. The local reachability search exhausts this finite graph; it is not limited to a chosen sequence length.

These checks do not prove the fidelity of the model to a physical mechanism, verify a production implementation, prove an implementation's type safety, or validate arbitrary decoded inputs. ZAL's generated Rust was not compiled or executed, and no theorem prover was run. The Python code checks the exported finite definitions and the declared mutant.

Input validation, hidden effects, concurrency, hardware faults, and unsafe interfaces require a separate implementation argument. No literal infinite-force or indestructible-material claim is made.

The essay uses Summon as an unacceptable outcome by stipulation, not as a claim that every character who summons the Cenobites dies. Cenobites-as-programs and Leviathan-as-governing-power are interpretive analogies.

## Primary sources

Clive Barker's official Hellraiser discussion and screenplay excerpts:
https://clivebarker.info/hellraiser.html

Official bibliography page for The Hellbound Heart:
https://www.clivebarker.com/html/visions/bib/book/books/heart.htm
