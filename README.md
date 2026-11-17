# Soar-Lean-Agents

Soar agents created from English -> Lean -> Soar, with the shared Soar library they run on and the Lean 4 specifications of the Common Model of Cognition (CMC), Soar, ACT-R and Sigma that support the work.

Start here:
- `RESUME.md`: current status and next steps of the English-to-Soar and library work.
- `Soar/docs/Soar-Lean-Agents-Manual-draft-v2.docx`: the manual, which includes how to set up Claude, Soar and a session to generate a Soar agent from English (Chapter 6), how to interface to an external environment (Chapter 7) and a worked Water Jug example (Appendices I to K).
- `Soar/soar-library/`: the Soar library every project loads (v2.42, 17 November 2026).
- `CMC/cmcsoar-release-2026-11-14.zip`: the Lean specifications of the CMC and of Soar (see `RELEASE.md` inside it); `STATUS.md` here is a copy of its status file.
- `Slides/From-English-to-Soar-CIC.pptx`: the main deck.

## Loading the Soar library

All projects load one copy of the library, `Soar/soar-library`. `VERSION.txt` and `CHANGES.md` inside it give the version and every change.

    pushd <repository>/Soar/soar-library
    source soar-library.soar      # soar-base, selection-world, agent-world, object-world
    source thor.soar              # only for Thor-Soar agents
    popd

The library needs Soar 9.6.6 (the SoarSuite 9.6.6 bug-fix release, used for all current tests) or a 9.6.50 build; releases up to 9.6.5 reject `$` in conditions.

Soar 9.6.6 download (the zip is not kept in this repository): <https://github.com/SoarGroup/Soar/releases/download/untagged-d618888db86c4a9e18ee/SoarSuite_9.6.6-bigbugfixrelease-Multiplatform.zip>

Each library release is a numbered zip in `Soar-library-dev/releases` (`soar-library-restructured-v2.NN.zip`) with an entry in `CHANGES.md`. To install a release, delete `Soar/soar-library` and unzip the release in `Soar/`: from v2.35 on, each release zip's top folder is `soar-library/`. (Up to v2.34 the top folder is `soar-library-restructured/`; copy its contents into `Soar/soar-library` instead.) `VERSION.txt` names the installed version. The load lines above do not change.

## Layout

