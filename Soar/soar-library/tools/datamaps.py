"""Datamaps: one merged library datamap (single source of truth, every edge tagged with the project that owns it)
and per-project <project>.vsa.json files assembled from it. Visual Soar's JSON format has no cross-project link,
so each project file contains its own edges plus those of the projects it requires, generated from the one source.
Usage: python3 datamaps.py OUTDIR            (build merged graph from the old tree, then assemble)
       python3 datamaps.py OUTDIR --assemble (reassemble from OUTDIR/datamaps/library-datamap.json only)"""
import os, sys, json, uuid, re, copy, collections
from soarparse import strip_comments
from chunker import segment
OLD='/tmp/s0/zip'
LAYERS=['soar-base','selection-world','agent-world','object-world','thor-soar','thor-tasks']
SRC={'AW':'default-world/agent-world.vsa.json','SW':'default-world/selection-world.vsa.json','ID':'default-world/selection-iterative-deepening.vsa.json','T':'thor-soar.vsa.json'}
SRC_LAYER={'AW':2,'SW':1,'ID':1,'T':4}
IMPASSE={'Operator_Tie','Operator_Constraint-Failure','State_No-Change','Operator_Conflict'}
NOT_OP={'elaborations','all','strategies','events','settings','from-agent-world','docs','from-thor','first-success','iterative-deepening','optimal','_flags'}
STRIP=['strategies/iterative-deepening/','strategies/first-success/','strategies/optimal/','events/']
NS=uuid.UUID('6f1c2a58-0000-4000-8000-5ca1ab1e0001')
def uid(*a): return uuid.uuid5(NS,':'.join(map(str,a))).hex
ATTR=re.compile(r'\^((?:[A-Za-z][\w-]*)(?:\.[A-Za-z][\w-]*)*)')

def load(tag):
    d=json.load(open(os.path.join(OLD,SRC[tag])))
    return {v['id']:v for v in d['datamap']['vertices']}, d['datamap']['rootId'], d['layout']

def old_dmids(tag,layout):
    res={}
    def walk(n,rel):
        if 'dmId' in n: res[rel]=n['dmId']
        for c in n.get('children',[]):
            walk(c,(rel+'/'+c.get('folder',c.get('file','')).replace('.soar','')).lstrip('/'))
    walk(layout,''); return res

def used_attrs(out):
    u={}
    for p in LAYERS:
        s=set(); base=os.path.join(out,p)
        if not os.path.isdir(base): u[p]=s; continue
        for dp,dn,fn in os.walk(base):
            if '/docs' in dp: continue
            for f in fn:
                if not f.endswith('.soar') or f.endswith('_source.soar'): continue
                for seg in segment(open(os.path.join(dp,f),errors='replace').read()):
                    if seg['kind']=='rule':
                        for m in ATTR.finditer(strip_comments(seg['text'])): s.update(m.group(1).split('.'))
        u[p]=s
    return u

