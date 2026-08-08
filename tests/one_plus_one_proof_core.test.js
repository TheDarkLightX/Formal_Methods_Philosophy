"use strict";

const assert = require("node:assert/strict");
const proof = require("../assets/js/one-plus-one-proof-core.js");

const domain = [0, 1, 2, 3, 4, 5, 6];
const forward = proof.exhaustiveShapeSearch(domain);

assert.equal(forward.unique, true);
assert.equal(forward.survivor, 2);
assert.deepEqual(forward.accepted.map((receipt) => receipt.candidate), [2]);
assert.equal(forward.rejected.length, 6);
assert.equal(forward.receipts[0].reason, "empty_space");
assert.equal(forward.receipts[1].reason, "no_distinct_partner");
assert.equal(forward.receipts[2].reason, "free_transitive_involution");
assert.equal(forward.receipts[3].reason, "flip_orbit_does_not_cover_space");
assert.deepEqual(forward.receipts[2].certificate.mapping, [1, 0]);
assert.equal(forward.receipts[2].certificate.validation.accepted, true);

assert.equal(
  /candidate\s*={2,3}\s*2/.test(proof.verifyFlipOrbit.toString()),
  false,
  "the shape verifier must not compare the candidate with a stored target",
);

function* permutations(values, prefix = []) {
  if (values.length === 0) {
    yield prefix;
    return;
  }
  for (let index = 0; index < values.length; index += 1) {
    const rest = values.slice(0, index).concat(values.slice(index + 1));
    yield* permutations(rest, prefix.concat(values[index]));
  }
}

let permutationCount = 0;
for (const order of permutations(domain)) {
  const result = proof.exhaustiveShapeSearch(order);
  assert.equal(result.unique, true);
  assert.equal(result.survivor, 2, "survivor must be search-order invariant");
  permutationCount += 1;
}
assert.equal(permutationCount, 5040);

const orders = proof.makeCandidateOrders(9);
for (const order of Object.values(orders)) {
  assert.equal(new Set(order).size, 10);
  assert.equal(proof.exhaustiveShapeSearch([...order]).survivor, 2);
}

assert.equal(
  proof.validateFlipCertificate(2, [1, 0]).accepted,
  true,
);
assert.equal(
  proof.validateFlipCertificate(2, [0, 1]).accepted,
  false,
);
assert.equal(
  proof.validateFlipCertificate(3, [1, 0, 2]).accepted,
  false,
);

function* mappings(size, prefix = []) {
  if (prefix.length === size) {
    yield prefix;
    return;
  }
  for (let image = 0; image < size; image += 1) {
    yield* mappings(size, prefix.concat(image));
  }
}

let derivedLawChecks = 0;
for (let size = 0; size <= 4; size += 1) {
  let exhaustiveCertificateExists = false;
  for (const mapping of mappings(size)) {
    const validation = proof.validateFlipCertificate(size, mapping);
    if (validation.accepted) exhaustiveCertificateExists = true;
    if (validation.nonempty && validation.fixedPointFree && validation.transitive) {
      assert.equal(
        validation.involutive,
        true,
        "fixed-point freedom plus orbit coverage must force reversibility",
      );
      derivedLawChecks += 1;
    }
  }
  assert.equal(
    proof.verifyFlipOrbit(size).accepted,
    exhaustiveCertificateExists,
    "bounded shape synthesis must agree with exhaustive function enumeration",
  );
}
assert.ok(derivedLawChecks > 0);

const labelsOnly = proof.taggedCollection("L", "R");
const matching = proof.exhaustiveMatchingSearch(labelsOnly, domain);
assert.equal(matching.unique, true);
assert.equal(matching.survivor, forward.survivor);

const fingerprint = proof.relationalFingerprint(forward.survivor);
assert.equal(fingerprint.greaterThanOne, true);
assert.equal(fingerprint.lessThanThree, true);
assert.equal(fingerprint.distanceFromZero, 2);
assert.equal(fingerprint.distanceFromNine, 7);
assert.equal(fingerprint.isEven, true);
assert.equal(fingerprint.isPrime, true);

const fourier = proof.fourierReceipt(10);
assert.deepEqual(fourier.support, [2]);
for (const coefficient of fourier.spectrum) {
  assert.ok(Math.abs(coefficient.magnitude - 1) < 1e-10);
}
for (const sample of fourier.reconstructed) {
  const expected = sample.position === 2 ? 1 : 0;
  assert.ok(Math.abs(sample.re - expected) < 1e-10);
  assert.ok(Math.abs(sample.im) < 1e-10);
}
assert.ok(
  Math.abs(fourier.spectrum[1].phase - (-4 * Math.PI) / 10) < 1e-10,
);

const incomplete = proof.exhaustiveShapeSearch([0, 1, 3, 4]);
assert.equal(incomplete.unique, false);
assert.equal(incomplete.survivor, null);

assert.throws(
  () => proof.exhaustiveShapeSearch([0, 1, 1, 2]),
  /must not contain duplicates/,
);
assert.throws(
  () => proof.verifyFlipOrbit(-1),
  /nonnegative safe integer/,
);
assert.throws(
  () => proof.buildInevitabilityExperiment(6, "sideways"),
  /unknown search order/,
);

console.log(
  `one-plus-one proof core: all checks passed, including ${permutationCount} search orders and ${derivedLawChecks} derived-law certificates`,
);
