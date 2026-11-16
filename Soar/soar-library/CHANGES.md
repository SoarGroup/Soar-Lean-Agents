# Changes after the restructure (v2.14 onward)

From v2.14 the library tree is edited directly; build.py and patches.py remain as the record of the restructure. Each change below was
checked with the regression test set (all tests unchanged with default flags, except as noted in the v2.23 and v2.24 entries) and, where new behavior was added, with new tests.

## v2.35 — Datamap: ^duplicate-of is an identifier  16 Nov 2026
Datamap only; no rule change, so the test set was not rerun. Following the decision of 13 Nov (datamaps/datamap-conflicts.txt: duplicate-of is SOAR_ID, it points to the original), the remaining STRING `^duplicate-of` edge on the world object is removed from agent-world, object-world and selection-world (agent-world.vsa.json, object-world.vsa.json, selection-world.vsa.json and datamaps/library-datamap.json); the object keeps its SOAR_ID `^duplicate-of`. thor-soar and thor-tasks are not changed yet: their datamaps are brought up to date in the Thor-Soar pass (they still list a STRING `^duplicate-of` and the old `^holding-object none`).
Packaging: from this release the zip's top folder is `soar-library/`, so deleting `Soar/soar-library` and unzipping the release in `Soar/` installs it.

## v2.34 — Search defaults confirmed; settings chosen per task  16 Nov 2026
No rule changes. The defaults stay `^iterative-step operator`, `^cost-metric none`, `^optimize false`; comments in the three flag files now say why.
Measured on the 171 library tests and the 68 step 6 world variants (seeds 1-3), against v2.33:
- `optimize true` as a default made no plan better on any task without costs and cost decisions everywhere (Hanoi 630 to 809, eight-puzzle 1,856 to 5,597, artists-2 648 to 3,672; eight-puzzle flat/static stopped solving within 3,000).
- `cost-metric unit` alone changed no plan in any of the 171 tests and raised decisions in 42 (eight-puzzle 492-776 to 1,767-1,947, blocks world, Hanoi, water jug, artists-2, wizards).
- `iterative-step tie-impasse` as a default broke tasks where every step is a choice (water-jug-look-ahead, eight-puzzle: the look-ahead runs past the depth bound; FINDING-tie-impasse-unbounded-continuation.md). A fix for that was tried and not adopted (artists-2 went from 165-282 to 2,160-4,226 decisions).
So each task sets what helps it in `^flag-override`, chosen with probe_settings.py (Soar-library-dev/docs/Search-Settings-Intake-Checklist-v1.md): tie-impasse for generated Blocks World, mc, blocks-world-look-ahead, kenken-4-5 and kenken-6-1 to 6-3.

## v2.33 — Only the top state counts applied operators  15 Nov 2026
Fix. The substate count of v2.32 (`selection-world*apply*state*applied-count*first` and `...*applied-count`, ground-state.soar) is removed. Those rules made o-supported WMEs on an operator no-change substate. Because they test the substate's selected operator, Soar adds the operator's proposal conditions (which test the shared world) to the substate's goal dependency set, and the substate was removed and rebuilt after every action that changed the world (`trace --gds`: "Removing state S3 because element in GDS changed"). The nine hierarchical step 6 world variants took 20-50% more decisions on v2.32 (blocks-world-hierarchical 63, hrl-3level 101-141, towers-of-hanoi-mea 59, water-jug-hierarchy +30%). With the rules removed they return to the v2.31 counts (43; 70-83; 48; 133-897).
Probes showed that any o-supported WME on such a substate has this effect, even one that tests only the operator's name; a count on the superstate operator instead is a result and is chunked. So a per-substate count has no place for now; the substate count was not used by any stamp. The v2.32 guarantee is kept: a substate never changes the world's count (no max-elaborations loop).
Test set: not yet rerun on this release.

## v2.32 — The applied count is local to the state  15 Nov 2026
Fix. In v2.28 to v2.30 the rules `selection-world*apply*world*applied-count*first` and `...applied-count` also fired in a substate that shares the real world. The top state and the substate then each saw a `^counted-operator` on the world that was not their own operator and rewrote it in turn, without end (`Warning: reached max-elaborations` on every decision; it happens with `chunk never` too). Found when the step 6 task families were ported to the world conventions: arithmetic-solve-problem, arithmetic-v5, blocks-world-hierarchical, blocks-world-hierarchical-lookahead, blocks-world-hrl-3level and towers-of-hanoi-mea.
The top state keeps the count on the real world, unchanged. A substate keeps its own `^applied-count` and `^counted-operator` on the substate, starting from zero, and does not change the count of the world or of any other state; two substates never share a count, even in the same problem space. (v2.31, replaced by this release, counted in the top state only, so operators applied in substates were not counted.)
Not wired yet: the substate count is not part of any stamp, so a chunk built in a substate is not tied to the substate's count.

