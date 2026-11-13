# Context: Soar in Lean 4 (soar-lean) and writing Soar programs

Purpose: working notes for a new session. Rename to `CLAUDE.md` in the project root to have it loaded automatically.
Paths below were valid in the session that produced this file; the sandbox is ephemeral, so re-check them.

## 1. Standing preferences (from the user, John Laird)

- Strictly professional tone; no expressions of compassion or sympathy.
- Slides: no font smaller than 20 pt in boxes/text, except citations.
- Progress updates about every 30 minutes on long jobs. Proceed without asking for confirmation unless a decision is irreversible.
- Documents the user will keep or share: deliver as files (.docx where Word is requested) in `/mnt/user-data/outputs/`.

## 2. Project layout and build

- Project: `/home/claude/cmcsoar` (Lean 4.35.0). Toolchain: `export PATH=/home/claude/cmc/dl/lean-4.35.0-linux/bin:$PATH`.
- Build: `lake build` (library) and `lake build soar-lean` (executable at `.lake/build/bin/soar-lean`).
- Main modules: `Soar/Syntax.lean`, `Soar/Cycle.lean` (decision cycle: `St.cycle`, `St.runN`), `Soar/Conform.lean` (CMC instance: `soarArch`, `cmcStep`, `runCMC`), `Soar/Seriality.lean` (`cycle_unique` and piece lemmas), `Soar/EpMem.lean`, `Soar/SMem.lean`, `Soar/WMA.lean`, `Soar/Parse.lean`, `Soar/Props.lean`, `Main.lean`. CMC framework in `CMC/` (`CMC.Proc`, `CMC.Meta`).
- Proved: one CMC cycle of the Soar instance equals `St.cycle`; n cycles equal `St.runN` (the `St.run` equivalent without `rlHalt`).
- Lean lemma names that exist in this version: `contains_insert`, `getElem?_insert`, `getD_eq_getD_getElem?`, `contains_eq_isSome_getElem?`, `UInt64.toNat_sub`, `UInt64.toNat_ofNat'`. Names like `getD_eq_getD_get?` do not exist. `List.enum` is defined in Syntax.lean as `zipIdx.map swap`. `Nat.iterate` / `^[n]` were unavailable (use structural recursion). Use `CMC.Proc.exec`, not the ambiguous `exec`. The dedup loop name is `eraseDupsBy.loop`.
- Proof-writing lessons: after `split`, `extract_lets` fails (use `rename_i`, hypothesis name last); a `split <;> rfl` timeout was fixed with `generalize`; timeouts can come from a wrong let-name count.

## 3. Running soar-lean

```
soar-lean FILE.soar [-d N] [--wm] [--watch] [--rl] [--rl-values F] [--trace-file F] [--wm-file F] [--hints F]
```
- Runs N decision cycles (default 100), stopping at `halt`. Prints the decision trace, then `--- write output ---` and the agent's `write` output.
- `--wm --wm-file F` dumps working memory after the run. Format: `<id> <attr> <value>`. Identifiers are renumbered (`#IDn`), and symbolic names print as `|C0|`. A state's own contents can be listed by filtering on its id (find it with `grep "impasse"`).
- No interactive commands (`run`, `print`) are available; use `-d` and `--wm`.
- Supports `source`, `pushd`, `popd`, `cd` in the agent file.
- Speed: soar-lean is a verified interpreter, not an optimized one. Rules with several joins over many working-memory elements are slow; measure before assuming real Soar behaves the same. No result in this file was checked on real Soar 9.6.x unless stated.

## 4. Regression harness (Lean work)

- Scratchpad: `/tmp/claude-0/-home-claude/db317edd-fb01-59c1-9f84-dfa0d94d465f/scratchpad`. Scripts: `rall.sh BIN TAG`, `par5.sh` groups, `tm.sh BIN` micro-timer. Binaries `x54`…`x57-bin` (`x57` current). Results land in `rNN-done.txt`. Wait on long runs with an until-loop monitor, not sleeps.
- Full regression takes roughly 925–980 s (machine load varies); it was 1318 s before the speed work.
- Known differences against Soar 9.6.5: AlphabetAgentAllOn and f014 (known). f229 and f299 differ by memory address (defect 4) and are flaky on the Soar side.
- Review work (October 31): S3, S13, S20–S28, most of P2 and the dead-code items are done; the full regression shows only the known differences. Still open: the other fold inductions (SMemProps, EpMemProps), `rlUpdate_frame`, `calcSpread_content`, the `Pat.binds`/`Pat.eqVars` merge, some docstring fixes. Binaries `x59`–`x63`; `x63` is current (full regression: only the known diffs). Proved on November 1: matcher completeness for negated conjunctions nested to any depth.

