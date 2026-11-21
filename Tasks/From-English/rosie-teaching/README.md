# Rosie teaching data: games and puzzles

Teaching dialogs in which an instructor taught Rosie (the Soar interactive task learning agent) 54 games and puzzles in restricted English, together with the world states the instructor set up during each dialog. This is the data published with the IJCAI 2019 work on interactive task learning of games and puzzles (Kirk & Laird, 2019); the original page, with links adjusted to this layout, is `index.html` (video example: https://youtu.be/RZUWEG-yHsI).

These differ from the other projects in `From-English` in two ways: the English is a dialog in Rosie's restricted language rather than a free description, and it is grounded in world states (`.world` files) that the instructor loads during the dialog. Twenty-seven of them have Soar agents generated from the instructor statements (16 November 2026, library v2.39): the pilot (`river-crossing-puzzles/fox-goose-bean`, `block-puzzles/tower-of-hanoi`, `board-games/tic-tac-toe`), all nine block puzzles (`block-puzzles/`; the 4- and 5-block Tower of Hanoi run but do not solve, because of the look-ahead depth limit), the four other river crossings (`river-crossing-puzzles/`; all solve their two-couple or smaller worlds with the shortest plan; the three-couple and three-pair worlds do not within 300,000 decisions) and all twelve logic puzzles (`logic-puzzles/`; 34 of 36 runs correct with library v2.39, against 14 of 36 with v2.37). Three of them (Tower of Hanoi, fox-goose-bean, KenKen) were also generated through Lean, two ways; `LEAN-PATHS.md` compares them. On 18 November 2026 agents were generated for 22 more: all side-swapping puzzles (`side-swapping-puzzles/`), all grid puzzles (`grid-puzzles/`), all chess problems (`chess-problems/`) and all solitaires (`solitaires/`); on library v2.42, 15 of them solve on every seed, 3 on some seeds, and the two knight swaps, sokoban and n-knights on none within 60,000 decisions (`PILOT.md`). 49 of the 54 dialogs now have agents; the five board games other than tic-tac-toe do not. `PILOT.md` reports the results; `tools/` holds the shared generator and checks, and `tools/rosie-language.md` how each kind of statement is read.

## Regenerated 18 November 2026

The 27 generated agents (and the Lean path A and B agents of Tower of Hanoi, fox-goose-bean and KenKen) were regenerated with the 18 Nov generators: `tools/wg.py` and `tools/convpass.py` are worldgen v22's, so every rule tests its state's or problem space's name (L3-005) and every rule group has an English comment (L3-012). See `../README.md` for the check runs.

## Files in each task folder

| File | Contents |
|---|---|
| `english-input.txt` | The instructor's statements, numbered and verbatim, with each `Load` linked to its world file; the world vocabulary (object categories, attributes, relations) extracted from the loaded world files; any world files in the folder that the dialog does not load. |
| `script.txt` | The instructor's statements as published (identical to the TEACHER lines of `dialog.txt` in all 54 tasks). |
| `dialog.txt` | The whole dialog, instructor and Rosie. |
| `dialog.html` | The dialog page, with links to the world files and pictures of the world states. |
| `init-*.world`, `fail-*.world`, `final-*.world`, `second-*.world` | World states: an initial state, examples of failure conditions, the goal state, and intermediate states. |
| `*.png` | Pictures of the world states (not available for every task). |

## World file format

Blocks separated by blank lines. An object block starts `objid N` and lists attributes one per line (`category block`, `color red1`, `shape boat1`, `row 2`, `volume 3.0`). A `predicate R` block lists pairs `a b` meaning R(a, b) (relations used: on1, below1, near1, diagonal-with1, above1, under1, left-of1, right-of1, alongside1). A `predicate-set S` block lists groups of objects, one group per line (used for `linear`: the rows, columns and diagonals of a board).

## Tasks

Statements: number of instructor statements in the script. Worlds: number of world files loaded in the dialog.

| Category | Task | Folder | Statements | Worlds |
|---|---|---|---|---|
| Grid puzzles | Sokoban | `grid-puzzles/sokoban` | 16 | 2 |
| Grid puzzles | Traveling Salesman | `grid-puzzles/traveling-salesman` | 15 | 2 |
| Grid puzzles | Simple Maze | `grid-puzzles/simple-maze` | 13 | 2 |
| Grid puzzles | Pushing Maze | `grid-puzzles/pushing-maze` | 16 | 2 |
| Grid puzzles | Eight Puzzle | `grid-puzzles/eight-puzzle` | 13 | 2 |
| Grid puzzles | Eight Puzzle v2 | `grid-puzzles/eight-puzzle2` | 13 | 2 |
| Grid puzzles | Five Puzzle | `grid-puzzles/five-puzzle` | 13 | 2 |
| Grid puzzles | Fifteen Puzzle | `grid-puzzles/fifteen-puzzle` | 13 | 2 |
| Side-swapping puzzles | Frogs and Toads | `side-swapping-puzzles/frogs-and-toads` | 17 | 3 |
| Side-swapping puzzles | 8 Men on a Raft | `side-swapping-puzzles/8-men-on-a-raft` | 17 | 3 |
| Side-swapping puzzles | Knight Swapping | `side-swapping-puzzles/knight-swapping` | 13 | 2 |
| Side-swapping puzzles | Knight Corner Swapping | `side-swapping-puzzles/4-corner-knights` | 13 | 2 |
| Chess problems | Knight's Tour | `chess-problems/knights-tour` | 15 | 2 |
| Chess problems | N Queens | `chess-problems/n-queens` | 26 | 3 |
| Chess problems | N Rooks | `chess-problems/n-rooks` | 22 | 3 |
| Chess problems | N Kings | `chess-problems/n-kings` | 18 | 3 |
| Chess problems | N Knights | `chess-problems/n-knights` | 19 | 3 |
| River-crossing puzzles | Missionaries and Cannibals | `river-crossing-puzzles/missionaries-and-cannibals` | 19 | 3 |
| River-crossing puzzles | Fox, Goose, Bean | `river-crossing-puzzles/fox-goose-bean` | 20 | 4 |
| River-crossing puzzles | Family Crossing | `river-crossing-puzzles/family-crossing` | 15 | 2 |
| River-crossing puzzles | Jealous Husbands | `river-crossing-puzzles/jealous-husbands` | 20 | 3 |
| River-crossing puzzles | Jealous Wives | `river-crossing-puzzles/jealous-wives` | 20 | 3 |
| Board games | Small Othello | `board-games/mini-othello` | 17 | 3 |
| Board games | Breakthrough | `board-games/breakthrough` | 17 | 4 |
| Board games | Tic-Tac-Toe | `board-games/tic-tac-toe` | 19 | 3 |
| Board games | Three Men's Morris | `board-games/three-mens-morris` | 21 | 3 |
| Board games | Picaria | `board-games/picaria` | 20 | 3 |
| Board games | Nine Holes | `board-games/nine-holes` | 20 | 3 |
| Marking and logic puzzles | KenKen | `logic-puzzles/kenken` | 26 | 4 |
| Marking and logic puzzles | KenKen v2 | `logic-puzzles/kenken2` | 26 | 4 |
| Marking and logic puzzles | Survo | `logic-puzzles/survo` | 26 | 3 |
| Marking and logic puzzles | Small Sudoku | `logic-puzzles/sudoku` | 24 | 3 |
| Marking and logic puzzles | Jigsawdoku | `logic-puzzles/jigsawdoku` | 24 | 3 |
| Marking and logic puzzles | Killer Sudoku | `logic-puzzles/killer-sudoku` | 29 | 4 |
| Marking and logic puzzles | Shuffle | `logic-puzzles/shuffle` | 25 | 3 |
| Marking and logic puzzles | 4 Map Coloring | `logic-puzzles/four-map-coloring` | 17 | 3 |
| Marking and logic puzzles | Kakuro | `logic-puzzles/kakuro` | 28 | 3 |
| Marking and logic puzzles | Logi-5 | `logic-puzzles/logi-five` | 24 | 3 |
| Marking and logic puzzles | Sujiko | `logic-puzzles/sujiko` | 20 | 3 |
| Marking and logic puzzles | Suko | `logic-puzzles/suko` | 26 | 3 |
| Block puzzles | Tower of Hanoi | `block-puzzles/tower-of-hanoi` | 11 | 2 |
| Block puzzles | Tower of Hanoi (4 blocks) | `block-puzzles/tower-of-hanoi-4` | 11 | 2 |
| Block puzzles | Tower of Hanoi (5 blocks) | `block-puzzles/tower-of-hanoi-5` | 11 | 2 |
| Block puzzles | Stacking Frogs | `block-puzzles/stacking-frogs` | 14 | 2 |
| Block puzzles | King Stacking Frogs | `block-puzzles/king-stacking-frogs` | 11 | 2 |
| Block puzzles | Lazy Stacking Frogs | `block-puzzles/lazy-stacking-frogs` | 14 | 2 |
| Block puzzles | Blocks World | `block-puzzles/blocks-world` | 10 | 2 |
| Block puzzles | Blocks World v2 | `block-puzzles/blocks-world2` | 10 | 2 |
| Block puzzles | Sorting | `block-puzzles/sorting` | 9 | 2 |
| Solitaires | Peg Solitaire | `solitaires/peg-solitaire` | 14 | 2 |
| Solitaires | Peg Solitaire v2 | `solitaires/peg-solitaire2` | 14 | 2 |
| Solitaires | Mahjong | `solitaires/mahjong` | 11 | 2 |
| Solitaires | Tri Peaks Card Solitaire | `solitaires/tri-peaks-solitaire` | 18 | 3 |
| Solitaires | Golf Card Solitaire | `solitaires/golf-solitaire` | 18 | 3 |

Three Men's Morris and Missionaries and Cannibals also appear in `From-English` as free-English projects (`three-mens-morris`, `mc-world`); the Rosie versions are separate inputs for the same tasks.

## What was left out of the uploaded archive

- **Empty task folders**, with no dialog or world files: `board-games/simple-risk`, `grid-puzzles/five-puzzle2`, `logic-puzzles/age-of-3-children`, `river-crossing-puzzles/manager-actor`, `solitaires/pyramid-solitaire`. They are not on the index page either.
- **Copies of another task's world files** found in six folders and not used by their dialogs. The `.world` files are byte-identical to the ones in the task they belong to, except the three frog files in fifteen-puzzle, which are earlier versions of the frogs-and-toads states without row and column attributes:
  - `grid-puzzles/sokoban`: fail-color-ken.png, fail-color-ken.world, fail-color-ken2.png, fail-color-ken2.world, final-color-ken.png, final-color-ken.world, init-color-ken.png, init-color-ken.world
  - `grid-puzzles/fifteen-puzzle`: final-frog.world, init-frog.world, second-frog.world
  - `river-crossing-puzzles/missionaries-and-cannibals`: fail-color-ken.png, fail-color-ken.world, fail-color-ken2.png, fail-color-ken2.world, final-color-ken.png, final-color-ken.world, init-color-ken.png, init-color-ken.world
  - `board-games/mini-othello`: fail-mini-sudoku.png, fail-mini-sudoku.world, final-mini-sudoku.png, final-mini-sudoku.world, init-mini-sudoku2.png, init-mini-sudoku2.world
  - `logic-puzzles/killer-sudoku`: fail-mini-sudoku.png, fail-mini-sudoku.world
  - `solitaires/peg-solitaire`: fail-tictactoerc.png, fail-tictactoerc.world, final-tictactoe2rc.png, final-tictactoe2rc.world, init-tictactoerc.png, init-tictactoerc.world
- **Editor backups** (`dialog.html~`), an older copy of the whole set (`data/teaching-data.zip`, which has earlier `dialog.html` files), and the draft files at the top of `data/` (frog and tic-tac-toe drafts, figures, `test.html`, `testCopy.html`).
