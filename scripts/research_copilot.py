#!/usr/bin/env python3
"""Action CLI for the research-project-coding-copilot skill.

This script operates on a target research repository. It never calls model
APIs, never executes prompt tasks, never commits, and never pushes.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import shutil
import subprocess
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "template"

PROMPT_RE = re.compile(r"^prompt(\d+)\.md$")
RESULT_RE = re.compile(r"^result(\d+)\.md$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

REQUIRED_RESULT_SECTIONS = [
    "对应 Prompt",
    "执行摘要",
    "完成内容",
    "涉及文件",
    "命令记录",
    "验证情况",
    "风险与注意事项",
]

MAX_CONTINUE_ROUNDS = 10

SKIP_CONTEXT_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    "node_modules",
    "catboost_info",
}

GENERATED_OR_LARGE_DIRS = {
    "data",
    "results",
    "outputs",
    "logs",
    "checkpoints",
    "models",
    "weights",
    "runs",
    "wandb",
}

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".r",
    ".sh",
    ".ps1",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
}


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def target_root(args: argparse.Namespace) -> Path:
    return Path(args.target).resolve()


def agent_dir(root: Path) -> Path:
    return root / ".research_agent"


def ans_dir(root: Path) -> Path:
    return root / "ans_qes"


def progress_path(root: Path) -> Path:
    return agent_dir(root) / "progress.json"


def state_path(root: Path) -> Path:
    return agent_dir(root) / "project_state.md"


def load_progress(root: Path) -> dict:
    path = progress_path(root)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_progress(root: Path, progress: dict) -> None:
    progress_path(root).write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def numbered_files(root: Path, pattern: re.Pattern[str]) -> dict[int, Path]:
    directory = ans_dir(root)
    if not directory.exists():
        return {}
    items: dict[int, Path] = {}
    for path in directory.iterdir():
        match = pattern.match(path.name)
        if match:
            items[int(match.group(1))] = path
    return items


def next_round_id(root: Path) -> int:
    used = set(numbered_files(root, PROMPT_RE)) | set(numbered_files(root, RESULT_RE))
    round_id = 1
    while round_id in used:
        round_id += 1
    return round_id


def copy_tree(src: Path, dst: Path, force: bool, written: list[Path], skipped: list[Path]) -> None:
    for item in src.iterdir():
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


def required_paths(root: Path) -> list[Path]:
    return [
        root / "AGENTS.md",
        root / "PROJECT_RULES.md",
        root / "README.md",
        root / "project_plan.md",
        ans_dir(root) / "README.md",
        agent_dir(root) / "AGENTS.md",
        agent_dir(root) / "config.yaml",
        progress_path(root),
        state_path(root),
        agent_dir(root) / "templates" / "prompt_template.md",
        agent_dir(root) / "templates" / "result_template.md",
        agent_dir(root) / "templates" / "commit_template.md",
        root / "scripts" / "research_flow.py",
    ]


def check_pairs(root: Path) -> list[str]:
    problems: list[str] = []
    prompts = numbered_files(root, PROMPT_RE)
    results = numbered_files(root, RESULT_RE)

    for round_id in sorted(results):
        if round_id not in prompts:
            problems.append(f"result{round_id}.md exists without prompt{round_id}.md")

    if prompts:
        expected = set(range(1, max(prompts) + 1))
        for missing in sorted(expected - set(prompts)):
            problems.append(f"missing prompt{missing}.md")

    return problems


def plan_report(root: Path) -> tuple[bool, list[str]]:
    path = root / "project_plan.md"
    if not path.exists():
        return False, ["project_plan.md does not exist"]

    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    warnings: list[str] = []
    placeholders = [
        "请填写项目名称",
        "说明研究领域",
        "问题一",
        "请填写",
    ]
    if len(stripped) < 800:
        warnings.append("project_plan.md looks short; consider filling the research plan before prompt generation")
    if any(token in text for token in placeholders):
        warnings.append("project_plan.md still contains template placeholder text")

    headings = [line.strip() for line in text.splitlines() if line.startswith("## ")]
    if len(headings) < 6:
        warnings.append("project_plan.md has fewer than 6 second-level sections")

    return not warnings, warnings


def update_state_for_prompt(root: Path, round_id: int, prompt_path: Path) -> None:
    progress = load_progress(root)
    progress.update(
        {
            "current_round": round_id,
            "phase": "prompt_drafted",
            "last_prompt": rel(prompt_path, root),
            "auto_next": False,
            "auto_execute_prompt": False,
            "auto_commit": False,
            "auto_push": False,
            "open_issues": [
                "prompt 已生成，等待用户审查；不得自动执行。"
            ],
        }
    )
    save_progress(root, progress)

    state = (
        "# Project State\n\n"
        "## Current Status\n\n"
        f"- current_round: {round_id}\n"
        "- phase: prompt_drafted\n"
        f"- last_prompt: {rel(prompt_path, root)}\n"
        f"- last_result: {progress.get('last_result')}\n"
        f"- last_commit: {progress.get('last_commit')}\n"
        "- auto_next: false\n\n"
        "## Open Issues\n\n"
        "- prompt 已生成，等待用户审查；不得自动执行。\n\n"
        "## Notes\n\n"
        "- 用户确认执行后，才允许读取该 prompt 并生成对应 result。\n"
        "- 本轮结束后必须停止，等待用户下一条明确指令。\n"
    )
    state_path(root).write_text(state, encoding="utf-8")


def update_state_for_result(root: Path, round_id: int, result_path: Path) -> None:
    progress = load_progress(root)
    progress.update(
        {
            "current_round": round_id,
            "phase": "executed",
            "last_result": rel(result_path, root),
            "auto_next": False,
            "auto_execute_prompt": False,
            "auto_commit": False,
            "auto_push": False,
            "open_issues": [
                "result 已生成，等待用户审查。",
                "commit 前必须等待用户明确确认。"
            ],
        }
    )
    if not progress.get("last_prompt"):
        progress["last_prompt"] = f"ans_qes/prompt{round_id}.md"
    save_progress(root, progress)

    state = (
        "# Project State\n\n"
        "## Current Status\n\n"
        f"- current_round: {round_id}\n"
        "- phase: executed\n"
        f"- last_prompt: {progress.get('last_prompt')}\n"
        f"- last_result: {rel(result_path, root)}\n"
        f"- last_commit: {progress.get('last_commit')}\n"
        "- auto_next: false\n\n"
        "## Open Issues\n\n"
        "- result 已生成，等待用户审查。\n"
        "- commit 前必须等待用户明确确认。\n\n"
        "## Notes\n\n"
        "- 不得自动生成下一轮 prompt。\n"
        "- 用户明确要求生成下一轮 prompt 后，才允许继续。\n"
    )
    state_path(root).write_text(state, encoding="utf-8")


def recent_results(root: Path, limit: int = 3) -> list[str]:
    results = numbered_files(root, RESULT_RE)
    lines: list[str] = []
    for round_id in sorted(results, reverse=True)[:limit]:
        lines.append(f"- `ans_qes/result{round_id}.md`")
    return list(reversed(lines))


def project_plan_headings(root: Path) -> list[str]:
    path = root / "project_plan.md"
    if not path.exists():
        return []
    headings: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            headings.append(line.strip())
    return headings[:12]


def render_prompt(root: Path, round_id: int, title: str, focus: str | None) -> str:
    result_path = f"ans_qes/result{round_id}.md"
    headings = project_plan_headings(root)
    recent = recent_results(root)
    focus_text = focus or "请根据项目计划书、当前进度和用户最新意图，设计本轮范围适中的科研开发任务。"

    headings_block = "\n".join(f"- {heading}" for heading in headings) or "- 待从 `project_plan.md` 读取。"
    recent_block = "\n".join(recent) or "- 当前没有已完成的 result。"

    return f"""# Prompt {round_id}

