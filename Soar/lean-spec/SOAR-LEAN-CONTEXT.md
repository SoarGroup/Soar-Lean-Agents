> Copy of CLAUDE.md in `CMC/cmcsoar-release-2026-11-14.zip` (the reference release). Rename to CLAUDE.md
> in the unpacked release to have it loaded.

# CLAUDE.md — working on Soar on CMC Lean

A Lean 4 specification of the Common Model of Cognition (CMC/) with Soar 9.6 built on it (Soar/),
and `soar-lean`, a program that runs `.soar` agents on the specification so that it can be
compared with the Soar 9.6.6 release (the reference since November 14, 2026; it fixes the 9.6.5
kernel defects this project found). Read README.md for the layout and STATUS.md for where
things stand. The report, doc/Soar-on-CMC-Lean.pdf, explains the design (Section 5 for running and
testing, Section 10 for the ad hoc places, Appendix B for the user guide).

## Build

- Toolchain: Lean 4.35.0, pinned in `lean-toolchain`; elan installs it on first use. Core library
  only; no Mathlib.
- `lake build` checks every definition and proof. `lake build soar-lean` builds the program at
  `.lake/build/bin/soar-lean`. A clean build of both takes about three minutes.
- No `sorry`, no new axioms: `#print axioms` on any theorem lists only `propext`,
  `Classical.choice` and `Quot.sound`. Keep it that way.

## Compare with Soar 9.6.6

- Set `SOAR966` to the `bin/<platform>` directory of the Soar 9.6.6 suite; `tools/soarsel.py`
  then loads its Python bindings. `SOAR_VERSION=9.6.5` uses `pip install soar-sml==9.6.5`
  instead (doc/HARNESS.md).
- Run the harness with standard input closed (`</dev/null`): tests/rhslib/accept.soar reads it.
- `python3 tools/diff.py tests/<set> <options>` runs every program of a set in both and compares;
  each set needs particular options (`tools/run_all.sh` lists them). `GROUP=A tools/run_all.sh`
  runs one group. The whole regression takes under an hour with three groups in parallel on two
  cores (timings in doc/HARNESS.md).
- `SOAR_LEAN=/path/to/binary` makes the tools use another build. `ONLY=name` limits diff.py to
  matching files.
- A program `X.soar` with `X.pre.soar` and `X.pre.n` beside it is run in two agents (the first
  leaves its semantic or episodic store in a file, the second opens it); see doc/HARNESS.md.
- When a program differs:
  - `tools/firstdiff.py` finds the first decision that differs.
  - `tools/firecmp.py agent.soar N` finds the first rule firing that differs.
  - `tools/ttcmp.py agent.soar N` compares every element with its timetag (`TTRANGE=lo-hi` to
    print a range).
  - `soar-lean --wma-debug F` prints activation histories as Soar's `wma --history`;
    `--smem-debug F`, `--rete-debug F` and `--watch` print the other internals.
  - In Soar (through soar_sml): `wma --history <timetag>`, `print --internal`, `trace`,
    `preferences <id> <attr> --names`.
- doc/DIFFERENCES.md records how each remaining difference was diagnosed.

## Conventions

- Every definition that models Soar names the Soar function(s) it follows in its docstring
  (for example "Soar 9.6.5 `decide_non_context_slot`"). Citations of 9.6.5 stand where 9.6.6 did
  not change the code; where 9.6.6 fixed a defect, the docstring says "Soar 9.6.6", describes the
  9.6.5 behaviour and gives the defect number. The map doc/Soar-Lean-map.xlsx is drawn from these
  docstrings; keep them accurate when changing code.
- Mark simplifications in docstrings with `SIMPLIFIED:` and gaps with `NOT FORMALIZED:` or
  `NOT MODELED:`.
- Where Soar's behaviour is a defect, the model reproduces it when tests depend on it and says so
  in the docstring; the defect is listed in doc/Soar-9.6.5-Kernel-Defects.docx (whose section
  "Status in Soar 9.6.6" gives the commit that fixed each) and the map's Kernel defects sheet.
- After a change: `lake build`, then the regression groups the change can affect; update
  doc/results.json and rebuild the report with
  `NODE_PATH=$(npm root -g) node doc/build_soar.js doc/Soar-on-CMC-Lean.docx doc/results.json`
  (run in doc/).

## Execution speed (`@[csimp]`)

