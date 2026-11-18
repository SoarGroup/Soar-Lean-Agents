# Finding: chunks learned in look-ahead are over-general, so chunking can make solutions longer

14 November 2026. Library v2.28 and v2.29 (`^flags.failure-grounding counter`, the default), Soar 9.6.6 (kernel 9.6.50), `chunk always`. Not fixed in the library; one cause is avoided by a task convention (below).

**Status (decision, 14 Nov 2026):** chunking stays off by default in look-ahead only as a temporary measure. Leaving it off is not acceptable as an end state: learning in look-ahead is wanted, and a better way must be found. The solutions below are the candidates.

## Update, 15 November 2026: optimal with chunking under tie-impasse depth with cost

Library dev (to be v2.30), worldgen with literal handles, `chunk always`, tie-impasse depth, `^cost-metric unit ^optimize true`. Run 2 starts with the chunks saved at the end of run 1 (same seed) and keeps learning.

| Task (seeds) | No chunking | Run 1 (median decisions) | Run 2 (median decisions) |
|---|---|---|---|
| Water jug B1 (5) | 8 on all | 8 on all (5,869) | 8 on all (4,576) |
| Water jug D1 (5) | 8 on all | 8 on all (6,018) | 8 on all (4,513) |
| Water jug B3 (5) | 8 on all | 8 on all (384) | 8 on all (76) |
| Water jug D3 (5) | 8 on all | 8 on all (602) | 8 on all (135) |
| Hanoi (6) | 3 on all | 3 on all (372) | 3 on all (191) |
| Blocks world (6) | 3 on all | 3 on all (697) | 3 on all (689) |
| Missionaries and cannibals (3) | 11 on all | 11 on all (164) | 11 on all (110) |
| Artists-2 (3) | 5 on all | 5, 7, 5 (473) | 5 on all (81) |

(Missionaries and cannibals and artists-2 are from the run before handles were made literal; their rules are hand-written and unchanged.) With the operator iterative step and chunking, water jug B1 and D1 still give 24 operators on one or two seeds. The causes and what removed them:

1. **Results computed below a depth cut-off.** A value computed in a look-ahead that was cut off by the depth limit is a guess relative to that depth. Every evaluation now starts with `^lower-bound none`; a cut-off below it replaces that with the cost bound of the cut-off branch, passed up through nested selections. Every rule that writes a value into an evaluation tests `^lower-bound $ <lower-bound>`, so the chunk keeps the bound as a constant: a value learned with `none` holds at any depth, and one learned below a cut-off fires only where the same bound has been reached again, never in a fresh evaluation. (Without `$`, the bound was variablized because it was already a superstate wme when the value was written, and the chunk matched any evaluation.) The depth itself cannot be tested: it exists only in the top selection substate.
2. **A success learned without its cost.** Two rules returned a success, one with the path cost and one without; the chunk of the second fired alone in other contexts and gave successes with no cost. With a cost metric, success is now returned only by the rule that also returns the cost.
3. **Failure-cutoff preference without the holder.** `worse*failure-cutoff-numeric-value2` made an operator worst because its look-ahead passed the best value found, without naming the operator that held that value. Its chunk could bind both to the same operator and made the best operator worst (Hanoi loop). The rule now names the holder and tests that it is another operator; a second version covers a best value passed down from above (`^passed-down-minimum`).
4. **Cause 2 (wmes that survive): literal handles.** In Hanoi run 2, a chunk learned from the look-ahead D1 to P2, D2 to P3, D1 onto D2 also matched D1 to P3: the destination and the goal peg were separate variables with no inequality. Task rules now test object handles with `$` (World-Conventions-Spec-v6, L11-005; worldgen default). Chunks keep handles as constants and transfer only to the same named objects. Two Soar 9.6.50 defects showed up: `$` inside a negated condition makes Soar report "bad test type in hash_test ... Soar cannot recover" each time it builds a justification from the rule (the run goes on; Hanoi and water jug still solved, blocks world did not), and `$` inside a `{ ... }` test that also holds a relational test (`{ <> <bh> $ <dh> }`) crashes Soar (segmentation fault). The generator avoids both. Neither construct occurs in the library or the test-set programs except `{ $ <count> > 2 }` in init-current-evaluation-depth.soar, used only with `^init-evaluation-depth unachieved-desireds`, which no test sets. Both defects should be reported to the Soar developers.

