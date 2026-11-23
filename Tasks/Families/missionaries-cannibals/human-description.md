# Missionaries and cannibals

*Task description for a human solver, written 21 November 2026 by Claude, supervised by John E. Laird, from the public sources listed at the end (paraphrased, not quoted).*

Three missionaries and three cannibals stand on the left bank of a river with a rowing boat that carries one or two
people. The boat never crosses empty. If, on either bank, the cannibals ever outnumber the missionaries who are there,
the missionaries are eaten (a bank with no missionaries is safe).

Goal: get all six people to the right bank.

## This instance

mac picks crossings without searching; mac-look-ahead and mac-look-ahead-numeric plan the crossings by look-ahead;
mac-rl learns which crossings to choose over many episodes. All start with everyone and the boat on the left bank.

## Sources

- [Missionaries and cannibals problem (Wikipedia)](https://en.wikipedia.org/wiki/Missionaries_and_cannibals_problem)
- [Missionaries and Cannibals (G. Wickler, University of Edinburgh)](https://www.aiai.ed.ac.uk/~gwickler/missionaries.html)