## v2.30 — Tie-impasse depth with a cost metric and optimize finds optimal solutions, with and without chunking  15 Nov 2026
Applies with `^flags.iterative-step tie-impasse ^cost-metric unit|time ^optimize true` unless noted. Background: FINDING-chunking-overgeneral.md (update of 15 Nov) and World-Conventions-Spec-v6.
- Fix (all modes with a cost metric): `agent-world/elaborations/cost.soar` no longer loops to max-elaborations; the step cost an operator states is copied to `^effective-step-cost`, with 1 as the default when none is stated, and the apply rules read that.
- Fix (iterative deepening): `remove-evaluation` is proposed only for an operator that is no longer proposed in the superstate. A failure-cutoff worst preference had removed an evaluation while its operator was still tied, and the evaluation was rebuilt and removed in turn.
- New `lower-bound.soar`: every evaluation starts with `^lower-bound none` (all modes); a branch cut off by the depth gives the lowest cost bound below the evaluation, passed up through nested selections. A top selection checks bounds (`^bound-check true`): an evaluation may lose only when it is `^closed` (no bound, or a bound not below the best value). Otherwise the top tie stays, the depth is incremented, and the open evaluations are evaluated again. Before, a costly success found along a chain of forced operators won over cheaper branches that had been cut off (water jug B1: 10 operators instead of 8).
- The rules that make an operator lose (reject, worst, worse, better-than) test `(<loser> ^closed true)`; in every other mode every evaluation is closed, so behaviour there is unchanged.
- New comparisons: the cheaper success is better, without `^better` on the desireds; a success is better than a depth-exhaustion with no bound below its cost; in nested selections a depth-exceeded or depth-exhaustion branch with a bound below a success's cost is followed first. The unary success-best preference is used only without tie-impasse depth and optimize (`^unary-success-best`), because its chunk tests only the successful operator.
- Learning: every rule that writes a value into an evaluation tests `^lower-bound $ <lower-bound>`, so a value computed below a depth cut-off is learned with that bound and never fires in a fresh evaluation. With a cost metric a success is returned only by the rule that also returns its path cost. `worse*failure-cutoff-numeric-value2` names the operator that holds the best value and tests that it is another operator (a second version covers a best value passed down, `^passed-down-minimum`).
Results, tie-impasse depth with cost and optimize (moves; median decisions): water jug B1 8 on all 5 seeds (6,208), D1 8 (5,530), B3 8 (402), D3 8 (648); Hanoi 3 on all 6 (488); blocks world 3 (725); mc 11 (163); artists-2 5, 5, 5 (1,294). With `chunk always` and literal handles in the task rules (worldgen v18): the same moves on every water jug, Hanoi and blocks-world seed, in a first run and in a second run that starts with the first run's chunks; artists-2 5, 7, 5, then 5 on all in the second run.
Default flags: no solution changed. Test set v1.27: 94 tests changed decisions (85 cost graphs, blocks world, Hanoi, mc, artists-2, artists-3), the action sequences of all env-complete tests are unchanged, mc and artists-2 still succeed; artists-3 seed 2 no longer solves within 20,000 decisions (known regression again). Two Soar 9.6.50 defects with `$` were found and reported (soar-dollar-bugs.zip); the library does not use either construct.

## v2.29 — Stamps elaborated only by the state that owns the world; one-argument declared relations are copied  14 Nov 2026
- The `^stamp` elaborations (ground-state.soar) fire only in the top state (real world) and in the evaluate-operator state (look-ahead copy). Before, an operator no-change substate that shares its superstate's world also fired them, the stamp became a result, and a chunk was built for it.
- New `selection-world*elaborate*evaluate-operator*default-state-copy-relation*declared*one-argument`: a relation the task declares with `^copy-relation` that has `^argument1` and no `^argument2` (a maintained `clear`) is copied into the look-ahead world.
- No change in behavior without chunking: decisions and traces unchanged in all 296 tests except the 12 Hanoi and blocks-world tests whose task rules changed (test set v1.26, `clear` maintained instead of derived).
- Chunking: see FINDING-chunking-overgeneral.md. With `clear` maintained, blocks world with `chunk always` is optimal on all seeds (3 moves, median 276 decisions against 384 without learning); Hanoi is not (6 and 4 moves on 2 of 6 seeds), because a chunk does not record that a move left other objects unchanged.

## v2.28 — Failure and depth-limit results depend on a world version stamp instead of an explicit grounding pass  14 Nov 2026
New flag `^flags.failure-grounding` (selection-world/_flags.soar): `counter` (the default), `explicit` (the v2.24 to v2.27 grounding pass, unchanged) or `none` (no grounding; reproduces the Hanoi stale worst preference).
- The real world has `^applied-count`, 0 at `initialize-agent-world` and incremented once for each operator applied with `^pre-conditions-satisfied true` in any state whose world is the real one (top state and operator no-change substates that share it).
- A look-ahead world gets a new version (`^local-version`, `make-constant-symbol`) each time an operator is applied to it; before that it carries the stamp of the world it was copied from (`^parent-stamp`). Each version rule tests the previous stamp, so a justification leads back to the real count.
- Every world has one `^stamp`. The failure substate and the selection state test `^superstate.world.stamp $ <n>` before a failure or depth-limit result is made, so the result retracts when that world changes and a chunk keeps the stamp as a constant and never matches another world version.
- Explicit grounding never reads the count and stamp attributes.
Results (no learning): Towers of Hanoi 2 discs seeds 1 to 6, 3 operators, median 152 decisions (explicit 218); water jug 7/9 world-convention agents 8 operators on every seed, B1 median 4,403 decisions (explicit 7,098); mc 11 crossings, 479 decisions (1,154); cost-graph paths unchanged. artists-3 seed 2 solves (10,068); seeds 1 and 3 do not within 20,000.
With `chunk always` the agents now run (with explicit grounding, chunking was killed by the system, out of memory) but some solutions are longer than optimal: Hanoi 3, 3, 4, 3, 4, 3 operators; water jug B1 one seed of five 24. The failure and depth-limit chunks test the stamp; the transfer comes from success and depth-exceeded chunks (not grounded). Not diagnosed further. The library sets no chunking mode (Thor-Soar sets `chunk flagged` with force-learn on evaluate-operator states).
Caveat: with an external environment the count changes when the operator is applied, and the world when the action completes.
Test set v1.25.

