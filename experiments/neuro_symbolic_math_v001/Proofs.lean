import Std

/-!
# Neuro-symbolic math v001

This packet checks two scoped kernels:

1. qNS finite powerset filtering laws.
2. EML-tree identity laws over an explicit abstract EML semantics.

The EML section does not claim real-analysis semantics. The needed log/exp
laws are visible hypotheses of the theorem surface.
-/

namespace NeuroSymbolicMathV001

namespace QNS

abbrev Carrier (Atom : Type) := Atom -> Bool

def bottom {Atom : Type} : Carrier Atom := fun _ => false
def meet {Atom : Type} (a b : Carrier Atom) : Carrier Atom := fun x => a x && b x
def join {Atom : Type} (a b : Carrier Atom) : Carrier Atom := fun x => a x || b x
def prime {Atom : Type} (a : Carrier Atom) : Carrier Atom := fun x => !a x

def proposed {Atom : Type} (u n : Carrier Atom) : Carrier Atom :=
  meet u n

def eligible {Atom : Type}
    (u n allowed hardReject : Carrier Atom) : Carrier Atom :=
  meet (meet (meet u n) allowed) (prime hardReject)

def autoAccept {Atom : Type}
    (u n allowed review hardReject : Carrier Atom) : Carrier Atom :=
  meet (eligible u n allowed hardReject) (prime review)

def humanReview {Atom : Type}
    (u n allowed review hardReject : Carrier Atom) : Carrier Atom :=
  meet (eligible u n allowed hardReject) review

def symbolicReject {Atom : Type}
    (u n allowed hardReject : Carrier Atom) : Carrier Atom :=
  meet (proposed u n) (join (prime allowed) hardReject)

def partition {Atom : Type}
    (u n allowed review hardReject : Carrier Atom) : Carrier Atom :=
  join
    (join
      (autoAccept u n allowed review hardReject)
      (humanReview u n allowed review hardReject))
    (symbolicReject u n allowed hardReject)

def survivors {Atom : Type}
    (proposed allowed hardReject : Carrier Atom) : Carrier Atom :=
  meet (meet proposed allowed) (prime hardReject)

def hardRejectLeak {Atom : Type}
    (u n allowed review hardReject : Carrier Atom) : Carrier Atom :=
  meet (autoAccept u n allowed review hardReject) hardReject

theorem auto_accept_no_hard_reject {Atom : Type}
    (u n allowed review hardReject : Carrier Atom) :
    hardRejectLeak u n allowed review hardReject = bottom := by
  funext x
  cases hu : u x <;> cases hn : n x <;> cases ha : allowed x <;>
    cases hr : review x <;> cases hh : hardReject x <;>
    simp [hardRejectLeak, autoAccept, eligible, meet, prime, bottom, hu, hn, ha, hr, hh]

theorem auto_and_review_disjoint {Atom : Type}
    (u n allowed review hardReject : Carrier Atom) :
    meet
      (autoAccept u n allowed review hardReject)
      (humanReview u n allowed review hardReject) = bottom := by
  funext x
  cases hu : u x <;> cases hn : n x <;> cases ha : allowed x <;>
    cases hr : review x <;> cases hh : hardReject x <;>
    all_goals
      simp [autoAccept, humanReview, eligible, meet, prime, bottom, hu, hn, ha, hr, hh]

theorem partition_eq_proposed {Atom : Type}
    (u n allowed review hardReject : Carrier Atom) :
    partition u n allowed review hardReject = proposed u n := by
  funext x
  cases hu : u x <;> cases hn : n x <;> cases ha : allowed x <;>
    cases hr : review x <;> cases hh : hardReject x <;>
    simp [
      partition,
      autoAccept,
      humanReview,
      symbolicReject,
      eligible,
      proposed,
      meet,
      join,
      prime,
      hu,
      hn,
      ha,
      hr,
      hh
    ]

theorem survivors_are_proposed {Atom : Type}
    (p allowed hardReject : Carrier Atom) :
    meet (survivors p allowed hardReject) (prime p) = bottom := by
  funext x
  cases hp : p x <;> cases ha : allowed x <;> cases hh : hardReject x <;>
    simp [survivors, meet, prime, bottom, hp, ha, hh]

theorem survivors_avoid_hard_reject {Atom : Type}
    (p allowed hardReject : Carrier Atom) :
    meet (survivors p allowed hardReject) hardReject = bottom := by
  funext x
  cases hp : p x <;> cases ha : allowed x <;> cases hh : hardReject x <;>
    simp [survivors, meet, prime, bottom, hp, ha, hh]

theorem survivors_are_allowed {Atom : Type}
    (p allowed hardReject : Carrier Atom) :
    meet (survivors p allowed hardReject) (prime allowed) = bottom := by
  funext x
  cases hp : p x <;> cases ha : allowed x <;> cases hh : hardReject x <;>
    simp [survivors, meet, prime, bottom, hp, ha, hh]

theorem auto_and_reject_disjoint {Atom : Type}
    (u n allowed review hardReject : Carrier Atom) :
    meet
      (autoAccept u n allowed review hardReject)
      (symbolicReject u n allowed hardReject) = bottom := by
  funext x
  cases hu : u x <;> cases hn : n x <;> cases ha : allowed x <;>
    cases hr : review x <;> cases hh : hardReject x <;>
    simp [
      autoAccept,
      symbolicReject,
      eligible,
      proposed,
      meet,
      join,
      prime,
      bottom,
      hu,
      hn,
      ha,
      hr,
      hh
    ]

theorem review_and_reject_disjoint {Atom : Type}
    (u n allowed review hardReject : Carrier Atom) :
    meet
      (humanReview u n allowed review hardReject)
      (symbolicReject u n allowed hardReject) = bottom := by
  funext x
  cases hu : u x <;> cases hn : n x <;> cases ha : allowed x <;>
    cases hr : review x <;> cases hh : hardReject x <;>
    simp [
      humanReview,
      symbolicReject,
      eligible,
      proposed,
      meet,
      join,
      prime,
      bottom,
      hu,
      hn,
      ha,
      hr,
      hh
    ]

namespace Loop

def hardWeight {Candidate : Type}
    (q : Candidate -> Nat) (chi : Candidate -> Bool) (y : Candidate) : Nat :=
  if chi y then q y else 0

theorem hardWeight_rejected_zero {Candidate : Type}
    (q : Candidate -> Nat) (chi : Candidate -> Bool) (y : Candidate)
    (h : chi y = false) :
    hardWeight q chi y = 0 := by
  simp [hardWeight, h]

theorem hardWeight_accepted_eq {Candidate : Type}
    (q : Candidate -> Nat) (chi : Candidate -> Bool) (y : Candidate)
    (h : chi y = true) :
    hardWeight q chi y = q y := by
  simp [hardWeight, h]

end Loop

end QNS

namespace EML

inductive Tree where
  | var : Tree
  | one : Tree
  | node : Tree -> Tree -> Tree
deriving Repr, DecidableEq

inductive Norm where
  | x : Norm
  | expX : Norm
  | expExpX : Norm
  | logX : Norm
deriving Repr, DecidableEq

inductive Target where
  | id : Target
  | exp : Target
  | expExp : Target
  | log : Target
deriving Repr, DecidableEq

structure Semantics (Alpha : Type) where
  one : Alpha
  exp : Alpha -> Alpha
  log : Alpha -> Alpha
  sub : Alpha -> Alpha -> Alpha

namespace Semantics

def eml {Alpha : Type} (s : Semantics Alpha) (a b : Alpha) : Alpha :=
  s.sub (s.exp a) (s.log b)

structure Laws {Alpha : Type} (s : Semantics Alpha) where
  log_one : s.log s.one = s.sub (s.exp s.one) (s.exp s.one)
  sub_zero_right : forall a, s.sub a (s.sub (s.exp s.one) (s.exp s.one)) = a
  log_exp : forall a, s.log (s.exp a) = a
  sub_self_sub : forall a b, s.sub a (s.sub a b) = b

structure BiLaws {Alpha : Type} (s : Semantics Alpha) extends Laws s where
  exp_log : forall a, s.exp (s.log a) = a

theorem eml_exp_identity {Alpha : Type}
    (s : Semantics Alpha) (laws : Laws s) (x : Alpha) :
    s.eml x s.one = s.exp x := by
  unfold eml
  rw [laws.log_one, laws.sub_zero_right]

theorem eml_log_standard_identity {Alpha : Type}
    (s : Semantics Alpha) (laws : Laws s) (x : Alpha) :
    s.eml s.one (s.eml (s.eml s.one x) s.one) = s.log x := by
  unfold eml
  rw [laws.log_one]
  rw [laws.sub_zero_right]
  rw [laws.log_exp]
  rw [laws.sub_self_sub]

theorem eml_log_discovered_identity {Alpha : Type}
    (s : Semantics Alpha) (laws : Laws s) (x : Alpha) :
    s.eml x (s.eml (s.eml x x) s.one) = s.log x := by
  unfold eml
  rw [laws.log_one]
  rw [laws.sub_zero_right]
  rw [laws.log_exp]
  rw [laws.sub_self_sub]

