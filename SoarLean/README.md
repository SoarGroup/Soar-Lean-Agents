# SoarLean: agentgen, the World library, worldcheck, rosiegen and familygen (release of 24 November 2026)

## Release of 24 November 2026 (`SoarLean-2026-11-24-release.zip`, for library v2.47)

Joins `SoarLean-2026-11-23-release.zip` with the changes since:
- WorldSpec phases and loops (World-Conventions L8-026 to L8-030): `Phase` and the `Task` fields `phases`, `loopStart`,
  `termination`, `repeatCount` (`WorldSpec/Types.lean`); `Compile.lean` (path A) and `worldgen/spec_backend.py` (path B)
  write the ^next-desireds chain, ^loop-start, ^termination-desireds and ^repeat-count; `Json.lean` and
  `worldgen/worldspec_py.py` carry them. New tasks `WorldSpec/Tasks/GuardTour.lean` and `GuardPatrol.lean`
  (Tasks/webtasks/classic-ai). The Lean semantics (check, explore, replay) test only `goal`.
- Declared output form (L10-018): `WorldSpec.OutputForm`, `Task.output`; `worldgen/wg.py` `Task.output` / `WG_OUTPUT`;
  `world_backend.py` reads an `output` field.
- `worldgen/wg.py`: phases and loops (`Task.phases`, `loop_start`, `termination`, `repeat_count`) and `Task.flags_comment`.
  Byte-identical with `Tasks/From-English/rosie-teaching/tools/wg.py` and with Soar-library-dev `tools/worldgen-v23.zip`.
- KenKen family and Cheryl's birthday / muddy children: monotonic operators (L15-027), as committed on 23 November.

Checked 24 November 2026 (Lean 4.35.0, `cmcsoar-release-2026-11-14` beside `agentgen`):
- `lake build agentgen worldcheck rosiegen familygen`: 136 jobs, warnings only; every `wellFormed` theorem proved.
- `familygen` writes the 67 family variants identically to `Tasks/Families/families-world-lean-2026-11-23.zip`.
- Water Jug: `agentgen water-jug-desc`, `world_backend.py`: 33 rules; `check_derived.py` passes; `worldcheck --task`: 0 violations.
- Classic AI (9 tasks): `rosiegen json` equals the Python JSON; paths A and B write the same rules apart from the header
  (bridge-and-torch also differs by one comment line, as before); path B reproduces every stored rules file.
  `rosiegen replay` accepts every stored run.
- Rosie Lean paths (Tower of Hanoi, fox-goose-bean, KenKen): `rosiegen compile` and `spec_backend.py` reproduce the stored
  agents; JSON unchanged.
- Every Python generator reproduces its stored outputs: 51 Rosie gen.py (with their search-control variants), the
  worldgen gen_*.py tasks (flat and static), the five English world agents.

## Release of 23 November 2026 (`SoarLean-2026-11-23-release.zip`, for library v2.46)

Joins `SoarLean-2026-11-21b-release.zip` (which already holds `SoarLean-family-2026-11-21.zip`: its `tools/` files are in
`agentgen/tools/`, its lakefile lines in `agentgen/lakefile.lean`) with the changes since:
- `agentgen/Family/Families/TowersOfHanoi.lean`: 3 disks (original and world versions; JL, 22 Nov 2026).
- `agentgen/Family/Families/Knights.lean`: an enumeration task; the run stops after 100 closed tours or 30,000 moves
  (knight moves and backups), or when the search is exhausted (JL, 22 Nov 2026).
- WorldSpec learning setting (World-Conventions L5-021; library v2.46 learns from look-ahead by default with chunk only):
  `Task.learning` (default true) and `Task.learningReason` in `WorldSpec/Types.lean`; `Compile.lean` (path A) and
  `worldgen/spec_backend.py` (path B) append `chunk never` with the reason when it is false; `Json.lean` exports it.
  `worldgen/worldspec_py.py` sets it from a line 'Learning: do not learn from look-ahead. <reason>' in the task's
  `english-input.txt`, and writes it into the Lean description. `WorldSpec/Tasks/CherylsBirthday.lean` and
  `MuddyChildren.lean` now carry `learning := false` (their English statements say so: with learning on they do not finish).