## v2.27 — A task can declare which object attributes its grounding reads  14 Nov 2026
New problem-space attribute `^ground-object-attribute <att>` (multi-valued). When a task declares it, grounding (ground-state.soar; both the state no-change failure and the depth-limit results) reads of each world object (an `^object` of the world's `^objects`) only `^object-handle` and the declared attributes; the world's other wmes and the desireds are read as before. Without the declaration nothing changes (two new elaborations fire; 18 test baselines changed only in firings and wme_changes).
The declaration is the task's claim that a failure depends on nothing else: not on static properties, derived attributes or the look-ahead path history (for example the artists boat's `^visited` labels, which are no longer read).
artists (test set, 2 and 3 pairs) declares `^ground-object-attribute side`: who is on which bank and the boat's side, which determines the other bank. A grounding pass fell from 75 to 90 decisions to 38. It also now lists its derived bank attribute `^dont-copy-object-attribute empty`.
Results: artists-2 still solves (958, 454, 392 decisions; v2.26 1,403, 384, 482). artists-3 does not solve within 40,000 decisions on seeds 1 to 3, with or without the declaration (v2.26 solved seed 3 at 17,601; at 40,000 the seeds made 0 to 2 of the 11 crossings). Grounding is now about half of its decisions; the rest is the look-ahead itself: iterative deepening to the 11 crossings with only path-based repeated-state rejection.
Known, not caused by this release: with `chunk always`, artists-3 is killed by the system (out of memory) within 2,300 to 4,500 decisions with or without the declaration, after only 4 to 6 chunks; the same happened to the water jug agents without repeated-state rejection on v2.25. Not diagnosed.
Test set v1.24.

## v2.26 — Grounding never follows ^duplicate-of  14 Nov 2026
`selection-world*propose*failure-evaluation*ground-wme` (ground-state.soar) no longer reads `^duplicate-of`. That link joins a look-ahead world, its objects and its desireds to the copy they were made from, so every grounding pass read every ancestor world back to the real one: about 90 more decisions per look-ahead level (artists-3: 160, 255 and 340 decisions per pass at levels 1, 2 and 3; now 75 to 90). The copy's wmes are derived from the parent's, so the failure still depends on the parent world through them. The rule serves every grounding (state no-change failures and the depth-limit results of achieved-max-depth.soar).
Results: Towers of Hanoi 2 discs seeds 1 to 6 still 3 operators (the v2.24 stale-worst fix holds). Test set: 24 baselines changed, solutions unchanged where checked; decisions fell in 22 (mc 2,466 to 2,746 became 1,150 to 1,163; artists-2 seed 1 4,415 to 1,403). Water jug 7/9 (world conventions, repeated-state rejection, no learning): median 17,878 became 7,099 decisions, still 8 operators on all 5 seeds.
artists-3: seed 3 now solves (17,601 decisions); seeds 1 and 2 still do not within 20,000 or 60,000 decisions. Test set v1.23.

## v2.25 — A dead end no longer fails the operator two ties up before its siblings are evaluated  14 Nov 2026
Fix for FINDING-early-failure-propagation.md. `selection-world*apply*initialize-failure-evaluation2` (iterative-deepening, Impasse__State_No-Change/initialize-failure-count.soar) gave `^symbolic-value failure` to the evaluation of the tie above the nearest tie at the first dead end, when the nearest tie had no depth-limited evaluation yet. It now also requires that every other operator of the nearest tie already has a failure evaluation. The old condition `-^selection-superstate.operator.evaluation <evaluation>` was always true and is removed. No other rule changed.
In every case checked the corrected rule does not fire, so the release behaves as if the rule were removed (same decisions and firings with the rule excised: water jug B1 seeds 1 to 5, mc seed 1, artists-2 seed 1, blocks world flat seeds 1 and 3). Failure of the operator above still comes from `all-evaluations-failed`.
Results: water jug 7/9 with repeated-state rejection (optimum 8 operators), 5 seeds: hand-adapted agent 24, 24, 10, 8, 10 operators in v2.24, 8 on every seed in v2.25; agent generated from the Lean description 26, 8, 10, 10, 8 in v2.24, 8 on every seed in v2.25. Median decisions rose from 9,341 to 17,878 and from 13,486 to 17,280.
Cost and regression: missionaries and cannibals 674 to 998 decisions became 2,466 to 2,746 (still 11 actions); blocks world and artists-2 moved both ways (artists-2 seed 1 1,033 to 4,415; seeds 2 and 3 fell). **artists-3 no longer finishes within its 20,000-decision cap on any of the 3 seeds** (v2.24: 3,024, 11,428, 11,982 decisions). With a 150,000 cap seed 1 solves at 78,394 decisions; seeds 2 and 3 do not solve. The early failure was pruning that search.
Test set v1.22: 296 tests; 12 baselines changed (mc, artists-2, blocks world, artists-3), all others identical. The three artists-3 baselines record the unsolved state and are marked `known_regression`.
Not changed, same pattern: `initialize-failure-evaluation3` marks the evaluation above as `depth-exhaustion` at the first dead end once a sibling was cut off by depth, which ends that evaluation before the remaining siblings are tried. Not examined further.
Chunking (first measurement, water jug 7/9 only, `chunk always`): the world-convention agents run and solve; see the water jug package. With chunking and no repeated-state rejection the process was killed by the system after about 15 s (cause not confirmed).

