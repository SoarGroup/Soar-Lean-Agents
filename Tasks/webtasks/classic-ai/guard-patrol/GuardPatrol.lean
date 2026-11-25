import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Guard patrol (guard-patrol) (Tasks/webtasks/classic-ai/guard-patrol), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def guardPatrol : Task where
  name := "guard-patrol"
  title := "Guard patrol (guard-patrol)"
  statements := [
    (1, "The world has three squares, A, B and C, in a row."),
    (2, "A guard robot is in square A."),
    (3, "The robot can move to a neighbouring square."),
    (4, "The robot goes to square C, then back to square A, and repeats this three times.")]
  world := { handle := fun o => o.sym "name", rels := ["at", "next"] }
  ops := [
    { name := "move", params := [("to", some "square")], stmts := [3]
      pre := [.obj "g" (some "agent"),
       .rel "at" [.var "g", .var "cur"],
       .rel "next" [.var "cur", .var "to"]]
      bind := [.obj "g" (some "agent"),
       .rel "at" [.var "g", .var "old"]]
      effects := [.change "at" [.var "g", .var "old"] 2 (.var "to")]
      report := [.text "Move to ", .handle "to"] }]
  goal := .ex [.obj "g" (some "agent"),
     .rel "at" [.var "g", .h "a"]]
  goalStmts := [4]
  assumptions := [
    { id := "A-G1", kind := .intent, stmts := [1, 3], text := "\"neighbouring\": a static next relation between A and B and between B and C, both ways." },
    { id := "A-G2", kind := .intent, stmts := [4], text := "Going to C and back to A are two phases; repeats closes the loop back to the first (L8-027); three times is ^repeat-count 3 (L8-029)." }]
  phases := [
    { name := "at-c", stmts := [4],
      cond := .ex [.obj "g" (some "agent"),
       .rel "at" [.var "g", .h "c"]] },
    { name := "at-a", stmts := [4],
      cond := .ex [.obj "g" (some "agent"),
       .rel "at" [.var "g", .h "a"]] }]
  loopStart := some 0
  repeatCount := some 3

end WorldSpec.Tasks
