# Grid

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Drew McDermott; AIPS-1998, round 2.

**Task.** A robot moves on a grid, picks up and carries one key at a time, unlocks locked cells with keys of the matching shape, and brings keys to goal cells.

**PDDL.** Untyped STRIPS. Requirements: :strips.

**Source.** `ipc-1998/domains/grid-round-2-strips` of [https://github.com/potassco/pddl-instances](https://github.com/potassco/pddl-instances) (original competition files).

**Overlap with existing tasks.** None.

**Notes for conversion.** Only five instances, all large; smaller ones may have to be written for first runs.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 5 problem files: instance-1.pddl to instance-5.pddl |
| `SOURCE-README.md` | The source repository's notes, with the original competition file names |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
