# Towers of Hanoi

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Origin of this encoding unknown (IPP collection); the formalization comment credits Hector Geffner.

**Task.** Move a stack of discs from the first peg to the third, one disc at a time, never placing a disc on a smaller one. Pegs are treated as very large discs.

**PDDL.** Untyped STRIPS. Requirements: :strips.

**Source.** domain and problems `pddl/hanoi.pddl`, `pddl/hanoi-3.pddl` to `hanoi-8.pddl` of [https://github.com/SoarGroup/Domains-Planning-Domain-Definition-Language](https://github.com/SoarGroup/Domains-Planning-Domain-Definition-Language), SoarGroup's earlier PDDL-to-Soar translator; the domain is identical in content to `hanoi/domain.pddl` of [https://github.com/AI-Planning/pddl-generators](https://github.com/AI-Planning/pddl-generators).

**Overlap with existing tasks.** Rosie tower-of-hanoi, -4 and -5 (Tasks/From-English/rosie-teaching/block-puzzles), which do not solve for 4 and 5 discs within the look-ahead depth limit.

**Notes for conversion.** A direct comparison of English-derived and PDDL-derived agents for 3 to 8 discs.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 6 problem files: hanoi-3.pddl to hanoi-8.pddl |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
