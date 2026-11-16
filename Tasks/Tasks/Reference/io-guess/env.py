"""Environment for io-guess: a secret number from 1 to 100.
usage: python3 env.py SECRET [FILE]   (needs the Soar 9.6.6 Python bindings on PYTHONPATH)
Per environment turn: wait for a command ^io.output-link.guess.value, answer on the input link
(next ^turn, ^feedback higher|lower|correct, ^game-over true when found), mark the command ^status complete."""
import sys, os
import Python_sml_ClientInterface as sml
secret = int(sys.argv[1]); load = sys.argv[2] if len(sys.argv) > 2 else 'io-guess.soar'
kernel = sml.Kernel.CreateKernelInCurrentThread(); agent = kernel.CreateAgent('io-guess')
r = agent.ExecuteCommandLine('source ' + load); assert 'rror' not in r, r
agent.ExecuteCommandLine('srand 1')
il = agent.GetInputLink()
turn = agent.CreateIntWME(il, 'turn', 1); fb = agent.CreateStringWME(il, 'feedback', 'start'); over = None
agent.Commit(); n = 1; decisions = 0; guesses = []
while decisions < 500:
    agent.RunSelf(1); decisions += 1
    if agent.GetRunState() == sml.sml_RUNSTATE_HALTED: break
    for i in range(agent.GetNumberCommands()):
        c = agent.GetCommand(i)
        if c.GetCommandName() != 'guess' or c.GetParameterValue('status'): continue
        v = int(c.GetParameterValue('value')); guesses.append(v); n += 1
        f = 'correct' if v == secret else ('higher' if v < secret else 'lower')
        agent.Update(turn, n); agent.Update(fb, f)
        if f == 'correct': over = agent.CreateStringWME(il, 'game-over', 'true')
        c.AddStatusComplete()
    agent.Commit()
halted = agent.GetRunState() == sml.sml_RUNSTATE_HALTED
print(f'secret {secret}: guesses {guesses}, decisions {decisions}, halted by the environment signal: {halted and over is not None}')
kernel.Shutdown()
