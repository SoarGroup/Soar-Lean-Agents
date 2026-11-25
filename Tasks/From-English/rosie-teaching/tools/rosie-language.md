# Reading Rosie's teaching language as world-convention Soar (16 November 2026)

This is the shared background that the pilot agents (fox-goose-bean, tower-of-hanoi, tic-tac-toe) and the block puzzles were generated against. It states how each kind of instructor statement, and the primitives Rosie already knew, are read. Task-specific readings are in each task's README (assumption ledger). Written from the twelve dialogs done so far (the pilot and the nine block puzzles) and their world files; the other dialogs will add statement forms.

## 1. World files

| World file | World-convention form |
|---|---|
| `objid N` block | a world object; `category` becomes `^type` (location, block); other attributes kept as plain attributes (`color`, `shape`, `size`, `volume`, `name`, `row`, `column`) |
| value `red1`, `on1` | Rosie's trailing sense number is dropped: `red`, `on`. Numbers stay numbers (`4.0` becomes `4`) |
| `predicate on1` / `below1` pairs | relation objects `(<w> ^on <r>) (<r> ^argument1 <a> ^argument2 <b>)`, one per pair; `below` is declared `^copy-relation` (the library copies `on` itself) |
| `predicate-set S` lines | one world object per line (type named by the task, e.g. `line`) and a static `member` relation from it to each listed object, declared `^copy-relation member` |
| object handles | chosen per task for readability from the world file's attributes (`bank-1`, `boat-6`, `block-4`, `loc-2-3`, `red-10`); the number is the world file's objid |
| (added) task object | handle `task`, `^type task`; carries the goal as the derived attribute `^goal-met true` (declared `^dont-copy-object-attribute goal-met`) and any bookkeeping |

The `Load init-*` world is the agent's initial world. The other loaded worlds (`fail-*`, `final-*`, `second-*`) are the instructor's examples: `gen.py WORLD` writes the same rules with that world as the initial world, and `run_agent.py --check` reports whether the goal and the failure hold there. Expected: goal true only on `final-*`, failure true only on `fail-*`.

## 2. Statement forms

| Statement | Reading |
|---|---|
| The name of the puzzle/game is N. | task name N |
| The name of an action is A. | name of the next taught action. An action taught without a name gets one from its verb (`move`, `cross`; recorded in the ledger) |
| You can move X onto Y. | a task operator, `^argument1` = the object described by X, `^argument2` = the one described by Y; each adjective and relative clause in X and Y becomes a condition of the proposal. "You can move the boat and a block ... onto Y" moves both objects; the block is `^argument1` |
| If C then it is P. / ... then they are P. | definition of the concept P (see section 3) |
| If the V of a X is more than the V of a Y then the X is R the Y. | comparative relation R: X R Y when V(X) > V(Y); used with either argument as the subject |
| If C then you lose. | failure: an elaboration that marks the state `^failure <desireds>` when C holds; in look-ahead the library returns it as a failure evaluation; on the real (top) state it is a loss |
| The goal is that C. | goal: an elaboration that sets `^goal-met true` on the task object when C holds; the single desired is `(task ^goal-met true)` |
| The name of the goal/failure is N. | name only (kept in rule names) |
| Load W. / Ok. / Done. / No. | dialog management: W is a world state (above); "Ok." confirms a set-up; "Done." ends teaching; "No." declines Rosie's offer to solve |

## 3. Concepts and primitives

