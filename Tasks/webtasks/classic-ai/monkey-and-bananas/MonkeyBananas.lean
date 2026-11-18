import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Monkey and bananas (monkey-and-bananas) (Tasks/webtasks/classic-ai/monkey-and-bananas), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def monkeyBananas : Task where
  name := "monkey-and-bananas"
  title := "Monkey and bananas (monkey-and-bananas)"
  statements := [
    (1, "There are three places in a room: A, B and C."),
    (2, "A monkey is at A. A box is at C. Bananas hang from the ceiling above B."),
    (3, "The monkey is on the floor."),
    (4, "The monkey can go from its place to another place if it is on the floor."),
    (5, "The monkey can push the box from its place to another place if the box is at the monkey's place and the monkey is on the floor. The monkey and the box both end at the new place."),
    (6, "The monkey can climb onto the box if the box is at the monkey's place and the monkey is on the floor."),
    (7, "The monkey can climb down from the box onto the floor."),
    (8, "The monkey can grasp the bananas if it is on the box and the box is at the place under the bananas."),
    (9, "The goal is that the monkey has the bananas.")]
  world := { handle := fun o => o.sym "name", rels := ["at", "on", "holds"] }
  ops := [
    { name := "go", params := [("to", some "location")], stmts := [4]
      pre := [.obj "m" (some "animal"),
       .rel "on" [.var "m", .h "floor"],
       .rel "at" [.var "m", .var "from"],
       .distinct "from" "to"]
      bind := [.obj "m" (some "animal"),
       .rel "at" [.var "m", .var "old"]]
      effects := [.change "at" [.var "m", .var "old"] 2 (.var "to")]
      report := [.text "Go to ", .handle "to"] },
    { name := "push", params := [("to", some "location")], stmts := [5]
      pre := [.obj "m" (some "animal"),
       .obj "bx" (some "box"),
       .rel "on" [.var "m", .h "floor"],
       .rel "at" [.var "m", .var "p"],
       .rel "at" [.var "bx", .var "p"],
       .distinct "p" "to"]
      bind := [.obj "m" (some "animal"),
       .obj "bx" (some "box"),
       .rel "at" [.var "m", .var "old"],
       .rel "at" [.var "bx", .var "old"]]
      effects := [.change "at" [.var "m", .var "old"] 2 (.var "to"), .change "at" [.var "bx", .var "old"] 2 (.var "to")]
      report := [.text "Push the box to ", .handle "to"] },
    { name := "climb-up", params := [("bx", some "box")], stmts := [6]
      pre := [.obj "m" (some "animal"),
       .rel "on" [.var "m", .h "floor"],
       .rel "at" [.var "m", .var "p"],
       .rel "at" [.var "bx", .var "p"]]
      bind := [.obj "m" (some "animal")]
      effects := [.change "on" [.var "m", .h "floor"] 2 (.var "bx")]
      report := [.text "Climb onto ", .handle "bx"] },
    { name := "climb-down", params := [("f", some "floor")], stmts := [7]
      pre := [.obj "m" (some "animal"),
       .obj "bx" (some "box"),
       .rel "on" [.var "m", .var "bx"]]
      bind := [.obj "m" (some "animal"),
       .obj "bx" (some "box"),
       .rel "on" [.var "m", .var "bx"]]
      effects := [.change "on" [.var "m", .var "bx"] 2 (.var "f")]
      report := [.text "Climb down onto ", .handle "f"] },
    { name := "grasp", params := [("fd", some "food")], stmts := [8]
      pre := [.obj "m" (some "animal"),
       .obj "bx" (some "box"),
       .rel "on" [.var "m", .var "bx"],
       .rel "at" [.var "bx", .var "p"],
       .rel "at" [.var "fd", .var "p"]]
      bind := [.obj "m" (some "animal")]
      effects := [.add "holds" [.var "m", .var "fd"]]
      report := [.text "Grasp ", .handle "fd"] }]
  goal := .ex [.obj "m" (some "animal"),
     .obj "fd" (some "food"),
     .rel "holds" [.var "m", .var "fd"]]
  goalStmts := [9]
  assumptions := [
    { id := "A-MB1", kind := .intent, stmts := [2, 8], text := "\"Bananas hang from the ceiling above B\": the bananas are at B, so \"the place under the bananas\" is the place the bananas are at." },
    { id := "A-MB2", kind := .intent, stmts := [3, 6, 7], text := "The floor is an object; being on the floor or on the box is an on relation from the monkey." },
    { id := "A-MB3", kind := .intent, stmts := [8, 9], text := "\"has the bananas\" is a holds relation from the monkey to the bananas, added by grasp." },
    { id := "A-MB4", kind := .intent, stmts := [4, 5, 6, 7, 8], text := "The actions are named go, push, climb-up, climb-down and grasp." }]

end WorldSpec.Tasks
