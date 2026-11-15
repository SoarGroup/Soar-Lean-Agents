# Option selection guide: cost and search options for tasks generated from English (v1.1, 14 Nov 2026)

Applies to the default-world libraries v2.22 or later (agent-world, selection-world). Read it before encoding any task whose English mentions cost, time, effort,
"cheapest", "fastest", "best", "value" or "optimal", and run sections 3 to 5 for every task, because a task that does not need cost options must be recorded as such.

## 1. Defaults and what they give
With no cost flag a task uses `^cost-metric none`, iterative deepening on operator count, and returns the first solution found at the shallowest depth. That solution has the fewest operators,
not the lowest cost. If every action costs the same, or the cheapest path is also the shortest, this is already optimal and no option is needed (probe P1 tests this).

## 2. Questions (ask the person one at a time, in this order; skip any the English already answers)
| # | Question | If yes | If no |
|---|---|---|---|
| Q1 | Does the English give actions a cost, duration or effort, or ask for the cheapest, fastest or best solution? | Q2 | `cost-metric none`. Stop. |
| Q2 | Is an action's cost fixed (unit) or does it depend on time and scheduled events (time)? | `^cost-metric unit` or `time`; every task operator carries `^step-cost` (unit) | |
| Q3 | Must the answer be provably the cheapest? | `^optimize true`; Q4 | cost-metric alone returns the cheapest path at the first successful depth. Optional: `^aspiration <level>` accepts any success at or below the level. |
| Q4 | Can the task supply a lower bound on the remaining cost from any state (an admissible estimate)? | task elaborates `^world.estimated-remaining-cost`; run P2 | none |
| Q5 | Is the state space large, with long solutions? | `^iterative-step cost` (IDA*, the cap rises by cost, not depth); needs Q2. With cycles of zero-cost actions it needs Q4 | `^iterative-step operator` (default) |
| Q6 | Does the goal state have a value apart from the cost of reaching it (reward minus cost)? | task elaborates `^state-value` on the evaluate-operator state and `^better higher` on `^desireds`; optional `^cost-weight` | |
| Q7 | Is there a numeric progress measure that rises toward the goal on every solution? | `^termination progress`, task supplies `^progress-score` (default: minus the number of unachieved desireds); run P4 | `termination depth` |
| Q8 | Is an answer within a factor w of the optimum acceptable, for faster search? | `^heuristic-weight w` (needs Q4) | 1 |
| Q9 | Does the task need `iterative-step tie-impasse`? | Since library v2.30 a cost metric with `optimize true` works in that mode (optimal, also with chunking); the other cost options do not apply | |
Record the answer, the English sentence that supports it, and the person's confirmation if asked. An answer that came from Claude's own reading is an assumption to be reviewed, not a fact.

