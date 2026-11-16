import sys, re
N=int(sys.argv[1]) if len(sys.argv)>1 else 3; side={f'{r}-{i}':'left' for r in ('artist','manager') for i in range(1,N+1)}; boat='left'; ok=True; n=0
for line in sys.stdin:
    m=re.match(r'Crossing: (.*) row from the (\w+) bank to the (\w+) bank', line)
    if not m: continue
    n+=1; ppl=m.group(1).split(' and '); f,t=m.group(2),m.group(3)
    assert f==boat and 1<=len(ppl)<=2 and all(side[p]==f for p in ppl), line
    for p in ppl: side[p]=t
    boat=t
    for b in ('left','right'):
        for i in range(1,N+1):
            a=f'artist-{i}'
            if side[a]==b and side[f'manager-{i}']!=b and any(side[f'manager-{j}']==b for j in range(1,N+1) if j!=i):
                ok=False; print('UNSAFE after', n, line.strip())
print(n,'crossings;', 'all safe' if ok else 'UNSAFE', '; all across' if all(v=='right' for v in side.values()) else '; NOT all across')
