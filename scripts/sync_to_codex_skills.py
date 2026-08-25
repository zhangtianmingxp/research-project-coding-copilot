#!/usr/bin/env python3
"""Sync this skill source tree into the local Codex skills directory."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


SKILL_NAME = "research-project-coding-copilot"
SOURCE_ROOT = Path(__file__).resolve().parents[1]
OBSOLETE_FILES = (
    "assets/template/.gitignore",
    "assets/template/.research_agent/templates/commit_template.md",
    "references/original_bootstrap_prompt.md",
)


def default_codex_home() -> Path:
    env = os.environ.get("CODEX_HOME")
    if env:
        return Path(env).expanduser().resolve()
    return Path.home() / ".codex"


def should_skip(path: Path) -> bool:
    rel = path.relative_to(SOURCE_ROOT).as_posix()
    if any(part.startswith(".tmp") for part in Path(rel).parts):
        return True
    if rel == ".git" or rel.startswith(".git/"):
        return True
    if rel == ".vscode" or rel.startswith(".vscode/"):
        return True
    if rel == "__pycache__" or "/__pycache__/" in rel:
        return True
    if rel.endswith(".pyc"):
        return True
    return False


def sync_tree(source: Path, target: Path) -> list[Path]:
    written: list[Path] = []
    for item in source.rglob("*"):
        if should_skip(item):
            continue
        rel = item.relative_to(source)
        dst = target / rel
        if item.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dst)
        written.append(dst)
    return written


def remove_obsolete_files(target: Path) -> list[Path]:
    removed: list[Path] = []
    for relative in OBSOLETE_FILES:
        path = target / relative
        if path.is_file():
            path.unlink()
            removed.append(path)
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync skill source to Codex skills directory.")
    parser.add_argument(
        "--target",
        default=None,
        help="skill install directory; defaults to $CODEX_HOME/skills/research-project-coding-copilot",
    )
    args = parser.parse_args()

    target = (
        Path(args.target).expanduser().resolve()
        if args.target
        else default_codex_home() / "skills" / SKILL_NAME
    )
    target.mkdir(parents=True, exist_ok=True)
    written = sync_tree(SOURCE_ROOT, target)
    removed = remove_obsolete_files(target)

    print(f"source: {SOURCE_ROOT}")
    print(f"target: {target}")
    print(f"written: {len(written)}")
    print(f"removed_obsolete: {len(removed)}")
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