## v2.24 — Failure and depth-limit worst preferences depend on the whole state; maximum evaluation depth 12  14 Nov 2026
Fix for the Hanoi stale worst preference (FINDING-stale-worst-preference.md). A worst preference (`<`) created from a failure evaluation was a justification that tested only `^operator` and `^desireds`; the operator keeps its identifier across decisions, so the `<` outlived the state it was computed for and demoted the best move in the next state.
Now, when a failure is established in the `Impasse__State_No-Change` substate of an evaluate-operator, the new file `ground-state.soar` reads every WME reachable from the world and the desireds (operators `ground-init`, `ground-wme`, `ground-finish`), then sets `^state-grounded true`. Both `initialize-failure-evaluation` proposals (initialize-failure-count.soar) require `^state-grounded true`, so the `<` result's justification contains the whole state and retracts when any world or desired WME changes. This runs only where a failure occurs, only in that substate, never in the top state, and not under `^world.future-event`. It generalizes the dead count-* rules of the original selection-iterative-deepening (which counted only on/in/above/under); it handles any relation generically and reaches leaf WMEs, because world relations are mutated in place.
achieved-max-depth: the proposal and its three result rules (`worst`, `worst2`, `best`) require `^state-grounded true`. When the depth limit is reached and the evaluate-operators are done, `selection-world*propose*selection*ground-init*max-depth` runs the same grounding in the top selection state. This path is untested for correctness: achieved-max-depth fires in none of the 296 tests at depth 12; a forced limit of 2 shows only added cost.
Maximum evaluation depth raised from 7 to 12 (verify mode from 10 to 12), in init-current-evaluation-depth.soar.
Rejected alternatives (measured): state-version markers; conditions on `-^operator` (loop: select, worst, deselect, justification gone, reselect; broke termination on mc and graph r4x8); grounding in the top state on every tie (cost on every tie); delaying the `<` without grounding (raced, picked a wrong operator on mc). No chunking over the grounding chain: it exhausted memory in learning runs, so learning is not supported with this grounding.
Results: Towers of Hanoi 2 discs, seeds 1 to 6, all 3 operators (optimal; v2.23 gave 4 and 6 for seeds 1 and 4). Random graphs 7 to 9 nodes and scheduling: path costs identical to v2.23 (graphs 17/18 optimal in both; r7 seed 7 returns 11 against an optimum of 10 in both; scheduling 6 optimal, 2 unfinished within 12,000 decisions). Missionaries-and-cannibals seed 3 now halts (674 decisions; it reached the 5,000-decision cap in v2.23).
Cost: decisions increase where failures occur: random graphs r7x7 about 6x, r1x8 3x; world artists-2 3.7 to 18x, artists-3 seed 2 7x (seed 1 fell from 4,414 to 3,024); blocks world 1.2 to 4.4x; Hanoi 1.2 to 2.1x. Water jug, eight puzzle, graph c and r8x7 tests are unchanged in decisions.
Test set v1.20: 296 tests, all pass. 61 baselines changed. Unlike earlier releases, this goes beyond firings and wme_changes: 36 tests changed decisions, operator trace or output hash (families: artists, mc, blocks world, Hanoi, graphs r7x7, r1x8, r3x7, r4x8 and c with cap). In all of them the final result is unchanged (task achieved; costs unchanged in the graph tests); only mc seed 3 changed halting status (non-halting at the cap to halting).
Limits: the cutoff-search, exhaustion-failure and partial-failure result producers are not grounded (none fires in the 296 tests; the same defect can occur through them). The old count-* rules remain unused. Cost grows with world size; a switch to disable grounding for very large worlds (Thor-Soar) is not yet implemented.

