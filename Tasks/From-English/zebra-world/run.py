"""Run the five-houses agent.  Usage: python3 run.py [seed] [soar command ...]
Prints the deductions, the elimination matrix, the answers, decisions and CPU time."""
import soar_sml as S, os, re, sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
seed = sys.argv[1] if len(sys.argv) > 1 else '1'
k = S.Kernel.CreateKernelInNewThread(0)
a = k.CreateAgent('zebra')
out = []
a.RegisterForPrintEvent(S.smlEVENT_PRINT, lambda mid, ud, ag, msg: out.append(msg), None)
print(a.ExecuteCommandLine('source zebra.soar').strip().splitlines()[-1])
for c in ['output agent-logs 1 off', 'watch 0', 'srand ' + seed] + sys.argv[2:]:
    a.ExecuteCommandLine(c)
for _ in range(5):   # the selection-world library interrupts once when the desired is achieved
    a.ExecuteCommandLine('run ' + __import__('os').environ.get('CAP', '20000'))
    if 'halted' in ''.join(out): break
st = a.ExecuteCommandLine('stats')
print(re.search(r'(\d+) decisions', st).group(0), '|',
      re.search(r'Kernel CPU Time:\s+[\d.]+', st).group(0))
txt = ''.join(out)
print('\n'.join(l for l in txt.splitlines() if True))
k.Shutdown()