Checked 23 November 2026 (Lean 4.35.0, `cmcsoar-release-2026-11-14` beside `agentgen`):
- `lake build agentgen worldcheck rosiegen familygen`: 132 jobs, warnings only; every `wellFormed` theorem proved.
- `familygen` writes the 67 family variants identically to `Tasks/Families/*/world-lean` (families-world-lean-2026-11-22).
- Water Jug: `agentgen water-jug-desc`, `world_backend.py`: 33 rules; `check_derived.py` passes; `worldcheck --task`: 0 violations.
- Classic AI (7 tasks): `rosiegen json` equals the Python JSON; paths A and B write the same rules apart from the header
  (bridge-and-torch also differs by one comment line, as before); the stored rules are reproduced, with the four-line
  learning block added for cheryls-birthday and muddy-children. `rosiegen check` agrees on every example state;
  `rosiegen replay` accepts every stored run.
- Rosie Lean paths (Tower of Hanoi, fox-goose-bean, KenKen): `rosiegen compile` and `spec_backend.py` reproduce the stored
  agents; JSON unchanged.


## Revision b of the release, 21 November 2026 (`SoarLean-2026-11-21b-release.zip`)

The release of 21 November was built from the 18 November line (`soarlean-agentgen-2026-11-18b.zip`), which
branched before the WorldSpec work for the classic-AI web tasks (`soarlean-agentgen-2026-11-16-classicai.zip`,
`-extensions.zip`, `-knowledge.zip`). Those additions were missing from it, so `spec_backend.py` could not regenerate
bridge-and-torch, Cheryl's birthday or muddy children. Revision b merges them (three-way merge, base the package each
line branched from):

- WorldSpec: `plus` right sides, `update` and `each` effects, `stepCost`, `repeatControl`, `derived` relations
  (Types, Sem, Json, Check, Compile, Proofs); `Var.badName` refuses reserved variable names.
- `WorldSpec/Tasks/`: MonkeyBananas, VacuumWorld, TowerOfLondon, InstantInsanity, BridgeAndTorch, CherylsBirthday,
  MuddyChildren; their `wellFormed` theorems are proved by `decide`; `rosiegen` knows all ten tasks.
- `worldgen/spec_backend.py`: the same extensions, with the 18 November convention pass (`convpass.apply`) kept
  last; `worldgen/worldspec_py.py` added (the Python port, also in `Tasks/webtasks/tools`).
- `WorldSpec/Compile.lean` (path A): the `each` apply rules and the derived-relation rules now test
  `^problem-space.name` (World-Conventions L3-005), as path B does through `convpass.py`. Without this, paths A and B
  differed on Cheryl's birthday and muddy children.
- `World/Check.lean`, `World/Compile.lean` keep their 16 November (revision b) versions.
- `worldgen/spec_backend.py` now refuses description variables whose names the back ends reserve or generate
  (`s`, `w`, `objs`, `ds`, `op`, `pre`, `pa`, `task`, `any-unachieved`, `dr`, any name with `-`, `r<digits>`,
  `e<digits>`), the same check as `Var.badName` in `WorldSpec/Check.lean`, so path B no longer writes broken
  rules silently (the Tower of London `<s>` finding of 16 November).
- `rosiegen replay` drops the `null`s that `run_agent.py --json` writes for a missing argument, so runs of
  one-argument actions replay without editing (the fix proposed on 16 November).

Checked 21 November 2026 (Lean 4.35.0): `lake build rosiegen familygen` succeeds; for the seven classic-AI tasks
`rosiegen json` equals the Python JSON and paths A and B write identical rules (apart from the header);
`rosiegen check` agrees with Soar on all 22 example states; `rosiegen replay` accepts every run as written by
`run_agent.py`; `spec_backend.py` writes the same rules as before for all ten WorldSpec tasks and refuses a description
with a variable named `s`.
Full build checked 21 November 2026 with `cmcsoar-release-2026-11-14` beside `agentgen` (Linux, Lean 4.35.0):
`lake build agentgen worldcheck rosiegen familygen` completes (132 jobs, warnings only). The Water Jug commands under
Use give 33 rules, `check_derived.py` passes and `worldcheck --task` reports 0 violations, as on 16 November;
`familygen` writes the 67 family variants identically to the build used for the release check. Unchanged outputs:
`rosiegen compile` on Tower of Hanoi, fox-goose-bean and KenKen (every world file), and `spec_backend.py` on their
JSON, give the same rules as the release.

