#!/usr/bin/env python3
"""link_glossary.py: link glossary terms in notes to the glossary note, anchored on the word.

  python3 link_glossary.py <vault> [--terms <file.json>] [--apply]

Dry run by default: prints what would be linked and changes nothing.
Reads <vault>/glossary_terms.json unless --terms is given. Format:
  {
    "glossary_note": "Glossary",                 # note name, without .md
    "folders": ["Cases", "Learnings"],           # folders to scan (default: whole vault)
    "skip_files": ["Glossary.md"],
    "skip_sections": ["Sources", "Cards"],       # "## " sections never touched
    "skip_line_prefixes": ["- [["],              # lines starting with these are skipped
    "terms": [["regex", "### heading in the glossary note"], ...]
  }
Each regex is case-insensitive unless wrapped in (?-i:...).
For each note it links the FIRST plain mention of each term as [[Glossary#Heading|word]].
Safe to re-run: terms already linked in a note are skipped. Never touches frontmatter,
headings, tables, code, cards (::), toggle questions, method labels, existing links or the
glossary note itself. Keeps each file's line endings.
Python 3.9+, standard library only. MIT licence.
"""
import argparse, glob, json, os, re, sys

MASK = re.compile(r"\[\[[^\]]*\]\]|\[[^\]]*\]\([^)]*\)|`[^`]*`|https?://\S+")
FENCE = re.compile(r"^\s*(```|~~~)")
SKIP_DIRS = {".obsidian", ".trash", ".git", "node_modules", "Templates", "_archive"}


def eligible(line, prefixes):
    s = line.strip()
    if not s or s.startswith(("#", "|", ">[!", "> [!")) or s.startswith(tuple(prefixes)):
        return False
    if "::" in line or "<summary>" in line or "Didactic Methods:" in line:
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vault")
    ap.add_argument("--terms")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    vault = os.path.abspath(os.path.expanduser(a.vault))
    if not os.path.isdir(vault):
        ap.error("vault folder not found: %s" % vault)
    cfg_path = a.terms or os.path.join(vault, "glossary_terms.json")
    if not os.path.exists(cfg_path):
        ap.error("terms file not found: %s (copy glossary_terms.example.json there, or pass --terms)" % cfg_path)
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    gnote = cfg["glossary_note"]
    try:
        terms = [(re.compile(p, re.I), h) for p, h in cfg["terms"]]
    except re.error as e:
        sys.exit("bad regex in terms file: %s" % e)
    skip_files = set(cfg.get("skip_files", [])) | {gnote + ".md"}
    skip_secs = tuple("## " + s for s in cfg.get("skip_sections", []))
    prefixes = cfg.get("skip_line_prefixes", [])

    gfiles = glob.glob(os.path.join(vault, "**", gnote + ".md"), recursive=True)
    if not gfiles:
        sys.exit("glossary note '%s' not found in %s" % (gnote, vault))
    headings = {l[4:].strip() for l in open(gfiles[0], encoding="utf-8").read().splitlines() if l.startswith("### ")}
    bad = sorted({h for _, h in terms if h not in headings})
    if bad:
        sys.exit("headings missing in the glossary note: " + ", ".join(bad))

    roots = [os.path.join(vault, f) for f in cfg.get("folders", [])] or [vault]
    files = []
    for r in roots:
        for root, dirs, fs in os.walk(r):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            files += [os.path.join(root, f) for f in fs if f.endswith(".md")]
    existing = re.compile(r"\[\[" + re.escape(gnote) + r"#[^|\]]*\|([^\]]*)\]\]")
    total = 0
    for path in sorted(set(files)):
        if os.path.basename(path) in skip_files:
            continue
        raw = open(path, encoding="utf-8", newline="").read()
        nl = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(nl)
        seen = set()
        for m in existing.finditer(raw):
            for i, (rx, _) in enumerate(terms):
                if rx.fullmatch(m.group(1)):
                    seen.add(i)
        in_fm = bool(lines) and lines[0].strip() == "---"
        in_code, section, edits = False, "", []
        for n, line in enumerate(lines):
            if in_fm:
                if n > 0 and line.strip() == "---":
                    in_fm = False
                continue
            if FENCE.match(line):
                in_code = not in_code
                continue
            if in_code:
                continue
            if line.startswith("## "):
                section = line
                continue
            if skip_secs and section.startswith(skip_secs):
                continue
            if not eligible(line, prefixes):
                continue
            masked = MASK.sub(lambda m: " " * len(m.group(0)), line)
            hits = []
            for i, (rx, head) in enumerate(terms):
                if i in seen:
                    continue
                m = rx.search(masked)
                if m and m.end() > m.start():
                    hits.append((m.start(), m.end(), head, i))
            hits.sort()
            keep = []
            for h in hits:
                if keep and h[0] < keep[-1][1]:
                    continue
                keep.append(h)
            for s, e, head, i in reversed(keep):
                seen.add(i)
                word = line[s:e]
                line = line[:s] + "[[%s#%s|%s]]" % (gnote, head, word) + line[e:]
                edits.append((n + 1, word, head))
            lines[n] = line
        if edits:
            total += len(edits)
            print("==", os.path.relpath(path, vault))
            for n, w, h in sorted(edits):
                print("   L%d: %s  ->  #%s" % (n, w, h))
            if a.apply:
                open(path, "w", encoding="utf-8", newline="").write(nl.join(lines))
    print("\n%s %d term(s)." % ("Linked" if a.apply else "Would link", total))
    if not a.apply and total:
        print("Run again with --apply to write the changes.")


if __name__ == "__main__":
    main()
