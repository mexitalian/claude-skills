import json
import os

from conftest import read, run, write

TRACK = """# Track
- [ ] Call dentist ⏰ 10:00 ⏱ 1h30m #calls #cal ⏫ 📅 2026-12-01
    - bring card
    - [ ] subtask
- [ ] Not synced #email 📅 2026-12-02
- [ ] #calendar is not the cal tag 📅 2026-12-03
- [ ] Has block ref #cal 📅 2026-12-06 ^myref
* [ ] Star bullet #cal 📅 2026-12-07
- [ ] No date #cal

```
- [ ] Example in a code block #cal 📅 2026-12-08
```
"""


def make(tmp_path):
    v = tmp_path / "v"
    write(str(v / "Notes" / "Track.md"), TRACK)
    return str(v)


def listing(vault):
    code, out = run("cal", "--vault", vault, "list")
    assert code == 0, out
    return json.loads(out)


def test_example_vault_lists_its_cal_tasks(example):
    data = listing(example)
    titles = {t["title"] for t in data["tasks"]}
    assert "Send the new address to the bank" in titles
    assert data["problems"] == []


def test_list_parses_time_duration_priority_and_notes(tmp_path):
    t = {x["title"]: x for x in listing(make(tmp_path))["tasks"]}
    dentist = t["Call dentist"]
    assert (dentist["date"], dentist["time"], dentist["duration_min"]) == ("2026-12-01", "10:00", 90)
    assert dentist["priority"] == "high"
    assert dentist["notes"] == "bring card"


def test_only_the_exact_cal_tag_counts_and_code_blocks_are_skipped(tmp_path):
    titles = {x["title"] for x in listing(make(tmp_path))["tasks"]}
    assert "Not synced" not in titles
    assert not any("is not the cal tag" in x for x in titles)
    assert not any("code block" in x for x in titles)
    assert "Star bullet" in titles


def test_block_reference_is_not_part_of_the_title(tmp_path):
    titles = {x["title"] for x in listing(make(tmp_path))["tasks"]}
    assert "Has block ref" in titles


def test_task_without_a_date_is_reported_as_a_problem(tmp_path):
    problems = " ".join(map(str, listing(make(tmp_path))["problems"]))
    assert "no 📅 date" in problems and "Track.md:9" in problems


def test_assign_dry_run_changes_nothing(tmp_path):
    v = make(tmp_path)
    path = os.path.join(v, "Notes", "Track.md")
    before = read(path)
    code, out = run("cal", "--vault", v, "assign")
    assert code == 0 and "DRY RUN" in out
    assert read(path) == before


def test_assign_apply_adds_ids_before_block_refs_and_is_idempotent(tmp_path):
    v = make(tmp_path)
    path = os.path.join(v, "Notes", "Track.md")
    assert run("cal", "--vault", v, "assign", "--apply")[0] == 0
    text = read(path)
    line = next(l for l in text.splitlines() if "Has block ref" in l)
    assert line.endswith(" ^myref") and "🆔 cal-" in line
    assert "Example in a code block #cal 📅 2026-12-08\n" in text  # untouched
    once = read(path)
    run("cal", "--vault", v, "assign", "--apply")
    assert read(path) == once


def test_assign_keeps_windows_line_endings(tmp_path):
    v = tmp_path / "v"
    write(str(v / "crlf.md"), "# CRLF\r\n- [ ] CRLF task #cal 📅 2026-12-04\r\n- [ ] Other\r\n", newline="")
    run("cal", "--vault", str(v), "assign", "--apply")
    text = read(str(v / "crlf.md"))
    assert "🆔 cal-" in text
    assert text.count("\r\n") == 3 and "\n" not in text.replace("\r\n", "")


def test_duplicate_ids_are_reported(tmp_path):
    v = tmp_path / "v"
    write(str(v / "a.md"), "- [ ] One #cal 📅 2026-12-01 🆔 cal-aaaaaa\n- [ ] Two #cal 📅 2026-12-02 🆔 cal-aaaaaa\n")
    problems = " ".join(map(str, listing(str(v))["problems"]))
    assert "cal-aaaaaa" in problems


def test_missing_vault_is_an_error(tmp_path):
    code, out = run("cal", "--vault", str(tmp_path / "nope"), "list")
    assert code != 0 and "not found" in out
