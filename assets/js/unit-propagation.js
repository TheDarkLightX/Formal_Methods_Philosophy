/**
 * Deterministic unit propagation demo.
 *
 * This is an educational Boolean Constraint Propagation (BCP) kernel.
 * It performs only forced assignments (unit resolution) and conflict detection.
 */

(() => {
  class UnitPropagator {
    constructor() {
      this.clauses = [];
      this.assignments = new Map(); // atom -> boolean
      this.conflict = false;
      this.log = [];
    }

    parse(input) {
      this.clauses = [];
      this.assignments.clear();
      this.conflict = false;
      this.log = [];

      const lines = input.split("\n");
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith("#")) continue;

        const parts = trimmed.split("|");
        const literals = parts
          .map((p) => p.trim())
          .filter((s) => s.length > 0)
          .map((s) => {
            const isNegated = s.startsWith("!");
            const atom = isNegated ? s.substring(1) : s;
            return { atom, isNegated, original: s };
          });

        if (literals.length === 0) continue;
        this.clauses.push({ literals, original: trimmed });
      }

      this.log.push(`Parsed ${this.clauses.length} clauses.`);
    }

    evalLiteral(lit) {
      if (!this.assignments.has(lit.atom)) return null;
      const val = this.assignments.get(lit.atom);
      return lit.isNegated ? !val : val;
    }

    step() {
      if (this.conflict) return false;

      for (const clauseObj of this.clauses) {
        let anyTrue = false;
        let unassignedCount = 0;
        let lastUnassigned = null;

        for (const lit of clauseObj.literals) {
          const val = this.evalLiteral(lit);
          if (val === true) {
            anyTrue = true;
            break;
          }
          if (val === null) {
            unassignedCount += 1;
            lastUnassigned = lit;
          }
        }

        if (anyTrue) continue;

        if (unassignedCount === 0) {
          this.conflict = true;
          this.log.push(`CONFLICT: Clause [ ${clauseObj.original} ] is all FALSE.`);
          return true;
        }

        if (unassignedCount === 1) {
          const atom = lastUnassigned.atom;
          const necessaryValue = !lastUnassigned.isNegated;

          if (this.assignments.has(atom)) {
            if (this.assignments.get(atom) !== necessaryValue) {
              this.conflict = true;
              this.log.push(
                `CONFLICT: Atom '${atom}' forced to ${necessaryValue} but already ${!necessaryValue}.`,
              );
              return true;
            }
          } else {
            this.assignments.set(atom, necessaryValue);
            this.log.push(
              `PROPAGATE: Clause [ ${clauseObj.original} ] forces ${lastUnassigned.original} (set ${atom} = ${necessaryValue})`,
            );
            return true;
          }
        }
      }

      return false;
    }

    runAll() {
      let limit = 1000;
      while (this.step() && limit-- > 0) {}
      if (limit <= 0) this.log.push("Run limit reached (cycle?).");
      if (!this.conflict && limit > 0) this.log.push("Stable. No further propagations.");
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    const inputEl = document.getElementById("up-input");
    const runBtn = document.getElementById("up-run");
    const stepBtn = document.getElementById("up-step");
    const resetBtn = document.getElementById("up-reset");
    const logEl = document.getElementById("up-log");
    const stateEl = document.getElementById("up-state");

    if (!inputEl || !runBtn || !stepBtn || !resetBtn || !logEl || !stateEl) return;

    const defaultInput = inputEl.value;
    const engine = new UnitPropagator();

    const render = () => {
      logEl.textContent = engine.log.join("\n");
      logEl.scrollTop = logEl.scrollHeight;

      const status = engine.conflict
        ? `<span style="color:#d32f2f; font-weight:bold">STATUS: CONFLICT</span><br/>`
        : `<span style="color:#388e3c; font-weight:bold">STATUS: OK</span><br/>`;

      const assignments =
        engine.assignments.size === 0
          ? `<span style="color:#666; font-style:italic">No assignments.</span>`
          : Array.from(engine.assignments.entries())
              .map(([atom, val]) => `<span class="fp-badge">${atom} = ${val}</span>`)
              .join(" ");

      stateEl.innerHTML = status + assignments;
    };

    const init = () => {
      engine.parse(inputEl.value);
      render();
    };

    runBtn.addEventListener("click", () => {
      init();
      engine.runAll();
      render();
    });

    stepBtn.addEventListener("click", () => {
      if (engine.log.length === 0) {
        engine.parse(inputEl.value);
      }
      const changed = engine.step();
      if (!changed && !engine.conflict) engine.log.push("Step: No unit clauses found.");
      render();
    });

    resetBtn.addEventListener("click", () => {
      inputEl.value = defaultInput;
      init();
    });

    init();
  });
})();
