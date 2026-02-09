(() => {
  const input = document.getElementById("po-input");
  const output = document.getElementById("po-output");
  const runBtn = document.getElementById("po-run");
  const resetBtn = document.getElementById("po-reset");
  const copyBtn = document.getElementById("po-copy");
  const notes = document.getElementById("po-notes");

  if (!input || !output || !runBtn || !resetBtn || !copyBtn || !notes) {
    return;
  }

  const DEFAULT_TEXT = `Write a short guide that explains what an invariant is, then give two examples.
Constraints: keep it under 250 words. Avoid jargon.
Checks: include a one-sentence definition and a concrete example in code-like pseudocode.
Output format: Markdown with headings.`;

  const normalize = (s) => String(s || "").replaceAll(/\r/g, "").trim();

  const splitSentences = (text) => {
    const s = normalize(text).replaceAll(/\s+/g, " ");
    if (!s) return [];
    return s
      .split(/(?<=[.!?])\s+/g)
      .map((x) => x.trim())
      .filter(Boolean);
  };

  const detect = (text) => {
    const t = normalize(text).toLowerCase();
    const hasConstraints =
      /\b(must|should|avoid|limit|deterministic|no\s+external|do\s+not|don't)\b/.test(
        t,
      ) || /\bconstraints?\b/.test(t);
    const hasChecks =
      /\b(test|tests|verify|verification|acceptance|criteria|check|checks|pass\/fail|examples?)\b/.test(
        t,
      );
    const hasOutputFormat =
      /\b(json|yaml|toml|markdown|md|csv|table|typescript|javascript|python|rust|code|schema)\b/.test(
        t,
      ) || /\boutput\s+format\b/.test(t);

    const mentionsSecrets =
      /\b(api\s*key|password|secret|token|bearer)\b/.test(t);

    return { hasConstraints, hasChecks, hasOutputFormat, mentionsSecrets };
  };

  const lint = (text) => {
    const flags = detect(text);
    const warnings = [];

    if (!normalize(text)) {
      warnings.push("empty input, nothing to optimize");
      return { flags, warnings };
    }

    if (!flags.hasConstraints) warnings.push("missing constraints, add boundaries and prohibitions");
    if (!flags.hasChecks) warnings.push("missing checks, add pass and fail criteria or test cases");
    if (!flags.hasOutputFormat) warnings.push("missing output format, specify structure and file types");
    if (flags.mentionsSecrets) warnings.push("safety: avoid placing secrets in prompts or examples");

    return { flags, warnings };
  };

  const chooseGoal = (text) => {
    const sentences = splitSentences(text);
    if (sentences.length === 0) return "(TODO) state the goal in one sentence";
    const first = sentences[0];
    if (first.length <= 140) return first;
    return `${first.slice(0, 137)}...`;
  };

  const defaultOutputFormat = (flags) => {
    if (flags.hasOutputFormat) return "(keep the output format requested in the prompt)";
    return "Markdown with headings: Summary, Assumptions, Solution, Checks";
  };

  const rewrite = (text) => {
    const { flags } = lint(text);
    const goal = chooseGoal(text);
    const of = defaultOutputFormat(flags);

    return (
      "Goal:\n" +
      `- ${goal}\n\n` +
      "Problem statement:\n" +
      `${normalize(text)}\n\n` +
      "Constraints:\n" +
      "- (TODO) list non-negotiable constraints (time, dependencies, scope)\n" +
      "- (TODO) list forbidden outputs or behaviors\n\n" +
      "Checks (pass/fail):\n" +
      "- (TODO) define acceptance criteria, include at least 2 positive test cases\n" +
      "- (TODO) include at least 1 negative test case or failure mode\n\n" +
      "Output format:\n" +
      `- ${of}\n\n` +
      "Assumption hygiene:\n" +
      "- If a required detail is missing, state assumptions explicitly, and mark them as assumptions\n"
    );
  };

  const renderNotes = (warnings, flags) => {
    const lines = [];
    lines.push("lint:");
    if (warnings.length === 0) lines.push("- ok: no obvious missing fields detected");
    else warnings.forEach((w) => lines.push(`- ${w}`));
    lines.push("");
    lines.push("detected:");
    lines.push(`- constraints: ${flags.hasConstraints ? "present" : "missing"}`);
    lines.push(`- checks: ${flags.hasChecks ? "present" : "missing"}`);
    lines.push(`- output format: ${flags.hasOutputFormat ? "present" : "missing"}`);
    return lines.join("\n");
  };

  const run = () => {
    const text = input.value || "";
    const { flags, warnings } = lint(text);
    output.value = rewrite(text);
    notes.textContent = renderNotes(warnings, flags);
  };

  const setDefaults = () => {
    input.value = DEFAULT_TEXT;
    output.value = "";
    notes.textContent = "";
  };

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
  run();
})();

