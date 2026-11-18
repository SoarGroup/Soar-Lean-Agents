import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Tower of London (tower-of-london) (Tasks/webtasks/classic-ai/tower-of-london), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def towerOfLondon : Task where
  name := "tower-of-london"
  title := "Tower of London (tower-of-london)"
  statements := [
    (1, "There are three pegs. The first peg holds up to three balls, the second up to two, the third one."),
    (2, "There are three balls: red, green and blue."),
    (3, "At the start the first peg holds red at the bottom and green on top of it, the second peg holds blue, and the third peg is empty."),
    (4, "You can move the top ball of a peg onto another peg that is not full."),
    (5, "The goal is that the first peg holds blue at the bottom and red on top of it, and the second peg holds green."),
    (6, "Reach the goal in as few moves as possible.")]
  world := { handle := fun o => o.sym "name", rels := ["over", "of", "at"] }
  maintained := [
    { name := "empty", var := "x", stmts := [1, 4],
      defn := [.obj "x" none,
       .has "x" "kind" .eq (.val (.sym "space")),
       .none [.rel "at" [.var "b", .var "x"]]] }]
  ops := [
    { name := "move", params := [("b", some "ball"), ("t", some "slot")], stmts := [4]
      pre := [.rel "at" [.var "b", .var "src"],
       .rel "over" [.var "c", .var "src"],
       .rel "empty" [.var "c"],
       .rel "empty" [.var "t"],
       .rel "over" [.var "t", .var "u"],
       .rel "at" [.var "o", .var "u"],
       .rel "of" [.var "src", .var "p1"],
       .rel "of" [.var "t", .var "p2"],
       .distinct "p1" "p2"]
      bind := [.rel "at" [.var "b", .var "old"]]
      effects := [.change "at" [.var "b", .var "old"] 2 (.var "t"), .del "empty" [.var "t"], .add "empty" [.var "old"]]
      report := [.text "Move ", .handle "b", .text " to ", .handle "t"] }]
  goal := .ex [.rel "at" [.h "blue-ball", .h "a-low"],
     .rel "at" [.h "red-ball", .h "a-mid"],
     .rel "at" [.h "green-ball", .h "b-low"]]
  goalStmts := [5]
  assumptions := [
    { id := "A-TL1", kind := .intent, stmts := [1], text := "\"holds up to n balls\": a peg has n slots, stacked by an over relation from a floor; a ball is at a slot." },
    { id := "A-TL2", kind := .intent, stmts := [4], text := "\"the top ball\": a ball whose slot has an empty space over it. Each peg has a cap space over its top slot that is always empty and never a target, so the top slot needs no special case." },
    { id := "A-TL3", kind := .intent, stmts := [4], text := "\"onto a peg that is not full\": into the peg's lowest empty slot, i.e. an empty slot over a slot or floor that something is at. Each floor holds a fixed base object, which no action moves." },
    { id := "A-TL4", kind := .intent, stmts := [4], text := "\"another peg\": the target slot is of a different peg than the ball's slot." },
    { id := "A-TL5", kind := .intent, stmts := [6], text := "\"as few moves as possible\": unit cost per move, read through the library's search settings, not through the rules." }]

end WorldSpec.Tasks
