# Soar-library-dev

Development of the shared Soar library (formerly `Default-conversion`). The library in use is `../Soar/soar-library`.

| Folder | Contents |
|---|---|
| `releases/` | Numbered library releases, `soar-library-restructured-v2.NN.zip` (current: v2.47, 24 Nov 2026: phases and loops of desireds, environment-neutral output map). Each zip's `CHANGES.md` has an entry for every release. |
| `testset/` | Numbered regression test sets, `soar-library-testset-v1.NN.zip` (current: v1.40, for v2.47; 515 tests). Each zip's `README.md` records the baseline changes of every version. |
| `docs/` | Design and process documents: `Soar-Library-Refactoring-Proposal-v3.docx`, `Restructure-Build-Report-v1.md`, `Cost-Aware-Evaluation-Plan-v2.docx`, `Option-Selection-Guide-v1.md`, `Search-Settings-Intake-Checklist-v1.md`, `History-verify-guardrails-force-conflict.md` (rule text of the verify, guardrails and force-conflict experiments removed in v2.38). |
| `findings/` | Library findings, one `FINDING-<topic>.md` per finding (chunking over-generality, early failure propagation, stale worst preference, tie-impasse unbounded continuation), and the findings of 10 November (`Library-Findings.docx`, `Library-Findings-Review.xlsx`). |
| `tools/` | `worldgen-v23.zip` (rule generators for the generated tasks; applies the 18 Nov 2026 conventions; v23 adds phases and loops, the output form and `flags_comment`), `restructure-tools-v2.22.zip` (builds the library from the original projects), `option-selection/` (option-selection tools, unpacked from `../option-selection-v1.2.zip` and updated 16 Nov 2026 for library v2.37 to v2.41, including `probe_settings.py`; see `docs/Option-Selection-Guide-v1.md`), `soar-lint/` (linter, step-0 report and baseline). |
| `studies/` | Experiments on particular tasks: `water-jug-79-v4.zip` (water jug 7/9 variants), `Families-Results.xlsx`. |
| `OLD/` | Superseded releases, test sets and tools (ignored by git). |

Release policy (full procedure: `RELEASE-CHECKLIST.md`, which covers the library, conventions, every generator and every task set):
- Each library release is a separate numbered zip in `releases/` with a `CHANGES.md` entry; each test set version is a numbered zip in `testset/`. Superseded zips move to `OLD/`.
- A release is installed by replacing `../Soar/soar-library` with the zip's contents. From v2.35 on, every release zip has `soar-library/` as its top folder (decided 16 Nov 2026), so deleting `../Soar/soar-library` and unzipping the release in `../Soar` installs it. Up to v2.34 the top folder is `soar-library-restructured/`: copy its contents into `../Soar/soar-library`. From v2.31 on, the zip includes `VERSION.txt`. `VERSION.txt` in `soar-library` names the installed version.
- The test set is run against the library before a release: `python3 run_tests.py --libs <library folder>`.

v2.46 (23 Nov 2026): the library learns from look-ahead by default (`chunk only`, World-Conventions L5-021). An agent that must not learn sets `chunk never` after loading the library; agents generated from English get it from a line 'Learning: do not learn from look-ahead. <reason>' in their English statement. Release evaluation: `../Tasks/Results on library v2.46 (23 Nov 2026).xlsx`.

v2.47 (24 Nov 2026): phases and loops of desireds (World-Conventions L8-026 to L8-030), the environment's command form from the top state's output map (L10-018), up to 10 desireds, look-ahead copies with their own desireds (L14-044), no failures passed up after a random continuation (L4-004), a step backstop for runaway look-ahead (L16-046), a workaround for a kernel crash with look-ahead and means-ends subgoaling; evaluation-order marks disabled (L15-026 suspended). Release evaluation: `../Tasks/Results on library v2.47 (24 Nov 2026).xlsx`.
