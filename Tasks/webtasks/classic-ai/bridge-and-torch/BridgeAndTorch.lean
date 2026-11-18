import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Bridge and torch (bridge-and-torch) (Tasks/webtasks/classic-ai/bridge-and-torch), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def bridgeAndTorch : Task where
  name := "bridge-and-torch"
  title := "Bridge and torch (bridge-and-torch)"
  statements := [
    (1, "Four people must cross a bridge at night. They start on the near side."),
    (2, "They have one torch. Anyone on the bridge must have the torch with them."),
    (3, "At most two people can be on the bridge at once."),
    (4, "Crossing takes Ann 1 minute, Bob 2 minutes, Cy 5 minutes and Di 10 minutes."),
    (5, "Two people crossing together go at the speed of the slower one."),
    (6, "One or two people on the side with the torch can cross with the torch to the other side."),
    (7, "The goal is that all four people are on the far side within 17 minutes.")]
  world := { handle := fun o => o.sym "name", rels := ["at", "other"] }
  ops := [
    { name := "cross-one", params := [("a", some "person"), ("to", some "bank")], stmts := [2, 4, 6]
      pre := [.obj "tc" (some "torch"),
       .rel "at" [.var "a", .var "from"],
       .rel "at" [.var "tc", .var "from"],
       .rel "other" [.var "from", .var "to"]]
      bind := [.obj "tc" (some "torch"),
       .obj "ck" (some "clock"),
       .rel "at" [.var "a", .var "old"],
       .rel "at" [.var "tc", .var "old"]]
      effects := [.change "at" [.var "a", .var "old"] 2 (.var "to"), .change "at" [.var "tc", .var "old"] 2 (.var "to"), .update "ck" "elapsed" (.plus (.prop "ck" "elapsed") (.prop "a" "minutes"))]
      report := [.handle "a", .text " crosses with the torch to ", .handle "to"]
      stepCost := some (.prop "a" "minutes") },
    { name := "cross-two", params := [("a", some "person"), ("b", some "person"), ("to", some "bank")], stmts := [2, 3, 4, 5, 6]
      pre := [.obj "tc" (some "torch"),
       .distinct "a" "b",
       .has "b" "minutes" .gt (.prop "a" "minutes"),
       .rel "at" [.var "a", .var "from"],
       .rel "at" [.var "b", .var "from"],
       .rel "at" [.var "tc", .var "from"],
       .rel "other" [.var "from", .var "to"]]
      bind := [.obj "tc" (some "torch"),
       .obj "ck" (some "clock"),
       .rel "at" [.var "a", .var "old"],
       .rel "at" [.var "b", .var "old"],
       .rel "at" [.var "tc", .var "old"]]
      effects := [.change "at" [.var "a", .var "old"] 2 (.var "to"), .change "at" [.var "b", .var "old"] 2 (.var "to"), .change "at" [.var "tc", .var "old"] 2 (.var "to"), .update "ck" "elapsed" (.plus (.prop "ck" "elapsed") (.prop "b" "minutes"))]
      report := [.handle "a", .text " and ", .handle "b", .text " cross with the torch to ", .handle "to"]
      stepCost := some (.prop "b" "minutes") }]
  goal := .all { outer := [], var := "x", type := "person", filter := [], body := [.rel "at" [.var "x", .h "far-side"]] }
  goalStmts := [7]
  failures := [
    { name := "over-17-minutes", stmts := [7],
      cond := .ex [.obj "ck" (some "clock"),
       .has "ck" "elapsed" .gt (.val (.int 17))] }]
  assumptions := [
    { id := "A-BT1", kind := .intent, stmts := [2, 6], text := "\"Anyone on the bridge must have the torch\": a crossing moves the torch with the people; the torch is at a side, like the people." },
    { id := "A-BT2", kind := .intent, stmts := [4, 5, 7], text := "Elapsed minutes are a number on a clock object, starting at 0; each crossing adds its time with the new update effect." },
    { id := "A-BT3", kind := .intent, stmts := [5], text := "\"at the speed of the slower one\": cross-two takes a faster person a and a slower person b (b.minutes > a.minutes) and adds b's minutes, so no maximum is needed and each pair is proposed once. All four times differ; equal times would need >= and would propose a pair twice." },
    { id := "A-BT4", kind := .intent, stmts := [1, 6], text := "\"the other side\": a static other relation between the two sides, both ways." },
    { id := "A-BT6", kind := .intent, stmts := [4, 7], text := "\"within 17 minutes\" asks for a fast crossing, so a crossing's minutes are also its step cost, and the task searches by cost (flags iterative-step cost, which brings cost-metric unit): iterative deepening on a cost cap, the library's IDA*. The clock still decides the losing state." },
    { id := "A-BT7", kind := .intent, stmts := [], text := "Search control, not from the English (as decided by JL on 16 Nov 2026 for the river crossings): a look-ahead state that returns to a situation already on its path fails. A situation is where each person and the torch are; the clock is not part of it, so going back and forth is cut off even though it changes the time." },
    { id := "A-BT5", kind := .intent, stmts := [7], text := "\"within 17 minutes\": more than 17 elapsed minutes is a losing state; the goal itself tests only where the people are." }]
  flags := [("iterative-step", "cost")]
  repeatControl := some { rel := "at", types := ["person", "torch"] }

end WorldSpec.Tasks