## v2.23 — Lower-bound ordering rule only when the task supplies a heuristic; scheduling with unattended jobs (time mode)  14 Nov 2026
Fix: the v2.21 rule `selection-world*compare*selection*lower-estimated-total-cost-better` now also requires `^world.estimated-remaining-cost` on the evaluating state. Without a heuristic the bound is the clock or path cost, a valid lower bound but a poor ordering signal when jobs run unattended:
on the scheduling task (3 jobs, time metric, unattended work, seed 2) `optimize true` returned cost 9 against an optimum of 8. Without the rule, or with it narrowed, the result is 8.
Measured, narrowed vs v2.22 (random graphs 7 to 9 nodes, 18 seeds; scheduling 3 jobs, 8 seeds; optimize true): graphs without heuristic 17/18 optimal in both; graphs with heuristic 17/18 (v2.21 without the rule: 16/18); scheduling 6 optimal, 0 suboptimal, 2 unfinished within 12,000 decisions (v2.22: 5, 1, 2).
Six no-heuristic cost-graph tests were re-baselined (decisions, firings, wme_changes, trace and output hashes: exploration order changed; path costs checked unchanged, e.g. graph c cost 3). Test set 296 tests, all pass.
Limit: the library's own future-event machinery (`^world.future-event`, skip-wait via `^io.input-link.time.ms`) needs an environment clock; the scheduling task models time in its own rules, so that machinery is not measured here.
Zero-cost cycles with cost-cap iteration and no heuristic (graph d): the search is slow, not infinite; no library change. optimize + cap, no h: min-step-cost 0.01 did not finish in 30,000 decisions, 0.1 finished in 1,560, 0.5 in 154 (optimum cost 3 in each); with h, 41. Guidance and lint O6 updated.
Known: Hanoi 2-disc stale worst preference (FINDING-stale-worst-preference.md) is unchanged.

## v2.22 — Cost-cap iteration in time mode returns the optimum (timing fix); time mode and net value measured on random graphs  14 Nov 2026
Fix: with `^flags.cost-metric time` and `^flags.iterative-step cost` the pass-back of a success could fire before `^cost-exceeded` existed. In time mode `^path-cost` is elaborated from the look-ahead clock, one cycle after the operator
changes the clock, so the `-^cost-exceeded true` guard of v2.20 had nothing to test yet and an over-cap goal was reported as a success. Results: random graphs seed 3 (7 nodes) cost 16 and seed 4 (8 nodes) cost 20; the optima are 14 and 15.
Under cost-cap iteration the success pass-back now requires a positive marker `^cost-within-cap true`, elaborated only when `^cost-bound` (new companion `^cost-bound-path`) was computed from the current `^world.path-cost` and does not pass the cap.
The success and path-cost pass-back rules each have a second variant for this case: `...symbolic-evaluation*from-subgoal*success*cost-cap` (selection-world) and `...numeric-evaluation-return*path-cost*cost-cap` (agent-world); the original rules now apply when iterative-step is not cost.
The same race could occur in unit mode; unit results did not change. Both seeds now return the optimum in time mode with the same decision counts as unit mode (871 and 2201). Without cost-cap iteration, nothing changed.
Measured, time mode (seeds 1 to 6 at 7 and 8 nodes, optimum from Dijkstra), after the fix: depth+opt, cap, cap+h and depth+opt+h optimal on all 12; plain depth suboptimal on one (seed 4, 8 nodes), as in unit mode.
Measured, net value (`^state-value` 10, cost weight 1; seeds 1 to 6 at 7 nodes, 1 to 4 at 8 nodes): depth iteration optimal on 9 of 10 graphs (8 nodes seed 4: cost 20, optimum 15); cost-cap iteration optimal on 9 of 10 (7 nodes seed 3: cost 16, optimum 14). The heuristic changes nothing.
Net value keeps its first-success semantics (v2.17): the optimize flag and the cost bounds do not apply to it, so it can return a costlier path. A task that needs the cheapest path among solutions of equal value should use cost-metric with `optimize true` instead of a net value.
Datamap: `^cost-within-cap`, `^cost-bound-path`.
Tests: 296 (4 new: time-mode random graphs, cap, cap+h, depth+opt+h). 40 cost-cap tests changed firings and wme_changes (the new rule); one changed decisions (graph c, time, opt, cap) and its result is the optimum (cost 3). All non-cap tests are unchanged, including every default-flag test.

## v2.21 — Lower-bound preference for optimize true with look-ahead; random-graph evaluation at 8 and 9 nodes  14 Nov 2026
Fix: with `^flags.optimize true` a nested look-ahead that reached the depth limit reported the bound of the one leaf its path followed, not the minimum over leaves, so with a heuristic the search could commit to a costlier path (random graph seed 4, 8 nodes: cost 16, optimum 15).
New compare rule `selection-world*compare*selection*lower-estimated-total-cost-better` (nested selections only, unit or time metric, `optimize true`): among depth-exceeded evaluations the lower `^estimated-total-cost` is preferred, so the reported bound is the minimum over the leaves, an admissible lower bound. It does not apply at the top-level selection, where a depth-exceeded set means "search deeper". Not active when `^better higher` (net value).
Measured (random weighted graphs, unit cost, optimum from Dijkstra; seeds 1 to 6 at 7 and 8 nodes, 1 to 4 at 9): depth+opt, cap, cap+h and depth+opt+h returned the optimum on all 14 graphs. Depth iteration without `optimize` was suboptimal on one graph at 8 nodes and one at 9 (it minimizes operator count first).
Decisions on seed 4, 8 nodes: depth+opt 434, depth+opt+h 359, cap 2200, cap+h 468.
Evaluation tasks examined and not added: weighted water jug, weighted Eight Puzzle and a grid with step costs. On each the cheapest path is also the shortest, so cost-aware and operator-count search give the same answer and the task does not discriminate. The random weighted graph is the discriminating family.
Tests: 292 (10 new random-graph tests at 8 and 9 nodes). Six optimize tests changed decisions and trace hashes (the new rule); each result was re-checked against the Dijkstra optimum first. Default-flag tests, including all artists tests, are unchanged.

