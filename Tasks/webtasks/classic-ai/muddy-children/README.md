# Muddy children: English to Soar through Lean (WorldSpec), 16 November 2026

## Regenerated 21 November 2026 (library v2.45, SoarLean release revision b)

Rules regenerated from `muddy-children-spec.py` with `spec_backend.py` of `SoarLean-2026-11-21b-release.zip` (path B); `rosiegen compile` (path A) gives identical rules apart from the header; `rosiegen json` equals the Python JSON. 27 rules, as before. The 47 changed lines are the 18 November conventions: `^problem-space.name` tests on the task rules (World-Conventions L3-005), the three rule-group comments (L3-012), and `^unachieved-desireds true` in place of a binding of every unachieved desired. The semantics and Soar agree on every example state; `rosiegen replay` accepts every new run.

Runs on library v2.45 (Soar 9.6.6, defaults; outcome, decisions / actions):

| Seed | Stored run (rules of 16 Nov, library v2.41) | Rules of 16 Nov, library v2.45 | New rules, library v2.45 | Plan (new rules) |
|---|---|---|---|---|
| 1 | success 15 / 4 | success 15 / 4 | success 15 / 4 | father-speaks talk; ask first; ask second; ask third |
| 2 | success 15 / 4 | success 15 / 4 | success 15 / 4 | father-speaks talk; ask first; ask second; ask third |
| 3 | success 15 / 4 | success 15 / 4 | success 15 / 4 | father-speaks talk; ask first; ask second; ask third |

The earlier sections below describe the generation of 16 November.

**Runnable.** Soar 9.6.6 (kernel 9.6.50), library v2.41, defaults. Each seed: the father speaks, then rounds 1, 2 and 3. The agent's world records yes from **Amy and Ben in round 2** and from **Cal in round 3**; round 1 rules out the three one-muddy worlds, round 2 the worlds with Cal muddy or all muddy. Read from the agent's real world after the run; identical to the semantics.

**Checked by Lean (Lean 4.35.0).** `muddyChildren_wellFormed : muddyChildren.wellFormed = [] := by decide` is proved; `rosiegen json` gives the same JSON as the Python description; path A (Lean) and path B (spec_backend.py) give identical rules; `rosiegen check` agrees on every example state; `rosiegen replay` accepts every run (with the null second arguments removed, see the classic-ai README).

## Representation

- **Possible worlds** are the eight mud patterns, as objects; `muddy` and `clean` give each child's forehead in each world, and `view-mate(c, w, w2)` says that `w2` differs from `w` only on `c`'s own forehead, which `c` cannot see (A-MC1).
- **Knowledge is explicit** (JL, 16 Nov 2026): `knows-at(c, w, r)` holds when no world `c` cannot tell from `w` is still live at round `r`; `answers-differ` and `answers-differ-too` say where some child would answer differently than in the actual world. Negation appears only in these definitions (A-MC2).
- **The father's statement and each round are operators** with `each` effects: a round records the yes answers in the actual world (`said-yes(c, r)`) and rules out every world where an answer would differ (`out-at(w, r)`). A world is live at round `r` if it was not ruled out in an earlier round, so each round is judged on the worlds left before it (A-MC3, A-MC4).

New WorldSpec constructs used: `derived` relations (i-supported elaborations, negation only in their definitions, never copied into look-ahead) and `each` effects (one apply rule per `each`, firing once per match, judged on the state before the action); see `../../WORLDSPEC-EXTENSIONS.md`.

## Example states

| World | State | goal-met / failure | Lean, Python, Soar |
|---|---|---|---|
| `init-muddy.world` | all eight worlds, before the father speaks | false / false | agree |
| `father-muddy.world` | all-clean world ruled out | false / false | agree |
| `final-muddy.world` | every child has said yes | true / false | agree |

## Runs (seeds 1-3)

| Seed | Outcome | Decisions | Actions | Seconds | Plan |
|---|---|---|---|---|---|
| 1 | success | 15 | 4 | 35.8 | father-speaks talk; ask first; ask second; ask third |
| 2 | success | 15 | 4 | 35.8 | father-speaks talk; ask first; ask second; ask third |
| 3 | success | 15 | 4 | 35.7 | father-speaks talk; ask first; ask second; ask third |

## Assumption ledger

- **A-MC1** (intent; statements 1, 2): The eight possible patterns of mud are world objects; muddy and clean say each child's forehead in each world; view-mate(c, w, w2) holds when w2 differs from w only on c's own forehead (what c cannot see). The actual world is w-mmc.
- **A-MC2** (intent; statements 2, 4, 5): Knowledge is explicit (JL, 16 Nov 2026): knows-at(c, w, r) holds when, in world w at round r, no world c cannot tell from w is still possible. It and the other derived relations use negation only in their definitions; operators test them positively.
- **A-MC3** (intent; statements 3, 4, 5): The father's statement and each round are operators that rule out worlds (out-at(w, round)), on every world at once. A world is live at round r if it was not ruled out in an earlier round, so each round is judged on the worlds left before it. A stage number keeps the order; round objects carry their number.
- **A-MC4** (intent; statements 4): A round records which children answer yes in the actual world (said-yes(c, r)), and rules out every world where some child would answer differently than in the actual world (all answers are heard).
- **A-MC5** (intent; statements 6): The goal is that every child has answered yes in some round; the rounds of first yes are read from said-yes. Four rounds are provided.

No `gap` or `tooling` assumption is open.
