# Ferry

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Origin unknown; IPP collection. The FF version restricts sailing to different locations.

**Task.** A ferry that holds one car at a time carries cars between locations to their goal locations.

**PDDL.** Untyped STRIPS (types given as unary predicates). Requirements: none declared (STRIPS).

**Source.** domain from `ferry/domain.pddl` of [https://github.com/AI-Planning/pddl-generators](https://github.com/AI-Planning/pddl-generators); three problems written for this collection following the generator's scheme.

**Overlap with existing tasks.** Related in kind to the river crossings (Tasks/From-English/rosie-teaching/river-crossing-puzzles).

**Notes for conversion.** `not-eq` facts are listed in the initial state, so no negation is needed.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 3 problem files: p01-l2-c1.pddl to p03-l3-c3.pddl |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
