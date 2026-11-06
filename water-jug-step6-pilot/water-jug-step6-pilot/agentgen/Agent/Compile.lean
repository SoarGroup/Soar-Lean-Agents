import Agent.DSL
import Soar.Syntax
/-!
# From a description to productions of the Soar specification

`compile a` gives the files of a VisualSoar project, each with productions of the Soar
specification (`Soar.Production`) and the commands it needs. Printing uses the specification's own
printer (`Soar.Production.toSoar`), so every generated rule is one the specification can parse and
run.

Layout (VisualSoar):
* `_firstload.soar` — commands (learning, multi-attributes)
* `elaborations/` — derived attributes, goal detection, problem space, ancestors
* `initialize-<task>.soar` — the initialization operator
* `<op>.soar` — one file per operator; an operator carried out in a substate also has a folder
  `<op>/` with one file per step
* `Impasse__Operator_Tie.soar`, `Impasse__Operator_Tie/` — the tie space of `tieHeuristic`
* `rl.soar` — RL templates and rewards
-/
namespace Agent
open Soar

/-- A file of the generated project. `kind` is the VisualSoar node type. -/
structure GenFile where
  path : String
  kind : String
  prods : List Production := []
  cmds : List String := []

/-! ## Small constructors -/

def vt (x : String) : Test := [.var x]
def ct (x : String) : Test := [.const (.str x)]
def itest (n : Int) : Test := [.const (.int n)]
def pp (i a : String) (val : Test) : Pat := { id := vt i, attr := ct a, val := val }
def P (i a : String) (val : Test) : Cond := .pos (pp i a val)
def Ps (i a : String) (val : Test) : Cond := .pos { pp i a val with goal := true }
def Pacc (i a : String) (val : Test) : Cond := .pos { pp i a val with acc := true }
def N (i a : String) (val : Test) : Cond := .neg [pp i a val]
def rv (x : String) : RVal := .var x
def rs (x : String) : RVal := .sym (.str x)
def ri (n : Int) : RVal := .sym (.int n)
def mk (i a : String) (val : RVal) : Action := .make i (rs a) val
def rm (i a : String) (val : RVal) : Action := .remove i (rs a) val

/-- The variable holding `obj.attr`. -/
def av (o a : String) : String := o ++ "-" ++ a

def Cmp.rel : Cmp → Option RelOp
  | .eq => none | .ne => some .ne | .lt => some .lt | .le => some .le
  | .gt => some .gt | .ge => some .ge

def Atom.term : Atom → Term
  | .lit n => .sym (.int n)
  | .get o a => .var (av o a)

def Expr.rval : Expr → RVal
  | .lit n => ri n
  | .get o a => rv (av o a)
  | .add x y => .call "+" [x.rval, y.rval]
  | .sub x y => .call "-" [x.rval, y.rval]

/-- Conditions that bind `obj.attr` for every reference and carry the guards' comparisons. -/
def refConds (refs : List (String × String)) (gs : List Guard) : List Cond :=
  let refs := (refs ++ gs.flatMap Guard.refs).eraseDups
  refs.map fun (o, a) =>
    let tests : Test := gs.filterMap fun g => match g with
      | .cmp o' a' op r =>
        if o' == o && a' == a then
          match op.rel, r with
          | none, .lit n => some (.const (.int n))
          | none, .get o2 a2 => some (.var (av o2 a2))
          | some rel, r => some (.rel rel r.term)
        else none
      | _ => none
    P o a (.var (av o a) :: tests)

/-- `(<s> ^holder <p>)` for each parameter, with distinctness tests. -/
def paramFromState (s : Schema) (ps : List (String × String)) (gs : List Guard) : List Cond :=
  ps.map fun (p, t) =>
    let h := ((s.holder? t).map (·.name)).getD t
    let ne : Test := gs.filterMap fun g => match g with
      | .distinct a b => if b == p then some (.rel .ne (.var a)) else none
      | _ => none
    P "s" h (.var p :: ne)