## 任务标题

{title}

## 任务背景

本项目使用交互式科研项目推进模板。请先读取并遵守：

- `AGENTS.md`
- `.research_agent/AGENTS.md`
- `PROJECT_RULES.md`
- `project_plan.md`
- `.research_agent/project_state.md`

项目计划书当前可见章节包括：

{headings_block}

最近完成记录：

{recent_block}

## 任务目标

{focus_text}

## 具体要求

1. 本轮任务范围必须可执行、可检查、可记录，不要把多个大阶段揉在一起。
2. 所有代码、实验和文档修改都必须服务于 `project_plan.md` 的科研目标。
3. 必须遵守 `PROJECT_RULES.md` 中与本轮任务相关的科研工程、数据、benchmark、模型、统计、文档、日志和低 token 上下文规则。
4. 如涉及数据、模型、benchmark 或统计分析，必须注意可复现性、数据泄漏风险和结果可解释性。
5. 长任务需要清晰日志或进度输出。
6. 新增说明类 Markdown 文档默认使用中文；代码标识、命令、配置键、字段名、路径、模型名和指标名保留英文。
7. 不调用远程 LLM API。
8. 不自动生成下一轮 prompt，除非用户明确要求受限连续推进 N 轮。
9. 不自动 commit 或 push。

## 预期输出

