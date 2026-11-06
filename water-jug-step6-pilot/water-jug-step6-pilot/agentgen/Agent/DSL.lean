/-!
# Agent DSL v0 — a constrained description of Soar task agents

An agent is described here, not as productions. `Agent/Compile.lean` turns a description into
productions of the Soar specification (`Soar.Production`, Soar/Syntax.lean), and from there into
Soar source. The conventions of the English → Lean → Soar plan (5 November 2026) are built into
the types and into `Agent.check`:

* **Declared state schema.** Every object type and attribute is declared (`Schema`); which
  attributes are multi-valued, which are derived. Nothing else can be written or tested.
* **One operator template.** `Operator`: name, typed parameters, proposal guards, apply cases
  (guard + effects). Only operator application makes persistent changes.
* **Stratified elaborations.** Derived attributes (`Derive`) are computed only from
  non-derived attributes of the same object, so elaboration has a unique fixed point.
* **Restricted preferences.** No preference is written by hand: they come from the selection
  method (`Method`).
* **Sanctioned impasses only.** Operator no-change (`Impl.steps`: an operator carried out in a
  substate) and tie (`Method.tieHeuristic`, `Method.lookahead`). Any other impasse is a bug.
* **Explicit goals.** `Goal` becomes a standard `^desired` structure plus a success rule.
* **Fixed I/O protocol.** Not used by this family (no input or output link); reserved.
* **Escape hatch.** `Agent.raw`: productions written directly, outside the guarantees.

Common-sense knowledge an LLM adds beyond a task description is kept as named
`Assumption`s, separate from what the description states.
-/
namespace Agent

/-! ## Schema -/

/-- The type of an attribute's values. -/
inductive VType where
  | int
  | sym (choices : List String)
  | obj (ty : String)
  deriving DecidableEq, Repr

/-- One declared attribute. `derived` attributes are i-supported and computed by a `Derive`. -/
structure AttrDecl where
  name : String
  ty : VType
  multi : Bool := false
  derived : Bool := false
  doc : String := ""
  deriving DecidableEq, Repr

/-- An object type. `key` names an attribute that identifies an object of this type among its
siblings (used to compare whole states, e.g. for duplicate detection in look-ahead). -/
structure ObjType where
  name : String
  attrs : List AttrDecl
  key : Option String := none
  doc : String := ""
  deriving DecidableEq, Repr

structure Schema where
  /-- The task name, which is also the value of the top state's `^name`. -/
  task : String
  /-- Attributes of the task state. Objects of a type are reached through a multi-valued state
  attribute of that type. -/
  stateAttrs : List AttrDecl
  types : List ObjType
  deriving DecidableEq, Repr

/-! ## Expressions, guards, effects -/

/-- Integer expressions over attributes of named objects (operator parameters, or `self` in a
derivation). -/
inductive Expr where
  | lit (n : Int)
  | get (obj attr : String)
  | add (a b : Expr)
  | sub (a b : Expr)
  deriving DecidableEq, Repr

inductive Cmp where
  | eq | ne | lt | le | gt | ge
  deriving DecidableEq, Repr

/-- The right side of a comparison: Soar conditions can compare with a constant or with another
bound value, not with computed values. -/
inductive Atom where
  | lit (n : Int)
  | get (obj attr : String)
  deriving DecidableEq, Repr

inductive Guard where
  /-- `obj.attr op atom` -/
  | cmp (obj attr : String) (op : Cmp) (rhs : Atom)
  /-- two parameters denote different objects -/
  | distinct (a b : String)
  deriving DecidableEq, Repr

/-- `obj.attr := e` (a persistent change, made only when an operator is applied). All effects of
a case are simultaneous: every value on the right is read in the state before any change (Soar
binds right-hand-side values from the match). -/
structure Effect where
  obj : String
  attr : String
  val : Expr
  deriving DecidableEq, Repr

/-- One case of an operator's application: when the guard holds, make these changes. -/
structure Case where
  guard : List Guard := []
  effects : List Effect
  deriving DecidableEq, Repr

/-! ## Operators -/

/-- How an operator is carried out. `atomic`: by apply rules in the state where it is selected.
`steps`: in an operator no-change substate, by a fixed sequence of sub-operators; the last step
makes the operator's changes (as results). -/
inductive Impl where
  | atomic
  | steps (names : List String)
  deriving DecidableEq, Repr

structure Operator where
  name : String
  /-- (parameter, object type) -/
  params : List (String × String)
  propose : List Guard
  apply : List Case
  impl : Impl := .atomic
  doc : String := ""
  deriving DecidableEq, Repr

/-- A derived attribute: `T.attr := e`, with `e` over `self`. -/
structure Derive where
  ty : String
  attr : String
  val : Expr
  deriving DecidableEq, Repr

