import os
import re

from conftest import audit, read, write


def case_path(v):
    return os.path.join(v, "Cases", "Register new address.md")


def edit(path, old, new):
    text = read(path)
    assert text.count(old) == 1, old
    write(path, text.replace(old, new), newline="")


def test_example_vault_is_clean_on_all_layers(example):
    code, out, counts = audit(example)
    assert "layers: core, recall, course" in out
    assert counts == {"FAIL": 0, "WARN": 0, "INFO": 0}, out
    assert code == 0


def test_broken_link_fails_and_sets_exit_code(example):
    edit(case_path(example), "## Sources\n", "## Sources\n- [[A note that does not exist]]\n")
    code, out, counts = audit(example)
    assert code == 1 and counts["FAIL"] == 1
    assert 'missing "A note that does not exist"' in out


def test_missing_heading_anchor_warns(example):
    edit(case_path(example), "Glossary#Registration certificate|", "Glossary#No such heading|")
    _, out, _ = audit(example)
    assert "that heading does not exist" in out


def test_log_must_be_newest_first(example):
    edit(case_path(example), "### 2026-11-20\n", "### 2026-10-01\n")
    _, out, _ = audit(example)
    assert "Log is not newest first" in out


def test_active_case_without_open_task_is_flagged(example):
    p = os.path.join(example, "Cases", "Home server backups.md")
    edit(p, "- [ ] Set a monthly reminder", "- [x] Set a monthly reminder")
    _, out, _ = audit(example)
    assert "active case with no open task" in out


def test_overdue_chase_date_is_noted(example):
    edit(case_path(example), "#waiting-for 📅 2026-12-04", "#waiting-for 📅 2026-11-01")
    _, out, _ = audit(example)
    assert "past its chase date" in out


def test_stale_learning_and_bad_basis(example):
    p = os.path.join(example, "Learnings", "Registration appointments are released in the morning.md")
    edit(p, "last_verified: 2026-11-03", "last_verified: 2024-01-10")
    edit(p, "\nbasis: experience\n", "\nbasis: guess\n")
    _, out, _ = audit(example)
    assert "re-check it" in out
    assert "basis 'guess' is not one of" in out


def test_orphan_learning_warns(example):
    write(os.path.join(example, "Learnings", "Lonely rule.md"),
          "---\ntype: learning\narea: x\nkind: tech\nbasis: official\nlast_verified: 2026-11-01\ntags: [learning]\n---\n"
          "# Lonely rule\n## How it actually works\n## Evidence\n## Seen in\n")
    _, out, _ = audit(example)
    assert "orphan learning" in out and "Lonely rule" in out


def test_sensitive_numbers_are_flagged_but_never_printed(example):
    iban = "DE89 3704 0044 0532 0130 00"
    card = "4111 1111 1111 1111"
    edit(case_path(example), "## Sources\n", "## Sources\n- Bank %s and card %s\n" % (iban, card))
    _, out, _ = audit(example)
    assert "bank account number (IBAN ...3000)" in out
    assert "card number (...1111)" in out
    assert iban not in out and iban.replace(" ", "") not in out
    assert card not in out and card.replace(" ", "") not in out


def test_recall_checks(example):
    p = os.path.join(example, "Notes", "How spaced practice works.md")
    edit(p, "confidence: 2\n", "confidence: 5\nnext_review: 2026-12-01\n")
    edit(p, "## Teach it back", "## Teach back")
    edit(p, "## In my life\n", "## In my life\nline one\\nline two\n")
    _, out, counts = audit(example)
    assert "stored next_review" in out
    assert "confidence 5 is not 1 to 4" in out
    assert 'section "## Teach it back" missing' in out
    assert "literal backslash-n" in out
    assert counts["FAIL"] >= 4


def test_only_core_skips_recall_and_course(example):
    p = os.path.join(example, "Notes", "How spaced practice works.md")
    edit(p, "confidence: 2\n", "confidence: 9\n")
    _, out, counts = audit(example, "--only", "core")
    assert "layers: core " in out
    assert "confidence 9" not in out


def test_course_lesson_needs_its_keys(example):
    p = os.path.join(example, "Courses", "Example Course", "Week 1 - Getting started", "W1-01 Welcome and how to study.md")
    edit(p, "video_minutes: 6\n", "")
    _, out, _ = audit(example)
    assert 'property "video_minutes" missing' in out


def test_unsafe_file_name_warns(example):
    write(os.path.join(example, "Notes", "What? Why.md"), "# What\n")
    _, out, _ = audit(example)
    assert re.search(r"What\? Why\.md: name has a character", out)


def test_missing_vault_is_an_error(tmp_path):
    from conftest import run
    code, out = run("audit", str(tmp_path / "nope"))
    assert code != 0 and "not found" in out


def test_whats_needed_checklist_is_not_a_next_action(example):
    p = os.path.join(example, "Cases", "Home server backups.md")
    edit(p, "- [ ] Set a monthly reminder", "- [x] Set a monthly reminder")
    _, out, _ = audit(example)
    assert "Home server backups.md: active case with no open task" in out  # the open Scope box doesn't count
