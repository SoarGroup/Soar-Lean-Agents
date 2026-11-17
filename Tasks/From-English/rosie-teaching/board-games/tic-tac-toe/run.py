"""Play tic-tac-toe: the agent is red, this environment plays blue (random legal moves under the same move rule as red's).
usage: python3 run.py [seed] [--cap N] [--games K]
The environment keeps its own board, checks every red move for legality (statement 4 of english-input.txt: a clear available
red block onto a clear location), reports blue's move on the input-link, and signals the end of the game (^game-over).
Red moves first. Prints each game's moves and result."""
import os, random, re, sys
import soar_sml as S
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import rosie_gen as R

def board_from_world(path):
    objs, rels, sets = R.read_world(path)
    h = lambda i: (f"loc-{objs[i]['row']}-{objs[i]['column']}" if objs[i]['category'] == 'location' else f"{objs[i]['color']}-{i}")
    on = {h(a): h(b) for a, b in rels.get('on', [])}
    lines = [[h(i) for i in members] for members in sets['linear']]
    stacks = {}
    for i, a in objs.items():
        if a['category'] == 'block': stacks.setdefault(a['color'], []).append(h(i))
    return on, lines, stacks

def clear(x, on): return x not in on.values()
def available(b, on): return not on.get(b, '').startswith('loc-')
def legal(color, on, locs, stacks):
    return [(b, l) for b in stacks[color] if clear(b, on) and available(b, on) for l in locs if clear(l, on)]
def move(b, l, on): on[b] = l
def three(color, on, lines):
    return any(all(any(on.get(b) == l for b in on if b.startswith(color)) for l in line) for line in lines)

def play(seed, cap):
    on, lines, stacks = board_from_world(os.path.join(HERE, 'init-tictactoerc.world'))
    locs = sorted({l for line in lines for l in line})
    rng = random.Random(seed)
    k = S.Kernel.CreateKernelInNewThread(); a = k.CreateAgent('ttt'); out = []
    a.RegisterForPrintEvent(S.smlEVENT_PRINT, lambda mid, ud, ag, msg: out.append(msg), None)
    os.chdir(HERE); a.ExecuteCommandLine('source tic-tac-toe.soar'); a.ExecuteCommandLine('watch 0')
    a.ExecuteCommandLine(f'srand {seed}')
    il = a.GetInputLink()
    turn = a.CreateStringWME(il, 'turn', 'red'); blue_n = a.CreateIntWME(il, 'blue-moves', 0); om = None; over = None
    a.Commit()
    log, result = [], None
    for step in range(cap):
        a.RunSelf(1)
        for i in range(a.GetNumberCommands()):
            c = a.GetCommand(i)
            if c.GetCommandName() != 'perform-action' or c.GetParameterValue('status') is not None: continue
            b, l = c.GetParameterValue('argument1'), c.GetParameterValue('argument2')
            ok = (b, l) in legal('red', on, locs, stacks)
            c.AddStatusComplete(); log.append(f'red  {b} -> {l}' + ('' if ok else '   ILLEGAL'))
            if not ok: result = 'illegal red move'; break
            move(b, l, on)
            if three('red', on, lines): result = 'red wins'
            else:
                bl = legal('blue', on, locs, stacks)
                if bl:
                    bb, bl_ = rng.choice(bl); move(bb, bl_, on); n = len([x for x in on if x.startswith('blue') and on[x].startswith('loc-')])
                    log.append(f'blue {bb} -> {bl_}')
                    if om: a.DestroyWME(om)
                    om = a.CreateIdWME(il, 'opponent-move'); a.CreateStringWME(om, 'block', bb); a.CreateStringWME(om, 'location', bl_)
                    a.CreateIntWME(om, 'number', n); a.Update(blue_n, n)
                    if three('blue', on, lines): result = 'blue wins'
                if result is None and not legal('red', on, locs, stacks): result = 'draw'
            if result and over is None: over = a.CreateStringWME(il, 'game-over', result.replace(' ', '-'))
        a.Commit(); a.ClearOutputLinkChanges()
        if result == 'illegal red move': break
        if a.GetRunState() == S.sml_RUNSTATE_HALTED or 'Game over' in ''.join(out) or 'success' in a.ExecuteCommandLine('print (s1 ^success *)'):
            break
    txt = ''.join(out)
    agent_view = 'success' if 'success' in a.ExecuteCommandLine('print (s1 ^success *)') else ('failure' if re.search(r'\^failure', a.ExecuteCommandLine('print s1')) else 'none')
    k.Shutdown()
    return dict(seed=seed, result=result or 'unfinished', decisions=step + 1, moves=log, agent=agent_view)

if __name__ == '__main__':
    args = sys.argv[1:]
    cap = int(args[args.index('--cap') + 1]) if '--cap' in args else 20000
    games = int(args[args.index('--games') + 1]) if '--games' in args else 1
    seed = int(args[0]) if args and not args[0].startswith('--') else 1
    for g in range(games):
        r = play(seed + g, cap)
        print(f"seed {r['seed']}: {r['result']} (agent: {r['agent']}), {r['decisions']} decisions")
        for m in r['moves']: print('   ', m)
