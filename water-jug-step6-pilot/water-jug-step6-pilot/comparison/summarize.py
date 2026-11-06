import json,glob,os,statistics as st,sys
def summ(f):
    rs=[json.loads(l) for l in open(f)] if os.path.exists(f) else []
    if not rs: return None
    sol=[r for r in rs if r['solved']]
    ops=[r['ops_to_goal'] for r in sol]
    return dict(n=len(rs),solved=len(sol),halted=sum(r['halted'] for r in rs),
        med=st.median(ops) if ops else None, mn=min(ops) if ops else None,
        dec=st.median([r['decisions'] for r in sol]) if sol else None,
        chunks=st.median([r['chunks'] for r in rs]))
if __name__=='__main__':
    for d in ['orig','gen']:
        for f in sorted(glob.glob(f'results/{d}/*.jsonl')):
            print(d, os.path.basename(f)[:-6], summ(f))