## v2.20 — Cost-cap iteration returns the optimum on random graphs (bug fix); random-graph tasks  14 Nov 2026
Fix: under `^flags.iterative-step cost` a goal reached by a last operator whose step cost carried the path cost past the cap was reported as a success. The nested selection then preferred that
over-cap success (it has a numeric value) to a cheaper branch that the cap had cut off, and the cheaper branch was never searched at the next cap. A random graph (seed 3, 7 nodes) returned cost 16; the optimum is 14.
The success and path-cost pass-back rules now require `-^cost-exceeded true` (agent-world and selection-world evaluate-operator elaborations): a goal beyond the cap counts as a cut-off branch with its cost as the bound, as in IDA*.
The elaboration `increment-current-evaluation-depth*cost-cap*drop-over-cap` and the within-cap dominance rule (now for every selection state) stay as safeguards.
Measured (n = 7 random graphs, seeds 1 to 8, unit cost, five configurations): cost-cap iteration, with or without the heuristic, returned the optimum on all 8; depth iteration was suboptimal on seeds 7 and 8 (it minimizes operator count first), and depth with `optimize true` on seed 7.
Cost: cap iteration takes more decisions than before on graphs where the old result was wrong or came from an over-cap success (graph c 198 -> 361, seed 3 310 -> 871); with the heuristic, 112 on graph c and 337 on seed 3.
Known limit: cap iteration without a heuristic on a graph with a zero-cost cycle charged the 0.01 minimum step cost (graph d) does not finish in 60,000 decisions, because the cap is 3 and the cycle is explored about 300 times with no cycle detection. With the heuristic it takes 40 decisions. Use `^estimated-remaining-cost` or a larger `^flags.min-step-cost` there. The graph d cost-cap test without the heuristic is removed.
Datamap: `^cost-exceeded` added (v2.19 introduced it without an entry).
Tests: 282 (12 new: random graphs seeds 3, 7, 8 under depth, depth+opt, cap, cap+h). 26 cost-cap tests changed decisions and trace hashes (the fix); every result was re-checked against the Dijkstra optimum first. Default-flag tests are unchanged.

## v2.19 — Progress termination fixed and measured; options d to f not built (plan Phase 7)  14 Nov 2026
Fix: the progress cut and the depth or cost-cap cut could both propose exceed-depth in one state. Each exceed-depth operator is preferred best over the other, which gave a
conflict impasse and runaway depth. The progress proposal now stands down when the depth or cost cap proposes it (new `^cost-exceeded` elaboration in cost-cap.soar).
New default score: with `^flags.termination progress` and no `^flags.progress-score task`, the progress score is minus the number of unachieved desireds, so the option works for any task with desireds.
Measurements (default library, seed 1, decisions to solve; the cap on search depth is 7):
- Eight Puzzle, 3 moves from the goal: 777 -> 337 with termination progress. 4 moves: 4019 -> 1835. Both solve in the minimum number of moves (3, 4). Threshold 0.0: 581 and 4019.
- Cost graphs with the task's own score (optimize true): b 49 -> 48; c 165 -> 123. This replaces the v2.18 statement that the cut saves nothing: that run had the conflict above.
- Hanoi, 2 discs: 250 decisions. 3 discs (7 moves): 48,746 decisions with iterative deepening. 4 discs (15 moves) is not solvable at depth 7.
  With termination progress, 3 discs takes 56,417 decisions and a 24-move solution: the score is not monotone (discs must move away from their goal pegs first), the failure the HPS paper reports. Do not use progress termination on such a task.
Options d to f (sampling, discrepancy, broadening) were not built. The task that exhausts iterative deepening (Hanoi) has neither a preference ranking for discrepancy search to follow
nor dense solutions for sampling to find, so I do not expect them to help there. This is a judgment from the measurements, not a test of d to f.
Tests: 271 (3 new: Eight Puzzle with termination progress, seeds 1 to 3). Cap-mode cost tests changed only in firings and wme_changes (the cost-exceeded elaboration); the progress cost tests changed in decisions (the fix).

## v2.18 — Search options a to c (plan Phase 6)  14 Nov 2026
All three options are off by default. Defaults and non-cost tests are unchanged.
a. Weighted bound. `^flags.heuristic-weight` (agent-world, default 1, set under cost-metric unit or time): the bound is path-cost + weight x ^estimated-remaining-cost,
   in the cost cap (`^cost-bound`) and in the `^estimated-total-cost` pass-back (both iterative-step modes). With an admissible estimate and weight w, the solution costs at most w times the optimum.
   Check: graph b with h, weight 3, first cost cap 7 (weight 1: 3). The result is still cost 3 here, because the cheapest route also has the lowest weighted bound; the guarantee is the bound, not a worse answer.
