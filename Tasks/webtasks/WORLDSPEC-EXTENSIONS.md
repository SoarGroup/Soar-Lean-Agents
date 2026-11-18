# WorldSpec extensions for the classic AI tasks (16 November 2026)

## Done: numbers that change, step costs, repeat control (bridge-and-torch)

Added to WorldSpec (Lean: Types, Sem, Compile, Json, Check; Python: spec_backend.py, worldspec_py.py), with no library change:

| Construct | Meaning | Soar |
|---|---|---|
| `Eff.update x p rhs` | replace the value `x.p` has before the action | `(<x> ^p <x-p> - rhs)` |
| `Rhs.plus a b` | sum of two integer right sides; effects only | `(+ a b)` on the right-hand side |
| `Op.stepCost : Option Rhs` | the operator's look-ahead cost | `^step-cost` on the proposed operator (library `cost-metric unit`) |
| `Task.repeatControl : Option RepeatControl` | search control, not from the English: a look-ahead state that returns to a situation on its path fails (situation: where the objects of the listed types are, by one relation) | four rules: ancestor worlds on each look-ahead state, and a failure rule that compares the current world with each ancestor world directly |
| `Task.wellFormed` | also refuses arithmetic in a condition or a step cost, and variable names the back ends reserve or generate (`s`, `w`, `objs`, `ds`, `op`, `pre`, `pa`, `task`, `any-unachieved`, names with `-`, `rN`, `eN`) | |

The five earlier descriptions give the same JSON and rules as before, and their `wellFormed` proofs still hold. Bridge-and-torch is described, proved well-formed and agrees on every example state in Lean, Python and Soar, but the Soar agent does not solve it yet: the library's cost search (nested caps, success past a losing state) needs a look before it can. See `classic-ai/bridge-and-torch/README.md`.

## Open: four kinds of extension, each a design choice

### 1. Hidden state and percepts: wumpus-world, and counterfeit-coin as a special case

**Skipped (JL, 16 Nov 2026):** option (a) is the right one, but it needs an environment that holds the true state, and these tasks are meant to run without one. Wumpus-world and counterfeit-coin are set aside; the options below are kept for later.

The agent must not see where the pits and the Wumpus are (or which coin is false). Options:

- **(a) The environment holds the truth; the agent plans over what it knows.** WorldSpec gains *hidden* relations, kept on a structure the agent's rules and the look-ahead cannot read, and *percept* rules: after each real action, the environment adds percept relations (breeze in [2,1]) to the agent's world. The agent's knowledge (a room is safe, a room may hold a pit) is derived from percepts by elaborations. Operators are legal only on what is known (enter a room known to be safe). The look-ahead is ordinary deterministic search over the known world, and the agent replans after each percept, as the AIMA hybrid Wumpus agent does. Library: probably none (real actions already go through the output link and environment-effect rules). Cost: knowledge rules need negated conditions ("no breeze, so every neighbour is safe"); see 3.
- **(b) Belief-state search.** The look-ahead world is a set of possible worlds and each action maps sets to sets. This is complete, so it also yields the coin puzzle's branching plan. Cost: a large library change (copying and evaluating sets of worlds) and exponential states.

Counterfeit coin under (a): the environment picks the coin and its weight, the agent weighs and narrows the candidates. Each run solves one case, and 24 runs cover all of them. "Within three weighings whatever the results" is then checked by an AND-OR search added to the Lean semantics, a verification step that changes nothing in Soar.

### 2. Plans that branch on results (counterfeit-coin)

**Skipped with 1 (JL, 16 Nov 2026).**

- **(a)** As above: Soar solves each case, and Lean checks the branching plan.
- **(b)** AND-OR look-ahead in the library: an operator with several outcomes is valued by its worst outcome. This is a selection-world change, and the most general option.

### 3. Knowledge and announcements: muddy-children, cheryls-birthday (done)

Decided by JL (16 Nov 2026): knowledge is represented explicitly, so it is tested by positive conditions; the relations are recomputed automatically (option 1). Added to WorldSpec (Lean and both Python back ends):

| Construct | Meaning | Soar |
|---|---|---|
| `Task.derived : List Derived` | `name(vars)` holds for every binding that meets `defn`; the definition may use negation (`none`, `lacks`) and earlier derived relations | an i-supported elaboration per relation on each world; never copied into look-ahead (not in `^copy-relation`), so every world recomputes it |
| `Eff.each atoms eff` | the inner effect for every match of the atoms (positive only), judged on the state before the action | an apply rule of its own (look-ahead and real world), firing once per match |
| `Task.wellFormed` | negation stays out of operators, `each` conditions, goals and losing conditions (W-CHK-009 unchanged for them); no `each` inside an `each`; no effect changes a derived relation; `dr` added to the reserved names | |

Both puzzles run on seeds 1-3 (Cheryl: July 16 in 21-22 decisions; muddy children: Amy and Ben say yes in round 2, Cal in round 3, 15 decisions), with Lean proofs, matching JSON and rules on paths A and B, 6 of 6 example states agreeing in Lean, Python and Soar, and every run replayed in Lean. The new well-formedness check caught a variable named `w` in the first muddy-children description.

### 4. Proofs instead of plans (mutilated-checkerboard)

No search can answer "no covering exists" in practice. Option: a Lean theorem by colouring (each domino covers one black and one white square; 30 white and 32 black remain), and no Soar agent. WorldSpec is not involved.

## Order proposed

1. Knowledge and announcements (3): done.
2. The colouring proof for mutilated-checkerboard (4).
3. Hidden state (1, 2): skipped until an environment is in scope.
