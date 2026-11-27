import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Blocks world (families, from English) (Tasks/webtasks/Families/blocks-world/english/blocks-world), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def blocksWorldEnglish : Task where
  name := "blocks-world"
  title := "Blocks world (families, from English)"
  statements := [
    (1, "Lettered blocks sit on a table, some stacked on others."),
    (2, "You may move one block at a time, and only a block with nothing on top of it."),
    (3, "A block can go onto the table or onto another block that has nothing on top of it."),
    (4, "Blocks A and B start on the table and block C is on block A."),
    (5, "The goal is A on B, B on C and C on the table.")]
  world := { handle := fun o => o.sym "name", rels := ["on"] }
  derived := [
    { name := "clear", vars := ["b"], stmts := [2, 3],
      defn := [.obj "b" (some "block"),
       .none [.rel "on" [.var "x", .var "b"]]] }]
  ops := [
    { name := "move-to-table", params := [("b", some "block")], stmts := [2, 3]
      pre := [.rel "clear" [.var "b"],
       .rel "on" [.var "b", .var "from"],
       .obj "from" (some "block")]
      bind := [.rel "on" [.var "b", .var "old"]]
      effects := [.change "on" [.var "b", .var "old"] 2 (.h "table")]
      report := [.text "Move block ", .handle "b", .text " to the table"] },
    { name := "move-to-block", params := [("b", some "block"), ("to", some "block")], stmts := [2, 3]
      pre := [.rel "clear" [.var "b"],
       .rel "clear" [.var "to"],
       .distinct "b" "to",
       .rel "on" [.var "b", .var "from"],
       .distinct "from" "to"]
      bind := [.rel "on" [.var "b", .var "old"]]
      effects := [.change "on" [.var "b", .var "old"] 2 (.var "to")]
      report := [.text "Move block ", .handle "b", .text " onto block ", .handle "to"] }]
  goal := .ex [.rel "on" [.h "a", .h "b"],
     .rel "on" [.h "b", .h "c"],
     .rel "on" [.h "c", .h "table"]]
  goalStmts := [5]
  assumptions := [
    { id := "A-BW1", kind := .intent, stmts := [1, 4], text := "One on relation from each block to what it sits on, a block or the table (a single table object)." },
    { id := "A-BW2", kind := .intent, stmts := [2, 3], text := "\"nothing on top of it\": no block is on it, a derived relation clear(block) tested positively (W-CHK-009). Two operators: move-to-table for a block that is on a block, and move-to-block onto a different clear block." },
    { id := "A-BW3", kind := .intent, stmts := [], text := "Search control, not from the English (as for the other WorldSpec search tasks): a look-ahead state that returns to a situation already on its path fails; a situation is where each block is." }]
  repeatControl := some { rel := "on", types := ["block"] }

end WorldSpec.Tasks
