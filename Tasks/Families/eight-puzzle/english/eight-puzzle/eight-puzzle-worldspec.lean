import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Eight puzzle (families, from English) (Tasks/webtasks/Families/eight-puzzle/english/eight-puzzle), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def eightPuzzleEnglish : Task where
  name := "eight-puzzle"
  title := "Eight puzzle (families, from English)"
  statements := [
    (1, "A 3 x 3 tray holds eight numbered tiles and one empty square."),
    (2, "A tile next to the empty square (left, right, above or below, not diagonally) may slide into it, leaving its own square empty."),
    (3, "Tiles may not be lifted out."),
    (4, "The goal is to slide tiles until they match the target arrangement.")]
  world := { handle := fun o => o.sym "name", rels := ["at", "next-to"] }
  ops := [
    { name := "slide", params := [("t", some "tile"), ("to", some "square")], stmts := [2, 3]
      pre := [.obj "bl" (some "blank"),
       .rel "at" [.var "bl", .var "to"],
       .rel "at" [.var "t", .var "from"],
       .rel "next-to" [.var "from", .var "to"]]
      bind := [.obj "bl" (some "blank"),
       .rel "at" [.var "t", .var "old"],
       .rel "at" [.var "bl", .var "bold"]]
      effects := [.change "at" [.var "t", .var "old"] 2 (.var "to"), .change "at" [.var "bl", .var "bold"] 2 (.var "old")]
      report := [.text "Slide tile ", .handle "t", .text " into ", .handle "to"] }]
  goal := .ex [.rel "at" [.h "one", .h "top-left"],
     .rel "at" [.h "eight", .h "top-middle"],
     .rel "at" [.h "seven", .h "top-right"],
     .rel "at" [.h "two", .h "middle-left"],
     .rel "at" [.h "blank", .h "center"],
     .rel "at" [.h "six", .h "middle-right"],
     .rel "at" [.h "three", .h "bottom-left"],
     .rel "at" [.h "four", .h "bottom-middle"],
     .rel "at" [.h "five", .h "bottom-right"]]
  goalStmts := [4]
  assumptions := [
    { id := "A-EP1", kind := .intent, stmts := [1], text := "Nine square objects with names by position (top-left ... bottom-right) and a static next-to relation between squares that share a side, both ways (\"not diagonally\")." },
    { id := "A-EP2", kind := .intent, stmts := [1, 2], text := "The empty square is marked by a blank object that is at a square like a tile, so a slide swaps the squares of a tile and the blank. Tiles are named one ... eight." },
    { id := "A-EP3", kind := .intent, stmts := [3], text := "\"may not be lifted out\": slide is the only operator." },
    { id := "A-EP4", kind := .intent, stmts := [4], text := "The start and target arrangements are not in the English; they were read from the original agent's initialize rules (JL allowed this). The goal names the square of every tile and of the blank." },
    { id := "A-EP5", kind := .intent, stmts := [], text := "Search control, not from the English (as for the other WorldSpec search tasks): a look-ahead state that returns to a situation already on its path fails; a situation is where each tile and the blank are." }]
  repeatControl := some { rel := "at", types := ["tile", "blank"] }

end WorldSpec.Tasks
