# Finding: a dead end deep in look-ahead marks an ancestor operator as failed too early

14 November 2026. Found in library v2.24 (the rule is unchanged from v2.23 except for the `^state-grounded true` test added to its proposal). Corrected in v2.25; see Resolution.

## What happens

Rule `selection-world*apply*initialize-failure-evaluation2`
(selection-world/strategies/iterative-deepening/Impasse__Operator_Tie/evaluate-operator/task-operator/Impasse__State_No-Change/initialize-failure-count.soar).

When a look-ahead state has no operator left (state no-change), this rule gives `^symbolic-value failure` to the evaluation that the selection state two levels up is working on. Its test is: the nearest selection state has no evaluation valued `depth-exhaustion` or `depth-exceeded`. The rule's negated condition `-^selection-superstate.operator.evaluation <evaluation>` uses the same variable as the grandparent's evaluation, so it is true whenever the two selection states differ.

The test is made at the first dead end. Sibling operators of the nearest tie that have not been evaluated yet do not count, and neither do alternatives passed over higher on the path when an earlier tie ended without a decision and one operator was picked to continue.

## Evidence

Water jug, 7 and 9 gallons, goal 3 in the 7-gallon jug, optimum 8 operators, repeated-state rejection on, 5 seeds, 30,000-decision cap.

| Agent | Rule present: operators | Rule excised: operators | Median decisions, present | Median decisions, excised |
|---|---|---|---|---|
| B1 (hand-adapted to world conventions) | 24, 24, 10, 8, 10 | 8, 8, 8, 8, 8 | 9,341 | 17,878 |
| D1 (generated from the Lean description) | 26, 8, 10, 10, 8 | 8, 8, 8, 8, 8 | 13,486 | 17,280 |

Trace, B1 seed 1 (trace-b1s1.txt in the water jug package): the agent fills the 7-gallon jug (correct). From (7, 0) the tie is between fill-9 and pour. In the depth-4 pass, inside the evaluation of pour, a nested tie ends with every evaluation cut off by depth, one operator is picked, and the look-ahead reaches (0, 9). There the first operator tried leads to (7, 9), where every move is a repeated state. The rule prints "Exhaustion Failure operator2: E829", the top-level tie then selects fill-9, and with repeated states rejected the agent can only go the long way round (24 operators). The other operator at (0, 9) was not evaluated. That E829 is the top-level evaluation of pour is inferred from its number and from the selection that follows; it was not printed.

With failure-state knowledge (both jugs full is rejected) the dead end is never reached, which is why B3 and D3 return 8 operators on every seed with the rule present.

## Not established

- The effect of removing or tightening the rule on other tasks. The Hanoi fix in v2.24 uses the same failure path, so this needs the full test set.
- Whether a sound version (wait until every operator of the nearest tie has an evaluation, and no cut-off happened on the path) keeps the lower decision counts.

## Resolution (v2.25)

The rule now also requires that every other operator of the nearest tie already has a failure evaluation; the always-true negated condition is removed. In every case checked the corrected rule does not fire, so v2.25 behaves as if the rule were removed (identical decisions and firings with the rule excised).

| Task | v2.24 | v2.25 |
|---|---|---|
| Water jug 7/9, B1, operators (5 seeds) | 24, 24, 10, 8, 10 | 8, 8, 8, 8, 8 |
| Water jug 7/9, D1, operators (5 seeds) | 26, 8, 10, 10, 8 | 8, 8, 8, 8, 8 |
| Water jug 7/9, B1 / D1, median decisions | 9,341 / 13,486 | 17,878 / 17,280 |
| Missionaries and cannibals, decisions (3 seeds) | 722, 998, 674 | 2,746, 2,555, 2,466 (still 11 actions) |
| Blocks world (3 changed tests), decisions | 1,059, 1,844, 1,725 | 1,609, 1,459, 1,566 (still 3 actions) |
| artists-2, decisions (3 seeds) | 1,033, 1,220, 2,478 | 4,415, 1,064, 1,866 |
| artists-3, decisions (3 seeds, cap 20,000) | 3,024, 11,428, 11,982 | not solved within the cap on any seed |

artists-3 with a 150,000-decision cap on v2.25: seed 1 solves at 78,394 decisions; seeds 2 and 3 do not solve. The early failure was pruning that search, and nothing sound replaces it yet.

The remaining 284 tests of the test set are identical. Test set v1.22 records the new baselines; the three artists-3 tests are marked `known_regression`.

Open: `initialize-failure-evaluation3` has the same early pattern with `depth-exhaustion` (it ends the evaluation above before the remaining siblings are tried). Not changed.
