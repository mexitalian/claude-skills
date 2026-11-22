#!/usr/bin/env python3
"""audit_vault.py: read-only audit of an Obsidian vault built with the obsidian-casebook,
obsidian-learning-recall and course-to-obsidian-vault skills. Prints findings; changes nothing.

  python3 audit_vault.py <vault> [--stale-months 12] [--only core|recall|course]

Layers:
  core    always: links and embeds (and #heading anchors), orphans, unsafe file names,
          literal backslash-n, case and learning notes, stale learnings, possible sensitive
          numbers (masked), ??? decision stubs, .stignore, Dashboard Tasks queries
  recall  when the vault has study/lesson notes or a Review Queue.base
  course  when the vault has a Courses/ folder
Levels: FAIL (broken), WARN (differs from the skill or needs attention), INFO (for the record).
Python 3.9+, standard library only. MIT licence.
"""
import argparse, datetime, json, os, re, sys

SKIP_DIRS = {'.obsidian', '.trash', '.git', 'node_modules', '.claudian', '.stversions'}
BAD_NAME = re.compile(r'[?:*"<>|]')
FENCE = re.compile(r'^\s*(```|~~~).*?^\s*\1', re.S | re.M)
INLINE_CODE = re.compile(r'`[^`\n]*`')
LINK = re.compile(r'(!?)\[\[([^\]\n]+)\]\]')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
TASK = re.compile(r'^\s*[-*+] \[(.)\] (.*)$', re.M)

F = []


def add(level, area, msg):
    F.append((level, area, msg))


# ---------- frontmatter (small YAML subset: scalars, [a, b] lists, block lists) ----------
def parse_scalar(v):
    v = v.strip()
    if v == '' or v in ('null', '~'):
        return None
    if (v[0] == v[-1]) and v[0] in '"\'' and len(v) >= 2:
        return v[1:-1]
    if v.startswith('[') and v.endswith(']'):
        return [parse_scalar(x) for x in v[1:-1].split(',') if x.strip()]
    if v in ('true', 'false'):
        return v == 'true'
    if re.fullmatch(r'-?\d+', v):
        return int(v)
    if re.fullmatch(r'-?\d+\.\d+', v):
        return float(v)
    return re.sub(r'\s+#.*$', '', v)


def frontmatter(text):
    m = re.match(r'---\r?\n(.*?)\r?\n---\s*(\r?\n|$)', text, re.S)
    if not m:
        return None
    d, key = {}, None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        km = re.match(r'([A-Za-z_][\w-]*):\s*(.*)$', line)
        if km and not line.startswith((' ', '\t', '-')):
            key = km.group(1)
            d[key] = parse_scalar(km.group(2))
            continue
        lm = re.match(r'\s*-\s+(.*)$', line)
        if lm and key:
            if not isinstance(d.get(key), list):
                d[key] = []
            d[key].append(parse_scalar(lm.group(1)))
    return d


def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if x is not None]
    return re.findall(r'[\w/-]+', str(v))


def as_date(v):
    if isinstance(v, datetime.date):
        return v
    if v is None or not DATE.match(str(v)):
        return None
    try:
        return datetime.date.fromisoformat(str(v))
    except ValueError:
        return None


def strip_code(t):
    return INLINE_CODE.sub('', FENCE.sub('', t))


def sections(t):
    return re.findall(r'^## (.+?)\s*$', strip_code(t), re.M)


def section_body(t, name):
    m = re.search(r'^## ' + re.escape(name) + r'[^\n]*\n(.*?)(?=^## |\Z)', t, re.S | re.M)
    return m.group(1) if m else ''


# ---------- privacy ----------
IBAN = re.compile(r'\b([A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){2,7}(?: ?[A-Z0-9]{1,3})?)\b')
DIGITS = re.compile(r'(?<![\w.-])(\d(?:[ -]?\d){10,18})(?![\w.-])')


def iban_ok(s):
    s = s.replace(' ', '')
    if not 15 <= len(s) <= 34:
        return False
    r = s[4:] + s[:4]
    try:
        return int(''.join(str(int(c, 36)) for c in r)) % 97 == 1
    except ValueError:
        return False


def luhn_ok(s):
    total, alt = 0, False
    for c in reversed(s):
        n = int(c)
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return total % 10 == 0


