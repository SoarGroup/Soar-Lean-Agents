import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Water jug (families, from English) (Tasks/webtasks/Families/water-jug/english/water-jug), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def waterJugEnglish : Task where
  name := "water-jug"
  title := "Water jug (families, from English)"
  statements := [
    (1, "You have two unmarked jugs, one holding 3 gallons and one holding 5 gallons, both empty, and an unlimited supply of water."),
    (2, "In one step you may fill a jug completely or empty a jug completely."),
    (3, "In one step you may pour from one jug into the other until the receiving jug is full or the pouring jug is empty."),
    (4, "The goal is to end with exactly 1 gallon in the 3-gallon jug.")]
  world := { handle := fun o => o.sym "name", rels := [] }
  ops := [
    { name := "fill", params := [("j", some "jug")], stmts := [1, 2]
      pre := [.has "j" "room" .gt (.val (.int 0))]
      bind := []
      effects := [.update "j" "amount" (.prop "j" "capacity"), .update "j" "room" (.val (.int 0))]
      report := [.text "Fill the ", .handle "j", .text " jug"] },
    { name := "empty", params := [("j", some "jug")], stmts := [2]
      pre := [.has "j" "amount" .gt (.val (.int 0))]
      bind := []
      effects := [.update "j" "amount" (.val (.int 0)), .update "j" "room" (.prop "j" "capacity")]
      report := [.text "Empty the ", .handle "j", .text " jug"] },
    { name := "pour-all", params := [("a", some "jug"), ("b", some "jug")], stmts := [3]
      pre := [.distinct "a" "b",
       .has "a" "amount" .gt (.val (.int 0)),
       .has "a" "amount" .le (.prop "b" "room")]
      bind := []
      effects := [.update "b" "amount" (.plus (.prop "b" "amount") (.prop "a" "amount")), .update "b" "room" (.minus (.prop "b" "room") (.prop "a" "amount")), .update "a" "amount" (.val (.int 0)), .update "a" "room" (.prop "a" "capacity")]
      report := [.text "Pour the ", .handle "a", .text " jug into the ", .handle "b", .text " jug until it is empty"] },
    { name := "pour-until-full", params := [("a", some "jug"), ("b", some "jug")], stmts := [3]
      pre := [.distinct "a" "b",
       .has "b" "room" .gt (.val (.int 0)),
       .has "a" "amount" .gt (.prop "b" "room")]
      bind := []
      effects := [.update "a" "amount" (.minus (.prop "a" "amount") (.prop "b" "room")), .update "a" "room" (.plus (.prop "a" "room") (.prop "b" "room")), .update "b" "amount" (.prop "b" "capacity"), .update "b" "room" (.val (.int 0))]
      report := [.text "Pour the ", .handle "a", .text " jug into the ", .handle "b", .text " jug until it is full"] }]
  goal := .ex [.obj "j" (some "jug"),
     .has "j" "capacity" .eq (.val (.int 3)),
     .has "j" "amount" .eq (.val (.int 1))]
  goalStmts := [4]
  assumptions := [
    { id := "A-WJ1", kind := .intent, stmts := [1], text := "Two jug objects, three-gallon and five-gallon, with a capacity and the amount of water in them (both 0 at the start). The supply of water is not an object: fill needs nothing." },
    { id := "A-WJ2", kind := .intent, stmts := [2, 3], text := "Pouring needs the amount that fits in the receiving jug, room = capacity - amount, in a condition, where arithmetic cannot be compiled; so each jug keeps room as a property beside its amount, and every operator updates both (with minus, added to WorldSpec 26 Nov 2026; the first version kept negated copies of the amounts, since WorldSpec then had only addition)." },
    { id := "A-WJ3", kind := .intent, stmts := [3], text := "\"until the receiving jug is full or the pouring jug is empty\": two operators. pour-all when the pouring jug's amount fits in the room of the other (the pouring jug ends empty); pour-until-full when it is more than the room (the receiving jug ends full and the rest stays behind)." },
    { id := "A-WJ4", kind := .intent, stmts := [2], text := "Filling a full jug or emptying an empty one changes nothing, so fill needs room in the jug and empty needs water in it." },
    { id := "A-WJ5", kind := .intent, stmts := [], text := "No repeated-situation control: it compares relations, and the amounts are numbers on the jugs. The look-ahead's depth limit bounds the search." }]

end WorldSpec.Tasks