## Release of 21 November 2026 (`SoarLean-2026-11-21-release.zip`)

One package for every Lean and Python generator of the English-to-Soar pipeline, for library v2.45 and the conventions of
21 November 2026 (World-Conventions-v6.xlsx, World-Conventions-Spec-v8.md; Soar-Conventions.xlsx, Soar-Conventions-Spec.md).
It joins `soarlean-agentgen-2026-11-18b.zip` (Agent, World, WorldSpec, worldgen) and `SoarLean-family-2026-11-21.zip`
(Family, familygen), which had separate lakefiles: the agentgen lakefile now declares all four libraries and all four
executables (`agentgen`, `worldcheck`, `rosiegen`, `familygen`).

- `agentgen/Family/` (new here): the 14 task families as typed Lean descriptions; `lake build familygen`, then
  `familygen OUT` writes `OUT/<family>/world-lean/<variant>/` (67 variants). README: `agentgen/Family/README.md`.
  Since 19 November: blocks-world state evaluation tests where every block is (`allOnConds`, World-Conventions L3-103).
- `agentgen/tools/`: `vsproject.py`, `convpass.py` as before; `soar2lean.py`, `v6tolean.py`, `compare.py` (family migration tools).
- Unchanged since 18 November: Agent, World, WorldSpec, worldgen (`wg.py`, `convpass.py`, `world_backend.py`,
  `spec_backend.py`, `check_derived.py`).

Checked 21 November 2026 (Lean 4.35.0, library v2.45, Soar 9.6.6 / PyPI bindings):
- `familygen` reproduces the 67 world-lean family agents in `Tasks/Families/*/world-lean` byte for byte.
- `rosiegen compile` (path A) and `spec_backend.py` (path B) reproduce the Lean-path agents of Tower of Hanoi,
  fox-goose-bean and KenKen in `Tasks/From-English/rosie-teaching` (apart from the header line).
- The shared Rosie generators (`tools/wg.py` = `worldgen/wg.py`, `convpass.py`) and the four English world agents'
  `gen.py` reproduce every checked agent file unchanged.
- `agentgen` and `worldcheck` were not built for the release itself; revision b builds them (see above).
- Known: convention IDs cited in the Lean sources and in checker messages are partly pre-renumbering IDs;
  `Conventions/id-renumbering-map-2026-11-18.csv` maps them. The ID history has two renumberings, so an automatic
  rewrite is ambiguous for a few IDs and was not done.

## Earlier history

One Lean package that holds the Lean tools of the English-to-Soar pipeline, plus the Python
back end that writes world-convention rules. It replaces `agentgen-bundle.zip` and
`agentgen-world.zip`, which did not build separately.

## Contents

- `agentgen/` (Lean package)
  - `Agent/`, `Agent.lean`: the task-design language (DSL), compiler, English renderer and
    semantics; the Water Jug family (`Families/WaterJug.lean`) and its round-trip proofs.
  - `AgentGen.lean`: the `agentgen` executable.
  - `World/`, `World.lean`: world-convention task descriptions, the convention check
    (`Conventional`, proved for Blocks World in `World/Tasks/BlocksWorld.lean`), rule predicates,
    and an older compiler from descriptions to rules (`World/Compile.lean`; superseded by `WorldSpec/Compile.lean`,
    not built; see Revision b of 16 November below).
  - `WorldCheck.lean`: the `worldcheck` executable.
  - `tools/vsproject.py`: writes Visual Soar projects.
