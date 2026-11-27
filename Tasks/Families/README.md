# Task families: originals and world versions (15 November 2026)

68 task agents in 14 families (the blind round trip set of step 6). For each: `<family>/original/<variant>` (the original Soar program) and `<family>/world/<variant>` (the same task rewritten to the world conventions, ported to the shared library v2.32). Unpack this zip in `Tasks/`; the world versions load `Soar/soar-library` through `../../../../../Soar/soar-library`, so it must be v2.32.

`Families-Results.xlsx`: per variant, seeds solved, task rules, decisions, production firings, chunks, WM changes, original and world (sheet Comparison); per-seed rows (sheet Per seed). `run.py` and `list.txt` are the harness (python3 run.py DIR FILE.soar --seeds 1-3 --episodes 1 --cap 3000; needs the Soar 9.6.6 Python bindings on PYTHONPATH).

## Method
World versions: the Direct-World rewrites of the blind round trip (original Soar rewritten to the conventions; no English intermediary), loaded from the shared library instead of the early-November library copy, with object handles tested with `$` (1623 tests) and `^flags` changed to `^flag-override`. One stale `excise` of a removed library rule was deleted (blocks-world-epmem). Seeds 1-3, one episode, cap 3000 decisions (80000 count-in-substate). Means are over seeds that solved.

## Results (Soar 9.6.6, library v2.32)
- 49 variants solved on all seeds by both; 10 solved by neither (the originals also fail: arithmetic x5 and fifteen-puzzle, knights-6/8, mac, mac-rl, which are incomplete or need an environment); 3 where the world version solves more (blocks-world-look-ahead 3/3 vs 2/3, water-jug-look-ahead 3/3 vs 2/3, mac-look-ahead 3/3 vs 0/3); 6 where it solves fewer (kenken-4-5, 6-1, 6-2, 6-3, eight-puzzle-expected-value, water-jug-look-ahead-rl).
- On the 49: task rules +10% median (world 1.10 x original; more rules, since objects, relations and desireds are explicit); decisions about equal (median 1.02 x; blocks-world-epmem, eight-puzzle and water-jug-tie-chunk take 2.6-2.7x more, blocks-world-rl 0.3x); production firings 2.7x median (the library rules); chunks 370 vs 234 in total.

## Findings
1. **Library defect, fixed in v2.32.** `selection-world*apply*world*applied-count` (and `*first`) also fired in operator no-change substates that share the real world. The top state and the substate each rewrote the one `^counted-operator` on the world, without end (max-elaborations on every decision, with chunking off too). Six world variants looped on v2.30. v2.32 keeps the count local to the state: the top state keeps it on the world, each substate keeps its own on the substate (from zero, never shared, even in the same problem space). Test set v1.27: 296 pass, results unchanged. (An intermediate v2.31, counting in the top state only, undercounted operators applied in substates and was replaced.) The substate count is not part of any stamp yet.
   Cost: the nine hierarchical variants take more decisions on v2.32 than on v2.31 and the originals (blocks-world-hierarchical 63 vs 43/42, hrl-3level 115-141 vs 79, hanoi-mea 59 vs 48, water-jug-hierarchy +30%); cause not identified.
2. **Kenken (open).** The world versions of kenken-4-5 and 6-1..6-3 reach "task has failed" on some seeds (constraint propagation commits before elimination finishes; the failure is the same with chunking off and with v2.30), where the originals solve all seeds. Not yet diagnosed.
3. Original programs that fail are unchanged by the port; the 10 variants above were not repaired.

## Search settings (16 Nov 2026, library v2.34)
Every world variant was run under four search settings (operator or tie-impasse depth, each with and without `cost-metric unit` plus `optimize true`), seeds 1 to 3, cap 3000, and the setting that solves every seed with the best plan and the fewest decisions was kept (probe_settings.py; Soar-library-dev/docs/Search-Settings-Intake-Checklist-v1.md). Five variants now set `^iterative-step tie-impasse` in their `^flag-override` (a comment on the line gives the numbers): kenken-4-5 (3/3 seeds solved, against 2/3), kenken-6-1 (3/3 against 1/3), kenken-6-2 (3/3 against 1/3), kenken-6-3 (3/3 against 2/3), blocks-world-look-ahead (189 decisions against 409, same 3 moves). All other variants are best or equal on the library defaults. water-jug-look-ahead keeps operator depth: under tie-impasse its look-ahead runs past the depth bound (Soar-library-dev/findings/FINDING-tie-impasse-unbounded-continuation.md).


