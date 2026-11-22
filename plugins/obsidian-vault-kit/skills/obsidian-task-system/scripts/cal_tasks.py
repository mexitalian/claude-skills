#!/usr/bin/env python3
"""cal_tasks.py: list Obsidian Tasks tagged #cal so they can be reconciled with a
Google Calendar. Read-only unless `assign --apply` is used.

  python3 cal_tasks.py --vault "<vault path>" list                 # JSON: open #cal tasks with a 📅 date, plus problems and done tasks
  python3 cal_tasks.py --vault "<vault path>" assign               # dry run: which #cal tasks still need a 🆔 id
  python3 cal_tasks.py --vault "<vault path>" assign --apply       # append "🆔 cal-xxxxxx" to those lines

Convention (one #cal task = one calendar event on its 📅 date):
  - `#cal` tag + 📅 YYYY-MM-DD on an open task.
  - Optional start time and length in the description (before the tags): `⏰ 10:00 ⏱ 1h`.
  - The 🆔 id is the link to the event: the event description carries `obsidian-task: cal-xxxxxx`.
Works on any vault. Python 3.9+, standard library only. MIT licence.
"""
import argparse, hashlib, json, os, re, sys

DEFAULT_VAULT = os.environ.get('OBSIDIAN_VAULT')  # or pass --vault "<path to the vault>"
SKIP_DIRS = {'.obsidian', '.stfolder', '.trash', '.git', 'node_modules', '_migration', '_tools'}
TASK_RE = re.compile(r'^(\s*)[-*+] \[(.)\] (.*?)\r?$')
FENCE_RE = re.compile(r'^\s*(```|~~~)')
BLOCK_REF_RE = re.compile(r'(\s\^[A-Za-z0-9-]+)$')
CAL_TAG_RE = re.compile(r'(?<!\S)#cal(?![\w/-])')
DUE_RE = re.compile(r'📅\s*(\d{4}-\d{2}-\d{2})')
DONE_RE = re.compile(r'✅\s*(\d{4}-\d{2}-\d{2})')
ID_RE = re.compile(r'🆔\s*([A-Za-z0-9_-]+)')
TIME_RE = re.compile(r'⏰\s*(\d{1,2}):(\d{2})')
DUR_RE = re.compile(r'⏱\s*((?:\d+\s*h)?\s*(?:\d+\s*m)?)')
PRIORITY = {'⏫': 'high', '🔼': 'medium', '🔽': 'low', '🔺': 'highest', '⏬': 'lowest'}
STRIP_RES = [
    re.compile(r'(?<!\S)#[\w/-]+'),
    re.compile(r'[⏫🔼🔽🔺⏬]'),
    re.compile(r'[📅⏳🛫✅❌➕]\s*\d{4}-\d{2}-\d{2}'),
    re.compile(r'🔁\s*[^📅⏳🛫✅🆔⏰⏱#⏫🔼🔽]*'),
    re.compile(r'🆔\s*[A-Za-z0-9_-]+'),
    re.compile(r'⛔\s*[A-Za-z0-9_,-]+'),
    re.compile(r'⏰\s*\d{1,2}:\d{2}'),
    re.compile(r'⏱\s*(?:\d+\s*h)?\s*(?:\d+\s*m)?'),
    re.compile(r'\s\^[A-Za-z0-9-]+$'),
]


def clean_title(text):
    for rx in STRIP_RES:
        text = rx.sub('', text)
    return re.sub(r'\s+', ' ', text).strip(' -–—:')


def duration_minutes(text):
    m = DUR_RE.search(text)
    if not m or not m.group(1).strip():
        return None
    h = re.search(r'(\d+)\s*h', m.group(1))
    mi = re.search(r'(\d+)\s*m', m.group(1))
    return (int(h.group(1)) * 60 if h else 0) + (int(mi.group(1)) if mi else 0) or None


def md_files(vault):
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.md'):
                yield os.path.join(root, f)


