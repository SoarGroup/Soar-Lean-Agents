import WorldSpec.Sem
import WorldSpec.WorldFile
/-! Pyramid problem (families, from English) (Tasks/webtasks/Families/pyramid/english/pyramid), from the numbered English statements.
    Printed by worldgen/worldspec_py.py from the same data that wrote the path B JSON. -/
namespace WorldSpec.Tasks
open WorldSpec

def pyramidEnglish : Task where
  name := "pyramid"
  title := "Pyramid problem (families, from English)"
  statements := [
    (1, "A pyramid problem adds a run of consecutive numbers counting down from a base."),
    (2, "The base is the first term, and each term is one less than the one before."),
    (3, "The height says how many terms follow the first, so height h gives h + 1 terms."),
    (4, "This problem has base 5 and height 10 (5 + 4 + ... + (-5))."),
    (5, "The goal is to compute the sum.")]
  world := { handle := fun o => o.sym "name", rels := [] }
  ops := [
    { name := "add-term", params := [], stmts := [1, 2, 3]
      pre := [.obj "p" (some "problem"),
       .has "p" "remaining" .ge (.val (.int 0))]
      bind := [.obj "p" (some "problem")]
      effects := [.update "p" "sum" (.plus (.prop "p" "sum") (.prop "p" "term")), .update "p" "term" (.plus (.prop "p" "term") (.val (.int (-1)))), .update "p" "remaining" (.plus (.prop "p" "remaining") (.val (.int (-1))))]
      report := [.text "Add the next term"] }]
  goal := .ex [.obj "p" (some "problem"),
     .has "p" "remaining" .lt (.val (.int 0))]
  goalStmts := [3, 5]
  assumptions := [
    { id := "A-PY1", kind := .intent, stmts := [2, 4], text := "A problem object holds the next term (starting at the base, 5), the running sum (starting at 0) and the number of terms still to add after the next one (remaining, starting at the height, 10)." },
    { id := "A-PY2", kind := .intent, stmts := [1, 2, 3], text := "add-term adds the next term to the sum, lowers the term by 1 and lowers remaining by 1 (adding -1; WorldSpec has no subtraction, so a negative constant is added). It is proposed while remaining is 0 or more, which gives h + 1 terms." },
    { id := "A-PY3", kind := .intent, stmts := [5], text := "\"compute the sum\": the goal is that every term has been added (remaining below 0); the sum is then on the problem object (0 for this instance)." }]

end WorldSpec.Tasks
