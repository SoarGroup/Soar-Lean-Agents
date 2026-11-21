# Resume: Soar-Lean-Agents (updated 18 Nov 2026)

## Status (18 Nov 2026): conventions and generators

- **Conventions reorganized.** Soar-Conventions.xlsx and World-Conventions-v6.xlsx were reviewed (the L3 rows: shared, moved to the world conventions, or Soar-only as L3S), checked against the manual for L0-L2 (rows added), sorted by level and then by topic in development order, and renumbered with level-based IDs numbered jointly across both workbooks (L0-001 ...; L3S Soar-only guidance; L5 Selection space (classic); L6P project conventions; L20 Thor). Old IDs map through `Conventions/id-renumbering-map-2026-11-18.csv` (and, for IDs from before 17 Nov, `id-renumbering-map.csv` first). The reference specifications are now generated from the workbooks (`gen_spec.py`: `World-Conventions-Spec-v7.md`, `Soar-Conventions-Spec.md`). Loose documents in the repository cite the new IDs; references inside zips were not updated (decided).
- **Convention decisions of 18 Nov:** L3-005 every rule tests its state's or problem space's name (exceptions: rules that create the name or problem space); L3-007 environment-effect rules may keep `:o-support` (better as part of the operator application); L3-012 one English comment per rule group; L3-039 `+ =` is acceptable when order does not matter (to be revisited), RL variants drop it (L3-083); L3-040 one rule may propose a fixed set of operators that differ only in a constant. W-DES-017 removed; SVS out of scope.
- **Generators updated:** worldgen v22 (`Soar-library-dev/tools/worldgen-v22.zip`; v21 shipped an earlier `convpass.py`), `SoarLean/soarlean-agentgen-2026-11-18b.zip` (revision b: path A writes the same group comments as path B) and `Tasks/Families/families-v6-tools.zip` share a final pass, `convpass.py`, that applies L3-005, L3-012 and L3-083; the Lean World and WorldSpec compilers write the problem-space tests themselves, and the Agent compiler records the last operator (name and parameters) in one rule that replaces the previous record (L3-021, L4-005).
- **Test set v1.37** (515 tests, library v2.42 unchanged): the 109 generated programs regenerated; decisions, traces and output identical in all 198 generated tests; 197 baselines re-recorded (elaboration cycles, firings, WME changes). v1.36 (17 Nov) fixed the worldgen duplicate-proposal bug.
- **Families world-v6** regenerated: every result unchanged; decisions changed in blocks-world-hrl (431 to 1,134, RL proposals without `+ =`), hrl-3level, water-jug-hierarchy and -hierarchy-chunk. `Tasks/Families/README-v6.md`, `Families-Results-v6.xlsx`.

- **English-to-Soar agents regenerated** (`Tasks/From-English`: the 4 world agents, the 27 Rosie agents and the Lean path A and B agents of 3 of them): on library v2.42, seeds 1-3, all 111 runs give the same outcome, decisions and actions as before (`Tasks/From-English/README.md`). The Lean path A Tower of Hanoi does solve on v2.42 (7 moves, 35,393 to 46,451 decisions); the earlier report that it does not came from a 20,000-decision cap. artists-world (2 pairs) does not solve within 60,000 decisions on v2.42, before or after (it solved on v2.30).

## Open (18 Nov 2026)

1. Convention IDs in the generator sources, agentgen checker messages and generated rule comments are still the old IDs (map: `id-renumbering-map-2026-11-18.csv`).
2. Library: halt only through an operator application (goal-completed) instead of the interrupt (to-do row 24).
3. Test set: 36 failures among the original-soar controls and artists world tests against the v1.35 baselines (to-do row 13).
4. Review the L6P rows of Soar-Conventions for moving to World-Conventions.
5. blocks-world-epmem (world-v6): how a task supplies a retrieved action model in look-ahead (specification silent).
6. The families soar-conv agents were not rechecked against the 18 Nov wording of L3-005.

## Status (17 Nov 2026): library

