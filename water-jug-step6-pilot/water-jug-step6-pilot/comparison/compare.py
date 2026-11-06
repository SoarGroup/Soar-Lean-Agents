import json,os,csv
from summarize import summ
vs=json.load(open('gen/water-jug.json'))
rows=[]
def fmt(s):
    if not s: return 'no runs (timeout)'
    return f"{s['solved']}/{s['n']} solved; median {s['med']} ops (min {s['mn']}); chunks {s['chunks']}"
for v in vs:
    g=summ(f"results/gen/{v['name']}.jsonl")
    for o in v['replaces']:
        a,ver=o.split()
        s=summ(f"results/orig/{a}-{ver}.jsonl")
        rows.append([v['name'],o,fmt(s),fmt(g)])
with open('compare.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['regenerated','original','original (20 seeds, 500 decisions)','regenerated (same seeds)']); w.writerows(rows)
for r in rows: print(' | '.join(r))
