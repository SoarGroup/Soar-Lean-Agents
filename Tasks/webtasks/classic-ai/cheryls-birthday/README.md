# Cheryl's birthday: English to Soar through Lean (WorldSpec), 16 November 2026

**Runnable.** Soar 9.6.6 (kernel 9.6.50), library v2.41, defaults. Each seed applies statement 3, 4 and 5 and answers **July 16** (the published answer).

**Checked by Lean (Lean 4.35.0).** `cherylsBirthday_wellFormed : cherylsBirthday.wellFormed = [] := by decide` is proved; `rosiegen json` gives the same JSON as the Python description; path A (Lean) and path B (spec_backend.py) give identical rules; `rosiegen check` agrees on every example state; `rosiegen replay` accepts every run (with the null second arguments removed, see the classic-ai README).

## Representation

- **Dates** are objects with a month and a day. Who was told what is not stored; "Albert would know" is read for every date, as if Albert had been told that date's month (A-CB1).
- **Knowledge is explicit** (JL, 16 Nov 2026): derived relations such as `albert-would-know(d)`, `bernard-might-know(d)`, `bernard-unsure-after-3(d)` and `albert-unsure-after-4(d)` are recomputed in every world; their definitions use negation ("no other date has that day"), and operators test them only positively (A-CB2).
- **Each statement is an operator** (`statement-3`, `statement-4`, `statement-5`) with `each` effects that mark, on every date at once, the dates where the statement would be false (`out3`, `out4`, `out5`). Marks are never removed, so each statement is judged on the dates left before it; a stage number keeps the order (A-CB3).
- **The answer** is proposed only for the single date left (`only-date`).

New WorldSpec constructs used: `derived` relations (i-supported elaborations, negation only in their definitions, never copied into look-ahead) and `each` effects (one apply rule per `each`, firing once per match, judged on the state before the action); see `../../WORLDSPEC-EXTENSIONS.md`.

## Example states

| World | State | goal-met / failure | Lean, Python, Soar |
|---|---|---|---|
| `init-cheryl.world` | all ten dates, before statement 3 | false / false | agree |
| `after3-cheryl.world` | May and June ruled out by statement 3 | false / false | agree |
| `final-cheryl.world` | July 16 given as the answer | true / false | agree |

## Runs (seeds 1-3)

| Seed | Outcome | Decisions | Actions | Seconds | Plan |
|---|---|---|---|---|---|
| 1 | success | 21 | 4 | 0.7 | statement-3 talk; statement-4 talk; statement-5 talk; answer july-16 |
| 2 | success | 22 | 4 | 0.7 | statement-3 talk; statement-4 talk; statement-5 talk; answer july-16 |
| 3 | success | 22 | 4 | 0.7 | statement-3 talk; statement-4 talk; statement-5 talk; answer july-16 |

## Assumption ledger

- **A-CB1** (intent; statements 1, 2): The ten dates are date objects with a month and a day. Who was told what is not stored: "Albert would know" is read over every date, as if Albert had been told that date's month.
- **A-CB2** (intent; statements 3, 4, 5, 6): Knowledge is explicit (JL, 16 Nov 2026): derived relations, recomputed in every world, say for which dates a speaker would or would not know; operators test them positively. Their definitions use negation ("no other date has that day"), which is allowed only there.
- **A-CB3** (intent; statements 3, 4, 5): Each statement is an operator that marks, on every date at once (an each effect), the dates where the statement would be false (out3, out4, out5). Marks are added, never removed, so each statement is judged on the dates left before it. A stage number keeps the statements in order.
- **A-CB4** (intent; statements 3): "I know that Bernard doesn't know": rules out every date in a month that has a date whose day is unique among all ten (Bernard might know). "I don't know": rules out dates in a month with one date (none here).
- **A-CB5** (intent; statements 4): "At first I didn't know": rules out dates with a unique day among all ten (already gone after statement 3). "I know now": rules out dates whose day is shared by another date left after statement 3.
- **A-CB6** (intent; statements 5, 7): "Then I also know": rules out dates whose month is shared by another date left after statement 4. The answer is the one date left; with more than one left, no answer is proposed.

No `gap` or `tooling` assumption is open.
