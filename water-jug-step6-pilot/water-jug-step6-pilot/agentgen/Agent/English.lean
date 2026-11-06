import Agent.DSL
/-!
# Template English for a description

One fixed sentence form per construct, so the English follows the Lean exactly; an LLM may
smooth it afterwards (blind to any original description), but each sentence here is the
reference. Formal points that fluent prose tends to hide are said explicitly: which attributes
are derived (and so retract), that an operator's changes are simultaneous, and when the agent
stops.
-/
namespace Agent

def Expr.en : Expr → String
  | .lit n => toString n
  | .get o a => s!"{o}.{a}"
  | .add x y => s!"{x.en} + {y.en}"
  | .sub x y => s!"{x.en} − {y.en}"

def Cmp.en : Cmp → String
  | .eq => "=" | .ne => "≠" | .lt => "<" | .le => "≤" | .gt => ">" | .ge => "≥"

def Atom.en : Atom → String
  | .lit n => toString n
  | .get o a => s!"{o}.{a}"

def Guard.en : Guard → String
  | .cmp o a op r => s!"{o}.{a} {op.en} {r.en}"
  | .distinct a b => s!"{a} and {b} are different objects"

def guardsEn (gs : List Guard) : String :=
  if gs.isEmpty then "always" else " and ".intercalate (gs.map Guard.en)

def ObjPat.en (p : ObjPat) : String :=
  " and ".intercalate (p.map fun (k, v) => s!"{k} {v}")

def StatePat.en (p : StatePat) : String :=
  "; ".intercalate (p.objs.map fun o => s!"a {p.ty} with {ObjPat.en o}")

def VType.en : VType → String
  | .int => "an integer"
  | .sym cs => "one of " ++ ", ".intercalate cs
  | .obj t => s!"a {t}"

def HVal.en : HVal → String
  | .best => "best" | .worst => "worst" | .equal => "neutral (indifferent)"

def english (a : Agent) : String := Id.run do
  let s := a.schema
  let mut out : List String := [s!"# {s.task}", "", "## The task", ""]
  -- schema
  for h in s.stateAttrs do
    out := out ++ [s!"The task state holds {if h.multi then "several values of" else "one value of"} " ++
      s!"`{h.name}`, each {h.ty.en}." ++ (if h.doc.isEmpty then "" else " " ++ h.doc)]
  for t in s.types do
    let base := t.attrs.filter (!·.derived)
    let der := t.attrs.filter (·.derived)
    out := out ++ ["", s!"A {t.name} has " ++ ", ".intercalate (base.map fun d => s!"`{d.name}` ({d.ty.en})") ++ "." ++
      (if t.doc.isEmpty then "" else " " ++ t.doc)]
    for d in der do
      match a.derive.find? (fun x => x.ty == t.name && x.attr == d.name) with
      | some x => out := out ++ [s!"Its `{d.name}` is derived: {x.val.en} (with `self` the {t.name}). " ++
          "It is recomputed whenever those values change and is never set directly."]
      | none => pure ()
  out := out ++ ["", "Initially the task state has:"]
  for (h, vals) in a.init do
    out := out ++ [s!"- a `{h}` with {ObjPat.en vals}"]
  out := out ++ ["", s!"**Goal.** Some {a.goal.ty} has {ObjPat.en a.goal.vals}. " ++
    "When the goal holds in the task state, the agent reports success and halts."]
  -- operators
  out := out ++ ["", "## Operators", "",
    "An operator's changes are made together: every value on the right is read before any change."]
  for o in a.ops do
    let ps := ", ".intercalate (o.params.map fun (p, t) => s!"{p}: {t}")
    out := out ++ ["", s!"**{o.name}({ps}).** Proposed when {guardsEn o.propose}." ++
      (if o.doc.isEmpty then "" else " " ++ o.doc)]
    for c in o.apply do
      let eff := "; ".intercalate (c.effects.map fun e => s!"{e.obj}.{e.attr} := {e.val.en}")
      out := out ++ [if c.guard.isEmpty then s!"- Effect: {eff}." else s!"- If {guardsEn c.guard}: {eff}."]
    match o.impl with
    | .atomic => pure ()
    | .steps ns => out := out ++ [s!"- Carried out in its own substate by the steps " ++
        ", ".intercalate ns ++ ", in that order; the last step makes the changes above."]
  -- selection
  out := out ++ ["", "## Choosing among proposed operators", ""]
  match a.method with
  | .random => out := out ++ ["Any proposed operator may be chosen; the choice is random."]
  | .tieHeuristic hs =>
    out := out ++ ["When several operators are proposed, the agent evaluates each one in a tie " ++
      "substate, from the operator applied last (`none` before the first task operator):"]
    for h in hs do
      out := out ++ [s!"- after {" or ".intercalate h.last}: {" or ".intercalate h.cands} is {h.value.en}"]
    out := out ++ ["Best is chosen over neutral over worst; ties among equals are broken at random."]
  | .lookahead av v =>
    out := out ++ ["When several operators are proposed, the agent tries each one in an internal " ++
      "copy of the state (look-ahead search, Soar's default selection library) and prefers those " ++
      "that lead to the goal. A state equal to one on the path from the task state is a failure " ++
      "for that path."]
    for p in av do
      out := out ++ [s!"- A state with {p.en} is " ++
        (match v with | none => "a (partial) failure." | some x => s!"given the value {x}.")]
  | .rl rs =>
    out := out ++ ["The agent learns by reinforcement which operator to choose, from the operator " ++
      "and the attribute values of its parameter objects. Rewards:"]
    for (p, r) in rs do
      out := out ++ [s!"- {r} for a state with {p.en}"]
  out := out ++ ["", "## Learning", "",
    match a.learning with
    | .none => "None."
    | .chunk ss => "Chunking on (`chunk always`)" ++
        (if ss.isEmpty then "." else s!"; singletons for chunking: {", ".intercalate ss}.")
    | .rl r d => s!"Reinforcement learning on: learning rate {Float.ofNat r / 1000}, discount {Float.ofNat d / 1000}, epsilon-greedy exploration."
    | .chunkRl ss r d => s!"Chunking on (`chunk always`)" ++
        (if ss.isEmpty then "" else s!", singletons {", ".intercalate ss}") ++
        s!"; reinforcement learning on: learning rate {Float.ofNat r / 1000}, discount {Float.ofNat d / 1000}, epsilon-greedy exploration."]
  if !a.assumptions.isEmpty then
    out := out ++ ["", "## Assumptions (added; not in the task description)", ""]
    for x in a.assumptions do
      out := out ++ [s!"- **{x.id}** [{x.status}] {x.text}"]
  if !a.raw.isEmpty then
    out := out ++ ["", "## Outside the conventions (unverified)", ""]
    for r in a.raw do
      out := out ++ [s!"- `{r.file}`: {r.why}"]
  return "\n".intercalate out ++ "\n"

end Agent