end Semantics

def Tree.eval {Alpha : Type} (s : Semantics Alpha) (x : Alpha) : Tree -> Alpha
  | Tree.var => x
  | Tree.one => s.one
  | Tree.node a b => s.eml (Tree.eval s x a) (Tree.eval s x b)

def Target.eval {Alpha : Type} (s : Semantics Alpha) (x : Alpha) : Target -> Alpha
  | Target.id => x
  | Target.exp => s.exp x
  | Target.expExp => s.exp (s.exp x)
  | Target.log => s.log x

def Norm.eval {Alpha : Type} (s : Semantics Alpha) (x : Alpha) : Norm -> Alpha
  | Norm.x => x
  | Norm.expX => s.exp x
  | Norm.expExpX => s.exp (s.exp x)
  | Norm.logX => s.log x

def shiftSemantics : Semantics Int where
  one := 1
  exp := fun a => a + 1
  log := fun a => a - 1
  sub := fun a b => a - b

theorem shiftSemantics_laws : Semantics.Laws shiftSemantics := by
  constructor
  · rfl
  · intro a
    simp [shiftSemantics]
  · intro a
    simp [shiftSemantics]
  · intro a b
    simp [shiftSemantics]
    omega

theorem shiftSemantics_biLaws : Semantics.BiLaws shiftSemantics := by
  constructor
  · exact shiftSemantics_laws
  · intro a
    simp [shiftSemantics]

theorem shiftSemantics_exp_ne_id_at_zero :
    Target.eval shiftSemantics 0 Target.exp ≠
      Target.eval shiftSemantics 0 Target.id := by
  native_decide

theorem shiftSemantics_log_ne_id_at_zero :
    Target.eval shiftSemantics 0 Target.log ≠
      Target.eval shiftSemantics 0 Target.id := by
  native_decide

theorem shiftSemantics_expExp_ne_exp_at_zero :
    Target.eval shiftSemantics 0 Target.expExp ≠
      Target.eval shiftSemantics 0 Target.exp := by
  native_decide

theorem shiftSemantics_wrapExp_var_not_id_at_zero :
    Tree.eval shiftSemantics 0 (Tree.node Tree.var Tree.one) ≠
      Target.eval shiftSemantics 0 Target.id := by
  native_decide

theorem shiftSemantics_var_not_exp_at_zero :
    Tree.eval shiftSemantics 0 Tree.var ≠
      Target.eval shiftSemantics 0 Target.exp := by
  native_decide

def doublingSemantics : Semantics Int where
  one := 0
  exp := fun a => 2 * a
  log := fun a => a / 2
  sub := fun a b => a - b

theorem doublingSemantics_laws : Semantics.Laws doublingSemantics := by
  constructor
  · rfl
  · intro a
    simp [doublingSemantics]
  · intro a
    simp [doublingSemantics]
  · intro a b
    simp [doublingSemantics]
    omega

theorem doublingSemantics_exp_log_ne_id_at_one :
    doublingSemantics.exp (doublingSemantics.log 1) ≠ (1 : Int) := by
  native_decide

theorem doublingSemantics_not_biLaws : ¬ Semantics.BiLaws doublingSemantics := by
  intro laws
  exact doublingSemantics_exp_log_ne_id_at_one (laws.exp_log 1)

def Norm.matchesTarget : Norm -> Target -> Bool
  | Norm.x, Target.id => true
  | Norm.expX, Target.exp => true
  | Norm.expExpX, Target.expExp => true
  | Norm.logX, Target.log => true
  | _, _ => false

def expTree : Tree :=
  Tree.node Tree.var Tree.one

def wrapExp (tree : Tree) : Tree :=
  Tree.node tree Tree.one

def wrapLogStandard (tree : Tree) : Tree :=
  Tree.node Tree.one (Tree.node (Tree.node Tree.one tree) Tree.one)

def expExpTree : Tree :=
  wrapExp expTree

def logStandardTree : Tree :=
  wrapLogStandard Tree.var

def logDiscoveredTree : Tree :=
  Tree.node Tree.var (Tree.node (Tree.node Tree.var Tree.var) Tree.one)

def identityViaLogExpTree : Tree :=
  wrapLogStandard expTree

def logExpExpTree : Tree :=
  wrapLogStandard expExpTree

def Tree.certNorm (tree : Tree) : Option Norm :=
  if tree = Tree.var then
    some Norm.x
  else if tree = expTree then
    some Norm.expX
  else if tree = expExpTree then
    some Norm.expExpX
  else if tree = logExpExpTree then
    some Norm.expX
  else if tree = logStandardTree then
    some Norm.logX
  else if tree = logDiscoveredTree then
    some Norm.logX
  else if tree = identityViaLogExpTree then
    some Norm.x
  else
    none

