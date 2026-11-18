# Tower of London: English to Soar through Lean (WorldSpec), 16 November 2026

**Runnable.** Soar 9.6.6 (SoarSuite bug-fix release, kernel 9.6.50, build of 6 Nov 2026), library v2.41. Solves on seeds 1-3 with a 5-action plan, the shortest the semantics finds.

**Checked by Lean (Lean 4.35.0, 16 November 2026).** `TowerOfLondon.lean` is in `SoarLean/agentgen/WorldSpec/Tasks` (package `soarlean-agentgen-2026-11-16-classicai.zip`). `towerOfLondon_wellFormed : towerOfLondon.wellFormed = [] := by decide` is proved; `rosiegen json` gives the same JSON as `tower-of-london-worldspec.json`; `rosiegen compile` (path A) gives the same rules as path B; `rosiegen check` agrees on every example state; `rosiegen replay` accepts every run. The description was first written in Python (`../../tools/worldspec_py.py`) while Lean was unavailable; the Lean file is printed from it.

## Files

| File | What it is |
|---|---|
| `english-input.txt` | The numbered English statements (the input) |
| `tower-of-london-spec.py` | The WorldSpec description, written once in Python (constructors of `worldspec_py.py`) |
| `TowerOfLondon.lean` | The same description as Lean source (`WorldSpec.Tasks`), printed from the spec |
| `*.world` | The initial world and example states, in the Rosie world-file format |
| `tower-of-london-worldspec.json` | Path B input (format worldspec-1, as `rosiegen json` writes it) |
| `tower-of-london-rules.soar` | Task rules, written by `SoarLean/worldgen/spec_backend.py` (11 rules; derived-attribute check passes) |
| `tower-of-london.soar` | Loader: library from `Soar/soar-library`, then the rules |
| `run-seed1..3.json` | The runs (`run_agent.py --json`) |

## Example states

Goal and losing conditions, evaluated by the semantics (`worldspec_py.py check`) and by Soar on rules whose initial world is the example state (`run_agent.py --check`):

| World | State | goal-met / failure | Semantics vs Soar |
|---|---|---|---|
| `init-tol.world` | initial state | false / false | agree |
| `near-tol.world` | green on the third peg, not the second | false / false | agree |
| `final-tol.world` | goal arrangement | true / false | agree |

## Runs (seeds 1-3, cap 300,000 decisions, library defaults)

| Seed | Outcome | Decisions | Actions | Seconds | Plan |
|---|---|---|---|---|---|
| 1 | success | 5,594 | 5 | 6.6 | move blue-ball c-low; move green-ball b-low; move red-ball b-top; move blue-ball a-low; move red-ball a-mid |
| 2 | success | 8,802 | 5 | 11.6 | move blue-ball c-low; move green-ball b-low; move red-ball b-top; move blue-ball a-low; move red-ball a-mid |
| 3 | success | 9,206 | 5 | 12.8 | move blue-ball c-low; move green-ball b-low; move red-ball b-top; move blue-ball a-low; move red-ball a-mid |

Every plan was replayed in the semantics (`worldspec_py.py replay`): every action legal, no maintained-relation error, goal holds. The same decisions were made on a Soar build from SoarGroup master (30 Oct 2026).

## Assumption ledger

- **A-TL1** (intent; statements 1): "holds up to n balls": a peg has n slots, stacked by an over relation from a floor; a ball is at a slot.
- **A-TL2** (intent; statements 4): "the top ball": a ball whose slot has an empty space over it. Each peg has a cap space over its top slot that is always empty and never a target, so the top slot needs no special case.
- **A-TL3** (intent; statements 4): "onto a peg that is not full": into the peg's lowest empty slot, i.e. an empty slot over a slot or floor that something is at. Each floor holds a fixed base object, which no action moves.
- **A-TL4** (intent; statements 4): "another peg": the target slot is of a different peg than the ball's slot.
- **A-TL5** (intent; statements 6): "as few moves as possible": unit cost per move, read through the library's search settings, not through the rules.

No `gap` or `tooling` assumption is open.

## Reproduce

    cd Tasks/webtasks/classic-ai/tower-of-london
    export PYTHONPATH=../../tools
    python3 ../../tools/worldspec_py.py tower-of-london-spec.py explore init-tol.world 200000
    python3 ../../tools/worldspec_py.py tower-of-london-spec.py json init-tol.world tower-of-london-worldspec.json
    python3 ../../../../SoarLean/worldgen/spec_backend.py tower-of-london-worldspec.json tower-of-london-rules.soar
    python3 ../../../From-English/rosie-teaching/tools/run_agent.py . tower-of-london.soar --seed 1 --cap 300000

## Checking with Lean

    cd SoarLean/agentgen && lake build rosiegen
    rosiegen json tower-of-london <world> lean.json     # compare with tower-of-london-worldspec.json
    rosiegen compile tower-of-london <world> A.soar     # path A; same rules as tower-of-london-rules.soar apart from the header
    rosiegen check tower-of-london <world>
    rosiegen replay tower-of-london <init world> run-seed1.json
