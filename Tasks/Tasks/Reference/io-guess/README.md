# io-guess: reference agent for environment I/O (standard conventions)

The smallest agent that reads an input structure, issues a command, waits for `^status complete`, and halts on the environment's signal. It pins the I/O pattern for generated agents (issue 5 of Soar-Lean-Agents) and is a test case for the generator.

- `io-guess.soar`: the agent (classic task rules, no library needed). Rule names carry the convention (IO-003, -005, -006, -008, -010, -012, -013, -014, -017) in the comment at the top.
- `env.py`: the environment, a secret number from 1 to 100. `python3 env.py SECRET` (Soar 9.6.6 Python bindings on `PYTHONPATH`). Per turn: reads `^io.output-link.guess.value`, answers `^feedback higher|lower|correct` and the next `^turn` on the input link, marks the command `^status complete`, sets `^game-over true` when found.

Tested, secrets 1, 37, 50, 64, 99, 100: found in 1 to 7 guesses (binary search), 5 to 26 decisions, halted by the environment's signal each time.

What the agent shows, and what a generator must reproduce:
1. Input is copied to the state by elaborations that test `^io.input-link` (constants, so no aliasing); every other rule tests the state.
2. One command per environment turn; the next waits for the next `^turn`.
3. The command is created by an operator application, and removed by a second operator once the environment marks it complete.
4. The agent halts on `^game-over`, which the environment sets; the agent has no goal of its own.
5. Competing proposals are indifferent (`+ =`); the stop operator is best (`+ >`). Without indifference the first run stalled in a tie impasse.
