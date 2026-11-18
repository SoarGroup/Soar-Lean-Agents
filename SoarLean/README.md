# SoarLean: agentgen, the World library and worldcheck (16 November 2026, revision b; updated 18 November 2026)

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

Package: `soarlean-agentgen-2026-11-18.zip`. The generators follow the conventions decided on 18 Nov 2026 (World-Conventions-v6 / Soar-Conventions, level-based IDs):
- `worldgen/convpass.py` (also in worldgen v21): a final pass over generated rules. L3-005: every rule tests, in its first condition, the name of its state or of its problem space (world and desired elaborations, internal applications and environment-effect rules now test `^problem-space.name`); exceptions are initialization, the problem-space elaborations and rules that only pass superstate structure into substates. L3-012: a rule group without an English comment gets one. `wg.py` (worldgen v21) and `spec_backend.py` (path B) call it.
- `agentgen/World/Compile.lean` and `agentgen/WorldSpec/Compile.lean` (rosiegen path A) write the same `^problem-space.name` tests; `World/Compile.lean` puts a comment line before every rule.
- `agentgen/Agent/Compile.lean` (tie-heuristic agents): ^last-operator is now a structure with the operator's name and parameters, written by one application rule per operator that also removes the previous record (L3-021, L4-005); initialization creates `(^last-operator.name none)`; the heuristics test `^last-operator.name`.
- `agentgen/tools/vsproject.py` passes every written file through `tools/convpass.py`, which adds a comment per rule group (agentgen rules already test the state name).
Checked: `lake build agentgen worldcheck rosiegen` succeeds; the nine Water Jug agentgen variants run with the same decision counts as before (srand 1); rosiegen path A for tower-of-hanoi differs only in the five `^problem-space.name` tests (it reaches the 20,000-decision cap without a move on library v2.42 before and after the change).
- Convention IDs cited in the Lean sources and in checker messages are still the IDs from before the 18 Nov renumbering; `Conventions/id-renumbering-map-2026-11-18.csv` maps them.