### Root
- `README.md`, `RESUME.md`, `STATUS.md` (copy of the Lean release's status), `LICENSE`.
- `OLD/` folders (here and in any subfolder) hold superseded files and are ignored by git (`.gitignore`).

### `Soar/`
Using Soar and the shared library. `Soar/README.md` lists the contents.
- `soar-library/`: the shared library (v2.42). Projects: soar-base, selection-world (with iterative deepening), agent-world, object-world, thor-soar and thor-tasks, each a VisualSoar project with its datamap; `tools/` holds the build scripts (parser, datamaps, chunker).
- `docs/`: `Soar-Lean-Agents-Manual-draft-v2.docx` (draft manual; it supersedes the former setup guide `English-to-Soar-Setup.docx`), `Visual Soar User's Manual.html`.
- `bugs/`: `Soar-9.6.5-Kernel-Defects.docx` (defects found in the Soar 9.6.5 kernel, with their status in 9.6.6) and `soar-dollar-bugs/` (two defects with `$`: repro programs, code locations, proposed fixes).
- `lean-spec/`: `Soar-on-CMC-Lean.docx` (and `.pdf`), `Soar-Lean-map.xlsx` (copies of those in the Lean release's `doc/`), `SOAR-LEAN-CONTEXT.md` (the release's `CLAUDE.md`; rename to `CLAUDE.md` to have it loaded), `Value of Lean Soar.docx`.

### `Soar-library-dev/`
Development of the shared library (formerly `Default-conversion`, the conversion of the Soar default libraries). `Soar-library-dev/README.md` lists the contents and the release policy.
- `releases/`: numbered library releases; current `soar-library-restructured-v2.42.zip` (same content as `Soar/soar-library`; v2.42 removes the nested-selection preference that kept cost graph r4x8 from finishing under tie-impasse). Library defaults: `^iterative-step operator`, `^cost-metric none`, `^optimize false`; each task sets better search settings in `^flag-override`.
- `testset/`: numbered regression test sets; current `soar-library-testset-v1.35.zip` (515 tests, for v2.42; v1.29 added the world-convention step 6 task families, v1.30 tie-impasse search with a cost metric, v1.31 re-baselined for v2.37, v1.32 the first tests of the unachieved-desireds starting depth, v1.33 re-baselined for v2.40, v1.34 README corrections only, v1.35 re-baselined for v2.42).
- `docs/`: `Soar-Library-Refactoring-Proposal-v3.docx`, `Restructure-Build-Report-v1.md`, `Cost-Aware-Evaluation-Plan-v2.docx`, `Option-Selection-Guide-v1.md`, `Search-Settings-Intake-Checklist-v1.md` (choosing a task's search settings), `History-verify-guardrails-force-conflict.md` (removed in v2.38, kept for reintroduction).
- `findings/`: `FINDING-chunking-overgeneral.md`, `FINDING-early-failure-propagation.md`, `FINDING-stale-worst-preference.md`, `FINDING-tie-impasse-unbounded-continuation.md`, and the findings of 10 November (`Library-Findings.docx`, `Library-Findings-Review.xlsx`).
- `tools/`: `worldgen-v19.zip` (generators for the generated test tasks), `restructure-tools-v2.22.zip`, `option-selection/` (option-selection tools, unpacked, including `probe_settings.py`), `soar-lint/` (the linter with its step-0 report and baseline).
- `studies/`: `water-jug-79-v4.zip` (the water jug 7/9 study), `Families-Results.xlsx`.

### `SoarLean/`
- `soarlean-agentgen-2026-11-16b.zip`: one Lean package with agentgen (task-design language and generator), the World library and worldcheck, WorldSpec and rosiegen, plus the Python world-rule back end. `README.md` says how to build and use it.
- `install-lean-sandbox.sh`: installs Lean 4.35.0 in a Claude cloud workspace (where elan cannot download toolchains).

### `Conventions/`
- `World-Conventions-Spec-v6.md`: the world conventions specification, including the chunking conventions W-CHK-009 to W-CHK-011.
- `IO-Conventions-Proposed.md`: proposed input/output conventions (draft).
- `World-Conventions-v6.xlsx`: the world conventions workbook (state and `^world` representation, desireds, operators, capacities, cost, chunking), with the REW reviewer column; it holds where it and the specification differ.
- `Soar-Conventions.xlsx`: conventions derived from existing Soar programs.
- `VisualSoar-Project-Conventions.docx`: conventions for laying out an agent as a VisualSoar project.

### `Tasks/`
Task agents that load `Soar/soar-library`.
- `From-English/`: agents written directly from English under the world conventions: `artists-world/`, `zebra-world/`, `mc-world/` (sets `^iterative-step tie-impasse`, v2.34), `wizards-world/`; also `Three-mens-morris/`, `UWM/` (the UWM task descriptions and first versions) and `rosie-teaching.zip` (54 games and puzzles as English input). `From-English/README.md` lists them.
- `Families/`: the 68 step 6 task agents in 14 families, each as the original program and the world-convention version, with `Families-Results.xlsx` and the harness (`run.py`, `list.txt`). `step6-families-world.zip` is the same folder as a zip. Five world variants set `^iterative-step tie-impasse` (v2.34; see `Families/README.md`).
- `STEP6/`: the blind round trip of 68 tasks (`Blind-Round-Trip-68.xlsx`, `blind-round-trip-68.zip`) and the step 6 package (`step6-consolidated-2026-11-08.zip`); these use the libraries of early November.
- `hps-tasks.zip`: PDDL task sets derived for replicating Langley, Barley and Meadows (2018): blocks world, five puzzle, kinship and logistics, 52 problems.
- `io-reference-and-conventions.zip`: an input/output reference agent (`io-guess`) and `IO-Conventions-Proposed.md` (also in `Conventions/`).
- `Issues-Priority-2026-11-15.xlsx`: open issues by priority.
- `soar-agents-default-libraries.zip`, `soar-agents-working.zip`, `soar-agents-other-issues.zip`: agent library test results (early November).

### `CMC/`
- `cmcsoar-release-2026-11-14.zip`: the reference release of the Lean 4 specifications (Lean 4.35.0): the CMC in three versions (2017, metacognition, emotion) with the proofs that each contains the one before, and Soar on the CMC with the executable model `soar-lean`.
- `cmcsoar-work-2026-11-14-theorems.zip`: a working copy of 14 November (theorems).
- `CMC Metacognition Guide to the Lean Specification v2.docx`, `CMC-Lean-Summary-v2.docx`, `Lean-CMC-commentary.docx`, `CMC-Emotion-Open-Questions.docx`, `CMC-Three-Way-Comparison-v6.docx`, `Formal, Executable Theories of Cognition.docx`.

### `ACT-R/`
- `ACT-R-on-CMC-Analysis-v8.docx` (latest), `-v7.docx`, and `-v6 CL.docx` (with Christian Lebiere's comments).
- `actr-lean.zip`, `actr-lean.tar.gz`: the ACT-R Lean specification.

### `Sigma/`
- `Sigma-on-CMC-Analysis-v3.docx`, `Sigma-CMC-Mapping-for-Review-v2.docx`, `Sigma38-Findings-for-Review-v2.docx`, `Sigma-materials-for-review-v2.zip` (latest), with their earlier versions; `Sigma-Survey-v2.docx`; `SigmaArch.zip` (the Lean specification of Sigma).

### `Slides/`
Decks, including `From-English-to-Soar-CIC.pptx` (main), the English-to-Soar setup, roles and without-Lean decks, world-convention decks, Development-Process, Finding-Library-Defects, Soar-Lean-Spec, the data-flow deck and the step 6 summary. The decks predate the shared library (15 November).

### `Papers/`
- Wray, Schmidt and Jones, *Cognitive Systems Engineering with Coding Models* (10 Jul 2026).
- Thor-Soar agent documentation (exported 8 Nov 2026).
