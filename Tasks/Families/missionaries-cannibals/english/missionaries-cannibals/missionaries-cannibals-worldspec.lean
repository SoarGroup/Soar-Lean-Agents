import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Missionaries and cannibals (families, from English) (Tasks/webtasks/Families/missionaries-cannibals/english/missionaries-cannibals), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def missionariesCannibalsEnglish : Task where
  name := "missionaries-cannibals"
  title := "Missionaries and cannibals (families, from English)"
  statements := [
    (1, "Three missionaries and three cannibals stand on the left bank of a river with a rowing boat."),
    (2, "The boat carries one or two people and never crosses empty."),
    (3, "If, on either bank, the cannibals ever outnumber the missionaries who are there, the missionaries are eaten."),
    (4, "A bank with no missionaries is safe."),
    (5, "The goal is to get all six people to the right bank.")]
  world := { handle := fun o => o.sym "name", rels := ["at", "other", "side", "one-less", "two-less"] }
  ops := [
    { name := "cross-one-missionary", params := [("to", some "bank")], stmts := [2]
      pre := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "from"],
       .rel "other" [.var "from", .var "to"],
       .obj "mf" (some "group"),
       .has "mf" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mf", .var "from"],
       .obj "mt" (some "group"),
       .has "mt" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mt", .var "to"],
       .rel "at" [.var "mf", .var "mn"],
       .rel "one-less" [.var "mn", .var "mn1"],
       .rel "at" [.var "mt", .var "mk"],
       .rel "one-less" [.var "mk1", .var "mk"]]
      bind := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "bold"],
       .obj "mf" (some "group"),
       .has "mf" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mf", .var "bold"],
       .obj "mt" (some "group"),
       .has "mt" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mt", .var "to"],
       .rel "at" [.var "mf", .var "mold"],
       .rel "one-less" [.var "mold", .var "mnew"],
       .rel "at" [.var "mt", .var "mtold"],
       .rel "one-less" [.var "mtnew", .var "mtold"]]
      effects := [.change "at" [.var "mf", .var "mold"] 2 (.var "mnew"), .change "at" [.var "mt", .var "mtold"] 2 (.var "mtnew"), .change "at" [.var "bt", .var "bold"] 2 (.var "to")]
      report := [.text "One missionary rows the boat to the ", .handle "to", .text " bank"] },
    { name := "cross-two-missionaries", params := [("to", some "bank")], stmts := [2]
      pre := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "from"],
       .rel "other" [.var "from", .var "to"],
       .obj "mf" (some "group"),
       .has "mf" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mf", .var "from"],
       .obj "mt" (some "group"),
       .has "mt" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mt", .var "to"],
       .rel "at" [.var "mf", .var "mn"],
       .rel "two-less" [.var "mn", .var "mn1"],
       .rel "at" [.var "mt", .var "mk"],
       .rel "two-less" [.var "mk1", .var "mk"]]
      bind := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "bold"],
       .obj "mf" (some "group"),
       .has "mf" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mf", .var "bold"],
       .obj "mt" (some "group"),
       .has "mt" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mt", .var "to"],
       .rel "at" [.var "mf", .var "mold"],
       .rel "two-less" [.var "mold", .var "mnew"],
       .rel "at" [.var "mt", .var "mtold"],
       .rel "two-less" [.var "mtnew", .var "mtold"]]
      effects := [.change "at" [.var "mf", .var "mold"] 2 (.var "mnew"), .change "at" [.var "mt", .var "mtold"] 2 (.var "mtnew"), .change "at" [.var "bt", .var "bold"] 2 (.var "to")]
      report := [.text "Two missionaries row the boat to the ", .handle "to", .text " bank"] },
    { name := "cross-one-cannibal", params := [("to", some "bank")], stmts := [2]
      pre := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "from"],
       .rel "other" [.var "from", .var "to"],
       .obj "cf" (some "group"),
       .has "cf" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "cf", .var "from"],
       .obj "ct" (some "group"),
       .has "ct" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "ct", .var "to"],
       .rel "at" [.var "cf", .var "cn"],
       .rel "one-less" [.var "cn", .var "cn1"],
       .rel "at" [.var "ct", .var "ck"],
       .rel "one-less" [.var "ck1", .var "ck"]]
      bind := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "bold"],
       .obj "cf" (some "group"),
       .has "cf" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "cf", .var "bold"],
       .obj "ct" (some "group"),
       .has "ct" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "ct", .var "to"],
       .rel "at" [.var "cf", .var "cold"],
       .rel "one-less" [.var "cold", .var "cnew"],
       .rel "at" [.var "ct", .var "ctold"],
       .rel "one-less" [.var "ctnew", .var "ctold"]]
      effects := [.change "at" [.var "cf", .var "cold"] 2 (.var "cnew"), .change "at" [.var "ct", .var "ctold"] 2 (.var "ctnew"), .change "at" [.var "bt", .var "bold"] 2 (.var "to")]
      report := [.text "One cannibal rows the boat to the ", .handle "to", .text " bank"] },
    { name := "cross-two-cannibals", params := [("to", some "bank")], stmts := [2]
      pre := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "from"],
       .rel "other" [.var "from", .var "to"],
       .obj "cf" (some "group"),
       .has "cf" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "cf", .var "from"],
       .obj "ct" (some "group"),
       .has "ct" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "ct", .var "to"],
       .rel "at" [.var "cf", .var "cn"],
       .rel "two-less" [.var "cn", .var "cn1"],
       .rel "at" [.var "ct", .var "ck"],
       .rel "two-less" [.var "ck1", .var "ck"]]
      bind := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "bold"],
       .obj "cf" (some "group"),
       .has "cf" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "cf", .var "bold"],
       .obj "ct" (some "group"),
       .has "ct" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "ct", .var "to"],
       .rel "at" [.var "cf", .var "cold"],
       .rel "two-less" [.var "cold", .var "cnew"],
       .rel "at" [.var "ct", .var "ctold"],
       .rel "two-less" [.var "ctnew", .var "ctold"]]
      effects := [.change "at" [.var "cf", .var "cold"] 2 (.var "cnew"), .change "at" [.var "ct", .var "ctold"] 2 (.var "ctnew"), .change "at" [.var "bt", .var "bold"] 2 (.var "to")]
      report := [.text "Two cannibals row the boat to the ", .handle "to", .text " bank"] },
    { name := "cross-missionary-and-cannibal", params := [("to", some "bank")], stmts := [2]
      pre := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "from"],
       .rel "other" [.var "from", .var "to"],
       .obj "mf" (some "group"),
       .has "mf" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mf", .var "from"],
       .obj "mt" (some "group"),
       .has "mt" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mt", .var "to"],
       .rel "at" [.var "mf", .var "mn"],
       .rel "one-less" [.var "mn", .var "mn1"],
       .rel "at" [.var "mt", .var "mk"],
       .rel "one-less" [.var "mk1", .var "mk"],
       .obj "cf" (some "group"),
       .has "cf" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "cf", .var "from"],
       .obj "ct" (some "group"),
       .has "ct" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "ct", .var "to"],
       .rel "at" [.var "cf", .var "cn"],
       .rel "one-less" [.var "cn", .var "cn1"],
       .rel "at" [.var "ct", .var "ck"],
       .rel "one-less" [.var "ck1", .var "ck"]]
      bind := [.obj "bt" (some "boat"),
       .rel "at" [.var "bt", .var "bold"],
       .obj "mf" (some "group"),
       .has "mf" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mf", .var "bold"],
       .obj "mt" (some "group"),
       .has "mt" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "mt", .var "to"],
       .rel "at" [.var "mf", .var "mold"],
       .rel "one-less" [.var "mold", .var "mnew"],
       .rel "at" [.var "mt", .var "mtold"],
       .rel "one-less" [.var "mtnew", .var "mtold"],
       .obj "cf" (some "group"),
       .has "cf" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "cf", .var "bold"],
       .obj "ct" (some "group"),
       .has "ct" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "ct", .var "to"],
       .rel "at" [.var "cf", .var "cold"],
       .rel "one-less" [.var "cold", .var "cnew"],
       .rel "at" [.var "ct", .var "ctold"],
       .rel "one-less" [.var "ctnew", .var "ctold"]]
      effects := [.change "at" [.var "mf", .var "mold"] 2 (.var "mnew"), .change "at" [.var "mt", .var "mtold"] 2 (.var "mtnew"), .change "at" [.var "cf", .var "cold"] 2 (.var "cnew"), .change "at" [.var "ct", .var "ctold"] 2 (.var "ctnew"), .change "at" [.var "bt", .var "bold"] 2 (.var "to")]
      report := [.text "A missionary and a cannibal row the boat to the ", .handle "to", .text " bank"] }]
  goal := .ex [.obj "g" (some "group"),
     .rel "side" [.var "g", .h "right"],
     .has "g" "role" .eq (.val (.sym "missionary")),
     .rel "at" [.var "g", .var "n"],
     .has "n" "value" .eq (.val (.int 3)),
     .obj "h" (some "group"),
     .rel "side" [.var "h", .h "right"],
     .has "h" "role" .eq (.val (.sym "cannibal")),
     .rel "at" [.var "h", .var "k"],
     .has "k" "value" .eq (.val (.int 3))]
  goalStmts := [5]
  failures := [
    { name := "missionaries-eaten", stmts := [3, 4],
      cond := .ex [.obj "g" (some "group"),
       .has "g" "role" .eq (.val (.sym "missionary")),
       .rel "side" [.var "g", .var "k"],
       .obj "h" (some "group"),
       .has "h" "role" .eq (.val (.sym "cannibal")),
       .rel "side" [.var "h", .var "k"],
       .rel "at" [.var "g", .var "n"],
       .rel "at" [.var "h", .var "c"],
       .has "n" "value" .gt (.val (.int 0)),
       .has "c" "value" .gt (.prop "n" "value")] }]
  assumptions := [
    { id := "A-MC1", kind := .intent, stmts := [1], text := "The three missionaries are interchangeable, and so are the three cannibals, so the state is how many of each are on each bank. Four group objects (the missionaries and the cannibals on the left and on the right bank, side relation to their bank) are at a number object (zero to three, with a value). The boat is at a bank; the two banks have a static other relation both ways." },
    { id := "A-MC2", kind := .intent, stmts := [2], text := "\"carries one or two people and never crosses empty\": five crossing operators, one for each mix of one or two people (one or two missionaries, one or two cannibals, one of each). A crossing moves the boat to the other bank and moves the people from the group on the boat's bank to the group of the same role on the other bank." },
    { id := "A-MC3", kind := .intent, stmts := [2], text := "WorldSpec has no subtraction, so the counts are number objects linked by static one-less(n, n - 1) and two-less(n, n - 2) relations; a crossing is legal only when the starting group has enough people (the relation exists for its number)." },
    { id := "A-MC4", kind := .intent, stmts := [3, 4], text := "\"cannibals outnumber the missionaries\", with no missionaries safe: a losing state is a bank whose missionaries number more than zero and fewer than its cannibals. \"ever\": wherever it arises, in the real world or in look-ahead." },
    { id := "A-MC5", kind := .intent, stmts := [5], text := "The goal is three missionaries and three cannibals on the right bank." },
    { id := "A-MC6", kind := .intent, stmts := [], text := "Search control, not from the English (as for the other WorldSpec river crossings): a look-ahead state that returns to a situation already on its path fails; a situation is the number in each group and where the boat is." },
    { id := "A-MC7", kind := .intent, stmts := [3], text := "Representation choice (25 Nov 2026): a first version with six person objects stated the losing states with negated conditions (exactly one or two missionaries on a bank); its learned rules dropped the negations and rejected every crossing at the start, and without learning its look-ahead did not finish in 100,000 decisions. Counting the groups needs no negation." }]
  repeatControl := some { rel := "at", types := ["group", "boat"] }

end WorldSpec.Tasks
