# Tyreworld (flat tyre)

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Stuart Russell; multi-tyre version by Jana Koehler; IPP collection.

**Task.** Replace flat tyres with inflated spares: open the boot, fetch the tools, loosen the nuts, jack up the hub, swap the wheels, and put everything away.

**PDDL.** Typed STRIPS with constants. Requirements: :strips :typing.

**Source.** domain from `tyreworld/domain.pddl` of [https://github.com/AI-Planning/pddl-generators](https://github.com/AI-Planning/pddl-generators); the problems for 1, 2 and 3 tyres were written for this collection following the generator's scheme (no randomization), since the repository has a generator but no instances.

**Overlap with existing tasks.** None.

**Notes for conversion.** Long plans from a fixed procedure; a good case for task decomposition and verification before halt. One change to the source domain file: the `(:constants ...)` line was moved before `(:predicates ...)`, as the PDDL grammar requires (strict parsers reject the original order); nothing else changed.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 3 problem files: p01-tyres1.pddl to p03-tyres3.pddl |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