## 5. Writing Soar programs that run correctly (lessons from Three Men's Morris)

Race and ordering
1. Rules that derive state attributes by negation (`-^mobile`, `-^winner`) race against the rules that derive the thing negated. A `halt` or a numeric value fired in the same wave can be wrong. Use negated conjunctions `-{ ... }` over the raw facts, and end the game with a `finish` operator rather than a halt rule on a derived attribute.
2. A rule that must wait for derivations to settle can use staged markers: `stage1` derived from the post-move condition, `stage2` from `stage1`, and the negation-based evaluation rule requires `stage2`.
3. A rule that tests `^operator` and creates a wme on the state is treated as an operator-application rule and may not fire in the lookahead after the operator is retracted. Test `^look-ahead-operator <lo>` instead.

Default selection space (`selection.soar`, 74 productions, extracted from `water-jug-lookahead.soar` in `soardbg/PerformanceTests/TestAgents/`)
4. Tie impasse leads to a `selection` substate that proposes `evaluate-operator`; the lookahead substate copies the state through `^problem-space`. The task must supply `^desired <d>` (with `^better higher` for numeric comparison) and set `^numeric-value`, `^success` or `^failure` on the lookahead state.
5. Problem-space object needs: `^default-state-copy yes`, `^all-attributes-at-level one` (without it, constants such as `turn` are not copied when `^two-level-attributes` is set), `^two-level-attributes <att>` for attributes holding objects that change, and `^dont-copy <att>` for every derived (i-supported) attribute, or stale o-supported copies appear.
6. Values returned through `evaluate-operator*elaborate*numeric-evaluation*from-subgoal` need the lookahead state to have `^numeric-value <v> ^desired <eb>`.
7. The default `tried-tied-operator` is o-supported and persists. Gate the task's proposals with `-^tried-tied-operator <t>` to stop nested ties.
8. The lookahead substate shows `^impasse no-change ^quiescence t` from creation, before the operator has applied, so `^quiescence t` alone does not mean the move is done. Condition on the post-move state (for example `^turn` flipped).
9. The lookahead state is evaluated at the end of its search, so "evaluation after one move" is: the mover's move applied, the turn flipped, derived facts settled.
10. Pointer sharing: with `^two-level-attributes occ`, objects under `occ` are duplicated, but their attribute values that are not themselves duplicated (for example `^pos <cell>`) are copied as pointers. Static geometry reachable only through such pointers is not copied (verified with a working-memory dump).

Authoring practice
11. Generate repetitive rules with a Python script (`gen.py`, `gen2.py`); it avoids transcription errors, but check format-argument order (a swapped argument order corrupted the board once).
12. Build a referee in Python that replays the agent's printed moves and checks legality and the declared result; add directed position tests (winning move, forced block) and a randomized test against a reference evaluator that scores moves the same way. Give the generator an optional start position so positions can be tested directly.
13. Start with `chunk never` unless chunking is under study.

## 6. Three Men's Morris artefacts (for reuse as a template)

- Option 1 (`three-mens-morris.soar` from `gen.py`, 336 rules): one rule per cell, line and move. Full game 7.5 s on soar-lean.
- Option 2 (`morris2.soar` from `gen2.py`, 53 rules): cell objects with `^id ^x ^y`, direction links, `^adj`, shared by pointer; occupancy objects `^pos ^owner`; player objects `^name ^opponent ^remaining`; derived `^moving` / `^placing` flags. Full game 45.6 s on soar-lean.
- Both: legal games confirmed by `referee.py`, 0 failures in 40 random positions (`battery2.py`), winning moves taken in the directed tests.
- Rules implemented: 3×3 board, 3 pieces each placed alternately, then moves along orthogonal neighbours plus every point to the centre; three in a line wins at once; a blocked player loses in the movement phase; draw at 30 plies.
- Development time, option 1: about 17 min (read 5, write 4, first run 1, debug 7, verify 3 of runs). Option 2: about 22 min.
- Not yet done: a run on real Soar (the `soar_sml` cross-check), a chunking-on run, and a variant where one side plays randomly.

## 7. Other deliverables from this work (in `/mnt/user-data/outputs/`)

`cmcsoar.zip`, `Soar-on-CMC-Lean.docx` / `.pdf` (55 pages), Remaining-Work, Code-Review, Kernel-Defects and CIC-Notes documents, the xlsx map, `Morris-Soar-Report.docx`, `Morris-Soar-Summary.docx`.
