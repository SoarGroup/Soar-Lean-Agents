# Resume: Soar-Lean-Agents (updated 10 Nov 2026)

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
  D-094, D-095 (suggestions in the 16:01 discussion; D-089 one test, narrow W-TOP-001/021 to task rules).
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
