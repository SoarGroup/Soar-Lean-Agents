import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Guard tour (guard-tour) (Tasks/webtasks/classic-ai/guard-tour), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def guardTour : Task where
  name := "guard-tour"
  title := "Guard tour (guard-tour)"
  statements := [
    (1, "The world has three squares, A, B and C, in a row."),
    (2, "A guard robot is in square A."),
    (3, "The robot can move to a neighbouring square."),
    (4, "First the robot goes to square C, then back to square A, and finally to square B.")]
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
     .rel "at" [.var "g", .h "b"]]
  goalStmts := [4]
  assumptions := [
    { id := "A-G1", kind := .intent, stmts := [1, 3], text := "\"neighbouring\": a static next relation between A and B and between B and C, both ways." },
    { id := "A-G2", kind := .intent, stmts := [4], text := "The three stages are phases in order (L8-026); the goal field holds the last phase (used by the semantics checks)." }]
  phases := [
    { name := "at-c", stmts := [4],
      cond := .ex [.obj "g" (some "agent"),
       .rel "at" [.var "g", .h "c"]] },
    { name := "at-a", stmts := [4],
      cond := .ex [.obj "g" (some "agent"),
       .rel "at" [.var "g", .h "a"]] },
    { name := "at-b", stmts := [4],
      cond := .ex [.obj "g" (some "agent"),
       .rel "at" [.var "g", .h "b"]] }]

end WorldSpec.Tasks