b. Progress-bounded termination. `^flags.termination progress` (default: depth), `^flags.progress-threshold` (default 0.15). The task supplies ^progress-score on the task state (root R)
   and on the evaluate-operator state (branch C). A branch is cut when P = (C - R + 1) / (D + 1) is below the threshold; it returns an unbounded cost bound (1000000) so a success dominates it.
   Operator-step only. The fixed depth cap (7) remains as a backstop; it is not replaced. On the cost graphs the result is unchanged (cost 3). The decision counts given here (b 57, c 193) were measured with the conflict fixed in v2.19; see v2.19 for the corrected figures.
c. Adaptive aspiration. `^flags.aspiration <cost level>`, `^flags.aspiration-step` (default 1). A success costing no more than the level is selected without waiting for other branches.
   After an iteration with no acceptable success the level rises by the step (depth iteration: every increment; cost-cap iteration: once the cap has reached the level).
   Graph b, optimize true, depth iteration: level 6 returns cost 6 in 33 decisions (49 without); level 2 relaxes to the optimum, cost 3. Cost-cap iteration returns cost 3 either way.
   Lower is better only.
New files (selection-world strategies/iterative-deepening/Impasse__Operator_Tie): aspiration.soar (3 applications, 1 compare), progress.soar (5 elaborations, 1 proposal, 1 application).
New default rules: agent-world heuristic-weight (cost-metric unit or time); selection-world aspiration-step (only with ^flags.aspiration) and progress-threshold (only with termination progress).
Tests: 268 (15 new). Existing cost tests changed only in firings and wme_changes (the heuristic-weight default rule). Non-cost tests unchanged.

## v2.17 — Net value (plan Phase 4)  14 Nov 2026
A task that computes a state value puts `^state-value <v>` on the evaluate-operator state and states `^better higher` on `^desireds`.
With cost-metric unit or time, a success then returns numeric-value = state-value - cost-weight x path-cost (`^flags.cost-weight`, default 1).
Without `^state-value` the numeric value is the path cost, as before.
New rules: agent-world*apply*evaluate-operator*numeric-evaluation-return*net-value; agent-world*elaborate*flags*default*cost-weight (only under cost-metric unit or time).
Modified: the path-cost return rule requires no ^state-value. The cost-bound rules (reject high-estimated-total-cost, success-within-cap, success-dominates-cost-bound) and
cutoff-search apply only when lower is better (they compare costs); under `^better higher` they do not fire.
Limits: net value uses the first-success semantics (optimize and cost bounds are not applied to a net value); `iterative-step cost` with net value deepens until every branch has a value, so it needs an acyclic or bounded graph.
Tests: 253 (4 new: graph b, state-value 10, cost-weight 2; depth iteration returns cost 6, net -2; cost-cap iteration returns cost 3, net 4). Existing cost tests changed only in firings and wme_changes. Non-cost tests unchanged.

