"""Check a run: every printed deduction removes a value that the unique solution does not put in
that house, every branch agrees with the solution, and the answers are right."""
import re, sys
from itertools import permutations as P
C=['red','green','white','yellow','blue'];N=['English','Swede','Dane','Norwegian','German'];D=['tea','coffee','milk','beer','water'];S=['PallMall','Dunhill','Blends','BlueMaster','Prince'];A=['dogs','birds','cats','horses','zebra']
nb=lambda a,b:abs(a-b)==1
sols=[]
for c in P(range(5)):
  col=dict(zip(C,c))
  if col['green']+1!=col['white']: continue
  for n in P(range(5)):
    nat=dict(zip(N,n))
    if nat['English']!=col['red'] or nat['Norwegian']!=0 or not nb(nat['Norwegian'],col['blue']): continue
    for d in P(range(5)):
      dr=dict(zip(D,d))
      if dr['tea']!=nat['Dane'] or dr['coffee']!=col['green'] or dr['milk']!=2: continue
      for s in P(range(5)):
        sm=dict(zip(S,s))
        if sm['Dunhill']!=col['yellow'] or sm['BlueMaster']!=dr['beer'] or sm['Prince']!=nat['German']: continue
        for a in P(range(5)):
          an=dict(zip(A,a))
          if an['dogs']!=nat['Swede'] or an['birds']!=sm['PallMall'] or not nb(sm['Blends'],an['cats']) or not nb(an['horses'],sm['Dunhill']): continue
          sols.append({**col,**nat,**dr,**sm,**an})
assert len(sols)==1, len(sols); sol=sols[0]
txt=sys.stdin.read(); bad=0
for h,v in re.findall(r'^  House (\d) is not (\w+):', txt, re.M):
    if sol[v]+1==int(h): bad+=1; print('WRONG deduction: house',h,'is not',v)
for h,c,v in re.findall(r'Branch: house (\d), (\w+) = (\w+)\.', txt):
    if sol[v]+1!=int(h): bad+=1; print('WRONG branch', h, v)
water=[k for k in N if sol[k]==sol['water']][0]; zebra=[k for k in N if sol[k]==sol['zebra']][0]
lab={'English':'Englishman'}
ok=f"the {lab.get(water,water)} drinks water; the {lab.get(zebra,zebra)} owns the zebra" in txt
n=len(re.findall(r'^  House', txt, re.M))
print(f"{n} deductions checked; {bad} wrong; answer {'correct' if ok else 'MISSING/WRONG'} (water: {water}, zebra: {zebra}; unique solution)")
