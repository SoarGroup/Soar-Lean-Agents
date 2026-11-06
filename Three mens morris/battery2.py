import random,subprocess,re,sys,referee as r
from battery import first_move
random.seed(int(sys.argv[1]) if len(sys.argv)>1 else 1)
N=int(sys.argv[2]) if len(sys.argv)>2 else 40
def legal(bd,p,rem):
    return r.moves(bd,p,rem)
def apply(bd,mv,p):
    nb=list(bd)
    if mv[0]=='place': nb[mv[1]]=p
    else: nb[mv[1]]='.'; nb[mv[2]]=p
    return nb
def score(bd,mv,p,rem):
    q='O' if p=='X' else 'X'
    nb=apply(bd,mv,p); nrem=dict(rem)
    if mv[0]=='place': nrem[p]-=1
    if r.won(nb,p): return 100
    ql=r.moves(nb,q,nrem)
    if nrem[q]==0 and not ql: return 100   # opponent blocked
    for m in ql:
        if r.won(apply(nb,m,q),q): return -100
    return 2 if nb[4]==p else 0
def gen():
    while True:
        phase=random.choice(['place','move'])
        if phase=='place':
            nx=random.randint(0,3); no=random.choice([nx,nx-1]) if nx>0 else 0
            turn='X' if nx==no else 'O'
            if nx==3 and no==3: continue
            nO=no
        else:
            nx=no=3; turn=random.choice('XO')
        bd=['.']*9; cells=random.sample(range(9),nx+no)
        for i,c in enumerate(cells): bd[c]='X' if i<nx else 'O'
        if r.won(bd,'X') or r.won(bd,'O'): continue
        rem={'X':3-nx,'O':3-no}
        if not legal(bd,turn,rem): continue
        return ''.join(bd),turn,rem
bad=0
for i in range(N):
    bd,turn,rem=gen()
    sc={mv:score(list(bd),mv,turn,rem) for mv in legal(list(bd),turn,rem)}
    best=max(sc.values()); good={mv for mv,v in sc.items() if v==best}
    m=first_move(bd,turn,rem['X'],rem['O'],0)
    t=m.split() if m else None
    if not t: played=None
    else: played=('place',int(t[2])) if t[1]=='places' else ('move',int(t[2]),int(t[4]))
    ok=played in good
    if not ok: bad+=1
    print(i,bd,turn,rem,'best',best,'agent',m,'OK' if ok else 'FAIL (good=%s)'%sorted(good))
print('failures:',bad,'of',N)
