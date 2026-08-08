(function attachOnePlusOneProof(root, factory) {
  "use strict";

  const api = factory();

  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }

  if (root) {
    root.OnePlusOneProof = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function buildOnePlusOneProof() {
  "use strict";

  function assertNatural(value, label) {
    if (!Number.isSafeInteger(value) || value < 0) {
      throw new TypeError(`${label} must be a nonnegative safe integer`);
    }
  }

  function validateCandidateDomain(candidates) {
    if (!Array.isArray(candidates)) {
      throw new TypeError("candidate domain must be an array");
    }

    const seen = new Set();
    for (const candidate of candidates) {
      assertNatural(candidate, "candidate");
      if (seen.has(candidate)) {
        throw new TypeError("candidate domain must not contain duplicates");
      }
      seen.add(candidate);
    }
  }

  function positionsFor(candidate) {
    assertNatural(candidate, "candidate");
    return Object.freeze(
      Array.from({ length: candidate }, (_, index) => index),
    );
  }

  function validateFlipCertificate(candidate, mapping) {
    assertNatural(candidate, "candidate");
    if (!Array.isArray(mapping) || mapping.length !== candidate) {
      return Object.freeze({
        accepted: false,
        nonempty: candidate > 0,
        involutive: false,
        fixedPointFree: false,
        transitive: false,
        reason: "mapping_has_wrong_domain",
      });
    }

    const positions = positionsFor(candidate);
    const total = mapping.every(
      (image) => Number.isSafeInteger(image) && image >= 0 && image < candidate,
    );
    const nonempty = positions.length > 0;
    const involutive =
      total && positions.every((position) => mapping[mapping[position]] === position);
    const fixedPointFree =
      total && positions.every((position) => mapping[position] !== position);
    const transitive =
      total &&
      positions.every((from) =>
        positions.every((to) => to === from || to === mapping[from]),
      );
    const accepted = nonempty && involutive && fixedPointFree && transitive;

    return Object.freeze({
      accepted,
      nonempty,
      involutive,
      fixedPointFree,
      transitive,
      reason: accepted ? "free_transitive_involution" : "invalid_flip_shape",
    });
  }

  function verifyFlipOrbit(candidate) {
    assertNatural(candidate, "candidate");
    const positions = positionsFor(candidate);
    let searchedDistinctPairs = 0;

    if (positions.length === 0) {
      return Object.freeze({
        candidate,
        accepted: false,
        reason: "empty_space",
        searchedDistinctPairs,
        certificate: null,
      });
    }

    for (const pivot of positions) {
      for (const partner of positions) {
        if (partner === pivot) continue;
        searchedDistinctPairs += 1;

        const coversSpace = positions.every(
          (position) => position === pivot || position === partner,
        );
        if (!coversSpace) continue;

        const mapping = positions.map((position) =>
          position === pivot ? partner : pivot,
        );
        const validation = validateFlipCertificate(candidate, mapping);
        if (validation.accepted) {
          return Object.freeze({
            candidate,
            accepted: true,
            reason: validation.reason,
            searchedDistinctPairs,
            certificate: Object.freeze({
              pivot,
              partner,
              mapping: Object.freeze(mapping),
              validation,
            }),
          });
        }
      }
    }

    return Object.freeze({
      candidate,
      accepted: false,
      reason:
        searchedDistinctPairs === 0
          ? "no_distinct_partner"
          : "flip_orbit_does_not_cover_space",
      searchedDistinctPairs,
      certificate: null,
    });
  }

  function exhaustiveShapeSearch(candidates) {
    validateCandidateDomain(candidates);
    const receipts = candidates.map(verifyFlipOrbit);
    const accepted = receipts.filter((receipt) => receipt.accepted);
    const rejected = receipts.filter((receipt) => !receipt.accepted);

    return Object.freeze({
      domain: Object.freeze([...candidates]),
      receipts: Object.freeze(receipts),
      accepted: Object.freeze(accepted),
      rejected: Object.freeze(rejected),
      unique: accepted.length === 1,
      survivor: accepted.length === 1 ? accepted[0].candidate : null,
    });
  }

  function makeCandidateOrders(maxCandidate) {
    assertNatural(maxCandidate, "maxCandidate");
    const forward = Array.from(
      { length: maxCandidate + 1 },
      (_, index) => index,
    );
    const backward = [...forward].reverse();
    const outsideIn = [];
    let low = 0;
    let high = maxCandidate;

    while (low <= high) {
      outsideIn.push(high);
      if (low !== high) outsideIn.push(low);
      low += 1;
      high -= 1;
    }

    const scrambled = [...forward].sort((left, right) => {
      const modulus = maxCandidate + 2;
      const leftKey = (left * (maxCandidate + 1) + 3) % modulus;
      const rightKey = (right * (maxCandidate + 1) + 3) % modulus;
      return leftKey - rightKey || right - left;
    });

    return Object.freeze({
      forward: Object.freeze(forward),
      backward: Object.freeze(backward),
      outsideIn: Object.freeze(outsideIn),
      scrambled: Object.freeze(scrambled),
    });
  }

  function relationalFingerprint(candidate) {
    assertNatural(candidate, "candidate");
    return Object.freeze({
      greaterThanOne: candidate > 1,
      lessThanThree: candidate < 3,
      distanceFromZero: Math.abs(candidate),
      distanceFromNine: Math.abs(candidate - 9),
      isEven: candidate % 2 === 0,
      isPrime: candidate >= 2 && (() => {
        for (let divisor = 2; divisor * divisor <= candidate; divisor += 1) {
          if (candidate % divisor === 0) return false;
        }
        return true;
      })(),
    });
  }

  function taggedCollection(leftName, rightName) {
    if (typeof leftName !== "string" || typeof rightName !== "string") {
      throw new TypeError("collection labels must be strings");
    }
    return Object.freeze([
      Object.freeze({ tag: "L", label: leftName }),
      Object.freeze({ tag: "R", label: rightName }),
    ]);
  }

  function verifyPerfectMatching(items, candidate) {
    assertNatural(candidate, "candidate");
    const slots = positionsFor(candidate);
    const matchedCount = Math.min(items.length, slots.length);
    const matching = Array.from({ length: matchedCount }, (_, index) =>
      Object.freeze({ item: items[index], slot: slots[index] }),
    );

    if (items.length > slots.length) {
      return Object.freeze({
        candidate,
        accepted: false,
        reason: "too_few_slots",
        matching: Object.freeze(matching),
        unmatchedItems: Object.freeze(items.slice(matchedCount)),
        unmatchedSlots: Object.freeze([]),
      });
    }
    if (slots.length > items.length) {
      return Object.freeze({
        candidate,
        accepted: false,
        reason: "too_many_slots",
        matching: Object.freeze(matching),
        unmatchedItems: Object.freeze([]),
        unmatchedSlots: Object.freeze(slots.slice(matchedCount)),
      });
    }
    return Object.freeze({
      candidate,
      accepted: true,
      reason: "bijection_witnessed",
      matching: Object.freeze(matching),
      unmatchedItems: Object.freeze([]),
      unmatchedSlots: Object.freeze([]),
    });
  }

  function exhaustiveMatchingSearch(items, candidates) {
    validateCandidateDomain(candidates);
    const receipts = candidates.map((candidate) =>
      verifyPerfectMatching(items, candidate),
    );
    const accepted = receipts.filter((receipt) => receipt.accepted);
    return Object.freeze({
      domain: Object.freeze([...candidates]),
      receipts: Object.freeze(receipts),
      unique: accepted.length === 1,
      survivor: accepted.length === 1 ? accepted[0].candidate : null,
    });
  }

  function acceptanceSignal(size) {
    assertNatural(size, "size");
    if (size === 0) throw new TypeError("size must be positive");
    return Object.freeze(
      Array.from(
        { length: size },
        (_, candidate) => (verifyFlipOrbit(candidate).accepted ? 1 : 0),
      ),
    );
  }

  function discreteFourierTransform(realSignal) {
    if (!Array.isArray(realSignal) || realSignal.length === 0) {
      throw new TypeError("signal must be a nonempty array");
    }
    if (!realSignal.every((value) => Number.isFinite(value))) {
      throw new TypeError("signal values must be finite numbers");
    }

    const size = realSignal.length;
    const spectrum = [];
    for (let frequency = 0; frequency < size; frequency += 1) {
      let re = 0;
      let im = 0;
      for (let position = 0; position < size; position += 1) {
        const angle = (-2 * Math.PI * frequency * position) / size;
        re += realSignal[position] * Math.cos(angle);
        im += realSignal[position] * Math.sin(angle);
      }
      spectrum.push(Object.freeze({
        frequency,
        re,
        im,
        magnitude: Math.hypot(re, im),
        phase: Math.atan2(im, re),
      }));
    }
    return Object.freeze(spectrum);
  }

  function inverseDiscreteFourierTransform(spectrum) {
    if (!Array.isArray(spectrum) || spectrum.length === 0) {
      throw new TypeError("spectrum must be a nonempty array");
    }
    const size = spectrum.length;
    return Object.freeze(
      Array.from({ length: size }, (_, position) => {
        let re = 0;
        let im = 0;
        for (let frequency = 0; frequency < size; frequency += 1) {
          const coefficient = spectrum[frequency];
          if (!Number.isFinite(coefficient.re) || !Number.isFinite(coefficient.im)) {
            throw new TypeError("spectrum coefficients must be finite");
          }
          const angle = (2 * Math.PI * frequency * position) / size;
          re += coefficient.re * Math.cos(angle) - coefficient.im * Math.sin(angle);
          im += coefficient.re * Math.sin(angle) + coefficient.im * Math.cos(angle);
        }
        return Object.freeze({ position, re: re / size, im: im / size });
      }),
    );
  }

  function fourierReceipt(size) {
    const signal = acceptanceSignal(size);
    const spectrum = discreteFourierTransform([...signal]);
    const reconstructed = inverseDiscreteFourierTransform([...spectrum]);
    const support = signal
      .map((value, position) => ({ value, position }))
      .filter((entry) => entry.value !== 0)
      .map((entry) => entry.position);
    return Object.freeze({
      convention: "F[k] = sum_n f[n] exp(-2 pi i k n / N)",
      size,
      signal,
      spectrum,
      reconstructed,
      support: Object.freeze(support),
    });
  }

  function buildInevitabilityExperiment(maxCandidate, orderName) {
    assertNatural(maxCandidate, "maxCandidate");
    const orders = makeCandidateOrders(maxCandidate);
    if (!Object.prototype.hasOwnProperty.call(orders, orderName)) {
      throw new TypeError("unknown search order");
    }

    const order = orders[orderName];
    const shapeSearch = exhaustiveShapeSearch([...order]);
    const labelsOnly = taggedCollection("left occurrence", "right occurrence");
    const matchingSearch = exhaustiveMatchingSearch(labelsOnly, [...order]);
    return Object.freeze({
      orderName,
      orders,
      shapeSearch,
      labelsOnly,
      matchingSearch,
      agreement:
        shapeSearch.unique &&
        matchingSearch.unique &&
        shapeSearch.survivor === matchingSearch.survivor,
      fingerprint:
        shapeSearch.survivor === null
          ? null
          : relationalFingerprint(shapeSearch.survivor),
      fourier: fourierReceipt(maxCandidate + 1),
    });
  }

  return Object.freeze({
    validateCandidateDomain,
    positionsFor,
    validateFlipCertificate,
    verifyFlipOrbit,
    exhaustiveShapeSearch,
    makeCandidateOrders,
    relationalFingerprint,
    taggedCollection,
    verifyPerfectMatching,
    exhaustiveMatchingSearch,
    acceptanceSignal,
    discreteFourierTransform,
    inverseDiscreteFourierTransform,
    fourierReceipt,
    buildInevitabilityExperiment,
  });
});