- `worldgen/` (Python): `world_backend.py` (Lean description to world-convention rules),
  `check_derived.py` (derived attributes are declared not to be copied), `wg.py` (shared generator).
  Declared output form (24 Nov 2026, World-Conventions L10-018): `wg.Task.output` (or the environment variable
  `WG_OUTPUT`, JSON with WorldSpec's OutputForm fields: command, nameAttribute, arguments, done, success, error,
  applied; `"command": null` = the command is the action handle) rewrites the environment-effect rules to read that
  command and adds `<task>*elaborate*environment-output-map`; `world_backend.py` takes it from an `output` field of
  the description. Without it every generator writes exactly what it wrote before (all worldgen gen_*.py tasks and
  world_backend water-jug variants compared byte for byte). Checked: water-jug (gen_waterjug.py) and
  water-jug-look-ahead (world_backend.py) with `do ^action ^object ^target` and with the action-handle form give the
  same actions at the same decisions as the default, seeds 1-3. The Rosie generators share `wg.py`.
  Phases and loops (24 Nov 2026, World-Conventions L8-026 to L8-030, library v2.47): `wg.Task.phases` (ordered
  list of named goal conditions), `loop_start`, `termination` and `repeat_count` write a ^next-desireds chain,
  ^loop-start, ^termination-desireds and ^repeat-count. WorldSpec has the same fields (`phases`, `loopStart`,
  `termination`, `repeatCount` in `agentgen/WorldSpec/Types.lean`; `Compile.lean` and `spec_backend.py` write the same
  rules, checked by the new tasks guard-tour and guard-patrol in Tasks/webtasks/classic-ai). Tasks without these
  fields are written exactly as before. The Lean semantics (check, explore, replay) test only the goal field.
  `wg.Task.flags_comment` (24 Nov 2026): a comment written above the task's flags rule (gen_blocks.py records how its
  search setting was measured); without it the convention pass writes the group comment, as before. With it the
  test set's blocks-world rules are reproduced byte for byte (they had carried the comment, added by hand).

## Revision b

`agentgen/tools/vsproject.py` takes `--settings FILE` (Soar commands, one per line) and a per-variant `settings` list in the JSON; the commands are appended to `_firstload.soar` before any rule or library loads (for example `srand 42`, `soar wait-snc on`, `multi-attributes turn 20`). Output is unchanged without them. This is the near-term part of issue 10; the Lean `Settings` field is not done.

## Build

1. Install Lean through elan (the `lean-toolchain` file selects Lean 4.35.0). In a Claude cloud workspace,
   where elan's toolchain download is blocked, run `bash install-lean-sandbox.sh` (in this folder) instead.
2. Unzip the Lean release, `CMC/cmcsoar-release-2026-11-14.zip`, so that its `cmcsoar` folder sits
   beside `agentgen` (or change the `require cmcsoar` path in `agentgen/lakefile.lean`).
3. `cd agentgen && lake build agentgen worldcheck`. The first build also builds soar-lean, which
   takes a long time.

## Use

    agentgen/.lake/build/bin/agentgen water-jug-desc wj.json
    OUT=wj-rules.soar python3 worldgen/world_backend.py wj.json water-jug-look-ahead flat
    python3 worldgen/check_derived.py wj-rules.soar
    agentgen/.lake/build/bin/worldcheck --task wj-rules.soar

- `agentgen water-jug-desc OUT.json` writes the descriptions of the nine Water Jug variants.
- `world_backend.py DESC.json VARIANT [flat|static]` writes world-convention rules for one
  variant (`OUT=` names the file; `DUP=0` leaves out repeated-state avoidance).
- `worldcheck --task F.soar` reports convention violations in task rules; `--lib F.soar` checks
  library rules; `--wm F` checks a working-memory dump.

## Checked on 15 November 2026

Built against release-2026-11-14 (it uses only `Soar.Parse` and `Soar.Syntax`). The four commands
above ran; the generated Water Jug rules (33 rules) pass `check_derived.py` and `worldcheck`
(0 violations) and load in Soar 9.6.6 with library v2.26 without error (see the updates below).

## Updated 15 November 2026 (afternoon)

