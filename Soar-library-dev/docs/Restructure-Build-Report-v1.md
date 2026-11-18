# Restructured libraries v2.5: build report

Supersedes v0. Built from the thor-soar.vsa.zip baseline with `build.py` (restructure-tools v2.5). Rebuild takes seconds: edit `manifest_spec.py` or `patches.py` and run `python3 build.py OUT`.

## Layout
`soar-library.soar` loads soar-base, selection-world, agent-world, object-world. `thor.soar` loads thor-soar and thor-tasks (kept apart because its settings turn on epmem/svs/rl).
- selection-world is one project (core, iterative-deepening, optimal, first-success under `strategies/`).
- Each project has `<p>.soar`, `<p>/<p>_source.soar` loaders, `<p>.vsa.json` (format version 6, opens in Visual Soar), and `<p>/_readme.soar`. Files starting with `_` list first in loaders and layouts. Notes files with no active rules are in `<p>/docs/`.
- Rules: 1,337 originally, 1,333 now (4 shadowed duplicates and the attend-all rule removed, one rule added by P-004). 1,323 are reachable from the loaders (selection-optimal is off).

## Content patches (patches.py, listed in PATCHES.txt)
- P-001: `agent-world*elaborate*desired-count3*achieved-3` tested an unbound variable and reported success with two of three desireds achieved.
- P-002 and P-003: the `attend-all` flag removed (initialization line in Thor; its only rule and file in object-world).
- P-004: look-ahead world copies also copy relations the task declares with `^copy-relation` on its problem space (new rule `evaluate-operator*elaborate*default-state-copy-relation*declared`; on, above, in unchanged).
- P-006: `^problem-space.agent-world` deprecated. The 31 rules that tested it (agent-world 15, object-world 10, Thor 6) no longer do, and Thor no longer sets it. Done as a text substitution in the build (patches.py `TEXT_SUBS`). Generated tasks no longer set it; only WME counts changed in the tests.
- P-005: look-ahead desireds copy any relation-shaped value, not only on/in/controlled-by/above.

## Datamaps
One merged graph (`datamaps/library-datamap.json`); each edge is owned by the lowest-layer project whose rules mention the attribute, so projects share structure instead of copying it. Trimmed in the per-project files: 151 edges whose attribute no rule in any project mentions (list in `datamap-trimmed.txt`; io, self, scene, smem, epmem, svs, reward-link are never trimmed; `TRIM=0` keeps everything). The type conflicts between projects are resolved: 34 by rule and the identifier-versus-constant cases by decision (JEL, 13 Nov 2026); `datamap-conflicts.txt` lists both groups, and no entry remains open. Opened successfully in Visual Soar; not otherwise validated.

## Verification
- `verify.py`: every old rule appears with the same body apart from `:default`, whitespace and patches; no duplicate names among sourced files; every file sourced except optimal (off).
- Library plus Thor (Thor `_firstload` blanked in both trees) loads to the same production count in old and new trees.
- Test set v1.6: 177 tests, all pass. Fifteen original tests load the library (behavior identical to the old tree, user-rule counts re-baselined). The rest are generated tasks on the new conventions (Counting, Water Jug, Arithmetic, Blocks World, Hanoi, Eight Puzzle, flat and static, 3 seeds each) plus the P-001 regression.

## Differences you should know about
1. `:default` added to 821 rules (512 already had it), all projects.
2. Load order is soar-base first; architecture settings load before the selection rules.
3. `thor-soar/_firstload.soar` is unchanged; it still sources `../../agent/thor-soar-semantic-memory.soar`, not in the zip.
4. Soar silently ignores duplicate-body rules (e.g. simple's top-state elaboration vs agent-world's); the duplicates should be removed in a content step.
5. 9 `external-operator-application` rules with Thor vocabulary stayed in agent-world (the wizards tests need them); 28 other vocabulary rules moved to `thor-soar/from-agent-world/`, untested. The 148 Thor scene/anchor/smem/svs candidates stay in thor-soar by decision.
6. Strategy choice is by editing `strategies_source.soar`; events by commenting the events line in `agent-world_source.soar`.

## Library findings from testing
- Look-ahead copied relations by fixed name list (world and desired); other names were silently invisible. Addressed by P-004/P-005 (declaration on the problem space for world relations).
- At most 6 desireds; iterative deepening capped at depth 7 (3-disc Hanoi does not finish).
- Counting and copying rules for more than 5 or 6 desireds are enumerated by hand in agent-world.

