"""Minimal Soar source parser: productions, top-level commands, commented-out productions."""
import re, os

CMD_RE = re.compile(r'^\s*([A-Za-z_][\w-]*)\b')

def strip_comments(s):
    """Remove #-comments to end of line outside |...| quoting."""
    out=[]; i=0; n=len(s); inq=False; bol=True
    while i<n:
        c=s[i]
        if inq:
            out.append(c)
            if c=='|': inq=False
            elif c=='\\' and i+1<n: out.append(s[i+1]); i+=1
        else:
            if c=='|': inq=True; out.append(c)
            elif c=='#':
                while i<n and s[i]!='\n': i+=1
                continue
            elif c=='\\' and i+1<n: out.append(c); out.append(s[i+1]); i+=1
            else: out.append(c)
        i+=1
    return ''.join(out)

def match_brace(s, i):
    """s[i]=='{' ; return index of matching '}' honoring |..|, backslash, and # comments."""
    depth=0; n=len(s); inq=False
    while i<n:
        c=s[i]
        if inq:
            if c=='|': inq=False
            elif c=='\\': i+=1
        else:
            if c=='|': inq=True
            elif c=='\\': i+=1
            elif c=='#':
                while i<n and s[i]!='\n': i+=1
                continue
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0: return i
        i+=1
    return -1

def parse_header(body):
    """body = text inside sp{...}. Return name, options, rest."""
    t=body; i=0; n=len(t)
    def skipws(i):
        while i<n:
            if t[i] in ' \t\r\n': i+=1
            elif t[i]=='#':
                while i<n and t[i]!='\n': i+=1
            else: break
        return i
    i=skipws(i); j=i
    while j<n and t[j] not in ' \t\r\n': j+=1
    name=t[i:j]; opts=[]; i=j
    while True:
        i=skipws(i)
        if i<n and t[i]==':':
            j=i
            while j<n and t[j] not in ' \t\r\n': j+=1
            opts.append(t[i:j]); i=j
        elif i<n and t[i]=='"':
            j=t.find('"',i+1); i=(j+1) if j>=0 else n
        else: break
    return name,opts,t[i:]

def parse_file(path):
    """Return dict(rules=[], commented_rules=[], commands=[])."""
    txt=open(path,errors='replace').read()
    rules=[]; crules=[]; cmds=[]
    n=len(txt); pos=0; line_starts=[0]
    for m in re.finditer('\n',txt): line_starts.append(m.end())
    import bisect
    def lineno(p): return bisect.bisect_right(line_starts,p)
    while pos<n:
        eol=txt.find('\n',pos); eol=n if eol<0 else eol
        line=txt[pos:eol]; st=line.lstrip()
        if not st: pos=eol+1; continue
        if st.startswith('#'):
            m=re.match(r'#+\s*(sp|gp)\s*\{\s*([^\s}]*)',st)
            if m: crules.append(dict(name=m.group(2),kind=m.group(1),file=path,line=lineno(pos)))
            m=re.match(r'#+\s*(excise)\s+(\S+)',st)
            if m: cmds.append(dict(cmd='excise',args=m.group(2),commented=True,file=path,line=lineno(pos)))
            pos=eol+1; continue
        m=CMD_RE.match(line)
        if m and m.group(1) in ('sp','gp'):
            b=txt.find('{',pos+line.index(m.group(1)))
            e=match_brace(txt,b) if b>=0 else -1
            if e<0:
                cmds.append(dict(cmd='UNBALANCED',args=line[:60],commented=False,file=path,line=lineno(pos))); pos=eol+1; continue
            name,opts,rest=parse_header(txt[b+1:e])
            rules.append(dict(name=name,kind=m.group(1),opts=opts,raw=rest,file=path,line=lineno(pos)))
            nl=txt.find('\n',e); pos=(n if nl<0 else nl)+1
            continue
        if m:
            # one-line command; allow backslash continuation / braces spanning lines
            end=eol
            if '{' in line and line.count('{')>line.count('}'):
                b=txt.find('{',pos); e=match_brace(txt,b); end=e if e>=0 else eol
                nl=txt.find('\n',end); end=n if nl<0 else nl
            cmds.append(dict(cmd=m.group(1),args=txt[pos:end].strip()[len(m.group(1)):].strip()[:200],commented=False,file=path,line=lineno(pos)))
            pos=end+1; continue
        cmds.append(dict(cmd='OTHER',args=st[:60],commented=False,file=path,line=lineno(pos))); pos=eol+1
    return dict(rules=rules,commented_rules=crules,commands=cmds)

def analyze_rule(r):
    body=strip_comments(r['raw'])
    k=body.find('-->')
    lhs,rhs=(body[:k],body[k+3:]) if k>=0 else (body,'')
    r['lhs']=lhs; r['rhs']=rhs
    return r