class G:
    def __init__(s): s.V={}; s.prov={}; s.conf=[]; s.res=[]; s.decided=[]; s.map={}; s.root=None; s.sub={}
    def path(s,vid):
        import collections as _c
        q=_c.deque([(s.root,'')]); seen={s.root}
        while q:
            v,p=q.popleft()
            if v==vid: return p or '<top-state>'
            for e in s.V[v].get('outEdges',[]):
                if e['toId'] not in seen: seen.add(e['toId']); q.append((e['toId'],p+'.'+e['name']))
        return '(substate)'
    def copyv(s,v,nid):
        n={'id':nid,'type':v['type']}
        for k in('choices','min','max'):
            if k in v: n[k]=list(v[k]) if k=='choices' else v[k]
        if v['type']=='SOAR_ID': n['outEdges']=[]
        return n
    def imp(s,tag,S,sid,keepid=False):
        if (tag,sid) in s.map: return s.map[(tag,sid)]
        nid=sid if keepid else uid(tag,sid); s.map[(tag,sid)]=nid
        s.V[nid]=s.copyv(S[sid],nid)
        for e in S[sid].get('outEdges',[]):
            t=s.imp(tag,S,e['toId'],keepid)
            ne=dict(e); ne['toId']=t; s.V[nid]['outEdges'].append(ne); s.prov[(nid,e['name'],t)]={tag}
        return nid
    def merge(s,tag,S,sroot):
        stack=[(s.root,sroot)]; seen=set(); s.map[(tag,sroot)]=s.root
        while stack:
            m,sv=stack.pop()
            if (m,sv) in seen: continue
            seen.add((m,sv))
            for e in S[sv].get('outEdges',[]):
                have=[x for x in s.V[m]['outEdges'] if x['name']==e['name']]
                if not have:
                    t=s.imp(tag,S,e['toId']); ne=dict(e); ne['toId']=t; s.V[m]['outEdges'].append(ne); s.prov[(m,e['name'],t)]={tag}; continue
                x=have[0]; mt=x['toId']; st=e['toId']; s.prov[(m,x['name'],mt)].add(tag)
                a,b=s.V[mt],S[st]
                if (tag,st) not in s.map: s.map[(tag,st)]=mt
                if a['type']!=b['type']:
                    ty={a['type'],b['type']}; nm=e['name']; where=s.path(m).lstrip('.')
                    if ty=={'STRING','ENUMERATION'}:           # open set of symbols: STRING is the broader type
                        a['type']='STRING'; a.pop('choices',None); s.res.append(f"^{nm}: STRING vs ENUMERATION ({tag}) -> STRING"); continue
                    if ty=={'INTEGER','FLOAT'}:                  # numbers: FLOAT is the broader type
                        a['type']='FLOAT'
                        if 'min' in a and 'min' in b: a['min']=min(a['min'],b['min'])
                        else: a.pop('min',None)
                        if 'max' in a and 'max' in b: a['max']=max(a['max'],b['max'])
                        else: a.pop('max',None)
                        s.res.append(f"^{nm}: INTEGER vs FLOAT ({tag}) -> FLOAT"); continue
                    if 'SOAR_ID' in ty:                          # id vs symbol: the attribute has children in one datamap
                        if a['type']=='SOAR_ID':
                            s.conf.append(f"[{where}] ^{nm}: SOAR_ID in one datamap, {b['type']} in {tag}; kept SOAR_ID (children win; the other use is a constant value)"); continue
                        if b.get('outEdges'):
                            a['type']='SOAR_ID'; a.pop('choices',None); a['outEdges']=a.get('outEdges',[]); stack.append((mt,st))
                            s.conf.append(f"[{where}] ^{nm}: {a['type']} in one datamap, SOAR_ID in {tag}; kept SOAR_ID (children win; the other use is a constant value)"); continue
                    if 'SOAR_ID' not in ty:                       # two constant types (for example STRING and INTEGER): mixed symbols
                        a['type']='STRING'; a.pop('choices',None); a.pop('min',None); a.pop('max',None)
                        s.res.append(f"^{nm}: {sorted(ty)[0]} vs {sorted(ty)[1]} ({tag}) -> STRING"); continue
                    s.conf.append(f"[{where}] ^{nm}: {a['type']} vs {b['type']} ({tag}); kept first (the SOAR_ID side has no children in its datamap)"); continue
                if a['type']=='SOAR_ID': stack.append((mt,st))
                elif a['type']=='ENUMERATION': a['choices']=sorted(set(a.get('choices',[]))|set(b.get('choices',[])))
                elif a['type'] in('INTEGER','FLOAT'):
                    if 'min' in a and 'min' in b: a['min']=min(a['min'],b['min'])
                    if 'max' in a and 'max' in b: a['max']=max(a['max'],b['max'])

