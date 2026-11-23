# Blocks world

*Task description for a human solver, written 21 November 2026 by Claude, supervised by John E. Laird, from the public sources listed at the end (paraphrased, not quoted).*

Lettered blocks sit on a table, some stacked on others. You may move one block at a time, and only a block with
nothing on top of it; it can go onto the table or onto another block that has nothing on top of it.

Goal: rebuild the blocks into the target stacks.

## This instance

In the look-ahead variants, A and B start on the table and C on A; the goal is A on B, B on C and C on the table (a
three-block tower C-B-A). Other variants (simple, simple-3, hierarchical, rl, hrl, operator-subgoaling, epmem, random)
use the arrangement in their own initialize rules.

## Sources

- [Blocks world (Wikipedia)](https://en.wikipedia.org/wiki/Blocks_world)
- [Blocks world planning (AIspace, UBC)](https://www.cs.ubc.ca/labs/lci/AIspace/planning/)
