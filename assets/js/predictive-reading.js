(() => {
  const input = document.getElementById("pr-input");
  const output = document.getElementById("pr-output");
  const intensity = document.getElementById("pr-intensity");
  const intensityValue = document.getElementById("pr-intensity-value");
  const seedInput = document.getElementById("pr-seed");
  const runBtn = document.getElementById("pr-run");
  const resetBtn = document.getElementById("pr-reset");
  const copyBtn = document.getElementById("pr-copy");
  const stats = document.getElementById("pr-stats");
  const detailsRoot = document.getElementById("pr-details");

  if (
    !input ||
    !output ||
    !intensity ||
    !intensityValue ||
    !seedInput ||
    !runBtn ||
    !resetBtn ||
    !copyBtn ||
    !stats ||
    !detailsRoot
  ) {
    return;
  }

  const DEFAULT_TEXT =
    "Predictive reading uses context. The first and last letters often anchor a word, while internal letters can be perturbed. Readers can still recover meaning, but usually with some extra effort.";

  const escapeHtml = (s) =>
    s
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");

  const makeRng = (seed) => {
    let x = Number.isFinite(seed) ? (seed | 0) : 1;
    if (x === 0) x = 1;
    return () => {
      x ^= x << 13;
      x ^= x >>> 17;
      x ^= x << 5;
      return (x >>> 0) / 4294967296;
    };
  };

  const letterBag = (word) => {
    const bag = new Map();
    for (const ch of word.toLowerCase()) {
      const prev = bag.get(ch) || 0;
      bag.set(ch, prev + 1);
    }
    return bag;
  };

  const sameBag = (a, b) => {
    if (a.length !== b.length) return false;
    const x = letterBag(a);
    const y = letterBag(b);
    if (x.size !== y.size) return false;
    for (const [k, v] of x.entries()) {
      if (y.get(k) !== v) return false;
    }
    return true;
  };

  const scrambleWord = (word, scrambleProb, rng) => {
    if (word.length <= 3) return word;
    if (rng() >= scrambleProb) return word;

    const chars = word.split("");
    const start = 1;
    const end = chars.length - 1;
    const n = end - start;
    if (n < 2) return word;

    const pool = chars.slice(start, end);
    for (let i = pool.length - 1; i > 0; i -= 1) {
      const j = Math.floor(rng() * (i + 1));
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }

    for (let i = 0; i < pool.length; i += 1) {
      chars[start + i] = pool[i];
    }

    // Avoid no-op shuffles when possible.
    if (chars.join("") === word && pool.length > 1) {
      const first = chars[start];
      for (let i = start; i < end - 1; i += 1) {
        chars[i] = chars[i + 1];
      }
      chars[end - 1] = first;
    }

    return chars.join("");
  };

  const tokenRe = /([A-Za-z]+)/g;

  const scrambleParagraph = (text, scrambleProb, seed) => {
    const rng = makeRng(seed);
    const details = [];
    tokenRe.lastIndex = 0;

    let out = "";
    let last = 0;
    let m = tokenRe.exec(text);
    while (m) {
      const original = m[0];
      out += text.slice(last, m.index);
      const scrambled = scrambleWord(original, scrambleProb, rng);
      out += scrambled;

      const lenOk = original.length === scrambled.length;
      const boundaryOk =
        original.length < 4 ||
        (original[0] === scrambled[0] &&
          original[original.length - 1] === scrambled[scrambled.length - 1]);
      const bagOk = original.length < 4 || sameBag(original, scrambled);

      details.push({
        original,
        scrambled,
        len: original.length,
        changed: original !== scrambled,
        eligible: original.length >= 4,
        lenOk,
        boundaryOk,
        bagOk,
      });

      last = m.index + original.length;
      m = tokenRe.exec(text);
    }
    out += text.slice(last);

    return { text: out, details };
  };

  const renderDetails = (details) => {
    const maxRows = 200;
    detailsRoot.innerHTML = details
      .slice(0, maxRows)
      .map((d) => {
        const boundary = d.boundaryOk ? "PASS" : "FAIL";
        const bag = d.bagOk ? "PASS" : "FAIL";
        return `<tr>
          <td>${escapeHtml(d.original)}</td>
          <td>${escapeHtml(d.scrambled)}</td>
          <td>${d.len}</td>
          <td>${boundary}</td>
          <td>${bag}</td>
        </tr>`;
      })
      .join("");
  };

  const renderStats = (details) => {
    const totalWords = details.length;
    const eligibleWords = details.filter((d) => d.eligible).length;
    const changedWords = details.filter((d) => d.changed).length;
    const boundaryFails = details.filter((d) => !d.boundaryOk).length;
    const bagFails = details.filter((d) => !d.bagOk).length;
    const invariantFails = boundaryFails + bagFails;

    stats.textContent =
      `words_total: ${totalWords}\n` +
      `words_len>=4: ${eligibleWords}\n` +
      `words_changed: ${changedWords}\n` +
      `boundary_invariant_failures: ${boundaryFails}\n` +
      `bag_invariant_failures: ${bagFails}\n` +
      `invariant_failures_total: ${invariantFails}`;
  };

  const run = () => {
    const p = Math.max(0, Math.min(100, Number(intensity.value || "0"))) / 100;
    const seed = Number(seedInput.value || "1");
    const text = input.value || "";

    const result = scrambleParagraph(text, p, seed);
    output.value = result.text;
    renderStats(result.details);
    renderDetails(result.details);
  };

  const setDefaults = () => {
    input.value = DEFAULT_TEXT;
    output.value = "";
    stats.textContent = "";
    detailsRoot.innerHTML = "";
  };

  intensity.addEventListener("input", () => {
    intensityValue.textContent = String(intensity.value);
  });

  runBtn.addEventListener("click", run);

  resetBtn.addEventListener("click", () => {
    setDefaults();
    run();
  });

  copyBtn.addEventListener("click", async () => {
    const text = output.value || "";
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      copyBtn.textContent = "Copied";
      setTimeout(() => {
        copyBtn.textContent = "Copy output";
      }, 1200);
    } catch {
      copyBtn.textContent = "Copy failed";
      setTimeout(() => {
        copyBtn.textContent = "Copy output";
      }, 1200);
    }
  });

  if (!input.value.trim()) setDefaults();
  intensityValue.textContent = String(intensity.value);
  run();
})();
