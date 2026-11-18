# Soar agents from Rosie instructor statements: pilot and block puzzles (16 November 2026)

**Runnable: all three pilot agents.** Fox-goose-bean, Tower of Hanoi and tic-tac-toe were generated from the instructor statements and world files of their dialogs, under the world conventions, on the shared library v2.34. All three load without errors or warnings and pass the derived-attribute check. Their goal and failure tests give the expected answer on all nine example states, and they solve their tasks.

## Results

| Task | Task rules | Example states (goal / failure) | Runs | Plan |
|---|---|---|---|---|
| tower-of-hanoi (3 blocks) | 11 | init F/F; final T/F | seeds 1-3 solved; 35,392-46,450 decisions; seed 1 19 s | 7 moves every seed (shortest); every move legal by independent replay |
| fox-goose-bean | 16 | init F/F; fail-fox F/T; fail-fox2 F/T; final T/F | seeds 1-3 solved; 3,437-16,517 decisions | 7-25 crossings (shortest 7); every crossing legal, no losing state, by independent replay |
| tic-tac-toe (agent red, environment blue) | 23 | init F/F; final T/F; fail F/T | 10 games: red wins 9, blue 1; 505-609 decisions | no illegal red move; the agent's own result matched the environment's in every game |

Settings (intake checklist, P6 probe): the library defaults were kept for both puzzles. Tie-impasse gave longer plans: Hanoi 216 moves against 21 over three seeds, fox 67 against 43 crossings. The probe was not run for tic-tac-toe because its harness has no opponent.

Soar: SoarSuite 9.6.6 (the bug-fix release; its kernel reports 9.6.50, build of 6 Nov 2026). The runs were first made on 9.6.50 built from SoarGroup master (30 Oct 2026), because the PyPI soar-sml 9.6.5 rejects `$`; on 9.6.6 every state check, plan and game result is the same.

## What the pilot showed

1. **The statements map onto the conventions with few constructs.** Actions become task operators; definitions that test absence become maintained one-argument relations; positive definitions are expanded in place. "You lose" becomes `^failure`, and the goal becomes `^goal-met` on a task object, read by one object-property desired (`tools/rosie-language.md`). Every rule names the statement it comes from.
2. **The example states are a strong check.** Writing the rules with each `fail-*` and `final-*` world as the initial world, and checking goal and failure there, tests the reading of the English before any search. It caught one error in the test harness (not in the agents) on the first run.
3. **Rosie's language needs a few readings that the dialogs do not state.** For example, "clear" is defined for locations but applied to blocks, "larger than" is used with its arguments reversed, the boat counts as a block, and unnamed actions need names. Each is in its task's assumption ledger. They recur across tasks, so the shared readings in `rosie-language.md` should carry over.
4. **Plan quality is a library matter, not a translation matter.** With no repeated-state rule in the English, the fox agent sometimes takes a block over and straight back (up to 25 crossings), even with unit cost and `^optimize true`. Hanoi is optimal but costs about 40,000 decisions, because nothing prunes undoing the last move. Adding such rules would go beyond the instructor's statements.
5. **Games need the opponent decision.** As decided, the environment plays the other side and the agent looks ahead over its own moves only. It therefore does not block threats (seed 2). Anticipating the opponent would need adversarial search, which the library does not have.

## What is not automatic yet

Each task's `gen.py` (operators, effects, maintenance of each concept, goal and failure) was written by Claude from the statements. Shared code covers the world files, relations, initialization, problem space, example-state variants, running and plan checking (`tools/`). To do the other 51 dialogs at scale, the next step is a parser from the statement forms to a small task description, from which the operator, maintenance, goal and failure rules are generated. The concept-maintenance rule (which relations each action adds and removes) is the part that needs the most care to derive automatically.

## Deviations and open points

- Tic-tac-toe: the application of a move by a block that sits on nothing tests the absence of an on relation (local negation in a look-ahead application, W-CHK-009, Should). It has no effect with chunking off.
- Turn order (red first) and draws (neither side can move) are environment choices; the dialog has neither.
- The world conventions have no three-argument relation. Rosie's `linear` sets became line objects with a binary `member` relation, which is within the conventions.

## Block puzzles (16 November 2026, afternoon)

