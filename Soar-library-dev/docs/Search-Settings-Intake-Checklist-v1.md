# Search settings intake checklist (v1, 16 Nov 2026)

For every task the pipeline generates. It decides three flags: `^iterative-step`, `^cost-metric` and `^optimize`. It extends the Option Selection Guide (Soar-library-dev/docs/Option-Selection-Guide-v1.md): that guide's questions Q1 to Q9 and probes P0 to P5 still apply to the cost options. This checklist adds the choice of depth unit, the measured probe (P6) and the rule for choosing among the measured configurations.

Library defaults (v2.34 to v2.41): `iterative-step operator`, `cost-metric none`, `optimize false`. Since v2.37 the depth limit is the
`max-evaluation-depth` flag (default 12) and `iterative-step cost` without a cost metric gets `cost-metric unit`; since v2.40 `optimize true`
guarantees the cheapest plan (positive step costs, admissible estimates) under operator depth as well as tie-impasse depth. Checked against
library v2.41 on 16 Nov 2026; the measurements below predate v2.37 and were not rerun. A task sets something else only through `^flag-override`, written by the generator from options.json.

## 1. Questions at intake (ask the person one at a time; skip any the English answers)

| # | Question | Leads to |
|---|---|---|
| S1 | Does the English ask for the cheapest, fastest, shortest or best solution, or give actions a cost? (= Q1 of the guide) | yes: candidates with `cost-metric unit` (or `time`) and `optimize true`. no: no cost options are tried. |
| S2 | Is there exactly one solution, or is any solution acceptable (a puzzle with a unique answer, constraint satisfaction)? | yes: never `optimize true`; it only adds the cost of proving that nothing cheaper exists. |
| S3 | In a typical state, how many actions apply: usually several real alternatives (moves, fills, crossings), or mostly one forced step (propagation, bookkeeping, inference) with an occasional guess? | several at almost every step: operator depth. Mostly forced with rare guesses: tie-impasse. |
| S4 | Roughly how many actions does a solution take, and how many of them are real choices? | more than 12 steps but at most 12 choices: tie-impasse (operator depth would hit the depth limit, `max-evaluation-depth`, default 12). |
| S5 | Do operators carry effect-desireds so that means-ends selection removes most ties (`^mea-operator-selection true`)? | yes: ties are rare, which favours tie-impasse; confirm with P6. |

Record each answer with the English sentence it rests on. An answer from Claude's own reading is an assumption for review, as in section 2 of the guide.

## 2. What the answers predict (static, before any run)

| Task kind | Depth unit | Cost and optimize | Examples measured on 16 Nov 2026 |
|---|---|---|---|
| Forward search, a choice at every step, no costs | operator | none, false | eight-puzzle, water jug, Hanoi |
| Search where MEA leaves few ties | tie-impasse | none, false | blocks world (958 against 1,356 decisions), missionaries and cannibals (367 against 1,451) |
| Long forced chains with occasional guesses | tie-impasse | none, false | KenKen 4-5 and 6-x (operator depth hits the limit of 12 and fails some seeds) |
| Unique answer or constraint satisfaction | either; follow the probe | none, false | zebra, three wizards |
| Actions have costs and the cheapest answer is required | operator (or cost, guide Q5) | unit or time, optimize true | cost graphs |

Known traps:
- **Tie-impasse when every step ties.** After a nested tie is broken, a look-ahead in tie-impasse mode continues without charging depth (by design since v2.30). When every step is a tie this can run without bound, or return longer plans: water jug took 6 to 12 moves against 4, and eight-puzzle and water-jug-look-ahead did not solve. A fix that stops the continuation made artists-2 take 2,160 to 4,226 decisions instead of 165 to 282, so it was not adopted (FINDING-tie-impasse-unbounded-continuation.md).
- **A cost metric without optimize** changes no plan and only adds bookkeeping: 42 of 171 library tests used more decisions, none found a better plan (v2.33 against unit cost, 16 Nov).
- **Optimize on a task with no costs** finds the same plan at a higher cost: Hanoi 630 against 809 decisions, eight-puzzle 1,856 against 5,597, artists-2 648 against 3,672.

## 3. Measured probe (P6): required before delivery

Run `worldgen/probe_settings.py` on the generated agent with three seeds:

    python3 probe_settings.py --lib <library> --dir <task folder> --load <task>.soar --seeds 1-3 --cap 3000 \
        [--configs default|cost|all] [--checker 'python3 check.py {plan}'] [--edges model.json] --options options.json

- `--configs default` tries operator and tie-impasse; `cost` adds `cost-metric unit` with `optimize true` (use it when S1 is yes); `all` tries all four.
- The probe adds one `^flag-override` object per configuration and leaves alone any flag the task already sets ("fixed"). Remove a hand-written flag first if it is in question.
- **Choice rule:** (1) solve every seed; (2) best plan, meaning the lowest cost from `--checker` when the task has costs, otherwise the fewest task operators applied in the top state (the world's `^applied-count`); (3) fewest decisions over the seeds. Ties go to the library defaults. A faster configuration that loses a seed, or returns a longer or costlier plan, never wins (water jug: tie-impasse took 312 decisions but returned 12-move plans).
- **Noise:** if the task makes no look-ahead (`^look-ahead-planning false`, or no operator ties reach the selection space), the three flags cannot matter; any difference between configurations comes from random choices or learning, not from the setting, and is not a reason to override. Water-jug-tie-chunk (look-ahead off) showed 147 against 182 decisions this way; no override was set.
- With `--edges` (the model graph of the guide, section 3) the probe also reports the choice profile of one fewest-operator solution: steps, choices and forced steps. This is advice only; the measured runs decide.
- Raise `--cap` if no configuration solves every seed; the probe then warns and must not be used to choose.

## 4. Record and generate

- `options.json` gets `search` (the chosen flags and the override rule) and `measured.probe_settings` (every configuration's runs).
- The generator writes only the flags that differ from the defaults into `^flag-override` (wg.py: `Task.extra_flags`). Put a comment above the flags rule naming the probe, the date, the library version and the decisive numbers.
- The README of the task names the configurations tried and why the others lost.

## 5. Delivery gate (additions to section 7 of the guide)

1. S1 to S5 answered and recorded.
2. P6 ran on the final rules with the release library; its recommendation equals the flags in the rules file.
3. If a later library release changes defaults or search behaviour, rerun P6 on every task (the test set does this for its tasks).