def privacy_scan(rel, text):
    for i, line in enumerate(text.split('\n'), 1):
        for m in IBAN.finditer(line):
            if iban_ok(m.group(1)):
                add('WARN', 'privacy', '%s:%d: looks like a bank account number (IBAN ...%s)' % (rel, i, m.group(1).replace(' ', '')[-4:]))
        for m in DIGITS.finditer(line):
            raw = re.sub(r'[ -]', '', m.group(1))
            if 13 <= len(raw) <= 19 and luhn_ok(raw) and len(set(raw)) > 1:
                add('WARN', 'privacy', '%s:%d: looks like a card number (...%s)' % (rel, i, raw[-4:]))
            elif len(raw) == 11 and ' ' not in m.group(1) and '-' not in m.group(1):
                add('INFO', 'privacy', '%s:%d: 11-digit number, possibly a tax ID (...%s)' % (rel, i, raw[-4:]))


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('vault')
    ap.add_argument('--stale-months', type=int, default=12)
    ap.add_argument('--only', choices=['core', 'recall', 'course'])
    a = ap.parse_args()
    V = os.path.abspath(os.path.expanduser(a.vault))
    if not os.path.isdir(V):
        ap.error('vault folder not found: %s' % V)
    today = datetime.date.today()

    files = []
    for root, dirs, fs in os.walk(V):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        files += [os.path.join(root, f) for f in fs]
    rel = lambda p: os.path.relpath(p, V)
    md = sorted(p for p in files if p.endswith('.md'))
    text = {p: open(p, encoding='utf-8', errors='replace').read() for p in md}
    meta = {p: (frontmatter(text[p]) or {}) for p in md}
    is_tpl = lambda p: rel(p).replace(os.sep, '/').split('/')[0] == 'Templates' or '/Templates/' in '/' + rel(p).replace(os.sep, '/')
    of_type = lambda *ts: [p for p in md if meta[p].get('type') in ts and not is_tpl(p)]

    has_recall = bool(of_type('lesson', 'study')) or os.path.exists(os.path.join(V, 'Review Queue.base'))
    has_course = os.path.isdir(os.path.join(V, 'Courses'))
    run = {'core': a.only in (None, 'core'), 'recall': a.only in (None, 'recall') and has_recall,
           'course': a.only in (None, 'course') and has_course}

    # ===== core =====
    if run['core']:
        for p in files:
            if BAD_NAME.search(os.path.basename(p)):
                add('WARN', 'files', '%s: name has a character Android/Windows sync cannot store (? : * " < > |)' % rel(p))
        names = {}
        for p in files:
            b = os.path.basename(p)
            names.setdefault(b[:-3] if b.endswith('.md') else b, p)
        heads = {}
        inbound = {}
        for p in md:
            t = strip_code(text[p])
            for bang, target in LINK.findall(t):
                target = target.split('|')[0].strip()
                name, _, anchor = target.partition('#')
                name = name.strip().split('/')[-1]
                if name.endswith('.md'):
                    name = name[:-3]
                if not name:
                    continue
                if name not in names:
                    add('FAIL', 'links', '%s: %slink to missing "%s"' % (rel(p), 'embedded ' if bang else '', name))
                    continue
                inbound.setdefault(name, set()).add(p)
                tp = names[name]
                if anchor and tp.endswith('.md') and not anchor.startswith('^'):
                    if tp not in heads:
                        heads[tp] = {h.strip().lower() for h in re.findall(r'^#{1,6} (.+?)\s*#*\s*$', text.get(tp, ''), re.M)}
                    if anchor.strip().lower() not in heads[tp]:
                        add('WARN', 'links', '%s: link to "%s#%s" but that heading does not exist' % (rel(p), name, anchor))
            if '<small>' in text[p]:
                add('FAIL', 'format', '%s: <small> wrapper (breaks links inside it)' % rel(p))
            if re.search(r'(?<!\\)\\n', t):
                add('FAIL', 'format', '%s: literal backslash-n text (a script wrote \\n instead of a newline)' % rel(p))
            q = text[p].count('???')
            if q and not is_tpl(p):
                add('INFO', 'decisions', '%s: %d decision stub(s) with ??? waiting for the user' % (rel(p), q))
            if not is_tpl(p):
                privacy_scan(rel(p), text[p])

        # cases
        KINDS = ('bureaucracy', 'tech', 'project')
        STAT = ('active', 'waiting', 'blocked', 'done', 'dropped')
        CASE_SECS = ['✅ Tasks', "What's needed|Scope", 'Log', 'Decisions', 'Learned here', 'Contacts and channels', 'Sources']
        for p in of_type('case'):
            d, t, n = meta[p], text[p], rel(p)
            for k in ('kind', 'status', 'counterpart', 'goal', 'started', 'tags'):
                if k not in d:
                    add('WARN', 'cases', '%s: property "%s" missing' % (n, k))
            if d.get('kind') not in KINDS:
                add('WARN', 'cases', '%s: kind %r is not one of %s' % (n, d.get('kind'), ', '.join(KINDS)))
            st = d.get('status')
            if st not in STAT:
                add('WARN', 'cases', '%s: status %r is not one of %s' % (n, st, ', '.join(STAT)))
            if d.get('started') is not None and not as_date(d.get('started')):
                add('FAIL', 'cases', '%s: started %r is not YYYY-MM-DD' % (n, d.get('started')))
            if '[!summary]' not in t:
                add('WARN', 'cases', '%s: no "Where this stands" summary callout' % n)
            hs = sections(t)
            pos = []
            for s in CASE_SECS:
                found = [i for i, h in enumerate(hs) if any(h.startswith(x) for x in s.split('|'))]
                if not found:
                    add('WARN', 'cases', '%s: section "## %s" missing' % (n, s.split('|')[0]))
                else:
                    pos.append(found[0])
            if pos != sorted(pos):
                add('INFO', 'cases', '%s: sections are in a different order from the template' % n)
            log = section_body(t, 'Log')
            dates = re.findall(r'^### (\d{4}-\d{2}-\d{2})', log, re.M)
            if log.strip() and not dates:
                add('WARN', 'cases', '%s: Log has no "### YYYY-MM-DD" entries' % n)
            if dates != sorted(dates, reverse=True):
                add('WARN', 'cases', '%s: Log is not newest first' % n)
            tasks = TASK.findall(strip_code(t))
            open_t = [b for s, b in tasks if s == ' ']
            if st in ('active', 'blocked') and not open_t:
                add('WARN', 'cases', '%s: %s case with no open task (no next action)' % (n, st))
            if st in ('done', 'dropped') and open_t:
                add('WARN', 'cases', '%s: %s but %d open task(s) left' % (n, st, len(open_t)))
            if st in ('done', 'dropped') and not d.get('closed'):
                add('INFO', 'cases', '%s: %s but no "closed" date' % (n, st))
            for b in open_t:
                if '#waiting-for' in b:
                    m = re.search(r'📅\s*(\d{4}-\d{2}-\d{2})', b)
                    dd = as_date(m.group(1)) if m else None
                    if dd and dd < today:
                        add('INFO', 'cases', '%s: waiting-for item past its chase date (%s)' % (n, dd))
                    if not m:
                        add('INFO', 'cases', '%s: waiting-for item without a 📅 chase date' % n)

        # learnings and concepts
        BASIS = ('official', 'experience', 'reported', 'assumption')
        stale_days = a.stale_months * 30.44
        for p in of_type('learning'):
            d, n = meta[p], rel(p)
            for k in ('area', 'kind', 'basis', 'last_verified', 'tags'):
                if k not in d:
                    add('WARN', 'learnings', '%s: property "%s" missing' % (n, k))
            if d.get('basis') not in BASIS:
                add('WARN', 'learnings', '%s: basis %r is not one of %s' % (n, d.get('basis'), ', '.join(BASIS)))
            elif d.get('basis') == 'assumption':
                add('INFO', 'learnings', '%s: basis is still "assumption" (not checked yet)' % n)
            lv = d.get('last_verified')
            if lv is not None and not as_date(lv):
                add('FAIL', 'learnings', '%s: last_verified %r is not YYYY-MM-DD' % (n, lv))
            elif as_date(lv) and (today - as_date(lv)).days > stale_days:
                add('WARN', 'learnings', '%s: last verified %s, over %d months ago: re-check it' % (n, lv, a.stale_months))
            for s in ('How it actually works', 'Evidence', 'Seen in'):
                if s not in sections(text[p]):
                    add('WARN', 'learnings', '%s: section "## %s" missing' % (n, s))
        for kind, label in (('learning', 'learning'), ('concept', 'concept')):
            for p in of_type(kind):
                nm = os.path.basename(p)[:-3]
                if not any(q != p for q in inbound.get(nm, ())):
                    add('WARN', 'links', 'orphan %s (no other note links to it): %s' % (label, nm))
        cases = of_type('case')
        for p in cases:
            nm = os.path.basename(p)[:-3]
            if not any(q != p for q in inbound.get(nm, ())):
                add('INFO', 'links', 'case not linked from any note (still listed in Cases.base): %s' % nm)
        if cases and not os.path.exists(os.path.join(V, 'Cases.base')):
            add('INFO', 'structure', 'vault has cases but no Cases.base')

        # sync, dashboard, config
        sti = os.path.join(V, '.stignore')
        if os.path.exists(sti) or os.path.isdir(os.path.join(V, '.stfolder')):
            si = open(sti, encoding='utf-8').read() if os.path.exists(sti) else ''
            for e in ('.DS_Store', '.obsidian/workspace.json', '.obsidian/workspace-mobile.json', '.trash'):
                if e not in si:
                    add('WARN', 'sync', '.stignore lacks %s' % e)
            if os.path.isdir(os.path.join(V, '.claudian')) and '.claudian' not in si:
                add('INFO', 'sync', '.claudian/ (plugin chat history) syncs to other devices; ask whether to ignore it')
        dash = os.path.join(V, 'Dashboard.md')
        if os.path.exists(dash):
            blocks = re.findall(r'```tasks\n(.*?)```', text[dash], re.S)
            for b in blocks:
                if 'path does not include Templates' not in b:
                    add('WARN', 'dashboard', 'a Tasks query in Dashboard.md does not exclude Templates')
        ty = os.path.join(V, '.obsidian', 'types.json')
        types = {}
        if os.path.exists(ty):
            try:
                types = json.load(open(ty, encoding='utf-8')).get('types', {})
            except ValueError:
                add('FAIL', 'config', '.obsidian/types.json is not valid JSON')
        want = {}
        if cases:
            want.update(started='date', closed='date')
        if of_type('learning'):
            want['last_verified'] = 'date'
        if has_recall:
            want.update(confidence='number', last_reviewed='date')
        for k, v in want.items():
            if types.get(k) != v:
                add('INFO', 'config', '.obsidian/types.json: %s is not "%s" (date picker / number field missing)' % (k, v))

    # ===== recall =====
    plugins = []
    cpf = os.path.join(V, '.obsidian', 'community-plugins.json')
    if os.path.exists(cpf):
        try:
            plugins = json.load(open(cpf, encoding='utf-8'))
        except ValueError:
            add('FAIL', 'config', '.obsidian/community-plugins.json is not valid JSON')
    if run['recall']:
        SECS = ['Before you', 'Start here', 'Picture it', 'The idea', 'In my ', 'Check yourself', 'Cards',
                'Teach it back', 'Actions', 'Concepts used', 'Source']
        notes = of_type('lesson', 'study')
        for p in notes:
            d, t, n = meta[p], text[p], rel(p)
            if 'next_review' in d:
                add('FAIL', 'recall', '%s: stored next_review (it should be computed by the base)' % n)
            c = d.get('confidence')
            if c not in (None, 1, 2, 3, 4):
                add('FAIL', 'recall', '%s: confidence %r is not 1 to 4' % (n, c))
            lr = d.get('last_reviewed')
            if lr is not None and not as_date(lr):
                add('FAIL', 'recall', '%s: last_reviewed %r is not YYYY-MM-DD' % (n, lr))
            if c is not None and lr is None:
                add('INFO', 'recall', '%s: has confidence but no last_reviewed, so it never enters the review queue' % n)
            stt = d.get('status')
            if stt not in ('pending', 'stub', 'captured'):
                add('WARN', 'recall', '%s: status %r is not pending, stub or captured' % (n, stt))
            if stt != 'captured':
                continue
            if 'flashcards' not in as_list(d.get('tags')):
                add('FAIL', 'recall', '%s: captured but no "flashcards" tag in the frontmatter' % n)
            if re.search(r'(^|\s)#flashcards', strip_code(t)):
                add('WARN', 'recall', '%s: inline #flashcards tag next to the frontmatter tag' % n)
            hs = sections(t)
            for s in SECS:
                if not any(h.startswith(s) for h in hs):
                    add('FAIL', 'recall', '%s: section "## %s" missing' % (n, s.strip()))
            labels = t.count('Didactic Methods:')
            if labels < 10:
                add('WARN', 'recall', '%s: %d method labels (expected 10)' % (n, labels))
            if t.count('<details>') > 5:
                add('WARN', 'recall', '%s: %d check-yourself toggles (max 5)' % (n, t.count('<details>')))
            cards = [l for l in section_body(t, 'Cards').split('\n') if ' :: ' in l and not l.lstrip().startswith('>')]
            if len(cards) > 5:
                add('WARN', 'recall', '%s: %d cards (max 5)' % (n, len(cards)))
            if '```mermaid' not in t:
                add('WARN', 'recall', '%s: no Mermaid diagram in "Picture it"' % n)
        for p in md:
            if not is_tpl(p) and 'next_review' in strip_code(text[p]) and 'next_review' not in meta[p]:
                add('WARN', 'recall', '%s: still mentions a stored next_review' % rel(p))

        def rd(name):
            q = os.path.join(V, name)
            return open(q, encoding='utf-8').read() if os.path.exists(q) else None
        rq, sn = rd('Review Queue.base'), rd('Study Notes.base') or rd('Lessons.base')
        if rq is None:
            add('FAIL', 'recall', 'Review Queue.base missing')
        else:
            if 'last_reviewed' not in rq or 'formula' not in rq:
                add('FAIL', 'recall', 'Review Queue.base does not compute the due date from last_reviewed + confidence')
            if '21d' not in rq:
                add('WARN', 'recall', 'Review Queue.base has no 21-day step (rating 4)')
        if sn is None:
            add('WARN', 'recall', 'Study Notes.base (or Lessons.base) missing')
        elif 'formula' not in sn:
            add('WARN', 'recall', 'Study Notes.base has no computed Next review column')
        sh = rd('Start Here.md')
        if sh is not None and not re.search(r'\|\s*4\s*\|[^\n]*21', sh):
            add('WARN', 'recall', 'Start Here rating table has no row 4 (locked in, 21 days)')
        dmdir = os.path.join(V, 'Didactic Methods')
        if any('Didactic Methods:' in text[p] for p in notes):
            k = len([p for p in md if p.startswith(dmdir + os.sep)])
            if k < 13:
                add('WARN', 'recall', 'Didactic Methods has %d notes (expected 13: index + 12 methods)' % k)
        if notes and 'obsidian-spaced-repetition' not in plugins:
            add('WARN', 'config', 'community plugin not enabled: obsidian-spaced-repetition (cards will not run)')

    # ===== course =====
    if run['course']:
        lessons = [p for p in of_type('lesson') if '/Courses/' in '/' + rel(p).replace(os.sep, '/')]
        for p in lessons:
            d, n = meta[p], rel(p)
            for k in ('course', 'week', 'order', 'group', 'video_minutes', 'source'):
                if k not in d:
                    add('WARN', 'course', '%s: property "%s" missing' % (n, k))
            if 'platform_watched' not in d:
                add('WARN', 'course', '%s: property "platform_watched" missing' % n)
        cdir = os.path.join(V, 'Courses')
        for c in sorted(os.listdir(cdir)):
            if os.path.isdir(os.path.join(cdir, c)) and not os.path.exists(os.path.join(cdir, c, c + '.md')):
                add('WARN', 'course', 'Courses/%s has no course map note "%s.md"' % (c, c))
        res = [p for p in files if '/Resources/' in '/' + rel(p).replace(os.sep, '/') and not p.endswith('.md')]
        if res and not os.path.exists(os.path.join(V, 'Resources', 'Resources.md')):
            add('FAIL', 'course', 'Resources/ has files but no Resources.md index')
        linked = set()
        for p in md:
            for _, tg in LINK.findall(strip_code(text[p])):
                linked.add(tg.split('|')[0].split('#')[0].strip().split('/')[-1])
        for p in res:
            b = os.path.basename(p)
            if b not in linked:
                add('WARN', 'course', '%s is not linked from any note' % b)
            if os.path.getsize(p) > 50_000_000:
                add('INFO', 'course', '%s is over 50 MB (consider a link only, plus .stignore)' % b)

    order = {'FAIL': 0, 'WARN': 1, 'INFO': 2}
    F.sort(key=lambda x: (order[x[0]], x[1]))
    layers = [k for k, v in run.items() if v]
    print('AUDIT %s' % V)
    print('layers: %s   notes: %d   cases: %d   learnings: %d   study notes: %d' % (
        ', '.join(layers), len(md), len(of_type('case')), len(of_type('learning')), len(of_type('lesson', 'study'))))
    for lv in ('FAIL', 'WARN', 'INFO'):
        print('%s: %d' % (lv, sum(1 for x in F if x[0] == lv)))
    for lv, area, msg in F:
        print('[%s] %s: %s' % (lv, area, msg))
    sys.exit(1 if any(x[0] == 'FAIL' for x in F) else 0)


if __name__ == '__main__':
    main()