def build_global(out):
    g=G(); S={}; lay={}; roots={}
    for t in SRC: S[t],roots[t],lay[t]=load(t)
    # base = agent-world, keep its ids
    for vid,v in S['AW'].items(): g.V[vid]=copy.deepcopy(v); g.map[('AW',vid)]=vid
    g.root=roots['AW']
    for v in g.V.values():
        for e in v.get('outEdges',[]): g.prov[(v['id'],e['name'],e['toId'])]={'AW'}
    for t in ('SW','ID','T'): g.merge(t,S[t],roots[t])
    # decisions on datamap type conflicts (JEL, 13 Nov 2026): attends.attend is a constant handle (STRING); the scene-copy structure has
    # no rules and is dropped. abstract-property stays STRING, desireds.achieved and the argument attributes stay SOAR_ID (merge default).
    def edge_at(path):
        c=g.root; ed=None
        for p in path.split('.'):
            ed=[e for e in g.V[c].get('outEdges',[]) if e['name']==p]
            if not ed: return None
            ed=ed[0]; c=ed['toId']
        return ed
    ed=edge_at('attends.attend')
    if ed:
        nid=uid('attend-string'); g.V[nid]=dict(id=nid,type='STRING'); ed['toId']=nid
        g.prov[(next(k[0] for k in list(g.prov) if k[1]=='attend'),'attend',nid)]={'T'}
    rv=g.V[g.root]; rv['outEdges']=[e for e in rv.get('outEdges',[]) if e['name']!='scene-copy']
    # decisions (JEL, 13 Nov 2026, second batch): disjunction -> the desired structure; holding-object -> an object (the old 'none' value is gone);
    # duplicate-of and future-event stay identifiers; instance-of is a constant (STRING).
    dest=edge_at('desireds.desired')['toId']; objv=edge_at('world.objects.object')['toId']
    sv=uid('instance-of-string'); g.V[sv]=dict(id=sv,type='STRING')
    supd=edge_at('super-desired'); supd=supd['toId'] if supd else None
    def repoint(vid,e,new):
        old=e['toId']; pv=g.prov.pop((vid,e['name'],old),set()); e['toId']=new
        g.prov[(vid,e['name'],new)]=g.prov.get((vid,e['name'],new),set())|pv
    for vid,v in list(g.V.items()):
        keep=[]
        for e in v.get('outEdges',[]):
            tg=g.V[e['toId']]; nm=e['name']
            if nm=='disjunction' and tg['type']=='SOAR_ID': repoint(vid,e,dest)
            elif nm=='holding-object' and tg['type']=='SOAR_ID' and tg.get('outEdges'): repoint(vid,e,objv)
            elif nm=='holding-object' and vid==supd and tg['type']=='ENUMERATION': g.prov.pop((vid,nm,e['toId']),None); continue
            elif nm=='instance-of': repoint(vid,e,sv)
            keep.append(e)
        if 'outEdges' in v: v['outEdges']=keep
    # decisions (JEL, 13 Nov 2026, third batch): last-operator dropped; mobile is an enumeration; next and superstate each get two entries,
    # one SOAR_ID and an additional ENUMERATION nil; task stays SOAR_ID.
    vis=uid('visible-enum'); g.V[vis]=dict(id=vis,type='ENUMERATION',choices=['false','true'])
    mob=uid('mobile-enum'); g.V[mob]=dict(id=mob,type='ENUMERATION',choices=['false','true'])
    nilv=uid('nil-enum'); g.V[nilv]=dict(id=nilv,type='ENUMERATION',choices=['nil'])
    for vid,v in list(g.V.items()):
        ne_list=[]
        for e in v.get('outEdges',[]):
            nm=e['name']
            if nm=='last-operator': g.prov.pop((vid,nm,e['toId']),None); continue
            if nm=='mobile': repoint(vid,e,mob)
            if nm=='visible': repoint(vid,e,vis)
            if nm=='top-segment' and g.V[e['toId']]['type']=='STRING': g.prov.pop((vid,nm,e['toId']),None); continue
            ne_list.append(e)
            if nm in('next','superstate','top-segment') and g.V[e['toId']]['type']=='SOAR_ID' and not any(x['name']==nm and g.V[x['toId']]['type']=='ENUMERATION' for x in v['outEdges']):
                ne=dict(e); ne['toId']=nilv; ne_list.append(ne); g.prov[(vid,nm,nilv)]=set(g.prov.get((vid,nm,e['toId']),{'AW'}))
        if 'outEdges' in v: v['outEdges']=ne_list
    g.decided=[
     'world.abstract-property: STRING (its value names an attribute; rule achieved-desired*abstract-property)',
     'desireds.achieved: SOAR_ID (pointer to an achieved desired; the ^achieved true comment in _firstload is stale)',
     '^argument1 to ^argument4 (operator, desireds, world, scene, retrieved-in, io.output-link.perform-action): SOAR_ID. A few Thor operators (turn, fill, scene-update) use constant arguments; the datamap cannot show both.',
     'attends.attend: STRING (the value is an object handle); children removed',
     'scene-copy: dropped (no rule creates or tests it)',
     'disjunction: SOAR_ID, the same structure as desireds.desired (it points to another desired)',
     'duplicate-of: SOAR_ID (points to the original)',
     'future-event: SOAR_ID',
     'holding-object: SOAR_ID, the object structure (world.objects.object); the old ^holding-object none value is gone. The input-link self.arm.holding-object handle stays a STRING.',
     'instance-of: STRING (a constant such as object-argument); children removed',
     'last-operator: dropped (no rule uses it)',
     'mobile: ENUMERATION true/false',
     'next and superstate: two entries each, a SOAR_ID and an additional ENUMERATION nil (end of chain; top state)',
     'task: SOAR_ID',
     'time (io.input-link): SOAR_ID with child ms; the Thor world-level ^time constant is a different attribute on a different parent',
     'top-segment: two entries, a SOAR_ID and an additional ENUMERATION nil',
     'visible: ENUMERATION true/false']
    import patches
    for v in g.V.values():
        if 'outEdges' in v: v['outEdges']=[e for e in v['outEdges'] if not (e['name'] in patches.REMOVED_FLAGS)]
    g.prov={k:p for k,p in g.prov.items() if k[1] not in patches.REMOVED_FLAGS}
    # flags convention: ^flag-override has the same flag attributes as ^flags (same value vertices)
    rootv=g.V[g.root]; fe=[e for e in rootv.get('outEdges',[]) if e['name']=='flags']
    if fe and not any(e['name']=='flag-override' for e in rootv['outEdges']):
        F=g.V[fe[0]['toId']]; fid=uid('flag-override')
        g.V[fid]=dict(id=fid,type='SOAR_ID',outEdges=[dict(e) for e in F.get('outEdges',[])])
        rootv['outEdges'].append({k:v for k,v in fe[0].items() if k not in('name','toId')}|dict(name='flag-override',toId=fid))
        g.prov[(g.root,'flag-override',fid)]={'AW'}
        for e in g.V[fid]['outEdges']: g.prov[(fid,e['name'],e['toId'])]={'AW'}
    use=used_attrs(out)
    # raw layer per edge by attribute usage, else by source
    def raw(name,prov):
        us=[i for i,p in enumerate(LAYERS) if name in use[p]]
        if us: return min(us),True
        return min(SRC_LAYER[t] for t in prov),False
    # relax layers from root
    EL={}; unused=0
    for v in g.V.values():
        for e in v.get('outEdges',[]):
            r,u=raw(e['name'],g.prov[(v['id'],e['name'],e['toId'])]); EL[(v['id'],e['name'],e['toId'])]=r
    VL={g.root:0}; changed=True
    while changed:
        changed=False
        for (a,n,b),r in list(EL.items()):
            if a not in VL: continue
            l=max(r,VL[a])
            if EL[(a,n,b)]!=l: EL[(a,n,b)]=l
            if b not in VL or l<VL[b]: VL[b]=l; changed=True
    # reachable-from-root vertices only; unreachable root-graph vertices are dropped
    for v in g.V.values():
        for e in v.get('outEdges',[]):
            e['layer']=EL[(v['id'],e['name'],e['toId'])] if v['id'] in VL else None
    # substates: for each new project layout node with an old dmId, import the subgraph
    return g,S,lay,use

