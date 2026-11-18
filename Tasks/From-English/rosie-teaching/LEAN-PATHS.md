# Rosie dialogs to Soar through Lean: path A, path B and the direct agents (16 November 2026)

**Runnable.** Three tasks were taken through Lean both ways: Tower of Hanoi (`block-puzzles/tower-of-hanoi`), fox-goose-bean (`river-crossing-puzzles/fox-goose-bean`) and KenKen with color groups (`logic-puzzles/kenken`). Each folder has the two Lean-path agents next to the direct one. All use Soar 9.6.6 and library v2.37.

| Path | How the rules are written | Files in the task folder |
|---|---|---|
| Direct | Python generator (`gen.py`, `tools/rosie_*.py`) that holds the rule text | `<task>.soar`, `<task>-rules.soar` |
| A | Lean: a typed WorldSpec description (`SoarLean/agentgen/WorldSpec/Tasks/*.lean`) compiled by Lean (`rosiegen compile`) | `<task>-lean-a.soar`, `<task>-lean-a-rules.soar` |
| B | Lean description exported as JSON (`rosiegen json`), rules written by Python (`SoarLean/worldgen/spec_backend.py`) | `<task>-worldspec.json`, `<task>-lean-b.soar`, `<task>-lean-b-rules.soar` |

The description language, its semantics and the tools are documented in `SoarLean/agentgen/WorldSpec/README.md`.

## Results

**Paths A and B write the same rules.** For all three tasks the two rule files are identical apart from the first header line, which names the path. Path B is a second implementation of path A's compiler, and the agreement checks each against the other.

**Example states.** The goal and the losing conditions were evaluated on all 10 example states of the three dialogs (init, fail and final). Three evaluations agree on every one, and each matches the instructor's intent:
- the Lean semantics (`rosiegen check`);
- Soar running the path A rules with that state as the initial world;
- Soar running the path B rules the same way.

fail-color-ken has the goal and a losing condition together, so it counts as lost.

**Runs (seeds 1–3, cap 300,000 decisions).** The direct agent, path A and path B made the same decisions in every run, so their plans are identical. Every plan was replayed twice, once in the Lean semantics (`rosiegen replay`) and once with `tools/check_plan.py`; the two replays agree on every run.

| Task | Shortest plan (Lean search) | Library v2.37 | v2.37 with failed moves rejected |
|---|---|---|---|
| Tower of Hanoi | 7 | 7 moves on every seed (35,393 / 44,438 / 46,451 decisions) | Unchanged |
| Fox-goose-bean | 7 | Solved: 11, 7 and 25 crossings (6,098 / 3,438 / 16,518 decisions) | 7 crossings on every seed (6,403 / 6,372 / 6,366) |
| KenKen | 4 | Seed 1 loses at write 2 (group sum); seeds 2–3 solve in 4 (263 / 549 / 360 decisions) | Every seed solves in 4 (1,110 / 1,104 / 1,098) |

"Failed moves rejected" is the overlay `tools/experiments/failure-becomes-reject.soar`. It is the library change agreed for proposal, still to be applied by John.

The shortest-plan column comes from `rosiegen explore`, a breadth-first search in the Lean semantics. On the way it checks every effect of every reachable state, and found no error: 25, 15 and 112 states.

## What Lean adds over the direct path

- **A typed description.** It holds the instructor's statement numbers and the assumption ledger; the rules are derived from it rather than written by hand.
- **Proved well-formedness.** `Task.wellFormed = []` is proved by `decide` for each task. It covers three checks:
  - no negation in a compiled condition (L11-003);
  - effects and reports use only bound variables;
  - no open `gap` or `tooling` assumption (CLAUDE.md, issue 6).
- **A semantics independent of Soar.** It does four jobs:
  - classifies the example states;
  - replays plans;
  - finds the shortest plan;
  - checks that each maintained relation (clear, opposite, empty) stays equal to its definition after every effect.

  The direct path has only the Python replay checkers, one per task family.
- **Maintained relations computed from their definitions.** The definitions use negation (clear: not below any object). Lean evaluates them for the initial world; the generator does not write them by hand per task.

## Cost

| | Direct | Path A | Path B |
|---|---|---|---|
| Per task | 40–180 lines of Python with rule text | 40–70 lines of Lean description | The same description |
| Shared code | `rosie_gen`, `rosie_blocks`, `rosie_tasks`, `rosie_logic`, `wg.py` (about 950 lines) | WorldSpec, about 1,100 lines of Lean (types, semantics, compiler, checks) | WorldSpec without `Compile.lean`, plus `spec_backend.py` (383 lines of Python) |
| Rules (Hanoi / fox / KenKen) | 11 / 16 / 17 | 11 / 16 / 17 | Same as A |
| Condition lines | 59 / 123 / 108 | 73 / 168 / 162: a uniform scheme with one test per line and no merged conditions | Same as A |

## Limits and next steps

- **Not yet in the language:**
  - path control against repeated states, used by the river crossings;
  - counted attributes (missionaries and cannibals);
  - sums whose target is a clue object (kakuro, shuffle, survo, sujiko, suko);
  - a filter on a universal condition.
- **Expansion over the initial world.** A universal condition is expanded over the objects of its type in the initial world, as in the direct generators.
- **The other 24 generated Rosie tasks** are not yet described in WorldSpec.
