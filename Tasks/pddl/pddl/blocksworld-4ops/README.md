# Blocksworld (4 operators, robot arm)

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Winograd (1972) and Sussman (1974) lineage; this PDDL encoding (pick-up, put-down, stack, unstack) was used at AIPS-2000.

**Task.** Restack blocks on a table with a one-block robot arm. The goal fixes some on-relations.

**PDDL.** Untyped STRIPS. Requirements: :strips.

**Source.** `ipc-2000/domains/blocks-strips-untyped` of [https://github.com/potassco/pddl-instances](https://github.com/potassco/pddl-instances) (original AIPS-2000 files; file names in SOURCE-README.md).

**Overlap with existing tasks.** Blocks World family (Tasks/Families) and the Rosie blocks-world puzzles (Tasks/From-English/rosie-teaching/block-puzzles).

**Notes for conversion.** Straightforward STRIPS. Instances grow from 4 to 50 blocks; the smallest are the first candidates.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 102 problem files: instance-1.pddl to instance-102.pddl |
| `SOURCE-README.md` | The source repository's notes, with the original competition file names |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
