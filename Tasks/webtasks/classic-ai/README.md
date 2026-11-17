# Classic AI and cognitive tasks: English to Soar through Lean (16 November 2026)

**Runnable: six of ten.** Each task was taken from numbered English statements to a WorldSpec description, then to world-convention Soar rules (paths A and B give identical rules). The six runnable agents solve on seeds 1-3; the four search tasks find the shortest plan. Soar 9.6.6 (kernel 9.6.50, build of 6 Nov 2026), library v2.41, defaults.

**Checked by Lean (Lean 4.35.0).** Each description was first written once in Python (`<task>-spec.py`, using `../tools/worldspec_py.py`, a port of `WorldSpec/Sem.lean` and `Json.lean`), which prints the Lean source (`<Name>.lean`) and the path B JSON. Once Lean was installed, the four Lean files were added to `SoarLean/agentgen/WorldSpec/Tasks` (package `SoarLean/soarlean-agentgen-2026-11-16-classicai.zip`). For all four: the `wellFormed` theorems are proved by `decide`; `rosiegen json` matches the Python JSON exactly; path A (Lean writes the rules) and path B give identical rules; `rosiegen check` agrees on all 12 example states; `rosiegen replay` accepts all 12 runs.

Two tooling findings from the Lean check: the Lean printer first broke a universal condition across lines at an indentation Lean rejects (fixed in `worldspec_py.py`); and `rosiegen replay` cannot read runs of one-argument actions, because `run_agent.py --json` writes `null` for the missing argument (proposed fix, not applied: drop nulls when reading `actions`).

| Task | Status | Seeds 1-3 |
|---|---|---|
| monkey-and-bananas | runnable | 4 actions every seed (shortest) |
| vacuum-world | runnable | 3 actions every seed (shortest) |
| tower-of-london | runnable | 5 moves every seed (shortest) |
| instant-insanity | runnable | a valid 4-cube column every seed |
| cheryls-birthday | runnable (derived relations, each effects) | July 16 every seed, 21-22 decisions |
| muddy-children | runnable (derived relations, each effects) | Amy and Ben yes in round 2, Cal in round 3, 15 decisions |
| bridge-and-torch | described and checked; Soar does not solve it yet (library cost search) | no move within 400,000 decisions |
| wumpus-world, counterfeit-coin | skipped: need an environment (JL, 16 Nov 2026) | |
| mutilated-checkerboard | not started: a Lean proof, no agent | |

Every plan was replayed in the semantics: every action legal, no maintained-relation error, goal holds.

## What the four needed

- **Monkey and bananas, vacuum world:** direct; the language covers them. "Clean" is "not dirty", kept as a maintained relation, as "opposite" is in fox-goose-bean.
- **Tower of London:** "a peg that holds up to n balls" has no counting in WorldSpec (counted attributes are a listed limit). Pegs are given n slots instead, with an always-empty cap space over the top slot and a fixed base under the bottom slot. "Top ball" and "not full" then need no negation and no special case (A-TL1 to A-TL4).
- **Instant Insanity:** each cube's turns are orientation objects (24 for cube 1, 16 for cubes 2-4: the distinct colourings of the four sides). Cubes are placed in order, and two cubes showing one colour on one side is a losing state (A-II1 to A-II3). With failed moves rejected (library v2.39 and later), dead partial columns are cut off.

## Finding: reserved variable names

The first Tower of London description used a variable `s`. The back end compiled it to `<s>`, which the generated rule already uses for the state, so `move` was never proposed and the agent made no move in 100,000 decisions. Renaming the variable fixed it. Neither back end checks for this. `<s>`, `<w>`, `<objs>`, `<ds>`, `<op>`, `<pre>`, `<pa>`, `<any-unachieved>`, and names of the form `<k-…>`, `<r…>`, `<e…>` and `<new-…>`, should be refused in descriptions. A check in `Task.wellFormed` (Lean) and in `spec_backend.py` is proposed.

## The other four

- **bridge-and-torch:** WorldSpec gained `update`, `plus`, `stepCost` and `repeatControl`; the description is proved well-formed and agrees on every example state, but the library's cost search does not finish (see its README).
- **cheryls-birthday, muddy-children:** WorldSpec gained `derived` relations (knowledge stated explicitly, tested positively) and `each` effects (JL, 16 Nov 2026); both run.
- **wumpus-world, counterfeit-coin:** skipped; hidden state needs an environment (JL, 16 Nov 2026).
- **mutilated-checkerboard:** the answer is a proof that no covering exists; planned as a Lean theorem by colouring, with no agent.

Details and the remaining options: `../WORLDSPEC-EXTENSIONS.md`.

## Files

Each task folder: `english-input.txt`, `<task>-spec.py`, `<Name>.lean`, the `.world` files, `<task>-worldspec.json`, `<task>-rules.soar`, the loader `<task>.soar`, `run-seed1..3.json` and `README.md` (results, assumption ledger, how to reproduce and how to check with Lean). Tools: `../tools/worldspec_py.py`.
