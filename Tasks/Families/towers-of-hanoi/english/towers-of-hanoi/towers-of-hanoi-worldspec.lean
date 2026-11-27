import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Tower of Hanoi (families, from English) (Tasks/webtasks/Families/towers-of-hanoi/english/towers-of-hanoi), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def towersOfHanoiEnglish : Task where
  name := "towers-of-hanoi"
  title := "Tower of Hanoi (families, from English)"
  statements := [
    (1, "There are three pegs, A, B and C, and three disks of different sizes, all on peg A, largest at the bottom."),
    (2, "Move one disk at a time, taking only the top disk of a peg."),
    (3, "A disk is placed on an empty peg or on a larger disk; a disk may never rest on a smaller one."),
    (4, "The goal is to move the whole stack to another peg.")]
  world := { handle := fun o => o.sym "name", rels := ["on"] }
  derived := [
    { name := "top", vars := ["d", "p"], stmts := [2],
      defn := [.obj "d" (some "disk"),
       .rel "on" [.var "d", .var "p"],
       .none [.obj "e" (some "disk"), .rel "on" [.var "e", .var "p"], .has "e" "size" .lt (.prop "d" "size")]] },
    { name := "can-take", vars := ["q", "d"], stmts := [3],
      defn := [.obj "q" (some "peg"),
       .obj "d" (some "disk"),
       .none [.obj "f" (some "disk"), .rel "on" [.var "f", .var "q"], .has "f" "size" .lt (.prop "d" "size")]] }]
  ops := [
    { name := "move-disk", params := [("d", some "disk"), ("to", some "peg")], stmts := [2, 3]
      pre := [.rel "top" [.var "d", .var "from"],
       .rel "can-take" [.var "to", .var "d"],
       .distinct "from" "to"]
      bind := [.rel "on" [.var "d", .var "old"]]
      effects := [.change "on" [.var "d", .var "old"] 2 (.var "to")]
      report := [.text "Move disk ", .handle "d", .text " to peg ", .handle "to"] }]
  goal := .all { outer := [], var := "x", type := "disk", filter := [], body := [.rel "on" [.var "x", .h "c"]] }
  goalStmts := [4]
  assumptions := [
    { id := "A-TH1", kind := .intent, stmts := [1], text := "Each disk (small, medium, large) has a size (1, 2, 3) and an on relation to the peg it is on; the order within a peg follows from the sizes, since a disk never rests on a smaller one." },
    { id := "A-TH2", kind := .intent, stmts := [2], text := "\"the top disk of a peg\": the smallest disk on its peg (no smaller disk on the same peg), a derived relation top(disk, peg)." },
    { id := "A-TH3", kind := .intent, stmts := [3], text := "\"an empty peg or a larger disk\": the target peg has no disk smaller than the moved one (its top disk, if any, is larger), a derived relation can-take(peg, disk). Negations stay in derived relations, which the operators test positively (W-CHK-009)." },
    { id := "A-TH4", kind := .intent, stmts := [4], text := "\"another peg\": peg C, read from the original agent's initialize rules (the English does not name it; JL allowed reading initial states there)." },
    { id := "A-TH5", kind := .intent, stmts := [], text := "Search control, not from the English (as for the other WorldSpec search tasks): a look-ahead state that returns to a situation already on its path fails; a situation is where each disk is." }]
  repeatControl := some { rel := "on", types := ["disk"] }

end WorldSpec.Tasks