- **Library v2.42** is installed in `Soar/soar-library` (release zip in `Soar-library-dev/releases`).
  v2.42 removes `selection-world*compare*selection*lower-bound-better-than-success`: in nested selections it preferred depth-exceeded branches over a success, which kept cost graph r4x8 from ever taking the goal edge under tie-impasse (lower bounds already pass up from every nested evaluation, so the cost guarantee does not need it). v2.41 corrects comments only (readme rule counts; the agent-world doc no longer asks for `^agent-world true`). v2.40: `^optimize true` guarantees the cheapest plan under operator depth as well as tie-impasse (bound checking, `^better` copied to look-ahead desireds); all-evaluations-failed up to 10 items. v2.39: failed operators are rejected; a lost top state does not halt with success (Rosie findings). v2.38 removes the verify and guardrails flags and the force-conflict mechanism (25 rules; history in `Soar-library-dev/docs/History-verify-guardrails-force-conflict.md`); the unachieved-desireds starting depth stays at the count. v2.37 adopts three search changes from the selection-world review: `^iterative-step cost` now defaults `^cost-metric unit`; the loser of an evaluation comparison is marked `^closed`; `^max-evaluation-depth` is a flag (default 12). v2.36 makes four corrections from the selection-world review (no behaviour change); v2.35 changed only datamaps (`^duplicate-of` is an identifier); v2.34 had no rule change from v2.33. Defaults: `^iterative-step operator`, `^cost-metric none`,
  `^optimize false`. Search gains come from per-task `^flag-override`, chosen by measurement with
  `probe_settings.py` (`Soar-library-dev/docs/Search-Settings-Intake-Checklist-v1.md`).
- Tasks that set `^iterative-step tie-impasse`: generated Blocks World (test set), mc
  (`Tasks/From-English/mc-world` and test set), and in `Tasks/Families`: blocks-world-look-ahead,
  kenken-4-5, kenken-6-1, 6-2, 6-3. water-jug-look-ahead keeps operator depth
  (`Soar-library-dev/findings/FINDING-tie-impasse-unbounded-continuation.md`).
- **Test set v1.35** (515 tests) holds the v2.42 baselines (v1.35: 20 tests re-baselined, all plans unchanged, r4x8 tie-impasse now solves with the optimal plan, cap 10,000; recorded with PyPI soar-sml 9.6.5; v1.34 corrects the README only; v1.33: 28 cost-graph tests change under optimize with operator depth, all still solve, no plan worse; v1.32 added 6 tests of `init-evaluation-depth unachieved-desireds`). v1.29 added 174 tests of the world-convention
  step 6 task families (58 variants, seeds 1-3); v1.30 added 39 tests of tie-impasse search with a cost
  metric. Known regression: artists-3 (all three
  seeds) does not solve within 20,000 decisions.
- **Tools:** worldgen v19; `SoarLean/soarlean-agentgen-2026-11-16b.zip` (agentgen with the
  `vsproject.py` settings option, the v18 `wg.py`, WorldSpec and rosiegen; reserved operator names in
  `World/Check.lean` match the library); `SoarLean/install-lean-sandbox.sh`; option tools in
  `Soar-library-dev/tools/option-selection/` updated for v2.37 to v2.41.
- **Consistency check (16 Nov 2026, evening):** the library, test set, conventions (specification v6,
  workbook v6, VisualSoar project conventions), SoarLean, the manual (draft v2), the option-selection
  guide (v1.2), the intake checklist and these top-level files were brought into line with v2.41.
  Not done: loading the generated agents in Soar 9.6.6 with v2.41, and rechecking measurements made on
  earlier library versions (marked as such in the documents).

## Open (library)

1. Chunking in look-ahead is off for now; the over-generality problem and candidate solutions are in
   `FINDING-chunking-overgeneral.md`. A better solution is still needed.
2. Build the search-settings intake (checklist and `probe_settings.py`) into agentgen.
3. Kenken world variants: the cause of the failures under operator depth is not diagnosed
   (`Tasks/Families/README.md`).
4. Clean up the repository's `Soar` directory; ACT-R and Sigma cleanup deferred.


---- Earlier status (10 Nov 2026), kept as written ----

## Status (10 Nov 2026)

Work since the defect review (9 Nov), all delivered in this folder:

- **Blind round trip, 68 tasks** (Soar -> English -> Soar, standard and world conventions), plus
  direct conversions of the original Soar code to both conventions: STEP6/Blind-Round-Trip-68.xlsx,
  STEP6/blind-round-trip-68.zip. Summary (original / standard / world / world-no-environment /
  direct-standard / direct-world): episode-1 successes 168/167/170/171/168/170; median decisions
  102/114/272/102/126/102. Task-rule counts exclude blocks-world-hrl-3level.
- **Artists-and-managers** in the world framework (artists-world.zip) with iterative deepening;
  `^iterative-step operator` mode was rerun. It does not return shortest plans (open).
