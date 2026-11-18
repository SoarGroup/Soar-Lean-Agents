# Five houses (zebra puzzle) under the world conventions

## Update, 15 November 2026: shared library v2.30

**Library.** This package no longer carries its own `lib/`. `zebra.soar` loads the shared library, Soar library v2.30, from `Soar/soar-library` in the Soar-Lean-Agents repository; the path (`../../../Soar/soar-library`) assumes this folder is unpacked in its place, `Tasks/From-English/zebra-world`. To use another library location, run `SOAR_LIBRARY=/path/to/soar-library python3 gen.py`, which rewrites the loader. The flags are set with `^flag-override` (only the values that differ from the library defaults). The rules are those of test set v1.27 (`world__zebra`); the earlier, library-specific notes below are kept as written and refer to the library copy embedded at the time (lib/ and its local fixes).

**Results with v2.30 (Soar 9.6.6, 15 Nov 2026).** Seeds 1 to 10: every run solved with 99 deductions, all checked by `check.py` (0 wrong, answer correct: the Norwegian drinks water, the German owns the zebra); 132 or 140 decisions, about 0.6 s CPU. `sample-run-seed1.txt` is the seed 1 run with v2.30.

---

`zebra.soar` loads the world libraries (lib/world2, no-environment mode) and `zebra-rules.soar`, which holds 87 task rules. Fifty of those rules only build the printed matrix.

`gen.py` writes `zebra-rules.soar`. The 14 clues are a data table in `gen.py` and become world objects; the reasoning rules are generic over them. The English is a comment at the top of the rules file.

## Running

- **Run the agent:** `python3 run.py [seed]` prints every deduction with its reason, the elimination matrix where deduction stalls, the branch, the solved matrix and the answers. The library interrupts once when the goal is reached; the runner continues past it.
- **Check a run independently:** `python3 run.py 1 | python3 check.py` finds the solution by brute force and confirms it is unique. It then checks that no printed deduction removes a true value, that the branch is right, and that the answers are correct.

## Results (Soar 9.6.50)

- **Seeds 1–30:** every run was correct and gave the answer below. Each run took 99 deductions (77 before the branch) and 132 or 140 decisions, in 0.4–0.7 s of CPU.
- **Answer:** the Norwegian (house 1) drinks water; the German (house 4) owns the zebra.
- **Difference from the classic puzzle:** the classic clue "the Blends smoker lives next to the water drinker" is not in this version, but the solution is still unique.

## How it reasons

- **World:**
  - house-1..5, each with `^position`, `^left`/`^right` neighbour handles, and a `^candidate` for every value still possible.
  - 25 value objects with `^group` (their category); 5 category objects; 14 clue objects; and the puzzle, whose desired state is `^solved true`.
- **eliminate (task operator):** removes one candidate. It is proposed for each of these reasons:
  - **position** (clues 9, 10);
  - **same house** (clues 2–4, 6–8, 13, 14): x cannot be here if y cannot;
  - **left-of** (clue 5);
  - **next-to** (clues 11, 12, 15): no neighbour can hold the partner;
  - **naked single:** a house has one value left in a category;
  - **hidden single:** a value has one house left.

  All eliminations are best and indifferent, and only real ones are printed.
- **Branching:** when no elimination applies, the agent prints the matrix and proposes `assign` for each value of the first open cell (house 1's pet: cats or zebra). The tie is settled by look-ahead (selection-world with iterative deepening):
  - a branch that empties a cell or leaves a value without a house is a failure;
  - one that solves the puzzle with no elimination pending is a success.
- **Solved:** every cell holds exactly one value and no elimination is proposed. The second condition matters because a full assignment can still break a clue.

## Library findings from this program

1. **The look-ahead world copy skips attributes named `^category`** (and `accessible`, `mass`, `instance-of`). With `^category` on the value objects, every copied cell looked empty, so whichever branch was evaluated first was judged a contradiction and rejected. Renamed to `^group`.
2. **In look-ahead every operator is best.** `apply*operator*maintain-operator*preconditions-satisfied` makes every operator best, so a task's best preference cannot hold a branch back behind deductions there. The branch is therefore proposed only while no eliminate is proposed.
3. **Non-task operators outrank task operators.** `agent-world*compare*task-operator-non-task-operator` makes every non-task operator better than every task operator, so the matrix print also waits until no eliminate is proposed.
4. **`initialize-agent-world` stays proposed** after it builds `^world` (as in the artists program), so it is rejected once `^world` exists.
5. **`top-goal*halt*success*desireds-count` interrupts** the run when the desired is achieved.
