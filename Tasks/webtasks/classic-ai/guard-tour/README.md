# Guard tour (phases test, 24 Nov 2026)

A test of phases (World-Conventions L8-026, L8-030): "First the robot goes to square C, then back to square A, and
finally to square B." The description (`guard-tour-spec.py`, printed to `GuardTour.lean`) has three phases, at-c, at-a
and at-b; the generated rules chain them with ^next-desireds. Paths A (`rosiegen compile`) and B (`spec_backend.py`)
give identical rules and the JSON exports agree. Library v2.47 candidate: seeds 1-3 move B C B A B (5 moves, the
shortest), 32-38 decisions. The semantics check (`worldspec_py.py replay`) tests the goal field, which holds the last
phase; it does not follow the phases.
Written by Claude, supervised by John E. Laird.