## 25 November 2026: redundant object tests removed, matching hints added (families-world-lean-2026-11-25.zip)

familygen (SoarLean-2026-11-25b-release.zip) makes two changes to every variant; nothing else in the rules changes.
- **World-Conventions L3-104.** A rule that binds an object as an argument of a relation it tests on the world no longer
  also tests `(<w> ^objects.object <x>)` (82 rule files). The library copies relations into look-ahead worlds through
  the copy map, so the arguments are always objects of that world. Example, kenken drop-tuple:
  `(<w> ^objects.object <t> <x> ^in-tuple <it>)` becomes `(<w> ^in-tuple <it>)`.
- **World-Conventions L11-009.** `_firstload.soar` ends with `production optimize-attribute` lines: `object` (the
  objects of the initialize rule) and every attribute a rule adds to `<w>` (its values on `<w>` in the initialize rule,
  at least 2), e.g. kenken-6-1: object 392, in-tuple 411, has-cand 216.

Runs, library v2.47, seeds 1-3, one episode, cap 3,000 (knights 40,000), 300 s, against the 23 November variants:

| Setting | Seeds solved (before -> now) | CPU, all variants | Variants with identical decisions |
|---|---|---|---|
| chunk never | 171 -> 171 | 157 -> 162 s | 47 / 67 |
| chunk only | 174 -> 174 | 146 -> 161 s | 47 / 67 |
| chunk always | 168 -> 168 | 369 -> 411 s | 47 / 67 |

The 20 that change are the same under all three settings (eight-puzzle and eight-puzzle-expected-value, the 16 kenken
variants, knights-6 and knights-8), so the hints change firing order, not what is learned. L3-104 alone changes no
decision. kenken-6-2 takes more decisions (1,343 / 1,485 / 975 vs 735 / 862 / 1,096; 46 s vs 27 s CPU); knights-6 the
same decisions in 22 s instead of 10 s; knights-8 58 s instead of 76 s. The hints without L3-104 made the 6x6 KenKen
variants 15-70 times slower (kenken-6-4 did not finish in 300 s): the in-tuple declaration made the reorderer join
`^objects.object <t> <x>` before `^in-tuple` in drop-tuple.

KenKen: 12 of the 16 variants are solved by the monotonic operators alone (2 decisions outside the top state);
kenken-4-5, 6-1, 6-2 and 6-3 get stuck, choose a cell with two candidates and resolve the guess tie by look-ahead.

## 25 November 2026 (evening): families-world-lean-2026-11-25b.zip and the standard-Soar comparison

familygen (SoarLean-2026-11-25c-release.zip) now also counts relation conditions with several values on one attribute
(`^at <rt> <rk>`) when leaving out redundant object tests (L3-104): 87 rule files differ from the unconverted rules
(82 in the 25 November zip; the 5 more are eight-puzzle move-tile rules). wg.py's version of the pass gives the same
files.

`Tasks/Families standard Soar vs World (25 Nov 2026).xlsx` compares the original programs with these World variants:
library v2.47, seeds 1-3, chunk never (1 run), chunk only and chunk always (2 runs), caps from caps.json. A pair is a
variant under one setting and run; it is compared when both versions solve all 3 seeds and neither takes more than
1.5 times the decisions of the other (238 pairs from 58 variants; 102 excluded). Over the compared pairs, World /
standard (ratio of means): decisions 0.99, production firings 3.4, WM changes 2.2, chunks 2.0, kernel CPU time 10.5
(medians per pair: decisions +1%, firings +139%, WM changes +114%). 238 of 238 pairs differ by more than 20% on at
least one measure, mostly firings (226) and WM changes (235). World runs of arithmetic (never, only),
arithmetic-v5 and arithmetic-smem-chunk (never, only) were not made: the standard programs do not solve them.

## 25 November 2026 (late evening): arithmetic cut back to 100 problems (families-world-lean-2026-11-25c.zip)

