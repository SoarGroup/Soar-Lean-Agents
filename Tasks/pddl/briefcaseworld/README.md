# Briefcaseworld

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** First described by Edwin Pednault; IPP collection.

**Task.** Carry objects between locations in a briefcase. Moving the briefcase moves everything inside it.

**PDDL.** Typed ADL: a conditional effect over all objects. Requirements: :adl.

**Source.** domain from `briefcaseworld/domain.pddl` of [https://github.com/AI-Planning/pddl-generators](https://github.com/AI-Planning/pddl-generators); three problems written for this collection following the generator's scheme (objects and briefcase over objects + 1 locations).

**Overlap with existing tasks.** None.

**Notes for conversion.** `move` has a `forall ... when` conditional effect, which is close to WorldSpec's `each` effect. `put-in` has a negative precondition `(not (in ?x))`, outside current WorldSpec operator conditions (L11-003); to be settled before conversion.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 3 problem files: p01-o1.pddl to p03-o3.pddl |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
