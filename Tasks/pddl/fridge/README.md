# Fridge

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Tony Barrett (University of Washington, 1993-94); quantified version by Joerg Hoffmann; IPP collection.

**Task.** For each fridge, turn it off, unfasten the screws of the backplane, swap the broken compressor for a new one, fasten the screws and turn it on.

**PDDL.** Typed ADL: quantified, negative and disjunctive (imply) preconditions. Requirements: :strips :typing :quantified-preconditions :negative-preconditions :disjunctive-preconditions.

**Source.** domain from `fridge/domain.pddl` of [https://github.com/AI-Planning/pddl-generators](https://github.com/AI-Planning/pddl-generators); three problems written for this collection following the generator's scheme (no randomization). The domain file carries a University of Washington copyright notice permitting non-commercial research use only, which must stay with the file.

**Overlap with existing tasks.** None.

**Notes for conversion.** Universal and existential preconditions are not in WorldSpec; second round.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 3 problem files: p01-f1-s2.pddl to p03-f2-s3.pddl |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
