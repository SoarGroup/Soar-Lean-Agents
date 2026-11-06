import Agent.DSL
import Agent.Sem
/-!
# Water Jug — one parameterized description for the family

Derived on 5 November 2026 from the 20 Water Jug task agents in the agent library (water-jug V1–V3,
water-jug-RL, water-jug-tie V1/V3, water-jug-hierarchy V1–V4, water-jug-look-ahead V2–V4,
water-jug-look-ahead-RL, water-jug-look-ahead-failure-states, and the copies in Soar's own test
suites: FunctionalTests_testWaterJug, FunctionalTests_testWaterJugHierarchy,
ChunkingDemoTests_Demo_Water_Jug_{Tie,Hierarchy,Look_Ahead}).

They share one task (jugs of 3 and 5, both empty; get 1 into the 3) and differ in five ways,
which are the parameters here: how operators are chosen (`Method`), whether `fill` is carried
out in a substate, learning, the extra states look-ahead avoids, and how avoided states are
scored. Two originals are not replaced: water-jug V1 (RL templates with RL learning off, an
unfinished mix of the plain and RL versions) and water-jug-hierarchy V1 (`fill` has a
numeric-indifferent template and `pour` none; in Soar 9.6.5 it never pours and solves 0 of 20
runs). The rest of their differences (variable and attribute names, monitoring output, local
copies of the selection library) are not task differences and are dropped.
-/
namespace Agent.WaterJug

def jug : String := "jug"

def schema : Schema where
  task := "water-jug"
  stateAttrs := [{ name := "jug", ty := .obj "jug", multi := true, doc := "The jugs." }]
  types := [{
    name := "jug", key := some "volume",
    attrs := [
      { name := "volume", ty := .int, doc := "capacity" },
      { name := "contents", ty := .int, doc := "amount of water held" },
      { name := "free", ty := .int, derived := true, doc := "room left" }] }]

def g (o a : String) : Expr := .get o a

/-- The three task operators. `fillImpl` is how `fill` is carried out. -/
def ops (fillImpl : Impl) : List Operator := [
  { name := "fill", params := [("jug", jug)],
    propose := [.cmp "jug" "free" .gt (.lit 0)],
    apply := [{ effects := [{ obj := "jug", attr := "contents", val := g "jug" "volume" }] }],
    impl := fillImpl,
    doc := "Fill a jug from the source, to its volume." },
  { name := "empty", params := [("jug", jug)],
    propose := [.cmp "jug" "contents" .gt (.lit 0)],
    apply := [{ effects := [{ obj := "jug", attr := "contents", val := .lit 0 }] }],
    doc := "Pour a jug out onto the ground." },
  { name := "pour", params := [("from", jug), ("to", jug)],
    propose := [.distinct "from" "to", .cmp "to" "free" .gt (.lit 0), .cmp "from" "contents" .gt (.lit 0)],
    apply := [
      { guard := [.cmp "from" "contents" .gt (.get "to" "free")],
        effects := [{ obj := "from", attr := "contents", val := .sub (g "from" "contents") (g "to" "free") },
                    { obj := "to", attr := "contents", val := g "to" "volume" }] },
      { guard := [.cmp "from" "contents" .le (.get "to" "free")],
        effects := [{ obj := "from", attr := "contents", val := .lit 0 },
                    { obj := "to", attr := "contents", val := .add (g "to" "contents") (g "from" "contents") }] }],
    doc := "Pour one jug into another until the first is empty or the second is full." }]

/-- Recovered intent and common-sense knowledge, for review. -/
def assumptions : List Assumption := [
  { id := "A1", text := "Pouring moves as much water as fits: the amount is the smaller of the source's contents and the target's free room. (All originals; stated in code, not in any description.)" },
  { id := "A2", text := "Contents stay between 0 and the jug's volume. (Implied by the originals; checked here over every reachable state, `contents_in_range`.)" },
  { id := "A3", text := "The goal is that some jug of volume 3 holds 1, written as a `^desired` structure. Most originals tested for it directly in a rule, without `^desired`." },
  { id := "A4", text := "In the tie heuristic, `none` means before the first task operator; the initialize operator does not count as a last operator. (Checked: water-jug-tie behaves the same way, because its recording rule tests `^name water-jug`, which the initialize operator itself creates.)" },
  { id := "A5", text := "In hierarchical fill, pick-up, fill-jug and put-down are bookkeeping steps: only the last changes the task state (the jug's contents). The originals marked the jug itself (`^picked-up`, `^filled-jug`) as results; here the markers stay in the substate." },
  { id := "A6", text := "Look-ahead: a state is a duplicate of an ancestor when every jug has a jug in the ancestor with the same volume and contents. The originals compared exactly the 3- and 5-litre jugs." },
  { id := "A7", text := "Every variant halts when the goal is reached. (water-jug V2/V3 and all others did; the RL variant also gives its reward first.)" },
  { id := "A8", text := "Names: the derived room left is `free` (originals: `empty`, which is also an operator's name); pour's parameters are `from` and `to` (originals: `empty-jug`/`fill-jug`, or `jug`/`into`)." }]

