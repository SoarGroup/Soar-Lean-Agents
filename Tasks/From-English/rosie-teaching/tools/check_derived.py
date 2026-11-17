"""Convention check (World-Conventions-Spec v2, section 2): every derived (i-supported) attribute a task rule
writes on a world object must be listed on the task's problem space as ^dont-copy-object-attribute.
usage: check_derived.py RULES.soar [...]   exit status 1 when a rule violates the convention."""
import re, sys
def rules(text):
    text = re.sub(r'(?m)^\s*#.*$', '', text)
    for m in re.finditer(r'sp\s*\{\s*(\S+)(.*?)\n\}', text, re.S):
        yield m.group(1), m.group(2)
def check(text):
    declared = set(re.findall(r'\^dont-copy-object-attribute\s+([\w-]+)', text)); bad = []
    for name, body in rules(text):
        if '-->' not in body: continue
        lhs, rhs = body.split('-->', 1)
        if ':o-support' in lhs: continue
        if re.search(r'\^operator(\.[\w-]+)?\s+<?[\w-]+>?(?!\s*\+)', re.sub(r'\^operator\s+<[\w-]+>\s*\+', '', lhs)): continue   # tests a selected operator: o-support
        objvars = set()
        for m in re.finditer(r'\^(?:objects\.)?object((?:\s+<[\w-]+>)+)', lhs): objvars |= set(re.findall(r'<[\w-]+>', m.group(1)))
        for v, acts in re.findall(r'\((<[\w-]+>)((?:\s*\^[\w-]+\s+(?:\([^()]*(?:\([^()]*\)[^()]*)*\)|[^\s()^]+))+)\s*\)', rhs):
            if v in objvars:
                for a in re.findall(r'\^([\w-]+)', acts):
                    if a not in declared: bad.append((name, a))
    return sorted(declared), bad
if __name__ == '__main__':
    rc = 0
    for f in sys.argv[1:]:
        d, bad = check(open(f).read())
        print(f, 'declared:', d, 'OK' if not bad else 'VIOLATIONS: ' + '; '.join(f'{n} writes ^{a}' for n, a in bad))
        rc |= bool(bad)
    sys.exit(rc)