**Runnable: all nine block puzzles. Seven solve with the shortest plan on every seed; Tower of Hanoi with 4 and 5 blocks does not solve** (named gap: their 15- and 31-move solutions are longer than the library's look-ahead depth limit of 12). No block puzzle needs an environment beyond marking commands complete.

| Task | Rules | Example states | Seeds 1-3 | Plan |
|---|---|---|---|---|
| tower-of-hanoi (3) | 11 | correct | 35,392-46,450 decisions | 7 moves (shortest) |
| tower-of-hanoi-4 | 11 | correct | no move within 500,000 decisions (seed 1) | none: needs 15 |
| tower-of-hanoi-5 | 11 | correct | no move within 100,000 decisions (seed 1) | none: needs 31 |
| blocks-world | 11 | correct | 1,373-3,288 decisions | 4 moves (shortest) |
| blocks-world2 (world-blocks) | 11 | correct | 1,373-3,288 decisions | 4 moves (shortest) |
| sorting | 11 | correct | 3,341-3,649 decisions | 3 moves (shortest) |
| stacking-frogs | 18 | correct; 6 moves proposed at the start, as the instructor said | 158-195 decisions | 3 moves (the instructor's "three steps") |
| king-stacking-frogs | 18 | correct; 6 moves at the start | 213-359 decisions | 3 moves (shortest) |
| lazy-stacking-frogs | 18 | correct; 5 moves at the start | 76-100 decisions | 3 moves (shortest) |

Every plan was replayed independently (`tools/check_plan.py`): every move legal, goal holds. The P6 probe chose tie-impasse for the three frog puzzles (same plans, fewer decisions) and kept the defaults for the others; under tie-impasse sorting solved only 1 of 3 seeds within 200,000 decisions, and the blocks-world probe was stopped after 38 minutes without finishing.

What the block puzzles added:
1. **Rosie's own disambiguation questions are usable checks.** In the frog dialogs Rosie asked how many instances the action has in the initial state ("6 or 4?"). The two numbers are the two readings of "the number of the locations between"; the instructor's answer picks one, and the generated agent proposes exactly that many moves.
2. **Counting** ("the number of the blocks on C") is a mutable attribute kept by the moves, and "the number of locations between" a static relation from the world file's coordinates. Neither needs arithmetic in a condition.
3. **The generation is now shared.** The nine tasks come from four operator builders (`tools/rosie_blocks.py`) and four task functions (`tools/rosie_tasks.py`); each folder's `gen.py` is one call. The original Hanoi agent regenerated this way behaves identically.
4. **The depth limit is the binding constraint**, not the translation: the 4- and 5-block Hanoi agents have correct goal tests and legal moves, but look-ahead alone cannot reach a solution. Solving them needs a deeper look-ahead or knowledge the instructions do not give.

## Logic puzzles (16 November 2026, evening)

**Runnable: all twelve.** Library v2.39. Every example state is classified as the instructor intended: 39 of 39, including the fail states where the goal also holds, which count as lost.

| Configuration | Correct runs (seeds 1-3) | Notes |
|---|---|---|
| Library v2.37 (failed moves worst) | 14 of 36 | Killer sudoku and shuffle 3/3; map coloring and kenken 2/3; sudoku, jigsawdoku, logi-five, kenken2 1/3; sujiko, suko, kakuro, survo 0/3 |
| Library v2.39 (failed moves rejected) | 34 of 36 | Every puzzle on every seed except sujiko seeds 1 and 2; about 2-4 times the decisions. Same decisions as the experiment overlay (`tools/experiments/failure-becomes-reject.soar`) on v2.37 |

Each run was replayed independently with `tools/check_plan.py`. That replay had a bug, now fixed: it read a clue object's id as the target sum.

**Why v2.37 failed.** In selection-world a failed evaluation becomes a worst preference, not a reject. A nested tie that runs out of operators to evaluate reaches a state no-change. The soar-base tie-breaker then gives every tied item `=, <`, so an operator already known to fail can be chosen, and its failure is returned upward as the result for a move that is good. Rejecting failed moves removes this, and it also makes losing take precedence over the goal: a move whose look-ahead state both reaches the goal and loses is rejected.

**Sujiko seeds 1 and 2 on v2.39.** The puzzle has one solution (loc-2-1 5, loc-3-1 4, loc-1-2 3, loc-2-2 1). The run goes wrong in four steps:
1. At look-ahead depth 4, the evaluations of all four correct moves at the initial state come back as failure.
2. The agent then takes the only move left that is not rejected (loc-3-1 1), which leads to a dead end.
3. After two more writes, every remaining move is rejected.
4. The top state reaches a state no-change, and agent-world's `wait` runs until the decision cap.

Starting one correct write further on (three empty cells), all five seeds solve. Why the correct moves are evaluated as failure at depth 4 is not yet found.

**Applied in library v2.39** (by Claude at JL's direction, 16 Nov 2026, on top of JL's v2.38; `Soar/soar-library/CHANGES.md`):
1. In `selection-world/Operator_Tie/elaborations.soar`, `selection-world*compare*selection*select*failure-evaluation-becomes-worst-preference`: change the action to `(<superstate> ^operator <operator1> -)`, and rename the rule back to `...failure-evaluation-becomes-reject-preference`.
2. In `selection-world/elaborations/top-state.soar`, `selection-world*apply*top-goal*halt*success` and `...*halt*success*desireds-count`: add `-^<< prohibit-failure failure exhaustion-failure >> <desireds>` to the state condition. The test is on the top state, so no chunk is built from it.

Item 2 changed no plan here. It only stops a lost top state from also printing a success. Test set v1.32: 507 of 515 tests identical to v2.38 (see CHANGES.md).

## River crossings (16 November 2026, evening)

**Runnable: all four.** Library v2.39. All 14 example states are classified correctly. Two kinds of search control were added, neither taught (JL's decisions, 16 Nov 2026):
- **In look-ahead:** a move whose result is a situation already on the look-ahead path is rejected.
- **Real moves:** a move back to a situation already visited gets a worst preference, as in `Tasks/From-English/mc-world`.

| Task | Rules | Library v2.39, seeds 1-3 | Shortest |
|---|---|---|---|
| family-crossing | 23 | 9 crossings on every seed (the instructor's "nine steps"), 3,461-3,767 decisions | 9 |
| jealous-husbands, two couples (init-husbands2) | 24 | 5 crossings on every seed (the instructor's "five steps"), 807-1,265 decisions | 5 |
| jealous-wives, two couples (init-husbands2) | 24 | 5 crossings on every seed, 957-1,259 decisions | 5 |
| missionaries-and-cannibals, init-mac2 | 32 | 5 crossings on every seed, 1,262-1,655 decisions | 5 |
| jealous husbands and wives, three couples; missionaries and cannibals, three of each | | seed 1: no move within 300,000 decisions | 11 |

Every plan was replayed independently with `tools/check_plan.py`: every crossing legal, goal holds.

**Compared with v2.37** (no control on real moves): family crossing 9 crossings in 5,194 decisions. The three-couple jealous husbands solved, but in 453 crossings. Jealous wives (574 crossings) and missionaries and cannibals (18 crossings; 333 with tie-impasse) did not solve. The agent made real moves that undid earlier ones.

**The three-couple and three-pair worlds on v2.39.** With failed moves rejected, a failed move can no longer be chosen at random, so the agent never commits to an unverified first move. The look-ahead keeps deepening toward the 11 crossings needed. Tie-impasse steps give 2 legal crossings in 300,000 decisions. mc-world solves its version of the same puzzle in 11 crossings at decision 495 with tie-impasse steps. The difference between the two agents is the next thing to examine.

**A bug in the first version of the real-move control.** The first version recorded the result of the operator just selected as visited. That made the selected operator worst, so Soar replaced it before its command completed, and a second command went out on the old state: an illegal move, caught by the plan checker. The rule now records only the situation being left.

## Files

- `tools/`: `rosie_gen.py` (shared generator), `rosie_blocks.py` and `rosie_tasks.py` (block-puzzle operators and tasks), `rosie_logic.py` and `rosie_river.py` (logic puzzles and river crossings), `experiments/` (library overlays tried, not adopted), `rosie-language.md` (the shared reading of the language), `run_agent.py` (run or check an example state), `check_plan.py` (independent replay), `probe_settings.py` (copy of the P6 probe), `wg.py` and `check_derived.py` (worldgen v19).
- In each of the three task folders: `gen.py`, `<task>.soar` (loader), `<task>-rules.soar`, `README.md` (run, results, assumption ledger), `probe*.json`; tic-tac-toe also has `run.py` (the environment).
