"""Interchangeable objects represented by counts (World-Conventions L7-027, 24 Nov 2026).

Two or more objects are interchangeable when nothing in the task can tell them apart:
  1. they have the same category and the same attribute values (no name, no other distinguishing attribute);
  2. each takes part in the same kinds of relations, only as the first argument, and only with objects that are not
     themselves interchangeable (membership: a missionary on a bank) -- never with one another (no stacking, no order);
  3. the task's statements never refer to one of them individually (the generator passes those it does as `referenced`).
Then only how many of them are at each place matters. The world keeps one count per place and kind
(^<kind>-count on the place) and one kind object (^type kind, the shared attributes, ^total) in place of the
individuals and their membership relations; operators take a kind as their argument and change the counts.
A kind needs at least two members: a single object stays an individual (the boat).

The detection works on any world given as objects {id: {attr: value}} and relations {name: [(id1, id2)]};
the generator of a task family decides whether its operators, goal and failures can be written over counts
(supports_counts) and writes them (rosie_river.py for river crossings)."""

IDENTITY = ('index', 'label-key')   # attributes a generator adds per object; never distinguishing

def _key(a):
    return tuple(sorted((k, v) for k, v in a.items() if k not in IDENTITY))

def interchangeable(objs, rels, referenced=(), mirror=('below',)):
    """-> {kind: {'members': [ids], 'attrs': {attr: value}, 'relation': name, 'places': {place id: count}}}.
    kind = the value of the attribute that separates the group from the others of its category (e.g. 'missionary'),
    or the values joined with '-'. mirror: relations that restate another with the arguments swapped (Rosie's
    below(place, object) mirrors on(object, place)); they are checked as the mirror of the main relation."""
    by_key = {}
    for i, a in objs.items():
        if i in referenced or 'name' in a: continue
        by_key.setdefault(_key(a), []).append(i)
    groups = {k: ids for k, ids in by_key.items() if len(ids) >= 2}
    member = {i: k for k, ids in groups.items() for i in ids}
    out = {}
    for key, ids in groups.items():
        roles = []
        ok = True
        for i in ids:
            r = []
            for name, pairs in rels.items():
                for a, b in pairs:
                    if a == i and name not in mirror:
                        if b in member: ok = False
                        r.append((name, 'first'))
                    elif b == i and name in mirror:
                        if a in member: ok = False
                        r.append((name, 'mirror'))
                    elif b == i or a == i:
                        ok = False          # second argument of a main relation, or first of a mirror: not membership
            roles.append(tuple(sorted(r)))
        main = {n for rr in roles for n, role in rr if role == 'first'}
        if not ok or len(set(roles)) != 1 or len(main) != 1: continue
        rel = main.pop()
        places = {}
        for a, b in rels[rel]:
            if a in ids: places[b] = places.get(b, 0) + 1
        attrs = dict(key)
        cat = attrs.get('category')
        same_cat = [_key(objs[j]) for j in objs if objs[j].get('category') == cat and j not in ids]
        sep = [k for k, v in attrs.items() if k != 'category' and all(dict(o).get(k) != v for o in same_cat)]
        kind = '-'.join(str(attrs[k]) for k in (sep or [k for k in attrs if k != 'category']))
        out[kind] = {'members': sorted(ids), 'attrs': attrs, 'relation': rel, 'places': places}
    return out

def counts_for(groups, place_ids):
    """{place id: {'<kind>-count': n}} for every place (0 where a kind has no member)."""
    return {p: {f'{k}-count': g['places'].get(p, 0) for k, g in groups.items()} for p in place_ids}