`worldgen/wg.py` is the worldgen v18 version (`Soar-library-dev/tools/worldgen-v18.zip`): object-handle
tests in generated rules carry `$` (World-Conventions-Spec-v6, L11-005). `world_backend.py` and
`check_derived.py` are unchanged. Checked: the Water Jug description generates 33 rules, 3 of them with
`$` handle tests; they pass `check_derived.py` and load without error after Soar library v2.30
(`Soar/soar-library`) in Soar 9.6.6.

## Updated 16 November 2026

This package combines `soarlean-agentgen-2026-11-15.zip` and `soarlean-agentgen-2026-11-15b.zip`, which
had diverged: revision b added the `vsproject.py` settings (above) but carried the older `wg.py`, without
the v18 literal handles. Here `vsproject.py` is revision b's and `wg.py` is the v18 one (the same file as in
`Soar-library-dev/tools/worldgen-v19.zip`). Library: v2.34 (`Soar/soar-library`). Library defaults are
`^iterative-step operator`, `^cost-metric none`, `^optimize false`; a task that does better with other
search settings sets them in `^flag-override`, chosen with `probe_settings.py`
(`Soar-library-dev/docs/Search-Settings-Intake-Checklist-v1.md`). agentgen does not yet choose these settings.

## Limits

- Under the world conventions, generation works for the Water Jug family only. The 14 step 6
  families (`Tasks/STEP6`) are not here and generate agents under the older conventions.
- `world_backend.py` supports integer attributes, one object type, atomic operators, a goal on one
  object, and look-ahead with complete avoid patterns.
- `worldcheck` encodes the conventions as of 10 and 11 November. It does not know later decisions
  (`^flag-override`, relation objects for one-argument relations, rule names, `$` on object-handle
  tests).
- The `World` compiler (`World/Compile.lean`) is superseded and not built; use `WorldSpec/Compile.lean` or
  `worldgen/world_backend.py`.
- `worldcheck --lib` on library v2.41 reports 56 violations, mostly L9-001 (library operators have no
  `^task-operator`); library rules need exemptions that the 10 to 11 November checks do not have.

## Provenance

`agentgen/Agent*`, `AgentGen.lean`, `tools/` and `worldgen/` are from `agentgen-bundle.zip`
(15 November); `World*` and `WorldCheck.lean` are from `agentgen-world.zip` (files of 10 and 11
November). The lakefile is new: it declares both libraries and both executables and points at the
Lean release instead of a bundled copy of soar-lean.

## Updated 16 November 2026 (afternoon): WorldSpec and rosiegen

`soarlean-agentgen-2026-11-16-worldspec.zip` adds `agentgen/WorldSpec/` (a typed description language for tasks
stated as in the Rosie teaching dialogs: legal-action conditions, goal and losing conditions, maintained relations,
sums), the `rosiegen` executable (`agentgen/RosieGen.lean`; lakefile: `lean_lib WorldSpec`, `lean_exe rosiegen`)
and `worldgen/spec_backend.py`. Nothing else changed. Build: `lake build rosiegen`. Three Rosie tasks (Tower of
Hanoi, fox-goose-bean, KenKen) are described; Lean writes their rules (path A) or exports the description for
`spec_backend.py` (path B). Both give the same rules, and the agents behave exactly as the direct ones
(`Tasks/From-English/rosie-teaching/LEAN-PATHS.md`). Details: `agentgen/WorldSpec/README.md`.

## Revision b, 16 November 2026 (evening): `soarlean-agentgen-2026-11-16b.zip`

Brought up to date with Soar library v2.41 (`Soar/soar-library`) after a cross-consistency check of the
repository. Supersedes `soarlean-agentgen-2026-11-16.zip` and `soarlean-agentgen-2026-11-16-worldspec.zip`
(both moved to `OLD/`).

- Library changes since v2.34 that bear on generated tasks: with `^iterative-step cost` the cost metric
  defaults to unit (v2.37); the depth limit is the `max-evaluation-depth` flag, default 12 (v2.37); a failed
  operator gets a reject preference instead of worst (v2.39); `^optimize true` guarantees the cheapest plan
  (positive step costs, admissible estimates) under operator depth as well as tie-impasse depth (v2.40); v2.41 changed
  comments only. Library defaults are still `^iterative-step operator`, `^cost-metric none`, `^optimize false`.
