import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Cheryl's birthday (cheryls-birthday) (Tasks/webtasks/classic-ai/cheryls-birthday), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def cherylsBirthday : Task where
  name := "cheryls-birthday"
  title := "Cheryl's birthday (cheryls-birthday)"
  statements := [
    (1, "Albert and Bernard want to know Cheryl's birthday. Cheryl gives them ten possible dates: May 15, May 16, May 19, June 17, June 18, July 14, July 16, August 14, August 15, August 17."),
    (2, "Cheryl tells Albert only the month and tells Bernard only the day."),
    (3, "Albert says: \"I don't know when Cheryl's birthday is, but I know that Bernard doesn't know either.\""),
    (4, "Bernard says: \"At first I didn't know when Cheryl's birthday is, but I know now.\""),
    (5, "Albert says: \"Then I also know when Cheryl's birthday is.\""),
    (6, "Each statement is true, and each speaker reasons perfectly."),
    (7, "The goal is to find Cheryl's birthday.")]
  world := { handle := fun o => o.sym "name", rels := ["out3", "out4", "out5", "answer"] }
  derived := [
    { name := "albert-would-know", vars := ["d"], stmts := [2, 3],
      defn := [.obj "d" (some "date"),
       .none [.obj "d2" (some "date"), .distinct "d" "d2", .has "d2" "month" .eq (.prop "d" "month")]] },
    { name := "bernard-would-know", vars := ["d"], stmts := [2, 3, 4],
      defn := [.obj "d" (some "date"),
       .none [.obj "d2" (some "date"), .distinct "d" "d2", .has "d2" "day" .eq (.prop "d" "day")]] },
    { name := "bernard-might-know", vars := ["d"], stmts := [3],
      defn := [.obj "d" (some "date"),
       .obj "d2" (some "date"),
       .has "d2" "month" .eq (.prop "d" "month"),
       .rel "bernard-would-know" [.var "d2"]] },
    { name := "left-after-3", vars := ["d"], stmts := [3],
      defn := [.obj "d" (some "date"),
       .none [.rel "out3" [.var "d"]]] },
    { name := "bernard-unsure-after-3", vars := ["d"], stmts := [4],
      defn := [.rel "left-after-3" [.var "d"],
       .rel "left-after-3" [.var "d2"],
       .distinct "d" "d2",
       .has "d2" "day" .eq (.prop "d" "day")] },
    { name := "left-after-4", vars := ["d"], stmts := [4],
      defn := [.rel "left-after-3" [.var "d"],
       .none [.rel "out4" [.var "d"]]] },
    { name := "albert-unsure-after-4", vars := ["d"], stmts := [5],
      defn := [.rel "left-after-4" [.var "d"],
       .rel "left-after-4" [.var "d2"],
       .distinct "d" "d2",
       .has "d2" "month" .eq (.prop "d" "month")] },
    { name := "left-after-5", vars := ["d"], stmts := [5],
      defn := [.rel "left-after-4" [.var "d"],
       .none [.rel "out5" [.var "d"]]] },
    { name := "only-date", vars := ["d"], stmts := [7],
      defn := [.rel "left-after-5" [.var "d"],
       .none [.rel "left-after-5" [.var "d2"], .distinct "d" "d2"]] }]
  ops := [
    { name := "statement-3", params := [("t", some "stage")], stmts := [3, 6]
      pre := [.has "t" "step" .eq (.val (.int 1))]
      bind := []
      effects := [.each [.rel "albert-would-know" [.var "d"]] (.add "out3" [.var "d"]), .each [.rel "bernard-might-know" [.var "d"]] (.add "out3" [.var "d"]), .update "t" "step" (.plus (.prop "t" "step") (.val (.int 1)))]
      report := [.text "Statement 3 rules out the dates in months where Albert would know, or where Bernard might know"]
      monotonic := true },
    { name := "statement-4", params := [("t", some "stage")], stmts := [4, 6]
      pre := [.has "t" "step" .eq (.val (.int 2))]
      bind := []
      effects := [.each [.rel "left-after-3" [.var "d"],
         .rel "bernard-would-know" [.var "d"]] (.add "out4" [.var "d"]), .each [.rel "bernard-unsure-after-3" [.var "d"]] (.add "out4" [.var "d"]), .update "t" "step" (.plus (.prop "t" "step") (.val (.int 1)))]
      report := [.text "Statement 4 rules out the dates where Bernard would have known at first, or would still not know"]
      monotonic := true },
    { name := "statement-5", params := [("t", some "stage")], stmts := [5, 6]
      pre := [.has "t" "step" .eq (.val (.int 3))]
      bind := []
      effects := [.each [.rel "albert-unsure-after-4" [.var "d"]] (.add "out5" [.var "d"]), .update "t" "step" (.plus (.prop "t" "step") (.val (.int 1)))]
      report := [.text "Statement 5 rules out the dates where Albert would still not know"]
      monotonic := true },
    { name := "answer", params := [("d", some "date")], stmts := [7]
      pre := [.obj "t" (some "stage"),
       .has "t" "step" .eq (.val (.int 4)),
       .rel "only-date" [.var "d"]]
      bind := [.obj "t" (some "stage")]
      effects := [.add "answer" [.var "d"], .update "t" "step" (.plus (.prop "t" "step") (.val (.int 1)))]
      report := [.text "Cheryl's birthday is ", .prop "d" "month", .text " ", .prop "d" "day"]
      monotonic := true }]
  goal := .ex [.rel "answer" [.var "x"]]
  goalStmts := [7]
  assumptions := [
    { id := "A-CB1", kind := .intent, stmts := [1, 2], text := "The ten dates are date objects with a month and a day. Who was told what is not stored: \"Albert would know\" is read over every date, as if Albert had been told that date's month." },
    { id := "A-CB2", kind := .intent, stmts := [3, 4, 5, 6], text := "Knowledge is explicit (JL, 16 Nov 2026): derived relations, recomputed in every world, say for which dates a speaker would or would not know; operators test them positively. Their definitions use negation (\"no other date has that day\"), which is allowed only there." },
    { id := "A-CB3", kind := .intent, stmts := [3, 4, 5], text := "Each statement is an operator that marks, on every date at once (an each effect), the dates where the statement would be false (out3, out4, out5). Marks are added, never removed, so each statement is judged on the dates left before it. A stage number keeps the statements in order." },
    { id := "A-CB4", kind := .intent, stmts := [3], text := "\"I know that Bernard doesn't know\": rules out every date in a month that has a date whose day is unique among all ten (Bernard might know). \"I don't know\": rules out dates in a month with one date (none here)." },
    { id := "A-CB5", kind := .intent, stmts := [4], text := "\"At first I didn't know\": rules out dates with a unique day among all ten (already gone after statement 3). \"I know now\": rules out dates whose day is shared by another date left after statement 3." },
    { id := "A-CB6", kind := .intent, stmts := [5, 7], text := "\"Then I also know\": rules out dates whose month is shared by another date left after statement 4. The answer is the one date left; with more than one left, no answer is proposed." }]
  learning := false
  learningReason := "With learning on (the library default) no seed finishes within 300 s; without it the agent finds July 16 in 15 decisions on every seed. (Added 23 November 2026 by Claude, supervised by John E. Laird; an agent setting, not a statement of the puzzle; library v2.46 runs, seeds 1-3.)"

end WorldSpec.Tasks
