# Task families: world-v6 and soar-conv groups (17 November 2026)

Two new groups beside `original/` and `world/` (15 Nov) in each `Tasks/Families/<family>/`:

- `world-v6/<variant>`: regenerated from the **original** program under World-Conventions-Spec v6 and workbook v6 (both revised 17 Nov 2026), for Soar library v2.42. 67 of 68 variants; `blocks-world-epmem` is not regenerated (see Open decision). Each variant is a flat folder: `<variant>.soar` (load file; loads `../../../../../Soar/soar-library`), `_firstload.soar` (the original's Soar settings) and the task files.
- `soar-conv/<variant>`: the original program with the Soar-Conventions.xlsx fixes applied (all 68). Same layout as `original/`.

Generators and tools are in `families-v6-tools.zip` (gen/*.py write world-v6; tools/soarconv.py writes soar-conv; tools/soarlint.py checks Soar-Conventions rows; tools/run2.py and batch.py are the harness). Results: `Families-Results-v6.xlsx`.

## Runs (Soar 9.6.50 Python bindings, library v2.42, seeds 1-3, one episode, cap 3,000; 80,000 for count-in-substate)

An episode ends at halt, at the library's "achieved" or "failed" message, or at the cap. run2.py also reports the top-level plan (operators selected in the top state).

| Group | Variants | Solved on all seeds | Solved on none | Task rules |
|---|---|---|---|---|
| original | 68 | 54 | 11 | 1,764 |
| world (15 Nov) | 68 | 56 | 10 | 1,940 |
| world-v6 | 67 | 55 | 10 | 1,579 |
| soar-conv | 68 | 54 | 11 | 1,764 |

- **soar-conv**: identical to the originals on every variant and seed (decisions, plans, results). The changes are 1,763 generated rule comments (L3-012), 59 lower-cased constants (L3-010: TicTacToe, Impasse__Operator_Tie, base-A, A-view and the like), 7 ^name tests added to operator-subgoal share rules (L3-005) and 4 unconnected conditions bound (arithmetic-smem-learn store-add/store-sub: `<up>` and `<local>` were unbound; binding them changed nothing in these runs). Remaining lint: 522 L3-039 (an indifferent preference in a proposal; kept, since the originals choose at random on purpose).
- **world-v6** against the originals, on the 52 variants both solve on all seeds: 25 have the same mean plan length (most take one decision more, for initialize-agent-world); the 16 kenken variants are shorter only by the original's print-row operators (world-v6 prints the solution with a monitoring rule); random and RL variants differ by their random draws. Other differences: mac-look-ahead solves (the original never does); blocks-world-look-ahead and water-jug-look-ahead solve 3/3 (originals 2/3); water-jug-tie(-chunk) take 10 moves (originals 23 and 8); water-jug-look-ahead-failure-states finds the 4-move solution (original 6); blocks-world-operator-subgoaling-relevant takes 2 moves (original 5); mac-look-ahead-numeric 21 crossings (original 16); blocks-world-hrl and hrl-3level take longer (RL with random exploration); blocks-world-look-ahead-state-eval plans are much longer (52 against 3; see note 6); eight-puzzle-expected-value solves 1/3 (original 2/3); water-jug-look-ahead-rl 2/3 (original 3/3). Answers checked independently for arithmetic (all problems correct in every variant).
- Not solved by any group: arithmetic (10,000 problems), arithmetic-smem, -smem-chunk, -smem-learn, -v5 (all reach the cap while answering correctly), fifteen-puzzle, knights-6, knights-8, mac and mac-rl (reach the failure state, as the originals do).

## How the world-v6 versions were written

All objects are `^world.objects.object` with handles; relations are relation objects; derived object attributes are listed as `^dont-copy-object-attribute`; legality-deciding properties are maintained (blocks `clear`/`free`, Hanoi `clear`, kenken candidate and tuple counts); handles tested with `$`; flags only through `^flag-override`; `^environment none`; task operators with `^task-operator true`, `^action-handle`, arguments, `^argument-count`, `^desireds` (count 0); composite operators with `^effect-desireds` and no application (W-COP); internal applications for every task-action operator; the library ends an episode (no task halt rules). Search control that the originals put in proposals (`+ =`) is in separate evaluation rules. Search settings: library defaults, except kenken-4-5, 6-1, 6-2, 6-3, which set `^iterative-step tie-impasse` (chosen by measurement: they fail on some seeds with operator depth and solve all with tie-impasse).

## Findings

1. **Duplicate operators from the generator pattern.** A proposal that tests `(<ds> ^unachieved <any>)` (worldgen's template) fires once per unachieved desired, so each move is proposed N times. With 2 desireds, mac-look-ahead failed within 3,000 decisions; testing `^desireds.unachieved-desireds true` (L8-024) instead, it solves 3/3 at about 700 decisions. worldgen's `wg.py` and the generated test-set tasks use the duplicating form.
2. **The eight-puzzle claim in spec section 4 does not hold.** "Eight Puzzle uses 6 tiles" (the other tiles follow by parity): a BFS over the 181,440 boards reachable from this start shows that no choice of 6 cell bindings (tiles, with or without the blank) determines the goal; 3 reachable boards always remain. world-v6 uses one desired, `board ^solved true`, derived positively from a static `^home` and a derived `^at-home` per tile.
3. **Unquoted letter-digit attribute names.** Soar reads `^d1` as the symbol `D1` (upper case), so rules written with `^d1` do not match smem facts stored as `^|d1|`. world-v6 arithmetic quotes `|d1|`, `|d2|` (the originals already did). A convention row may be worth adding.
4. **Internal operators with implementation substates** (arithmetic get-digit2, borrow, borrow-from, get-digit1, add-digits/subtract-digits in smem-learn) are given `^desireds` with `^desired-count 0` so that agent-world names their substate's problem space; L9-022 states this only for task operators.
5. **water-jug-tie**: the original's own tie space cannot coexist with selection-world (L14-001, L14-002), so its last-operator heuristics became preferences in the task state; the variant no longer exercises a tie impasse.
6. **blocks-world-look-ahead-state-eval**: the original recognises success only at the top state, so look-ahead is guided by expected values alone; the library computes success in every state (L8-025), which changes the search (much longer plans).
7. **Chunking settings**: each variant keeps its original's `chunk` setting; the spec says generated tasks run with learning off and leaves the question open (proposed convention 5).

## Open decision (specification silent)

`blocks-world-epmem` uses episodic memory as the action model in look-ahead: it excises two default rules, moves `^untried-tied-operator`/`^tried-tied-operator` itself and writes `^symbolic-value partial-success ^numeric-value 2.5` onto selection evaluations. The world conventions require an internal application rule for every task-action operator (L9-012) and keep selection bookkeeping in selection-world; nothing says how a task supplies a learned or retrieved action model, or reports an unknown outcome, in look-ahead. Not regenerated until that is decided.

## Not done

VisualSoar project files and datamaps for world-v6 (flat folders, like the 15 Nov versions); the regression test set is not updated; nothing pushed to GitHub.

## Update, 18 November 2026

world-v6 was regenerated with the 18 November conventions; the generator (`gen/v6.py`) now passes every agent through `gen/convpass.py` (in `families-v6-tools.zip`). The pass:

- adds a problem-space test (`^name` or `^problem-space.name`) to every rule that lacks one (L3-005), except initialization rules, problem-space elaborations, impasse tests and superstate propagation rules;
- adds one English comment per rule group (L3-012);
- removes `+ =` from proposals in the RL variants (`-rl`, `hrl*`; L3-083).

Results are unchanged on every variant and seed. Decisions or top-level operators changed in 4 variants (mean decisions, old to new): blocks-world-hrl 431 to 1,134 (RL proposals no longer carry an indifferent preference, so exploration is wider), blocks-world-hrl-3level 140 to 121, water-jug-hierarchy 413 to 116 and water-jug-hierarchy-chunk 164 to 54 (random choice; the problem-space tests change the order of the random draws). Eight- and fifteen-puzzle chunking variants learn fewer chunks (e.g. 15 to 9), and the water-jug look-ahead variants learn one chunk fewer. Families-Results-v6.xlsx has the new world-v6 values. blocks-world-epmem is still not generated (open decision below).

Prepared by Claude, supervised by John E. Laird.