theorem eval_expTree {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Tree.eval s x expTree = s.exp x := by
  simp [Tree.eval, expTree, Semantics.eml_exp_identity, laws]

theorem eval_wrapExpWithOne {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) (tree : Tree) :
    Tree.eval s x (Tree.node tree Tree.one) = s.exp (Tree.eval s x tree) := by
  simp [Tree.eval, Semantics.eml_exp_identity, laws]

theorem eval_wrapExp {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) (tree : Tree) :
    Tree.eval s x (wrapExp tree) = s.exp (Tree.eval s x tree) := by
  simp [wrapExp, eval_wrapExpWithOne, laws]

theorem eval_wrapLogStandard {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) (tree : Tree) :
    Tree.eval s x (wrapLogStandard tree) = s.log (Tree.eval s x tree) := by
  simp [wrapLogStandard, Tree.eval, Semantics.eml_log_standard_identity, laws]

inductive ConstructorPlan where
  | var : ConstructorPlan
  | wrapExp : ConstructorPlan -> ConstructorPlan
  | wrapLog : ConstructorPlan -> ConstructorPlan
deriving Repr, DecidableEq

namespace ConstructorPlan

def tree : ConstructorPlan -> Tree
  | ConstructorPlan.var => Tree.var
  | ConstructorPlan.wrapExp p => EML.wrapExp p.tree
  | ConstructorPlan.wrapLog p => EML.wrapLogStandard p.tree

def offset : ConstructorPlan -> Int
  | ConstructorPlan.var => 0
  | ConstructorPlan.wrapExp p => p.offset + 1
  | ConstructorPlan.wrapLog p => p.offset - 1

theorem eval_shiftSemantics (p : ConstructorPlan) (x : Int) :
    Tree.eval shiftSemantics x p.tree = x + p.offset := by
  induction p with
  | var =>
    simp [tree, offset, Tree.eval]
  | wrapExp p ih =>
    rw [tree, eval_wrapExp shiftSemantics shiftSemantics_laws x p.tree, ih]
    simp [offset, shiftSemantics]
    omega
  | wrapLog p ih =>
    rw [tree, eval_wrapLogStandard shiftSemantics shiftSemantics_laws x p.tree, ih]
    simp [offset, shiftSemantics]
    omega

end ConstructorPlan

def Target.offset : Target -> Int
  | Target.id => 0
  | Target.exp => 1
  | Target.expExp => 2
  | Target.log => -1

def Target.constructorPlan : Target -> ConstructorPlan
  | Target.id => ConstructorPlan.var
  | Target.exp => ConstructorPlan.wrapExp ConstructorPlan.var
  | Target.expExp => ConstructorPlan.wrapExp (ConstructorPlan.wrapExp ConstructorPlan.var)
  | Target.log => ConstructorPlan.wrapLog ConstructorPlan.var

theorem Target.constructorPlan_offset (target : Target) :
    target.constructorPlan.offset = target.offset := by
  cases target <;> rfl

theorem Target.constructorPlan_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (target : Target) :
    Tree.eval s x target.constructorPlan.tree = Target.eval s x target := by
  cases target
  · rfl
  · exact eval_wrapExp s laws x Tree.var
  · rw [Target.constructorPlan, ConstructorPlan.tree]
    rw [eval_wrapExp s laws x (ConstructorPlan.wrapExp ConstructorPlan.var).tree]
    rw [ConstructorPlan.tree]
    exact congrArg s.exp (eval_wrapExp s laws x Tree.var)
  · exact eval_wrapLogStandard s laws x Tree.var

theorem Target.eval_shiftSemantics (target : Target) (x : Int) :
    Target.eval shiftSemantics x target = x + target.offset := by
  cases target <;> simp [Target.eval, Target.offset, shiftSemantics] <;> omega

theorem constructorPlan_offset_mismatch_countermodel
    (plan : ConstructorPlan) (target : Target)
    (h : plan.offset ≠ target.offset) :
    Tree.eval shiftSemantics 0 plan.tree ≠
      Target.eval shiftSemantics 0 target := by
  intro heq
  have hp := ConstructorPlan.eval_shiftSemantics plan 0
  have ht := Target.eval_shiftSemantics target 0
  rw [hp, ht] at heq
  simp at heq
  exact h heq

def offsetMatchButUnsoundPlan : ConstructorPlan :=
  ConstructorPlan.wrapExp (ConstructorPlan.wrapLog ConstructorPlan.var)

theorem offsetMatchButUnsoundPlan_offset :
    offsetMatchButUnsoundPlan.offset = Target.id.offset := by
  rfl

theorem offsetMatchButUnsoundPlan_countermodel :
    Tree.eval doublingSemantics 1 offsetMatchButUnsoundPlan.tree ≠
      Target.eval doublingSemantics 1 Target.id := by
  native_decide

theorem offset_match_is_not_sufficient :
    offsetMatchButUnsoundPlan.offset = Target.id.offset ∧
      Tree.eval doublingSemantics 1 offsetMatchButUnsoundPlan.tree ≠
        Target.eval doublingSemantics 1 Target.id := by
  exact ⟨offsetMatchButUnsoundPlan_offset, offsetMatchButUnsoundPlan_countermodel⟩

theorem eval_wrapLog_wrapExp {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) (tree : Tree) :
    Tree.eval s x (wrapLogStandard (wrapExp tree)) = Tree.eval s x tree := by
  calc
    Tree.eval s x (wrapLogStandard (wrapExp tree)) =
        s.log (Tree.eval s x (wrapExp tree)) := by
      rw [eval_wrapLogStandard s laws x (wrapExp tree)]
    _ = s.log (s.exp (Tree.eval s x tree)) := by
      rw [eval_wrapExp s laws x tree]
    _ = Tree.eval s x tree :=
      laws.log_exp (Tree.eval s x tree)

theorem eval_wrapExp_wrapLogStandard_guarded {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) (tree : Tree)
    (exp_log : forall a, s.exp (s.log a) = a) :
    Tree.eval s x (wrapExp (wrapLogStandard tree)) = Tree.eval s x tree := by
  calc
    Tree.eval s x (wrapExp (wrapLogStandard tree)) =
        s.exp (Tree.eval s x (wrapLogStandard tree)) := by
      rw [eval_wrapExp s laws x (wrapLogStandard tree)]
    _ = s.exp (s.log (Tree.eval s x tree)) := by
      rw [eval_wrapLogStandard s laws x tree]
    _ = Tree.eval s x tree :=
      exp_log (Tree.eval s x tree)

theorem offsetMatchButUnsoundPlan_sound_with_exp_log {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (exp_log : forall a, s.exp (s.log a) = a) :
    Tree.eval s x offsetMatchButUnsoundPlan.tree =
      Target.eval s x Target.id := by
  exact eval_wrapExp_wrapLogStandard_guarded s laws x Tree.var exp_log

theorem eval_wrapExp_wrapLogStandard_biLaws {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.BiLaws s) (x : Alpha) (tree : Tree) :
    Tree.eval s x (wrapExp (wrapLogStandard tree)) = Tree.eval s x tree := by
  exact eval_wrapExp_wrapLogStandard_guarded s laws.toLaws x tree laws.exp_log

theorem offsetMatchButUnsoundPlan_sound_with_biLaws {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.BiLaws s) (x : Alpha) :
    Tree.eval s x offsetMatchButUnsoundPlan.tree =
      Target.eval s x Target.id := by
  exact offsetMatchButUnsoundPlan_sound_with_exp_log s laws.toLaws x laws.exp_log

theorem eval_expExpTree {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Tree.eval s x expExpTree = s.exp (s.exp x) := by
  rw [expExpTree]
  rw [eval_wrapExp s laws x expTree]
  rw [eval_expTree s laws x]

theorem eval_logStandardTree {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Tree.eval s x logStandardTree = s.log x := by
  rw [logStandardTree]
  rw [eval_wrapLogStandard s laws x Tree.var]
  rfl

theorem eval_logDiscoveredTree {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Tree.eval s x logDiscoveredTree = s.log x := by
  simp [Tree.eval, logDiscoveredTree, Semantics.eml_log_discovered_identity, laws]

theorem eval_identityViaLogExpTree {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Tree.eval s x identityViaLogExpTree = x := by
  calc
    Tree.eval s x identityViaLogExpTree = s.log (s.exp x) := by
      rw [identityViaLogExpTree]
      rw [eval_wrapLogStandard s laws x expTree]
      rw [eval_expTree s laws x]
    _ = x :=
      laws.log_exp x

theorem eval_logExpExpTree {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Tree.eval s x logExpExpTree = s.exp x := by
  calc
    Tree.eval s x logExpExpTree = s.log (s.exp (s.exp x)) := by
      rw [logExpExpTree]
      rw [eval_wrapLogStandard s laws x expExpTree]
      rw [eval_expExpTree s laws x]
    _ = s.exp x :=
      laws.log_exp (s.exp x)

theorem certNorm_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (tree : Tree) (norm : Norm)
    (h : tree.certNorm = some norm) :
    Tree.eval s x tree = Norm.eval s x norm := by
  unfold Tree.certNorm at h
  by_cases hvar : tree = Tree.var
  · have hnorm : norm = Norm.x := by
      symm
      simpa [hvar] using h
    subst tree
    subst norm
    rfl
  · simp [hvar] at h
    by_cases hexp : tree = expTree
    · have hnorm : norm = Norm.expX := by
        symm
        simpa [hexp] using h
      subst tree
      subst norm
      exact eval_expTree s laws x
    · simp [hexp] at h
      by_cases hexpExp : tree = expExpTree
      · have hnorm : norm = Norm.expExpX := by
          symm
          simpa [hexpExp] using h
        subst tree
        subst norm
        exact eval_expExpTree s laws x
      · simp [hexpExp] at h
        by_cases hlogExpExp : tree = logExpExpTree
        · have hnorm : norm = Norm.expX := by
            symm
            simpa [hlogExpExp] using h
          subst tree
          subst norm
          exact eval_logExpExpTree s laws x
        · simp [hlogExpExp] at h
          by_cases hlogStandard : tree = logStandardTree
          · have hnorm : norm = Norm.logX := by
              symm
              simpa [hlogStandard] using h
            subst tree
            subst norm
            exact eval_logStandardTree s laws x
          · simp [hlogStandard] at h
            by_cases hlogDiscovered : tree = logDiscoveredTree
            · have hnorm : norm = Norm.logX := by
                symm
                simpa [hlogDiscovered] using h
              subst tree
              subst norm
              exact eval_logDiscoveredTree s laws x
            · simp [hlogDiscovered] at h
              by_cases hidentity : tree = identityViaLogExpTree
              · have hnorm : norm = Norm.x := by
                  symm
                  simpa [hidentity] using h
                subst tree
                subst norm
                exact eval_identityViaLogExpTree s laws x
              · simp [hidentity] at h

inductive Cert where
  | varTree : Cert
  | identityViaLogExpTree : Cert
  | expTree : Cert
  | expExpTree : Cert
  | logExpExpTree : Cert
  | logStandardTree : Cert
  | logDiscoveredTree : Cert
deriving Repr, DecidableEq

namespace Cert

def tree : Cert -> Tree
  | Cert.varTree => Tree.var
  | Cert.identityViaLogExpTree => EML.identityViaLogExpTree
  | Cert.expTree => EML.expTree
  | Cert.expExpTree => EML.expExpTree
  | Cert.logExpExpTree => EML.logExpExpTree
  | Cert.logStandardTree => EML.logStandardTree
  | Cert.logDiscoveredTree => EML.logDiscoveredTree

def target : Cert -> Target
  | Cert.varTree => Target.id
  | Cert.identityViaLogExpTree => Target.id
  | Cert.expTree => Target.exp
  | Cert.expExpTree => Target.expExp
  | Cert.logExpExpTree => Target.exp
  | Cert.logStandardTree => Target.log
  | Cert.logDiscoveredTree => Target.log

def check (cert : Cert) (tree : Tree) (target : Target) : Bool :=
  decide (cert.tree = tree) && decide (cert.target = target)

theorem sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (cert : Cert) (tree : Tree) (target : Target)
    (h : cert.check tree target = true) :
    Tree.eval s x tree = Target.eval s x target := by
  unfold check at h
  simp at h
  rcases h with ⟨htree, htarget⟩
  subst htree
  subst htarget
  cases cert <;>
    simp [
      Cert.tree,
      Cert.target,
      Tree.eval,
      Target.eval,
      eval_identityViaLogExpTree,
      eval_expTree,
      eval_expExpTree,
      eval_logExpExpTree,
      eval_logStandardTree,
      eval_logDiscoveredTree,
      laws
    ]

theorem identity_certificate_accepts :
    Cert.identityViaLogExpTree.check EML.identityViaLogExpTree Target.id = true := by
  simp [check, tree, target]

theorem var_certificate_accepts :
    Cert.varTree.check Tree.var Target.id = true := by
  simp [check, tree, target]

theorem exp_certificate_accepts :
    Cert.expTree.check EML.expTree Target.exp = true := by
  simp [check, tree, target]

theorem exp_exp_certificate_accepts :
    Cert.expExpTree.check EML.expExpTree Target.expExp = true := by
  simp [check, tree, target]

theorem log_exp_exp_certificate_accepts :
    Cert.logExpExpTree.check EML.logExpExpTree Target.exp = true := by
  simp [check, tree, target]

theorem log_standard_certificate_accepts :
    Cert.logStandardTree.check EML.logStandardTree Target.log = true := by
  simp [check, tree, target]

theorem log_discovered_certificate_accepts :
    Cert.logDiscoveredTree.check EML.logDiscoveredTree Target.log = true := by
  simp [check, tree, target]

end Cert

def checkByNorm (tree : Tree) (target : Target) : Bool :=
  match tree.certNorm with
  | some norm => norm.matchesTarget target
  | none => false

theorem checkByNorm_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (tree : Tree) (target : Target)
    (h : checkByNorm tree target = true) :
    Tree.eval s x tree = Target.eval s x target := by
  unfold checkByNorm at h
  cases hnorm : tree.certNorm with
  | none =>
    simp [hnorm] at h
  | some norm =>
    have hs := certNorm_sound s laws x tree norm hnorm
    cases norm <;> cases target <;>
      simp [Norm.matchesTarget, Target.eval, Norm.eval, hnorm] at h hs ⊢
    · exact hs
    · exact hs
    · exact hs
    · exact hs

theorem checkByNorm_accepts_expTree :
    checkByNorm expTree Target.exp = true := by
  native_decide

theorem checkByNorm_accepts_varTree :
    checkByNorm Tree.var Target.id = true := by
  native_decide

theorem checkByNorm_accepts_expExpTree :
    checkByNorm expExpTree Target.expExp = true := by
  native_decide

theorem checkByNorm_accepts_logExpExpTree :
    checkByNorm logExpExpTree Target.exp = true := by
  native_decide

theorem checkByNorm_accepts_identityViaLogExpTree :
    checkByNorm identityViaLogExpTree Target.id = true := by
  native_decide

theorem checkByNorm_accepts_logStandardTree :
    checkByNorm logStandardTree Target.log = true := by
  native_decide

theorem checkByNorm_accepts_logDiscoveredTree :
    checkByNorm logDiscoveredTree Target.log = true := by
  native_decide

inductive Expr where
  | var : Expr
  | one : Expr
  | zero : Expr
  | exp : Expr -> Expr
  | log : Expr -> Expr
  | sub : Expr -> Expr -> Expr
deriving Repr, DecidableEq

def Expr.eval {Alpha : Type} (s : Semantics Alpha) (x : Alpha) : Expr -> Alpha
  | Expr.var => x
  | Expr.one => s.one
  | Expr.zero => s.sub (s.exp s.one) (s.exp s.one)
  | Expr.exp a => s.exp (Expr.eval s x a)
  | Expr.log a => s.log (Expr.eval s x a)
  | Expr.sub a b => s.sub (Expr.eval s x a) (Expr.eval s x b)

def Expr.size : Expr -> Nat
  | Expr.var => 1
  | Expr.one => 1
  | Expr.zero => 1
  | Expr.exp a => a.size + 1
  | Expr.log a => a.size + 1
  | Expr.sub a b => a.size + b.size + 1

theorem Expr.size_pos (expr : Expr) : 0 < expr.size := by
  induction expr with
  | var => simp [Expr.size]
  | one => simp [Expr.size]
  | zero => simp [Expr.size]
  | exp a ih =>
    simp [Expr.size]
  | log a ih =>
    simp [Expr.size]
  | sub a b iha ihb =>
    simp [Expr.size]

def Tree.compileExpr : Tree -> Expr
  | Tree.var => Expr.var
  | Tree.one => Expr.one
  | Tree.node a b =>
    Expr.sub (Expr.exp a.compileExpr) (Expr.log b.compileExpr)

theorem compileExpr_sound {Alpha : Type}
    (s : Semantics Alpha) (x : Alpha) (tree : Tree) :
    Expr.eval s x tree.compileExpr = Tree.eval s x tree := by
  induction tree with
  | var => rfl
  | one => rfl
  | node a b iha ihb =>
    simp [Tree.compileExpr, Expr.eval, Tree.eval, Semantics.eml, iha, ihb]

inductive RewriteRule where
  | logOne : RewriteRule
  | subZeroRight : RewriteRule
  | logExp : RewriteRule
  | subSelfSub : RewriteRule
deriving Repr, DecidableEq

def RewriteRule.applyRoot? : RewriteRule -> Expr -> Option Expr
  | RewriteRule.logOne, Expr.log Expr.one =>
    some Expr.zero
  | RewriteRule.subZeroRight, Expr.sub a Expr.zero =>
    some a
  | RewriteRule.logExp, Expr.log (Expr.exp a) =>
    some a
  | RewriteRule.subSelfSub, Expr.sub a (Expr.sub a' b) =>
    if a = a' then some b else none
  | _, _ =>
    none

theorem RewriteRule.applyRoot?_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (rule : RewriteRule) (before after : Expr)
    (h : rule.applyRoot? before = some after) :
    Expr.eval s x before = Expr.eval s x after := by
  cases rule with
  | logOne =>
    cases before <;> simp [RewriteRule.applyRoot?] at h
    case log a =>
      cases a <;> simp [Expr.eval] at h ⊢
      subst after
      exact laws.log_one
  | subZeroRight =>
    cases before <;> simp [RewriteRule.applyRoot?] at h
    case sub a b =>
      cases b <;> simp [Expr.eval] at h ⊢
      subst after
      exact laws.sub_zero_right _
  | logExp =>
    cases before <;> simp [RewriteRule.applyRoot?] at h
    case log a =>
      cases a <;> simp [Expr.eval] at h ⊢
      subst after
      exact laws.log_exp _
  | subSelfSub =>
    cases before <;> simp [RewriteRule.applyRoot?] at h
    case sub a b =>
      cases b <;> simp [Expr.eval] at h ⊢
      case sub a' b' =>
        by_cases heq : a = a'
        · simp [heq] at h
          subst a'
          subst after
          exact laws.sub_self_sub _ _
        · simp [heq] at h

theorem RewriteRule.applyRoot?_size_decreases
    (rule : RewriteRule) (before after : Expr)
    (h : rule.applyRoot? before = some after) :
    after.size < before.size := by
  cases rule with
  | logOne =>
    cases before <;> simp [RewriteRule.applyRoot?] at h
    case log a =>
      cases a <;> simp at h
      case one =>
        subst after
        simp [Expr.size]
  | subZeroRight =>
    cases before <;> simp [RewriteRule.applyRoot?] at h
    case sub a b =>
      cases b <;> simp at h
      case zero =>
        subst after
        change a.size < a.size + 1 + 1
        omega
  | logExp =>
    cases before <;> simp [RewriteRule.applyRoot?] at h
    case log a =>
      cases a <;> simp at h
      case exp inner =>
        subst after
        change inner.size < inner.size + 1 + 1
        omega
  | subSelfSub =>
    cases before <;> simp [RewriteRule.applyRoot?] at h
    case sub a b =>
      cases b <;> simp at h
      case sub a' b' =>
        by_cases heq : a = a'
        · simp [heq] at h
          subst a'
          subst after
          change b'.size < a.size + (a.size + b'.size + 1) + 1
          omega
        · simp [heq] at h

inductive RewriteCert where
  | root : RewriteRule -> RewriteCert
  | exp : RewriteCert -> RewriteCert
  | log : RewriteCert -> RewriteCert
  | subLeft : RewriteCert -> RewriteCert
  | subRight : RewriteCert -> RewriteCert
deriving Repr, DecidableEq

def RewriteCert.apply? : RewriteCert -> Expr -> Option Expr
  | RewriteCert.root rule, before =>
    rule.applyRoot? before
  | RewriteCert.exp cert, Expr.exp a =>
    match cert.apply? a with
    | some a' => some (Expr.exp a')
    | none => none
  | RewriteCert.log cert, Expr.log a =>
    match cert.apply? a with
    | some a' => some (Expr.log a')
    | none => none
  | RewriteCert.subLeft cert, Expr.sub a b =>
    match cert.apply? a with
    | some a' => some (Expr.sub a' b)
    | none => none
  | RewriteCert.subRight cert, Expr.sub a b =>
    match cert.apply? b with
    | some b' => some (Expr.sub a b')
    | none => none
  | _, _ =>
    none

theorem RewriteCert.apply?_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (cert : RewriteCert) (before after : Expr)
    (h : cert.apply? before = some after) :
    Expr.eval s x before = Expr.eval s x after := by
  induction cert generalizing before after with
  | root rule =>
    exact RewriteRule.applyRoot?_sound s laws x rule before after h
  | exp cert ih =>
    cases before <;> simp [RewriteCert.apply?] at h
    case exp a =>
      cases hcert : cert.apply? a <;> simp [hcert] at h
      subst after
      exact congrArg s.exp (ih a _ hcert)
  | log cert ih =>
    cases before <;> simp [RewriteCert.apply?] at h
    case log a =>
      cases hcert : cert.apply? a <;> simp [hcert] at h
      subst after
      exact congrArg s.log (ih a _ hcert)
  | subLeft cert ih =>
    cases before <;> simp [RewriteCert.apply?] at h
    case sub a b =>
      cases hcert : cert.apply? a <;> simp [hcert] at h
      subst after
      exact congrArg (fun v => s.sub v (Expr.eval s x b)) (ih a _ hcert)
  | subRight cert ih =>
    cases before <;> simp [RewriteCert.apply?] at h
    case sub a b =>
      cases hcert : cert.apply? b <;> simp [hcert] at h
      subst after
      exact congrArg (fun v => s.sub (Expr.eval s x a) v) (ih b _ hcert)

theorem RewriteCert.apply?_size_decreases
    (cert : RewriteCert) (before after : Expr)
    (h : cert.apply? before = some after) :
    after.size < before.size := by
  induction cert generalizing before after with
  | root rule =>
    exact RewriteRule.applyRoot?_size_decreases rule before after h
  | exp cert ih =>
    cases before <;> simp [RewriteCert.apply?] at h
    case exp a =>
      cases hcert : cert.apply? a <;> simp [hcert] at h
      subst after
      have hdec := ih a _ hcert
      simp [Expr.size]
      omega
  | log cert ih =>
    cases before <;> simp [RewriteCert.apply?] at h
    case log a =>
      cases hcert : cert.apply? a <;> simp [hcert] at h
      subst after
      have hdec := ih a _ hcert
      simp [Expr.size]
      omega
  | subLeft cert ih =>
    cases before <;> simp [RewriteCert.apply?] at h
    case sub a b =>
      cases hcert : cert.apply? a <;> simp [hcert] at h
      subst after
      have hdec := ih a _ hcert
      simp [Expr.size]
      omega
  | subRight cert ih =>
    cases before <;> simp [RewriteCert.apply?] at h
    case sub a b =>
      cases hcert : cert.apply? b <;> simp [hcert] at h
      subst after
      have hdec := ih b _ hcert
      simp [Expr.size]
      omega

namespace RewriteChain

def apply? : List RewriteCert -> Expr -> Option Expr
  | [], expr => some expr
  | cert :: rest, expr =>
    match cert.apply? expr with
    | some next => apply? rest next
    | none => none

theorem apply?_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (chain : List RewriteCert) (before after : Expr)
    (h : apply? chain before = some after) :
    Expr.eval s x before = Expr.eval s x after := by
  induction chain generalizing before with
  | nil =>
    simp [apply?] at h
    subst after
    rfl
  | cons cert rest ih =>
    simp [apply?] at h
    cases hstep : cert.apply? before with
    | none =>
      simp [hstep] at h
    | some next =>
      simp [hstep] at h
      exact (RewriteCert.apply?_sound s laws x cert before next hstep).trans
        (ih next h)

end RewriteChain

def logDiscoveredExprTarget : Expr :=
  Expr.log Expr.var

def logDiscoveredRewriteChain : List RewriteCert :=
  [
    RewriteCert.subRight
      (RewriteCert.log
        (RewriteCert.subRight
          (RewriteCert.root RewriteRule.logOne))),
    RewriteCert.subRight
      (RewriteCert.log
        (RewriteCert.root RewriteRule.subZeroRight)),
    RewriteCert.subRight
      (RewriteCert.root RewriteRule.logExp),
    RewriteCert.root RewriteRule.subSelfSub
  ]

theorem logDiscoveredRewriteChain_accepts :
    RewriteChain.apply?
      logDiscoveredRewriteChain
      logDiscoveredTree.compileExpr = some logDiscoveredExprTarget := by
  native_decide

theorem logDiscoveredRewriteChain_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Expr.eval s x logDiscoveredTree.compileExpr = s.log x := by
  have h := RewriteChain.apply?_sound
    s laws x
    logDiscoveredRewriteChain
    logDiscoveredTree.compileExpr
    logDiscoveredExprTarget
    logDiscoveredRewriteChain_accepts
  simpa [logDiscoveredExprTarget, Expr.eval] using h

def Target.compileExpr : Target -> Expr
  | Target.id => Expr.var
  | Target.exp => Expr.exp Expr.var
  | Target.expExp => Expr.exp (Expr.exp Expr.var)
  | Target.log => Expr.log Expr.var

def Norm.compileExpr : Norm -> Expr
  | Norm.x => Expr.var
  | Norm.expX => Target.exp.compileExpr
  | Norm.expExpX => Target.expExp.compileExpr
  | Norm.logX => Target.log.compileExpr

theorem Target.compileExpr_sound {Alpha : Type}
    (s : Semantics Alpha) (x : Alpha) (target : Target) :
    Expr.eval s x target.compileExpr = Target.eval s x target := by
  cases target <;> rfl

theorem Norm.compileExpr_sound {Alpha : Type}
    (s : Semantics Alpha) (x : Alpha) (norm : Norm) :
    Expr.eval s x norm.compileExpr = Norm.eval s x norm := by
  cases norm <;> rfl

def emitRewriteChain? (tree : Tree) (target : Target) : Option (List RewriteCert) :=
  if tree = logDiscoveredTree then
    if target = Target.log then
      some logDiscoveredRewriteChain
    else
      none
  else
    none

theorem emitRewriteChain?_accepts
    (tree : Tree) (target : Target) (chain : List RewriteCert)
    (h : emitRewriteChain? tree target = some chain) :
    RewriteChain.apply? chain tree.compileExpr = some target.compileExpr := by
  unfold emitRewriteChain? at h
  by_cases htree : tree = logDiscoveredTree
  · simp [htree] at h
    by_cases htarget : target = Target.log
    · simp [htarget] at h
      subst tree
      subst target
      subst chain
      exact logDiscoveredRewriteChain_accepts
    · simp [htarget] at h
  · simp [htree] at h

theorem emitRewriteChain?_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (tree : Tree) (target : Target) (chain : List RewriteCert)
    (h : emitRewriteChain? tree target = some chain) :
    Expr.eval s x tree.compileExpr = Target.eval s x target := by
  have haccept := emitRewriteChain?_accepts tree target chain h
  have hchain := RewriteChain.apply?_sound
    s laws x chain tree.compileExpr target.compileExpr haccept
  exact hchain.trans (Target.compileExpr_sound s x target)

namespace RewriteStrategy

def emitStepCert? : Expr -> Option RewriteCert
  | Expr.log Expr.one =>
    some (RewriteCert.root RewriteRule.logOne)
  | Expr.sub _ Expr.zero =>
    some (RewriteCert.root RewriteRule.subZeroRight)
  | Expr.log (Expr.exp _) =>
    some (RewriteCert.root RewriteRule.logExp)
  | Expr.sub a (Expr.sub a' b) =>
    if a = a' then
      some (RewriteCert.root RewriteRule.subSelfSub)
    else
      match emitStepCert? a with
      | some cert => some (RewriteCert.subLeft cert)
      | none =>
        match emitStepCert? (Expr.sub a' b) with
        | some cert => some (RewriteCert.subRight cert)
        | none => none
  | Expr.exp a =>
    match emitStepCert? a with
    | some cert => some (RewriteCert.exp cert)
    | none => none
  | Expr.log a =>
    match emitStepCert? a with
    | some cert => some (RewriteCert.log cert)
    | none => none
  | Expr.sub a b =>
    match emitStepCert? a with
    | some cert => some (RewriteCert.subLeft cert)
    | none =>
      match emitStepCert? b with
      | some cert => some (RewriteCert.subRight cert)
      | none => none
  | _ =>
    none

def emitStep? (before : Expr) : Option (RewriteCert × Expr) :=
  match emitStepCert? before with
  | some cert =>
    match cert.apply? before with
    | some after => some (cert, after)
    | none => none
  | none => none

theorem emitStep?_accepts
    (before : Expr) (cert : RewriteCert) (after : Expr)
    (h : emitStep? before = some (cert, after)) :
    cert.apply? before = some after := by
  unfold emitStep? at h
  cases hcert : emitStepCert? before with
  | none =>
    simp [hcert] at h
  | some emittedCert =>
    cases happ : emittedCert.apply? before with
    | none =>
      simp [hcert, happ] at h
    | some emittedAfter =>
      simp [hcert, happ] at h
      rcases h with ⟨hcertEq, hafterEq⟩
      subst cert
      subst after
      exact happ

theorem emitStep?_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (before : Expr) (cert : RewriteCert) (after : Expr)
    (h : emitStep? before = some (cert, after)) :
    Expr.eval s x before = Expr.eval s x after :=
  RewriteCert.apply?_sound s laws x cert before after
    (emitStep?_accepts before cert after h)

theorem emitStep?_size_decreases
    (before : Expr) (cert : RewriteCert) (after : Expr)
    (h : emitStep? before = some (cert, after)) :
    after.size < before.size :=
  RewriteCert.apply?_size_decreases cert before after
    (emitStep?_accepts before cert after h)

def emitChainFuel : Nat -> Expr -> List RewriteCert × Expr
  | 0, before => ([], before)
  | fuel + 1, before =>
    match emitStep? before with
    | some (cert, next) =>
      let result := emitChainFuel fuel next
      (cert :: result.1, result.2)
    | none =>
      ([], before)

theorem emitChainFuel_ge_size_stable
    (fuel : Nat) (before : Expr) (hsize : before.size ≤ fuel) :
    emitStep? (emitChainFuel fuel before).2 = none := by
  induction fuel generalizing before with
  | zero =>
    have hpos := Expr.size_pos before
    omega
  | succ fuel ih =>
    cases hstep : emitStep? before with
    | none =>
      simp [emitChainFuel, hstep]
    | some pair =>
      rcases pair with ⟨cert, next⟩
      have hdec := emitStep?_size_decreases before cert next hstep
      have hnext : next.size ≤ fuel := by
        omega
      simp [emitChainFuel, hstep]
      exact ih next hnext

theorem emitChainFuel_size_stable (before : Expr) :
    emitStep? (emitChainFuel before.size before).2 = none :=
  emitChainFuel_ge_size_stable before.size before (Nat.le_refl before.size)

theorem emitChainFuel_of_stable
    (fuel : Nat) (expr : Expr) (h : emitStep? expr = none) :
    emitChainFuel fuel expr = ([], expr) := by
  cases fuel with
  | zero =>
    simp [emitChainFuel]
  | succ fuel =>
    simp [emitChainFuel, h]

theorem emitStep?_var_none :
    emitStep? Expr.var = none := by
  native_decide

theorem emitStep?_exp_target_none :
    emitStep? Target.exp.compileExpr = none := by
  native_decide

theorem emitStep?_log_target_none :
    emitStep? Target.log.compileExpr = none := by
  native_decide

theorem emitStep?_expExp_target_none :
    emitStep? Target.expExp.compileExpr = none := by
  native_decide

theorem exp_emitChainFuel_size_reaches :
    (emitChainFuel expTree.compileExpr.size expTree.compileExpr).2 =
      Target.exp.compileExpr := by
  native_decide

theorem expExp_emitChainFuel_size_reaches :
    (emitChainFuel expExpTree.compileExpr.size expExpTree.compileExpr).2 =
      Target.expExp.compileExpr := by
  native_decide

theorem logExpExp_emitChainFuel_size_reaches :
    (emitChainFuel logExpExpTree.compileExpr.size logExpExpTree.compileExpr).2 =
      Target.exp.compileExpr := by
  native_decide

theorem logStandard_emitChainFuel_size_reaches :
    (emitChainFuel logStandardTree.compileExpr.size logStandardTree.compileExpr).2 =
      Target.log.compileExpr := by
  native_decide

theorem logDiscovered_emitChainFuel_size_reaches :
    (emitChainFuel logDiscoveredTree.compileExpr.size logDiscoveredTree.compileExpr).2 =
      Target.log.compileExpr := by
  native_decide

theorem identityViaLogExp_emitChainFuel_size_reaches :
    (emitChainFuel identityViaLogExpTree.compileExpr.size identityViaLogExpTree.compileExpr).2 =
      Target.id.compileExpr := by
  native_decide

theorem var_emitChainFuel_size_reaches :
    (emitChainFuel Tree.var.compileExpr.size Tree.var.compileExpr).2 =
      Target.id.compileExpr := by
  native_decide

theorem certNorm_emitChainFuel_size_reaches
    (tree : Tree) (norm : Norm) (h : tree.certNorm = some norm) :
    (emitChainFuel tree.compileExpr.size tree.compileExpr).2 = norm.compileExpr := by
  unfold Tree.certNorm at h
  by_cases hvar : tree = Tree.var
  · have hnorm : norm = Norm.x := by
      symm
      simpa [hvar] using h
    subst tree
    subst norm
    native_decide
  · simp [hvar] at h
    by_cases hexp : tree = expTree
    · have hnorm : norm = Norm.expX := by
        symm
        simpa [hexp] using h
      subst tree
      subst norm
      exact exp_emitChainFuel_size_reaches
    · simp [hexp] at h
      by_cases hexpExp : tree = expExpTree
      · have hnorm : norm = Norm.expExpX := by
          symm
          simpa [hexpExp] using h
        subst tree
        subst norm
        exact expExp_emitChainFuel_size_reaches
      · simp [hexpExp] at h
        by_cases hlogExpExp : tree = logExpExpTree
        · have hnorm : norm = Norm.expX := by
            symm
            simpa [hlogExpExp] using h
          subst tree
          subst norm
          exact logExpExp_emitChainFuel_size_reaches
        · simp [hlogExpExp] at h
          by_cases hlogStandard : tree = logStandardTree
          · have hnorm : norm = Norm.logX := by
              symm
              simpa [hlogStandard] using h
            subst tree
            subst norm
            exact logStandard_emitChainFuel_size_reaches
          · simp [hlogStandard] at h
            by_cases hlogDiscovered : tree = logDiscoveredTree
            · have hnorm : norm = Norm.logX := by
                symm
                simpa [hlogDiscovered] using h
              subst tree
              subst norm
              exact logDiscovered_emitChainFuel_size_reaches
            · simp [hlogDiscovered] at h
              by_cases hidentity : tree = identityViaLogExpTree
              · have hnorm : norm = Norm.x := by
                  symm
                  simpa [hidentity] using h
                subst tree
                subst norm
                exact identityViaLogExp_emitChainFuel_size_reaches
              · simp [hidentity] at h

theorem emitChainFuel_accepts
    (fuel : Nat) (before : Expr) :
    RewriteChain.apply?
      (emitChainFuel fuel before).1
      before = some (emitChainFuel fuel before).2 := by
  induction fuel generalizing before with
  | zero =>
    simp [emitChainFuel, RewriteChain.apply?]
  | succ fuel ih =>
    simp [emitChainFuel]
    cases hstep : emitStep? before with
    | none =>
      simp [RewriteChain.apply?]
    | some pair =>
      rcases pair with ⟨cert, next⟩
      have hcert := emitStep?_accepts before cert next hstep
      have htail := ih next
      simp [RewriteChain.apply?, hcert, htail]

theorem emitChainFuel_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (fuel : Nat) (before : Expr) :
    Expr.eval s x before =
      Expr.eval s x (emitChainFuel fuel before).2 :=
  RewriteChain.apply?_sound
    s laws x
    (emitChainFuel fuel before).1
    before
    (emitChainFuel fuel before).2
    (emitChainFuel_accepts fuel before)

theorem certNorm_emitChainFuel_size_final_sound {Alpha : Type}
    (s : Semantics Alpha) (x : Alpha)
    (tree : Tree) (norm : Norm) (h : tree.certNorm = some norm) :
    Expr.eval s x (emitChainFuel tree.compileExpr.size tree.compileExpr).2 =
      Norm.eval s x norm := by
  rw [certNorm_emitChainFuel_size_reaches tree norm h]
  exact Norm.compileExpr_sound s x norm

theorem certNorm_emitChainFuel_size_source_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (tree : Tree) (norm : Norm) (h : tree.certNorm = some norm) :
    Expr.eval s x tree.compileExpr = Norm.eval s x norm := by
  calc
    Expr.eval s x tree.compileExpr =
        Expr.eval s x (emitChainFuel tree.compileExpr.size tree.compileExpr).2 :=
      emitChainFuel_sound s laws x tree.compileExpr.size tree.compileExpr
    _ = Norm.eval s x norm :=
      certNorm_emitChainFuel_size_final_sound s x tree norm h

def normalize (expr : Expr) : Expr :=
  (emitChainFuel expr.size expr).2

theorem normalize_stable (expr : Expr) :
    emitStep? (normalize expr) = none :=
  emitChainFuel_size_stable expr

theorem normalize_of_stable
    (expr : Expr) (h : emitStep? expr = none) :
    normalize expr = expr := by
  unfold normalize
  simp [emitChainFuel_of_stable expr.size expr h]

theorem normalize_idempotent (expr : Expr) :
    normalize (normalize expr) = normalize expr :=
  normalize_of_stable (normalize expr) (normalize_stable expr)

theorem normalize_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (expr : Expr) :
    Expr.eval s x expr = Expr.eval s x (normalize expr) :=
  emitChainFuel_sound s laws x expr.size expr

def equivByNormalize? (a b : Expr) : Bool :=
  decide (normalize a = normalize b)

def normalizeQuotient (a b : Expr) : Prop :=
  normalize a = normalize b

theorem normalizeQuotient_refl (a : Expr) :
    normalizeQuotient a a := by
  rfl

theorem normalizeQuotient_symm (a b : Expr)
    (h : normalizeQuotient a b) :
    normalizeQuotient b a :=
  h.symm

theorem normalizeQuotient_trans (a b c : Expr)
    (hab : normalizeQuotient a b) (hbc : normalizeQuotient b c) :
    normalizeQuotient a c :=
  hab.trans hbc

theorem normalizeQuotient_equivalence :
    Equivalence normalizeQuotient :=
  ⟨
    normalizeQuotient_refl,
    fun h => h.symm,
    fun hab hbc => hab.trans hbc
  ⟩

theorem equivByNormalize?_eq_true_iff (a b : Expr) :
    equivByNormalize? a b = true ↔ normalizeQuotient a b := by
  unfold equivByNormalize? normalizeQuotient
  by_cases h : normalize a = normalize b <;> simp [h]

theorem equivByNormalize?_refl (a : Expr) :
    equivByNormalize? a a = true := by
  rw [equivByNormalize?_eq_true_iff]
  exact normalizeQuotient_refl a

theorem equivByNormalize?_symm (a b : Expr)
    (h : equivByNormalize? a b = true) :
    equivByNormalize? b a = true := by
  rw [equivByNormalize?_eq_true_iff] at h ⊢
  exact normalizeQuotient_symm a b h

theorem equivByNormalize?_trans (a b c : Expr)
    (hab : equivByNormalize? a b = true)
    (hbc : equivByNormalize? b c = true) :
    equivByNormalize? a c = true := by
  rw [equivByNormalize?_eq_true_iff] at hab hbc ⊢
  exact normalizeQuotient_trans a b c hab hbc

theorem normalizeQuotient_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (a b : Expr) (h : normalizeQuotient a b) :
    Expr.eval s x a = Expr.eval s x b := by
  have ha := normalize_sound s laws x a
  have hb := normalize_sound s laws x b
  calc
    Expr.eval s x a = Expr.eval s x (normalize a) := ha
    _ = Expr.eval s x (normalize b) := by simp [normalizeQuotient] at h; simp [h]
    _ = Expr.eval s x b := by
      symm
      exact hb

theorem equivByNormalize?_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (a b : Expr)
    (h : equivByNormalize? a b = true) :
    Expr.eval s x a = Expr.eval s x b := by
  unfold equivByNormalize? at h
  by_cases hnorm : normalize a = normalize b
  · have ha := normalize_sound s laws x a
    have hb := normalize_sound s laws x b
    calc
      Expr.eval s x a = Expr.eval s x (normalize a) := ha
      _ = Expr.eval s x (normalize b) := by simp [hnorm]
      _ = Expr.eval s x b := by
        symm
        exact hb
  · simp [hnorm] at h

def zeroExpanded : Expr :=
  Expr.sub (Expr.exp Expr.one) (Expr.exp Expr.one)

theorem zeroExpanded_semantic_eq {Alpha : Type}
    (s : Semantics Alpha) (x : Alpha) :
    Expr.eval s x zeroExpanded = Expr.eval s x Expr.zero := by
  rfl

theorem equivByNormalize?_incomplete_example :
    equivByNormalize? Expr.zero zeroExpanded = false := by
  native_decide

def canonZero : Expr -> Expr
  | Expr.exp a => Expr.exp (canonZero a)
  | Expr.log a => Expr.log (canonZero a)
  | Expr.sub a b =>
    if _h : a = Expr.exp Expr.one ∧ b = Expr.exp Expr.one then
      Expr.zero
    else
      Expr.sub (canonZero a) (canonZero b)
  | expr => expr

theorem canonZero_sound {Alpha : Type}
    (s : Semantics Alpha) (x : Alpha) (expr : Expr) :
    Expr.eval s x (canonZero expr) = Expr.eval s x expr := by
  induction expr with
  | var =>
    rfl
  | one =>
    rfl
  | zero =>
    rfl
  | exp a ih =>
    simp [canonZero, Expr.eval, ih]
  | log a ih =>
    simp [canonZero, Expr.eval, ih]
  | sub a b iha ihb =>
    by_cases h : a = Expr.exp Expr.one ∧ b = Expr.exp Expr.one
    · rcases h with ⟨ha, hb⟩
      subst ha
      subst hb
      simp [canonZero, Expr.eval]
    · simp [canonZero, Expr.eval, h, iha, ihb]

def equivByNormalizeCanonZero? (a b : Expr) : Bool :=
  decide (normalize (canonZero a) = normalize (canonZero b))

def canonZeroQuotient (a b : Expr) : Prop :=
  normalize (canonZero a) = normalize (canonZero b)

theorem canonZeroQuotient_refl (a : Expr) :
    canonZeroQuotient a a := by
  rfl

theorem canonZeroQuotient_symm (a b : Expr)
    (h : canonZeroQuotient a b) :
    canonZeroQuotient b a :=
  h.symm

theorem canonZeroQuotient_trans (a b c : Expr)
    (hab : canonZeroQuotient a b) (hbc : canonZeroQuotient b c) :
    canonZeroQuotient a c :=
  hab.trans hbc

theorem canonZeroQuotient_equivalence :
    Equivalence canonZeroQuotient :=
  ⟨
    canonZeroQuotient_refl,
    fun h => h.symm,
    fun hab hbc => hab.trans hbc
  ⟩

theorem equivByNormalizeCanonZero?_eq_true_iff (a b : Expr) :
    equivByNormalizeCanonZero? a b = true ↔ canonZeroQuotient a b := by
  unfold equivByNormalizeCanonZero? canonZeroQuotient
  by_cases h : normalize (canonZero a) = normalize (canonZero b) <;> simp [h]

theorem equivByNormalizeCanonZero?_refl (a : Expr) :
    equivByNormalizeCanonZero? a a = true := by
  rw [equivByNormalizeCanonZero?_eq_true_iff]
  exact canonZeroQuotient_refl a

theorem equivByNormalizeCanonZero?_symm (a b : Expr)
    (h : equivByNormalizeCanonZero? a b = true) :
    equivByNormalizeCanonZero? b a = true := by
  rw [equivByNormalizeCanonZero?_eq_true_iff] at h ⊢
  exact canonZeroQuotient_symm a b h

theorem equivByNormalizeCanonZero?_trans (a b c : Expr)
    (hab : equivByNormalizeCanonZero? a b = true)
    (hbc : equivByNormalizeCanonZero? b c = true) :
    equivByNormalizeCanonZero? a c = true := by
  rw [equivByNormalizeCanonZero?_eq_true_iff] at hab hbc ⊢
  exact canonZeroQuotient_trans a b c hab hbc

theorem canonZeroQuotient_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (a b : Expr) (h : canonZeroQuotient a b) :
    Expr.eval s x a = Expr.eval s x b := by
  have ha0 := canonZero_sound (s := s) (x := x) a
  have hb0 := canonZero_sound (s := s) (x := x) b
  have ha := normalize_sound s laws x (canonZero a)
  have hb := normalize_sound s laws x (canonZero b)
  calc
    Expr.eval s x a = Expr.eval s x (canonZero a) := by simpa using ha0.symm
    _ = Expr.eval s x (normalize (canonZero a)) := ha
    _ = Expr.eval s x (normalize (canonZero b)) := by
      simp [canonZeroQuotient] at h
      simp [h]
    _ = Expr.eval s x (canonZero b) := by
      symm
      exact hb
    _ = Expr.eval s x b := by simpa using hb0

theorem equivByNormalizeCanonZero?_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (a b : Expr)
    (h : equivByNormalizeCanonZero? a b = true) :
    Expr.eval s x a = Expr.eval s x b := by
  unfold equivByNormalizeCanonZero? at h
  by_cases hnorm : normalize (canonZero a) = normalize (canonZero b)
  · have ha0 := canonZero_sound (s := s) (x := x) a
    have hb0 := canonZero_sound (s := s) (x := x) b
    have ha := normalize_sound s laws x (canonZero a)
    have hb := normalize_sound s laws x (canonZero b)
    calc
      Expr.eval s x a = Expr.eval s x (canonZero a) := by simpa using ha0.symm
      _ = Expr.eval s x (normalize (canonZero a)) := ha
      _ = Expr.eval s x (normalize (canonZero b)) := by simp [hnorm]
      _ = Expr.eval s x (canonZero b) := by
        symm
        exact hb
      _ = Expr.eval s x b := by simpa using hb0
  · simp [hnorm] at h

theorem equivByNormalizeCanonZero?_accepts_zeroExpanded :
    equivByNormalizeCanonZero? Expr.zero zeroExpanded = true := by
  native_decide

def normalizeReceipt (expr : Expr) : List RewriteCert × Expr :=
  emitChainFuel expr.size expr

theorem normalizeReceipt_accepts (expr : Expr) :
    RewriteChain.apply? (normalizeReceipt expr).1 expr = some (normalizeReceipt expr).2 := by
  unfold normalizeReceipt
  simpa using emitChainFuel_accepts expr.size expr

theorem normalizeReceipt_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (expr : Expr) :
    Expr.eval s x expr = Expr.eval s x (normalizeReceipt expr).2 := by
  unfold normalizeReceipt
  simpa using emitChainFuel_sound s laws x expr.size expr

def normalizeReceiptCanonZero (expr : Expr) : List RewriteCert × Expr :=
  normalizeReceipt (canonZero expr)

theorem normalizeReceiptCanonZero_accepts (expr : Expr) :
    RewriteChain.apply?
      (normalizeReceiptCanonZero expr).1
      (canonZero expr) = some (normalizeReceiptCanonZero expr).2 := by
  unfold normalizeReceiptCanonZero
  simpa using normalizeReceipt_accepts (canonZero expr)

theorem normalizeReceiptCanonZero_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (expr : Expr) :
    Expr.eval s x expr = Expr.eval s x (normalizeReceiptCanonZero expr).2 := by
  unfold normalizeReceiptCanonZero
  have hcanon := canonZero_sound (s := s) (x := x) expr
  have hnorm := normalizeReceipt_sound s laws x (canonZero expr)
  calc
    Expr.eval s x expr = Expr.eval s x (canonZero expr) := by
      simpa using hcanon.symm
    _ = Expr.eval s x (normalizeReceipt (canonZero expr)).2 := hnorm

def equivReceiptCanonZero? (a b : Expr) :
    Option (List RewriteCert × List RewriteCert × Expr) :=
  let ra := normalizeReceiptCanonZero a
  let rb := normalizeReceiptCanonZero b
  if ra.2 = rb.2 then
    some (ra.1, rb.1, ra.2)
  else
    none

theorem equivReceiptCanonZero?_accepts_left
    (a b : Expr) (chainA chainB : List RewriteCert) (nf : Expr)
    (h : equivReceiptCanonZero? a b = some (chainA, chainB, nf)) :
    RewriteChain.apply? chainA (canonZero a) = some nf := by
  unfold equivReceiptCanonZero? at h
  dsimp at h
  by_cases hnorm : (normalizeReceiptCanonZero a).2 = (normalizeReceiptCanonZero b).2
  · simp [hnorm] at h
    have hchainA : chainA = (normalizeReceiptCanonZero a).1 := by
      simpa using h.1.symm
    have hnf : nf = (normalizeReceiptCanonZero a).2 := by
      calc
        nf = (normalizeReceiptCanonZero b).2 := by simpa using h.2.2.symm
        _ = (normalizeReceiptCanonZero a).2 := by simpa using hnorm.symm
    subst hchainA
    subst hnf
    simpa using normalizeReceiptCanonZero_accepts a
  · simp [hnorm] at h

theorem equivReceiptCanonZero?_accepts_right
    (a b : Expr) (chainA chainB : List RewriteCert) (nf : Expr)
    (h : equivReceiptCanonZero? a b = some (chainA, chainB, nf)) :
    RewriteChain.apply? chainB (canonZero b) = some nf := by
  unfold equivReceiptCanonZero? at h
  dsimp at h
  by_cases hnorm : (normalizeReceiptCanonZero a).2 = (normalizeReceiptCanonZero b).2
  · simp [hnorm] at h
    have hchainB : chainB = (normalizeReceiptCanonZero b).1 := by
      simpa using h.2.1.symm
    have hnfB : nf = (normalizeReceiptCanonZero b).2 := by
      simpa using h.2.2.symm
    subst hchainB
    subst hnfB
    simpa using normalizeReceiptCanonZero_accepts b
  · simp [hnorm] at h

theorem equivReceiptCanonZero?_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha)
    (a b : Expr) (chainA chainB : List RewriteCert) (nf : Expr)
    (h : equivReceiptCanonZero? a b = some (chainA, chainB, nf)) :
    Expr.eval s x a = Expr.eval s x b := by
  unfold equivReceiptCanonZero? at h
  simp [normalizeReceiptCanonZero] at h
  by_cases hnorm :
      (normalizeReceipt (canonZero a)).2 = (normalizeReceipt (canonZero b)).2
  · simp [hnorm] at h
    have ha0 := canonZero_sound (s := s) (x := x) a
    have hb0 := canonZero_sound (s := s) (x := x) b
    have ha := normalizeReceipt_sound s laws x (canonZero a)
    have hb := normalizeReceipt_sound s laws x (canonZero b)
    calc
      Expr.eval s x a = Expr.eval s x (canonZero a) := by simpa using ha0.symm
      _ = Expr.eval s x (normalizeReceipt (canonZero a)).2 := ha
      _ = Expr.eval s x (normalizeReceipt (canonZero b)).2 := by simp [hnorm]
      _ = Expr.eval s x (canonZero b) := by
        symm
        exact hb
      _ = Expr.eval s x b := by simpa using hb0
  · simp [hnorm] at h

theorem equivReceiptCanonZero?_some_implies_equivByNormalizeCanonZero?_true
    (a b : Expr) (chainA chainB : List RewriteCert) (nf : Expr)
    (h : equivReceiptCanonZero? a b = some (chainA, chainB, nf)) :
    equivByNormalizeCanonZero? a b = true := by
  unfold equivReceiptCanonZero? at h
  dsimp at h
  by_cases hcond : (normalizeReceiptCanonZero a).2 = (normalizeReceiptCanonZero b).2
  · have hnorm : normalize (canonZero a) = normalize (canonZero b) := by
      simpa [normalizeReceiptCanonZero, normalizeReceipt, normalize] using hcond
    unfold equivByNormalizeCanonZero?
    simp [hnorm]
  · simp [hcond] at h

theorem equivByNormalizeCanonZero?_true_implies_equivReceiptCanonZero?_some
    (a b : Expr)
    (h : equivByNormalizeCanonZero? a b = true) :
    equivReceiptCanonZero? a b =
      some ((normalizeReceiptCanonZero a).1,
            (normalizeReceiptCanonZero b).1,
            (normalizeReceiptCanonZero a).2) := by
  unfold equivByNormalizeCanonZero? at h
  by_cases hnorm : normalize (canonZero a) = normalize (canonZero b)
  · have hcond : (normalizeReceiptCanonZero a).2 = (normalizeReceiptCanonZero b).2 := by
      simpa [normalizeReceiptCanonZero, normalizeReceipt, normalize] using hnorm
    unfold equivReceiptCanonZero?
    dsimp
    simp [hcond]
  · simp [hnorm] at h

theorem normalize_certNorm_reaches
    (tree : Tree) (norm : Norm) (h : tree.certNorm = some norm) :
    normalize tree.compileExpr = norm.compileExpr :=
  certNorm_emitChainFuel_size_reaches tree norm h

theorem normalize_certNorm_sound {Alpha : Type}
    (s : Semantics Alpha) (x : Alpha)
    (tree : Tree) (norm : Norm) (h : tree.certNorm = some norm) :
    Expr.eval s x (normalize tree.compileExpr) = Norm.eval s x norm :=
  certNorm_emitChainFuel_size_final_sound s x tree norm h

theorem logDiscovered_emitChainFuel_4_reaches :
    (emitChainFuel 4 logDiscoveredTree.compileExpr).2 = logDiscoveredExprTarget := by
  native_decide

theorem logDiscovered_emitChainFuel_4_chain :
    (emitChainFuel 4 logDiscoveredTree.compileExpr).1 = logDiscoveredRewriteChain := by
  native_decide

theorem logDiscovered_emitChainFuel_4_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Expr.eval s x logDiscoveredTree.compileExpr = s.log x := by
  have hsound := emitChainFuel_sound s laws x 4 logDiscoveredTree.compileExpr
  rw [logDiscovered_emitChainFuel_4_reaches] at hsound
  simpa [logDiscoveredExprTarget, Expr.eval] using hsound

theorem exp_emitChainFuel_2_reaches :
    (emitChainFuel 2 expTree.compileExpr).2 = (Target.exp.compileExpr) := by
  native_decide

theorem exp_emitChainFuel_2_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Expr.eval s x expTree.compileExpr = s.exp x := by
  have hsound := emitChainFuel_sound s laws x 2 expTree.compileExpr
  rw [exp_emitChainFuel_2_reaches] at hsound
  simpa [Target.compileExpr, Expr.eval] using hsound

theorem expExp_emitChainFuel_size_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Expr.eval s x expExpTree.compileExpr = s.exp (s.exp x) := by
  have hsound := emitChainFuel_sound
    s laws x
    expExpTree.compileExpr.size
    expExpTree.compileExpr
  rw [expExp_emitChainFuel_size_reaches] at hsound
  simpa [Target.compileExpr, Expr.eval] using hsound

theorem logExpExp_emitChainFuel_size_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Expr.eval s x logExpExpTree.compileExpr = s.exp x := by
  have hsound := emitChainFuel_sound
    s laws x
    logExpExpTree.compileExpr.size
    logExpExpTree.compileExpr
  rw [logExpExp_emitChainFuel_size_reaches] at hsound
  simpa [Target.compileExpr, Expr.eval] using hsound

theorem logStandard_emitChainFuel_4_reaches :
    (emitChainFuel 4 logStandardTree.compileExpr).2 = (Target.log.compileExpr) := by
  native_decide

theorem logStandard_emitChainFuel_4_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Expr.eval s x logStandardTree.compileExpr = s.log x := by
  have hsound := emitChainFuel_sound s laws x 4 logStandardTree.compileExpr
  rw [logStandard_emitChainFuel_4_reaches] at hsound
  simpa [Target.compileExpr, Expr.eval] using hsound

theorem identityViaLogExp_emitChainFuel_size_sound {Alpha : Type}
    (s : Semantics Alpha) (laws : Semantics.Laws s) (x : Alpha) :
    Expr.eval s x identityViaLogExpTree.compileExpr = x := by
  have hsound := emitChainFuel_sound
    s laws x
    identityViaLogExpTree.compileExpr.size
    identityViaLogExpTree.compileExpr
  rw [identityViaLogExp_emitChainFuel_size_reaches] at hsound
  simpa [Target.compileExpr, Expr.eval] using hsound

end RewriteStrategy

end EML

end NeuroSymbolicMathV001
