import os, sys, json, shutil, subprocess, re
from concurrent.futures import ThreadPoolExecutor
FAM='/home/claude/runroot6/Tasks/Families'
fam=['blocks-world/world-lean/blocks-world-hierarchical-lookahead','blocks-world/world-lean/blocks-world-look-ahead',
 'blocks-world/world-lean/blocks-world-look-ahead-state-eval','blocks-world/world-lean/blocks-world-operator-subgoaling',
 'blocks-world/world-lean/blocks-world-operator-subgoaling-relevant','eight-puzzle/world-lean/eight-puzzle',
 'missionaries-cannibals/world-lean/mac-look-ahead','missionaries-cannibals/world-lean/mac-look-ahead-numeric',
 'towers-of-hanoi/world-lean/towers-of-hanoi','towers-of-hanoi/world-lean/towers-of-hanoi-mea',
 'water-jug/world-lean/water-jug-look-ahead','water-jug/world-lean/water-jug-look-ahead-failure-states',
 'water-jug/world-lean/water-jug-tie','water-jug/world-lean/water-jug-hierarchy',
 'kenken/world-lean/kenken-4-1','kenken/world-lean/kenken-4-5','kenken/world-lean/kenken-5-1']
gen=['conventions/towers-of-hanoi','examples/towers-of-hanoi-sc1','heldout/kenken','heldout/blocks-world','heldout/towers-of-hanoi','examples/blocks-world']
TIE='''
## experiment: iterative-step tie-impasse
sp {exp*flag-override*iterative-step*tie
   (state <s> ^superstate nil ^flag-override <fo>)
-->
   (<fo> ^iterative-step tie-impasse)
}
'''
jobs=[]
for rel in fam:
    jobs.append(('fam:'+rel, os.path.join(FAM,rel)))
for rel in gen:
    jobs.append(('gen3:'+rel, '/home/claude/gen3/out/'+rel))
def soarfiles(d):
    out=[]
    for r,_,fs in os.walk(d):
        out+= [os.path.join(r,f) for f in fs if f.endswith('.soar')]
    return out
def variant(label,d):
    name=os.path.basename(d)
    v=d.rstrip('/')+'__toggled' if label.startswith('fam') else '/tmp/tie-'+label.split(':')[1].replace('/','-')
    if os.path.exists(v): shutil.rmtree(v)
    shutil.copytree(d,v)
    txt=''.join(open(f).read() for f in soarfiles(v))
    if re.search(r'iterative-step tie-impasse',txt):
        for f in soarfiles(v):
            s=open(f).read(); open(f,'w').write(s.replace('iterative-step tie-impasse','iterative-step operator'))
        mode='tie-impasse -> operator'
    else:
        open(os.path.join(v,'exp-tie.soar'),'w').write(TIE)
        open(os.path.join(v,name+'.soar'),'a').write('\nsource exp-tie.soar\n')
        mode='operator -> tie-impasse'
    return v,mode
def run(d):
    name=os.path.basename(d.rstrip('/')).replace('__toggled','')
    try:
        p=subprocess.run(['python3','/home/claude/runtools/run2.py',d,name+'.soar','--seeds','1-3','--episodes','1','--cap','20000'],capture_output=True,text=True,timeout=2400)
        L=[json.loads(l) for l in p.stdout.splitlines() if l.startswith('{')]
        return [(e['episodes'][0]['result'],e['episodes'][0]['decisions'],e['episodes'][0]['top_ops']) for e in L]
    except subprocess.TimeoutExpired:
        return 'TIMEOUT'
def job(j):
    label,d=j
    v,mode=variant(label,d)
    return label,mode,run(d),run(v)
with ThreadPoolExecutor(8) as ex:
    for label,mode,a,b in ex.map(job,jobs):
        print(json.dumps({'agent':label,'change':mode,'as_written':a,'toggled':b}),flush=True)
