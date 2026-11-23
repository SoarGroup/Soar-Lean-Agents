# Logistics

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Manuela Veloso (Prodigy); this version by Selman and Kautz; AIPS-1998, round 1.

**Task.** Trucks carry packages within cities and airplanes carry them between cities' airports, to deliver every package to its goal location.

**PDDL.** Untyped STRIPS (types as unary predicates). Requirements: :strips.

**Source.** `ipc-1998/domains/logistics-round-1-strips` of [https://github.com/potassco/pddl-instances](https://github.com/potassco/pddl-instances) (original competition files).

**Overlap with existing tasks.** None; transport tasks of the same kind are not yet in the repository.

**Notes for conversion.** Packages can be delivered nearly independently: the standard case for decomposition by goal conjunct.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 35 problem files: instance-1.pddl to instance-35.pddl |
| `SOURCE-README.md` | The source repository's notes, with the original competition file names |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