def substate_index(g,S,lay,out):
    """For every high-level node in the new tree find its old dmId and import that substate subgraph into g."""
    old={t:old_dmids(t,lay[t]) for t in SRC}
    res={}
    for p in LAYERS:
        base=os.path.join(out,p)
        if not os.path.isdir(base): continue
        res[p]={}
        for dp,dn,fn in os.walk(base):
            if '/docs' in dp: continue
            rel=os.path.relpath(dp,base); rel='' if rel=='.' else rel
            parent=os.path.dirname(dp)
            name=os.path.basename(dp)
            if rel and os.path.exists(os.path.join(parent,name+'.soar')):
                key=rel
                for pre in STRIP:
                    if key.startswith(pre): key=key[len(pre):]
                for t in (('SW','ID') if p=='selection-world' else ('AW',) if p in('agent-world','object-world') else ('T',)):
                    if key in old[t]:
                        sid=old[t][key]
                        if sid in S[t]:
                            res[p][rel]=imp_sub(g,t,S[t],sid); break
    return res
def imp_sub(g,t,S,sid):
    if (t,sid) in g.map: return g.map[(t,sid)]
    nid=uid(t,sid); g.map[(t,sid)]=nid; g.V[nid]=g.copyv(S[sid],nid)
    for e in S[sid].get('outEdges',[]):
        tgt=imp_sub(g,t,S,e['toId']); ne=dict(e); ne['toId']=tgt; ne['layer']=None; g.V[nid]['outEdges'].append(ne)
    return nid

