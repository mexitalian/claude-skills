import json
import os

from conftest import read, run, write

GLOSSARY = "# Glossary\n\n### Registration\nMeaning.\n\n### Snapshot\nMeaning.\n"


def make(tmp_path, note, terms=None, newline=None):
    v = tmp_path / "v"
    write(str(v / "Glossary.md"), GLOSSARY)
    write(str(v / "Notes" / "n.md"), note, newline=newline)
    cfg = {"glossary_note": "Glossary", "skip_sections": ["Sources"],
           "terms": terms or [["registration", "Registration"], ["snapshots?", "Snapshot"]]}
    write(str(v / "glossary_terms.json"), json.dumps(cfg))
    return str(v)


def note_text(v):
    return read(os.path.join(v, "Notes", "n.md"))


def test_example_vault_is_already_fully_linked(example):
    code, out = run("glossary", example)
    assert code == 0 and "Would link 0 term(s)" in out


def test_dry_run_changes_nothing(tmp_path):
    v = make(tmp_path, "The registration took a week.\n")
    code, out = run("glossary", v)
    assert code == 0 and "Would link 1 term(s)" in out
    assert note_text(v) == "The registration took a week.\n"


def test_links_first_mention_only_keeping_the_word(tmp_path):
    v = make(tmp_path, "Registration first. Then registration again.\nA snapshot.\n")
    run("glossary", v, "--apply")
    t = note_text(v)
    assert t.count("[[Glossary#Registration|Registration]]") == 1
    assert "Then registration again." in t
    assert "[[Glossary#Snapshot|snapshot]]" in t


def test_is_idempotent(tmp_path):
    v = make(tmp_path, "The registration took a week.\n")
    run("glossary", v, "--apply")
    once = note_text(v)
    code, out = run("glossary", v, "--apply")
    assert note_text(v) == once and "Linked 0 term(s)" in out


def test_skips_frontmatter_headings_code_cards_links_and_skip_sections(tmp_path):
    note = ("---\ntitle: registration\n---\n# Registration heading\n"
            "```\nregistration in code\n```\n"
            "Card :: registration answer\n"
            "See [[registration notes]] and `registration`.\n"
            "## Sources\n- registration page\n")
    v = make(tmp_path, note)
    code, out = run("glossary", v, "--apply")
    assert "Linked 0 term(s)" in out
    assert note_text(v) == note


def test_keeps_windows_line_endings(tmp_path):
    v = make(tmp_path, "One registration.\r\nTwo.\r\n", newline="")
    run("glossary", v, "--apply")
    t = note_text(v)
    assert "[[Glossary#Registration|registration]]" in t
    assert t.count("\r\n") == 2


def test_unknown_heading_is_an_error(tmp_path):
    v = make(tmp_path, "x\n", terms=[["foo", "Not a heading"]])
    code, out = run("glossary", v)
    assert code != 0 and "Not a heading" in out


def test_missing_terms_file_is_an_error(tmp_path):
    v = tmp_path / "v"
    write(str(v / "Glossary.md"), GLOSSARY)
    code, out = run("glossary", str(v))
    assert code != 0 and "terms file not found" in out
