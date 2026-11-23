# Blocksworld (3 operators, no arm)

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Winograd and Sussman lineage; taken by the FF collection from the IPP domain collection.

**Task.** Move a clear block onto another clear block or the table, with no arm. The goal fixes some on-relations.

**PDDL.** Untyped STRIPS with equality and a negative precondition. Requirements: :strips :equality :negative-preconditions.

**Source.** domain from `blocksworld/3ops/domain.pddl` of [https://github.com/AI-Planning/pddl-generators](https://github.com/AI-Planning/pddl-generators); the three problems were written for this collection (Sussman anomaly, 4 and 5 blocks), since the repository has a generator but no instances.

**Overlap with existing tasks.** As blocksworld-4ops; the 3-operator form is closer to the Rosie blocks-world task.

**Notes for conversion.** Uses `(not (= ?bm ?bt))`. Negated conditions in operators are outside the current WorldSpec well-formedness (negation stays out of operators; convention L11-003). How to translate an inequality is a question to settle before conversion.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 3 problem files: p01-sussman.pddl to p03-5blocks.pddl |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
