import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Instant Insanity (instant-insanity) (Tasks/webtasks/classic-ai/instant-insanity), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def instantInsanity : Task where
  name := "instant-insanity"
  title := "Instant Insanity (instant-insanity)"
  statements := [
    (1, "There are four cubes. Each face of a cube is red, green, blue, white or yellow."),
    (2, "Each cube is given by its three pairs of opposite faces: cube 1: red and green, blue and white, red and yellow; cube 2: green and blue, yellow and red, white and white; cube 3: yellow and white, green and red, blue and blue; cube 4: blue and red, white and yellow, green and green."),
    (3, "You stack the four cubes in a column, each turned any way you like."),
    (4, "The column has four sides: front, back, left and right."),
    (5, "The goal is that each of the four sides of the column shows four different colours.")]
  world := { handle := fun o => o.sym "name", rels := ["orient", "placed"] }
  maintained := [
    { name := "unplaced", var := "x", stmts := [3],
      defn := [.obj "x" (some "cube"),
       .none [.rel "placed" [.var "x", .var "y"]]] }]
  ops := [
    { name := "place", params := [("c", some "cube"), ("o", some "orientation")], stmts := [3, 4]
      pre := [.rel "unplaced" [.var "c"],
       .rel "orient" [.var "o", .var "c"]]
      bind := []
      effects := [.add "placed" [.var "c", .var "o"], .del "unplaced" [.var "c"]]
      report := [.text "Place ", .handle "c", .text " turned as ", .handle "o"] }]
  goal := .all { outer := [], var := "x", type := "cube", filter := [], body := [.rel "placed" [.var "x", .var "o"]] }
  goalStmts := [3, 5]
  failures := [
    { name := "same-colour-front", stmts := [5],
      cond := .ex [.obj "c1" (some "cube"),
       .obj "c2" (some "cube"),
       .distinct "c1" "c2",
       .rel "placed" [.var "c1", .var "o1"],
       .rel "placed" [.var "c2", .var "o2"],
       .has "o1" "front" .eq (.prop "o2" "front")] },
    { name := "same-colour-back", stmts := [5],
      cond := .ex [.obj "c1" (some "cube"),
       .obj "c2" (some "cube"),
       .distinct "c1" "c2",
       .rel "placed" [.var "c1", .var "o1"],
       .rel "placed" [.var "c2", .var "o2"],
       .has "o1" "back" .eq (.prop "o2" "back")] },
    { name := "same-colour-left", stmts := [5],
      cond := .ex [.obj "c1" (some "cube"),
       .obj "c2" (some "cube"),
       .distinct "c1" "c2",
       .rel "placed" [.var "c1", .var "o1"],
       .rel "placed" [.var "c2", .var "o2"],
       .has "o1" "left" .eq (.prop "o2" "left")] },
    { name := "same-colour-right", stmts := [5],
      cond := .ex [.obj "c1" (some "cube"),
       .obj "c2" (some "cube"),
       .distinct "c1" "c2",
       .rel "placed" [.var "c1", .var "o1"],
       .rel "placed" [.var "c2", .var "o2"],
       .has "o1" "right" .eq (.prop "o2" "right")] }]
  assumptions := [
    { id := "A-II1", kind := .intent, stmts := [2, 3, 4], text := "\"turned any way you like\": each cube has one orientation object per distinct assignment of colours to the four sides (front, back, left, right); the top and bottom faces do not matter. Cube 1 has 24, cubes 2 to 4 have 16 (each has a pair of equal colours)." },
    { id := "A-II2", kind := .intent, stmts := [3, 5], text := "\"stack in a column\": where a cube is in the column does not matter (the goal and the losing conditions depend only on the colours each cube shows on the four sides), so placing a cube is choosing its orientation; cubes are placed one at a time, in any order. Until 24 Nov 2026 this entry fixed the order 1, 2, 3, 4 in the description; the generators now supply an order as search control (World-Conventions L21-001)." },
    { id := "A-II3", kind := .intent, stmts := [5], text := "\"four different colours\" on a side: two placed cubes showing the same colour on the same side is a losing state, so a partial column that cannot be completed is cut off at once." }]

end WorldSpec.Tasks
