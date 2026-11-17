import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Vacuum world (vacuum-world) (Tasks/webtasks/classic-ai/vacuum-world), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def vacuumWorld : Task where
  name := "vacuum-world"
  title := "Vacuum world (vacuum-world)"
  statements := [
    (1, "The world has two squares, Left and Right, side by side."),
    (2, "A vacuum cleaner is in the Left square. Both squares are dirty."),
    (3, "The vacuum can move to the other square."),
    (4, "The vacuum can suck, which makes the square it is in clean."),
    (5, "Each action costs one step."),
    (6, "The goal is that both squares are clean, in as few steps as possible.")]
  world := { handle := fun o => o.sym "name", rels := ["at", "dirty", "next"] }
  maintained := [
    { name := "clean", var := "x", stmts := [4, 6],
      defn := [.obj "x" (some "square"),
       .none [.rel "dirty" [.var "x"]]] }]
  ops := [
    { name := "move", params := [("to", some "square")], stmts := [3]
      pre := [.obj "v" (some "agent"),
       .rel "at" [.var "v", .var "cur"],
       .rel "next" [.var "cur", .var "to"]]
      bind := [.obj "v" (some "agent"),
       .rel "at" [.var "v", .var "old"]]
      effects := [.change "at" [.var "v", .var "old"] 2 (.var "to")]
      report := [.text "Move to ", .handle "to"] },
    { name := "suck", params := [("sq", some "square")], stmts := [4]
      pre := [.obj "v" (some "agent"),
       .rel "at" [.var "v", .var "sq"],
       .rel "dirty" [.var "sq"]]
      bind := []
      effects := [.del "dirty" [.var "sq"], .add "clean" [.var "sq"]]
      report := [.text "Suck in ", .handle "sq"] }]
  goal := .all { outer := [], var := "x", type := "square", filter := [], body := [.rel "clean" [.var "x"]] }
  goalStmts := [6]
  assumptions := [
    { id := "A-V1", kind := .intent, stmts := [1, 3], text := "\"the other square\": a static next relation holds between Left and Right in both directions." },
    { id := "A-V2", kind := .intent, stmts := [4, 6], text := "\"clean\" is \"not dirty\", kept as a maintained relation (it tests absence and decides the goal)." },
    { id := "A-V3", kind := .intent, stmts := [4], text := "Suck is proposed only in a dirty square: sucking a clean square changes nothing, so it is never part of a shortest plan." },
    { id := "A-V4", kind := .intent, stmts := [5, 6], text := "\"as few steps as possible\": unit cost per action, read through the library's search settings, not through the rules." }]

end WorldSpec.Tasks
