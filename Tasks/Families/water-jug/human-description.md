# Water jug puzzle

*Task description for a human solver, written 21 November 2026 by Claude, supervised by John E. Laird, from the public sources listed at the end (paraphrased, not quoted).*

You have two unmarked jugs, one holding 3 gallons and one holding 5 gallons, both empty, and an unlimited supply of
water. Because the jugs have no markings, you can only measure an amount by filling a jug to the brim or by pouring
until one jug is full or the other is empty. In one step you may fill a jug completely, empty a jug completely, or pour
from one jug into the other until the receiving jug is full or the pouring jug is empty.

Goal: end with exactly 1 gallon in the 3-gallon jug.

## This instance

All variants (water-jug, -hierarchy, -look-ahead, -look-ahead-failure-states, -rl, -tie and their chunking versions)
use the 3- and 5-gallon jugs, both empty at the start, and the goal of 1 gallon in the 3-gallon jug. They differ in how
the agent solves it, not in the task.

## Sources

- [Water pouring puzzle (Wikipedia)](https://en.wikipedia.org/wiki/Water_pouring_puzzle)
- [Jug Problem (Wolfram Demonstrations)](https://demonstrations.wolfram.com/JugProblem/)
