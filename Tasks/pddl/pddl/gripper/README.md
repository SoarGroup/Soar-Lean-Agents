# Gripper

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Jana Koehler; AIPS-1998, round 1.

**Task.** A robot with two grippers carries N balls from room A to room B, one ball per gripper.

**PDDL.** Untyped STRIPS. Requirements: none declared (STRIPS).

**Source.** `ipc-1998/domains/gripper-round-1-strips` of [https://github.com/potassco/pddl-instances](https://github.com/potassco/pddl-instances) (original competition files).

**Overlap with existing tasks.** None.

**Notes for conversion.** The two grippers are interchangeable, and so are the balls: the standard example of symmetry pruning (strategy catalog PH-12).

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 20 problem files: instance-1.pddl to instance-20.pddl |
| `SOURCE-README.md` | The source repository's notes, with the original competition file names |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
