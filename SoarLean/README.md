# SoarLean: agentgen, the World library and worldcheck (16 November 2026)

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
    and a compiler from descriptions to rules (not yet exposed as a command).
  - `WorldCheck.lean`: the `worldcheck` executable.
  - `tools/vsproject.py`: writes Visual Soar projects.
- `worldgen/` (Python): `world_backend.py` (Lean description to world-convention rules),
  `check_derived.py` (derived attributes are declared not to be copied), `wg.py` (shared generator).

## Revision b

`agentgen/tools/vsproject.py` takes `--settings FILE` (Soar commands, one per line) and a per-variant `settings` list in the JSON; the commands are appended to `_firstload.soar` before any rule or library loads (for example `srand 42`, `soar wait-snc on`, `multi-attributes turn 20`). Output is unchanged without them. This is the near-term part of issue 10; the Lean `Settings` field is not done.

## Build

1. Install Lean through elan (the `lean-toolchain` file selects Lean 4.35.0).
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
tests in generated rules carry `$` (World-Conventions-Spec-v6, W-CHK-011). `world_backend.py` and
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
- The `World` compiler has no `agentgen` command yet.

## Provenance

`agentgen/Agent*`, `AgentGen.lean`, `tools/` and `worldgen/` are from `agentgen-bundle.zip`
(15 November); `World*` and `WorldCheck.lean` are from `agentgen-world.zip` (files of 10 and 11
November). The lakefile is new: it declares both libraries and both executables and points at the
Lean release instead of a bundled copy of soar-lean.
