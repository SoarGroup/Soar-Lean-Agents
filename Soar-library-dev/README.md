# Soar-library-dev

Development of the shared Soar library (formerly `Default-conversion`). The library in use is `../Soar/soar-library`.

| Folder | Contents |
|---|---|
| `releases/` | Numbered library releases, `soar-library-restructured-v2.NN.zip` (current: v2.30). Each zip's `CHANGES.md` has an entry for every release. |
| `testset/` | Numbered regression test sets, `soar-library-testset-v1.NN.zip` (current: v1.27, for v2.30; 296 tests). Each zip's `README.md` records the baseline changes of every version. |
| `docs/` | Design and process documents: `Soar-Library-Refactoring-Proposal-v3.docx`, `Restructure-Build-Report-v1.md`, `Cost-Aware-Evaluation-Plan-v2.docx`, `Option-Selection-Guide-v1.md`. |
| `findings/` | Library findings, one `FINDING-<topic>.md` per finding (chunking over-generality, early failure propagation, stale worst preference), and the findings of 10 November (`Library-Findings.docx`, `Library-Findings-Review.xlsx`). |
| `tools/` | `worldgen-v18.zip` (rule generators for the generated tasks), `restructure-tools-v2.22.zip` (builds the library from the original projects), `option-selection/` (option-selection tools; see `docs/Option-Selection-Guide-v1.md`), `soar-lint/` (linter, step-0 report and baseline). |
| `studies/` | Experiments on particular tasks: `water-jug-79-v4.zip` (water jug 7/9 variants). |
| `OLD/` | Superseded releases, test sets and tools (ignored by git). |

Release policy:
- Each library release is a separate numbered zip in `releases/` with a `CHANGES.md` entry; each test set version is a numbered zip in `testset/`. Superseded zips move to `OLD/`.
- A release is installed by replacing `../Soar/soar-library` with the zip's contents. v2.30's top folder is `soar-library-restructured/`; from v2.31 on, the top folder is `soar-library/` and the zip includes `VERSION.txt`, so unzipping it in `../Soar` replaces the library in place. `VERSION.txt` in `soar-library` names the installed version.
- The test set is run against the library before a release: `python3 run_tests.py --libs <library folder>`.