## v2.16 — Iterative deepening on cost, IDA* (plan Phase 3)  14 Nov 2026
New value `cost` for the selection-world flag `iterative-step` (operator | tie-impasse | cost). Requires `cost-metric` unit or time. Operator-step only; tie-impasse mode is unchanged.
- Each iteration has a cost cap, `^cost-cap` on the selection state (first cap 0). The depth counter becomes the iteration index: it is no longer decremented per operator.
- A look-ahead branch whose cost bound (`^path-cost`, plus the task's optional world `^estimated-remaining-cost`) exceeds the cap is cut off (exceed-depth) and returns `^estimated-total-cost`.
- Next cap: the smallest cut-off bound above the current cap (IDA*); with `^flags.cost-quantum <q>` the cap rises by q instead; with no cut-off bound it rises by 1.
- With optimize false, only a success inside the cap dominates a cut-off branch, so the first success is the optimum when the bound is admissible. Without `cost` the success rule is unchanged.
- Zero-cost minimum (cost-metric unit): an operator whose step-cost is below `^flags.min-step-cost` (default 0.01) is charged the minimum, so zero-cost cycles terminate.

New rules: selection-world cost-cap.soar (4 elaborations, 1 proposal, 5 applications), compare success-within-cap-better-than-depth-exceeded;
agent-world step-cost*minimum and flags default min-step-cost (set only under cost-metric unit).
Modified: success-better-than-depth-exceeded now excludes iterative-step cost; the depth propagation and duplicate-look-ahead rules accept `<< operator cost >>`; init max-evaluation-depth rule excludes cost (1000 under cost).
Results (unit cost, seed 1, decisions): graph a 48; b 61; c 199 (depth iteration with optimize true: 44, 49, 165). With an admissible h: a 32, b 41, c 104 (depth iteration with h: 38, 49, 167).
Graph d (graph b plus a zero-cost cycle C<>E): optimum 3 in 60 decisions. Time mode on graphs b and c returns the optimum, the same as unit mode.
Not yet tested: Thor (needs the simulator), composite operators, learning on, tie-impasse mode with cost.
Tests: 249 (28 new). Existing cost tests changed only in firings and wme_changes (the min-step-cost default rule). All non-cost tests unchanged.

## v2.15 — Acceptance rule and `optimize` (plan Phase 2)  14 Nov 2026
New selection-world flag `optimize` (false default | true), used with `cost-metric` unit or time.
- optimize false: a success dominates a depth-exceeded evaluation. The cheapest path at the first successful depth is selected
  (graph a: cost 10 in 1 operator; graph b: cost 6 in 2 operators). This is not globally optimal.
- optimize true: depth-exceeded evaluations return `^estimated-total-cost` = path-cost (+ the task's optional world `^estimated-remaining-cost`).
  A success whose cost does not exceed that bound dominates the evaluation; a bound above the minimum numeric value is rejected.
  Graphs a, b and c all return the optimum, cost 3 in 3 operators (decisions: a 44, b 49, c 165; c takes 265 without the bound).
  The bound is passed back in both iterative-step modes (operator: evaluate-operator/elaborations.soar; tie-impasse: exceed-depth.soar).

New rules (selection-world/strategies/iterative-deepening/Impasse__Operator_Tie):
- selection-world*elaborate*flags*default*optimize                                   (_flags.soar)
- selection-world*compare*selection*success-better-than-depth-exceeded               (optimize false)
- selection-world*compare*selection*success-dominates-cost-bound                     (optimize true)
- selection-world*apply*evaluate-operator*...depth-exceeded*numeric*remaining        (adds the task's remaining-cost estimate; one pair per iterative-step mode)
Modified rules:
- ...depth-exceeded*numeric: passes back `^estimated-total-cost` (was the dead `^estimated-minimum-total-time`, which read an attribute nothing set).
- ...compare*selection*reject*high-estimated-minimum-total-time  ->  ...reject*high-estimated-total-cost (optimize true only).
Retired: selection-world/strategies/optimal (10 rules; it was never enabled or tested).
Behavior change for cost-metric users: with the default optimize false, a cost metric no longer deepens to global optimality (the Phase 1 behavior); set `^optimize true` for that.
Tests: 221 (18 new: graphs a, b, c with optimize true; graph c unit with optimize false). All other tests unchanged except firings and wme_changes (+1 firing, the optimize default rule). The unit/time fingerprints were re-baselined because optimize false changed their decisions.
Datamap: flags.optimize, world.estimated-remaining-cost, evaluation.estimated-total-cost.

## v2.14 — Cost model (plan Phase 1)  14 Nov 2026
Plan: Cost-Aware-Evaluation-Plan-v2.docx. Decision 1: the flag use-timers is retired and replaced by cost-metric.

New flag `cost-metric` (agent-world/_flags.soar): none (default, earlier behavior) | unit | time.
- unit: each task operator costs `^step-cost` (default 1). The evaluated world carries `^path-cost`.
- time: the cost is the look-ahead world clock; `^path-cost` is defined as `^time`.

New file agent-world/elaborations/cost.soar (8 rules):
- agent-world*elaborate*operator*step-cost*default                      (unit) step-cost 1 on task operators without one
- agent-world*elaborate*evaluate-operator*path-cost*copy*lock-in        (unit) path-cost 0 at the top selection
- agent-world*elaborate*evaluate-operator*path-cost*copy                (unit) copied down like ^time
- agent-world*elaborate*evaluate-operator*path-cost*copy-not-from-super-state   (unit)
- agent-world*elaborate*evaluate-operator*path-cost*time                (time) path-cost = look-ahead time
- agent-world*apply*operator*step-cost                                  (unit) increments path-cost once per applied task operator.
  Explicit :o-support: it changes the world and marks the operator ^cost-applied; without the marker the changed value matches again
  and the increment repeats until max-elaborations.
- agent-world*elaborate*desireds*better*lower*cost-metric               better lower unless the task states ^better.
  Explicit :o-support: it tests that better is absent, so an i-supported result would retract itself and fire again.

Modified rules:
- agent-world*apply*evaluate-operator*numeric-evaluation-return*time  ->  ...*path-cost: returns ^world.path-cost under unit or time.
- agent-world*propose*evaluate-operator*cutoff-search: compares ^world.path-cost (was ^world.time) with the selection minimum.
- agent-world*elaborate*flags*default*use-timers  ->  ...*default*cost-metric.
- thor-soar: the five action-times rules test ^flags.cost-metric time; the Thor flag initialization sets ^cost-metric time (was ^use-timers true).

Datamap: flags.cost-metric (none|time|unit), world.path-cost, operator.step-cost, operator.cost-applied; use-timers removed.

Finding: with a cost metric set, the selection already compares numeric values (better lower) and iterative deepening keeps deepening while an
evaluation is depth-exceeded, so unit and time mode return the cheapest path on the cost-graph tests. Cheapest-at-first-success-depth and
pruning by cost bound are the next phases.

Tests: 177 earlier tests unchanged; 26 new cost-graph tests (gen/costgraph-*).
