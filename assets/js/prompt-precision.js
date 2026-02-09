(() => {
  const input = document.getElementById("pp-input");
  const output = document.getElementById("pp-output");
  const format = document.getElementById("pp-format");
  const mode = document.getElementById("pp-mode");
  const runBtn = document.getElementById("pp-run");
  const resetBtn = document.getElementById("pp-reset");
  const copyBtn = document.getElementById("pp-copy");
  const notes = document.getElementById("pp-notes");

  if (
    !input ||
    !output ||
    !format ||
    !mode ||
    !runBtn ||
    !resetBtn ||
    !copyBtn ||
    !notes
  ) {
    return;
  }

  const DEFAULT_TEXT = `# Controlled-Lojban prompt (demo)
# Pattern: (.i)? zoi <kdelim> <key> <kdelim> du zoi <vdelim> <value> <vdelim>

.i zoi gy goal gy du zoi gy Solve a hard problem by changing representation. gy
.i zoi gy problem gy du zoi gy Find a reliable verification method when direct exploration is too slow. gy
.i zoi gy domain_a gy du zoi gy The original system description (large state machine, huge search space). gy
.i zoi gy why_intractable gy du zoi gy State explosion and limited observability. gy
.i zoi gy target_domain_b gy du zoi gy A smaller model (modules with interfaces, or an abstract domain). gy
.i zoi gy mapping_f gy du zoi gy Describe an abstraction or decomposition mapping from A to B. gy
.i zoi gy preserve gy du zoi gy List what must be preserved (safety invariants, interface behavior). gy
.i zoi gy solve_in_b gy du zoi gy Verify obligations in B (local proofs and composition rules). gy
.i zoi gy inverse_mapping gy du zoi gy Reconstruct an A-level result (refinement or witness trace). gy
.i zoi gy validation gy du zoi gy Re-run gates in A and stress-test edge cases. gy

# Extra keys are allowed in Warn mode:
.i zoi gy mode gy du zoi gy constraint_relaxation gy
`;

  const CANON_KEYS = [
    "goal",
    "problem",
    "domain_a",
    "why_intractable",
    "target_domain_b",
    "mapping_f",
    "preserve",
    "solve_in_b",
    "inverse_mapping",
    "validation",
  ];

  const KEY_ALIASES = new Map([
    ["domain a", "domain_a"],
    ["domain_a", "domain_a"],
    ["domain b", "target_domain_b"],
    ["domain_b", "target_domain_b"],
    ["target_domain_b", "target_domain_b"],
    ["mapping", "mapping_f"],
    ["mapping_f", "mapping_f"],
    ["inverse", "inverse_mapping"],
    ["inverse_mapping", "inverse_mapping"],
  ]);

  const normalizeKey = (raw) => {
    const k = raw.trim().toLowerCase().replaceAll(/\s+/g, " ");
    if (KEY_ALIASES.has(k)) return KEY_ALIASES.get(k);
    return k.replaceAll(" ", "_").replaceAll(/[^a-z0-9_]/g, "");
  };

  const escapeRegex = (s) => s.replaceAll(/[.*+?^${}()|[\]\\]/g, "\\$&");

  const isWordBoundary = (s, i) => {
    if (i <= 0) return true;
    const ch = s[i - 1];
    return /\s/.test(ch);
  };

  const skipWs = (s, i) => {
    let j = i;
    while (j < s.length && /\s/.test(s[j])) j += 1;
    return j;
  };

  const startsWithWordCI = (s, i, word) => {
    const slice = s.slice(i, i + word.length);
    if (slice.toLowerCase() !== word) return false;
    const next = s[i + word.length];
    return !next || /\s/.test(next);
  };

  const parseZoi = (s, i, lineNo, errors) => {
    let j = skipWs(s, i);
    if (!startsWithWordCI(s, j, "zoi")) {
      errors.push(`line ${lineNo}: expected "zoi"`);
      return { ok: false, endIndex: i };
    }
    j = skipWs(s, j + 3);
    const mDelim = /^\S+/.exec(s.slice(j));
    if (!mDelim) {
      errors.push(`line ${lineNo}: missing zoi delimiter`);
      return { ok: false, endIndex: i };
    }
    const delim = mDelim[0];
    j += delim.length;
    j = skipWs(s, j);

    const closeRe = new RegExp(`\\s${escapeRegex(delim)}(?:\\s|$)`, "g");
    closeRe.lastIndex = j;
    const mClose = closeRe.exec(s);
    if (!mClose) {
      errors.push(`line ${lineNo}: unterminated zoi quote (missing closing "${delim}")`);
      return { ok: false, endIndex: i };
    }

    const body = s.slice(j, mClose.index).trim();
    const endIndex = mClose.index + mClose[0].length;
    return { ok: true, body, endIndex };
  };

  const assignKeyValue = (rawKey, value, lineNo, parsingMode, spec, extras, warnings, errors) => {
    const key = normalizeKey(rawKey);
    const isKnown = CANON_KEYS.includes(key);
    if (!isKnown) {
      const msg = `line ${lineNo}: unknown key "${rawKey}" (normalized as "${key}")`;
      if (parsingMode === "strict") {
        errors.push(msg);
      } else {
        warnings.push(msg);
        extras[key] = value;
      }
      return;
    }

    if (Object.prototype.hasOwnProperty.call(spec, key)) {
      warnings.push(`line ${lineNo}: duplicate key "${key}", overwriting earlier value`);
    }
    spec[key] = value;
  };

  const parseDuPairsInLine = (line, lineNo, parsingMode, spec, extras, warnings, errors) => {
    let s = line.trim();
    if (s.toLowerCase().startsWith(".i")) s = s.slice(2).trim();

    let i = 0;
    let sawAny = false;

    while (i < s.length) {
      i = skipWs(s, i);
      if (i >= s.length) break;
      if (!startsWithWordCI(s, i, "zoi")) break;

      const keyQuote = parseZoi(s, i, lineNo, errors);
      if (!keyQuote.ok) return sawAny;
      let j = skipWs(s, keyQuote.endIndex);
      if (!startsWithWordCI(s, j, "du")) {
        errors.push(`line ${lineNo}: expected "du" after key quote`);
        return sawAny;
      }
      j = skipWs(s, j + 2);

      const valQuote = parseZoi(s, j, lineNo, errors);
      if (!valQuote.ok) return sawAny;

      const rawKey = keyQuote.body;
      const value = valQuote.body;
      if (!rawKey) {
        errors.push(`line ${lineNo}: empty key in zoi quote`);
        i = valQuote.endIndex;
        continue;
      }
      if (!value) warnings.push(`line ${lineNo}: empty value for key "${rawKey}"`);
      assignKeyValue(rawKey, value, lineNo, parsingMode, spec, extras, warnings, errors);
      sawAny = true;
      i = valQuote.endIndex;
    }

    return sawAny;
  };

  const parseKeyValueLine = (line, lineNo, parsingMode, spec, extras, warnings, errors) => {
    const withoutPrefix = line.startsWith(".i") ? line.slice(2).trim() : line;
    const idx = withoutPrefix.indexOf(":");
    if (idx < 0) return false;

    const rawKey = withoutPrefix.slice(0, idx).trim();
    const value = withoutPrefix.slice(idx + 1).trim();
    if (!rawKey) {
      errors.push(`line ${lineNo}: empty key`);
      return true;
    }
    if (!value) {
      warnings.push(`line ${lineNo}: empty value for key "${rawKey}"`);
    }
    assignKeyValue(rawKey, value, lineNo, parsingMode, spec, extras, warnings, errors);
    return true;
  };

  const parseFihoTagsInLine = (line, lineNo, parsingMode, spec, extras, warnings, errors) => {
    const lower = line.toLowerCase();
    let i = 0;
    let sawAny = false;

    while (i < line.length) {
      const idx = lower.indexOf("fi'o", i);
      if (idx < 0) break;
      if (!isWordBoundary(line, idx)) {
        i = idx + 4;
        continue;
      }
      let j = skipWs(line, idx + 4);
      if (!startsWithWordCI(line, j, "me")) {
        errors.push(`line ${lineNo}: expected "me" after "fi'o"`);
        i = idx + 4;
        continue;
      }
      j = skipWs(line, j + 2);

      const keyQuote = parseZoi(line, j, lineNo, errors);
      if (!keyQuote.ok) {
        i = idx + 4;
        continue;
      }
      j = skipWs(line, keyQuote.endIndex);

      const valQuote = parseZoi(line, j, lineNo, errors);
      if (!valQuote.ok) {
        i = idx + 4;
        continue;
      }
      j = valQuote.endIndex;

      const rawKey = keyQuote.body;
      const value = valQuote.body;
      if (!rawKey) {
        errors.push(`line ${lineNo}: empty key in zoi quote after "fi'o me"`);
        i = j;
        continue;
      }
      if (!value) {
        warnings.push(`line ${lineNo}: empty value for key "${rawKey}"`);
      }

      assignKeyValue(rawKey, value, lineNo, parsingMode, spec, extras, warnings, errors);
      sawAny = true;
      i = j;
    }

    return sawAny;
  };

  const parse = (text, parsingMode) => {
    const warnings = [];
    const errors = [];
    const spec = {};
    const extras = {};

    const lines = text.split(/\r?\n/);
    for (let lineNo = 0; lineNo < lines.length; lineNo += 1) {
      const rawLine = lines[lineNo];
      const line = rawLine.trim();
      if (!line) continue;
      if (line.startsWith("#")) continue;

      const lineno1 = lineNo + 1;

      // Preferred: controlled-Lojban key equals value statements ("zoi ... du zoi ...").
      const sawDu = parseDuPairsInLine(line, lineno1, parsingMode, spec, extras, warnings, errors);
      if (sawDu) continue;

      // Supported: controlled-Lojban tags ("fi'o me zoi ... zoi ...").
      const sawFiho = parseFihoTagsInLine(line, lineno1, parsingMode, spec, extras, warnings, errors);
      if (sawFiho) continue;

      // Backward-compatible: "key: value" lines.
      const sawKeyValue = parseKeyValueLine(line, lineno1, parsingMode, spec, extras, warnings, errors);
      if (sawKeyValue) continue;

      // If the line is neither, treat it as a warning in warn mode to avoid silent drops.
      const msg = `line ${lineno1}: unrecognized line format (expected zoi/du, fi'o tags, or "key: value")`;
      if (parsingMode === "strict") errors.push(msg);
      else warnings.push(msg);
    }

    for (const k of CANON_KEYS) {
      if (!Object.prototype.hasOwnProperty.call(spec, k)) continue;
      if (typeof spec[k] !== "string") continue;
      if (spec[k].trim().length === 0) {
        warnings.push(`key "${k}" is present but empty`);
      }
    }

    return { spec, extras, warnings, errors };
  };

  const renderJson = (parsed) => {
    const obj =
      Object.keys(parsed.extras).length === 0
        ? parsed.spec
        : { ...parsed.spec, extras: parsed.extras };
    return JSON.stringify(obj, null, 2);
  };

  const renderMarkdown = (parsed) => {
    const s = parsed.spec;
    const sections = [
      ["Goal", s.goal],
      ["Problem", s.problem],
      ["Domain A", s.domain_a],
      ["Why Intractable", s.why_intractable],
      ["Target Domain B", s.target_domain_b],
      ["Mapping f (A -> B)", s.mapping_f],
      ["Must Preserve", s.preserve],
      ["Solve In B", s.solve_in_b],
      ["Translate Back", s.inverse_mapping],
      ["Validation", s.validation],
    ];

    let out = "# PromptSpec\n\n";
    for (const [title, body] of sections) {
      out += `## ${title}\n\n`;
      out += body ? `${body}\n\n` : "_(missing)_\n\n";
    }

    if (Object.keys(parsed.extras).length > 0) {
      out += "## Extras\n\n";
      for (const [k, v] of Object.entries(parsed.extras)) {
        out += `- ${k}: ${v}\n`;
      }
      out += "\n";
    }
    return out;
  };

  const renderTypeScript = (parsed) => {
    const s = parsed.spec;
    const esc = (x) =>
      String(x || "")
        .replaceAll("\\", "\\\\")
        .replaceAll("`", "\\`")
        .replaceAll("${", "\\${");

    return `export type PromptSpec = {
  goal?: string;
  problem?: string;
  domain_a?: string;
  why_intractable?: string;
  target_domain_b?: string;
  mapping_f?: string;
  preserve?: string;
  solve_in_b?: string;
  inverse_mapping?: string;
  validation?: string;
  extras?: Record<string, string>;
};

export const SPEC: PromptSpec = ${renderJson(parsed)};

export function validateSpec(spec: PromptSpec): string[] {
  const errs: string[] = [];
  const req = ["goal", "problem"] as const;
  for (const k of req) {
    if (!spec[k] || String(spec[k]).trim().length === 0) {
      errs.push(\`missing required field: \${k}\`);
    }
  }
  return errs;
}

// Example usage:
// const errors = validateSpec(SPEC);
// if (errors.length) console.error(errors.join("\\n"));
// else console.log("spec ok");

// Human-readable summary:
export const SUMMARY = \`Goal: ${esc(s.goal)}
Problem: ${esc(s.problem)}
Domain A: ${esc(s.domain_a)}
Target B: ${esc(s.target_domain_b)}\`;
`;
  };

  const renderNotes = (parsed) => {
    const lines = [];
    if (parsed.errors.length > 0) {
      lines.push("errors:");
      for (const e of parsed.errors) lines.push(`- ${e}`);
    }
    if (parsed.warnings.length > 0) {
      if (parsed.errors.length > 0) lines.push("");
      lines.push("warnings:");
      for (const w of parsed.warnings) lines.push(`- ${w}`);
    }
    if (parsed.errors.length === 0 && parsed.warnings.length === 0) {
      lines.push("ok: parsed with no warnings");
    }
    return lines.join("\n");
  };

  const transpile = () => {
    const parsingMode = String(mode.value || "warn");
    const parsed = parse(String(input.value || ""), parsingMode);

    notes.textContent = renderNotes(parsed);

    if (parsed.errors.length > 0) {
      output.value = "";
      return;
    }

    const fmt = String(format.value || "json");
    if (fmt === "md") output.value = renderMarkdown(parsed);
    else if (fmt === "ts") output.value = renderTypeScript(parsed);
    else output.value = renderJson(parsed);
  };

  const setDefaults = () => {
    input.value = DEFAULT_TEXT;
    output.value = "";
    notes.textContent = "";
    format.value = "json";
    mode.value = "warn";
  };

  runBtn.addEventListener("click", transpile);
  resetBtn.addEventListener("click", () => {
    setDefaults();
    transpile();
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
  transpile();
})();
