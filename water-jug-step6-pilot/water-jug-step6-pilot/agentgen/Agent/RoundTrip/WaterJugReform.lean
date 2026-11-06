import Agent.DSL

namespace Agent.Reform.WaterJug

open Agent

def schema : Schema :=
  { task := "water-jug"
    stateAttrs := [{ name := "jug", ty := .obj "jug", multi := true }]
    types := [
      { name := "jug"
        attrs := [
          { name := "volume", ty := .int },
          { name := "contents", ty := .int },
          { name := "free", ty := .int, derived := true }]
        key := some "volume" }] }

def init : List (String × ObjPat) :=
  [("jug", [("volume", 3), ("contents", 0)]),
   ("jug", [("volume", 5), ("contents", 0)])]

def derive : List Derive :=
  [{ ty := "jug", attr := "free", val := .sub (.get "self" "volume") (.get "self" "contents") }]

def fillOp (fillImpl : Impl) : Operator :=
  { name := "fill"
    params := [("jug", "jug")]
    propose := [.cmp "jug" "free" .gt (.lit 0)]
    apply := [{ guard := [], effects := [{ obj := "jug", attr := "contents", val := .get "jug" "volume" }] }]
    impl := fillImpl }

def emptyOp : Operator :=
  { name := "empty"
    params := [("jug", "jug")]
    propose := [.cmp "jug" "contents" .gt (.lit 0)]
    apply := [{ guard := [], effects := [{ obj := "jug", attr := "contents", val := .lit 0 }] }]
    impl := .atomic }

def pourOp : Operator :=
  { name := "pour"
    params := [("from", "jug"), ("to", "jug")]
    propose := [.distinct "from" "to",
                .cmp "to" "free" .gt (.lit 0),
                .cmp "from" "contents" .gt (.lit 0)]
    apply := [
      { guard := [.cmp "from" "contents" .gt (.get "to" "free")]
        effects := [
          { obj := "from", attr := "contents", val := .sub (.get "from" "contents") (.get "to" "free") },
          { obj := "to", attr := "contents", val := .get "to" "volume" }] },
      { guard := [.cmp "from" "contents" .le (.get "to" "free")]
        effects := [
          { obj := "from", attr := "contents", val := .lit 0 },
          { obj := "to", attr := "contents", val := .add (.get "to" "contents") (.get "from" "contents") }] }]
    impl := .atomic }

def goal : Goal := { ty := "jug", vals := [("volume", 3), ("contents", 1)] }

def hierarchical : Impl := .steps ["pick-up", "fill-jug", "put-down"]

def full : StatePat :=
  { ty := "jug", objs := [[("volume", 3), ("contents", 3)], [("volume", 5), ("contents", 5)]] }

def emptyBoth : StatePat :=
  { ty := "jug", objs := [[("volume", 3), ("contents", 0)], [("volume", 5), ("contents", 0)]] }

def goalPat : StatePat :=
  { ty := "jug", objs := [[("volume", 3), ("contents", 1)]] }

def alternate : List Heur :=
  [{ last := ["none"], cands := ["fill", "empty", "pour"], value := .equal },
   { last := ["pour"], cands := ["fill", "empty"], value := .equal },
   { last := ["pour"], cands := ["pour"], value := .worst },
   { last := ["fill", "empty"], cands := ["fill", "empty"], value := .worst },
   { last := ["fill", "empty"], cands := ["pour"], value := .best }]

def mk (method : Method) (fillImpl : Impl) (learning : Learning) : Agent :=
  { schema := schema
    init := init
    derive := derive
    ops := [fillOp fillImpl, emptyOp, pourOp]
    goal := goal
    method := method
    learning := learning
    assumptions := []
    raw := [] }

def variants : List (String × Agent) :=
  [("water-jug", mk .random .atomic .none),
   ("water-jug-rl", mk (.rl [(emptyBoth, -1), (goalPat, 1)]) .atomic (.rl 100 500)),
   ("water-jug-tie", mk (.tieHeuristic alternate) .atomic .none),
   ("water-jug-tie-chunk", mk (.tieHeuristic alternate) .atomic (.chunk ["contents", "volume"])),
   ("water-jug-hierarchy", mk .random hierarchical .none),
   ("water-jug-hierarchy-chunk", mk .random hierarchical (.chunk [])),
   ("water-jug-look-ahead", mk (.lookahead []) .atomic (.chunk [])),
   ("water-jug-look-ahead-failure-states", mk (.lookahead [full, emptyBoth]) .atomic (.chunk [])),
   ("water-jug-look-ahead-rl", mk (.lookahead [full, emptyBoth] (some (-1))) .atomic (.chunkRl [] 100 500))]

theorem conventions : variants.all (fun v => check v.2 == []) = true := by decide

end Agent.Reform.WaterJug
