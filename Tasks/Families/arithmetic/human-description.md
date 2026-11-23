# Multi-column arithmetic

*Task description for a human solver, written 21 November 2026 by Claude, supervised by John E. Laird, from the public sources listed at the end (paraphrased, not quoted).*

Solve multi-digit addition and subtraction problems column by column, as taught in school: write the numbers one above
the other, work from the ones column leftwards, carry 1 to the next column when a column's sum is 10 or more, and borrow
from the next column when a digit to subtract is larger than the digit above it.

Goal: give the correct answer to each problem.

## This instance

addition and subtraction solve single problems; arithmetic, arithmetic-v5 and the smem variants generate random
three-digit problems and solve many of them in a row (10,000 for arithmetic, 1,000 for arithmetic-smem), using
semantic memory for arithmetic facts in the smem variants.

## Sources

- [Arithmetic (with Semantic Memory) agent, Soar downloads](https://soar.eecs.umich.edu/downloads/agents/arithmetic_%28with_semantic_memory%29/)
- [Addition with carrying (Adult Literacy Fundamental Mathematics)](https://opentextbc.ca/alfm2/chapter/addition-with-carrying/)