def save_global(g,sub,use,out):
    os.makedirs(os.path.join(out,'datamaps'),exist_ok=True)
    d=dict(rootId=g.root,vertices=list(g.V.values()),substates=sub,layers=LAYERS,
           note='edge "layer" = index in layers of the project that owns the edge (null = substate-only edge, always included)',
           conflicts=g.conf)
    json.dump(d,open(os.path.join(out,'datamaps','library-datamap.json'),'w'),indent=0)
    return d

PROTECT_TOP={'io','self','scene','smem','epmem','svs','reward-link'}
def trim_set(out,V,root):
    """Edges (parent id, attr, child id) to drop: attribute mentioned by no rule in any project, and not part of
    the environment/architecture interface (anything under io, self, scene, smem, epmem, svs, reward-link)."""
    if os.environ.get('TRIM','1')=='0': return set(),[]
    use=used_attrs(out); allu=set().union(*use.values())
    path={root:()}; q=[root]
    while q:
        a=q.pop(0)
        for e in V[a].get('outEdges',[]):
            if e['toId'] not in path: path[e['toId']]=path[a]+(e['name'],); q.append(e['toId'])
    drop=set(); rep=[]
    for a,p in path.items():
        for e in V[a].get('outEdges',[]):
            if e['name'] in allu: continue
            if set(p)&PROTECT_TOP or e['name'] in PROTECT_TOP: continue
            drop.add((a,e['name'],e['toId'])); rep.append('.'.join(p)+' ^'+e['name'])
    return drop,sorted(rep)

def assemble(out,d=None):
    d=d or json.load(open(os.path.join(out,'datamaps','library-datamap.json')))
    V={v['id']:v for v in d['vertices']}; root=d['rootId']; report=[]
    TRIM,trep=trim_set(out,V,root)
    open(os.path.join(out,'datamaps','datamap-trimmed.txt'),'w').write(
        '# Datamap edges removed from the project datamaps because no rule in any project mentions the attribute.\n'
        '# Environment/architecture interface (io, self, scene, smem, epmem, svs, reward-link) is never trimmed.\n'
        '# Full untrimmed graph remains in library-datamap.json. Rebuild with TRIM=0 to keep everything.\n'
        +'\n'.join(trep)+'\n')
    report.append('trimmed %d unused edges (see datamaps/datamap-trimmed.txt)'%len(TRIM))
    for li,p in enumerate(LAYERS):
        base=os.path.join(out,p)
        if not os.path.isdir(base): continue
        keep={}; 
        def visit(vid):
            if vid in keep: return
            v=V[vid]; n={k:v[k] for k in v if k not in('outEdges',)}
            keep[vid]=n
            if v['type']=='SOAR_ID':
                n['outEdges']=[]
                for e in v.get('outEdges',[]):
                    if (vid,e['name'],e['toId']) in TRIM: continue
                    L=e.get('layer')
                    if L is not None and L>li: continue
                    ne={k:e[k] for k in e if k!='layer'}; n['outEdges'].append(ne); visit(e['toId'])
        visit(root)
        sub=d['substates'].get(p,{})
        for vid in sub.values(): visit(vid)
        newv=[]
        # layout
        def node(dp,rel,name):
            files=sorted((f for f in os.listdir(dp) if f.endswith('.soar') and not f.endswith('_source.soar')),key=lambda x:(not x.startswith('_'),x))
            dirs=sorted((x for x in os.listdir(dp) if os.path.isdir(os.path.join(dp,x)) and x!='docs'),key=lambda x:(not x.startswith('_'),x))
            ch=[]
            for f in files:
                if f[:-5] in dirs: continue
                ch.append(dict(file=f,id=uid(p,rel,f),name=f[:-5],type='FILE_OPERATOR'))
            for x in dirs:
                r=(rel+'/'+x).lstrip('/'); sn=node(os.path.join(dp,x),r,x)
                if x+'.soar' in files:
                    dm=sub.get(r)
                    if dm is None:
                        dm=uid(p,'new',r); keep[dm]=dict(id=dm,type='SOAR_ID',outEdges=[]); newv.append(r)
                    sn.update(dmId=dm,file=x+'.soar',type='HIGH_LEVEL_IMPASSE_OPERATOR' if (x in IMPASSE or x.startswith('Impasse__')) else 'HIGH_LEVEL_OPERATOR')
                ch.append(sn)
            ch.sort(key=lambda c:(not (c.get('file') or c.get('folder','')).startswith('_')))   # "_" entries first, files and folders alike
            n=dict(folder=name,id=uid(p,rel,'folder'),name=name,type='FOLDER')
            if ch: n['children']=ch
            return n
        lay=node(base,'',p); lay['type']='OPERATOR_ROOT'
        out_json=dict(datamap=dict(rootId=root,vertices=list(keep.values())),layout=lay,version='6')
        json.dump(out_json,open(os.path.join(out,p+'.vsa.json'),'w'),indent=1)
        ne=sum(len(v.get('outEdges',[])) for v in keep.values())
        report.append(f'{p}: {len(keep)} vertices, {ne} edges; {len(sub)} operator substates carried over, {len(newv)} new empty')
    return report

