# Instant Insanity: English to Soar through Lean (WorldSpec), 16 November 2026

## Regenerated 25 November 2026: matching hints for learned rules (World-Conventions L11-009)

**Runnable with the library default (learning on, `chunk only`)** and with learning off. The rules now open with
`production optimize-attribute` lines written by both generators (`Compile.lean` `matchHints`, `spec_backend.py`
`match_hints`): `object 77`, `orient 72`, `unplaced 4`, `unplaced-next 3`, `unplaced-first 2`, `placed 2` (sizes from
the initial world). Nothing else in the rules changes; paths A and B agree apart from the header.

Cause of the earlier blow-up (To-do row 44): at decision 5,201 look-ahead learns two chunks of 70-80 conditions that
test five `^orient` tuples of cube-d and 13 `^object` links, with the orientations identified only by handle tests in
later conditions. Without hints Soar's reorderer treats `^orient` (72 tuples) and `^object` (77 links) as single-valued
and joins them before those tests, so the partial matches of one chunk exhaust memory.

Runs, library v2.47, `run_agent.py`, cap 20,000 (two runs at a time on 2 cores, so CPU times are high):

| Seed | `chunk only` (default) | `chunk never` |
|---|---|---|
| 1 | success, 5,170 decisions, 1,606 s CPU | success, 18,874 decisions |
| 2 | success, 5,367 decisions, 1,711 s CPU | success, 18,692 decisions |
| 3 | success, 5,358 decisions, 1,548 s CPU | success, 19,208 decisions |

Memory stayed below about 225 MB. `chunk never` makes exactly the decisions of 24 November (the hints change only
condition order). `rosiegen replay` accepts the three `chunk only` runs (`run-chunk-only-seed1..3.json`), each 4
actions. Learning cuts decisions by more than two thirds but costs CPU time: the large chunks are expensive to match.

## Regenerated 24 November 2026: the cube order is generated, not written (World-Conventions L21-001)

Runnable with learning off (`chunk never`). With learning on it did not finish on library v2.47 (see "Learning on"
below); fixed on 25 November (above).

What changed (JL, 24 Nov 2026):
- **Description.** Assumption A-II2 no longer fixes the order 1, 2, 3, 4. `place` now tests only that the cube is
  unplaced and that the orientation is one of its own (the tests `prev(c, q)` and `placed(q, r)` are gone). The world
  files lose the `ground` and `ground-pose` objects, the `prev` relation and the initial `placed(ground, ground-pose)`.
  A-II2 now records the reading that a cube's place in the column does not matter, so cubes are placed in any order.
- **Generators.** Both paths recognize from the description that it is a set of slots (cubes) each filled once, with
  commuting fills (`SoarLean/agentgen/WorldSpec/SlotOrder.lean`; `worldgen/spec_backend.py`, `slots`), and propose
  `place` only for the first unplaced cube in the order of the world file (`unplaced-first`, moved along
  `unplaced-next`). The order is the same as before (cube-a, b, c, d), but it now comes from the generator, and the
  rules say so in a comment after the assumption ledger. 17 rules (15 before: the two new ones are the `each` rules that
  move `unplaced-first`).

Checks (SoarLean release of 24 November 2026, revision b; Lean 4.35.0):
- `instantInsanity_wellFormed` and `instantInsanity_slots` (the structure is recognized) are proved by `decide`.
- `rosiegen json` equals the JSON written by `worldspec_py.py`; paths A and B write the same rules apart from the header,
  on the initial world and on both example states.
- `rosiegen check` and Soar on the path A and path B rules agree on the three example states (init: neither; fail: lost;
  final: goal).
- `rosiegen explore`: shortest plan 4 actions (19,850 states now that the description allows any order); 0 errors.
- `rosiegen replay` and `worldspec_py.py replay` accept the three new runs.

Runs, library v2.47 with `chunk never` (`run_agent.py --extra` with a file holding `chunk never`), cap 300,000:

| Seed | Rules of 21 Nov (A-II2 in the description) | Regenerated rules (generated order) | Plan (regenerated rules) |
|---|---|---|---|
| 1 | success, 19,608 decisions | success, 18,874 decisions | place cube-a a-o23x; cube-b b-o3x; cube-c c-o2x; cube-d d-o3x |
| 2 | success, 19,588 decisions | success, 18,692 decisions | place cube-a a-o2x; cube-b b-o2x; cube-c c-o3x; cube-d d-o2x |
| 3 | success, 20,093 decisions | success, 19,208 decisions | place cube-a a-o16x; cube-b b-o6x; cube-c c-o13x; cube-d d-o12x |

The old rules make exactly the decisions of their 21 November runs on v2.45. The regenerated rules tie the same
operators at the first decision (the 24 orientations of cube-a, in the same order), but they do not make the same
decisions throughout: the look-ahead worlds hold other relations (no `prev` or ground objects; `unplaced-next` and
`unplaced-first` added), so the library's random choices among tied evaluations fall differently. All six runs find a
valid column; the regenerated rules take 3-5% fewer decisions on these seeds. `run-seed1..3.json` are the new runs.

**Learning on (the library default since v2.46).** With `chunk only`, every run, with the old rules and the new,
grew past 5.5 GB and was killed by the workspace's 8 GB memory limit, after several minutes of CPU
each. The old rules do it too, so the generated order is not the cause. It may be related to To-do rows 35-37
(chunking blow-ups); not yet investigated. (Cause found and fixed 25 November; see above.)

## Regenerated 21 November 2026 (library v2.45, SoarLean release revision b)

Rules regenerated from `instant-insanity-spec.py` with `spec_backend.py` of `SoarLean-2026-11-21b-release.zip` (path B); `rosiegen compile` (path A) gives identical rules apart from the header; `rosiegen json` equals the Python JSON. 15 rules, as before. The 23 changed lines are the 18 November conventions: `^problem-space.name` tests on the task rules (World-Conventions L3-005), the three rule-group comments (L3-012), and `^unachieved-desireds true` in place of a binding of every unachieved desired. The semantics and Soar agree on every example state; `rosiegen replay` accepts every new run.

Runs on library v2.45 (Soar 9.6.6, defaults; outcome, decisions / actions):

| Seed | Stored run (rules of 16 Nov, library v2.41) | Rules of 16 Nov, library v2.45 | New rules, library v2.45 | Plan (new rules) |
|---|---|---|---|---|
| 1 | success 15748 / 4 | success 19608 / 4 | success 19608 / 4 | place cube-a a-o0x; place cube-b b-o0x; place cube-c c-o1x; place cube-d d-o0x |
| 2 | success 14951 / 4 | success 19588 / 4 | success 19588 / 4 | place cube-a a-o2x; place cube-b b-o2x; place cube-c c-o1x; place cube-d d-o2x |
| 3 | success 16092 / 4 | success 20093 / 4 | success 20093 / 4 | place cube-a a-o11x; place cube-b b-o9x; place cube-c c-o6x; place cube-d d-o9x |

The earlier sections below describe the generation of 16 November.

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
