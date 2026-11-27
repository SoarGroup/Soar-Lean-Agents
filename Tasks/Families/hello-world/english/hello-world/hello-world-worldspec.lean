import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Hello World (families, from English) (Tasks/webtasks/Families/hello-world/english/hello-world), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def helloWorldEnglish : Task where
  name := "hello-world"
  title := "Hello World (families, from English)"
  statements := [
    (1, "Write the words \"Hello World\" once, then stop.")]
  world := { handle := fun o => o.sym "name", rels := [] }
  ops := [
    { name := "write-hello-world", params := [], stmts := [1]
      pre := [.obj "p" (some "page"),
       .has "p" "written" .eq (.val (.sym "nothing"))]
      bind := [.obj "p" (some "page")]
      effects := [.update "p" "written" (.val (.sym "hello-world"))]
      report := [.text "Hello World"] }]
  goal := .ex [.obj "p" (some "page"),
     .has "p" "written" .eq (.val (.sym "hello-world"))]
  goalStmts := [1]
  assumptions := [
    { id := "A-HW1", kind := .intent, stmts := [1], text := "Writing is an action of the agent (a perform-action command); its report prints \"Hello World\"." },
    { id := "A-HW2", kind := .intent, stmts := [1], text := "\"once, then stop\": a page object records what is written on it (nothing at the start); the operator needs a page with nothing written, and the goal is a page with the words, so the agent writes once and the task ends. (A test that the page lacks the property is a negation, which the compiled conditions may not contain, W-CHK-009.)" }]

end WorldSpec.Tasks
