# Resume: world-conventions defect review (stopped 8 Nov 2026, 21:00)

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