- **move X onto Y.** X's `on` relation now names Y and the matching `below` relation now has Y as its first argument. If X was on nothing, both relations are created. Objects on X are not affected (in the pilot tasks only clear objects move).
- **on, below.** Primitive relations of the world file, maintained by every action. `below(A, B)` holds exactly when `on(B, A)`.
- **A concept that tests absence** ("not below an object", "not on a location", "not below a boat") and is used to decide legality, the goal or a failure is a **maintained one-argument relation** (`(<w> ^clear <c>) (<c> ^argument1 <x>)`), declared `^copy-relation`. Its initial members are computed from the world file by the definition; each action's application adds and removes members as the definition requires. This follows World-Conventions-Spec v6 section 3 (maintained, not derived, when it decides legality; avoid local negations, L11-003). Pilot instances: `clear` (Hanoi, tic-tac-toe), `opposite` (fox), `available` (tic-tac-toe).
- **A concept that is a positive test** ("below a boat", "below a red block", "linear", "larger than") is **expanded in place** wherever it is used (proposal, goal, failure). No relation is created for it. Pilot instances: `current`, `captured`, `occupied`, `in a line`, `larger than`.
- **Quantified goals.** "There are two clear green locations": two different objects meeting the description. "Three of the captured locations are in a line": three different members of one line object, each meeting the description. "All the blocks are on a destination bank": expanded over the blocks of the world file into one positive condition per block (closed world), so the goal test needs no negation.
- **Opponent (games).** The dialogs teach only the learner's side. In the pilot (decided 16 Nov 2026) the environment plays the other side under the same move rule; its moves arrive on the input-link and are applied to the world by task rules (I/O conventions L3-092 and L3-093 (the turn-signal proposal IO-021 was deleted on 18 Nov 2026)). Look-ahead covers the agent's own moves only.

## 4. What is generated per task, and what is shared

- Shared (`tools/rosie_gen.py`): world-file reading, objects and relations, maintained-relation initialization, task object, problem space, flags, achievement rules (through worldgen v19 `wg.py`), the loader, and the example-state variants. `tools/run_agent.py` runs an agent or checks an example state; `tools/check_plan.py` replays a plan in Python using the statements directly.
- Per task (`gen.py`, or for the block puzzles `tools/rosie_tasks.py` with the operators in `tools/rosie_blocks.py`): proposals, applications (look-ahead and real world), maintenance of each maintained concept by each action, the goal and failure elaborations, and the statement each comes from. In the pilot these were written by Claude from the statements. A parser from statements to these parts is the next step if the remaining dialogs are to be done at scale.

## 5. Forms added by the block puzzles (16 November 2026, afternoon)

