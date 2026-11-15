# Resume: Soar-Lean-Agents (updated 15 Nov 2026)

The earlier resume (10 Nov 2026) is in `OLD/RESUME.md`; its next steps (library findings, Blocks World optimality, Soar 9.6.50 with `$`, workbook updates) are done or carried below.

## Status (15 Nov 2026)

**Shared library v2.30.** The Soar default libraries were restructured into one library, `Soar/soar-library` (soar-base, selection-world with iterative deepening, agent-world, object-world, thor-soar, thor-tasks). All projects load it through `soar-library.soar`; each release is a numbered zip in `Soar-library-dev/releases` with an entry in `CHANGES.md`. v2.30 makes iterative deepening with tie-impasse depth, a cost metric and `^optimize true` find optimal solutions, with and without chunking:

| Task | No chunking | Chunking, first run | Chunking, second run (reusing the first run's chunks) |
|---|---|---|---|
| Hanoi, 2 discs | 3 moves on all seeds | 3 on all | 3 on all |
| Blocks world | 3 on all | 3 on all | 3 on all |
| Water jug 7/9 B1, D1, B3, D3 | 8 on all | 8 on all | 8 on all |
| Missionaries and cannibals | 11 on all | 11 on all | 11 on all |
| Artists, 2 pairs | 5 on all | 5, 7, 5 | 5 on all |

**Regression test set v1.27** (`Soar-library-dev/testset/soar-library-testset-v1.27.zip`): 296 tests, all passing on v2.30. Action sequences are unchanged from v2.29 in every environment-complete test that changed.

**Conventions.** `Conventions/World-Conventions-v5.xlsx` and `Conventions/World-Conventions-Spec-v6.md`. New in v5/v6: W-CHK-009 (no negated tests on look-ahead structure; maintain such elaborations in the applications), W-CHK-010 (status of chunking in look-ahead), W-CHK-011 (object-handle tests carry `$`, with two exceptions for Soar defects). Generated task rules follow them (`Soar-library-dev/tools/worldgen-v18.zip`).

**Soar defects with `$`.** `Soar/bugs/soar-dollar-bugs.zip`: `$` in a negated condition makes chunking fail ("bad test type in hash_test"), and `$` after a relational test inside `{ }` crashes Soar when the rule loads. Repro programs, code locations and proposed fixes are in the report; the library uses neither construct.

**Task packages.** `Tasks/zebra-world.zip`, `Tasks/artists-world.zip`, `Tasks/UWM Tasks/mc-world.zip` and `wizards-world.zip` now load the shared library and were rerun on v2.30 (zebra solved and checked on seeds 1 to 10; artists 2 pairs solved and checked safe on seeds 1 to 3; mc 11 crossings; wizards solved).

**Lean tools.** `SoarLean/soarlean-agentgen-2026-11-15.zip`: agentgen, the World library and worldcheck in one Lean package, with the Python world-rule back end (its `wg.py` now adds `$`).

## Open items

1. **Artists, 3 pairs:** not solved within 20,000 decisions since v2.25 (known regression in the test set). Artists 2 pairs, seed 2, took 7 crossings in a first chunking run; not yet traced.
2. **Operator iterative step with chunking:** still longer than optimal on some water jug seeds (24 moves on some B1 and D1 seeds).
3. **Chunk transfer across objects:** with `$` on handles, chunks apply only to the same named objects. A chunking mechanism that keeps distinct handles distinct would remove the need for `$` (JEL looking into chunking options).
4. **Report the `$` defects** to SoarGroup (`Soar/bugs/soar-dollar-bugs.zip`). Pushing to SoarGroup repositories needs the Claude GitHub App installed or GitHub reconnected.
5. **Thor-Soar on the shared library:** `thor-soar` and `thor-tasks` load in v2.30 but have not been run against the Thor simulator.
6. **worldcheck** encodes the conventions of 10 and 11 November; it does not yet know `^flag-override`, relation objects for one-argument relations, rule names or `$` on handles.
7. **Generation from English** under the world conventions covers the Water Jug family only; the 14 step 6 families (`Tasks/STEP6`) use the older conventions and libraries.
8. **Ratify** the world conventions (World-Conventions-v5.xlsx and the VisualSoar project conventions) with CIC reviewers.
9. **Decks** in `Slides/` and the draft manual (`Soar/docs/Soar-Lean-Agents-Manual-draft-v1.docx`) predate the current layout and library v2.30.
