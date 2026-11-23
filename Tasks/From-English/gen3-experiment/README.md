# gen3: Soar agents written from English under three conditions (21-22 November 2026)

Written by Claude, supervised by John E. Laird.

## What this is
Fresh writer sub-agents each wrote one Soar agent (library v2.45) from a short English task statement, for 14 task families, under three conditions:
- **conventions**: the two convention specs, the library and the task statement only;
- **examples**: plus all example agents (families world-lean, English world agents, Rosie agents);
- **heldout**: the examples with every agent of the same task removed.

Every agent was rerun in one harness (run2.py, seeds 1-3). All 126 runs succeed (all 42 agents, 3 seeds each).

## Changes on 22 November 2026
- **Tower of Hanoi:** 3 disks (was 5) in the task statement and the family agents. The three Hanoi agents were regenerated; the 5-disk agents are kept as `out/*/towers-of-hanoi-5disks-superseded`.
- **Knights:** the task is now to count closed tours from b23 (column 2, row 3) and stop after 100 closed tours or 30,000 moves (each knight move and each backup counts), as the family agents now do. The three knights agents were regenerated; the earlier single-tour agents are `out/*/knights-opentour-superseded`, and one agent written to an intermediate rule is `out/examples/knights-20k-superseded`.
- **Search control (Tower of Hanoi):** `tasks-src/towers-of-hanoi/task.md` holds the task with a `Search control` section (SC-1). `tools/control.py` produces the text each condition sees: `tasks/towers-of-hanoi/task.md` (none) and `tasks/towers-of-hanoi-sc1/task.md` (SC-1). The agents written with SC-1 are in `out/*/towers-of-hanoi-sc1`.

## Contents of gen3-2026-11-22.zip
- `WRITER-INSTRUCTIONS.md`: what every writer was told.
- `tasks/`, `tasks-src/`: task statements.
- `conventions/`: the convention specs the writers read (as of 21 Nov 2026).
- `examples/all/`: the example agents. The `heldout-<family>` folders are left out to save space; each is `all` minus that family's own agents (see `QUEUE.txt`).
- `out/<condition>/<family>/`: the agents, each with a REPORT.md listing every file the writer read. Some REPORT.md files were saved by the main session from the writer's message, and say so.
- `rerun/`: harness output of the reruns.
- `tools/`: run2.py, rerun_all.py, make_xlsx.py, control.py.
- `results/`: the results workbooks.

## Results workbook
`gen3 three-condition results (22 Nov 2026).xlsx`:
- **Summary, Runs and Notes sheets:** cover all 42 agents.
- **Search control sheet:** Rosie Tower of Hanoi with and without SC-1 to SC-3, the gen3 SC-1 agents with the rule removed, and the evaluation-order tests (L15-026).
- **Formatting:** failures are filled orange.

The library is loaded by absolute path (`/home/claude/lib244/soar-library`) in the session workspace; to run an agent here, change the pushd path in its main file to `Soar/soar-library`.
