# Three Men's Morris: VisualSoar project

Open `ThreeMensMorris.vsa.json` in VisualSoar (File > Open Project). The agent plays Three Men's Morris
against itself: three pieces each, placement then movement along adjacent points, three in a line wins,
a draw after 30 plies. Move choice is one-ply look-ahead through Soar's default selection space.

Layout
- `_firstload` : `chunk never`
- `selection/` : the 74 default selection-space productions (from the water-jug look-ahead agent)
- `elaborations/` : problem-space, phases, winner, draw, threats, stages
- `lookahead/` : evaluation of look-ahead states
- operators: `initialize-morris`, `place`, `move`, `finish`
- Datamap: 22 vertices; the static `geometry` cells are shared by pointer and not copied into look-ahead states.

Run: source `ThreeMensMorris.soar` in the Soar debugger (or `soar-lean ThreeMensMorris.soar -d 400`).
A full game takes about 40 s on soar-lean. The project was not opened in VisualSoar or run in Soar 9.6.5 itself.
