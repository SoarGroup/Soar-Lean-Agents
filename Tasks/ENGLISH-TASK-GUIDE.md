# Specifying tasks in English for the Soar agent generators

User's guide, library v2.47, 24 November 2026. Written by Claude, supervised by John E. Laird. For CIC researchers. Also published as a doc: https://claude.ai/artifact/QDQbEjhxkDb8d92RUyGo8z

## 1. Routes from English to an agent

| Route | Input | Generator | Output |
|---|---|---|---|
| Rosie teaching | a restricted-English teaching dialog plus world files (`english-input.txt`, `init-*.world`) | `Tasks/From-English/rosie-teaching/tools/rosie_gen.py` with a writer per task family (blocks, river, logic, grid, chess, solitaire, swap) | `<task>-rules.soar`, loader, Visual Soar project |
| WorldSpec | free English (`english-input.txt`); a WorldSpec description is written from it (Lean `WorldSpec/Tasks/<T>.lean`, or Python `<task>-spec.py`), with an assumption ledger | path A: `lake build rosiegen` (Lean); path B: `worldgen/spec_backend.py` (Python). Both write identical rules | rules, loader, JSON export of the description |
| worldgen | a Python task description (`wg.Task`) | `SoarLean/worldgen/gen_*.py`, `world_backend.py` | rules |

All routes share `worldgen/wg.py` and write rules that follow World-Conventions (spec v8) and load on top of the default-world library. WorldSpec descriptions can be checked before any rules are written: `check` (goal, losing conditions and maintained relations in a world file), `explore` (reachable states), `replay` (a plan).

## 2. The task itself

These statements define the problem: initial state, legal actions, goal, losing conditions. Rosie phrasing is shown; WorldSpec accepts any English that maps to the same structure.

| What | English | Generated |
|---|---|---|
| World | `Load init-X.` (a world file: objects with attributes, relations `on`, `below`, sets) | world objects (`^type` from category), relation objects, a task object |
| Action | `You can move X onto Y.` Adjectives and relative clauses in X and Y are preconditions. `The name of an action is A.` | a task operator with `^argument1..3`; look-ahead and real-world applications |
| Concept | `If C then it is P.` | a positive concept is expanded in place; a concept that tests absence and decides legality becomes a maintained relation, kept by every action |
| Comparison | `If the V of a X is more than the V of a Y then the X is R the Y.` | a comparative relation |
| Count | `the number of the blocks that are on C` | an attribute kept by the actions |
| Goal | `The goal is that C.` (`all the X are on a Y` expands over the world file) | `^goal-met true` on the task object; one desired |
| Losing | `If C then you lose.` | `^failure`; losing takes precedence over the goal |
| Solution length | `The solution has N steps.` | look-ahead depth limit max(12, N) (L16-045) |

WorldSpec adds forms that Rosie does not teach: derived relations recomputed each state ("Albert does not know"), sums over groups, effects over every match ("every date in that month is ruled out"), updates with arithmetic on integers ("add the time of the crossing to the elapsed time"; `plus`, `minus`, `times`, and `quot` and `rem` for the integer quotient and remainder, since 26 Nov 2026), computed in effects only (a condition cannot compute; keep a value it needs, such as the room left in a jug, as a property and update it), a step cost per operator, and monotonic operators (their effect follows from the state and is never undone, L15-027).

Generated automatically, not stated: objects that nothing in the task tells apart (same category and attributes, never named, never related to one another) are kept as counts per place, `^<kind>-count` (L7-027). Missionaries and cannibals is the example.

## 3. Lines that augment a task

Each line is optional, is placed after the teaching script, and never changes the problem. A task without the line is generated exactly as before.

| Line | Effect | Convention |
|---|---|---|
| `Learning: do not learn from look-ahead. <reason>` | `chunk never` after the library (default: chunking on) | L5-021 |
| `Goal <name>: <goal statement>.` | an extra named goal, `^<name>-met` | L8-026 |
| `Phases: first <goal>, then <goal>, ..., finally <goal>.` | goals pursued in order (a `^next-desireds` chain) | L8-026 |
| `Repeat: from <goal>[, N times][, until <goal>].` | the last phase returns to `<goal>`; `N times` sets `^repeat-count`; `until` sets `^termination-desireds`; neither: loops for ever | L8-027 to L8-030 |
| `Output: command <c>; name attribute <a>; arguments <a1> <a2> <a3>; done ...; success ...; error ...; applied <s>.` | the environment's command form (section 5) | L10-018 |
| `Search control` section | search-control items (section 4) | L15-026 |

