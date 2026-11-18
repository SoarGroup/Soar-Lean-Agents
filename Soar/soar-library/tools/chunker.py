"""Split a .soar file into ordered segments that concatenate back to the exact file text.
Segment kinds: rule (name, kind sp/gp), crule (commented-out rule block), cmd (top-level command), text (comments/blank/other)."""
import re
from soarparse import match_brace, parse_header
CMD_RE=re.compile(r'^\s*([A-Za-z_][\w-]*)')
CRULE_RE=re.compile(r'^\s*#+\s*(sp|gp)\s*\{\s*([^\s}]*)')

def segment(txt):
    segs=[]; n=len(txt); pos=0
    def add(k,s,e,**kw): segs.append(dict(kind=k,text=txt[s:e],**kw))
    while pos<n:
        eol=txt.find('\n',pos); eol=n if eol<0 else eol
        line=txt[pos:eol]; st=line.strip()
        if not st or (st.startswith('#') and not CRULE_RE.match(line)):
            add('text',pos,min(eol+1,n)); pos=eol+1; continue
        m=CRULE_RE.match(line)
        if m:
            # commented-out rule: consume # lines until braces balance
            depth=0; p=pos; started=False
            while p<n:
                e2=txt.find('\n',p); e2=n if e2<0 else e2
                l=txt[p:e2].lstrip()
                if not l.startswith('#'): break
                body=re.sub(r'^#+','',l)
                depth+=body.count('{')-body.count('}')
                started=started or '{' in body
                p=min(e2+1,n)
                if started and depth<=0: break
            add('crule',pos,p,name=m.group(2),rtype=m.group(1)); pos=p; continue
        m=CMD_RE.match(line)
        if m and m.group(1) in ('sp','gp'):
            b=txt.find('{',pos+line.index(m.group(1)))
            e=match_brace(txt,b)
            name,opts,rest=parse_header(txt[b+1:e])
            nl=txt.find('\n',e); end=n if nl<0 else nl+1
            add('rule',pos,end,name=name,rtype=m.group(1)); pos=end; continue
        end=eol
        if '{' in line and line.count('{')>line.count('}'):
            b=txt.find('{',pos); e=match_brace(txt,b); end=e if e>=0 else eol
            nl=txt.find('\n',end); end=n if nl<0 else nl
        add('cmd',pos,min(end+1,n),name=m.group(1) if m else 'OTHER'); pos=min(end+1,n)
    return segs
