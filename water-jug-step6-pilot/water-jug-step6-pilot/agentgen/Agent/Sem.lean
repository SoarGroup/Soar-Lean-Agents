import Agent.DSL
/-!
# Task-level meaning of a description

A small interpreter for the task a description defines, independent of Soar: states are the
objects' attribute values, an operator instance is an operator with objects for its parameters,
and applying it runs the first case whose guard holds. Used before any Soar is generated, to
check that the goal is reachable, how short a solution can be, and that invariants hold in every
reachable state. (These are properties of the task, not of the Soar agents; the generated agents
are compared with the originals separately.)
-/
namespace Agent

/-- An object: its holder attribute and its attribute values (derived ones included). -/
abbrev Obj := List (String × Int)
/-- A state: the objects, in a fixed order. -/
abbrev TState := List Obj

def Expr.eval (env : List (String × Obj)) : Expr → Int
  | .lit n => n
  | .get o a => ((env.lookup o).bind (·.lookup a)).getD 0
  | .add x y => x.eval env + y.eval env
  | .sub x y => x.eval env - y.eval env

def Atom.eval (env : List (String × Obj)) : Atom → Int
  | .lit n => n
  | .get o a => ((env.lookup o).bind (·.lookup a)).getD 0

def Cmp.holds : Cmp → Int → Int → Bool
  | .eq, a, b => a == b | .ne, a, b => a != b | .lt, a, b => a < b
  | .le, a, b => a ≤ b | .gt, a, b => a > b | .ge, a, b => a ≥ b

/-- `env` binds parameter names to object indices and their values. -/
def Guard.holds (env : List (String × (Nat × Obj))) : Guard → Bool
  | .cmp o a op r =>
    let e := env.map fun (p, (_, ob)) => (p, ob)
    op.holds (((env.lookup o).bind (·.2.lookup a)).getD 0) (r.eval e)
  | .distinct a b => (env.lookup a).map (·.1) != (env.lookup b).map (·.1)

/-- Recompute derived attributes of every object. -/
def Agent.derived (ag : Agent) (st : TState) : TState :=
  st.map fun ob =>
    let base := ob.filter fun (a, _) => !ag.derive.any (·.attr == a)
    base ++ ag.derive.map fun d => (d.attr, d.val.eval [("self", base)])

def Agent.initial (ag : Agent) : TState := ag.derived (ag.init.map (·.2))

/-- Parameter assignments: objects (by index) for each parameter in turn. -/
def assignments (st : TState) : List (String × String) → List (List (String × (Nat × Obj)))
  | [] => [[]]
  | (p, _) :: ps =>
    (assignments st ps).flatMap fun rest =>
      (List.range st.length).filterMap fun i => st[i]?.map fun ob => (p, (i, ob)) :: rest

/-- The states reachable in one operator application, each with the instance's label. -/
def Agent.succ (ag : Agent) (st : TState) : List (String × TState) :=
  ag.ops.flatMap fun o =>
    (assignments st o.params).filterMap fun env =>
      if o.propose.all (Guard.holds env) then
        (o.apply.find? fun c => c.guard.all (Guard.holds env)).map fun c =>
          let e := env.map fun (p, (_, ob)) => (p, ob)
          let st' := c.effects.foldl (fun s ef =>
            match env.lookup ef.obj with
            | some (i, _) => s.modify i fun ob =>
                (ob.filter (·.1 != ef.attr)) ++ [(ef.attr, ef.val.eval e)]
            | none => s) st
          (o.name ++ "(" ++ ",".intercalate (env.map fun (_, (i, _)) => toString i) ++ ")",
           ag.derived st')
      else none

def ObjPat.matches (p : ObjPat) (ob : Obj) : Bool := p.all fun (a, v) => ob.lookup a == some v

def Agent.isGoal (ag : Agent) (st : TState) : Bool := st.any ag.goal.vals.matches

/-- Normal form of a state for duplicate detection: objects with sorted attributes. -/
def norm (st : TState) : List (List (String × Int)) :=
  st.map fun ob => ob.mergeSort (fun a b => a.1 ≤ b.1)

/-- Breadth-first search to depth `n`: a shortest plan to the goal, if one exists within `n`
steps, and the number of distinct states seen. -/
def Agent.bfs (ag : Agent) (n : Nat) : Option (List String) × Nat :=
  let rec go : Nat → List (TState × List String) → List (List (List (String × Int))) →
      Option (List String) × Nat
    | 0, _, seen => (none, seen.length)
    | k + 1, frontier, seen =>
      match frontier.find? (fun (s, _) => ag.isGoal s) with
      | some (_, plan) => (some plan.reverse, seen.length)
      | none =>
        let (next, seen') := frontier.foldl (fun (acc, sn) (s, plan) =>
          (ag.succ s).foldl (fun (acc, sn) (lbl, s') =>
            if sn.contains (norm s') then (acc, sn) else (acc ++ [(s', lbl :: plan)], sn ++ [norm s']))
            (acc, sn)) ([], seen)
        if next.isEmpty then (none, seen'.length) else go k next seen'
  go n [(ag.initial, [])] [norm ag.initial]

/-- Every reachable state satisfies `inv`. `true` only if the search exhausts the state space
within `n` steps (otherwise `false`), so the result covers every reachable state. -/
def Agent.invariant (ag : Agent) (n : Nat) (inv : Obj → Bool) : Bool :=
  let rec go : Nat → List TState → List (List (List (String × Int))) → Bool
    | 0, fr, _ => fr.isEmpty
    | k + 1, fr, seen =>
      if !(fr.all (·.all inv)) then false else
      let (next, seen') := fr.foldl (fun (acc, sn) s =>
        (ag.succ s).foldl (fun (acc, sn) (_, s') =>
          if sn.contains (norm s') then (acc, sn) else (acc ++ [s'], sn ++ [norm s'])) (acc, sn))
        ([], seen)
      if next.isEmpty then true else go k next seen'
  go n [ag.initial] [norm ag.initial]

end Agent
