# Library findings review: resume point (stopped 10 Nov 2026, 20:24)

Going through Library-Findings.docx, High findings first, checked against JEL's library
(default-world.zip uploaded 10 Nov 20:21).

## Decisions so far
- LF-01: accepted; in JEL's library (-^world on propose*initialize-agent-world).
- LF-02: accepted (operator copy); the two rules are in JEL's library.
- LF-03: already fixed by JEL (^copied-from desireds + ...super-operator-desireds*copy).
- LF-12, LF-13, LF-15, LF-17: moot (no ^environment none mode).
- LF-14, LF-16: already fixed in JEL's library.

## Open question (resume here)
LF-19: the world copy skips category, mass, instance-of, accessible, anchored. Proposed fix: an explicit
^dont-copy-object-attribute list on the evaluation state, extendable by tasks. Question for JEL: why are
category, mass and instance-of excluded (Thor-only constants, or something breaks if copied)?
Then test on five houses with ^category restored.

## Still present in JEL's library, in review order
High: LF-20, LF-21, LF-22, LF-23, LF-24, LF-32, LF-38 (LF-44, LF-45 are kernel reports).
Need a run: LF-33, LF-04, LF-36, LF-39.
Medium/Low still present: LF-05, LF-06, LF-08, LF-10, LF-34.

## To restart
Say "continue the library findings review". Claude's working copy of JEL's library: /home/claude/jel/default-world
(re-upload default-world.zip if the session is new).
