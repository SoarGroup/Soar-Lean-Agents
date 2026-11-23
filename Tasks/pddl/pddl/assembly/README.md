# Assembly

**Status: PDDL input only; not yet converted.** Downloaded 23 November 2026.

**Origin.** Drew McDermott; AIPS-1998, round 1 (ADL track only).

**Task.** Assemble an object from a tree of parts, subject to resources, transient parts and ordering constraints between parts.

**PDDL.** Typed ADL: quantified and conditional preconditions and effects. Requirements: :adl.

**Source.** `ipc-1998/domains/assembly-round-1-adl` of [https://github.com/potassco/pddl-instances](https://github.com/potassco/pddl-instances) (original competition files; the source notes buggy versions of some instances, kept there under additional-notes and not copied here).

**Overlap with existing tasks.** None.

**Notes for conversion.** The most complex of the set; last.

## Files

| File | What it is |
|---|---|
| `domain.pddl` | The domain: types, predicates, actions (the input, as `english-input.txt` is for the From-English tasks) |
| `problems/` | 30 problem files: instance-1.pddl to instance-30.pddl |
| `SOURCE-README.md` | The source repository's notes, with the original competition file names |

Files added at conversion, named as in `Tasks/webtasks/classic-ai`: `<task>-spec.py` (WorldSpec description), `<Name>.lean`, `<task>-worldspec.json`, `*.world` example states, `<task>-rules.soar`, `<task>.soar` (loader), `run-seed*.json`.