def main(out,only_assemble=False):
    if only_assemble:
        dd=json.load(open(os.path.join(out,'datamaps','library-datamap.json'))); rep=assemble(out,dd)+dd.get('stats',[])
    else:
        g,S,lay,use=build_global(out)
        sub=substate_index(g,S,lay,out)
        d=save_global(g,sub,use,out)
        rep=assemble(out,d)
        # ownership statistics
        own=collections.Counter(LAYERS[e['layer']] for v in d['vertices'] for e in v.get('outEdges',[]) if e.get('layer') is not None)
        rep.append('edges owned (root datamap): '+', '.join(f'{k} {v}' for k,v in own.items()))
        d['stats']=['edges owned (root datamap): '+', '.join(f'{k} {v}' for k,v in own.items()),'type disagreements between the old datamaps: %d resolved by rule, %d genuine (id vs symbol), see datamap-conflicts.txt'%(len(set(g.res)),len(set(g.conf)))]
        json.dump(d,open(os.path.join(out,'datamaps','library-datamap.json'),'w'),indent=0)
        rep.append(d['stats'][1])
        DEC={'abstract-property','achieved','argument1','argument2','argument3','argument4','attend','class','disjunction','duplicate-of','future-event',
             'holding-object','instance-of','last-operator','mobile','next','superstate','task','time','top-segment','visible'}
        import re as _re
        C=collections.Counter(c for c in g.conf if (_re.search(r'\^([\w-]+):',c) or [None,None])[1] not in DEC); R=collections.Counter(g.res)
        open(os.path.join(out,'datamaps','datamap-conflicts.txt'),'w').write(
          'Type disagreements between the old datamaps (agent-world was the base; SW=selection-world, ID=iterative-deepening, T=thor-soar).\n'
          'Resolution rules: STRING vs ENUMERATION -> STRING (open set of symbols); INTEGER vs FLOAT -> FLOAT; SOAR_ID vs a constant type -> SOAR_ID\n'
          '(an attribute that has children in one datamap is an identifier there; the other datamap used it with a constant value, e.g. ^superstate nil).\n\n'
          'Decided by JEL on 13 Nov 2026:\n'+''.join('  '+x+'\n' for x in g.decided)+'\n'+
          'Resolved by rule (%d distinct):\n'%len(R)+'\n'.join('  %s'%k+(' x%d'%v if v>1 else '') for k,v in sorted(R.items()))+
          '\n\nId vs constant still to review (%d distinct entries):\n'%len(C)+'\n'.join('  %s'%k+(' x%d'%v if v>1 else '') for k,v in sorted(C.items()))+'\n')
    open(os.path.join(out,'datamaps','datamap-report.txt'),'w').write('\n'.join(rep)+'\n')
    print('\n'.join(rep))
if __name__=='__main__': main(sys.argv[1],'--assemble' in sys.argv)
