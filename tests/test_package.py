"""Checks on the plugin itself: manifests, skill metadata, templates, and no leaked personal data."""
import glob
import json
import os
import re
import shutil

import pytest

from conftest import ROOT, SKILLS, audit, write

SKILL_DIRS = sorted(glob.glob(os.path.join(SKILLS, "*")))


def frontmatter(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, "%s has no frontmatter" % path
    meta = dict(re.findall(r"^(\w+): (.*)$", m.group(1), re.M))
    return meta, text[m.end():]


def test_manifests_parse_and_agree():
    market = json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
    plugin = json.load(open(os.path.join(ROOT, "plugins", "obsidian-vault-kit", ".claude-plugin", "plugin.json"), encoding="utf-8"))
    assert market["plugins"][0]["name"] == plugin["name"] == "obsidian-vault-kit"
    assert re.fullmatch(r"\d+\.\d+\.\d+", plugin["version"])


def test_plugin_version_matches_changelog():
    plugin = json.load(open(os.path.join(ROOT, "plugins", "obsidian-vault-kit", ".claude-plugin", "plugin.json"), encoding="utf-8"))
    changelog = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
    assert "## %s" % plugin["version"] in changelog


@pytest.mark.parametrize("skill", SKILL_DIRS, ids=os.path.basename)
def test_skill_metadata_follows_the_authoring_rules(skill):
    meta, body = frontmatter(os.path.join(skill, "SKILL.md"))
    name = meta["name"]
    desc = meta["description"].strip('"')
    assert name == os.path.basename(skill)
    assert re.fullmatch(r"[a-z0-9-]{1,64}", name)
    assert "claude" not in name and "anthropic" not in name
    assert 0 < len(desc) <= 1024 and "<" not in desc
    assert len(body.splitlines()) < 500


@pytest.mark.parametrize("skill", SKILL_DIRS, ids=os.path.basename)
def test_files_named_in_a_skill_exist(skill):
    _, body = frontmatter(os.path.join(skill, "SKILL.md"))
    for ref in set(re.findall(r"`((?:scripts|assets|references)/[^`*<>]+?)`", body)):
        path = ref.split(" <")[0].split(" --")[0].split(" [")[0]
        assert os.path.exists(os.path.join(skill, path)), ref


def test_templates_alone_build_a_clean_vault(tmp_path):
    """A vault assembled only from the skills' assets passes every audit layer."""
    v = tmp_path / "v"
    cb = os.path.join(SKILLS, "obsidian-casebook", "assets")
    rc = os.path.join(SKILLS, "obsidian-learning-recall", "assets")
    shutil.copytree(rc, v)
    for f in ("Dashboard.md", "Glossary.md", "Cases.base", "Learnings.base"):
        shutil.copy(os.path.join(cb, f), v / f)
    os.makedirs(v / "Templates")
    for name in ("Study note.md", "Concept.md"):
        shutil.move(str(v / name), str(v / "Templates" / name))
    for name in ("Case.md", "Learning.md"):
        shutil.copy(os.path.join(cb, name), str(v / "Templates" / name))
    write(str(v / ".obsidian" / "types.json"), json.dumps({"types": {"confidence": "number", "last_reviewed": "date"}}))
    write(str(v / ".obsidian" / "community-plugins.json"), json.dumps(["obsidian-spaced-repetition"]))
    code, out, counts = audit(str(v))
    assert counts["FAIL"] == 0 and counts["WARN"] == 0, out


PERSONAL = re.compile(r"/Users/[a-z]|@gmail\.com|charlos\.co|\b[0-9a-f]{26}@group\.calendar", re.I)


def test_no_personal_data_in_the_repo():
    hits = []
    for path in glob.glob(os.path.join(ROOT, "**", "*"), recursive=True):
        if os.path.isdir(path) or "/.git/" in path or "/tests/" in path or path.endswith((".zip", ".pyc")):
            continue
        for n, line in enumerate(open(path, encoding="utf-8", errors="ignore"), 1):
            if PERSONAL.search(line):
                hits.append("%s:%d" % (os.path.relpath(path, ROOT), n))
    assert not hits, hits


EVALS = os.path.join(ROOT, "plugins", "obsidian-vault-kit", "evals")
CASES = sorted(d for d in glob.glob(os.path.join(EVALS, "*")) if os.path.isdir(d) and os.path.basename(d) != "results")
GRADER_TYPES = {"regex", "tool_used", "tool_order", "file_exists", "llm", "baseline"}


@pytest.mark.parametrize("case", CASES, ids=os.path.basename)
def test_eval_cases_are_well_formed(case):
    """Each eval case has a prompt, at least one grader of a known type, and a runnable seed script if it uses one."""
    prompt = open(os.path.join(case, "prompt.md"), encoding="utf-8").read()
    assert re.match(r"---\n.*?\n---\n\s*\S", prompt, re.S), "prompt.md needs frontmatter and a prompt"
    graders = glob.glob(os.path.join(case, "graders", "*.md"))
    assert graders, "no graders"
    for g in graders:
        m = re.match(r"---\n(.*?)\n---", open(g, encoding="utf-8").read(), re.S)
        assert m and re.search(r"^type: (\w+)", m.group(1), re.M).group(1) in GRADER_TYPES, g
    yaml_path = os.path.join(case, "case.yaml")
    if os.path.exists(yaml_path) and "scaffold_script" in open(yaml_path).read():
        assert os.access(os.path.join(case, "seed.sh"), os.X_OK), "seed.sh must be executable"


def test_seed_script_copies_the_example_vault(tmp_path):
    import subprocess
    seed = os.path.join(EVALS, "casebook-letter-arrived", "seed.sh")
    subprocess.run(["bash", seed], cwd=str(tmp_path), check=True)
    assert (tmp_path / "vault" / "Cases" / "Register new address.md").exists()