| Statement | Reading |
|---|---|
| You can move a block onto a location. | any block onto any location other than the one it is on (sorting) |
| If the number of the locations between L and C is the number of the blocks that are on C then you can move it onto L. | all the blocks on C move together onto L (the frog-stacking pile). "The number of the locations between" is a static relation apart-k computed from the locations' x and y; "the number of the blocks on C" is a mutable attribute ^block-count kept by the moves |
| There is six. (answer to Rosie's "How many instances of this action are there, 6 or 4?") | a check on the reading of the action: the reading chosen must give that many instances in the initial world, and the generated agent must propose exactly that many. In the frog dialogs it settles "between": adjacent locations count 1 |
| The solution has three steps. | checked against the plans; since 24 Nov 2026 also a lower bound on the look-ahead depth (section 8) |
| The goal is that all the X are on a Y (and ...). | expanded over the X of the world file, one positive condition each |
| The goal is that a X is on a Y and the X is below a Z. | one elaboration with a variable per noun phrase; "the X" refers back to the same object |

Where a concept tests absence but no action can change it (lazy frogs: accessible), it is still a maintained relation, initialized from the world file, with no maintenance rules; the task README says why none is needed.

Search: every block puzzle with look-ahead depth at most 12 solves with the shortest plan. Tower of Hanoi with 4 and 5 blocks (15 and 31 moves) does not: the library's look-ahead stops at depth 12 (library limit).

## 6. Forms added by the logic puzzles (16 November 2026, evening)

| Statement | Reading |
|---|---|
| You can write a number that is between one and N onto an empty location. | operator `write`: argument1 = the location, argument2 = a number object `number-k` (`^number k`), k = 1..N (operator arguments are objects); the effect is `^value k` on the location |
| If the value of a location is absent then the location is empty. | tests absence and decides legality: a maintained one-argument relation `empty`, removed by `write` |
| If the value of a location is more than zero then the location is filled. | expanded in place (`^value > 0`) |
| If the R of a location is the R of a location and the value of the former location is the value of the latter location then you lose. | two different locations (A-L1) with the same R and the same value: `^failure` |
| If the locations in a G are filled and the sum of the values of the G is not T then you lose. | one group object per G of the world file (`^type group ^size n`, static `member` relation); a derived `^sum` once every member has a value (one rule per group size, members distinct); failure when the sum differs from the target: a constant `^target-value`, or the value of the clue object named by the static `sum-target` relation |
| If the blocks have the same C then they are in a group. / If a block is blue and the column of the block is the column of a location then the block is beneath the location. | definitions of the groups and of their targets, evaluated on the world file when the rules are generated (static relations); see A-L3, A-L4 |
| The goal is that all locations are filled. | expanded over the locations of the world file |

A losing condition and the goal can hold together (fail-color-ken, fail-kakuro, fail-sujiko, ...). Losing takes precedence (JL, 16 Nov 2026); the plan checker and `run_agent.py` report such a state as a failure.

## 7. Forms added by the river crossings (16 November 2026, evening)

| Statement | Reading |
|---|---|
| You can move a block that is on the current bank and another block that is on the current bank and the boat onto the opposite bank. | operator `ferry-two`: the two blocks (lower `^index` first, so each pair is proposed once) and the boat move; `ferry-two-children` when the blocks must be children |
| If a woman is on a bank and the husband of the woman is not on the bank and a man is on the bank then you lose. | "not on the bank" read as "on the other bank" (A-R3), so the test is positive; "husband" (same last-name) expanded in place |
| If the number of cannibals on a bank is more than the number of missionaries on the bank then you lose. | `^cannibal-count` and `^missionary-count` on each bank, maintained by every crossing; read with the usual exception that a bank with no missionaries is safe (A-M1: the literal reading makes the puzzle unsolvable) |
| The solution has nine (five) steps. | checked against the plans; "five" does not fit the three-couple and three-pair worlds (11 crossings), only the two-couple world init-husbands2 |

Search control (JL, 16 Nov 2026; not from the English): in look-ahead, a move whose result is a situation already on the current look-ahead path is rejected; a real move back to a situation already visited is worst (the top state records each situation it leaves).

## 8. Lines added after the teaching script (23-24 November 2026)

These lines augment a task; they never change its initial state, legal moves or goal. Each is read by one tool, and a task without the line is generated exactly as before.

| Line | Reading | Tool, convention |
|---|---|---|
| `Learning: do not learn from look-ahead. <reason>` | `chunk never` after the library loads | learning.py, L5-021 |
| `The solution has N steps.` (in the teaching script) | max-evaluation-depth = max(12, N) | solution_length.py, L16-045 |
| `Goal <name>: <goal statement>.` | an extra named goal, ^<name>-met on the task object | sequence.py, L8-026 |
| `Phases: first <goal>, then <goal>, ..., finally <goal>.` | ^next-desireds chain, pursued in order | sequence.py, L8-026 |
| `Repeat: from <goal>[, N times][, until <goal>].` | ^loop-start, ^repeat-count, ^termination-desireds; no count and no until-goal loops for ever | sequence.py, L8-027 to L8-030 |
| `Output: command <name>; name attribute <a>; arguments <a1> <a2> <a3>; done ...; success ...; error ...; applied ...` | environment command form and output map | output_form.py, L10-018 |
| `Search control` section, items `SC-<n> [<kind>]: <statement>` | desired order, operator preference, evaluation order or method rules, selectable per test condition (evaluation-order marks are ignored by library v2.47: L15-026 suspended) | control.py, L15-026 |

Interchangeable objects (same category and attributes, never named individually, never related to one another) are found by aggregate.py (L7-027) and kept as counts per place where the task family's generator supports it (river crossings, rosie_river.py). Examples: block-puzzles/sorting-phases (Goal, Phases, Repeat) and block-puzzles/sorting-output (Output).
