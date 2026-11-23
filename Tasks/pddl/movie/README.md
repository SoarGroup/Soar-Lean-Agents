# Movie

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Corin Anderson; AIPS-1998, round 1.

**Task.** Get ready to watch a movie: buy one snack of each kind, rewind the movie and reset the counter.

**PDDL.** Untyped STRIPS. Requirements: none declared (STRIPS).

**Source.** `ipc-1998/domains/movie-round-1-strips` of [https://github.com/potassco/pddl-instances](https://github.com/potassco/pddl-instances) (original competition files).

**Overlap with existing tasks.** None.

**Notes for conversion.** Trivial plans; useful as a first end-to-end test of the PDDL front end. Instances grow only in the number of interchangeable snacks.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 30 problem files: instance-1.pddl to instance-30.pddl |
| `SOURCE-README.md` | The source repository's notes, with the original competition file names |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
