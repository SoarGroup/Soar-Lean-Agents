# Finding: a worst preference left by an earlier look-ahead persists after the state changes (selection-world, all versions checked back to v2.13)

Found 14 Nov 2026 by the model-versus-agent check of the option pipeline (task_options.py): Towers of Hanoi, 2 discs, default flags, seed 1 solves in 4 operators and seed 4 in 6; the optimum is 3. Seeds 2, 3, 5, 6 use 3. v2.13 and v2.22 give identical results.
Cause (seed 1, third decision): the top state holds operators D2>P1, D1>P1 and D1>D2, but D1>D2 (the one that finishes the task) also carries `O174 <` (worst) from the justification
`sp {justify179 (state S1 ^operator O174 + ^desireds D1) --> (S1 ^operator O174 <)}`. The justification tests only the operator and the desireds, not the world. It came from a depth-cutoff evaluation of the same operator in the previous state
(rule `selection-world*compare*selection*worse*failure-cutoff-numeric-value2`, or the exhaustion/failure rules next to it). The operator keeps its identifier from one decision to the next, so the justification stays true and the best move is demoted.
Effect: wrong (non-shortest) solutions and, with the cost options, possibly non-optimal ones; found only because the model's fewest-operator count was compared with the agent's.
Status: FIXED in v2.24 (see below). Original analysis: the dependency on the world is lost in the copy of the world made for look-ahead, so the fix belongs in how the `<` result is created (for example make it o-supported and remove it when the operator is selected, or give the copy-derived result a test of the real world). It changes behavior of tests that contain such decisions; decision needed before any change.
Reproduce: `HANOI_DISCS=2 python3 gen_hanoi.py flat`, then play hanoi-rules.soar with seed 1 (worldgen/play.py), count the actions.

## Resolution (v2.24, 14 Nov 2026)
Source of the stale `<`: `initialize-failure-evaluation` in the state-no-change substate of the evaluation (`^impasse no-change ^attribute state`), through rule `...failure-evaluation-becomes-reject-preference`. The o-support remedy was rejected (a rule cannot retract an o-supported WME, and the operator keeps its identifier).
Fix: before the failure evaluation is produced, that substate reads every WME reachable from the world and desireds (`ground-state.soar`), so the justification depends on the whole state. Same for achieved-max-depth results. Hanoi 2 discs, seeds 1 to 6: 3 operators each. Costs and limits: CHANGES.md v2.24.
