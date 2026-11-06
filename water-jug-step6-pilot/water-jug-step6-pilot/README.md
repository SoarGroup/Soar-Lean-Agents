# Step 6 pilot: Water Jug family (5 November 2026)

Plan step 6 (normalize the existing test-agent corpus), tried on one family. A minimal version of
the step 5 tools was built for it.

## Contents

| Folder / file | What it is |
|---|---|
| `corpus-sort.csv` | All 598 versions in the working set, each with: category (task agent / Soar unit test or probe / expected-output file / fragment / RL rule dump), task family, input-link use (a heuristic), rule count and learning flags. For Water Jug it also gives what replaces the version. |
| `agentgen/` | Lean package with the agent DSL v0, its compiler to `Soar.Production`, template English, a task-level interpreter, the Water Jug family and the round trip. `tools/vsproject.py` writes VisualSoar projects. The lakefile requires `../cmcsoar/cmcsoar`; edit the path if yours differs. |
| `generated/` | The 9 regenerated agents as VisualSoar projects. Each has a load file `V.soar`, `V.vsa.json` (format 6), the project folder, and `english.md`. The look-ahead variants also include Soar's `default/`. |
| `comparison/` | `harness.py` (task-level runs in Soar 9.6.5), the raw results, `compare.csv`, and `soar-vs-soar-lean.txt`. |
| `review/` | Template English for each variant, `blind-review.md` (written from the Lean only), and `round-trip-notes.md` (the choices the re-formalizer had to make). |

## Corpus sort

The working set has 598 versions. Of these, 298 are task agents, 171 are Soar unit tests or architecture probes, 97 are expected-output files, 23 are fragments and 9 are RL rule dumps. The task agents fall into 20 families; the largest are Blocks World (69), Water Jug (20), Robots (20), Missionaries & Cannibals (15), Towers of Hanoi (15) and Arithmetic (14). Another 32 are ungrouped.

Sorting is by name pattern plus features. Treat it as a first pass.

## Water Jug: 20 originals → 1 description, 9 variants

The parameters are: selection method (random, tie with heuristics, look-ahead, RL), whether fill is atomic or done in a substate, learning, and the avoid-states used in look-ahead and how they are scored.

Two originals are not replaced:
- **water-jug V1**: it has RL templates but RL learning is off.
- **water-jug-hierarchy V1**: it never pours (0 of 20 solved).

## Checks

- **Lean, before any Soar is generated.**
  - `conventions`: all variants conform (kernel `decide`).
  - Shortest solution is 4 task operators.
  - 0 ≤ contents ≤ volume over the whole reachable state space.
  - The task properties use `native_decide`.
- **Soar 9.6.5 vs soar-lean.** All 9 regenerated agents match: decisions, working memory, chunks, and RL values (60 decisions each).
- **Task level, regenerated vs original.** Each was run with 20 seeds (seed set after loading), capped at 500 decisions. Full table in `comparison/compare.csv`. Ops counts include the initialize operator.
  - Random, tie, tie+chunk, hierarchy and hierarchy+chunk give identical solve counts and operator distributions.
  - RL: 18/20 for both; median 118 vs 103.
  - Look-ahead + chunking: 9/20 vs 10–15/20 for the originals; median 7 for both. Both get stuck in the same ways (fill/empty loops, or over-long deliberation).
  - Look-ahead with failure states: 19/20 vs 20/20; median 7 vs 6.
  - Look-ahead + RL: 14/20 vs 10/20. The original never halts after reaching the goal.
- **Round trip.**
  1. English was back-translated blind from the Lean.
  2. A second model, given only that English, re-formalized it.
  3. The theorem `water_jug_round_trip` shows the result is equal to the original description for all 9 variants. The tie heuristic is compared by its table, because the re-formalizer grouped the same table differently.

## Build and regenerate

    cd agentgen && lake build && lake build agentgen
    .lake/build/bin/agentgen water-jug wj.json
    python3 -I tools/vsproject.py wj.json OUT path/to/default