/-- The tie heuristic of water-jug-tie: alternate pouring with filling or emptying. -/
def alternate : List Heur := [
  { last := ["none"], cands := ["fill", "empty", "pour"], value := .equal },
  { last := ["pour"], cands := ["fill", "empty"], value := .equal },
  { last := ["pour"], cands := ["pour"], value := .worst },
  { last := ["fill", "empty"], cands := ["pour"], value := .best },
  { last := ["fill", "empty"], cands := ["fill", "empty"], value := .worst }]

def full : StatePat := { ty := jug, objs := [[("volume", 3), ("contents", 3)], [("volume", 5), ("contents", 5)]] }
def emptyBoth : StatePat := { ty := jug, objs := [[("volume", 3), ("contents", 0)], [("volume", 5), ("contents", 0)]] }
def goalPat : StatePat := { ty := jug, objs := [[("volume", 3), ("contents", 1)]] }

/-- The family. -/
def mk (method : Method) (fillImpl : Impl := .atomic) (learning : Learning := .none) : Agent where
  schema := schema
  init := [("jug", [("volume", 3), ("contents", 0)]), ("jug", [("volume", 5), ("contents", 0)])]
  derive := [{ ty := jug, attr := "free", val := .sub (g "self" "volume") (g "self" "contents") }]
  ops := ops fillImpl
  goal := { ty := jug, vals := [("volume", 3), ("contents", 1)] }
  method := method
  learning := learning
  assumptions := assumptions

def hierarchical : Impl := .steps ["pick-up", "fill-jug", "put-down"]

/-- The variants: name, agent, and the originals each one replaces. -/
def variants : List (String × Agent × List String) := [
  ("water-jug", mk .random,
    ["water-jug V2", "water-jug V3", "FunctionalTests_testWaterJug V1"]),
  ("water-jug-rl", mk (.rl [(emptyBoth, -1), (goalPat, 1)]) .atomic (.rl 100 500),
    ["water-jug-RL V1"]),
  ("water-jug-tie", mk (.tieHeuristic alternate),
    ["water-jug-tie V1"]),
  ("water-jug-tie-chunk", mk (.tieHeuristic alternate) .atomic (.chunk ["contents", "volume"]),
    ["water-jug-tie V3", "ChunkingDemoTests_Demo_Water_Jug_Tie V1"]),
  ("water-jug-hierarchy", mk .random hierarchical,
    ["water-jug-hierarchy V2", "FunctionalTests_testWaterJugHierarchy V1"]),
  ("water-jug-hierarchy-chunk", mk .random hierarchical (.chunk []),
    ["water-jug-hierarchy V3", "water-jug-hierarchy V4", "ChunkingDemoTests_Demo_Water_Jug_Hierarchy V1"]),
  ("water-jug-look-ahead", mk (.lookahead []) .atomic (.chunk []),
    ["water-jug-look-ahead V2", "water-jug-look-ahead V3", "water-jug-look-ahead V4",
     "ChunkingDemoTests_Demo_Water_Jug_Look_Ahead V1"]),
  ("water-jug-look-ahead-failure-states", mk (.lookahead [full, emptyBoth]) .atomic (.chunk []),
    ["water-jug-look-ahead-failure-states V1"]),
  ("water-jug-look-ahead-rl", mk (.lookahead [full, emptyBoth] (some (-1))) .atomic (.chunkRl [] 100 500),
    ["water-jug-look-ahead-RL V1"])]

/-! ## Checks before any Soar is generated

`conventions` is checked by the kernel (`decide`). The task-level properties run the search of
`Agent/Sem.lean`, whose sorting is not reducible by the kernel, so they are checked by evaluation
(`native_decide`, which trusts the compiler: axiom `Lean.ofReduceBool`). -/

/-- Every variant obeys the conventions. -/
theorem conventions : variants.all (fun v => check v.2.1 == []) = true := by decide

/-- The task: the shortest solution has 4 operators (fill 3, pour into 5, fill 3, pour into 5). -/
theorem shortest : ((mk .random).bfs 8).1.map List.length = some 4 := by native_decide

/-- No shorter one: within 3 steps the goal is not reachable. -/
theorem none_shorter : ((mk .random).bfs 4).1 = none := by native_decide

/-- Contents stay within 0..volume in every reachable state (the search exhausts the state space
within 20 steps). -/
theorem contents_in_range :
    (mk .random).invariant 20 (fun o => match o.lookup "contents", o.lookup "volume" with
      | some c, some v => 0 ≤ c && c ≤ v | _, _ => false) = true := by native_decide

end Agent.WaterJug