def opWithParams (o : String) (name : String) (ps : List (String × String)) : List Cond :=
  P o "name" (ct name) :: ps.map fun (p, _) => P o p (vt p)

def effectActs (es : List Effect) : List Action :=
  es.flatMap fun e => [mk e.obj e.attr e.val.rval, rm e.obj e.attr (rv (av e.obj e.attr))]

def effectRefs (es : List Effect) : List (String × String) :=
  es.flatMap fun e => (e.obj, e.attr) :: e.val.refs

/-! ## Pieces -/

def initOpName (a : Agent) : String := "initialize-" ++ a.schema.task

def objActs (holderOwner : String) (h : String) (var : String) (vals : ObjPat) : List Action :=
  mk holderOwner h (rv var) :: vals.map fun (k, n) => mk var k (ri n)

def initFile (a : Agent) : GenFile :=
  let t := a.schema.task
  let goalH := ((a.schema.holder? a.goal.ty).map (·.name)).getD a.goal.ty
  let objs := (a.init.zip (List.range a.init.length)).flatMap fun ((h, vals), i) =>
    objActs "s" h s!"x{i}" vals
  let lastOp := match a.method with
    | .tieHeuristic _ => [mk "s" "last-operator" (rs "none")]
    | _ => []
  { path := initOpName a ++ ".soar", kind := "OPERATOR", prods := [
    { name := s!"{t}*propose*{initOpName a}",
      conds := [Ps "s" "superstate" (ct "nil"), N "s" "name" []],
      acts := [.pref "s" (rv "o") .acceptable none none, mk "o" "name" (rs (initOpName a))] },
    { name := s!"{t}*apply*{initOpName a}",
      conds := [Ps "s" "operator" (vt "o"), P "o" "name" (ct (initOpName a))],
      acts := mk "s" "name" (rs t) :: objs ++
        [mk "s" "desired" (rv "d")] ++ objActs "d" goalH "dg" a.goal.vals ++ lastOp }] }

def deriveProds (a : Agent) : List Production :=
  a.derive.map fun d =>
    let h := ((a.schema.holder? d.ty).map (·.name)).getD d.ty
    { name := s!"{a.schema.task}*elaborate*{d.ty}*{d.attr}",
      conds := [Ps "s" "name" (ct a.schema.task), P "s" h (vt "self")] ++ refConds d.val.refs [],
      acts := [mk "self" d.attr d.val.rval] }

/-- The goal: success when some object matches the desired object; halt at the top state. -/
def goalProds (a : Agent) : List Production :=
  let t := a.schema.task
  let h := ((a.schema.holder? a.goal.ty).map (·.name)).getD a.goal.ty
  let keys := a.goal.vals.map (·.1)
  [{ name := s!"{t}*elaborate*goal*success",
     conds := [Ps "s" "name" (ct t), P "s" "desired" (vt "d"), P "s" h (vt "x"), P "d" h (vt "dx")] ++
       keys.map (fun k => P "dx" k (vt ("g-" ++ k))) ++ keys.map (fun k => P "x" k (vt ("g-" ++ k))),
     acts := [mk "s" "success" (rv "d")] },
   { name := s!"{t}*halt*goal*success",
     conds := [Ps "s" "superstate" (ct "nil"), P "s" "desired" (vt "d"), P "s" "success" (vt "d")],
     acts := [.write [.call "crlf" [], rs "The problem has been solved."], .halt] }]

def proposeProd (a : Agent) (o : Operator) : Production :=
  let indiff := match a.method with
    | .random | .rl _ => [Action.pref "s" (rv "o") .unaryIndiff none none]
    | _ => []
  { name := s!"{a.schema.task}*propose*{o.name}",
    conds := Ps "s" "name" (ct a.schema.task) :: paramFromState a.schema o.params o.propose ++
      refConds [] (o.propose.filter fun g => match g with | .distinct _ _ => false | _ => true),
    acts := [.pref "s" (rv "o") .acceptable none none] ++ indiff ++
      mk "o" "name" (rs o.name) :: o.params.map (fun (p, _) => mk "o" p (rv p)) }

