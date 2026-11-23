# Three wizards (the wise men puzzle)

*Task description for a human solver, written 21 November 2026 by Claude, supervised by John E. Laird, from the public sources listed at the end (paraphrased, not quoted).*

Three wizards, A, B and C, sit where each can see the others but not himself. Each has a spot on his forehead that is
either white or black, and they are told that at least one spot is white. They are asked in turn whether they know the
colour of their own spot; each can reason about what the others would have concluded from what they see and from the
answers so far.

Goal: a wizard correctly states the colour of his own spot.

## This instance

The agent reasons from A's point of view, modelling what B and C know; B and C start marked (rule ^mark 1), A unmarked.
The puzzle is the classic three wise men puzzle; the family calls them wizards.

## Sources

- [J. McCarthy, Formalization of two puzzles involving knowledge (wise men puzzle)](https://eu.swi-prolog.org/pack/file_details/narsese/jmc/puzzles.md)
- [Induction puzzles (Wikipedia)](https://en.wikipedia.org/wiki/Induction_puzzles)
- [Non-classical logic notes, wise men example (University of Miami)](https://www.cs.miami.edu/home/geoff/Courses/CSC345-26S/Content/KnowledgeRepresentation/NonClassicalLogic.shtml)