## 3. Probes (run on a small instance of the task; `Soar-library-dev/tools/option-selection/probe_graph.py`)
The generator exports the instance as a state graph: edges {state: [(next, cost)]}, start, goals, optionally h and score. Then `probe_graph.report(...)` recommends flags and warns.
| Id | Test | Meaning |
|---|---|---|
| P1 | Cheapest path costs less than the cheapest of the fewest-operator paths | True: cost matters, use Q2/Q3. False: leave cost off. Checked on 16 random graphs: it predicted every case where plain depth iteration was suboptimal (2 of 16) and cleared the other 14. |
| P2 | h(s) <= true remaining cost for every state that reaches a goal | A violation loses optimality. Fix h or drop it. |
| P3 | Cycles of zero-cost actions | Do not use `iterative-step cost` without h. The library charges 0.01 per action (`^min-step-cost`); the search terminates but explores a cycle about cap/0.01 times per cap. Measured (graph with a zero-cost C<>E cycle, optimize, cap, no h): min-step-cost 0.01 did not finish in 30,000 decisions; 0.1 finished in 1,560; 0.5 in 154, all with the optimal cost 3. Set `^min-step-cost` to about a tenth of the smallest real step cost, or supply h (41 decisions). |
| P4 | Some solution never lowers the progress score | Zero decreases: progress termination is safe. Otherwise not (Hanoi, 3 discs: 56,417 decisions and a 24-move solution). |
| P0 | The model graph agrees with the agent: the agent's operator count on the small instance equals the model's fewest operators (P1 false) or its cost equals the model's optimum (P1 true) | A mismatch means a model error or a library defect; do not trust the other probes until resolved. Found one: Hanoi 2 discs, seeds 1 and 4 (see Soar-library-dev/findings/FINDING-stale-worst-preference.md). |
| P5 | Run the generated agent under each candidate configuration and compare the cost with an independent optimum (the task's check.py), using `p5_compare` | Required for the final configuration; it also picks the cheapest configuration that is optimal. |

## 4. Static check (`Soar-library-dev/tools/option-selection/check_options.py`, run on the rules file)
Errors (E) block delivery; warnings (W) go in the README with the reason they are acceptable.
| Id | Rule |
|---|---|
| O1 | Flag values must be allowed ones (`cost-metric` none/unit/time, `optimize` true/false, `iterative-step` operator/tie-impasse/cost, `termination` depth/progress); numeric flags numeric |
| O2 | optimize, heuristic-weight, cost-weight, cost-quantum, min-step-cost, aspiration need cost-metric unit or time; `iterative-step cost` too |
| O3 | cost-metric unit needs `^step-cost` on task operators (E); step-cost or h with cost-metric none is ignored (W) |
| O4 | h is used only with optimize true or `iterative-step cost`; heuristic-weight without h does nothing |
| O5 | Reminder to run P2 whenever h is present |
| O6 | Zero step-cost with cost-cap iteration and no h |
| O7 | `^state-value` and `^better higher` come together (E); net value needs a cost metric |
| O8 | Net value uses first-success semantics: optimize and cost bounds do not apply (about 1 graph in 10 returned a costlier path); cost-cap iteration needs an acyclic or bounded graph |
| O9 | Progress termination needs a score or desireds (E); run P4 |
| O10 | With tie-impasse, a cost metric needs `optimize true` (library v2.30); the other cost options are operator-step only |
| O11 | Cost-metric time: measured only on tasks without scheduled future events; with events, run P5 |
| O12 | Cost-metric without optimize or cost iteration returns the cheapest path at the first successful depth, not the global optimum |

## 5. Record: options.json (delivered with the task package, reviewed with the encoding)
`{"answers": {"Q1": {"answer": ..., "basis": "<English sentence or person>", "kind": "stated|assumption"}, ...}, "flags": {...}, "probes": {"P1": ..., ...}, "lint": [...], "measured": {"decisions": ..., "cost": ..., "optimum": ...}}`
`emit_options.py` (same folder) writes this file from the answers, the probes and the check, and stops on any lint error. The flags in the rules file must equal `flags`. The README states, for every option not used, why (for example "P1 false: cheapest = shortest").

## 6. Measured behavior (v2.22, random weighted graphs, optimum from Dijkstra)
- Unit cost, 16 graphs (7, 8, 9 nodes): depth with optimize, cost-cap iteration with and without h, and depth with optimize and h were optimal on all 16. Plain depth iteration: 2 suboptimal.
- Time mode (no scheduled events), 12 graphs (7, 8 nodes): the same four configurations optimal on all 12 after the v2.22 timing fix (before it, cost-cap without h returned a costlier path on 2 graphs). Plain depth: 1 suboptimal.
- Net value (`^state-value`, `^better higher`), 10 graphs: depth iteration and cost-cap iteration each optimal on 9 of 10; the heuristic changes nothing. Net value keeps first-success semantics, so use cost-metric with `optimize true` when the cheapest path among equal-value solutions is required.
- Decisions, 8-node graph seed 4 (unit or time): depth+optimize 434, depth+optimize+h 359, cost-cap 2200, cost-cap+h 468. The heuristic cut decisions 17 to 80 percent. Depth with optimize and h was cheapest here; cost-cap is for cases where a depth bound is impractical.
- Not discriminating (cheapest = shortest, P1 false): weighted water jug, weighted Eight Puzzle, grids with step costs. Do not add cost flags to such tasks.
- Task models (graph_models.py, run by task_options.py): Eight Puzzle (2 and 3 moves), water jug, Hanoi (2 and 3 discs), unit and weighted step costs. P1 false in all ten cases (weighted: cost of tile t = t; litres moved; disc size), so none of these takes cost options. Hanoi 3 discs: P4 reports a score decrease on every solution, as measured. Model and agent agree except Hanoi 2 discs seeds 1 and 4 (P0).
- Known limits: a stale worst preference can demote the best operator under default flags (Hanoi 2 discs; Soar-library-dev/findings/FINDING-stale-worst-preference.md); cost-cap without h on a zero-cost cycle (slow, not infinite; mitigated by P3 above); progress termination on non-monotone scores; net value with optimize; tie-impasse with cost; time mode with scheduled future events (measured on a model with unattended jobs: see CHANGES v2.23; the library's own future-event machinery needs an environment clock and is not measured).
- P5 helper: `probe_graph.p5_compare(runs, optimum)` returns the configurations that reached the optimum, cheapest in decisions first; `p5_costgraph.py` in `Soar-library-dev/tools/worldgen-v18.zip` is the driver for the cost-graph family.

## 7. Pipeline hooks
0. The task generator provides a model of its task (graph_models.py shows the form: edges, start, goals, optional h and score); `task_options.py` runs P0 to P4 on it and writes options.json.
1. Reading step: the session reads this guide with the conventions.
2. Encoding review (setup doc 5.4): Claude puts Q1 to Q9 to the person one at a time and shows the recommended flags with probe results before generating rules.
3. Generation: gen.py writes `^flag-override` from options.json, never from hand-edited text.
4. Delivery gate: `check_options.py <task>-rules.soar` has no E; P5 ran; options.json present.
5. Review: README lists unused options with reasons and every W with its justification.
6. Recording: new probe results or library limits found by the task go to a FINDING-<topic>.md in `Soar-library-dev/findings/` and to section 6 of this guide.
