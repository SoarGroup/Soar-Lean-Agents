# Mystery

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Drew McDermott; AIPS-1998, round 1.

**Task.** A disguised transport problem: vehicles with limited space and fuel move cargo over a map. Object and operator names are deliberately meaningless (pleasures, cravings, foods).

**PDDL.** Untyped STRIPS (types as unary predicates). Requirements: none declared (STRIPS).

**Source.** `ipc-1998/domains/mystery-round-1-strips` of [https://github.com/potassco/pddl-instances](https://github.com/potassco/pddl-instances) (original competition files).

**Overlap with existing tasks.** None.

**Notes for conversion.** The meaningless names make it a test of blind back-translation to English: the back-translator cannot lean on the names.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 30 problem files: instance-1.pddl to instance-30.pddl |
| `SOURCE-README.md` | The source repository's notes, with the original competition file names |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
