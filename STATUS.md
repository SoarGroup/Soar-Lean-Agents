# Status — October 31, 2026

A Lean 4 specification of the Common Model of Cognition (CMC) and of Soar 9.6 built on it,
with an executable model (`soar-lean`) checked against the Soar 9.6.5 release. The report,
doc/Soar-on-CMC-Lean.pdf, is the main document; this file is a short summary.

## What is covered

- The decision cycle: preference memory, elaboration loops, i- and o-support, impasses and
  substates, results, the goal dependency set, input and output.
- Chunking (explanation-based learning).
- Reinforcement learning, including Q-learning, eligibility traces, GQ(λ) and templates.
- Exploration policies and Soar's random-number generator, bit for bit.
- Semantic memory, including base-level and spreading activation.
- Episodic memory.
- Semantic and episodic stores kept in files between agents (`database file`, `path`,
  `append`; `smem --backup`, `--clear`, `--init`), as Soar 9.6.5 reopens its databases.
- Working-memory activation and forgetting.
- The right-hand-side function library.
- Soar's Rete: the order in which matches fire and retract, and Soar's timetags. The model of
  the Rete is also the matcher, except for rules with long-term-identifier tests.

Out of scope by decision: the explainer and the spatial-visual system. Brought back into scope
on October 31 and done the same day: the memory databases on disk, and rules made from RL
templates while chunking.

## Evidence