- `World/Check.lean`: the reserved operator names (L6-005) now match the library: `remove-object` and
  `force-conflict` (removed from the library) and `copy-task-state`, `apply-task-operator`,
  `evaluate-task-state` (never in it) dropped; selection-world's failure-evaluation operators
  (`initialize-failure-evaluation`, `count-object`, `count-relation`, `count-desired-object`,
  `count-desired-relation`, `count-name-finish`) added.
- `World/Compile.lean`: marked superseded (header comment only). It is not imported by `World.lean`, and what
  it emits predates P-006 and P-007 (`^agent-world true`, `default-*-copy`, direct `^flags`, `simple.soar`).
- `install-lean-sandbox.sh` (beside this README in the repository) installs Lean 4.35.0 in a Claude cloud
  workspace from GitHub releases.

Checked 16 November 2026 with Lean 4.35.0 and `cmcsoar-release-2026-11-14`: `lake build agentgen worldcheck`
and `lake build rosiegen` succeed; the Water Jug commands under Use give the same 33 rules as before, which pass
`check_derived.py` and `worldcheck --task` (0 violations); `worldcheck --lib` on library v2.41 gives the same
report as before the change; a probe confirms `remove-object` is no longer flagged and `count-object` is.
Not checked here: loading the generated rules with library v2.41 in Soar (the workspace has only Soar 9.6.5,
which lacks `$`).

## Updated 18 November 2026: conventions of the 18 Nov workbook review

Package: `soarlean-agentgen-2026-11-18.zip` (superseded by revision b, below). The generators follow the conventions decided on 18 Nov 2026 (World-Conventions-v6 / Soar-Conventions, level-based IDs):
- `worldgen/convpass.py` (also in worldgen v21): a final pass over generated rules. L3-005: every rule tests, in its first condition, the name of its state or of its problem space (world and desired elaborations, internal applications and environment-effect rules now test `^problem-space.name`); exceptions are initialization, the problem-space elaborations and rules that only pass superstate structure into substates. L3-012: a rule group without an English comment gets one. `wg.py` (worldgen v21) and `spec_backend.py` (path B) call it.
- `agentgen/World/Compile.lean` and `agentgen/WorldSpec/Compile.lean` (rosiegen path A) write the same `^problem-space.name` tests; `World/Compile.lean` puts a comment line before every rule.
- `agentgen/Agent/Compile.lean` (tie-heuristic agents): ^last-operator is now a structure with the operator's name and parameters, written by one application rule per operator that also removes the previous record (L3-021, L4-005); initialization creates `(^last-operator.name none)`; the heuristics test `^last-operator.name`.
- `agentgen/tools/vsproject.py` passes every written file through `tools/convpass.py`, which adds a comment per rule group (agentgen rules already test the state name).
Checked: `lake build agentgen worldcheck rosiegen` succeeds; the nine Water Jug agentgen variants run with the same decision counts as before (srand 1); rosiegen path A for tower-of-hanoi differs only in the five `^problem-space.name` tests (it reaches the 20,000-decision cap without a move on library v2.42 before and after the change).
- Convention IDs cited in the Lean sources and in checker messages are still the IDs from before the 18 Nov renumbering; `Conventions/id-renumbering-map-2026-11-18.csv` maps them.

## Revision b, 18 November 2026 (evening): `soarlean-agentgen-2026-11-18b.zip`

`agentgen/WorldSpec/Compile.lean` (rosiegen path A) now writes the three rule-group comments that `convpass.py` adds on path B (the initialization proposal, the problem-space elaborations and the flags elaboration), worded as `convpass.describe` words them. Paths A and B again write identical rules apart from the first header line; checked on Tower of Hanoi, fox-goose-bean and KenKen (initial worlds, and the fail and final KenKen worlds). Nothing else changed from the 18 November package.
