# shared helpers for the English-derived family agents
def world(objs, preds):
    """objs: list of (category, name, {attr: value}); preds: {rel: [(name, name), ...]}"""
    ids = {}
    out = []
    for i, (cat, name, attrs) in enumerate(objs, 1):
        ids[name] = i
        out.append(f'objid {i}\ncategory {cat}\nname {name}' + ''.join(f'\n{k} {v}' for k, v in attrs.items()))
    for r, ts in preds.items():
        out.append(f'predicate {r}\n' + '\n'.join(' '.join(str(ids[x]) for x in t) for t in ts))
    return '\n\n'.join(out) + '\n'