- **Proofs.** `lake build` checks 348 theorems (339 about Soar, 9 for the CMC backbone),
  with no unproved steps and only Lean's standard axioms, also in the compiled program (its
  hash-table lookup is proved equal to the matcher it stands for). Besides properties of the
  cycle and the memories:
  - the matcher is proved sound and complete for positive conditions, negations and negated
    conjunctions (inner negations to any depth, with the variables of an inner negation local to it), and the order of positive patterns is proved
    not to change the matches (Soar/MatchComplete.lean);
  - the join order returns the rule's own conditions, reordered, and exactly a permutation when
    no relational test between variables has to move; a moved test keeps its meaning between
    numbers and between identifiers, but not between values of different types, in Soar too
    (kernel defect 6) (Soar/JoinOrder.lean); and, when every relational test between variables
    compares values of one kind (and the patterns have no `@` test), the positive patterns of the
    join order hold under the same bindings as the rule's own and the matcher finds the same
    instantiations (`joinOrder_posSat`, `joinOrder_matches`, `joinOrder_matches_rev`,
    Soar/JoinOrderSem.lean);
  - `reach` (working memory's link to a state) returns exactly the identifiers reachable from
    the roots (`mem_reach_iff`, Soar/ReachProps.lean);
  - from the initial state, every state has at most one selected operator after any number of
    decision cycles (Soar/Seriality.lean).

  The theorems are properties of the model; they do not prove that the model is equivalent to
  Soar 9.6.5.
- **Comparison with Soar 9.6.5.** About 2,800 programs in tests/, compared with
  `tools/run_all.sh` (see the README). Hand-written programs, generated programs and the Soar
  repository's own test agents match in decisions and final working memory, and where relevant
  in learned rules, learned values, memory stores and activations. Every set that is also run
  without Soar's choices replayed matches that way too.
- **Remaining differences** (report Section 2; doc/DIFFERENCES.md), none of them in the
  decision cycle, all from Soar's undefined or address-dependent behaviour:
  - Two episodic programs (one of them matching or not from run to run): Soar tries
    graph-match mappings in memory-address order.
  - One semantic-memory test agent (AlphabetAgentAllOn), and 9 of 30 edge-updating
    programs (generated, not in tests/): Soar reads freed or out-of-bounds memory.

## Findings

- **Soar 9.6.5 kernel:** 29 defects across eight modules.
  doc/Soar-9.6.5-Kernel-Defects.docx gives the source location, cause and a recommended
  fix for each. The fixes are untested sketches. bugs/ has programs that show the main ones.
- **Soar manual:** 43 places where it is wrong, silent or ambiguous (report Section 11).
- **The CMC:** five findings (report Section 13).

## Not yet done

- **Proofs:** the chunking computation; the same preservation for negations and for Soar's
  reorderer (which in the model affects only chunking), and that `joinOrder` yields a safe order.
- **The ad hoc places** listed in report Section 10, among them justifications in the Rete
  model, Soar's batches of working-memory changes, and long-term-identifier tests in the network.
- **The map spreadsheet** (doc/Soar-Lean-map.xlsx): six areas reviewed line by line against
  Soar (126 of 607 definitions: 71 agree, 44 differ, 11 are data types; six right-hand-side
  differences fixed, most parser and syntax differences not yet confirmed by runs); the other
  areas not yet.

The plan is in doc/Soar-on-CMC-Lean-Remaining-Work.docx; a code review for simplifications and
optimizations (October 31) is in doc/Soar-on-CMC-Lean-Code-Review.docx, with the five
reviewers' reports in doc/review/. Done from the review (October 31): the speed items S1, S2,
S4–S6, S7, S8–S12, S14–S19 (hash sets and maps beside the lists, `dedupFirst`, `ttMap` with
`ttMap_getD_eq_ttOf`, the empty-list short-circuits), P1 (`Conform.cmcStep_pst` and
`runCMC_pst`: a CMC cycle of the Soar instance is `St.cycle`, via `St.cycleElab`, `St.cycleDec`
and `St.cycleApply`), the stale files (Soar/Examples.lean, Fuzz*.lean and their outputs), and
part of the dead code and docstring list. Also done (October 31; the full regression after the last change to the executable shows only the known differences): S3, S13, S20–S28 (S25 includes the `learn` accumulators and hash-based union-find); the dead parameters `Goal.rlQ`, `_deselected`, `_pre`, `isFirst`; from P2, the `foldl_rel` lemma (replacing seven fold inductions), the merged `decideImpasse` lemmas, the shared `stage2_impasse` lemma for the three impasse-cause theorems, the `St.Same` relation, and the move of the reinforcement-learning, template-rule and tie-picking lemmas from Cycle.lean to Props.lean; the merged `STest` and `eqOf` duplicates; two docstring fixes. Later the same day: the remaining fold inductions in SMemProps and EpMemProps now use `foldl_rel`; `Pat.binds` is merged into `Pat.eqVars`; `symRank` is an array and `Rete.names` a hash set; `keepEdges` is linear (a hash map of the new rows) instead of removed through `calcSpread_content`, which is not proved; `curMatches_off` and `matchConds_neg_eq_ncc` are proved; docstrings in SMem, Chunk and EpMem fixed; `NegTree.holds` is structural (mutual with `NegTree.noneHold`) instead of `partial`; with it, matcher completeness is proved for negated conjunctions nested to any depth (`tree_complete`, `tree_clear`). Then `rlUpdate_frame` (one lemma for what a reinforcement-learning update leaves alone) and `fireMatch_eq_fireOneBase`; the P3 equalities `deepCopy_eq`, `dedupFirst_eq`, `cycSub_eq` and `ttMap_getD_eq_ttOf` already existed. The code review is closed (November 1): every item is done or closed with its reason in doc/Soar-on-CMC-Lean-Code-Review.docx (Closure). Also then: `sync_idem` (SyncProps), `reteSupport_nil` (SupportProps), `calcSpread` proved through its stages (`calcSpread_keeps`; `keepEdges` removed), the reinforcement-learning tables merged into `rlTab`, `upd` once in CMC/Util.lean, strength notes on `quiescence_ie/pe` and `cycle_independent_of_decl`. Also: `mem_reach_iff` and the preservation of matches by the join order (`joinOrder_matches`) are proved. Developer notes: CLAUDE.md,
doc/HARNESS.md (versions and run times) and doc/DIFFERENCES.md (diagnoses).
