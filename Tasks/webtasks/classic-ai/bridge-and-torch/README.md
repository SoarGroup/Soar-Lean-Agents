# Bridge and torch: English to Soar through Lean (WorldSpec), 16 November 2026

**Not runnable yet.** The description is complete and checked by Lean, and the rules are generated and agree with it on every example state. The Soar agent does not solve the task: seed 1 makes no move within 400,000 decisions. The cause is in the library's cost search, not in the description (below).

## What it needed from WorldSpec (extensions made for this task)

- `update x p rhs` and `plus a b`: the clock's elapsed minutes grow by each crossing's time (A-BT2).
- `stepCost` on operators: a crossing's minutes are also its look-ahead cost, so the task can use the library's cost search (`iterative-step cost`, A-BT6).
- `repeatControl`: search control, not from the English, as decided by JL for the river crossings (16 Nov 2026). A look-ahead state that returns to where the people and the torch were earlier on its path fails (A-BT7).
- "The speed of the slower one" needs no maximum: `cross-two` takes a faster person `a` and a slower person `b` and adds `b`'s minutes (A-BT3).

## Checks

| Check | Result |
|---|---|
| Lean | `bridgeAndTorch_wellFormed : bridgeAndTorch.wellFormed = [] := by decide` proved |
| Path B input | `rosiegen json` identical to the Python JSON |
| Rules | path A (Lean) identical to path B (spec_backend.py) |
| Example states, Lean / Python / Soar | init, mid (Bob across, 3 minutes): not goal, not lost; final (17 minutes): goal; late (19 minutes): goal and lost, all three agree |
| Cheapest plan in the semantics | 17 minutes, 5 crossings: Ann and Bob over, Ann back, Cy and Di over, Bob back, Ann and Bob over |

## Soar runs (seed 1, Soar 9.6.6, library v2.41)

| Settings | Result |
|---|---|
| defaults, no repeat control | no move in 300,000 decisions |
| `iterative-step cost`, no repeat control | no move in 300,000 decisions; probe of 6 settings: none solves in 60,000 |
| `iterative-step cost` + repeat control | no move in 400,000 decisions; the top cost cap reaches 16 at decision 80,000 and 17 is never completed |
| defaults + repeat control | no move in 100,000 decisions |
| `tie-impasse` + repeat control | 6 moves in 100,000 decisions, each person over and back (real moves are not repeat-controlled) |

The search the agent needs is small: iterative deepening by cost with path-repeat checks expands 635 operators at cap 17 (the semantics, `worldspec_py.py`). Two observations point at the library:

1. Nested look-aheads run past the top cap: costs of 19 and 25 appear while the top selection's cap is 16.
2. The look-ahead records a success at path cost 25, where the clock is over 17 and the state is also lost.

## Findings on the way (fixed)

- A derived situation label is i-supported, so it lags the effects by one elaboration wave. A freshly applied look-ahead state matched its parent's label and was failed, which rejected every first move. The repeat check now compares the current world with each ancestor world directly.

## Assumption ledger

See the header of `bridge-and-torch-rules.soar` (A-BT1 to A-BT7). No `gap` or `tooling` assumption is open.
