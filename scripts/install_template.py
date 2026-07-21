#!/usr/bin/env python3
"""Install the research workflow template into a target repository."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "template"


def copy_tree(src: Path, dst: Path, force: bool, written: list[Path], skipped: list[Path]) -> None:
    for item in src.iterdir():
        if item.name == "__pycache__" or item.suffix.lower() == ".pyc":
            continue
        target = dst / item.name
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            copy_tree(item, target, force, written, skipped)
            continue

        if target.exists() and not force:
            skipped.append(target)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        written.append(target)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy the interactive research workflow template into a repository."
    )
    parser.add_argument("--target", default=".", help="target repository root")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args()

    target = Path(args.target).resolve()
    if not TEMPLATE_ROOT.exists():
        print(f"template not found: {TEMPLATE_ROOT}")
        return 1

    written: list[Path] = []
    skipped: list[Path] = []
    copy_tree(TEMPLATE_ROOT, target, args.force, written, skipped)

    print(f"target: {target}")
    print(f"written: {len(written)}")
    for path in written:
        print(f"+ {path.relative_to(target)}")

    if skipped:
        print(f"skipped_existing: {len(skipped)}")
        for path in skipped:
            print(f"= {path.relative_to(target)}")
        print("rerun with --force only if the user explicitly wants to overwrite files")

    print("done: fill project_plan.md, then ask Codex to generate ans_qes/prompt1.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