## Not done
Section 6 decisions, hooks and flag files, removing duplicate-body rules, Thor achievement rules and generic-looking Thor rules, the 118 datamap type conflicts, GitHub commit.

## Additions: P-006 and P-007

- P-006: `^agent-world true` removed from all problem spaces and rules (text substitution in the build).
- P-007: flag files and the `^flag-override` mechanism (15 added rules in total with P-004). Thor `flags-initialization` converted to `^flag-override`.
- Verification: 177 tests, 0 failures. Relative to v1.6 decisions, halted, operator-trace hash, output hash and user-rule-name hashes are identical in all tests; only elab_cycles, firings and wme_changes changed (155 counts), because the new default and override rules fire.

## Addition: P-008 cleanup

- 490 library rules renamed to `<project>*<phase>*<topic>`: elaborate 220, propose 50, compare 88, apply 132. Mapping in `rule-renames.csv`.
- verify.py (rename-aware): 1337 old active rules, 1347 new; the 5 lost are the 4 shadowed rules plus attend-all; 15 gained, all expected (P-004, P-007). No duplicate names among the loaded rules.
- 177 tests, 0 failures with no change to any fingerprint, including firings and WME changes. The renaming and regrouping therefore changed no behavior.

## Addition: P-009 (look-ahead-planning retired)

- Removed the flag from the Thor initialization and deleted the one rule that tested it false. Generators and test programs no longer set it.
- 1337 old active rules, 1346 new; the 6 lost are the 4 shadowed rules, attend-all and the Thor random-selection rule. 177 tests: decisions, elaboration cycles, trace and output hashes unchanged; firings and WME changes re-baselined (one flag WME fewer).

## Addition: P-010 (forget-unattended retired)

- Deleted object-world/remove-object.soar (5 rules) and the Thor proposal rule; removed the Thor flag line and the object-world `_flags` file. 1337 old active rules, 1339 new. 177 tests: decisions, elaboration cycles, trace and output hashes unchanged; firings and WME changes re-baselined (the default rule no longer fires).

## Addition: P-011 (duplicate-body rules)

- Loading the library in Soar 9.6.6 reports duplicate-body rules as "Ignoring X because it is a duplicate of Y". Library alone: 1 (agent-world elaborate*substate*top-state, a duplicate of soar-base elaborate*state*top-state). Library plus Thor, with the semantic-memory source stubbed: 1 more (Thor elaborations*elaborate*state*mobile*true2, a duplicate of true1). Both were already inactive; both are deleted.
- After deletion the library loads 473 productions with none ignored, and library plus Thor loads 854 Thor productions with none ignored. 177 tests: every fingerprint unchanged. check_load.py in the tools reruns this check (Python SML needed).
- Duplicate detection by Soar is structural, so no textual-duplicate scan is needed beyond this load log.

## Addition: datamap type conflicts

- The old datamaps disagreed on the type of 62 distinct attributes (118 occurrences). Resolution rules in the build: STRING with ENUMERATION gives STRING; INTEGER with FLOAT gives FLOAT; two other constant types give STRING; SOAR_ID with a constant type gives SOAR_ID when the identifier side has children (a vertex has one type). 34 attributes are resolved by rule. 28 are identifier-versus-constant and listed for review in datamaps/datamap-conflicts.txt; 2 more kept the first definition because the identifier side has no children.
- Structural check of the merged datamap: 1,323 vertices, every edge target exists, no constant-typed vertex has edges, no enumeration without choices. The six project files are format version 6. Visual Soar was not run on this build.

## Addition: datamap conflict decisions (JEL, 13 Nov 2026)
All identifier-versus-constant conflicts are decided. Types: abstract-property STRING; achieved, argument1-4, task, duplicate-of, future-event SOAR_ID; attend STRING; instance-of STRING; disjunction SOAR_ID (the desireds.desired structure); holding-object SOAR_ID (world.objects.object); mobile and visible ENUMERATION {false, true}; time (io.input-link) SOAR_ID with INTEGER child ms. Two-entry attributes (a SOAR_ID plus an ENUMERATION {nil}): next, superstate, top-segment. Dropped: scene-copy, last-operator. Check on the final build: 1,327 vertices, 0 structural problems, 177 tests pass, verify.py old 1,337 / new 1,337, no duplicate rule names among loaded rules.