- **Five-houses (zebra) puzzle** encoded under the world conventions (zebra-world.zip).
- **Library findings:** Library-Findings.docx, 47 findings (17 high, 20 medium, 10 low), by
  component. The Library findings sheet in Blind-Round-Trip-68.xlsx holds only the first 9 added;
  the zebra findings are in the document and the zebra README only.
- **Conventions:** VisualSoar-Project-Conventions.docx (37 conventions for representing Soar agents
  on the VisualSoar project structure). World conventions: World-Conventions.xlsx, Slides/.
- **Deck:** Slides/From-English-to-Soar-CIC.pptx (37 slides, with page numbers), plus the single-topic
  slide files in Slides/.

## Next steps (from the Next steps slide)

1. Address the 17 high-priority library findings, starting with the selection-world attribute
   copying and the iterative-deepening guard (once per operator, not once per state).
2. Retest Blocks World optimality with the fixed libraries (carried over from 9 Nov).
3. Add the remaining findings to the spreadsheet's Library findings sheet.
4. Ratify one convention set (world conventions plus the VisualSoar project conventions).
5. Test the pipeline on tasks that were not written for it.

---- Earlier status, kept as written ----

## Resume: world-conventions defect review (stopped 8 Nov 2026, 21:00)

Defects are taken in order of severity, high first. JL edits the original library rules; Claude
re-checks them in Soar and soar-lean.

## Status (9 Nov 2026, 16:05): defect review complete

Every defect now has a decision in the "Review (8-9 Nov 2026)" column of the Defects sheet in
World-Conventions.xlsx. (That column was added after build_world.py ran; rerunning the build
script would drop it.)

- Fixed by JL (35, incl. D-019, D-030, D-068), D-010 count-6 rules, D-043/D-053 covered by other fixes.
- Moot: base selection dropped (D-003, D-004, D-034-037, D-073, D-074).
- On hold: D-012/D-017 generic achievement rules (fixes/d012v2/); retest Blocks World optimality now
  that the look-ahead defects are fixed, before deciding.
- Deferred: D-013/D-055 (operator next-desireds), D-032 group (Thor names out of agent-world:
  D-032, D-057, D-058, D-061-063, D-070; markers ^custom-output, ^grounding-operator, ^no-verify).
- Documentation corrections: D-015, D-016, D-018 (fixes/doc-errata-D015-D016-D018.md); still to add:
  D-049 (task copies scene relations), D-054, D-056, D-085 (^world.estimated-total-time optional).
- Saved for future, skipped now: D-060, D-067, D-072, D-075, D-078-081, D-084, D-085, D-087, D-089,
  D-094, D-095 (suggestions in the 16:01 discussion; D-089 one test, narrow L9-001/L9-014 to task rules).
- Kept for possible future use: D-064, D-077, D-082, D-083. Skipped: D-065, D-088, D-091, naming/:default items.

## Next steps
1. Get JL's updated libraries (agent-world, selection-world, selection-iterative-deepening) and rerun:
   Blocks World (id, indiff, sw), WM/rule checks, soar-lean comparison.
2. Build Soar 9.6.50 (has `$`) from SoarGroup source; add `$` to soar-lean.
3. Update the workbook: conventions changed by the fixes (no-value, ^dont-copy-object-attribute,
   ^copied-from, ^internal-actions on every state, reserved operator attributes, top-state
   ^quiescence t, ^action-handle only), base-selection rows out of scope, Lean checks to match.

## Open side issue

selection-world loaded without iterative deepening does not run: the evaluate-operator substate
gets no operators and falls into a state no-change. Iterative deepening currently provides what
it lacks.

## Where things are

- Workbook: /home/claude/wc/World-Conventions.xlsx, built by /home/claude/wc/build/build_world.py
- Lean: /home/claude/src/agentgen/World/ (Types, Check, RulePred, Compile, Tasks/BlocksWorld).
  The generator no longer loads base selection.
- Generated Blocks World: /home/claude/wc/gen2/{id,indiff,sw}; run with
  `python3 /home/claude/wc/runworld.py <dir> 400`
- Libraries as uploaded: /home/claude/wc/in/dw/default-world (read-only copy). Test copy with
  the D-005 fix: /tmp/libfix
- Package sent: world-conventions-2026-11-08.zip

## To restart

Say "continue the defect review". Claude starts with D-005 (your decision) and then D-006. Upload
the edited library folder when convenient so that D-001 and D-002 can be re-checked.