def applyProds (a : Agent) (o : Operator) : List Production :=
  (o.apply.zip (List.range o.apply.length)).map fun (c, i) =>
    { name := s!"{a.schema.task}*apply*{o.name}" ++ (if o.apply.length > 1 then s!"*case{i+1}" else ""),
      conds := [Ps "s" "name" (ct a.schema.task), P "s" "operator" (vt "o")] ++
        opWithParams "o" o.name o.params ++ refConds (effectRefs c.effects) c.guard,
      acts := effectActs c.effects }

/-- An operator carried out by steps in its operator no-change substate. -/
def stepFiles (a : Agent) (o : Operator) (steps : List String) : List GenFile :=
  let nameProd : Production :=
    { name := s!"{o.name}*elaborate*substate",
      conds := [Ps "s" "impasse" (ct "no-change"), P "s" "attribute" (ct "operator"),
        P "s" "superstate" (vt "ss"), P "ss" "operator" (vt "so")] ++ opWithParams "so" o.name o.params,
      acts := mk "s" "name" (rs o.name) :: o.params.map (fun (p, _) => mk "s" p (rv p)) }
  let n := steps.length
  let stepFile (k : Nat) (st : String) : GenFile :=
    let prev := if k == 0 then [] else [P "s" "done" (ct steps[k-1]!)]
    let prop : Production :=
      { name := s!"{o.name}*propose*{st}",
        conds := [Ps "s" "name" (ct o.name), N "s" "done" (ct st)] ++ prev,
        acts := [.pref "s" (rv "o") .acceptable none none, .pref "s" (rv "o") .unaryIndiff none none,
          mk "o" "name" (rs st)] }
    let applies : List Production :=
      if k + 1 < n then
        [{ name := s!"{o.name}*apply*{st}",
           conds := [Ps "s" "name" (ct o.name), P "s" "operator" (vt "o"), P "o" "name" (ct st)],
           acts := [mk "s" "done" (rs st)] }]
      else
        (o.apply.zip (List.range o.apply.length)).map fun (c, i) =>
          { name := s!"{o.name}*apply*{st}" ++ (if o.apply.length > 1 then s!"*case{i+1}" else ""),
            conds := [Ps "s" "name" (ct o.name), P "s" "operator" (vt "o"), P "o" "name" (ct st)] ++
              o.params.map (fun (p, _) => P "s" p (vt p)) ++ refConds (effectRefs c.effects) c.guard,
            acts := effectActs c.effects ++ [mk "s" "done" (rs st)] }
    { path := s!"{o.name}/{st}.soar", kind := "OPERATOR", prods := prop :: applies }
  { path := s!"{o.name}/elaborations.soar", kind := "FILE_OPERATOR", prods := [nameProd] } ::
    (steps.zip (List.range n)).map fun (st, k) => stepFile k st

def opFiles (a : Agent) (o : Operator) : List GenFile :=
  match o.impl with
  | .atomic => [{ path := o.name ++ ".soar", kind := "OPERATOR", prods := [proposeProd a o] ++ applyProds a o }]
  | .steps ss => { path := o.name ++ ".soar", kind := "HIGH_LEVEL_OPERATOR", prods := [proposeProd a o] } ::
      stepFiles a o ss

/-- Conditions: `s` has objects matching each pattern of `p` (distinct objects). -/
def statePatConds (a : Agent) (st : String) (p : StatePat) (pfx : String) : List Cond :=
  let h := ((a.schema.holder? p.ty).map (·.name)).getD p.ty
  let vars := (List.range p.objs.length).map fun i => s!"{pfx}{i}"
  (vars.zip (List.range vars.length)).map (fun (x, i) =>
      P st h (.var x :: (vars.take i).map fun y => .rel .ne (.var y))) ++
    (p.objs.zip vars).flatMap fun (o, x) => o.map fun (k, n) => P x k (itest n)

