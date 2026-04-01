/**
 * ShapeLogic: a lightweight propositional + linear arithmetic reasoning engine
 * for the ZenoDEX shape pruning lab.
 *
 * Replaces hardcoded lookup tables with real symbolic verification:
 * SAT checking, counterexample generation, proof traces, and minimal
 * blocking set discovery.
 */
(function () {
  "use strict";

  // ================================================================
  // SECTION 1: AST builders
  // ================================================================

  function bool(name) { return { type: "bool", name: name }; }
  function num(name) { return { type: "num", name: name }; }
  function lit(value) { return { type: "const", value: value }; }

  function cmp(op, left, right) {
    return { type: "cmp", op: op, left: left, right: right };
  }

  function and() {
    var children = [];
    for (var i = 0; i < arguments.length; i++) {
      var arg = arguments[i];
      if (arg.type === "and") {
        for (var j = 0; j < arg.children.length; j++) children.push(arg.children[j]);
      } else {
        children.push(arg);
      }
    }
    return { type: "and", children: children };
  }

  function or() {
    var children = [];
    for (var i = 0; i < arguments.length; i++) {
      var arg = arguments[i];
      if (arg.type === "or") {
        for (var j = 0; j < arg.children.length; j++) children.push(arg.children[j]);
      } else {
        children.push(arg);
      }
    }
    return { type: "or", children: children };
  }

  function not(child) {
    if (child.type === "not") return child.child;
    return { type: "not", child: child };
  }

  function implies(left, right) {
    return or(not(left), right);
  }

  function iff(left, right) {
    return and(implies(left, right), implies(right, left));
  }

  // ================================================================
  // SECTION 2: Formula utilities
  // ================================================================

  var _cmpCounter = 0;

  function collectVars(formula) {
    var bools = {};
    var nums = {};
    function walk(f) {
      if (!f) return;
      switch (f.type) {
        case "bool": bools[f.name] = true; break;
        case "num": nums[f.name] = true; break;
        case "const": break;
        case "cmp": walk(f.left); walk(f.right); break;
        case "and": f.children.forEach(walk); break;
        case "or": f.children.forEach(walk); break;
        case "not": walk(f.child); break;
      }
    }
    walk(formula);
    return { bools: Object.keys(bools), nums: Object.keys(nums) };
  }

  function formulaToString(f) {
    if (!f) return "?";
    switch (f.type) {
      case "bool": return f.name;
      case "num": return f.name;
      case "const": return String(f.value);
      case "cmp":
        return formulaToString(f.left) + " " + f.op + " " + formulaToString(f.right);
      case "and":
        return "(" + f.children.map(formulaToString).join(" AND ") + ")";
      case "or":
        return "(" + f.children.map(formulaToString).join(" OR ") + ")";
      case "not":
        return "NOT(" + formulaToString(f.child) + ")";
    }
    return "?";
  }

  // Normalize formula to NNF (negation normal form)
  function toNNF(f) {
    switch (f.type) {
      case "bool":
      case "cmp":
      case "const":
        return f;
      case "and":
        return { type: "and", children: f.children.map(toNNF) };
      case "or":
        return { type: "or", children: f.children.map(toNNF) };
      case "not":
        return pushNot(f.child);
    }
    return f;
  }

  function pushNot(f) {
    switch (f.type) {
      case "bool":
        return { type: "not", child: f };
      case "cmp":
        return { type: "not", child: f };
      case "const":
        return { type: "not", child: f };
      case "not":
        return toNNF(f.child);
      case "and":
        return { type: "or", children: f.children.map(pushNot) };
      case "or":
        return { type: "and", children: f.children.map(pushNot) };
    }
    return { type: "not", child: f };
  }

  // Convert to CNF (array of clauses, each clause is array of literals)
  // Literal: { positive: bool, atom: formula }
  function toCNF(formula) {
    var nnf = toNNF(formula);
    var cnfTree = distribute(nnf);
    var clauses = [];
    collectClauses(cnfTree, clauses);
    return clauses;
  }

  // Distribute OR over AND to produce a proper CNF tree:
  //   or(A, and(B, C)) => and(or(A, B), or(A, C))
  function distribute(f) {
    if (f.type === "and") {
      var ch = [];
      for (var i = 0; i < f.children.length; i++) {
        var d = distribute(f.children[i]);
        if (d.type === "and") {
          for (var j = 0; j < d.children.length; j++) ch.push(d.children[j]);
        } else { ch.push(d); }
      }
      return ch.length === 1 ? ch[0] : { type: "and", children: ch };
    }
    if (f.type === "or") {
      var dc = [];
      for (var i2 = 0; i2 < f.children.length; i2++) {
        dc.push(distribute(f.children[i2]));
      }
      var result = dc[0];
      for (var k = 1; k < dc.length; k++) {
        result = distributeOr(result, dc[k]);
      }
      return result;
    }
    return f;
  }

  function distributeOr(a, b) {
    if (a.type === "and") {
      var ch = [];
      for (var i = 0; i < a.children.length; i++) {
        var d = distributeOr(a.children[i], b);
        if (d.type === "and") {
          for (var j = 0; j < d.children.length; j++) ch.push(d.children[j]);
        } else { ch.push(d); }
      }
      return { type: "and", children: ch };
    }
    if (b.type === "and") {
      var ch2 = [];
      for (var i2 = 0; i2 < b.children.length; i2++) {
        var d2 = distributeOr(a, b.children[i2]);
        if (d2.type === "and") {
          for (var j2 = 0; j2 < d2.children.length; j2++) ch2.push(d2.children[j2]);
        } else { ch2.push(d2); }
      }
      return { type: "and", children: ch2 };
    }
    var ac = a.type === "or" ? a.children : [a];
    var bc = b.type === "or" ? b.children : [b];
    return { type: "or", children: ac.concat(bc) };
  }

  function collectClauses(f, clauses) {
    if (f.type === "and") {
      f.children.forEach(function (c) { collectClauses(c, clauses); });
    } else {
      var lits = [];
      collectLiterals(f, lits);
      clauses.push(lits);
    }
  }

  function collectLiterals(f, lits) {
    if (f.type === "or") {
      f.children.forEach(function (c) { collectLiterals(c, lits); });
    } else if (f.type === "not") {
      lits.push({ positive: false, atom: f.child });
    } else {
      lits.push({ positive: true, atom: f });
    }
  }

  // ================================================================
  // SECTION 3: Evaluator
  // ================================================================

  function evaluate(formula, env) {
    switch (formula.type) {
      case "bool":
        if (env.booleans && formula.name in env.booleans) return env.booleans[formula.name];
        return null;
      case "num":
        if (env.numerics && formula.name in env.numerics) return env.numerics[formula.name];
        return null;
      case "const":
        return formula.value;
      case "cmp":
        var l = evaluate(formula.left, env);
        var r = evaluate(formula.right, env);
        if (l === null || r === null) return null;
        switch (formula.op) {
          case ">=": return l >= r;
          case "<=": return l <= r;
          case ">": return l > r;
          case "<": return l < r;
          case "=": return l === r;
          case "!=": return l !== r;
        }
        return null;
      case "and":
        var result = true;
        for (var i = 0; i < formula.children.length; i++) {
          var v = evaluate(formula.children[i], env);
          if (v === false) return false;
          if (v === null) result = null;
        }
        return result;
      case "or":
        var result2 = false;
        for (var j = 0; j < formula.children.length; j++) {
          var v2 = evaluate(formula.children[j], env);
          if (v2 === true) return true;
          if (v2 === null) result2 = null;
        }
        return result2;
      case "not":
        var inner = evaluate(formula.child, env);
        if (inner === null) return null;
        return !inner;
    }
    return null;
  }

  // ================================================================
  // SECTION 4: SAT solver (DPLL with arithmetic intervals)
  // ================================================================

  function atomKey(lit) {
    var a = lit.atom;
    if (a.type === "bool") return "b:" + a.name;
    if (a.type === "cmp") return "c:" + formulaToString(a);
    return "?" + formulaToString(a);
  }

  function solve(formula, seedEnv) {
    var cnf = toCNF(formula);
    var assignment = {};
    var trace = [];
    var numBounds = {};
    var vars = collectVars(formula);

    // Seed environment
    if (seedEnv) {
      if (seedEnv.booleans) {
        for (var bk in seedEnv.booleans) {
          assignment["b:" + bk] = seedEnv.booleans[bk];
        }
      }
      if (seedEnv.numerics) {
        for (var nk in seedEnv.numerics) {
          var v = seedEnv.numerics[nk];
          numBounds[nk] = { lo: v, hi: v };
        }
      }
    }

    // Initialize bounds for unseeded numerics
    vars.nums.forEach(function (n) {
      if (!numBounds[n]) numBounds[n] = { lo: 0, hi: 1000 };
    });

    function evalLit(lit) {
      var key = atomKey(lit);
      if (key in assignment) {
        return lit.positive ? assignment[key] : !assignment[key];
      }
      // Try arithmetic evaluation
      if (lit.atom.type === "cmp") {
        var env = makeEnv();
        var val = evaluate(lit.atom, env);
        if (val !== null) return lit.positive ? val : !val;
      }
      return null;
    }

    function makeEnv() {
      var booleans = {};
      var numerics = {};
      for (var k in assignment) {
        if (k.startsWith("b:")) booleans[k.substring(2)] = assignment[k];
      }
      for (var n in numBounds) {
        var b = numBounds[n];
        if (b.lo === b.hi) numerics[n] = b.lo;
      }
      return { booleans: booleans, numerics: numerics };
    }

    function evalClause(clause) {
      var hasNull = false;
      for (var i = 0; i < clause.length; i++) {
        var v = evalLit(clause[i]);
        if (v === true) return true;
        if (v === null) hasNull = true;
      }
      return hasNull ? null : false;
    }

    function propagateArith(lit, val) {
      var a = lit.atom;
      if (a.type !== "cmp") return true;
      var actual = val;
      var l = a.left, r = a.right;
      var lName = l.type === "num" ? l.name : null;
      var rName = r.type === "num" ? r.name : null;
      var lVal = l.type === "const" ? l.value : null;
      var rVal = r.type === "const" ? r.value : null;

      if (lName && numBounds[lName]) {
        if (rVal !== null || (rName && numBounds[rName] && numBounds[rName].lo === numBounds[rName].hi)) {
          var rv = rVal !== null ? rVal : numBounds[rName].lo;
          var b = numBounds[lName];
          if (actual) {
            switch (a.op) {
              case ">=": b.lo = Math.max(b.lo, rv); break;
              case ">": b.lo = Math.max(b.lo, rv + 1); break;
              case "<=": b.hi = Math.min(b.hi, rv); break;
              case "<": b.hi = Math.min(b.hi, rv - 1); break;
              case "=": b.lo = Math.max(b.lo, rv); b.hi = Math.min(b.hi, rv); break;
              case "!=": if (b.lo === rv && b.hi === rv) return false; break;
            }
          } else {
            switch (a.op) {
              case ">=": b.hi = Math.min(b.hi, rv - 1); break;
              case ">": b.hi = Math.min(b.hi, rv); break;
              case "<=": b.lo = Math.max(b.lo, rv + 1); break;
              case "<": b.lo = Math.max(b.lo, rv); break;
              case "=":
                if (b.lo === rv && b.hi === rv) return false;
                break;
              case "!=": b.lo = Math.max(b.lo, rv); b.hi = Math.min(b.hi, rv); break;
            }
          }
          if (b.lo > b.hi) return false;
        }
      }
      return true;
    }

    function unitPropagate() {
      var changed = true;
      while (changed) {
        changed = false;
        for (var ci = 0; ci < cnf.length; ci++) {
          var clause = cnf[ci];
          var cv = evalClause(clause);
          if (cv === true) continue;
          if (cv === false) return { conflict: true, clauseIndex: ci };

          // Find unresolved literals
          var unresolved = [];
          for (var li = 0; li < clause.length; li++) {
            var lv = evalLit(clause[li]);
            if (lv === null) unresolved.push(clause[li]);
          }
          if (unresolved.length === 1) {
            var unit = unresolved[0];
            var key = atomKey(unit);
            assignment[key] = unit.positive;
            trace.push({
              kind: "unit", clauseIndex: ci,
              literal: formulaToString(unit.atom),
              value: unit.positive
            });
            if (!propagateArith(unit, unit.positive)) {
              return { conflict: true, clauseIndex: ci };
            }
            changed = true;
          } else if (unresolved.length === 0) {
            return { conflict: true, clauseIndex: ci };
          }
        }
      }
      return { conflict: false };
    }

    function dpll() {
      // Save state
      var savedAssignment = Object.assign({}, assignment);
      var savedBounds = {};
      for (var bn in numBounds) savedBounds[bn] = { lo: numBounds[bn].lo, hi: numBounds[bn].hi };
      var savedTraceLen = trace.length;

      var up = unitPropagate();
      if (up.conflict) {
        assignment = savedAssignment;
        for (var rn in savedBounds) numBounds[rn] = savedBounds[rn];
        trace.length = savedTraceLen;
        return false;
      }

      // Check if all clauses satisfied
      var allSat = true;
      for (var ci = 0; ci < cnf.length; ci++) {
        if (evalClause(cnf[ci]) !== true) { allSat = false; break; }
      }
      if (allSat) return true;

      // Find unassigned variable to branch on
      var branchKey = null;
      for (var ci2 = 0; ci2 < cnf.length; ci2++) {
        var clause = cnf[ci2];
        if (evalClause(clause) === true) continue;
        for (var li = 0; li < clause.length; li++) {
          var key = atomKey(clause[li]);
          if (!(key in assignment)) {
            branchKey = clause[li];
            break;
          }
        }
        if (branchKey) break;
      }

      if (!branchKey) return false;

      var bKey = atomKey(branchKey);

      // Try positive
      var s1 = Object.assign({}, assignment);
      var b1 = {};
      for (var n1 in numBounds) b1[n1] = { lo: numBounds[n1].lo, hi: numBounds[n1].hi };
      var t1 = trace.length;

      assignment[bKey] = branchKey.positive;
      trace.push({
        kind: "decide",
        literal: formulaToString(branchKey.atom),
        value: branchKey.positive
      });
      if (propagateArith(branchKey, branchKey.positive) && dpll()) return true;

      // Backtrack, try negative
      assignment = s1;
      for (var r1 in b1) numBounds[r1] = b1[r1];
      trace.length = t1;

      assignment[bKey] = !branchKey.positive;
      trace.push({
        kind: "decide",
        literal: formulaToString(branchKey.atom),
        value: !branchKey.positive
      });
      if (propagateArith(branchKey, !branchKey.positive) && dpll()) return true;

      // Both failed
      assignment = savedAssignment;
      for (var r2 in savedBounds) numBounds[r2] = savedBounds[r2];
      trace.length = savedTraceLen;
      return false;
    }

    var sat = dpll();
    return {
      satisfiable: sat,
      witness: sat ? makeEnv() : null,
      trace: trace.slice()
    };
  }

  // ================================================================
  // SECTION 5: High-level reasoning API
  // ================================================================

  function checkBlocked(clauseFormulas, disasterFormula, facts) {
    // If the conjunction of all clause blocking rules and the disaster
    // is UNSAT, then the disaster is blocked.
    var parts = clauseFormulas.slice();
    parts.push(disasterFormula);
    var combined = parts.length === 1 ? parts[0] : and.apply(null, parts);

    var result = solve(combined, facts || null);

    if (!result.satisfiable) {
      return {
        blocked: true,
        witness: null,
        proofTrace: result.trace
      };
    }
    return {
      blocked: false,
      witness: result.witness,
      proofTrace: result.trace
    };
  }

  function checkImplies(premises, conclusion) {
    // premises => conclusion iff premises AND NOT(conclusion) is UNSAT
    var parts = premises.slice();
    parts.push(not(conclusion));
    var combined = and.apply(null, parts);
    var result = solve(combined, null);
    return {
      holds: !result.satisfiable,
      counterexample: result.satisfiable ? result.witness : null
    };
  }

  function minimalBlockingSet(clauseIds, clauseFormulas, disasterFormula, facts) {
    // Find the smallest subset of clauses that still blocks the disaster.
    var essential = [];
    var remaining = clauseIds.slice();

    for (var i = remaining.length - 1; i >= 0; i--) {
      // Try removing clause i
      var candidate = remaining.slice();
      candidate.splice(i, 1);
      var candidateFormulas = candidate.map(function (id) { return clauseFormulas[id]; }).filter(Boolean);

      var result = checkBlocked(candidateFormulas, disasterFormula, facts);
      if (result.blocked) {
        remaining = candidate;
      }
    }
    return remaining;
  }

  // ================================================================
  // SECTION 6: Domain model - ZenoDEX clause and disaster encodings
  // ================================================================

  var clauseBlocks = {};
  var disasters = {};
  var scenarioFacts = {};
  var probeFormulas = {};

  // -- Clause blocking formulas --
  // Each formula expresses what the clause enforces.
  // When active, the clause formula is conjoined with the disaster,
  // making the conjunction UNSAT if the clause blocks the disaster.

  // BoundaryValidity: well-formed params, reserves, drift, and K_after >= K_before
  clauseBlocks.BoundaryValidity = and(
    bool("ParamsOK"),
    bool("ReservesOK"),
    bool("SafeOK"),
    bool("DriftOK"),
    cmp(">=", num("K_after"), num("K_before"))
  );

  // TemporalAdmissibility: accepted => requestedNonce > lastUsedNonce
  clauseBlocks.TemporalAdmissibility = implies(
    bool("accepted"),
    cmp(">", num("requestedNonce"), num("lastUsedNonce"))
  );

  // CanonicalWinnerSelection: a deterministic winner key exists
  clauseBlocks.CanonicalWinnerSelection = implies(
    bool("candidateSetNonEmpty"),
    bool("deterministicWinnerExists")
  );

  // ReserveMonotonicity: K_after >= K_before
  clauseBlocks.ReserveMonotonicity = cmp(">=", num("K_after"), num("K_before"));

  // SettlementCompositionality: compositional delta law holds
  clauseBlocks.SettlementCompositionality = bool("deltaCompositional");

  // DeterministicRouting: same inputs => same output
  clauseBlocks.DeterministicRouting = bool("deterministicOutput");

  // StablecoinSolvency: risky ops require oracle alignment and no recovery mode
  clauseBlocks.StablecoinSolvency = implies(
    bool("risky"),
    and(
      bool("oracle_seen"),
      cmp(">", num("price"), lit(0)),
      cmp(">", num("price_pending"), lit(0)),
      bool("OracleFresh"),
      not(bool("RecoveryMode"))
    )
  );

  // CBCValidity: filled => output >= min_out (by construction)
  clauseBlocks.CBCValidity = implies(
    bool("filled"),
    cmp(">=", num("output"), num("min_out"))
  );

  // UniqueCanonicalWinnerEverywhere: at most one canonical winner
  clauseBlocks.UniqueCanonicalWinnerEverywhere = implies(
    bool("candidateSetNonEmpty"),
    and(
      bool("uniqueWinnerExists"),
      not(and(bool("winner_a"), bool("winner_b"),
        cmp("=", num("score_a"), num("score_b"))))
    )
  );

  // ExactFeeAwareAccounting: exact residue tracking, not just monotonicity
  clauseBlocks.ExactFeeAwareAccounting = and(
    cmp(">=", num("K_after"), num("K_before")),
    implies(
      bool("exactConservationClaimed"),
      not(bool("dustDiscarded"))
    )
  );

  // ValueAwareSettlementSafety: settlement needs value lane
  clauseBlocks.ValueAwareSettlementSafety = implies(
    bool("settlementAccepted"),
    and(
      bool("strongCertificateOK"),
      bool("featureExtensionOK"),
      bool("moduleBundleOK"),
      bool("fullPriceRailsOK"),
      bool("valueLaneOK")
    )
  );

  // ProofCarryingOptimizerCertificates: winner => proof + binding
  clauseBlocks.ProofCarryingOptimizerCertificates = implies(
    bool("executableWinner"),
    and(bool("ProofOK"), bool("BindingOK"))
  );

  // AntiFragmentationByTheorem: same-pool same-direction fragments are dominated
  clauseBlocks.AntiFragmentationByTheorem = implies(
    bool("samePoolSameDirection"),
    not(bool("fragmentedRouteKept"))
  );

  // NonCommutativityQuarantine: opposite direction => do not assume commutes
  clauseBlocks.NonCommutativityQuarantine = implies(
    bool("OppositeDirection"),
    not(bool("AssumeCommutes"))
  );

  // OracleDivergenceSafety: risky => price_pending = price
  clauseBlocks.OracleDivergenceSafety = implies(
    bool("risky"),
    cmp("=", num("price_pending"), num("price"))
  );

  // LiquidationSpiralContainment: liquidation is bounded
  clauseBlocks.LiquidationSpiralContainment = implies(
    and(not(bool("MCR_OK")), cmp(">", num("debt"), lit(0))),
    and(
      bool("oracle_seen"),
      cmp(">", num("price_pending"), lit(0)),
      cmp("<=", num("debt"), num("sp_debt"))
    )
  );

  // PhaseProgressGuarantee: closed non-complete phase must have enabled moves or be rejected
  clauseBlocks.PhaseProgressGuarantee = implies(
    and(bool("phaseClosed"), not(bool("Complete"))),
    or(not(bool("enabledEmpty")), bool("rejected"))
  );

  // CrossLayerReplayParity: runtime = certificate = proof
  clauseBlocks.CrossLayerReplayParity = and(
    implies(
      bool("settlementAccepted"),
      cmp("=", num("obs_runtime"), num("obs_certificate"))
    ),
    implies(
      and(
        bool("settlementAccepted"),
        cmp("!=", num("obs_runtime"), num("obs_certificate"))
      ),
      bool("rejected")
    )
  );

  // -- Disaster formulas --

  disasters["replay"] = and(
    bool("accepted"),
    cmp("<=", num("requestedNonce"), num("lastUsedNonce"))
  );

  disasters["reserve-drain"] = and(
    cmp("=", num("amount_out"), num("reserve_out")),
    not(bool("ParamsOK"))
  );

  disasters["invalid-fill"] = and(
    bool("filled"),
    cmp("<", num("output"), num("min_out"))
  );

  disasters["ambiguous-winner"] = and(
    bool("candidateSetNonEmpty"),
    bool("winner_a"),
    bool("winner_b"),
    cmp("=", num("score_a"), num("score_b"))
  );

  disasters["partial-exact-out"] = and(
    bool("executableWinner"),
    cmp("<", num("totalLegOut"), num("requestedQ")),
    not(bool("ProofOK"))
  );

  disasters["fee-leak"] = and(
    bool("exactConservationClaimed"),
    bool("dustDiscarded")
  );

  disasters["fragmentation"] = and(
    bool("samePoolSameDirection"),
    bool("fragmentedRouteKept")
  );

  disasters["noncommute"] = and(
    bool("OppositeDirection"),
    bool("AssumeCommutes")
  );

  disasters["oracle-mismatch"] = and(
    bool("risky"),
    cmp("!=", num("price_pending"), num("price"))
  );

  disasters["value-blind"] = and(
    bool("settlementAccepted"),
    not(bool("valueLaneOK"))
  );

  disasters["liquidation"] = and(
    not(bool("MCR_OK")),
    cmp(">", num("debt"), lit(0)),
    bool("uncontrolledTransition"),
    not(cmp("<=", num("debt"), num("sp_debt")))
  );

  disasters["deadlock"] = and(
    bool("phaseClosed"),
    not(bool("Complete")),
    bool("enabledEmpty"),
    not(bool("rejected"))
  );

  // -- Scenario facts (concrete values for witness display) --

  scenarioFacts["replay"] = {
    numerics: { requestedNonce: 41, lastUsedNonce: 41 },
    booleans: { accepted: true }
  };

  scenarioFacts["reserve-drain"] = {
    numerics: { amount_out: 500, reserve_out: 500, K_after: 0, K_before: 250000 },
    booleans: { ParamsOK: false }
  };

  scenarioFacts["invalid-fill"] = {
    numerics: { output: 93, min_out: 100 },
    booleans: { filled: true }
  };

  scenarioFacts["ambiguous-winner"] = {
    numerics: { score_a: 42, score_b: 42 },
    booleans: { candidateSetNonEmpty: true, winner_a: true, winner_b: true }
  };

  scenarioFacts["partial-exact-out"] = {
    numerics: { totalLegOut: 80, requestedQ: 100 },
    booleans: { executableWinner: true, ProofOK: false }
  };

  scenarioFacts["fee-leak"] = {
    booleans: { exactConservationClaimed: true, dustDiscarded: true }
  };

  scenarioFacts["fragmentation"] = {
    booleans: { samePoolSameDirection: true, fragmentedRouteKept: true }
  };

  scenarioFacts["noncommute"] = {
    booleans: { OppositeDirection: true, AssumeCommutes: true }
  };

  scenarioFacts["oracle-mismatch"] = {
    numerics: { price_pending: 105, price: 100 },
    booleans: { risky: true }
  };

  scenarioFacts["value-blind"] = {
    booleans: { settlementAccepted: true, valueLaneOK: false }
  };

  scenarioFacts["liquidation"] = {
    numerics: { debt: 500, sp_debt: 200 },
    booleans: { MCR_OK: false, uncontrolledTransition: true }
  };

  scenarioFacts["deadlock"] = {
    booleans: { phaseClosed: true, Complete: false, enabledEmpty: true, rejected: false }
  };

  // -- Probe formulas --

  probeFormulas["proof-timeout"] = and(
    bool("executableWinner"),
    not(bool("ProofOK"))
  );

  probeFormulas["truncated-tcp"] = and(
    bool("partialPacket"),
    bool("settlementAccepted")
  );

  probeFormulas["oversized-body"] = and(
    bool("oversizedBody"),
    not(bool("ParamsOK"))
  );

  probeFormulas["rapid-pending-price"] = and(
    bool("risky"),
    cmp("!=", num("price_pending"), num("price"))
  );

  probeFormulas["malformed-certificate"] = and(
    bool("executableWinner"),
    not(bool("ProofOK")),
    not(bool("rejected"))
  );

  probeFormulas["opposite-direction-rewrite"] = and(
    bool("OppositeDirection"),
    bool("rewriteApplied"),
    bool("AssumeCommutes")
  );

  // ================================================================
  // SECTION 7: Self-test
  // ================================================================

  function selfTest() {
    var pass = 0;
    var fail = 0;
    var results = [];

    function assert(label, condition) {
      if (condition) { pass++; results.push("PASS: " + label); }
      else { fail++; results.push("FAIL: " + label); }
    }

    // Test 1: each disaster is satisfiable on its own
    for (var did in disasters) {
      var r = solve(disasters[did], scenarioFacts[did] || null);
      assert("disaster '" + did + "' is SAT alone", r.satisfiable);
    }

    // Test 2: each disaster is blocked under full Shape++
    var allClauseIds = Object.keys(clauseBlocks);
    var allFormulas = allClauseIds.map(function (id) { return clauseBlocks[id]; });

    for (var did2 in disasters) {
      var r2 = checkBlocked(allFormulas, disasters[did2], scenarioFacts[did2] || null);
      assert("disaster '" + did2 + "' blocked under full Shape++", r2.blocked);
    }

    // Test 3: under minimal shell (BoundaryValidity only), most disasters survive
    var minFormulas = [clauseBlocks.BoundaryValidity];
    var surviveCount = 0;
    for (var did3 in disasters) {
      var r3 = checkBlocked(minFormulas, disasters[did3], scenarioFacts[did3] || null);
      if (!r3.blocked) surviveCount++;
    }
    assert("minimal shell leaves most disasters reachable", surviveCount >= 6);

    // Test 4: basic logic checks
    var r4 = solve(and(bool("x"), not(bool("x"))), null);
    assert("x AND NOT(x) is UNSAT", !r4.satisfiable);

    var r5 = solve(and(bool("x"), bool("y")), null);
    assert("x AND y is SAT", r5.satisfiable);

    var r6 = solve(and(cmp(">=", num("a"), lit(10)), cmp("<", num("a"), lit(5))), null);
    assert("a >= 10 AND a < 5 is UNSAT", !r6.satisfiable);

    var r7 = solve(and(cmp(">=", num("a"), lit(5)), cmp("<=", num("a"), lit(10))), null);
    assert("a >= 5 AND a <= 10 is SAT", r7.satisfiable);

    console.log("ShapeLogic self-test: " + pass + " passed, " + fail + " failed");
    results.forEach(function (r) { console.log("  " + r); });
    return { pass: pass, fail: fail, results: results };
  }

  // ================================================================
  // Public API
  // ================================================================

  window.ShapeLogic = {
    // Builders
    bool: bool,
    num: num,
    lit: lit,
    cmp: cmp,
    and: and,
    or: or,
    not: not,
    implies: implies,
    iff: iff,

    // Utilities
    collectVars: collectVars,
    formulaToString: formulaToString,
    evaluate: evaluate,
    toCNF: toCNF,

    // Reasoning
    solve: solve,
    checkBlocked: checkBlocked,
    checkImplies: checkImplies,
    minimalBlockingSet: minimalBlockingSet,

    // Domain
    domain: {
      clauseBlocks: clauseBlocks,
      disasters: disasters,
      scenarioFacts: scenarioFacts,
      probeFormulas: probeFormulas
    },

    // Testing
    selfTest: selfTest
  };
})();
