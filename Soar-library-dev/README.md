# Soar-library-dev

Development of the shared Soar library (formerly `Default-conversion`). The library in use is `../Soar/soar-library`.

| Folder | Contents |
|---|---|
| `releases/` | Numbered library releases, `soar-library-restructured-v2.NN.zip` (current: v2.35). Each zip's `CHANGES.md` has an entry for every release. |
| `testset/` | Numbered regression test sets, `soar-library-testset-v1.NN.zip` (current: v1.28, for v2.34 and v2.35; 296 tests). Each zip's `README.md` records the baseline changes of every version. |
| `docs/` | Design and process documents: `Soar-Library-Refactoring-Proposal-v3.docx`, `Restructure-Build-Report-v1.md`, `Cost-Aware-Evaluation-Plan-v2.docx`, `Option-Selection-Guide-v1.md`, `Search-Settings-Intake-Checklist-v1.md`. |
| `findings/` | Library findings, one `FINDING-<topic>.md` per finding (chunking over-generality, early failure propagation, stale worst preference, tie-impasse unbounded continuation), and the findings of 10 November (`Library-Findings.docx`, `Library-Findings-Review.xlsx`). |
| `tools/` | `worldgen-v19.zip` (rule generators for the generated tasks), `restructure-tools-v2.22.zip` (builds the library from the original projects), `option-selection/` (option-selection tools, including `probe_settings.py`; see `docs/Option-Selection-Guide-v1.md`), `soar-lint/` (linter, step-0 report and baseline). |
| `studies/` | Experiments on particular tasks: `water-jug-79-v4.zip` (water jug 7/9 variants), `Families-Results.xlsx`. |
| `OLD/` | Superseded releases, test sets and tools (ignored by git). |

Release policy:
- Each library release is a separate numbered zip in `releases/` with a `CHANGES.md` entry; each test set version is a numbered zip in `testset/`. Superseded zips move to `OLD/`.
- A release is installed by replacing `../Soar/soar-library` with the zip's contents. From v2.35 on, every release zip has `soar-library/` as its top folder (decided 16 Nov 2026), so deleting `../Soar/soar-library` and unzipping the release in `../Soar` installs it. Up to v2.34 the top folder is `soar-library-restructured/`: copy its contents into `../Soar/soar-library`. From v2.31 on, the zip includes `VERSION.txt`. `VERSION.txt` in `soar-library` names the installed version.
- The test set is run against the library before a release: `python3 run_tests.py --libs <library folder>`.
