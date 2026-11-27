import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Three wizards (families, from English) (Tasks/webtasks/Families/wizards/english/wizards), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def wizardsEnglish : Task where
  name := "wizards"
  title := "Three wizards (families, from English)"
  statements := [
    (1, "Three wizards, A, B and C, sit where each can see the others but not himself."),
    (2, "Each has a spot on his forehead that is either white or black."),
    (3, "They are told that at least one spot is white."),
    (4, "They are asked in turn, A, then B, then C, whether they know the colour of their own spot."),
    (5, "Each can reason about what the others would have concluded from what they see and from the answers so far."),
    (6, "In this instance B and C have white spots and A has a black spot."),
    (7, "The goal is that a wizard correctly states the colour of his own spot.")]
  world := { handle := fun o => o.sym "name", rels := ["spot", "view-mate", "actual", "asks", "out-at", "says"] }
  derived := [
    { name := "all-black", vars := ["pw"], stmts := [3],
      defn := [.obj "pw" (some "world"),
       .none [.rel "spot" [.var "c", .var "pw", .h "white"]]] },
    { name := "live-at", vars := ["pw", "r"], stmts := [3, 4, 5],
      defn := [.obj "pw" (some "world"),
       .obj "r" (some "turn"),
       .none [.rel "out-at" [.var "pw", .var "earlier"], .has "earlier" "n" .lt (.prop "r" "n")]] },
    { name := "knows-at", vars := ["c", "pw", "r"], stmts := [1, 4, 5],
      defn := [.obj "c" (some "wizard"),
       .rel "live-at" [.var "pw", .var "r"],
       .none [.rel "view-mate" [.var "c", .var "pw", .var "w2"], .rel "live-at" [.var "w2", .var "r"]]] },
    { name := "answer-differs", vars := ["pw", "r"], stmts := [4, 5],
      defn := [.rel "live-at" [.var "pw", .var "r"],
       .rel "asks" [.var "r", .var "c"],
       .rel "actual" [.var "wa"],
       .rel "knows-at" [.var "c", .var "wa", .var "r"],
       .none [.rel "knows-at" [.var "c", .var "pw", .var "r"]]] },
    { name := "answer-differs-too", vars := ["pw", "r"], stmts := [4, 5],
      defn := [.rel "live-at" [.var "pw", .var "r"],
       .rel "asks" [.var "r", .var "c"],
       .rel "actual" [.var "wa"],
       .rel "knows-at" [.var "c", .var "pw", .var "r"],
       .none [.rel "knows-at" [.var "c", .var "wa", .var "r"]]] }]
  ops := [
    { name := "tell", params := [("t", some "stage")], stmts := [3]
      pre := [.has "t" "step" .eq (.val (.int 0))]
      bind := []
      effects := [.each [.rel "all-black" [.var "pw"]] (.add "out-at" [.var "pw", .h "told"]), .update "t" "step" (.plus (.prop "t" "step") (.val (.int 1)))]
      report := [.text "Told: at least one spot is white"]
      monotonic := true },
    { name := "ask", params := [("r", some "turn")], stmts := [4, 5, 7]
      pre := [.obj "t" (some "stage"),
       .has "t" "step" .eq (.prop "r" "n"),
       .has "r" "n" .gt (.val (.int 0))]
      bind := [.obj "t" (some "stage")]
      effects := [.each [.rel "actual" [.var "wa"],
         .rel "asks" [.var "r", .var "c"],
         .rel "knows-at" [.var "c", .var "wa", .var "r"],
         .rel "spot" [.var "c", .var "wa", .var "col"]] (.add "says" [.var "c", .var "col"]), .each [.rel "answer-differs" [.var "pw", .var "r"]] (.add "out-at" [.var "pw", .var "r"]), .each [.rel "answer-differs-too" [.var "pw", .var "r"]] (.add "out-at" [.var "pw", .var "r"]), .update "t" "step" (.plus (.prop "t" "step") (.val (.int 1)))]
      report := [.text "Ask, turn ", .prop "r" "n"]
      monotonic := true }]
  goal := .ex [.rel "says" [.var "c", .var "col"]]
  goalStmts := [7]
  assumptions := [
    { id := "A-WZ1", kind := .intent, stmts := [1, 2], text := "The eight possible patterns of spots are world objects (w-bww: A black, B white, C white); spot(c, w, colour) gives each wizard's colour in each world; view-mate(c, w, w2) holds when w2 differs from w only in c's own spot (what c cannot see). The actual world is w-bww." },
    { id := "A-WZ2", kind := .intent, stmts := [6], text := "\"B and C start marked, A unmarked\" in the description is read as B and C white and A black (marked = the colour the announcement is about)." },
    { id := "A-WZ3", kind := .intent, stmts := [1, 4, 5], text := "Knowledge is explicit: knows-at(c, w, r) holds when, in world w at turn r, no world c cannot tell from w is still possible. Derived relations use negation only in their definitions; operators test them positively." },
    { id := "A-WZ4", kind := .intent, stmts := [3, 4, 5], text := "The announcement and each turn are operators that rule out worlds (out-at(w, turn)). A world is live at turn r if it was not ruled out at an earlier turn. A stage number keeps the order; turn objects carry their number and asks(turn, wizard) says who is asked (A, B, C in that order)." },
    { id := "A-WZ5", kind := .intent, stmts := [4, 5, 7], text := "A turn records the asked wizard's answer in the actual world: if he knows, he states his colour (says(c, colour), the colour of his spot in the actual world, so it is correct). Every world where he would have answered differently is ruled out, since all hear the answer." },
    { id := "A-WZ6", kind := .intent, stmts := [7], text := "The goal is that some wizard has stated his colour. With A black, B and C white, A and B do not know and C states white at the third turn." }]

end WorldSpec.Tasks
