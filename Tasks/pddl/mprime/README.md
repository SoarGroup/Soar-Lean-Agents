# Mystery Prime (Mprime)

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Drew McDermott; AIPS-1998, round 1.

**Task.** Mystery with one more operator: fuel can be passed between locations.

**PDDL.** Untyped STRIPS with one inequality. Requirements: :negative-preconditions :equality.

**Source.** `ipc-1998/domains/mystery-prime-round-1-strips` of [https://github.com/potassco/pddl-instances](https://github.com/potassco/pddl-instances) (original competition files).

**Overlap with existing tasks.** None.

**Notes for conversion.** Second round, after Mystery. The fuel-passing operator has `(not (= ?n1 ?n2))`, a correction added by Malte Helmert to the original file; as with blocksworld-3ops, how to translate an inequality is to be settled before conversion.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 35 problem files: instance-1.pddl to instance-35.pddl |
| `SOURCE-README.md` | The source repository's notes, with the original competition file names |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
