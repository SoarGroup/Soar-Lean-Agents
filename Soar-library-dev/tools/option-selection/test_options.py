import check_options as C
def rules(flags, extra=''):
    return '(<f> %s)\n%s' % (' '.join(f'^{k} {v}' for k, v in flags.items()), extra)
SC = '(<op> ^step-cost 2)'; H = '(<w> ^estimated-remaining-cost 3)'
cases = [
 ({'optimize': 'true'}, SC, 'O2', 'E'), ({'iterative-step': 'cost', 'cost-metric': 'none'}, '', 'O2', 'E'),
 ({'cost-metric': 'unit'}, '', 'O3', 'W'), ({'cost-metric': 'speed'}, SC, 'O1', 'E'),
 ({'cost-metric': 'unit', 'optimize': 'true'}, SC + '(<s> ^state-value 4)', 'O7', 'E'),
 ({'cost-metric': 'unit', 'heuristic-weight': '2'}, SC, 'O4', 'W'),
 ({'cost-metric': 'unit', 'iterative-step': 'cost'}, '(<op> ^step-cost 0) ' + '', 'O6', 'W'),
 ({'cost-metric': 'unit', 'optimize': 'true'}, SC + '(<s> ^state-value 4)(<d> ^better higher)', 'O8', 'W'),
 ({'cost-metric': 'unit', 'optimize': 'true'}, SC + H, 'O5', 'W'),
 ({'cost-metric': 'unit'}, SC, 'O12', 'W'), ({'cost-metric': 'unit', 'iterative-step': 'tie-impasse'}, SC, 'O10', 'W'),
 ({'termination': 'progress'}, '', 'O9', 'E'),
]
for fl, ex, rid, lvl in cases:
    got = {(i, l) for i, l, _ in C.check(rules(fl, ex))}
    assert (rid, lvl) in got, (fl, ex, rid, got)
ok = rules({'cost-metric': 'unit', 'optimize': 'true'}, SC)
assert not [x for x in C.check(ok) if x[1] == 'E']
assert not [x for x in C.check(rules({'mea-operator-selection': 'true'}, ''))]
# library v2.37: iterative-step cost without a cost metric gets unit, so it is not an error
assert not [x for x in C.check(rules({'iterative-step': 'cost'}, SC)) if x[1] == 'E']
print('check_options: %d negative cases and 3 positive cases pass' % len(cases))
