# Instant Insanity: English to Soar through Lean (WorldSpec), 16 November 2026

**Runnable.** Soar 9.6.6 (SoarSuite bug-fix release, kernel 9.6.50, build of 6 Nov 2026), library v2.41. Solves on seeds 1-3 with a 4-action plan, the shortest the semantics finds.

**Checked by Lean (Lean 4.35.0, 16 November 2026).** `InstantInsanity.lean` is in `SoarLean/agentgen/WorldSpec/Tasks` (package `soarlean-agentgen-2026-11-16-classicai.zip`). `instantInsanity_wellFormed : instantInsanity.wellFormed = [] := by decide` is proved; `rosiegen json` gives the same JSON as `instant-insanity-worldspec.json`; `rosiegen compile` (path A) gives the same rules as path B; `rosiegen check` agrees on every example state; `rosiegen replay` accepts every run. The description was first written in Python (`../../tools/worldspec_py.py`) while Lean was unavailable; the Lean file is printed from it.

## Files

| File | What it is |
|---|---|
| `english-input.txt` | The numbered English statements (the input) |
| `instant-insanity-spec.py` | The WorldSpec description, written once in Python (constructors of `worldspec_py.py`) |
| `InstantInsanity.lean` | The same description as Lean source (`WorldSpec.Tasks`), printed from the spec |
| `*.world` | The initial world and example states, in the Rosie world-file format |
| `instant-insanity-worldspec.json` | Path B input (format worldspec-1, as `rosiegen json` writes it) |
| `instant-insanity-rules.soar` | Task rules, written by `SoarLean/worldgen/spec_backend.py` (15 rules; derived-attribute check passes) |
| `instant-insanity.soar` | Loader: library from `Soar/soar-library`, then the rules |
| `run-seed1..3.json` | The runs (`run_agent.py --json`) |

## Example states

Goal and losing conditions, evaluated by the semantics (`worldspec_py.py check`) and by Soar on rules whose initial world is the example state (`run_agent.py --check`):

| World | State | goal-met / failure | Semantics vs Soar |
|---|---|---|---|
| `init-cubes.world` | nothing placed | false / false | agree |
| `fail-cubes.world` | cubes 1 and 2 both blue in front | false / true | agree |
| `final-cubes.world` | a solution | true / false | agree |

## Runs (seeds 1-3, cap 300,000 decisions, library defaults)

| Seed | Outcome | Decisions | Actions | Seconds | Plan |
|---|---|---|---|---|---|
| 1 | success | 15,748 | 4 | 124.7 | place cube-a a-o8x; place cube-b b-o6x; place cube-c c-o8x; place cube-d d-o6x |
| 2 | success | 14,951 | 4 | 97.5 | place cube-a a-o20x; place cube-b b-o6x; place cube-c c-o15x; place cube-d d-o14x |
| 3 | success | 16,092 | 4 | 106.5 | place cube-a a-o0x; place cube-b b-o0x; place cube-c c-o1x; place cube-d d-o0x |

Every plan was replayed in the semantics (`worldspec_py.py replay`): every action legal, no maintained-relation error, goal holds. The same decisions were made on a Soar build from SoarGroup master (30 Oct 2026) for seeds 1 and 2 (seed 3 was not run there).

## Assumption ledger

- **A-II1** (intent; statements 2, 3, 4): "turned any way you like": each cube has one orientation object per distinct assignment of colours to the four sides (front, back, left, right); the top and bottom faces do not matter. Cube 1 has 24, cubes 2 to 4 have 16 (each has a pair of equal colours).
- **A-II2** (intent; statements 3): "stack in a column": cubes are placed one at a time in the order 1, 2, 3, 4, each on the one before; cube 1 goes on the ground, which counts as placed from the start.
- **A-II3** (intent; statements 5): "four different colours" on a side: two placed cubes showing the same colour on the same side is a losing state, so a partial column that cannot be completed is cut off at once.

No `gap` or `tooling` assumption is open.

## Reproduce

    cd Tasks/webtasks/classic-ai/instant-insanity
    export PYTHONPATH=../../tools
    python3 ../../tools/worldspec_py.py instant-insanity-spec.py explore init-cubes.world 200000
    python3 ../../tools/worldspec_py.py instant-insanity-spec.py json init-cubes.world instant-insanity-worldspec.json
    python3 ../../../../SoarLean/worldgen/spec_backend.py instant-insanity-worldspec.json instant-insanity-rules.soar
    python3 ../../../From-English/rosie-teaching/tools/run_agent.py . instant-insanity.soar --seed 1 --cap 300000

## Checking with Lean

    cd SoarLean/agentgen && lake build rosiegen
    rosiegen json instant-insanity <world> lean.json     # compare with instant-insanity-worldspec.json
    rosiegen compile instant-insanity <world> A.soar     # path A; same rules as instant-insanity-rules.soar apart from the header
    rosiegen check instant-insanity <world>
    rosiegen replay instant-insanity <init world> run-seed1.json
