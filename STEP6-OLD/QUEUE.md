# Step 6 queue (7 Nov 2026, 14:10, revised)

Task agents in the corpus: 262. Done: 91. Dropped earlier: testing-only 18, trivial 15. Skipped now: 83. Remaining: 55.

Rules (JL, 7 Nov): skip agents with ^world/^scene when other versions exist; skip the Pyramid instruct agents; skip agents that need an external environment; Towers of Hanoi limited to five disks on three pegs. An agent is skipped for I/O only if it reads the input-link; agents that keep their own model on the output-link (the Blocks World gripper) or only write to it are kept.

Order (JL, 7 Nov): after KenKen, families with the fewest remaining first, Blocks World last: Tic-Tac-Toe / games → NEW: RL toy tasks → Episodic memory → Graph search → Towers of Hanoi → Arithmetic → Blocks World.

## Tic-Tac-Toe / games — 1
TicTacToe V1 (17)

## NEW: RL toy tasks — 1
left-right V1 (11)

## Episodic memory — 1
count-epmem V1 (49)

## Graph search — 2
graph-search-smem V1 (156), graph-search-smem V2 (136)

## Towers of Hanoi — 11  (five disks, three pegs)
tower-of-hanoi-search V1 (133), towers-of-hanoi V1 (21), towers-of-hanoi V2 (18), towers-of-hanoi-fast V1 (18), towers-of-hanoi-fast V2 (18), towers-of-hanoi-faster V1 (13), towers-of-hanoi-faster V2 (13), towers-of-hanoi-no-ops V1 (9), towers-of-hanoi-recur V1 (18), towers-of-hanoi-recursive V1 (21), towers-of-hanoi-recursive V2 (21)

## Arithmetic — 11
addition V1 (33), arithmetic V3 (99), arithmetic V4 (104), arithmetic V9 (153), arithmetic V10 (156), arithmetic V11 (149), arithmetic-save V1 (84), arithmetic-solve-problem V1 (98), multiplication V1 (41), subtraction V1 (33), algebra V3 (176)

## Blocks World — 28
BW-Hierarchical V1 (51), BW-Hierarchical V2 (51), BW-Hierarchical-LA V3 (157), block-world-HRL-3level V1 (121), blocks-world-hierachical-lookahead V2 (157), blocks-world-hierachical-lookahead V3 (155), blocks-world-hierachical-lookahead V4 (164), blocks-world-hierachical-lookahead V5 (169), blocks-world-hierachical-lookahead V6 (157), blocks-world-hierarchical V2 (51), blocks-world-hierarchical V3 (51), blocks-world-hierarchical V4 (51), blocks-world-hierarchical V5 (51), blocks-world-hierarcical-RL V2 (69), BW-LA-state-eval V1 (103), BW-LA-state-eval V2 (102), BW-Op-Subgoal-RL V1 (23), BW-RL V1 (12), BW-RL V2 (12), blocks-world-HRL V1 (22), blocks-world-RL V2 (12), blocks-world-epmem V2 (120), blocks-world-lookahead-state-evaluation V2 (103), blocks-world-lookahead-state-evaluation V3 (103), blocks-world-operator-subgoaling-RL V2 (23), blocks-world-operator-subgoaling-RL V3 (23), blocks-world-operator-subgoaling-RL V4 (23), blocks-world-operator-subgoaling-lookahead V2 (23)

## Skipped
- read the input-link (the task needs an environment) (28): Robot V1, advanced-move V1, advanced-move V2, avoider-robot V1, collect-cubes V1, count-blocks V1, cozmo V1, cozmo-save V1, cozmo-save2 V1, cube-stack V1, event-comprehension V1, flat-all V1, flat-phase V1, flat-phase-regions V1, flat-smart V1, hrl-full-max V1, hrl-nav V1, hrl-nav-general V1, hrl-nav-max V1, hrl-nav-max-general V1, johns-eater V1, jump-and-move V1, laird-dudo V1, move20 V1, robot-RL V1, robot-hierarchical-pickup V1, robot-move-turn-pickup-block V1, robot-pickup-block V1
- need an external environment (simulator) (33): Johnbot V1, MOUTBot V1, UCBot V1, agent_1 V1, buttons V1, clean-house-9-4-09 V1, clean-house-new V5, dice-easy V1, dice-hard V1, dice-harder V1, dice-hardest V1, dice-medium V1, dice-model-bot-new V1, dice-probabilities-true V1, discrete-agent V1, mummymaze1p-horiz.xbiduy V1, mummymaze1p-hreform.d9du2o V1, mummymaze1p-hv.d0mkoc V1, mummymaze1p-hv.ebd8g3 V1, mummymaze1p-hvrope.6ho6jr V1, mummymaze1p-hvrope.m9buyr V1, newmummy-jel V1, simple-robot-with-avoidance-line V1, simple-robot-with-avoidance-patrol-lab V1, simple-robot-with-avoidance-rectangle V1, simple-robot-with-avoidance-square V1, simple-robot-with-avoidance-star-plan V1, taxi V2, taxi-hrl V1, taxi-hrl-oracle V1, taxi-mapping V1, taxi-rl V1, taxi-rl-oracle V1
- ^world / ^scene on the state (other versions exist) (7): blocks-world-RL V3, blocks-world-operator-subgoaling-RL-world V1, blocks-world-opsub-lookahead V1, blocks-world-opsub-lookahead V2, blocks-world-opsub-lookahead V3, interpret-game-state-tower-change V1, opsub-core V1
- Pyramid instruct agents (JL: skip the rest of Pyramid) (10): instruct V1, instruct V2, instruct V3, instruct V5, instruct V6, instruct V7, instruct V8, instruct V9, instruct V10, instruct-01-03-05 V1
- JL, 7 Nov 14:05 (5): taxi V1, patrol V1, mummy-draw V1, mummy-draw-num V1, mummy-monitor V1