/-! ## Selection methods -/

def tieFiles (a : Agent) (hs : List Heur) : List GenFile :=
  let t := a.schema.task
  let imp := "Impasse__Operator_Tie"
  let record : GenFile := { path := "elaborations/last-operator.soar", kind := "FILE_OPERATOR", prods := [
    { name := s!"{t}*apply*record*last-operator",
      conds := [Ps "s" "name" (ct t), P "s" "operator" (vt "o"),
        P "o" "name" [.var "n", .rel .ne (.sym (.str (initOpName a)))]],
      acts := [mk "s" "last-operator" (rv "n")] },
    { name := s!"{t}*apply*remove*last-operator",
      conds := [Ps "s" "name" (ct t), P "s" "last-operator" (vt "l"), P "s" "operator" (vt "o"),
        P "o" "name" [.var "n", .rel .ne (.var "l"), .rel .ne (.sym (.str (initOpName a)))]],
      acts := [rm "s" "last-operator" (rv "l")] }] }
  let elabF : GenFile := { path := imp ++ "/elaborations.soar", kind := "FILE_OPERATOR", prods := [
    { name := s!"{imp}*elaborate*name",
      conds := [Ps "s" "impasse" (ct "tie"), P "s" "attribute" (ct "operator"),
        P "s" "superstate" (vt "ss"), P "ss" "name" (ct t)],
      acts := [mk "s" "name" (rs imp)] },
    { name := s!"{imp}*elaborate*evaluation",
      conds := [Ps "s" "name" (ct imp), P "s" "item" (vt "x")],
      acts := [mk "s" "evaluation" (rv "e"), mk "e" "super-operator" (rv "x")] },
    { name := s!"{imp}*elaborate*last-operator",
      conds := [Ps "s" "name" (ct imp), P "s" "superstate" (vt "ss"), P "ss" "last-operator" (vt "l")],
      acts := [mk "s" "last-operator" (rv "l")] }] }
  let hval : HVal → String := fun | .best => "best" | .worst => "worst" | .equal => "equal"
  let disj (xs : List String) : Test := match xs with
    | [x] => ct x
    | xs => [.disj (xs.map Sym.str)]
  let evalProds := (hs.zip (List.range hs.length)).map fun (h, i) =>
    { name := s!"{imp}*apply*evaluate-operator*h{i+1}",
      conds := [Ps "s" "name" (ct imp), P "s" "operator" (vt "o"), P "s" "last-operator" (disj h.last),
        P "o" "name" (ct "evaluate-operator"), P "o" "evaluation" (vt "e"),
        P "e" "super-operator" (vt "so"), P "so" "name" (disj h.cands)],
      acts := [mk "e" "value" (rs (hval h.value))] : Production }
  let evalOp : GenFile := { path := imp ++ "/evaluate-operator.soar", kind := "OPERATOR", prods :=
    { name := s!"{imp}*propose*evaluate-operator",
      conds := [Ps "s" "name" (ct imp), P "s" "evaluation" (vt "e"), N "e" "value" []],
      acts := [.pref "s" (rv "o") .acceptable none none, .pref "s" (rv "o") .unaryIndiff none none,
        mk "o" "name" (rs "evaluate-operator"), mk "o" "evaluation" (rv "e")] } :: evalProds }
  let prefActs : HVal → List Action
    | .equal => [.pref "ss" (rv "so") .unaryIndiff none none]
    | .worst => [.pref "ss" (rv "so") .worst none none, .pref "ss" (rv "so") .unaryIndiff none none]
    | .best => [.pref "ss" (rv "so") .best none none, .pref "ss" (rv "so") .unaryIndiff none none]
  let createOp : GenFile := { path := imp ++ "/create-preferences.soar", kind := "OPERATOR", prods :=
    { name := s!"{imp}*propose*create-preferences",
      conds := [Ps "s" "name" (ct imp),
        .ncc [pp "s" "evaluation" (vt "e")] [[pp "e" "value" []]]],
      acts := [.pref "s" (rv "o") .acceptable none none, .pref "s" (rv "o") .unaryIndiff none none,
        .pref "s" (rv "o") .best none none, mk "o" "name" (rs "create-preferences")] } ::
    [HVal.equal, .worst, .best].map fun v =>
      { name := s!"{imp}*apply*create-preferences*{hval v}",
        conds := [Ps "s" "name" (ct imp), P "s" "operator" (vt "o"), P "o" "name" (ct "create-preferences"),
          P "s" "superstate" (vt "ss"), P "s" "evaluation" (vt "e"), P "e" "value" (ct (hval v)),
          P "e" "super-operator" (vt "so")],
        acts := prefActs v } }
  [record, { path := imp ++ ".soar", kind := "HIGH_LEVEL_IMPASSE_OPERATOR" }, elabF, evalOp, createOp]