JL: at most 100 problems per arithmetic variant. arithmetic, arithmetic-v5 and arithmetic-smem-chunk (10,000 before),
arithmetic-smem (1,000) and arithmetic-smem-learn (2,000) now solve 100 problems, in the original programs
(`original/<variant>/<variant>/initialize-arithmetic.soar`, `^count 100`) and in the World variants (Arithmetic.lean,
SoarLean-2026-11-25d-release.zip). Library v2.47, seeds 1-3, every learning setting: all five solve every seed in both
versions (before, the originals of arithmetic, arithmetic-v5 and arithmetic-smem-chunk failed with chunk never and only
at 150,000 decisions); decisions 2,665-4,276 with chunk never or only, 1,101-3,399 with chunk always; World CPU
1.3-2.5 s per run for arithmetic and arithmetic-v5, at most 0.5 s for the others. caps.json: 10,000 for the five.
The comparison workbook of 25 November used the old counts; these variants enter it when it is next rebuilt.


## 25 November 2026: agents from the English descriptions (`<family>/english/<task>/`)

A third version of nine families, written from each family's `human-description.md` through a WorldSpec description (path B, SoarLean release 2026-11-25d), without reading the Soar rules of the original or world versions. The original initialize rules were read only for initial states the English leaves open (hanoi target peg C; eight-puzzle start and target). One agent per family. Each folder has `english-input.txt`, `<task>-spec.py` (with the assumption ledger), the `.world` file, `-worldspec.json` and `.lean`, the generated rules, the loader and a README with results. Tools: `english-tools/` (run3.py = run2.py plus the world-convention end test; batch_settings3.py; build.sh).

Results (library v2.47, seeds 1-3, chunk never / only / always): hello-world, counting (0 to 100), pyramid (base 5, height 10, sum 0), towers-of-hanoi (7 moves with learning, 8-9 without), blocks-world (3 moves), eight-puzzle (5 moves), water-jug (4 steps) and wizards (C states white at the third turn) solve every seed in every setting. missionaries-cannibals did not finish in 80 minutes (iterative deepening to depth 11).

Not built: arithmetic (random problems, many in a row), kenken (products and quotients), left-right (reinforcement learning), knights (enumerating and counting all tours), tictactoe (an opponent). WorldSpec could not state these directly; now To-do row 45 (arithmetic and kenken can use the new arithmetic).

Findings, all addressed in SoarLean-2026-11-26-release.zip (JL): (1) WorldSpec had no subtraction (water-jug kept negated copies of its amounts); it now has minus, times, quot and rem, and water-jug uses minus. (2) A first missionaries-cannibals with six person objects stated losing banks with negated conditions; its learned rules dropped the negations and rejected every crossing at the start. (3) The world-file reader dropped a trailing `1` from values (taken as a Rosie sense number), so `d1` silently became `d`; now only after a word of two or more letters, and objects sharing a handle are rejected. (4) An effect using a variable bound only in an operator's preconditions made a new identifier on every firing (the agent looped). Path A (Lean `Task.wellFormed`) already rejected (2) and (4); path B now makes the same checks, so Tower of Hanoi and blocks world were rewritten to test derived relations (top, can-take, clear) and Hello World a property's value; results as before (Tower of Hanoi now 20,700-35,400 decisions with learning, 43,000-55,000 without, 7-8 moves).

## 27 November 2026: families-world-lean-2026-11-27.zip (library v2.48)

familygen of SoarLean-2026-11-27-release.zip. 167 of the 473 files change, by World-Conventions L7-028 (static objects
get `^static true`; relations no rule changes are declared with `^share-relation`) and L9-011 (operators with no
preconditions are proposed with `^pre-conditions-satisfied true`); no family meets the `^fixed` criteria (L7-022).
The English-derived agents (`<family>/english/`) were regenerated the same way (static marks and L9-011 only).
Runs, library v2.48, seeds 1-3, caps from caps.json, 300 s per variant and setting (`Tasks/Results on library v2.48
(27 Nov 2026).xlsx`): own settings and chunk only (2 episodes) 378 successful episodes each; chunk never, only and always
identical in results and decisions to the same variants on v2.48 before its row 12 fix. English-derived agents: eight
of nine solve every seed in every setting; missionaries-cannibals does not finish in 300 s. Superseded:
families-world-lean-2026-11-25c.zip.