Also part of this work: an open evaluation (one with a cut-off bound below the best value) is not allowed to lose at the top level, so the top tie is searched deeper instead of committing greedily (`^closed`, `^bound-check`), and the unary success-best preference is not used with tie-impasse depth and optimize, because its chunk tests only the successful operator.

Still open: artists-2 seed 2 in run 1 (7 crossings); chunking with the operator iterative step; transfer of chunks across differently named objects (needs a chunking mechanism that keeps distinct handles distinct, or explicit frame tests, solution 7 below).

## Symptom

With chunking on, look-ahead still finds solutions, but some are longer than the optimum, while every run without chunking is optimal.

| Task (seeds, optimum) | No chunking | `chunk always` |
|---|---|---|
| Towers of Hanoi, 2 discs, derived `clear` (6, 3 moves) | 3 on every seed | 3, 3, 4, 3, 4, 3 |
| Towers of Hanoi, maintained `clear` (6, 3 moves) | 3 on every seed | 6, 3, 4, 3, 3, 3; seed 5 not solved in 3,000 decisions |
| Blocks world, maintained `clear` (6 + 3 static layout, 3 moves) | 3 on every seed | 3 on every seed (median 276 decisions against 384) |
| Water jug 7/9, world conventions, B1 (5, 8 operators) | 8 on every seed | 24, 8, 8, 8, 8 |
| Artists and managers, 2 pairs (3, 5 crossings) | 7, 5, 5 | 9, 9, 7 |

The failure and depth-limit results are not the cause: their chunks test the world version stamp (`^stamp`, kept as a constant by `$`) and never match again. The over-general chunks are success chunks (`...symbolic-evaluation*from-subgoal*success`, and the `...success-evaluation-becomes-best-preference` chunks built on them) and depth-exceeded chunks, which are not grounded.

## Why there are problems

Chunking builds a rule from the superstate wmes that the substate's reasoning tested. Two kinds of dependence are not wmes the substate tested, so they are missing from the chunk.

### Cause 1: negations over the look-ahead world (local negations)

A look-ahead world is substate structure. A rule that tests the absence of something in it ("no disc is on this peg", "no world relation matches this desired") contributes nothing to the chunk: Soar leaves local negations out (`chunk allow-local-negations on`, the default).

Hanoi, seed 3, derived `clear`. The first decision is a tie between D1→P2 (optimal) and D1→P3. Both get a best preference from the same chunk, so Soar chooses at random and took D1→P3. The chunk summarizes the 3-move look-ahead D1 off D2, D2 onto P3, D1 onto D2. The second move is legal only because P3 is clear, and `hanoi*elaborate*world*clear` derives `clear` by testing that no disc is on the peg. The explainer shows that rule (4 firings) and `hanoi*elaborate*state*unachieved*relation2` (also a negation, 2 firings) in the chunk's formation, and neither negation in the chunk. The chunk reads: with D1 on D2, D2 on a peg, and the goal D2 on a peg with D1 on D2, moving D1 anywhere leads to success. It matches D1→P3, which blocks the peg D2 needs.

Evidence that this is general: Soar's statistics for that run count 130 chunks that "used negated reasoning about sub-state". With `chunk allow-local-negations off` (Soar then builds no chunk that depends on a local negation) every run is optimal (Hanoi 3 moves on all 6 seeds, water jug B1 8 on all 5, artists-2 7, 5, 5), but only 0 or 1 chunks are learned per run, so learning stops helping.

### Cause 2: wmes that survive because an operator did not touch them

With `clear` maintained by the move application (no negation), Hanoi seed 3 still opens with D1→P3. Both first moves again get best preferences from one chunk. The chunk now tests that the destination is clear, and that the goal peg P3 is clear, but not that the destination is a different object from P3.