def scan(vault):
    """Return every #cal task: dicts with file, line index, status, text, etc."""
    found = []
    for path in sorted(md_files(vault)):
        rel = os.path.relpath(path, vault)
        lines = open(path, encoding='utf-8', newline='').read().split('\n')
        in_fence = False
        for i, line in enumerate(lines):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            m = TASK_RE.match(line)
            if not m or not CAL_TAG_RE.search(m.group(3)):
                continue
            indent, status, body = len(m.group(1)), m.group(2), m.group(3)
            notes = []
            for nxt in lines[i + 1:]:
                if not nxt.strip():
                    break
                ni = len(nxt) - len(nxt.lstrip())
                if ni <= indent:
                    break
                if TASK_RE.match(nxt):
                    continue
                notes.append(re.sub(r'^\s*[-*+]\s*', '', nxt).strip())
            due, done, tid = DUE_RE.search(body), DONE_RE.search(body), ID_RE.search(body)
            tm = TIME_RE.search(body)
            prio = next((v for k, v in PRIORITY.items() if k in body), 'normal')
            found.append({
                'id': tid.group(1) if tid else None,
                'title': clean_title(body),
                'date': due.group(1) if due else None,
                'time': '%02d:%s' % (int(tm.group(1)), tm.group(2)) if tm else None,
                'duration_min': duration_minutes(body),
                'priority': prio,
                'status': 'done' if status.lower() == 'x' else ('cancelled' if status == '-' else 'open'),
                'done_date': done.group(1) if done else None,
                'note': rel,
                'line': i + 1,
                'notes': ' | '.join(notes)[:800],
                '_path': path,
            })
    return found


def make_id(rel, title, taken):
    n = 6
    while True:
        cand = 'cal-' + hashlib.sha1(('%s|%s' % (rel, title)).encode('utf-8')).hexdigest()[:n]
        if cand not in taken:
            return cand
        n += 1


def cmd_list(vault):
    tasks = scan(vault)
    out = {'vault': vault, 'tasks': [], 'done': [], 'problems': []}
    ids = {}
    for t in tasks:
        pub = {k: v for k, v in t.items() if k != '_path'}
        where = '%s:%d' % (t['note'], t['line'])
        if t['id']:
            if t['id'] in ids:
                out['problems'].append('duplicate id %s at %s and %s' % (t['id'], ids[t['id']], where))
            ids[t['id']] = where
        if t['status'] == 'open':
            if not t['date']:
                out['problems'].append('#cal task has no 📅 date, cannot be synced: %s' % where)
                continue
            if not t['id']:
                out['problems'].append('#cal task has no 🆔 yet (run assign): %s' % where)
            out['tasks'].append(pub)
        else:
            out['done'].append(pub)
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_assign(vault, apply):
    tasks = scan(vault)
    taken = {t['id'] for t in tasks if t['id']}
    edits = {}
    for t in tasks:
        if t['id'] or t['status'] != 'open':
            continue
        new_id = make_id(t['note'], t['title'], taken)
        taken.add(new_id)
        edits.setdefault(t['_path'], []).append((t['line'] - 1, new_id))
        print('%s %s:%d -> %s  (%s)' % ('ASSIGN' if apply else 'WOULD ASSIGN', t['note'], t['line'], new_id, t['title'][:60]))
    if not edits:
        print('nothing to assign')
        return
    if not apply:
        print('DRY RUN (use --apply to write)')
        return
    for path, items in edits.items():
        content = open(path, encoding='utf-8', newline='').read()
        lines = content.split('\n')
        for idx, new_id in items:
            line = lines[idx]
            cr = '\r' if line.endswith('\r') else ''
            body = line.rstrip()
            ref = BLOCK_REF_RE.search(body)
            tail = ref.group(1) if ref else ''
            body = body[:len(body) - len(tail)].rstrip()
            lines[idx] = body + ' 🆔 ' + new_id + tail + cr
        open(path, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    print('APPLIED')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--vault', default=DEFAULT_VAULT)
    sub = ap.add_subparsers(dest='cmd')
    sub.add_parser('list')
    a = sub.add_parser('assign')
    a.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    if not args.vault:
        ap.error('pass --vault "<vault path>" (or set OBSIDIAN_VAULT)')
    args.vault = os.path.expanduser(args.vault)
    if not os.path.isdir(args.vault):
        ap.error('vault folder not found: %s' % args.vault)
    if args.cmd == 'assign':
        cmd_assign(args.vault, args.apply)
    else:
        cmd_list(args.vault)
