import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Muddy children (muddy-children) (Tasks/webtasks/classic-ai/muddy-children), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def muddyChildren : Task where
  name := "muddy-children"
  title := "Muddy children (muddy-children)"
  statements := [
    (1, "Three children are playing. Two of them, Amy and Ben, have mud on their foreheads; Cal does not."),
    (2, "Each child can see the other children's foreheads but not his or her own."),
    (3, "Their father says to all of them: \"At least one of you has mud on your forehead.\""),
    (4, "Then he asks, again and again: \"Do you know whether you have mud on your forehead?\" All the children answer at the same time, truthfully, \"yes\" or \"no\"."),
    (5, "Every child reasons perfectly and knows that the others do too, and every child hears every answer."),
    (6, "The goal is to find in which round each child first answers \"yes\", and why.")]
  world := { handle := fun o => o.sym "name", rels := ["muddy", "clean", "view-mate", "actual", "out-at", "said-yes"] }
  derived := [
    { name := "all-clean", vars := ["pw"], stmts := [3],
      defn := [.obj "pw" (some "world"),
       .none [.rel "muddy" [.var "c", .var "pw"]]] },
    { name := "live-at", vars := ["pw", "r"], stmts := [3, 4, 5],
      defn := [.obj "pw" (some "world"),
       .obj "r" (some "round"),
       .none [.rel "out-at" [.var "pw", .var "earlier"], .has "earlier" "n" .lt (.prop "r" "n")]] },
    { name := "knows-at", vars := ["c", "pw", "r"], stmts := [2, 4, 5],
      defn := [.obj "c" (some "child"),
       .rel "live-at" [.var "pw", .var "r"],
       .none [.rel "view-mate" [.var "c", .var "pw", .var "w2"], .rel "live-at" [.var "w2", .var "r"]]] },
    { name := "answers-differ", vars := ["pw", "r"], stmts := [4, 5],
      defn := [.rel "live-at" [.var "pw", .var "r"],
       .rel "actual" [.var "wa"],
       .obj "c" (some "child"),
       .rel "knows-at" [.var "c", .var "wa", .var "r"],
       .none [.rel "knows-at" [.var "c", .var "pw", .var "r"]]] },
    { name := "answers-differ-too", vars := ["pw", "r"], stmts := [4, 5],
      defn := [.rel "live-at" [.var "pw", .var "r"],
       .rel "actual" [.var "wa"],
       .obj "c" (some "child"),
       .rel "knows-at" [.var "c", .var "pw", .var "r"],
       .none [.rel "knows-at" [.var "c", .var "wa", .var "r"]]] }]
  ops := [
    { name := "father-speaks", params := [("t", some "stage")], stmts := [3]
      pre := [.has "t" "step" .eq (.val (.int 0))]
      bind := []
      effects := [.each [.rel "all-clean" [.var "pw"]] (.add "out-at" [.var "pw", .h "father-round"]), .update "t" "step" (.plus (.prop "t" "step") (.val (.int 1)))]
      report := [.text "Father: at least one of you has mud on your forehead"] },
    { name := "ask", params := [("r", some "round")], stmts := [4, 5]
      pre := [.obj "t" (some "stage"),
       .has "t" "step" .eq (.prop "r" "n"),
       .has "r" "n" .gt (.val (.int 0))]
      bind := [.obj "t" (some "stage")]
      effects := [.each [.rel "actual" [.var "wa"],
         .rel "knows-at" [.var "c", .var "wa", .var "r"]] (.add "said-yes" [.var "c", .var "r"]), .each [.rel "answers-differ" [.var "pw", .var "r"]] (.add "out-at" [.var "pw", .var "r"]), .each [.rel "answers-differ-too" [.var "pw", .var "r"]] (.add "out-at" [.var "pw", .var "r"]), .update "t" "step" (.plus (.prop "t" "step") (.val (.int 1)))]
      report := [.text "Father asks, round ", .prop "r" "n"] }]
  goal := .all { outer := [], var := "x", type := "child", filter := [], body := [.rel "said-yes" [.var "x", .var "y"]] }
  goalStmts := [6]
  assumptions := [
    { id := "A-MC1", kind := .intent, stmts := [1, 2], text := "The eight possible patterns of mud are world objects; muddy and clean say each child's forehead in each world; view-mate(c, w, w2) holds when w2 differs from w only on c's own forehead (what c cannot see). The actual world is w-mmc." },
    { id := "A-MC2", kind := .intent, stmts := [2, 4, 5], text := "Knowledge is explicit (JL, 16 Nov 2026): knows-at(c, w, r) holds when, in world w at round r, no world c cannot tell from w is still possible. It and the other derived relations use negation only in their definitions; operators test them positively." },
    { id := "A-MC3", kind := .intent, stmts := [3, 4, 5], text := "The father's statement and each round are operators that rule out worlds (out-at(w, round)), on every world at once. A world is live at round r if it was not ruled out in an earlier round, so each round is judged on the worlds left before it. A stage number keeps the order; round objects carry their number." },
    { id := "A-MC4", kind := .intent, stmts := [4], text := "A round records which children answer yes in the actual world (said-yes(c, r)), and rules out every world where some child would answer differently than in the actual world (all answers are heard)." },
    { id := "A-MC5", kind := .intent, stmts := [6], text := "The goal is that every child has answered yes in some round; the rounds of first yes are read from said-yes. Four rounds are provided." }]
  learning := false
  learningReason := "With learning on seeds 1 and 2 do not finish within 300 s; without it every seed solves in 15 decisions. (Added 23 November 2026 by Claude, supervised by John E. Laird; an agent setting, not a statement of the puzzle; library v2.46 runs, seeds 1-3.)"

end WorldSpec.Tasks
