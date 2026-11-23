# Stacking frogs (with blocked stacks)

*Task description for a human solver, written 21 November 2026 by Claude, supervised by John E. Laird, from the public sources listed at the end (paraphrased, not quoted).*

Frogs sit on a row of lily pads. A stack of frogs moves as one: it must jump exactly as many pads as there are frogs in
the stack (one frog jumps one pad, a stack of two jumps two, and so on), counting empty pads, and it may only land on a
pad that already has a frog, joining that stack.

Goal: gather all the frogs into as few stacks as the puzzle asks for.

## This instance

A variant in which a stack whose bottom frog is red may not move; all frogs must end in one stack (init-lzstacked-frogs.world).

## Note

The red-frog restriction is specific to this Rosie variant; the sources describe the basic jumping-frogs puzzle.

## Sources

- [Jumping Frogs Puzzle (MathWorld)](https://mathworld.wolfram.com/JumpingFrogsPuzzle.html)
