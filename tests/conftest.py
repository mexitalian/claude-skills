"""Shared helpers for the script tests. Run with: python -m pytest"""
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "plugins", "obsidian-vault-kit", "skills")
EXAMPLE = os.path.join(ROOT, "examples", "Example vault")
TODAY = "2026-11-23"  # fixed date so stale-learning and chase-date checks don't drift

SCRIPTS = {
    "cal": os.path.join(SKILLS, "obsidian-task-system", "scripts", "cal_tasks.py"),
    "audit": os.path.join(SKILLS, "obsidian-casebook", "scripts", "audit_vault.py"),
    "glossary": os.path.join(SKILLS, "obsidian-casebook", "scripts", "link_glossary.py"),
}


def run(script, *args):
    """Run a bundled script in isolated mode; return (exit code, stdout + stderr)."""
    p = subprocess.run([sys.executable, "-I", SCRIPTS[script], *args],
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout + p.stderr


def audit(vault, *args):
    code, out = run("audit", vault, "--today", TODAY, *args)
    counts = {}
    for level in ("FAIL", "WARN", "INFO"):
        line = next(l for l in out.splitlines() if l.startswith(level + ":"))
        counts[level] = int(line.split(":")[1])
    return code, out, counts


def write(path, text, newline=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline=newline) as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


@pytest.fixture
def example(tmp_path):
    """A fresh copy of the example vault that a test may change."""
    dst = tmp_path / "vault"
    shutil.copytree(EXAMPLE, dst)
    return str(dst)