/-- A state equal to an ancestor state: each of its `n` objects has a twin there (same non-derived
values). Written with positive conditions only, over the number of objects the task starts with,
so that chunking can trace it: a nested negation over the ancestor (the first version) made
chunking learn over-general rules ("every operator is a partial failure"). -/
def dupProd (t h : String) (keys : List String) (n : Nat) : Production where
  name := t ++ "*evaluate*state*failure*duplicate"
  conds := [Ps "s" "name" (ct t), P "s" "tried-tied-operator" [], P "s" "desired" (vt "d"),
    P "s" "ancestor" (vt "a"), P "a" "name" (ct t)] ++
    ((List.range n).flatMap fun i =>
      P "s" h (.var s!"x{i}" :: (List.range i).map fun j => .rel .ne (.var s!"x{j}")) ::
      keys.map (fun k => P s!"x{i}" k (vt s!"k{i}-{k}"))) ++
    ((List.range n).flatMap fun i =>
      P "a" h (vt s!"y{i}") :: keys.map (fun k => P s!"y{i}" k (vt s!"k{i}-{k}")))
  acts := [mk "s" "partial-failure" (rv "d")]

def lookaheadFiles (a : Agent) (avoid : List StatePat) (avoidValue : Option Int) : List GenFile :=
  let t := a.schema.task
  let s := a.schema
  let holders := s.stateAttrs.filter (fun d => d.multi && match d.ty with | .obj _ => true | _ => false)
  let derivedAttrs := s.types.flatMap fun ty => ty.attrs.filter (·.derived) |>.map (·.name)
  let ps : Production :=
    { name := s!"{t}*elaborate*problem-space",
      conds := [Ps "s" "name" (ct t)],
      acts := [mk "s" "problem-space" (rv "p"), mk "p" "name" (rs t),
        mk "p" "default-state-copy" (rs "yes"), mk "p" "default-operator-copy" (rs "yes")] ++
        holders.map (fun h => mk "p" "two-level-attributes" (rs h.name)) ++
        (derivedAttrs ++ ["ancestor"]).map (fun d => mk "p" "dont-copy" (rs d)) }
  let anc : List Production :=
    [{ name := s!"{t}*elaborate*ancestor*superstate",
       conds := [Ps "s" "superstate" (vt "ss"), P "ss" "superstate" []],
       acts := [mk "s" "ancestor" (rv "ss")] },
     { name := s!"{t}*elaborate*ancestor*inherit",
       conds := [Ps "s" "superstate" (vt "ss"), P "ss" "ancestor" (vt "a")],
       acts := [mk "s" "ancestor" (rv "a")] }]
  let dups : List Production := holders.filterMap fun h => match h.ty with
    | .obj ty => some (dupProd t h.name (((s.type? ty).map (fun o => (o.attrs.filter (fun d => !d.derived)).map (·.name))).getD [])
        (a.init.filter (·.1 == h.name)).length)
    | _ => none
  let avoids := (avoid.zip (List.range avoid.length)).map fun (p, i) =>
    { name := s!"{t}*evaluate*state*avoid*{i+1}",
      conds := [Ps "s" "name" (ct t), P "s" "tried-tied-operator" [], P "s" "desired" (vt "d")] ++
        statePatConds a "s" p "x",
      acts := match avoidValue with
        | none => [mk "s" "partial-failure" (rv "d")]
        | some v => [mk "s" "expected-value" (ri v)] : Production }
  [{ path := "elaborations/problem-space.soar", kind := "FILE_OPERATOR", prods := [ps] },
   { path := "elaborations/ancestors.soar", kind := "FILE_OPERATOR", prods := anc },
   { path := "elaborations/state-evaluation.soar", kind := "FILE_OPERATOR", prods := dups ++ avoids }]