In the look-ahead, D1 went to P2: the application removed P2's `clear` and left P3's. D2 could then move to P3. P3's `clear` survived only because the destination was not P3. No rule tested that inequality; it is a consequence of which wme the operator removed. In the chunk, the destination and P3 are separate variables, and Soar variables may bind the same object, so the chunk also matches D1→P3. EBC has no setting that adds such inequalities (the chunk settings in 9.6.6 are learning mode, bottom-only, add-osk, allow-local-negations, allow-opaque, singletons, limits). Singleton declarations constrain how many values an attribute has; they do not state that two objects differ.

### Still open

- Hanoi with maintained `clear` and `allow-local-negations off` still learns no chunks, so its remaining chunks also depend on local negations: the goal test (`hanoi*elaborate*state*unachieved*relation2`, a negation over the world, tested by every proposal through `^unachieved`) is the likely one. Not traced.
- Water jug B1 (24 operators on one seed) has no `clear`; which negation or survival causes it was not traced.
- Other derived, negation-based attributes remain in tasks: the artists bank `^empty` (also the goal), and the unachieved-desired rules of every generated task.

## Possible solutions

1. **Task convention (adopted for `clear`; now convention L11-003).** A relation or property that decides whether an operator is legal in look-ahead is maintained by the operator's application, not derived by negation. Hanoi and blocks world now do this for `clear`, declared with `^copy-relation clear` (library v2.29 copies one-argument relations). It removes cause 1 for that relation. It is enough for blocks world, not for Hanoi (cause 2).
2. **Goal test without negation.** Derive `^unachieved` positively, for example by maintaining achievement in the application of the operator that changes the relevant relation, or by counting achieved desireds and comparing with `^desired-count` without testing absence. Library and generator change; not tried.
3. **Keep chunking off for look-ahead (current default).** Every run is optimal; no learning speed-up. With `allow-local-negations off` the agent is also correct but learns almost nothing.
4. **Ground success results like failures.** Testing the stamp in success and depth-exceeded results would stop all transfer, which also removes the benefit (chunks would never match again). Only useful to measure the cost of over-generality, not as a fix.
5. **Change chunking (architecture).** Two changes would address the causes directly:
   - For cause 2: when a result depends on a wme in a set from which an operator removed a different member (here, the `clear` relations), add an inequality between the removed object and the surviving one to the chunk.
   - For cause 1: represent a local negation in the chunk by the superstate wmes that made it true, where the negated structure is a copy of superstate structure (a look-ahead world copy): the absence in the copy implies an absence in the original, unless an operator in the look-ahead changed it, which brings back cause 2.
6. **Ground success results in the whole state, not the stamp (most promising, untested).** If success and depth-exceeded results read the declared state before they are returned (as failures did with `^flags.failure-grounding explicit`, ideally with `^ground-object-attribute` to keep it small), their chunks test the complete state and transfer only to an identical state: a transposition table. That still pays off, because iterative deepening re-searches the same look-ahead states at every depth and the agent revisits states across real steps. Costs: a grounding pass per result, larger chunks, and the earlier out-of-memory failure of chunking over the explicit grounding chain must not recur (it occurred with the full-world pass, before `^ground-object-attribute`).
7. **Explicit frame tests in the application (untested).** The application could test, with an explicit inequality, each relation of the kind it changes that survives (for example `(<c2> ^argument1 { <> <d> })` for every other `clear`) and mark it, and the proposals could test the mark. Rule-level inequality tests are kept in chunks, so the missing inequality of cause 2 would appear. Costs: more rule firings per application and a less natural task encoding.
8. **Restrict where learning happens.** `chunk only` with `force-learn` on selected states (Thor-Soar's setting: `chunk flagged`, force-learn on evaluate-operator states) limits which results are chunked but does not change what each chunk tests, so it does not remove either cause. Not measured.

## Files

- Hanoi with maintained `clear`: worldgen/gen_hanoi.py (also in the test set, programs/gen__hanoi); blocks world: gen_blocks.py (programs/gen__blocks-world). Test set v1.26.
- Experiment harness: /tmp/gx (exp.py, batch.py, firstmove.py, expl2.py), not packaged.
