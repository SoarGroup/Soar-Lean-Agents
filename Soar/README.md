# Soar

Using Soar and the shared Soar library. Library development is in `../Soar-library-dev`.

| Folder | Contents |
|---|---|
| `soar-library/` | The shared library every project loads (v2.30; `VERSION.txt`, `CHANGES.md`). Load it with `pushd soar-library`, `source soar-library.soar` (and `source thor.soar` for Thor-Soar agents), `popd`. To install a new release, replace this folder with the contents of a zip from `../Soar-library-dev/releases`. |
| `docs/` | Guides and manuals: `Soar-Lean-Agents-Manual-draft-v1.docx` (draft manual, including setting up Claude, Soar and a session to generate an agent from English; it supersedes `English-to-Soar-Setup.docx`), `Visual Soar User's Manual.html`. |
| `bugs/` | Soar kernel defects and bug reports: `Soar-9.6.5-Kernel-Defects.docx` (with their status in 9.6.6), `soar-dollar-bugs.zip` (two defects with `$` in Soar 9.6.6, kernel 9.6.50). |
| `lean-spec/` | Copies of the Lean specification documents from `../CMC/cmcsoar-release-2026-11-14.zip`: `Soar-on-CMC-Lean.docx` and `.pdf`, `Soar-Lean-map.xlsx`, `SOAR-LEAN-CONTEXT.md` (the release's `CLAUDE.md`); and `Value of Lean Soar.docx`. |
| `OLD/` | Superseded files (ignored by git). |

What goes where: a guide or manual for people using Soar or the library goes in `docs/`; a defect in the Soar kernel goes in `bugs/` (one file or zip per report, with a repro program); a defect or limitation of the library goes in `../Soar-library-dev/findings/`.

Soar itself is not kept here. The library needs Soar 9.6.6; download the SoarSuite 9.6.6 release from <https://github.com/SoarGroup/Soar/releases/download/untagged-d618888db86c4a9e18ee/SoarSuite_9.6.6-bigbugfixrelease-Multiplatform.zip>.