/-- An object pattern: attribute values that one object must have. -/
abbrev ObjPat := List (String × Int)

/-- A goal: some object of type `ty` has these attribute values. It becomes a `^desired` structure;
any state of the task with a matching object gets `^success`; at the top state that halts the
agent (a look-ahead copy reaching it only counts as a successful evaluation). -/
structure Goal where
  ty : String
  vals : ObjPat
  deriving DecidableEq, Repr

/-- A whole-state pattern: for each listed object pattern, some object of type `ty` matches it. -/
structure StatePat where
  ty : String
  objs : List ObjPat
  deriving DecidableEq, Repr

/-! ## Selection methods -/

inductive HVal where
  | best | worst | equal
  deriving DecidableEq, Repr

/-- A heuristic: when the last operator applied was one of `last` (`none` before the first),
candidates named in `cands` get `value`. -/
structure Heur where
  last : List String
  cands : List String
  value : HVal
  deriving DecidableEq, Repr

/-- How operators are chosen among the proposed ones. -/
inductive Method where
  /-- uniformly at random (all proposals indifferent) -/
  | random
  /-- tie impasse, resolved in a tie substate by evaluating each tied operator with heuristics:
  `best` becomes best + indifferent preferences, `worst` worst + indifferent, `equal`
  indifferent; Soar then chooses at random among the remaining equals. `check` requires exactly
  one heuristic for each (last operator or `none`, candidate). -/
  | tieHeuristic (hs : List Heur)
  /-- tie impasse, resolved by look-ahead search with Soar's default selection library; states
  equal to an ancestor state are partial failures; states matching `avoid` are partial failures,
  or, with `avoidValue`, get that numeric evaluation -/
  | lookahead (avoid : List StatePat) (avoidValue : Option Int := none)
  /-- reinforcement learning over operator and parameter-object attributes (RL templates with
  initial value 0), with rewards for states matching patterns, given whenever such a state holds
  (Soar's reward link). Algorithm and exploration are set by `Learning.rl`. A look-ahead variant
  with RL learning (`Learning.chunkRl`) needs no rewards: chunking over numeric evaluations makes
  the RL rules. -/
  | rl (rewards : List (StatePat × Int))
  deriving DecidableEq, Repr

/-- Learning. -/
inductive Learning where
  | none
  /-- `chunk always`; `singletons` are attributes declared singletons for chunking -/
  | chunk (singletons : List String)
  /-- `rl` on with these parameters (learning rate and discount ×1000) and epsilon-greedy
  exploration -/
  | rl (rate discount : Nat)  -- Soar's default RL algorithm (SARSA); epsilon-greedy, epsilon 0.1
  /-- both -/
  | chunkRl (singletons : List String) (rate discount : Nat)
  deriving DecidableEq, Repr

/-- Common-sense knowledge added to a description, kept separate and reviewable. -/
structure Assumption where
  id : String
  text : String
  /-- `accepted`, `rejected`, `revised`, or `open` -/
  status : String := "open"
  deriving DecidableEq, Repr

/-- A raw production (escape hatch): outside the conventions and their checks. -/
structure Raw where
  file : String
  text : String
  why : String
  deriving DecidableEq, Repr

/-- An agent. -/
structure Agent where
  schema : Schema
  /-- initial objects: (state attribute, attribute values) -/
  init : List (String × ObjPat)
  derive : List Derive
  ops : List Operator
  goal : Goal
  method : Method
  learning : Learning := .none
  assumptions : List Assumption := []
  raw : List Raw := []
  deriving Repr, DecidableEq

/-! ## The conventions as checks

`check a` lists every violation; a well-formed agent has none. Families state
`theorem … : check a = [] := by decide` for each variant, so a variant that breaks a convention
does not compile. -/

def Schema.type? (s : Schema) (t : String) : Option ObjType := s.types.find? (·.name == t)

def Schema.attr? (s : Schema) (t a : String) : Option AttrDecl :=
  (s.type? t).bind fun ty => ty.attrs.find? (·.name == a)

/-- The state attribute through which objects of type `t` are reached. -/
def Schema.holder? (s : Schema) (t : String) : Option AttrDecl :=
  s.stateAttrs.find? fun d => d.ty == .obj t && d.multi

def Expr.refs : Expr → List (String × String)
  | .lit _ => []
  | .get o a => [(o, a)]
  | .add a b => a.refs ++ b.refs
  | .sub a b => a.refs ++ b.refs

def Atom.refs : Atom → List (String × String)
  | .lit _ => []
  | .get o a => [(o, a)]

def Guard.refs : Guard → List (String × String)
  | .cmp o a _ r => (o, a) :: r.refs
  | .distinct _ _ => []

/-- `(obj, attr)` must name a parameter of `params` and an int attribute of its type. -/
def checkRef (s : Schema) (params : List (String × String)) (ctx : String) (r : String × String) :
    List String :=
  match params.find? (·.1 == r.1) with
  | none => [s!"{ctx}: {r.1} is not a parameter"]
  | some (_, t) =>
    match s.attr? t r.2 with
    | none => [s!"{ctx}: {t} has no attribute {r.2}"]
    | some d => if d.ty == .int then [] else [s!"{ctx}: {t}.{r.2} is not an integer"]

def checkGuard (s : Schema) (ps : List (String × String)) (ctx : String) (g : Guard) : List String :=
  match g with
  | .distinct a b =>
    (if ps.any (·.1 == a) then [] else [s!"{ctx}: {a} is not a parameter"]) ++
    (if ps.any (·.1 == b) then [] else [s!"{ctx}: {b} is not a parameter"])
  | g => g.refs.flatMap (checkRef s ps ctx)

def checkOp (s : Schema) (o : Operator) : List String :=
  let ctx := s!"operator {o.name}"
  let paramErrs := o.params.flatMap fun (p, t) =>
    match s.type? t, s.holder? t with
    | none, _ => [s!"{ctx}: parameter {p}: no type {t}"]
    | _, none => [s!"{ctx}: parameter {p}: no multi-valued state attribute holds {t}"]
    | _, _ => []
  let guardErrs := (o.propose ++ o.apply.flatMap (·.guard)).flatMap (checkGuard s o.params ctx)
  let effErrs := o.apply.flatMap (·.effects) |>.flatMap fun e =>
    checkRef s o.params ctx (e.obj, e.attr) ++ e.val.refs.flatMap (checkRef s o.params ctx) ++
    match (o.params.find? (·.1 == e.obj)).bind (fun (_, t) => s.attr? t e.attr) with
    | some d => if d.derived then [s!"{ctx}: effect writes derived attribute {e.attr}"] else []
    | none => []
  let reserved := ["evaluate-operator", "create-preferences", "initialize-" ++ s.task]
  let nameErr := if reserved.contains o.name then [s!"{ctx}: reserved name"] else []
  let implErr := match o.impl with
    | .atomic => []
    | .steps ns => if ns.isEmpty then [s!"{ctx}: no steps"] else
        if ns.eraseDups.length != ns.length then [s!"{ctx}: repeated step"] else []
  let caseErr := if o.apply.isEmpty then [s!"{ctx}: no apply case"] else []
  paramErrs ++ guardErrs ++ effErrs ++ nameErr ++ implErr ++ caseErr

def checkDerive (s : Schema) (d : Derive) : List String :=
  let ctx := s!"derive {d.ty}.{d.attr}"
  (match s.attr? d.ty d.attr with
   | none => [s!"{ctx}: undeclared"]
   | some a => if a.derived then [] else [s!"{ctx}: attribute is not declared derived"]) ++
  -- stratified: only non-derived attributes of the same object
  d.val.refs.flatMap fun (o, a) =>
    if o != "self" then [s!"{ctx}: refers to {o}"] else
    match s.attr? d.ty a with
    | none => [s!"{ctx}: {d.ty} has no attribute {a}"]
    | some x => if x.derived then [s!"{ctx}: depends on derived {a} (not stratified)"] else []

def checkObjPat (s : Schema) (t ctx : String) (p : ObjPat) : List String :=
  p.flatMap fun (a, _) =>
    match s.attr? t a with
    | none => [s!"{ctx}: {t} has no attribute {a}"]
    | some d => if d.ty == .int then [] else [s!"{ctx}: {t}.{a} is not an integer"]

def checkStatePat (s : Schema) (ctx : String) (p : StatePat) : List String :=
  (if (s.holder? p.ty).isSome then [] else [s!"{ctx}: no state attribute holds {p.ty}"]) ++
  p.objs.flatMap (checkObjPat s p.ty ctx)

def check (a : Agent) : List String :=
  let s := a.schema
  let opNames := a.ops.map (·.name)
  let dupOps := if opNames.eraseDups.length != opNames.length then ["repeated operator name"] else []
  let initErrs := a.init.flatMap fun (attr, vals) =>
    match s.stateAttrs.find? (·.name == attr) with
    | some { ty := .obj t, multi := true, .. } =>
      checkObjPat s t s!"init {attr}" vals ++
      ((s.type? t).map (fun ty => ty.attrs.filter (fun d => !d.derived && !vals.any (·.1 == d.name))
        |>.map fun d => s!"init {attr}: missing {d.name}")).getD []
    | _ => [s!"init: {attr} is not a multi-valued object attribute of the state"]
  let derivedCovered := s.types.flatMap fun t => t.attrs.filter (·.derived) |>.flatMap fun d =>
    if a.derive.any (fun x => x.ty == t.name && x.attr == d.name) then [] else
      [s!"derived {t.name}.{d.name} has no derivation"]
  let keyErrs := s.types.flatMap fun t => match t.key with
    | some k =>
      (if t.attrs.any (·.name == k) then [] else [s!"{t.name}: key {k} undeclared"]) ++
      -- key values are unique among the initial objects, and no operator changes the key
      (let ks := a.init.filterMap fun (h, vals) =>
          if (s.stateAttrs.find? (·.name == h)).map (·.ty) == some (.obj t.name) then vals.lookup k else none
       if ks.eraseDups.length == ks.length then [] else [s!"{t.name}: key {k} not unique initially"]) ++
      (a.ops.flatMap fun o => o.apply.flatMap (·.effects) |>.filterMap fun e =>
        if e.attr == k && (o.params.lookup e.obj) == some t.name then some s!"operator {o.name} changes key {k}" else none)
    | none => []
  let methodErrs := match a.method with
    | .random => []
    | .tieHeuristic hs =>
      (hs.flatMap fun h => (h.last ++ h.cands).flatMap fun n =>
        if n == "none" || opNames.contains n then [] else [s!"heuristic: no operator {n}"]) ++
      -- the evaluation is total and single-valued: exactly one heuristic for each
      -- (last operator, candidate)
      (("none" :: opNames).flatMap fun l => opNames.flatMap fun c =>
        match (hs.filter fun h => h.last.contains l && h.cands.contains c).length with
        | 1 => []
        | 0 => [s!"heuristic: nothing evaluates {c} after {l}"]
        | _ => [s!"heuristic: several values for {c} after {l}"])
    | .lookahead av _ => av.flatMap (checkStatePat s "avoid") ++
        (s.types.filter (fun t => (s.holder? t.name).isSome && t.key.isNone)).map
          (fun t => s!"look-ahead needs a key for {t.name}")
    | .rl rs => rs.flatMap (fun (p, _) => checkStatePat s "reward" p)
  let learnErrs := match a.method, a.learning with
    | .rl _, .rl _ _ | .rl _, .chunkRl _ _ _ => []
    | .rl _, _ => ["method rl needs rl learning"]
    | _, _ => []
  dupOps ++ a.ops.flatMap (checkOp s) ++ a.derive.flatMap (checkDerive s) ++ initErrs ++
    derivedCovered ++ keyErrs ++ checkObjPat s a.goal.ty "goal" a.goal.vals ++
    (if (s.holder? a.goal.ty).isSome then [] else ["goal: no state attribute holds the type"]) ++
    methodErrs ++ learnErrs

/-! ## Comparing two descriptions (round trip)

Used to compare a description with one re-formalized from its English: which parts differ.
Documentation strings and assumptions are not compared. -/

def Operator.core (o : Operator) : Operator := { o with doc := "" }
def Schema.core (s : Schema) : Schema :=
  { s with stateAttrs := s.stateAttrs.map ({ · with doc := "" }),
           types := s.types.map fun t => { t with doc := "", attrs := t.attrs.map ({ · with doc := "" }) } }

/-- The evaluation a heuristic list gives each (last operator or `none`, candidate): its meaning,
independent of how the entries are grouped or ordered. -/
def heurTable (ops : List String) (hs : List Heur) : List (String × String × Option HVal) :=
  ("none" :: ops).flatMap fun l => ops.map fun c =>
    (l, c, (hs.find? fun h => h.last.contains l && h.cands.contains c).map (·.value))

/-- Methods compared by meaning: tie heuristics by their table. -/
def methodEquiv (ops : List String) : Method → Method → Bool
  | .tieHeuristic h1, .tieHeuristic h2 => heurTable ops h1 == heurTable ops h2
  | m1, m2 => m1 == m2

def diffCore (a b : Agent) : List String :=
  (if a.schema.core == b.schema.core then [] else ["schema"]) ++
  (if a.init == b.init then [] else ["init"]) ++
  (if a.derive == b.derive then [] else ["derive"]) ++
  ((a.ops.zip b.ops).filterMap fun (x, y) => if x.core == y.core then none else some s!"operator {x.name}") ++
  (if a.ops.length == b.ops.length then [] else ["number of operators"]) ++
  (if a.goal == b.goal then [] else ["goal"]) ++
  (if methodEquiv (a.ops.map (·.name)) a.method b.method then [] else ["method"]) ++
  (if a.learning == b.learning then [] else ["learning"])

end Agent