- soar-lean is compiled from the specification, but the compiler runs faster versions of some
  definitions: each `XFast` (or `XWith`, `XBy`) definition in Soar/Cycle.lean is marked
  "Execution only", proved equal to the specification's `X`, and substituted for it by an
  `@[csimp] theorem X_eq_fast : @X = @XFast`. Theorems are about `X`; only the compiled program
  uses `XFast`. A csimp lemma applies to code compiled after it, so each one sits directly after
  the definition it replaces.
- Most of these proofs are `rfl` (the fast version only computes a shared value once). If a
  change to `X` breaks one, either make the same change to `XFast` or delete the fast version
  and its lemma; never weaken the lemma.
- `Sym` and `WME` have hand-written hash functions (Soar/Syntax.lean). Any hash is lawful with
  decidable equality; but a change to them changes the iteration order of hash maps keyed by
  symbols or elements, so run the full regression after changing them.
- Incremental execution layer (November 14): indexes kept between working-memory phases live
  in `St.xi : Squash (Option WCache)` (Soar/WmIx.lean; key = the slots list). The logic cannot
  see the field (`St.with_xi`); fast versions read it through `St.withIx`, which checks the key
  (`wkeyDec`, pointer first) and falls back to the specification's computation. A fast version
  of a function that changes the slots must install the updated index with a proof (`WIx.Ok`),
  as `St.syncX` does through `St.ixStep`; any other change to the slots simply invalidates it.
  Keep the index's key the very list object stored in the state, or the pointer check fails
  and every query pays a structural comparison.
- A membership test used inside a filter must be data, not a function: a fast version
  returning `WME → Bool` is recomputed for every element by the compiled program. Use a
  squashed test with its proof, computed once and asked per element (`St.wmOracle` /
  `WmOracle.ask` for working memory, `St.slotOracle` / `SlotOracle.ask` for the slots).
- A cache pays only when the same value is asked for more than once before it changes:
  measure how often a table changes before caching what is computed from it (the timetag
  map paid only once `St.retag` stopped remaking an unchanged table; see STATUS.md).
- To find what to speed up next: `valgrind --tool=callgrind soar-lean agent.soar -d 40` and
  `callgrind_annotate --inclusive=yes`. Most time goes to recomputing working memory from
  scratch in each working-memory phase (`St.raw`, `reach`, `St.desired`, `St.ttMap`).

## Where things are

- Soar/Cycle.lean — the decision cycle, preference memory, memories' interfaces, WMA, RL hooks.
- Soar/Match.lean, Soar/MatchComplete.lean, Soar/JoinOrder.lean — the matcher, its soundness and
  completeness, and the join order.
- Soar/Rete.lean — Soar's Rete: the matcher
  and the order in which matches fire.
- Soar/Chunk.lean — chunking. Soar/SMem.lean, Soar/EpMem.lean, Soar/WMA.lean — the memories;
  Soar/Store.lean — writing and reading their files (`database file`).
- Soar/Props.lean, Soar/Seriality.lean, Soar/SMemProps.lean, Soar/EpMemProps.lean, Soar/OrderSafe.lean,
  Soar/ReorderProps.lean — theorems.
- tests/ — about 5,200 programs; `.n` files give the number of decisions.
- tests/agentlib/ — the agent library: every agent given for testing, versioned (README.md,
  CATALOG.md); `tools/agentlib.py` maintains it and `GROUP=L tools/run_all.sh` compares it.
- bugs/ — programs that show Soar 9.6.5 defects (tests/kerneldefects: those that run, against 9.6.6).
- Soar/SVS/ — the spatial visual system (README.md, Spatial visual system). Its elements are
  architecture elements with `WME.dup ≥ SVS.dupBase`; the kernel's side is in Soar/Cycle.lean
  (`St.svsCall`, `St.svsInput`, `St.svsOutput`, `St.createSubstate`, `St.removeGoalsFrom`).
  Floating-point code there follows Eigen's and libccd's order of operations exactly: change it
  only with the oracle in tools/svs/ (rebuild, rerun `G.lean` and `A.lean`, expect 0 bad).
- tests/svs, tests/svsgen, tests/svsextra, tests/svsfuzz, tests/svschunk, tests/svsenv — SVS
  programs (`GROUP=S`). SGEL from an environment (`SendSVSInput`) is `Env.svsIn` in the model,
  `K svs LINE` in an input script; avoid scenes where `closest`/`farthest` tie (heap-address order).
- tests/mapdiff/ — one program per difference found by the line-by-line review of the map (README.txt
  lists each set's options).
