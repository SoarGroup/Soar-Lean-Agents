# Knight's tour

*Task description for a human solver, written 21 November 2026 by Claude, supervised by John E. Laird, from the public sources listed at the end (paraphrased, not quoted).*

A chess knight moves in an L: two squares in one direction and one square at right angles. Starting from a given square,
move the knight so that it lands on every square of the board exactly once.

## This instance

knights-6 uses a 6 x 6 board and knights-8 the standard 8 x 8 board; the knight starts on b3 (column 2, row 3). The task
is to find many solutions, not one: the agents search all tours from the start square, backing up after each tour and
at each dead end, and count the closed tours (a closed tour ends a knight's move away from the start). They stop after
100 closed tours, after 30,000 moves (each knight move and each backup counts), or when the search is exhausted, and report the
count. (Changed 22 November 2026; the original programs stopped after 1,000,000 moves.)

## Sources

- [Knight's tour (Wikipedia)](https://en.wikipedia.org/wiki/Knight%27s_tour)
- [The Knight's Tour (Wolfram Demonstrations)](https://demonstrations.wolfram.com/TheKnightsTour/)
