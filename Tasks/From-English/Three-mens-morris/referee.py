import sys,re
L=[(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
ADJ={(a,b) for a in range(9) for b in range(9) if a!=b and ((abs(a-b)==1 and a//3==b//3) or abs(a-b)==3 or a==4 or b==4)}
def won(bd,p): return any(all(bd[i]==p for i in l) for l in L)
def moves(bd,p,rem):
    if rem[p]>0: return [('place',c) for c in range(9) if bd[c]=='.']
    return [('move',a,b) for (a,b) in sorted(ADJ) if bd[a]==p and bd[b]=='.']
def play(lines):
    bd=['.']*9; rem={'X':3,'O':3}; turn='X'; plies=0; res=None
    for ln in lines:
        m=re.match(r'([XO]) places (\d)$',ln); m2=re.match(r'([XO]) moves (\d) -> (\d)$',ln)
        if m: p,c=m[1],int(m[2]); mv=('place',c)
        elif m2: p,a,b=m2[1],int(m2[2]),int(m2[3]); mv=('move',a,b)
        else: continue
        if res: return 'move after end'
        if p!=turn: return 'wrong turn: '+ln
        if mv not in moves(bd,p,rem): return 'illegal: '+ln
        if mv[0]=='place': bd[mv[1]]=p; rem[p]-=1
        else: bd[mv[1]]='.'; bd[mv[2]]=p
        plies+=1
        if won(bd,p): res='WINNER: '+p
        turn='O' if p=='X' else 'X'
        if not res and not moves(bd,turn,rem): res='WINNER: '+p
        if not res and plies>=30: res='DRAW'
    return res or 'unfinished'
if __name__=='__main__':
    txt=open(sys.argv[1]).read().split('--- write output ---')[-1].splitlines()
    exp=[l.strip() for l in txt if l.startswith(('WINNER','DRAW'))]
    got=play([l.strip() for l in txt])
    print('referee:',got,'| agent:',exp[0] if exp else None,'| OK' if exp and got==exp[0] else '| MISMATCH')