In WorldSpec the same are fields of `Task`: `learning`, `phases`, `loopStart`, `termination`, `repeatCount`, `output`, `evalMarks`. The Lean semantics (`check`, `explore`, `replay`) test only `goal`, not phases.

Example (`block-puzzles/sorting-phases`):

```
Goal gathered: all the blocks are on the red location.
Phases: first goal, then gathered.
Repeat: from goal, 2 times.
```

## 4. Search control

Search control is knowledge about how to search, kept apart from the problem so that each item can be switched on and off in tests (`gen.py --control none|all|SC-1,SC-3`). Format:

```
Search control
  SC-1 [evaluation]: During look-ahead, first try crossings that carry two blocks to the destination bank, ...
```

| Kind | Meaning | Generated |
|---|---|---|
| evaluation | which tied operators look-ahead evaluates first or last | `^evaluate-first` / `^evaluate-last` on proposals (L15-026). Suspended in v2.47: the library ignores the marks, because they entered learned rules and slowed learning |
| operator-preference | prefer or reject operators ("do not move the smallest block twice in a row") | preference rules |
| method | a decomposition ("work toward one block at a time") | operator and desired rules |
| desired-order | the order in which desireds are pursued | (no translation yet) |

The translation of an item is written per task family; an item with no translation stops generation with an error rather than being ignored. WorldSpec also accepts `repeatControl`: a look-ahead state whose situation already occurs on its path fails.

## 5. External environment

By default real actions are applied to the agent's own world, and the agent issues the library's default command, `^perform-action` with `^name` and `^argument1..3` (the Thor-Soar form). For another environment, the `Output:` line (or WorldSpec `output`) gives:

- `command`: the output-link attribute (`command action` makes the action name itself the command);
- `name attribute` and `arguments`: where the action and its arguments go;
- `done`, `success`, `error`: the status values the environment reports;
- `applied`: the status on which the completed command is applied to the agent's world.

The generator writes the environment-effect rules and the output map (`<task>*elaborate*environment-output-map`). In games, the opponent's moves arrive on the input-link and are applied by task rules (L3-092, L3-093); look-ahead covers only the agent's own moves.

## 6. Search settings

Settings that differ from the library defaults are written as `^flag-override` on the top state (WorldSpec `flags`).

| Flag | Default | Use |
|---|---|---|
| `max-evaluation-depth` | 12 | look-ahead depth; set by the solution-length statement |
| `iterative-step` | operator | `tie-impasse`, or `cost` (deepens by cost; use with `cost-metric unit` and per-operator step cost) |
| `cost-metric`, `optimize` | none, false | cost-aware selection of outcomes |
| `max-look-ahead-steps` | 1000 | backstop on runaway look-ahead (L16-046); not used with `iterative-step operator` |
| `rl`, `explore` | false | reinforcement learning, exploration |

## 7. Checks the generators make

- Each generated agent is run on seeds 1-3 (`run_agent.py`); the plan is replayed in Python (`check_plan.py`) or Lean (`replay`).
- The instructor's example worlds: goal true only on `final-*`, failure true only on `fail-*`.
- Rosie "There is N." answers fix the number of action instances.
- Readings the English left open are recorded in each task's README (assumption ledger); gaps are raised with the user before generation.
- Each generator reproduces its stored agents byte for byte before a release.
- WorldSpec descriptions are checked for well-formedness on both paths (Lean `Task.wellFormed`; Python `spec_backend.well_formed`, run by `worldspec_py.py json` and by `spec_backend.py`, since 26 Nov 2026): no negation in a compiled condition (operator conditions, losing conditions, goal; put "nothing is on it" in a derived relation and test that, W-CHK-009), effects and reports use only parameters and variables bound by the operator's `bind` (a variable known only in its preconditions would be a new identifier on every firing), no arithmetic in a condition, no open gap in the assumption ledger, and no two objects with one handle.
- World files: a trailing `1` is read as a Rosie sense number only after a word of two or more letters (`red1`, `on1`, `destination1`); names such as `d1`, `t1`, `c11` keep it (26 Nov 2026; before, `d1` silently became `d`).

## Further reading

- `Tasks/From-English/rosie-teaching/tools/rosie-language.md`: every Rosie statement form and its reading.
- `SoarLean/agentgen/WorldSpec/Types.lean`: the WorldSpec description, field by field.
- `Conventions/World-Conventions-Spec-v8.md`: the conventions cited above.
- Examples: `rosie-teaching/block-puzzles/sorting-phases`, `sorting-output`; `river-crossing-puzzles/missionaries-and-cannibals` (search control, counts); `webtasks/classic-ai/guard-tour`, `guard-patrol` (phases and loops in WorldSpec).
