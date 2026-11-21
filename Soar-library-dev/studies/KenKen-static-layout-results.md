# KenKen in the ^static layout: results

19 November 2026. Library v2.43, Soar 9.6.5 (soar-sml), test set v1.37 KenKen world family (16 puzzles: seven 4x4, five 5x5, four 6x6), seeds 1-3, both layouts: 96 runs.

## What was done

- `staticize.py` (Soar-library-dev/tools/staticize) rewrote each `fam__kenken-*` program to the ^static layout, following L7-022: the static set is computed, not declared. It is every attribute the initialization gives a world object (minus ^object-handle and ^anchored), minus every attribute that a rule writes on a world object.
- Computed for KenKen. Static: type, coord, row, col, cand, cid, value, in-tuple, uses-cand, tid, pid. Mutable: alive, mark (cells), marks and gcell (puzzle).
- Rewritten condition tests: 86 (4x4), 113 (5x5), 146 (6x6). No rule writes a static attribute (the tool checks this, L7-018). Index structures (cell-info, cand-info, tuple-info) are not world objects and are left as they are.
- No library change was needed: the copy rule shares the ^static link, and KenKen's only desired (the puzzle's ^marks) is mutable.

## Correctness

- All 96 runs reach success.
- For each puzzle, the final grid is the same in all six runs (two layouts, three seeds), and it is a complete Latin square.
- Operator traces differ between the layouts (a few decisions either way) because the random choices among indifferent operators fall differently. The solutions do not differ.

## Cost

| Size | Decisions | Firings | WME changes | Seconds |
|---|---|---|---|---|
| 4x4 (21 runs per layout) | 2,125 -> 2,117 | 74,708 -> 72,786 (-2.6%) | 245,383 -> 244,320 (-0.4%) | 2.76 -> 3.13 |
| 5x5 (15 runs) | 2,614 -> 2,612 | 78,578 -> 77,537 (-1.3%) | 257,935 -> 260,482 (+1.0%) | 5.32 -> 5.99 |
| 6x6 (12 runs) | 6,816 -> 6,627 | 303,748 -> 248,679 (-18.1%) | 851,799 -> 736,518 (-13.5%) | 80.27 -> 74.96 |
| All | 11,555 -> 11,356 | 457,034 -> 399,002 (-12.7%) | 1,355,117 -> 1,241,320 (-8.4%) | 88.35 -> 84.08 |

Seconds are wall time on a shared 2-core machine; differences under about 10% are within run-to-run variation.

## Why the time barely changes

In kenken-6-2, seed 1, the look-ahead copy rule `default-state-copy-object-attributes` fires 10,344 times in the flat layout and 2,529 times in the static layout (-76%). So ^static does what it was meant to do. But the time per decision stays near 16 ms in both layouts (kernel CPU 12.3 s flat, 13.0 s static), so the copy is not where KenKen spends its time. The largest remaining costs are:

- `kenken*select*two-before-three`: about 10,000 firings, one binary preference per pair of proposed operators.
- The index elaborations (`index*cand*tuple`, `index*tuple*cand`, `index*cand`, `index*cell*cand`, `index*tuple`): about 6,500 firings. They are rebuilt in every look-ahead state, because they point to that state's world objects.
- Matching the propagation proposals (eliminate, assign, prune), which join cell-info pairs and test negated conjunctions over all candidates.

So the 4-7x slowdown of the KenKen world versions against the originals is not explained by world copying. The next places to look are the pairwise preference rule and the per-state index rebuilding.

## Per puzzle (sum over seeds 1-3)

| Variant | Decisions flat | Decisions static | Firings flat | Firings static | WME changes flat | WME changes static | Seconds flat | Seconds static |
|---|---|---|---|---|---|---|---|---|
| 4-1 | 279 | 279 | 9,394 | 9,326 | 30,832 | 31,072 | 0.37 | 0.39 |
| 4-2 | 276 | 275 | 8,503 | 8,375 | 29,822 | 30,068 | 0.30 | 0.40 |
| 4-3 | 291 | 296 | 8,940 | 8,955 | 31,594 | 32,018 | 0.39 | 0.42 |
| 4-4 | 285 | 284 | 8,441 | 8,445 | 30,180 | 30,668 | 0.35 | 0.35 |
| 4-5 | 448 | 440 | 21,383 | 19,649 | 62,719 | 59,806 | 0.74 | 0.86 |
| 4-6 | 269 | 269 | 8,805 | 8,787 | 29,782 | 30,014 | 0.29 | 0.34 |
| 4-7 | 277 | 274 | 9,242 | 9,249 | 30,454 | 30,674 | 0.32 | 0.37 |
| 5-1 | 522 | 522 | 16,017 | 15,654 | 52,013 | 52,531 | 1.08 | 1.25 |
| 5-2 | 519 | 521 | 16,162 | 16,537 | 51,459 | 52,551 | 1.05 | 1.23 |
| 5-3 | 515 | 513 | 15,511 | 15,022 | 50,581 | 50,806 | 1.03 | 1.18 |
| 5-4 | 506 | 508 | 15,009 | 14,667 | 50,485 | 50,980 | 1.01 | 1.09 |
| 5-5 | 552 | 548 | 15,879 | 15,657 | 53,397 | 53,614 | 1.15 | 1.24 |
| 6-1 | 1261 | 1260 | 60,495 | 53,413 | 161,555 | 149,345 | 10.41 | 10.95 |
| 6-2 | 2411 | 2269 | 142,277 | 102,240 | 382,335 | 292,350 | 42.18 | 36.42 |
| 6-3 | 1744 | 1701 | 65,786 | 58,457 | 192,119 | 177,662 | 17.52 | 17.88 |
| 6-4 | 1400 | 1397 | 35,190 | 34,569 | 115,790 | 117,161 | 10.16 | 9.71 |

Assisted by Claude.
