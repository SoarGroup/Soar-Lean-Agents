# Monkey and bananas: English to Soar through Lean (WorldSpec), 16 November 2026

## Regenerated 21 November 2026 (library v2.45, SoarLean release revision b)

Rules regenerated from `monkey-and-bananas-spec.py` with `spec_backend.py` of `SoarLean-2026-11-21b-release.zip` (path B); `rosiegen compile` (path A) gives identical rules apart from the header; `rosiegen json` equals the Python JSON. 23 rules, as before. The 39 changed lines are the 18 November conventions: `^problem-space.name` tests on the task rules (World-Conventions L3-005), the three rule-group comments (L3-012), and `^unachieved-desireds true` in place of a binding of every unachieved desired. The semantics and Soar agree on every example state; `rosiegen replay` accepts every new run.

Runs on library v2.45 (Soar 9.6.6, defaults; outcome, decisions / actions):

| Seed | Stored run (rules of 16 Nov, library v2.41) | Rules of 16 Nov, library v2.45 | New rules, library v2.45 | Plan (new rules) |
|---|---|---|---|---|
| 1 | success 1078 / 4 | success 1386 / 4 | success 1386 / 4 | go place-c; push place-b; climb-up box; grasp bananas |
| 2 | success 1296 / 4 | success 742 / 4 | success 742 / 4 | go place-c; push place-b; climb-up box; grasp bananas |
| 3 | success 903 / 4 | success 1170 / 4 | success 1170 / 4 | go place-c; push place-b; climb-up box; grasp bananas |

The earlier sections below describe the generation of 16 November.

**Runnable.** Soar 9.6.6 (SoarSuite bug-fix release, kernel 9.6.50, build of 6 Nov 2026), library v2.41. Solves on seeds 1-3 with a 4-action plan, the shortest the semantics finds.

**Checked by Lean (Lean 4.35.0, 16 November 2026).** `MonkeyBananas.lean` is in `SoarLean/agentgen/WorldSpec/Tasks` (package `soarlean-agentgen-2026-11-16-classicai.zip`). `monkeyBananas_wellFormed : monkeyBananas.wellFormed = [] := by decide` is proved; `rosiegen json` gives the same JSON as `monkey-and-bananas-worldspec.json`; `rosiegen compile` (path A) gives the same rules as path B; `rosiegen check` agrees on every example state; `rosiegen replay` accepts every run. The description was first written in Python (`../../tools/worldspec_py.py`) while Lean was unavailable; the Lean file is printed from it.

## Files

| File | What it is |
|---|---|
| `english-input.txt` | The numbered English statements (the input) |
| `monkey-and-bananas-spec.py` | The WorldSpec description, written once in Python (constructors of `worldspec_py.py`) |
| `MonkeyBananas.lean` | The same description as Lean source (`WorldSpec.Tasks`), printed from the spec |
| `*.world` | The initial world and example states, in the Rosie world-file format |
| `monkey-and-bananas-worldspec.json` | Path B input (format worldspec-1, as `rosiegen json` writes it) |
| `monkey-and-bananas-rules.soar` | Task rules, written by `SoarLean/worldgen/spec_backend.py` (23 rules; derived-attribute check passes) |
| `monkey-and-bananas.soar` | Loader: library from `Soar/soar-library`, then the rules |
| `run-seed1..3.json` | The runs (`run_agent.py --json`) |

## Example states

Goal and losing conditions, evaluated by the semantics (`worldspec_py.py check`) and by Soar on rules whose initial world is the example state (`run_agent.py --check`):

| World | State | goal-met / failure | Semantics vs Soar |
|---|---|---|---|
| `init-monkey.world` | initial state | false / false | agree |
| `final-monkey.world` | monkey on the box at B holding the bananas | true / false | agree |
| `onbox-monkey.world` | monkey on the box at C | false / false | agree |

## Runs (seeds 1-3, cap 300,000 decisions, library defaults)

| Seed | Outcome | Decisions | Actions | Seconds | Plan |
|---|---|---|---|---|---|
| 1 | success | 1,078 | 4 | 0.6 | go place-c; push place-b; climb-up box; grasp bananas |
| 2 | success | 1,296 | 4 | 0.7 | go place-c; push place-b; climb-up box; grasp bananas |
| 3 | success | 903 | 4 | 0.5 | go place-c; push place-b; climb-up box; grasp bananas |

Every plan was replayed in the semantics (`worldspec_py.py replay`): every action legal, no maintained-relation error, goal holds. The same decisions were made on a Soar build from SoarGroup master (30 Oct 2026).

## Assumption ledger

- **A-MB1** (intent; statements 2, 8): "Bananas hang from the ceiling above B": the bananas are at B, so "the place under the bananas" is the place the bananas are at.
- **A-MB2** (intent; statements 3, 6, 7): The floor is an object; being on the floor or on the box is an on relation from the monkey.
- **A-MB3** (intent; statements 8, 9): "has the bananas" is a holds relation from the monkey to the bananas, added by grasp.
- **A-MB4** (intent; statements 4, 5, 6, 7, 8): The actions are named go, push, climb-up, climb-down and grasp.

No `gap` or `tooling` assumption is open.

## Reproduce

    cd Tasks/webtasks/classic-ai/monkey-and-bananas
    export PYTHONPATH=../../tools
    python3 ../../tools/worldspec_py.py monkey-and-bananas-spec.py explore init-monkey.world 200000
    python3 ../../tools/worldspec_py.py monkey-and-bananas-spec.py json init-monkey.world monkey-and-bananas-worldspec.json
    python3 ../../../../SoarLean/worldgen/spec_backend.py monkey-and-bananas-worldspec.json monkey-and-bananas-rules.soar
    python3 ../../../From-English/rosie-teaching/tools/run_agent.py . monkey-and-bananas.soar --seed 1 --cap 300000

## Checking with Lean

    cd SoarLean/agentgen && lake build rosiegen
    rosiegen json monkey-and-bananas <world> lean.json     # compare with monkey-and-bananas-worldspec.json
    rosiegen compile monkey-and-bananas <world> A.soar     # path A; same rules as monkey-and-bananas-rules.soar apart from the header
    rosiegen check monkey-and-bananas <world>
    rosiegen replay monkey-and-bananas <init world> run-seed1.json

`rosiegen replay` stops with "String expected" on these runs: `run_agent.py --json` writes `null` for a missing second argument, and `rosiegen` reads actions as lists of strings. With the nulls removed, every run replays to the goal. Proposed fix (not applied): have `rosiegen` drop nulls when it reads `actions`.
