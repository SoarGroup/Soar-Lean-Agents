> Copy of STATUS.md in `CMC/cmcsoar-release-2026-11-14.zip`. Paths (doc/, Soar/, tests/, tools/) refer to
> files inside that release.

# Status — November 14, 2026

A Lean 4 specification of the Common Model of Cognition (CMC) and of Soar 9.6 built on it,
with an executable model (`soar-lean`) checked against the Soar 9.6.6 release (the reference
since November 14; before, Soar 9.6.5). The report, doc/Soar-on-CMC-Lean.pdf, is the main
document; this file is a short summary.

## Moved to Soar 9.6.6 (November 14)

Soar 9.6.6 fixes the Soar 9.6.5 kernel defects this project reported: all 33 numbered findings
but defect 33, and the departure S1 (doc/Soar-9.6.5-Kernel-Defects.docx, "Status in Soar
9.6.6", gives the fixing commit of each). The model now follows 9.6.6:
- **Baseline:** with the November 14 model, 5,429 of the 5,850 programs then in the regression
  matched 9.6.6.
- **Changes to the model, one per defect:** chunk names from the match goal's impasse (5);
  attribute identifiers as links (30); cross-type relational tests false (6); real zeros
  always 0.0 (21); module slots protected from rules (new in 9.6.6); every new o-supported
  substate element elaborates the goal dependency set (32); support from the new match only
  (10); the reorderer's tie-break by binding age (1); reversed relational tests kept in a
  learned rule's own instantiation (9); deep-copied identifiers promoted (8); a justification
  when backtracing reaches a top-state instantiation (20); duplicate checks (11; templates
  compare conditions only); RL rule values per rule, with the GQ(λ) correction (14, 15);
  template variables cleared per rule (28); sum and product over reals, set-function error
  strings, select-point over all slots (12, 13); store-new always new LTIs (S1); per-state
  smem link settings; smem --add numbering (7); base-level history bound (16); threshes as a
  list (17); spreading context counts on relinking (25); invalidation check reset (26);
  drop_tables (29); episode intervals keep their opening LTI (18); graph-match backtracking
  restores bindings (31); WMA skips removed elements (22); Petrov's d = 1 limit (23); bounded
  forgetting estimate (24).
- **Docstrings:** each changed definition says "Soar 9.6.6", describes the 9.6.5 behaviour and
  gives the defect number. Proofs were updated where definitions changed (`reteSupport_eq`
  replaces `reteSupport_nil`; `agrees_closeOwnLti`; the reorderer and memory lemmas); `lake
  build` passes with no unproved steps and only the standard axioms.
- **Regression against 9.6.6 (November 14):** 5,851 of 5,857 programs match, including the new
  set tests/kerneldefects (the bug programs that run; 7 of 7). The six that differ: five of the
  80 random SVS programs, whose result depends on heap addresses in SVS and varies between
  runs, and AlphabetAgentAllOn (two elements start with one more activation reference in the
  model; doc/DIFFERENCES.md). The programs that were address-dependent in 9.6.5 (epwma f014,
  epfuzz2 f229, the bwbook template rule) now match. With tests/svsenv (SGEL from an
  environment, 8 of 8, below) the total is 5,859 of 5,865; groups S and E were rerun with the
  new binary and gave the same results, except that 73 of the 80 random SVS programs matched
  on that run (75 in the full regression).
- **Harness:** the tools compare with 9.6.6 by default (`SOAR966`, tools/soarsel.py);
  `SOAR_VERSION=9.6.5` compares with the PyPI 9.6.5 package (doc/HARNESS.md). Fixed: a commented
  `#sp {chunk…}` in a source file was taken for a loaded rule.

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
  the Rete is also the matcher, for all rules (long-term-identifier tests included, since November 1).
- The spatial visual system (SVS, since November 14): scenes, SGEL, the scene graph in working
  memory, every command and every filter of Soar 9.6.6's tables, in substates too (Soar/SVS/).

Out of scope by decision: the explainer. Brought back into scope on October 31 and done the same
day: the memory databases on disk, and rules made from RL templates while chunking. Brought into
scope on November 14: the spatial visual system.

## Evidence

- **Proofs.** `lake build` checks 691 theorems (682 about Soar, 9 for the CMC backbone),
  with no unproved steps and only Lean's standard axioms, also in the compiled program (its
  hash-table lookup is proved equal to the matcher it stands for). Besides properties of the
  cycle and the memories:
  - the matcher is proved sound and complete for positive conditions, negations and negated
    conjunctions (inner negations to any depth, with the variables of an inner negation local to it), and the order of positive patterns is proved
    not to change the matches (Soar/MatchComplete.lean);
  - the join order returns the rule's own conditions, reordered, and exactly a permutation when
    no relational test between variables has to move; a moved test keeps its meaning between
    numbers and between identifiers, and, since Soar 9.6.6 makes ordering tests between values of
    different types false both ways, between those too (`RelOp.holds_inv_incomparable`; in 9.6.5
    it did not, kernel defect 6) (Soar/JoinOrder.lean); and, when every relational test between variables
    compares values of one kind (and the patterns have no `@` test), the positive patterns of the
    join order hold under the same bindings as the rule's own and the matcher finds the same
    instantiations (`joinOrder_posSat`, `joinOrder_matches`, `joinOrder_matches_rev`,
    Soar/JoinOrderSem.lean);
  - the join order loses no match when each condition's tests need only variables bound before it
    (`joinOrder_safe`, `joinOrder_matches'`, Soar/OrderSafe.lean), which cannot be dropped:
    `joinOrder_loses_matches` is a rule for which it does; and Soar's reorderer, a total function,
    places every positive condition exactly once (`order_perm`, `soarOrder_idx_perm`,
    Soar/ReorderProps.lean);
  - `reach` (working memory's link to a state) returns exactly the identifiers reachable from
    the roots (`mem_reach_iff`, Soar/Cycle.lean, on `mem_closure_iff`, Soar/Graph.lean);
  - from the initial state, every state has at most one selected operator after any number of
    decision cycles (Soar/Seriality.lean).

  The theorems are properties of the model; they do not prove that the model is equivalent to
  Soar.
- **Comparison with Soar 9.6.6:** see the section above. **Earlier comparison with Soar 9.6.5.** About 5,200 programs in tests/ plus the agent library, compared with
  `tools/run_all.sh` (see the README). Hand-written programs, generated programs and the Soar
  repository's own test agents match in decisions and final working memory, and where relevant
  in learned rules, learned values, memory stores and activations. Every set that is also run
  without Soar's choices replayed matches that way too. Full regression November 3 (afternoon): 5,715 of 5,718 match;
  the 3 that differ are those below (two episodic programs that differ from run to run matched
  this time).
- **Agent library** (tests/agentlib, added November 2):
  - **Contents:** every agent given for testing, 824 versions of 596 agents from 14 zips: 813
    received (deduplicated by content and numbered V1, V2, … in the order received) and 11
    corrected versions (each a new version; the received one is kept). 45 versions are Soar's
    default libraries, sourced by agents rather than run alone.
  - **CATALOG.md:** lists where each copy came from, how it runs in Soar, and a diagnosis where
    one was made.
  - **Comparison:** `GROUP=L tools/run_all.sh` compares the 747 versions that run on their own,
    at most 100 decisions each (results.txt; the 16 saved RL value tables with 5,000–68,000
    rules are in runs-big/).
  - **November 3 results (complete):** 603 of the 614 that run in both match; 133 have a load
    error in Soar itself. The earlier figure (497 of 515) was incomplete: the rule comparer
    crashed on a quoted `|\||` in kenken and took down the rest of its shard, so 147 versions
    had never been compared. The comparer is fixed.
  - **The 11 that differ, all known or not modeled:** kernel defect 28 in four RL-template
    copies; AlphabetAgentAllOn; SVS; `(cmd stop-soar)` and `:interrupt`, which stop a run in a
    way soar-lean does not model; the Bug510 chunk loop; and two that time out in soar-lean
    (ToH_Recursive, taxi-rl). graph-search-smem, whose `smem --add` numbering depends on memory
    addresses, matched in this run.
  - **What it found and fixed:**
    - model defects in chunking: identifier promotion stopping early; relational tests on an
      element with no equality test (local and superstate conditions); duplicate keys for
      empty negated tests; rules learned mid-pass not firing in the same pass, with their
      support from the p-node's earlier matches; state tests only on root state variables;
      literalization of values made by unevaluable functions; the learned rule's own
      instantiation;
    - in justifications and the goal dependency set: negated conditions on superstate
      identifiers; superstate elements reached through local elements already gone; operator
      proposals of intermediate states for results two levels up;
    - in replay: choices drawing on the random-number generator;
    - in RL templates: the letters of identifier variables, and duplicate detection in stored
      order;
    - parser gaps: trailing comments on setting lines, dashed words as function arguments,
      number lexing (`^2.<< 2 >>.h`, `2.5.`), `(state <s>)` with no attribute test, two equality
      tests in one conjunction, a failed redefinition of a rule, and five earlier ones;
    - six harness errors;
    - one new Soar crash, kernel defect 33 (bugs/chunk-computed-numeric-pref.soar);
    - soar-lean's run time grows faster than linearly in long runs (partly fixed).
- **Remaining differences** (report Section 2; doc/DIFFERENCES.md), none of them in the
  decision cycle, all from Soar's undefined or address-dependent behaviour:
  - Three episodic programs (two of them matching or not from run to run): Soar tries
    graph-match mappings in memory-address order.
  - One semantic-memory test agent (AlphabetAgentAllOn), and 9 of 30 edge-updating
    programs (generated, not in tests/): Soar reads freed or out-of-bounds memory.
  - One of the 11 Soar-book blocks-world agents (tests/bwbook, added November 2): a template
    rule's variables collide in Soar through a reused identifier address (kernel defect 28).

## CMC versions (November 14)

- **Three versions, each contained in the next.** `CMC/Base.lean` (2017), `CMC/Meta.lean`
  (metacognition) and `CMC/Emotion.lean` (the proposed emotion extension, 30 theorems).
  `CMC/MetaRefines.lean` (30 theorems) proves that every 2017 architecture, with any choice of
  the metacognitive additions, is a metacognition architecture whose runs project to 2017
  runs (`execAll_proj`, `exec_new`, `execAll_lift`); `CMC/EmotionRefines.lean` (14) proves the
  metacognition version is the emotion version with neutral emotion.
- **Decisions (Laird, November 14):** motor status goes into working memory (process data);
  declarative memory is split into semantic and episodic memories, both with buffers; a direct
  link from perception to emotion; a buffer for the assessment module; no decision on the
  emotion vector or on filtering.
- **Finding:** the 2017 model is contained in the metacognition version only if retrieval
  from semantic memory has no metadata effect; the extension's retrieval updates recency and
  frequency, which 2017 retrieval reads. Put to the coauthors as Q20 of the 22 emotion questions.
- **Checked:** `lake build` (the CMC library is a default target), no unproved steps,
  standard axioms only. The theorem count under Evidence covers Soar and the CMC backbone
  (`CMC/Proc.lean`), not these files.

## Incremental execution layer, first stage (November 14)

Profiles (callgrind) show about three quarters of the arithmetic agent's time in rebuilding
working memory, the slots, the timetag order and the identifiers linked to a state from
scratch in every working-memory phase; in agents with large match sets the model of the Rete
takes most of the rest. Caching unchanged results would save about a quarter of the working-memory
computations, so the layer keeps indexes brought up to date with each change instead (decided
November 14: the full incremental layer, staged over several sessions).
- **Mechanism:** the indexes live in `St.xi : Squash (Option WCache)`. A `Squash` has one value
  in the logic, so no theorem can tell states apart by it (`St.with_xi`) and the specification
  never reads it; the compiled program reads it only after checking (by pointer, then by value,
  `wkeyDec`) that it describes the state's own slots, which the index's proof (`WIx.Ok`)
  guarantees. Each function using it has an execution-only version proved equal to the
  specification's (`@[csimp]`), as before.
- **Stage 1:** the elements of the slots, their identifiers and their links, with
  multiplicities (Soar/WmIx.lean), updated by each synchronisation step from the elements that
  go and the new ones (`St.sync_eq_fast`, `syncPlan_perm`); working memory (`St.wm_eq_fast`)
  and garbage collection (`St.gc_eq_fast`) use it, the architecture's elements and the input
  (few, changed at every decision) being indexed when needed. `reach` is now the closure of a
  graph on identifiers (Soar/Graph.lean, `mem_closure_iff`; `mem_reach_iff` moved into
  Soar/Cycle.lean, Soar/ReachProps.lean removed), which the index computes too.
- **Effect:** arithmetic 0.82 s to 0.69 s for 40 decisions (21 percent fewer instructions), the
  eight puzzle 6 percent fewer instructions; the other benchmark agents are within noise.
  Lean ÷ Soar 9.6.6 is now about 60 to 830 (doc/bench.json).
- **Checked:** `lake build`, no unproved steps, standard axioms only; full regression
  (groups A–K): 5,857 of 5,865, the known differences only (AlphabetAgentAllOn and seven
  heap-address ties in svsfuzz).
- **Stage 2 (same day):** `St.raw` from the index (`St.raw_eq_fast`: no repeat removal when
  the elements have none); membership in working memory for the goal dependency set check,
  `addGds` and the retraction checks through `St.wmOracle`, a squashed test with its
  correctness proof, computed only when needed (`WmOracle.ask_eq`, `St.wmOracle_eq_fast`).
  Instructions against the binary before stage 1 (40 decisions): arithmetic −25 percent,
  blocks world with look-ahead −8, the eight puzzle −5, Towers of Hanoi −2, hierarchical water
  jug +4. A first attempt passed the test as a function and was slower (the compiled program
  recomputed it per element); computing it unconditionally also cost 20 percent on Hanoi.
  Making the Rete's alpha-memory and token updates use `modify` changed nothing measurable.
- **Stage 3 (same day): the slots.** `St.syncPlan` sorted every element preference memory
  requires (`St.desired`) to compare them with the slots; `St.syncPlanFast` indexes them
  unsorted and sorts only the new ones (`St.syncPlan_eq_fast`, through `filter_mergeSort`: a
  stable sort commutes with filtering, and `insW_perm`). `St.desired` is now stated through
  `dAgg`, `St.dEnt`, `St.dOthers` and `St.dProt`. Membership in the slots for the
  synchronisation plan, `St.wmPhase`, `St.pushOrder` and `St.wmaNewWmes` goes through
  `St.slotOracle`, a squashed test computed once, from the index's counts when it describes
  the slots (`St.slotMem_cnt`); a test given as a function was recomputed for every element
  (it cost 7 percent of arithmetic). Instructions against the binary before this stage (40
  decisions): arithmetic −12 percent, Towers of Hanoi −8, blocks world with look-ahead −4,
  the eight puzzle −3, hierarchical water jug −2. Lean ÷ Soar 9.6.6 is now about 70 to 800
  (doc/bench.json; the C++ times are under 5 ms, so the ratios move by tens from run to run).
  Checked: `lake build`, no unproved steps, standard axioms only; full regression (groups A–W):
  5,857 of 5,865, the known differences only.
- **Tried and dropped (same day):** a cache of the maps computed from the timetag table, kept
  with the table, saved nothing while `St.retag` made a new table on every call (stage 4
  stops that, and the cache is now kept); and a cheap hash of strings (length and four bytes),
  which made every agent 5 to 7 percent slower.
- **Stage 4 (same day): the timetag order.** Five changes, each proved equal except the third,
  which restates the specification:
  `St.retag` does nothing when the table already lists working memory in order
  (`St.retagX`, from `retag_fixed`, which moved with its lemmas from `SyncProps.lean` to
  `Cycle.lean`; most calls, after the input phase, are such); the map of the timetags is kept
  with the table it was built from (`TCache`, the state's `tx` field, installed by `St.retag`
  and `St.soarRetag`; `St.ttMap_eq_fast`); `St.letterTable` finds each identifier's oldest
  holder in one pass instead of sorting the table (the same letters when timetags are
  distinct, which they are); and `St.pushOrder` is stated through `St.pushOrderCore`, which
  asks for slot preferences only of the marked slots and applies the garbage-collection test
  only to gone elements, so `St.pushOrderFast` builds those tables only for them
  (`St.pushOrderCore_congr`, `foldl_first_get`, `find?_filter_key`, `foldr_group_getD`); and
  `St.retag` reads the old table's map (`St.ttLast`) from the cache when the table is known to
  list each element once, so the first-come and last-come maps agree (`TCache.nd`,
  `foldl_first_eq_last`, `St.retagWith_keys`, `St.soarRetag_keys`). Instructions against
  stage 3 (40 decisions): arithmetic −17 percent (5.64 G to 4.69 G), Towers of Hanoi −11,
  hierarchical water jug −10, blocks world with look-ahead −7, the eight puzzle −4.
  Lean ÷ Soar 9.6.6 is now about 65 to 660 (doc/bench.json). Checked: full regression 5,857
  of 5,865, the known differences only (with the last change added afterwards, proved equal,
  and identical on the benchmark agents).
- **Closed (Laird, November 14).** The speed work stops here: what remains would take
  arithmetic perhaps another 20 to 25 percent, still several hundred times slower than Soar,
  for a large amount of proof work. Left, with what each would take: the synchronisation plan
  (15 percent of arithmetic; keeping the slot summaries `dAgg` up to date as preferences are
  added gives about 5, but removals touch the firing and retraction code); the identifiers
  linked to a state (12 percent; reusing them between garbage collection and the
  working-memory test needs slots, preferences, goals and input unchanged in between); the
  Rete (most of the eight puzzle's time, allocation in its trees: a redesign of the Rete model
  and its proofs).
- **Earlier note, not done:** the identifiers linked to a state (`St.idsWith`, computed by both garbage
  collection and the working-memory test: about 17 percent), and the Rete (most of the eight
  puzzle's time, dominated by allocation). Each needs the specification's lists (preferences,
  timetags) mirrored by indexes updated where they change, which touches the firing and
  retraction code, with proofs.

## Speed (November 13)

Execution-only versions of the most-used functions, each proved equal to the specification's
definition and substituted by the compiler (`@[csimp]`, see CLAUDE.md), and cheaper hash
functions for symbols and elements cut every benchmark agent's time by 7 to 40 percent
(arithmetic 1.30 s to 0.85 s; Lean ÷ Soar 9.6.5 now about 40 to 900, report Appendix E).
`lake build` passes with no unproved steps and only the standard axioms; the full regression
(`tools/run_all.sh`, all groups) gives the same results as before: only the known differences
(AlphabetAgentAllOn, f014, f229) and blocks-world-operator-subgoaling-RL in bwbook/world, which
differs the same way with the previous binary.

## The spatial visual system (November 14)

Soar/SVS/ models SVS from the Soar source (SoarGroup/Soar as of October 30, 2026) and the manual's chapter 8. Soar 9.6.5 and 9.6.6 behave the same on every SVS test:
- **Geometry and numbers:** double-precision geometry, the same operations in the same order as
  Eigen and libccd. Results are bit-identical to SVS's own code, compiled as Soar compiles it.
  That was checked on 8,202 random scene queries (transforms, boxes, projections, distances,
  GJK hull distances) and 1,200 of placement, overlap, occlusion and size adjustment
  (tools/svs/). Numbers become text as C's `%g` does, exactly.
- **Scenes:** scenes and SGEL (`svs S1.scene.sgel …`), and the scene graph's mirror in working
  memory. A substate's scene is a copy of its superstate's.
- **Commands and filters:** the seven commands and `extract`/`extract_once`. All 34 filters of
  the filter table, with SVS's incremental bookkeeping of new, changed and removed values.
  Release defects are reproduced and marked SOAR 9.6.6 DEFECT:
  - `gen_new_combinations` returns early;
  - commands are re-read only when their size changes;
  - boolean parameters never compare equal;
  - `clear_output` keeps part of the state;
  - a ball's projection includes its translation.
- **Kernel hooks:** SVS's elements are architecture elements, made at state creation and in the
  input and output phases as Soar's callbacks make them. Commands are ordered by Soar's
  identifier names.
- **Proofs:** the seriality theorem is extended through SVS's callbacks. Six new theorems
  (`svsApply_arch`, `svsCall_sub` and others). The tie-breaking and chunk-naming findings
  below are not proof gaps.

Comparison with Soar 9.6.6 (and 9.6.5, which behaves the same on these):
- **Soar's own SVS test agent:** `testSVS.soar` (155 decisions, all 66 filter checks) matches.
- **Hand-written programs:** 51 hand-written programs and checkpoints match (tests/svs,
  svsgen, svsextra). They cover:
  - continuous extracts while the scene changes;
  - substates;
  - error statuses;
  - command order;
  - the reproduced defects;
  - the extra filters and `^adjust`.
- **Random agents:** 73 to 76 of 80 random agents (tools/gen_svsfuzz.py) match Soar 9.6.6,
  depending on the run, and 74 match Soar 9.6.5. Every one that differs is a tie in `closest`, `farthest`, `largest` or
  `smallest`. SVS breaks such a tie by the heap address of the parameter set (a `std::map`
  keyed by pointer); the model breaks it by the order the sets were made. Which agents differ
  depends on the heap's history: two that differ when 9.6.5 runs the set in one process match
  when run alone.

**SGEL from an environment (November 14).** An environment sends SGEL to SVS through SML
(`Agent::SendSVSInput`). The model follows Soar 9.6.6: the text is dropped when SVS is off
(`KernelSML::HandleSVSInput`); otherwise its lines are queued (`svs::add_input`, empty lines
skipped) and, at the start of the next input phase, before SVS's commands run, each line is
parsed on its own on the top state's scene (`svs::proc_input`), so an error in one line does
not stop the next; any input sets the filters' dirty bit. A substate's scene is not changed.
In the model the environment's lines are `Env.svsIn k`, the lines sent before the input phase
of decision k, passed to `St.cycleElab` (and through the CMC instance's perception step) to
`SVS.inputCb`. An input script gives them as `K svs LINE`; `tools/simenv.py` sends them to
Soar with `SendSVSInput` from the before-input-phase event, which Soar runs before SVS's input
callback, and a reactive environment (`X.env.py`) may return `svs …` lines too. New theorem:
`svsInput_off` (the input changes nothing when SVS is off); the seriality proofs cover the
input (`svsInput_sub` with the environment's lines). tests/svsenv (8 programs) matches Soar
9.6.6 and 9.6.5 on five runs in a row: objects added, moved, rescaled, rotated, tagged and
deleted by the environment; every kind of SGEL error; SVS off; a substate (whose scene keeps
its copy); the environment's input and the agent's commands in the same cycles; adding,
deleting and re-adding a name in one cycle, and groups; a reactive environment that moves a
ball to where the agent writes on its output link until SVS reports contact and the agent
halts. Two programs first differed on some runs from ties in `closest` at distance zero (the
heap-address tie above); their scenes were changed to avoid the tie.

Chunking over SVS structures matches Soar 9.6.5 (tests/svschunk). SVS elements are
architecture elements, so they are not conditions of learned rules; their values become
constants.

Found while testing: Soar 9.6.6 names learned rules differently from 9.6.5, with or without
SVS (defect 5). The model now follows 9.6.6's naming.

Not modelled: the viewer and `svs` printing commands; SML's `SVSQuery` (a query of the top
state's scene from outside the agent, which changes nothing) and `GetSVSOutput` (always empty in
Soar 9.6.6: nothing writes `svs::env_output`). `init-soar` is not modelled. The full regression with the new binary gives the same results as November 13.
The one exception, epfuzz2/f299, now differs with the November 13 binary too, so it is the
harness or Soar, not the model.

## Findings

- **Soar 9.6.5 kernel:** 33 numbered defects across nine modules.
  doc/Soar-9.6.5-Kernel-Defects.docx gives the source location, cause and a recommended
  fix for each, and the commit of Soar 9.6.6 that fixed it (all but defect 33). bugs/ has
  programs that show the main ones.
- **Soar manual:** 43 places where it is wrong, silent or ambiguous (report Section 11).
- **The CMC:** five findings (report Section 13).

## Not yet done

- **Proofs:** the chunking computation; the same preservation for negations and for Soar's
  reorderer (which in the model affects only chunking), and that `joinOrder` yields a safe order.
- **The ad hoc places** listed in report Section 10, among them justifications in the Rete
  model (probed: 300 programs, no effect), Soar's batches of working-memory changes (probed: 450
  programs; one real difference found and fixed, the order of semantic-memory results).
  Long-term-identifier tests are now evaluated in the network (done November 1).
- **The map spreadsheet** (doc/Soar-Lean-map.xlsx): every definition was reviewed line by
  line against Soar 9.6.5 (October 31 to November 1; the map's README). Updated November 14
  (tools/map_update.py, rerunnable, keeps every review): the map now follows the current
  sources and the Soar 9.6.6 source (column I locations; every cited Soar name is found); 1,029
  definitions, of which 418 added since the review (338 to review, among them 138 for SVS; 41
  execution-only and 39 proof-only, marked Not applicable), 20 reviewed ones changed for 9.6.6
  (their review notes describe 9.6.5), 14 reviewed definitions deleted since (sheet "Removed since review"); column
  T says what changed for each row. 91 rows are marked Differs: 41 name the program that
  confirmed the fix (14 linked November 14); the other 50 are unconfirmed, mostly corner cases
  (64-bit casts, NaN bits, unbounded loops), order of symbols and parser or command-line
  checks. Not yet done: review of the 338 added definitions and the 20 changed for 9.6.6;
  confirming or closing the 50 unconfirmed differences.

The plan is in doc/Soar-on-CMC-Lean-Remaining-Work.docx; a code review for simplifications and
optimizations (October 31) is in doc/Soar-on-CMC-Lean-Code-Review.docx, with the five
reviewers' reports in doc/review/. Done from the review (October 31): the speed items S1, S2,
S4–S6, S7, S8–S12, S14–S19 (hash sets and maps beside the lists, `dedupFirst`, `ttMap` with
`ttMap_getD_eq_ttOf`, the empty-list short-circuits), P1 (`Conform.cmcStep_pst` and
`runCMC_pst`: a CMC cycle of the Soar instance is `St.cycle`, via `St.cycleElab`, `St.cycleDec`
and `St.cycleApply`), the stale files (Soar/Examples.lean, Fuzz*.lean and their outputs), and
part of the dead code and docstring list. Also done (October 31; the full regression after the last change to the executable shows only the known differences): S3, S13, S20–S28 (S25 includes the `learn` accumulators and hash-based union-find); the dead parameters `Goal.rlQ`, `_deselected`, `_pre`, `isFirst`; from P2, the `foldl_rel` lemma (replacing seven fold inductions), the merged `decideImpasse` lemmas, the shared `stage2_impasse` lemma for the three impasse-cause theorems, the `St.Same` relation, and the move of the reinforcement-learning, template-rule and tie-picking lemmas from Cycle.lean to Props.lean; the merged `STest` and `eqOf` duplicates; two docstring fixes. Later the same day: the remaining fold inductions in SMemProps and EpMemProps now use `foldl_rel`; `Pat.binds` is merged into `Pat.eqVars`; `symRank` is an array and `Rete.names` a hash set; `keepEdges` is linear (a hash map of the new rows) instead of removed through `calcSpread_content`, which is not proved; `curMatches_off` and `matchConds_neg_eq_ncc` are proved; docstrings in SMem, Chunk and EpMem fixed; `NegTree.holds` is structural (mutual with `NegTree.noneHold`) instead of `partial`; with it, matcher completeness is proved for negated conjunctions nested to any depth (`tree_complete`, `tree_clear`). Then `rlUpdate_frame` (one lemma for what a reinforcement-learning update leaves alone) and `fireMatch_eq_fireOneBase`; the P3 equalities `deepCopy_eq`, `dedupFirst_eq`, `cycSub_eq` and `ttMap_getD_eq_ttOf` already existed. The code review is closed (November 1): every item is done or closed with its reason in doc/Soar-on-CMC-Lean-Code-Review.docx (Closure). Also then: `sync_idem` (SyncProps), `reteSupport_nil` (SupportProps), `calcSpread` proved through its stages (`calcSpread_keeps`; `keepEdges` removed), the reinforcement-learning tables merged into `rlTab`, `upd` once in CMC/Util.lean, strength notes on `quiescence_ie/pe` and `cycle_independent_of_decl`. Also: `mem_reach_iff` and the preservation of matches by the join order (`joinOrder_matches`) are proved. Developer notes: CLAUDE.md,
doc/HARNESS.md (versions and run times) and doc/DIFFERENCES.md (diagnoses).
