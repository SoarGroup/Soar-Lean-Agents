"""batch_settings.py ROOT KIND OUT.jsonl [--only fam,...]
Every variant in ROOT/list.txt under three learning settings: chunk never (1 episode), chunk only and chunk always
(2 episodes: run, init-soar, run again), seeds 1-3, through run2.py --chunk. KIND = original | world-lean | ...
Caps and time limits from ROOT/caps.json; a 3 GB memory limit per run. Used for
the English-derived agents (run3.py: run2.py plus the world-convention end test)."""
import sys, os, json, subprocess, resource, concurrent.futures as cf
root, kind, outp = sys.argv[1:4]
only = sys.argv[sys.argv.index('--only')+1].split(',') if '--only' in sys.argv else None
L = [l.split() for l in open(os.path.join(root, os.environ.get('LIST', 'list.txt'))) if l.strip()]
if only: L = [x for x in L if x[0] in only or x[1] in only]
C = json.load(open(os.path.join(root, os.environ.get('CAPS', 'caps.json'))))
def caps(v):
    x = C['variants'].get(v, {})
    return x.get('cap', C['default_cap']), x.get('time_limit_s', C['default_time_limit_s'])
RUN2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run3.py')
jobs = [(f, v, ch, ep) for f, v in L for ch, ep in (('never', 1), ('only', 2), ('always', 2))]
def lim(): resource.setrlimit(resource.RLIMIT_AS, (3 << 30, 3 << 30))
def go(j):
    f, v, ch, ep = j; d = os.path.join(root, f, kind, v); cap, tl = caps(v)
    base = dict(family=f, variant=v, setting=ch, cap=cap)
    if not os.path.isdir(d): return dict(base, error='missing')
    try:
        r = subprocess.run([sys.executable, RUN2, d, v + '.soar', '--seeds', '1-3', '--episodes', str(ep), '--cap', str(cap), '--chunk', ch],
                           capture_output=True, text=True, timeout=tl, preexec_fn=lim)
        seeds = [json.loads(l) for l in r.stdout.splitlines() if l.startswith('{')]
        return dict(base, seeds=seeds, rc=r.returncode, stderr=r.stderr[-300:])
    except subprocess.TimeoutExpired: return dict(base, error=f'timeout ({tl} s)')
with cf.ThreadPoolExecutor(int(os.environ.get('J', 2))) as ex, open(outp, 'w') as o:
    for res in ex.map(go, jobs): o.write(json.dumps(res) + '\n'); o.flush()
