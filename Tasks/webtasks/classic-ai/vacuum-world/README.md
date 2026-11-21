# Vacuum world: English to Soar through Lean (WorldSpec), 16 November 2026

## Regenerated 21 November 2026 (library v2.45, SoarLean release revision b)

Rules regenerated from `vacuum-world-spec.py` with `spec_backend.py` of `SoarLean-2026-11-21b-release.zip` (path B); `rosiegen compile` (path A) gives identical rules apart from the header; `rosiegen json` equals the Python JSON. 14 rules, as before. The 21 changed lines are the 18 November conventions: `^problem-space.name` tests on the task rules (World-Conventions L3-005), the three rule-group comments (L3-012), and `^unachieved-desireds true` in place of a binding of every unachieved desired. The semantics and Soar agree on every example state; `rosiegen replay` accepts every new run.

Runs on library v2.45 (Soar 9.6.6, defaults; outcome, decisions / actions):

| Seed | Stored run (rules of 16 Nov, library v2.41) | Rules of 16 Nov, library v2.45 | New rules, library v2.45 | Plan (new rules) |
|---|---|---|---|---|
| 1 | success 70 / 3 | success 68 / 3 | success 68 / 3 | suck left; move right; suck right |
| 2 | success 111 / 3 | success 68 / 3 | success 68 / 3 | suck left; move right; suck right |
| 3 | success 107 / 3 | success 97 / 3 | success 97 / 3 | suck left; move right; suck right |

The earlier sections below describe the generation of 16 November.

**Runnable.** Soar 9.6.6 (SoarSuite bug-fix release, kernel 9.6.50, build of 6 Nov 2026), library v2.41. Solves on seeds 1-3 with a 3-action plan, the shortest the semantics finds.

**Checked by Lean (Lean 4.35.0, 16 November 2026).** `VacuumWorld.lean` is in `SoarLean/agentgen/WorldSpec/Tasks` (package `soarlean-agentgen-2026-11-16-classicai.zip`). `vacuumWorld_wellFormed : vacuumWorld.wellFormed = [] := by decide` is proved; `rosiegen json` gives the same JSON as `vacuum-world-worldspec.json`; `rosiegen compile` (path A) gives the same rules as path B; `rosiegen check` agrees on every example state; `rosiegen replay` accepts every run. The description was first written in Python (`../../tools/worldspec_py.py`) while Lean was unavailable; the Lean file is printed from it.

## Files

| File | What it is |
|---|---|
| `english-input.txt` | The numbered English statements (the input) |
| `vacuum-world-spec.py` | The WorldSpec description, written once in Python (constructors of `worldspec_py.py`) |
| `VacuumWorld.lean` | The same description as Lean source (`WorldSpec.Tasks`), printed from the spec |
| `*.world` | The initial world and example states, in the Rosie world-file format |
| `vacuum-world-worldspec.json` | Path B input (format worldspec-1, as `rosiegen json` writes it) |
| `vacuum-world-rules.soar` | Task rules, written by `SoarLean/worldgen/spec_backend.py` (14 rules; derived-attribute check passes) |
| `vacuum-world.soar` | Loader: library from `Soar/soar-library`, then the rules |
| `run-seed1..3.json` | The runs (`run_agent.py --json`) |

## Example states

Goal and losing conditions, evaluated by the semantics (`worldspec_py.py check`) and by Soar on rules whose initial world is the example state (`run_agent.py --check`):

| World | State | goal-met / failure | Semantics vs Soar |
|---|---|---|---|
| `init-vacuum.world` | initial state | false / false | agree |
| `half-vacuum.world` | left clean, vacuum on the right | false / false | agree |
| `final-vacuum.world` | both squares clean | true / false | agree |

## Runs (seeds 1-3, cap 300,000 decisions, library defaults)

| Seed | Outcome | Decisions | Actions | Seconds | Plan |
|---|---|---|---|---|---|
| 1 | success | 70 | 3 | 0.0 | suck left; move right; suck right |
| 2 | success | 111 | 3 | 0.0 | suck left; move right; suck right |
| 3 | success | 107 | 3 | 0.0 | suck left; move right; suck right |

Every plan was replayed in the semantics (`worldspec_py.py replay`): every action legal, no maintained-relation error, goal holds. The same decisions were made on a Soar build from SoarGroup master (30 Oct 2026).

## Assumption ledger

- **A-V1** (intent; statements 1, 3): "the other square": a static next relation holds between Left and Right in both directions.
- **A-V2** (intent; statements 4, 6): "clean" is "not dirty", kept as a maintained relation (it tests absence and decides the goal).
- **A-V3** (intent; statements 4): Suck is proposed only in a dirty square: sucking a clean square changes nothing, so it is never part of a shortest plan.
- **A-V4** (intent; statements 5, 6): "as few steps as possible": unit cost per action, read through the library's search settings, not through the rules.

No `gap` or `tooling` assumption is open.

## Reproduce

    cd Tasks/webtasks/classic-ai/vacuum-world
    export PYTHONPATH=../../tools
    python3 ../../tools/worldspec_py.py vacuum-world-spec.py explore init-vacuum.world 200000
    python3 ../../tools/worldspec_py.py vacuum-world-spec.py json init-vacuum.world vacuum-world-worldspec.json
    python3 ../../../../SoarLean/worldgen/spec_backend.py vacuum-world-worldspec.json vacuum-world-rules.soar
    python3 ../../../From-English/rosie-teaching/tools/run_agent.py . vacuum-world.soar --seed 1 --cap 300000

## Checking with Lean

    cd SoarLean/agentgen && lake build rosiegen
    rosiegen json vacuum-world <world> lean.json     # compare with vacuum-world-worldspec.json
    rosiegen compile vacuum-world <world> A.soar     # path A; same rules as vacuum-world-rules.soar apart from the header
    rosiegen check vacuum-world <world>
    rosiegen replay vacuum-world <init world> run-seed1.json

`rosiegen replay` stops with "String expected" on these runs: `run_agent.py --json` writes `null` for a missing second argument, and `rosiegen` reads actions as lists of strings. With the nulls removed, every run replays to the goal. Proposed fix (not applied): have `rosiegen` drop nulls when it reads `actions`.