def rlFiles (a : Agent) (rewards : List (StatePat × Int)) : List GenFile :=
  let t := a.schema.task
  let tmpl := a.ops.map fun o =>
    let refs := o.params.flatMap fun (p, ty) =>
      ((a.schema.type? ty).map (fun x => (x.attrs.filter (fun d => !d.derived)).map fun d => (p, d.name))).getD []
    { name := s!"{t}*rl*{o.name}",
      conds := [Ps "s" "name" (ct t), Pacc "s" "operator" (vt "o")] ++ opWithParams "o" o.name o.params ++
        refConds refs [],
      acts := [.pref "s" (rv "o") .numericIndiff none (some (.int 0))],
      template := true : Production }
  let rw := (rewards.zip (List.range rewards.length)).map fun ((p, v), i) =>
    { name := s!"{t}*reward*{i+1}",
      conds := [Ps "s" "name" (ct t), P "s" "reward-link" (vt "r")] ++ statePatConds a "s" p "x",
      acts := [mk "r" "reward" (rv "w"), mk "w" "value" (ri v)] : Production }
  [{ path := "rl.soar", kind := "FILE_OPERATOR", prods := tmpl ++ rw }]

/-! ## The whole project -/

def firstload (a : Agent) : GenFile :=
  let holders := a.schema.stateAttrs.filter (·.multi)
  let multi := holders.map fun h => s!"multi-attributes {h.name} {(a.init.filter (·.1 == h.name)).length + 1}"
  let anc := match a.method with | .lookahead _ _ => ["multi-attributes ancestor 20"] | _ => []
  let chunk (ss : List String) := ["chunk always", "chunk add-osk on"] ++
    ss.map fun x => s!"chunk singleton any {x} any"
  let rl (r d : Nat) := ["rl --set learning on", s!"rl --set learning-rate {Float.ofNat r / 1000}",
    s!"rl --set discount-rate {Float.ofNat d / 1000}", "indifferent-selection --epsilon-greedy"]
  let learn := match a.learning with
    | .none => ["chunk never"]
    | .chunk ss => chunk ss
    | .rl r d => ["chunk never"] ++ rl r d
    | .chunkRl ss r d => chunk ss ++ rl r d
  { path := "_firstload.soar", kind := "FILE_OPERATOR", cmds := learn ++ multi ++ anc }

def compile (a : Agent) : List GenFile :=
  let base := [firstload a,
    { path := "elaborations/derived.soar", kind := "FILE_OPERATOR", prods := deriveProds a },
    { path := "elaborations/goal.soar", kind := "FILE_OPERATOR", prods := goalProds a },
    initFile a] ++ a.ops.flatMap (opFiles a)
  let m := match a.method with
    | .random => []
    | .tieHeuristic hs => tieFiles a hs
    | .lookahead av v => lookaheadFiles a av v
    | .rl rs => rlFiles a rs
  base ++ m

/-- Does the project need Soar's default selection library? -/
def needsSelection (a : Agent) : Bool := match a.method with | .lookahead _ _ => true | _ => false

end Agent
