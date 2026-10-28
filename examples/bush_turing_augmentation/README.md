# Companion to Why I Favor Bush on the Purpose of AI

Read the essay: https://thedarklightx.github.io/Formal_Methods_Philosophy/tutorials/bush-turing-augmentation/


This packet accompanies a first-person Formal Methods Philosophy essay. The philosophical preference is the author's stated position. The checks below concern finite reservation models only; they do not prove a philosophical preference or measure human benefit.

## Contents

- zal-evidence.json: complete structured results from ZAL inspection, layered abstraction, reservation-pair resolution, requirement conjunction, and exact-record replay.
- verify_finite_models.py: independent standard-library Python checker over the exported tables.
- independent-check-results.json: observed output of that checker.
- replay-requests.json: source-bound requests for repeating the remote checks.
- SHA256SUMS.json: hashes for the other files in this packet.

## Reproduce the local check

Run from the extracted directory:

    python3 verify_finite_models.py

The script resolves its data file relative to itself. It has no network access or third-party dependencies. It checks all rows of the stated maps and explores every reachable control-state/monitor pair. The monitor counts accepted reservations, saturating at two. This is exhaustive reachability for the stated safety property in these finite tables; it is not a finite trace-depth sampling claim.

Observed checks:
- Six-to-three state map: exact for the selected decision observation across all 24 source rows.
- Three-to-two occupancy map: sound across all 12 source rows, with additional abstract behavior.
- Refinement: exact for the selected class observation across all 12 source rows; rejection reasons remain outside that observation.
- One-use lifecycle: 3 reachable control/monitor pairs, no second accepted reservation.
- Reusable lifecycle: 5 reachable pairs, second acceptance reachable.
- Occupancy abstraction: 5 reachable pairs, second acceptance reachable.
- The specific ZAL abstract witness cannot lift at step 3 (one-based).
- Both concrete policies reject Boolean-unauthorized events and accept an authorized reserve from unseen.
- The policies differ only at released + reserve + authorized.
- The conjoined accept-reuse and reject-reuse requirements have no allowed output at that input.
- ZAL's remote replay matches the stored refutation. A matching refutation remains a refutation.

## Reproduce the ZAL checks

Use the exact operation names and arguments in replay-requests.json through the ZAL connector. The expected source identity is:

138294e67be19ba662069d3cbd713176eafe63f32c369a2262505075993664e9

The recorded reservation-pair context is:

8e44c2aefded7b5e4802f4701ce3ed2d0fe32e3c02d61f2d60cb9704d1ffcc4e

The requirement meet is a separate conjunction over the LEFT component's interface. It is not shared-state wiring, a conflict between the product's two independent resources, or a proof that the two real-world uses are incompatible. The two policies are compared as alternatives for the same decision.

If the server source changes, a source-bound rerun may reject the old identity. Do not silently transfer these receipts to a new source or a changed model.

## Assumptions and limits

The model has one request identity, a fixed initial state, atomic synchronous steps, fresh Boolean inputs, and rejection that leaves the state unchanged. Authorization is an input observation, not verified identity. No process restart, durable storage, network effects, concurrent real-world execution, liveness, fairness, or production implementation is covered. Neither the tool checks nor this script ran a theorem prover or verified native code.

The Python replay independently checks finite tables supplied by ZAL; it does not independently establish that those tables model a real service or express the intended policy. File hashes detect changes relative to this packet; they are not signatures or external attestations.

The historical source list and exact source URLs are in zal-evidence.json. Primary passages used: Bush (1945), sections III and VI–VII; Turing (1950), sections 1–2 and 7; Engelbart (1962), section I.A. The 1949 program-checking reference is grounded in the King's College Cambridge archive catalogue record, not a claimed reading of the original manuscript.

## Claim status

Historical descriptions: sourced paraphrases.
Preference for augmentation and proposed evaluation criteria: authorial position.
Checkable augmentation: local label for a design commitment.
Reservation results: finite-model evidence and independent finite-table exploration.
Improved human reasoning in practice: an empirical objective, not established by these checks.
