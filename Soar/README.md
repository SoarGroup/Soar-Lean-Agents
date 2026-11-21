# Soar

Using Soar and the shared Soar library. Library development is in `../Soar-library-dev`.

| Folder | Contents |
|---|---|
| `soar-library/` | The shared library every project loads (v2.45 of 21 Nov 2026 once installed from `../Soar-library-dev/releases/soar-library-restructured-v2.45.zip`; `VERSION.txt`, `CHANGES.md`). Load it with `pushd soar-library`, `source soar-library.soar` (and `source thor.soar` for Thor-Soar agents), `popd`. To install a new release, delete this folder and unzip a release from `../Soar-library-dev/releases` here, in `Soar/`: from v2.35 on, the zip's top folder is `soar-library/`. (Up to v2.34 it is `soar-library-restructured/`; copy its contents into this folder instead.) |
| `docs/` | Guides and manuals: `Soar-Lean-Agents-Manual-draft-v2.docx` (draft manual, including setting up Claude, Soar and a session to generate an agent from English; it supersedes `English-to-Soar-Setup.docx`), `Visual Soar User's Manual.html`. |
| `bugs/` | Soar kernel defects and bug reports: `Soar-9.6.5-Kernel-Defects.docx` (with their status in 9.6.6), `soar-dollar-bugs/` (two defects with `$` in Soar 9.6.6, kernel 9.6.50). |
| `lean-spec/` | Copies of the Lean specification documents from `../CMC/cmcsoar-release-2026-11-14.zip`: `Soar-on-CMC-Lean.docx` and `.pdf`, `Soar-Lean-map.xlsx`, `SOAR-LEAN-CONTEXT.md` (the release's `CLAUDE.md`); and `Value of Lean Soar.docx`. |
| `Proposals/` | Proposals for new library competences and Soar architecture changes, one Word document each (e.g. `Proposal-Learning-Action-Models-from-Surprises.docx`). Each proposal analyzes the architecture changes needed, the supporting knowledge required, and a hybrid option. |
| `OLD/` | Superseded files (ignored by git). |

What goes where: a guide or manual for people using Soar or the library goes in `docs/`; a defect in the Soar kernel goes in `bugs/` (one file or zip per report, with a repro program); a defect or limitation of the library goes in `../Soar-library-dev/findings/`; a proposal for a new library competence or an architecture change goes in `Proposals/`.

Soar itself is not kept here. The library needs Soar 9.6.6; download the SoarSuite 9.6.6 release from <https://github.com/SoarGroup/Soar/releases/download/untagged-d618888db86c4a9e18ee/SoarSuite_9.6.6-bigbugfixrelease-Multiplatform.zip>.
