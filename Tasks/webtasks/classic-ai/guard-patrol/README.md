# Guard patrol (loop test, 24 Nov 2026)

A test of a loop with a repeat count (World-Conventions L8-027, L8-029, L8-030): "The robot goes to square C, then back
to square A, and repeats this three times." Two phases (at-c, at-a), the loop back to the first (^loop-start) and
^repeat-count 3. Paths A and B give identical rules and the JSON exports agree. Library v2.47 candidate: seeds 1-3 make
the 12 moves B C B A three times, 57-63 decisions, and halt when the count reaches 0. The semantics check tests the goal
field (the last phase); it does not follow the loop.
Written by Claude, supervised by John E. Laird.
