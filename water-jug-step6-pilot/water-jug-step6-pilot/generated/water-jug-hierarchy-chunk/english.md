# water-jug

## The task

The task state holds several values of `jug`, each a jug. The jugs.

A jug has `volume` (an integer), `contents` (an integer).
Its `free` is derived: self.volume − self.contents (with `self` the jug). It is recomputed whenever those values change and is never set directly.

Initially the task state has:
- a `jug` with volume 3 and contents 0
- a `jug` with volume 5 and contents 0

**Goal.** Some jug has volume 3 and contents 1. When the goal holds in the task state, the agent reports success and halts.

## Operators

An operator's changes are made together: every value on the right is read before any change.

**fill(jug: jug).** Proposed when jug.free > 0. Fill a jug from the source, to its volume.
- Effect: jug.contents := jug.volume.
- Carried out in its own substate by the steps pick-up, fill-jug, put-down, in that order; the last step makes the changes above.

**empty(jug: jug).** Proposed when jug.contents > 0. Pour a jug out onto the ground.
- Effect: jug.contents := 0.

**pour(from: jug, to: jug).** Proposed when from and to are different objects and to.free > 0 and from.contents > 0. Pour one jug into another until the first is empty or the second is full.
- If from.contents > to.free: from.contents := from.contents − to.free; to.contents := to.volume.
- If from.contents ≤ to.free: from.contents := 0; to.contents := to.contents + from.contents.

## Choosing among proposed operators

Any proposed operator may be chosen; the choice is random.

## Learning

Chunking on (`chunk always`).

## Assumptions (added; not in the task description)

- **A1** [open] Pouring moves as much water as fits: the amount is the smaller of the source's contents and the target's free room. (All originals; stated in code, not in any description.)
- **A2** [open] Contents stay between 0 and the jug's volume. (Implied by the originals; checked here over every reachable state, `contents_in_range`.)
- **A3** [open] The goal is that some jug of volume 3 holds 1, written as a `^desired` structure. Most originals tested for it directly in a rule, without `^desired`.
- **A4** [open] In the tie heuristic, `none` means before the first task operator; the initialize operator does not count as a last operator. (Checked: water-jug-tie behaves the same way, because its recording rule tests `^name water-jug`, which the initialize operator itself creates.)
- **A5** [open] In hierarchical fill, pick-up, fill-jug and put-down are bookkeeping steps: only the last changes the task state (the jug's contents). The originals marked the jug itself (`^picked-up`, `^filled-jug`) as results; here the markers stay in the substate.
- **A6** [open] Look-ahead: a state is a duplicate of an ancestor when every jug has a jug in the ancestor with the same volume and contents. The originals compared exactly the 3- and 5-litre jugs.
- **A7** [open] Every variant halts when the goal is reached. (water-jug V2/V3 and all others did; the RL variant also gives its reward first.)
- **A8** [open] Names: the derived room left is `free` (originals: `empty`, which is also an operator's name); pour's parameters are `from` and `to` (originals: `empty-jug`/`fill-jug`, or `jug`/`into`).
