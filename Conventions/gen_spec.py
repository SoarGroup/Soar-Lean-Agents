"""Generate a reference specification (Markdown) from a conventions workbook.

Usage:
    python gen_spec.py World-Conventions-v6.xlsx World-Conventions-Spec-v7.md
    python gen_spec.py Soar-Conventions.xlsx Soar-Conventions-Spec.md
An optional third argument sets the title.

The spec lists every convention, one section per level (in level order) and one
subsection per topic (in the development order below), then by ID. Rebuild it
whenever the workbook changes; do not edit the generated file by hand.
Requires openpyxl.

Revision of 21 November 2026 (release with library v2.45): every level of the Levels sheet is listed, including
levels with no rows yet (e.g. L21 Strategy selection); each row shows its Type (Requirement, Choice, Reserved,
Library definition, ...) and, where it is not Proposed, its Status; rows show their former ID ("formerly"),
so IDs cited in older sources can be found; Soar-Conventions rows shared with the World workbook are marked;
the topics added since 18 November (Flags, Impasses, Evaluation values, Look-ahead settings) have their place
in the development order instead of sorting last.
"""
import re
import sys
from datetime import datetime

import openpyxl

TOPIC_ORDER = [
    'Project/file organization', 'Naming and files', 'Flags', 'Flags and constants', 'Rule syntax/naming',
    'State representation', 'World/state', 'Objects', 'Relations',
    'Goal/desired representation', 'Desireds', 'Desireds bookkeeping',
    'Operator WM representation', 'Task operators', 'Composite operators', 'Non-task operators',
    'Rule: state elaboration', 'Rule: operator proposal', 'Rule: operator elaboration',
    'Rule: operator evaluation/selection', 'Search control', 'Rule: operator application',
    'Operator application (internal/external)', 'Output and events', 'Rule: monitoring/output',
    'Impasses', 'Rule: impasse/substate handling', 'Substate representation', 'Substates (general)', 'Rule: results',
    'Selection space', 'Look-ahead / evaluation', 'Evaluation values', 'Look-ahead settings', 'Cost', 'Iterative deepening',
    'MEA operator subgoaling', 'Grounding', 'Time and future events',
    'Semantic memory', 'Episodic memory', 'Learning: chunking', 'Learning: RL',
    'Input/output link', 'Settings/commands', 'Other',
]
TOPIC_POS = {t: i for i, t in enumerate(TOPIC_ORDER)}


def level_key(level):
    m = re.match(r'L(\d+)([A-Z]?)', level or '')
    return (int(m.group(1)), m.group(2)) if m else (999, '')


def id_key(i):
    m = re.match(r'(.*?)-(\d+)$', i or '')
    return (m.group(1), int(m.group(2))) if m else (i or '', 0)


def rows_of(ws):
    head = [c.value for c in ws[1]]
    for r in ws.iter_rows(min_row=2, values_only=True):
        d = dict(zip(head, r))
        if d.get('ID'):
            yield d


def clean(v):
    return ' '.join(str(v).split()) if v not in (None, '') else ''


def block(label, v):
    if v in (None, ''):
        return []
    s = str(v).strip()
    if '\n' in s or s.startswith(('sp {', '(')):
        return [f'*{label}:*', '', '```', s, '```', '']
    return [f'*{label}:* {clean(s)}', '']


def main(src, dst, title=None):
    wb = openpyxl.load_workbook(src, data_only=True)
    title = title or (clean(wb['README']['A1'].value) if 'README' in wb.sheetnames else src)
    meanings = {}
    if 'Levels' in wb.sheetnames:
        for r in wb['Levels'].iter_rows(min_row=2, values_only=True):
            if r[0] and r[0] != 'Total' and re.match(r'L\d+', str(r[0])):
                meanings[r[0]] = clean(r[1])
    sheets = [n for n in ('Conventions', 'Thor-specific') if n in wb.sheetnames]
    rows = [d for n in sheets for d in rows_of(wb[n])]
    topic_col = 'Subject' if 'Subject' in rows[0] else 'Area'
    rows.sort(key=lambda d: (level_key(d['Level']), TOPIC_POS.get(d[topic_col], 999), id_key(d['ID'])))

    levels = []
    for d in rows:
        if not levels or levels[-1] != d['Level']:
            levels.append(d['Level'])
    for lv in meanings:                      # levels defined but still empty
        if lv not in levels:
            levels.append(lv)
    levels.sort(key=level_key)
    count = {lv: sum(1 for d in rows if d['Level'] == lv) for lv in levels}
    count.update({lv: 0 for lv in meanings if lv not in count})

    now = datetime.now().strftime('%d %B %Y, %H:%M')
    out = [f'# {title}', '',
           f'Generated {now} by `gen_spec.py` from `{src.split("/")[-1]}` ({len(rows)} rows). '
           'Do not edit by hand: change the workbook and rebuild. '
           'Rows are ordered by level, then by topic in development order, then by ID.', '',
           '## Levels', '', '| Level | Rows | Meaning |', '|---|---|---|']
    for lv in levels:
        anchor = re.sub(r'[^a-z0-9 -]', '', lv.lower()).replace(' ', '-')
        out.append(f'| [{lv}](#{anchor}) | {count[lv]} | {meanings.get(lv, "")} |')
    out.append('')

    cur_lv = cur_topic = None
    empty = [lv for lv in levels if count[lv] == 0]
    for d in rows:
        if d['Level'] != cur_lv:
            cur_lv, cur_topic = d['Level'], None
            out += [f'## {cur_lv}', '']
            if meanings.get(cur_lv):
                out += [meanings[cur_lv], '']
        if d[topic_col] != cur_topic:
            cur_topic = d[topic_col]
            out += [f'### {cur_topic}', '']
        tags = [t for t in (d.get('Type'), d.get('Strength'), d.get('Kind')) if t]
        if d.get('Capacity'):
            tags.append(f'capacity: {clean(d["Capacity"])}')
        if d.get('Status') and clean(d['Status']) != 'Proposed':
            tags.append(f'status: {clean(d["Status"])}')
        if clean(d.get('World-Conventions')) == 'Shared':
            tags.append('shared with World-Conventions')
        old = clean(d.get('Old ID'))
        if old and old != 'None' and old != d['ID']:
            tags.append(f'formerly {old}')
        out += [f'**{d["ID"]}**' + (f' ({", ".join(tags)})' if tags else '') + f' — {clean(d["Convention"])}', '']
        out += block('Rationale', d.get('Rationale'))
        out += block('If violated', d.get('If violated'))
        out += block('Exceptions', d.get('Exceptions'))
        out += block('Example', d.get('Example'))
        out += block('Task supplies', d.get('Task supplies'))
        out += block('Library rules', d.get('Library rules'))
        refs = [x for x in (d.get('Parent') and f'parent {d["Parent"]}',
                            d.get('Related rows') and f'related {clean(d["Related rows"])}') if x]
        if refs:
            out += [f'*See:* {"; ".join(refs)}', '']
        if d.get('Source'):
            out += [f'*Source:* {clean(d["Source"])}', '']
    for lv in empty:
        out += [f'## {lv}', '']
        if meanings.get(lv):
            out += [meanings[lv], '']
        out += ['No conventions at this level yet.', '']
    open(dst, 'w', encoding='utf-8', newline='\n').write('\n'.join(out).rstrip() + '\n')
    print(f'{dst}: {len(rows)} rows, {len(levels)} levels')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