- 明确列出本轮需要创建或修改的文件。
- 明确列出本轮需要运行的检查、测试或命令。
- 执行结果需要说明是否满足 `PROJECT_RULES.md` 的相关规则。
- 执行完成后必须生成 `{result_path}`。

## 暂不执行

本文件只是任务提示词。生成后必须停止，等待用户审查和确认后才能执行。
"""


def result_sections(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return {match.group(1).strip() for match in SECTION_RE.finditer(text)}


def git_changed_files(root: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "status", "--short", "--", "."],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return []
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def should_skip_context_path(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in SKIP_CONTEXT_DIRS for part in rel_parts)


def iter_context_files(root: Path):
    for path in root.rglob("*"):
        if should_skip_context_path(path, root):
            continue
        if path.is_file():
            yield path


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f}{unit}" if unit != "B" else f"{int(value)}B"
        value /= 1024
    return f"{size}B"


def cmd_context_summary(args: argparse.Namespace) -> int:
    root = target_root(args)
    files = list(iter_context_files(root))
    by_ext: Counter[str] = Counter()
    top_dirs: Counter[str] = Counter()
    generated_counts: Counter[str] = Counter()
    large_files: list[tuple[int, Path]] = []
    text_candidates: list[tuple[int, Path]] = []

    for path in files:
        rel_parts = path.relative_to(root).parts
        top = rel_parts[0] if rel_parts else "."
        top_dirs[top] += 1
        if any(part in GENERATED_OR_LARGE_DIRS for part in rel_parts):
            generated_counts[top] += 1
        suffix = path.suffix.lower() or "<none>"
        by_ext[suffix] += 1
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size >= args.large_threshold:
            large_files.append((size, path))
        if suffix in TEXT_EXTENSIONS:
            text_candidates.append((size, path))

    print(f"target: {root}")
    print(f"files_seen: {len(files)}")
    print("workflow:")
    progress = load_progress(root)
    print(f"- current_round: {progress.get('current_round', 0)}")
    print(f"- phase: {progress.get('phase', 'idle')}")
    print(f"- last_prompt: {progress.get('last_prompt')}")
    print(f"- last_result: {progress.get('last_result')}")
    print(f"- next_prompt_id: {next_round_id(root)}")

    plan = root / "project_plan.md"
    if plan.exists():
        print("project_plan:")
        print(f"- size: {format_bytes(plan.stat().st_size)}")
        headings = project_plan_headings(root)
        for heading in headings[: args.max_items]:
            print(f"- {heading}")

    print("top_dirs:")
    for name, count in top_dirs.most_common(args.max_items):
        print(f"- {name}: {count}")

    print("extensions:")
    for name, count in by_ext.most_common(args.max_items):
        print(f"- {name}: {count}")

    if generated_counts:
        print("generated_or_large_dirs:")
        for name, count in generated_counts.most_common(args.max_items):
            print(f"- {name}: {count} files; inspect summaries before raw reads")

    if large_files:
        print("large_files:")
        for size, path in sorted(large_files, reverse=True)[: args.max_items]:
            print(f"- {rel(path, root)}: {format_bytes(size)}")

    prompts = numbered_files(root, PROMPT_RE)
    results = numbered_files(root, RESULT_RE)
    print("recent_round_files:")
    for round_id in sorted(set(prompts) | set(results), reverse=True)[: args.max_items]:
        prompt = f"ans_qes/prompt{round_id}.md" if round_id in prompts else "missing"
        result = f"ans_qes/result{round_id}.md" if round_id in results else "missing"
        print(f"- round {round_id}: prompt={prompt}; result={result}")

    changed = git_changed_files(root)
    if changed:
        print("git_status_short:")
        for line in changed[: args.max_items]:
            print(f"- {line}")
        if len(changed) > args.max_items:
            print(f"- ... {len(changed) - args.max_items} more")

    print("context_rule: use this summary, rg, and bounded excerpts before opening large files")
    return 0


def summarize_prompt(root: Path, round_id: int) -> str:
    prompt_path = ans_dir(root) / f"prompt{round_id}.md"
    if not prompt_path.exists():
        return f"round {round_id}"
    text = prompt_path.read_text(encoding="utf-8")
    match = re.search(r"##\s+任务标题\s*\n+(.+)", text)
    if match:
        return re.sub(r"\s+", " ", match.group(1)).strip()[:60]
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:60]
    return f"round {round_id}"


def cmd_init(args: argparse.Namespace) -> int:
    root = target_root(args)
    written: list[Path] = []
    skipped: list[Path] = []
    copy_tree(TEMPLATE_ROOT, root, args.force, written, skipped)

    print(f"target: {root}")
    print(f"written: {len(written)}")
    for path in written:
        print(f"+ {rel(path, root)}")
    if skipped:
        print(f"skipped_existing: {len(skipped)}")
        for path in skipped:
            print(f"= {rel(path, root)}")
        print("rerun with --force only if the user explicitly wants overwrite")
    print("stop: fill project_plan.md before generating prompt1.md")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = target_root(args)
    progress = load_progress(root)
    print(f"target: {root}")
    print(f"current_round: {progress.get('current_round', 0)}")
    print(f"phase: {progress.get('phase', 'idle')}")
    print(f"last_prompt: {progress.get('last_prompt')}")
    print(f"last_result: {progress.get('last_result')}")
    print(f"last_commit: {progress.get('last_commit')}")
    print(f"auto_next: {progress.get('auto_next', False)}")
    for issue in progress.get("open_issues", []):
        print(f"open_issue: {issue}")
    return 0


def cmd_next_id(args: argparse.Namespace) -> int:
    print(next_round_id(target_root(args)))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    root = target_root(args)
    problems: list[str] = []
    for path in required_paths(root):
        if not path.exists():
            problems.append(f"missing required path: {rel(path, root)}")

    progress = load_progress(root)
    for key in ("auto_next", "auto_execute_prompt", "auto_commit", "auto_push"):
        if progress.get(key) is not False:
            problems.append(f"progress.json must set {key}: false")

    problems.extend(check_pairs(root))
    plan_ok, plan_warnings = plan_report(root)

    if problems:
        print("check: failed")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("check: ok")
    print(f"next_prompt_id: {next_round_id(root)}")
    if plan_ok:
        print("project_plan: looks filled enough for a first pass")
    else:
        print("project_plan_warnings:")
        for warning in plan_warnings:
            print(f"- {warning}")
    return 0


def cmd_plan_check(args: argparse.Namespace) -> int:
    root = target_root(args)
    ok, warnings = plan_report(root)
    if ok:
        print("plan-check: ok")
        return 0
    print("plan-check: warnings")
    for warning in warnings:
        print(f"- {warning}")
    return 0


def cmd_draft_prompt(args: argparse.Namespace) -> int:
    root = target_root(args)
    round_id = args.round or next_round_id(root)
    prompt_path = ans_dir(root) / f"prompt{round_id}.md"
    if prompt_path.exists() and not args.force:
        print(f"refusing to overwrite existing {rel(prompt_path, root)}")
        print("use --force only if the user explicitly asked to overwrite")
        return 1

    ans_dir(root).mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(
        render_prompt(root, round_id, args.title, args.focus),
        encoding="utf-8",
    )
    update_state_for_prompt(root, round_id, prompt_path)
    print(f"created: {rel(prompt_path, root)}")
    print("stop: prompt_drafted; wait for user review before execution")
    return 0


def cmd_result_check(args: argparse.Namespace) -> int:
    root = target_root(args)
    round_id = args.round
    prompt_path = ans_dir(root) / f"prompt{round_id}.md"
    result_path = ans_dir(root) / f"result{round_id}.md"

    problems: list[str] = []
    if not prompt_path.exists():
        problems.append(f"missing {rel(prompt_path, root)}")
    if not result_path.exists():
        problems.append(f"missing {rel(result_path, root)}")

    if result_path.exists():
        sections = result_sections(result_path)
        for section in REQUIRED_RESULT_SECTIONS:
            if section not in sections:
                problems.append(f"{rel(result_path, root)} missing section: {section}")

    if problems:
        print("result-check: failed")
        for problem in problems:
            print(f"- {problem}")
        return 1

    if args.mark_executed:
        update_state_for_result(root, round_id, result_path)
        print("state: executed")
    print("result-check: ok")
    print("stop: wait for user review; do not generate next prompt")
    return 0


def cmd_suggest_commit(args: argparse.Namespace) -> int:
    root = target_root(args)
    round_id = args.round
    summary = args.summary or summarize_prompt(root, round_id)
    summary = re.sub(r"\s+", " ", summary).strip()
    if len(summary) > 72:
        summary = summary[:72].rstrip()
    print(f"p{round_id}: {summary}")

    changed = git_changed_files(root)
    if changed:
        print("changed_files:")
        for line in changed[:30]:
            print(f"- {line}")
        if len(changed) > 30:
            print(f"- ... {len(changed) - 30} more")
    print("suggestion only; commit requires explicit user confirmation")
    return 0


def cmd_continue_plan(args: argparse.Namespace) -> int:
    root = target_root(args)
    if args.rounds < 1:
        print("continue-plan: failed")
        print("- --rounds must be >= 1")
        return 1
    if args.rounds > MAX_CONTINUE_ROUNDS and not args.allow_large_n:
        print("continue-plan: failed")
        print(f"- refusing more than {MAX_CONTINUE_ROUNDS} rounds without --allow-large-n")
        return 1

    problems = check_pairs(root)
    if problems:
        print("continue-plan: failed")
        for problem in problems:
            print(f"- {problem}")
        return 1

    progress = load_progress(root)
    start = next_round_id(root)
    end = start + args.rounds - 1
    prompts = numbered_files(root, PROMPT_RE)
    results = numbered_files(root, RESULT_RE)
    latest_result = max(results) if results else None

    if prompts and latest_result is None:
        print("continue-plan: warning")
        print("- prompts exist but no result files exist yet")
    if latest_result is not None and latest_result < max(prompts):
        print("continue-plan: warning")
        print("- latest prompt has not produced a matching result")

    progress.update(
        {
            "phase": "continue_requested",
            "continue_rounds_requested": args.rounds,
            "continue_start_round": start,
            "continue_end_round": end,
            "auto_next": False,
            "auto_execute_prompt": False,
            "auto_commit": False,
            "auto_push": False,
            "open_issues": [
                f"用户请求受限连续推进 {args.rounds} 轮：round {start} 到 {end}。",
                "每轮仍必须生成 prompt/result；不得无限循环；不得自动 push。",
            ],
        }
    )
    save_progress(root, progress)

    print("continue-plan: ok")
    print(f"current_round: {progress.get('current_round', 0)}")
    print(f"latest_result_round: {latest_result}")
    print(f"next_round_start: {start}")
    print(f"next_round_end: {end}")
    print(f"rounds_requested: {args.rounds}")
    print("mode: bounded_continue")
    print("rule: stop after requested rounds, on test failure, on uncertainty, on large-file/secret risk, or before push")
    return 0


def add_target(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target", default=".", help="target research repository root")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Operate the interactive research coding workflow on a target repository."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="install the workflow template into a target repo")
    add_target(init)
    init.add_argument("--force", action="store_true", help="overwrite existing template files")
    init.set_defaults(func=cmd_init)

    status = subparsers.add_parser("status", help="show workflow state")
    add_target(status)
    status.set_defaults(func=cmd_status)

    context = subparsers.add_parser("context-summary", help="summarize repo context without reading large files")
    add_target(context)
    context.add_argument("--max-items", type=int, default=12, help="maximum rows per summary section")
    context.add_argument("--large-threshold", type=int, default=1024 * 1024, help="large file threshold in bytes")
    context.set_defaults(func=cmd_context_summary)

    check = subparsers.add_parser("check", help="check template structure and numbering")
    add_target(check)
    check.set_defaults(func=cmd_check)

    plan = subparsers.add_parser("plan-check", help="check whether project_plan.md looks filled")
    add_target(plan)
    plan.set_defaults(func=cmd_plan_check)

    next_id = subparsers.add_parser("next-id", help="print next prompt/result round id")
    add_target(next_id)
    next_id.set_defaults(func=cmd_next_id)

    draft = subparsers.add_parser("draft-prompt", help="create a prompt draft and stop")
    add_target(draft)
    draft.add_argument("--round", type=int, default=None, help="round number; defaults to next id")
    draft.add_argument("--title", required=True, help="prompt title")
    draft.add_argument("--focus", default=None, help="specific goal/focus text")
    draft.add_argument("--force", action="store_true", help="overwrite existing prompt")
    draft.set_defaults(func=cmd_draft_prompt)

    result = subparsers.add_parser("result-check", help="validate resultn.md structure")
    add_target(result)
    result.add_argument("--round", type=int, required=True, help="round number")
    result.add_argument("--mark-executed", action="store_true", help="update state to executed when valid")
    result.set_defaults(func=cmd_result_check)

    commit = subparsers.add_parser("suggest-commit", help="suggest a commit message")
    add_target(commit)
    commit.add_argument("--round", type=int, required=True, help="round number")
    commit.add_argument("--summary", default=None, help="explicit summary")
    commit.set_defaults(func=cmd_suggest_commit)

    cont = subparsers.add_parser("continue-plan", help="plan a bounded N-round continuation")
    add_target(cont)
    cont.add_argument("--rounds", type=int, required=True, help="number of rounds to continue")
    cont.add_argument("--allow-large-n", action="store_true", help="allow more than the default maximum")
    cont.set_defaults(func=cmd_continue_plan)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
