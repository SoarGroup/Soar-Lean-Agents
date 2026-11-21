# Release checklist: library, conventions and generators (21 November 2026)

A release brings **everything that generates or checks agents** up to date with the newest library and conventions, and
shows that every stored generated file is what the current generators produce. Work through the steps in order; record
each result in the release notes. A step that cannot be done is recorded as not done, with the reason.

Written after the release of 21 November 2026, which missed the classic-AI WorldSpec line (merged in
`SoarLean-2026-11-21b-release.zip`) and did not build `agentgen` or `worldcheck`.

## 1. Inventory (before changing anything)

1. **SoarLean packages.** List every zip in `SoarLean/` and `SoarLean/OLD/`. For each, check that the new release
   contains it: three-way merge it into the new package against the package it branched from; the merge must add
   nothing. A package that adds something is a missed line: merge it.
2. **Generators and their outputs.** Confirm the table below is complete (look for new `gen*.py`, `*-spec.py`, Lean
   task files and generator zips since the last release) and update it.
3. **Shared copies.** These files exist in several places and must be byte-identical:
   - `wg.py`, `convpass.py`, `check_derived.py`, `world_backend.py`: `SoarLean/worldgen/`,
     `Tasks/From-English/rosie-teaching/tools/` (`wg.py`, `convpass.py`, `check_derived.py`),
     `SoarLean/agentgen/tools/convpass.py`, `Soar-library-dev/tools/worldgen-vNN.zip`.
   - `worldspec_py.py`: `SoarLean/worldgen/`, `Tasks/webtasks/tools/`.

| Generator | Inputs | Outputs it must reproduce |
|---|---|---|
| `familygen` (`SoarLean/agentgen/Family/`) | Family Lean descriptions | `Tasks/Families/*/world-lean/*` (67 variants) |
| `rosiegen compile` (path A) and `worldgen/spec_backend.py` (path B) | `WorldSpec/Tasks/*.lean`, `*-worldspec.json` | Lean-path Rosie agents (Hanoi, fox-goose-bean, KenKen); `Tasks/webtasks/classic-ai/*/*-rules.soar` |
| Webtasks `*-spec.py` + `tools/worldspec_py.py` | `english-input.txt` statements | `*-worldspec.json`, `<Name>.lean` (must equal `rosiegen json`) |
| Rosie `gen.py` (per task) + `tools/rosie_*.py`, `wg.py` | `script.txt` | `Tasks/From-English/rosie-teaching/*/*` rule files |
| English world agents `gen.py` | artists, mc, wizards, zebra worlds | their rule files |
| `agentgen`, `world_backend.py` | Water Jug descriptions | Water Jug variants (33 rules for water-jug-look-ahead flat) |
| `worldcheck` | generated rules, library | 0 violations on task rules |
| `Conventions/gen_spec.py` | `World-Conventions-vN.xlsx`, `Soar-Conventions.xlsx` | `World-Conventions-Spec-vN.md`, `Soar-Conventions-Spec.md` |
| `Soar-library-dev/tools/worldgen-vNN.zip` | (generator copies) | the shared copies above |

## 2. Library and conventions

1. Library release zip in `Soar-library-dev/releases/` with `VERSION.txt` and a `CHANGES.md` entry.
2. Convention workbooks updated; every library or generator change that implements a convention cites its ID, and every
   new decision is recorded as a convention (fixes go into conventions and generators, never into generated agents).
3. `gen_spec.py` run; the spec `.md` files regenerated and committed; READMEs point to the current spec version.

## 3. Generators

1. Every generator updated for the new conventions; the Lean path (A) and the Python path (B) changed together.
2. One SoarLean package with every line merged (step 1.1); `README.md` section for the release.
3. Build every Lean program with `cmcsoar-release-…` beside `agentgen`:
   `lake build agentgen worldcheck rosiegen familygen`. Record the Lean version and the job count.
4. WorldSpec: every `wellFormed` theorem proved; `rosiegen json` equals the Python JSON for every task.

## 4. Regenerate and compare

For every row of the inventory table: regenerate, then diff against the stored output.
- Paths A and B identical (apart from the header line) for every WorldSpec task.
- Every difference from the stored file is explained by a change in this release (name the convention or library
  change); anything unexplained is a defect to fix before release.
- Commit the regenerated files.

## 5. Evaluate

1. Test set: `python3 run_tests.py --libs <library>`; rebaseline with `--update` only for explained changes; second
   identical pass; new test set zip.
2. Families: own settings and chunk-only, all variants.
3. Rosie tasks, seeds 1-3; English world agents; webtasks (classic AI, seeds 1-3), with the semantic checks
   (`rosiegen check` on every example state, `rosiegen replay` on every run).
4. Compare with the previous release's results; every regression gets a To-do row.
5. Results spreadsheet `Tasks/Results on library vN (date).xlsx`; failing variants with an orange background.

## 6. Publish

1. Release zips in place (library, test set, SoarLean); superseded zips to `OLD/`.
2. READMEs updated: Soar-library-dev, Soar, SoarLean, Tasks folders touched.
3. Release notes list: what changed, what was regenerated, results compared with the previous release, steps not done.
4. To-do sheet updated (fixed items to Completed, new regressions added).
