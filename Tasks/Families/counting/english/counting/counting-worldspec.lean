import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Counting (families, from English) (Tasks/webtasks/Families/counting/english/counting), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def countingEnglish : Task where
  name := "counting"
  title := "Counting (families, from English)"
  statements := [
    (1, "Count upwards from a starting number to a target number, one at a time."),
    (2, "This instance counts from 0 to 100.")]
  world := { handle := fun o => o.sym "name", rels := [] }
  ops := [
    { name := "count-up", params := [], stmts := [1]
      pre := [.obj "c" (some "counter"),
       .has "c" "count" .lt (.prop "c" "target")]
      bind := [.obj "c" (some "counter")]
      effects := [.update "c" "count" (.plus (.prop "c" "count") (.val (.int 1)))]
      report := [.text "Count one more"] }]
  goal := .ex [.obj "c" (some "counter"),
     .has "c" "count" .eq (.prop "c" "target")]
  goalStmts := [1]
  assumptions := [
    { id := "A-CT1", kind := .intent, stmts := [1, 2], text := "A counter object holds the current number (count, starting at 0) and the target (100)." },
    { id := "A-CT2", kind := .intent, stmts := [1], text := "\"one at a time\": each count-up action adds 1 to the count; it is proposed only while the count is below the target, and the goal is a count equal to the target." }]

end WorldSpec.Tasks
