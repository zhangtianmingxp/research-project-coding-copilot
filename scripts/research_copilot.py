#!/usr/bin/env python3
"""Action CLI for the research-project-coding-copilot skill.

This script operates on a target research repository. It never calls model
APIs, never executes prompt tasks, never commits, and never pushes.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import re
import shutil
import subprocess
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "template"

PROMPT_RE = re.compile(r"^prompt(\d+)(?:_(.+))?\.md$", re.IGNORECASE)
RESULT_RE = re.compile(r"^result(\d+)(?:_(.+))?\.md$", re.IGNORECASE)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

RESULT_SECTION_CONCEPTS = {
    "summary": {"执行摘要", "本轮目的", "本轮目标", "任务摘要"},
    "work": {"完成内容", "新增脚本", "新增图表", "核心数值", "主要结果"},
    "files": {"涉及文件", "新增/更新文档", "新增文档", "输出文件", "产物"},
    "verification": {"验证情况", "验证命令", "QC 结果", "QC结果", "测试结果"},
    "risks": {"风险与注意事项", "解释边界", "局限性", "剩余风险"},
    "next": {"后续建议", "下一步建议", "推荐下一步"},
}

SENSITIVE_NAME_RE = re.compile(
    r"(^|[._-])(api[_-]?key|apikey|credential|credentials|secret|token|private[_-]?key)([._-]|$)",
    re.IGNORECASE,
)
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}

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


def profile_path(root: Path) -> Path:
    return agent_dir(root) / "project_profile.json"


def load_profile(root: Path) -> dict:
    path = profile_path(root)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_profile(root: Path, profile: dict) -> None:
    path = profile_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_progress(root: Path) -> dict:
    path = progress_path(root)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_progress(root: Path, progress: dict) -> None:
    progress_path(root).parent.mkdir(parents=True, exist_ok=True)
    progress_path(root).write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def numbered_file_groups(root: Path, pattern: re.Pattern[str]) -> dict[int, list[Path]]:
    directory = ans_dir(root)
    if not directory.exists():
        return {}
    items: dict[int, list[Path]] = {}
    for path in directory.iterdir():
        match = pattern.match(path.name)
        if match:
            items.setdefault(int(match.group(1)), []).append(path)
    for paths in items.values():
        paths.sort(key=lambda item: item.name.lower())
    return items


def numbered_files(root: Path, pattern: re.Pattern[str]) -> dict[int, Path]:
    return {round_id: paths[0] for round_id, paths in numbered_file_groups(root, pattern).items()}


def find_round_file(root: Path, pattern: re.Pattern[str], round_id: int) -> Path | None:
    return numbered_files(root, pattern).get(round_id)


def next_round_id(root: Path) -> int:
    used = set(numbered_files(root, PROMPT_RE)) | set(numbered_files(root, RESULT_RE))
    return max(used, default=0) + 1


def round_title(path: Path, pattern: re.Pattern[str]) -> str | None:
    match = pattern.match(path.name)
    return match.group(2) if match else None


def safe_title_slug(title: str) -> str:
    slug = re.sub(r'[<>:"/\\|?*]+', "_", title.strip())
    slug = re.sub(r"\s+", "_", slug)
    slug = re.sub(r"_+", "_", slug).strip("._")
    return slug[:80] or "任务"


def resolve_title_arg(args: argparse.Namespace, root: Path) -> str:
    if getattr(args, "title_file", None):
        path = Path(args.title_file)
        if not path.is_absolute():
            path = root / path
        return path.read_text(encoding="utf-8").strip()
    return args.title


def detect_path(root: Path, profile_key: str, candidates: list[str]) -> Path | None:
    configured = load_profile(root).get(profile_key)
    if configured:
        path = root / configured
        if path.exists():
            return path
    seen: set[Path] = set()
    for candidate in candidates:
        for path in sorted(root.glob(candidate), key=lambda item: item.name.lower()):
            if path.is_file() and path not in seen:
                seen.add(path)
                return path
    return None


def project_plan_path(root: Path) -> Path | None:
    return detect_path(root, "project_plan", ["project_plan.md", "PROJECT_PLAN.md", "PROJECT_PLAN*.md", "project_plan*.md"])


def project_rules_path(root: Path) -> Path | None:
    return detect_path(root, "project_rules", ["PROJECT_RULES.md", "project_rules.md"])


def context_rules_path(root: Path) -> Path | None:
    return detect_path(root, "context_rules", ["AI_AGENT_CONTEXT_RULES.md", "*CONTEXT_RULES*.md"])


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


def detected_project_profile(root: Path, args: argparse.Namespace | None = None) -> dict:
    explicit_plan = getattr(args, "plan", None) if args else None
    explicit_rules = getattr(args, "rules", None) if args else None
    explicit_docs = getattr(args, "docs_dir", None) if args else None
    plan = root / explicit_plan if explicit_plan else project_plan_path(root)
    rules = root / explicit_rules if explicit_rules else project_rules_path(root)
    context_rules = context_rules_path(root)

    docs_dir: Path | None = None
    if explicit_docs:
        docs_dir = root / explicit_docs
    elif (root / "docs").is_dir():
        docs_dir = root / "docs"
    elif (root / "doc").is_dir():
        docs_dir = root / "doc"

    output_dirs = [
        rel(root / name, root)
        for name in sorted(GENERATED_OR_LARGE_DIRS)
        if (root / name).is_dir()
    ]
    environment_docs = []
    for pattern in ("*runtime*environment*.md", "*environment*.md", "*环境*.md"):
        search_root = docs_dir or root
        for path in sorted(search_root.glob(pattern), key=lambda item: item.name.lower()):
            if path.is_file() and rel(path, root) not in environment_docs:
                environment_docs.append(rel(path, root))

    prompts = numbered_files(root, PROMPT_RE)
    titled = any(round_title(path, PROMPT_RE) for path in prompts.values())
    return {
        "project_plan": rel(plan, root) if plan and plan.exists() else None,
        "project_rules": rel(rules, root) if rules and rules.exists() else None,
        "context_rules": rel(context_rules, root) if context_rules else None,
        "docs_dir": rel(docs_dir, root) if docs_dir and docs_dir.exists() else None,
        "output_dirs": output_dirs,
        "environment_docs": environment_docs,
        "prompt_naming": "prompt{n}_{title}.md" if titled else "prompt{n}.md",
        "result_naming": "result{n}_{title}.md" if titled else "result{n}.md",
        "max_recent_results_to_read": 3,
        "context_mode": "low",
    }


def inferred_progress(root: Path) -> dict:
    prompts = numbered_files(root, PROMPT_RE)
    results = numbered_files(root, RESULT_RE)
    used = set(prompts) | set(results)
    current = max(used, default=0)
    latest_prompt = prompts.get(max(prompts)) if prompts else None
    latest_result = results.get(max(results)) if results else None
    if current == 0:
        phase = "idle"
    elif current in prompts and current in results:
        phase = "executed"
    elif current in prompts:
        phase = "prompt_drafted"
    else:
        phase = "result_orphaned"
    return {
        "current_round": current,
        "phase": phase,
        "last_prompt": rel(latest_prompt, root) if latest_prompt else None,
        "last_result": rel(latest_result, root) if latest_result else None,
        "last_commit": None,
        "auto_next": False,
        "auto_execute_prompt": False,
        "auto_commit": False,
        "auto_push": False,
        "open_issues": round_warnings(root),
    }


def effective_progress(root: Path) -> dict:
    """Prefer saved metadata, but never let it lag behind round files on disk."""
    saved = load_progress(root)
    inferred = inferred_progress(root)
    if not saved:
        return inferred
    if inferred["current_round"] <= int(saved.get("current_round", 0)):
        return saved

    reconciled = {**saved, **inferred}
    reconciled["last_commit"] = saved.get("last_commit")
    reconciled["open_issues"] = list(
        dict.fromkeys(
            [
                *saved.get("open_issues", []),
                f"progress.json lagged behind round files and was read as round {inferred['current_round']}",
                *inferred.get("open_issues", []),
            ]
        )
    )
    return reconciled


def write_state_snapshot(root: Path, progress: dict) -> None:
    issues = progress.get("open_issues") or ["当前没有已记录的 open issue。"]
    issue_lines = "".join(f"- {issue}\n" for issue in issues)
    state = (
        "# Project State\n\n"
        "## Current Status\n\n"
        f"- current_round: {progress.get('current_round', 0)}\n"
        f"- phase: {progress.get('phase', 'idle')}\n"
        f"- last_prompt: {progress.get('last_prompt')}\n"
        f"- last_result: {progress.get('last_result')}\n"
        f"- last_commit: {progress.get('last_commit')}\n"
        "- auto_next: false\n\n"
        "## Open Issues\n\n"
        f"{issue_lines}\n"
        "## Notes\n\n"
        "- 状态由 research-project-coding-copilot 根据现有 prompt/result 推断。\n"
        "- 历史编号缺口不会自动回填；下一轮默认使用最大编号加一。\n"
    )
    state_path(root).parent.mkdir(parents=True, exist_ok=True)
    state_path(root).write_text(state, encoding="utf-8")


def required_paths(root: Path) -> list[Path]:
    paths = [
        root / "AGENTS.md",
        root / "README.md",
        ans_dir(root) / "README.md",
        agent_dir(root) / "AGENTS.md",
        agent_dir(root) / "config.yaml",
        profile_path(root),
        progress_path(root),
        state_path(root),
        agent_dir(root) / "templates" / "prompt_template.md",
        agent_dir(root) / "templates" / "result_template.md",
        agent_dir(root) / "templates" / "commit_template.md",
        root / "scripts" / "research_flow.py",
    ]
    paths.append(project_rules_path(root) or root / "PROJECT_RULES.md")
    paths.append(project_plan_path(root) or root / "project_plan.md")
    return paths


def check_pairs(root: Path) -> list[str]:
    problems: list[str] = []
    prompt_groups = numbered_file_groups(root, PROMPT_RE)
    result_groups = numbered_file_groups(root, RESULT_RE)
    prompts = {round_id: paths[0] for round_id, paths in prompt_groups.items()}
    results = {round_id: paths[0] for round_id, paths in result_groups.items()}

    for round_id, paths in sorted(prompt_groups.items()):
        if len(paths) > 1:
            problems.append(f"duplicate prompt round {round_id}: {', '.join(path.name for path in paths)}")
    for round_id, paths in sorted(result_groups.items()):
        if len(paths) > 1:
            problems.append(f"duplicate result round {round_id}: {', '.join(path.name for path in paths)}")

    for round_id in sorted(results):
        if round_id not in prompts:
            problems.append(f"result round {round_id} exists without a matching prompt")

    return problems


def round_warnings(root: Path) -> list[str]:
    warnings: list[str] = []
    prompts = numbered_files(root, PROMPT_RE)
    results = numbered_files(root, RESULT_RE)
    used = set(prompts) | set(results)
    if used:
        missing = sorted(set(range(1, max(used) + 1)) - used)
        if missing:
            preview = ", ".join(str(item) for item in missing[:20])
            suffix = " ..." if len(missing) > 20 else ""
            warnings.append(f"historical round gaps detected: {preview}{suffix}; next-id still uses max+1")
    for round_id in sorted(set(prompts) & set(results)):
        prompt_title = round_title(prompts[round_id], PROMPT_RE)
        result_title = round_title(results[round_id], RESULT_RE)
        if prompt_title and result_title and prompt_title != result_title:
            warnings.append(
                f"round {round_id} title mismatch: prompt={prompt_title!r}, result={result_title!r}"
            )
    return warnings


def plan_report(root: Path) -> tuple[bool, list[str]]:
    path = project_plan_path(root)
    if path is None:
        return False, ["no project plan found (expected project_plan.md or PROJECT_PLAN*.md)"]

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
        warnings.append(f"{path.name} looks short; consider filling the research plan before prompt generation")
    if any(token in text for token in placeholders):
        warnings.append(f"{path.name} still contains template placeholder text")

    headings = [line.strip() for line in text.splitlines() if line.startswith("## ")]
    if len(headings) < 6:
        warnings.append(f"{path.name} has fewer than 6 second-level sections")

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
    state_path(root).parent.mkdir(parents=True, exist_ok=True)
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
    matching_prompt = find_round_file(root, PROMPT_RE, round_id)
    if matching_prompt is not None:
        progress["last_prompt"] = rel(matching_prompt, root)
    elif not progress.get("last_prompt"):
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
    state_path(root).parent.mkdir(parents=True, exist_ok=True)
    state_path(root).write_text(state, encoding="utf-8")


def recent_results(root: Path, limit: int = 3) -> list[str]:
    results = numbered_files(root, RESULT_RE)
    lines: list[str] = []
    for round_id in sorted(results, reverse=True)[:limit]:
        lines.append(f"- `{rel(results[round_id], root)}`")
    return list(reversed(lines))


def project_plan_headings(root: Path) -> list[str]:
    path = project_plan_path(root)
    if path is None:
        return []
    headings: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            headings.append(line.strip())
    return headings[:12]


def render_prompt(root: Path, round_id: int, title: str, focus: str | None) -> str:
    title_slug = safe_title_slug(title)
    result_path = f"ans_qes/result{round_id}_{title_slug}.md"
    plan = project_plan_path(root)
    rules = project_rules_path(root)
    plan_name = rel(plan, root) if plan else "project_plan.md"
    rules_name = rel(rules, root) if rules else "PROJECT_RULES.md"
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
- `{rules_name}`
- `{plan_name}`
- `.research_agent/project_state.md`

项目计划书当前可见章节包括：

{headings_block}

最近完成记录：

{recent_block}

## 任务目标

{focus_text}

## 具体要求

1. 本轮任务范围必须可执行、可检查、可记录，不要把多个大阶段揉在一起。
2. 所有代码、实验和文档修改都必须服务于 `{plan_name}` 的科研目标。
3. 必须遵守 `{rules_name}` 中与本轮任务相关的科研工程、数据、benchmark、模型、统计、文档、日志和低 token 上下文规则。
4. 如涉及数据、模型、benchmark 或统计分析，必须注意可复现性、数据泄漏风险和结果可解释性。
5. 长任务需要清晰日志或进度输出。
6. 新增说明类 Markdown 文档默认使用中文；代码标识、命令、配置键、字段名、路径、模型名和指标名保留英文。
7. 不调用远程 LLM API。
8. 不自动生成下一轮 prompt，除非用户明确要求受限连续推进 N 轮。
9. 不自动 commit 或 push。

## 预期输出

- 明确列出本轮需要创建或修改的文件。
- 明确列出本轮需要运行的检查、测试或命令。
- 执行结果需要说明是否满足 `{rules_name}` 的相关规则。
- 执行完成后必须生成 `{result_path}`。

## 暂不执行

本文件只是任务提示词。生成后必须停止，等待用户审查和确认后才能执行。
"""


def result_sections(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return {match.group(1).strip() for match in SECTION_RE.finditer(text)}


def has_section_alias(sections: set[str], aliases: set[str]) -> bool:
    return any(section == alias or section.startswith(alias) for section in sections for alias in aliases)


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


def is_sensitive_path(path: Path) -> bool:
    return path.suffix.lower() in SENSITIVE_SUFFIXES or bool(SENSITIVE_NAME_RE.search(path.name))


def iter_context_files(root: Path, include_generated: bool = False):
    for current, dirnames, filenames in os.walk(root):
        current_path = Path(current)
        dirnames[:] = [
            name
            for name in dirnames
            if name not in SKIP_CONTEXT_DIRS
            and (include_generated or name not in GENERATED_OR_LARGE_DIRS)
        ]
        for filename in filenames:
            path = current_path / filename
            if should_skip_context_path(path, root) or is_sensitive_path(path):
                continue
            yield path


def sensitive_paths(root: Path) -> list[Path]:
    found: list[Path] = []
    for current, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name
            for name in dirnames
            if name not in SKIP_CONTEXT_DIRS and name not in GENERATED_OR_LARGE_DIRS
        ]
        current_path = Path(current)
        for filename in filenames:
            path = current_path / filename
            if is_sensitive_path(path):
                found.append(path)
    return sorted(found, key=lambda item: rel(item, root).lower())


def git_tracked_files(root: Path) -> set[str]:
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return set()
    if completed.returncode != 0:
        return set()
    return {line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()}


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
    files = list(iter_context_files(root, include_generated=args.include_generated))
    by_ext: Counter[str] = Counter()
    top_dirs: Counter[str] = Counter()
    large_files: list[tuple[int, Path]] = []

    for path in files:
        rel_parts = path.relative_to(root).parts
        top = rel_parts[0] if rel_parts else "."
        top_dirs[top] += 1
        suffix = path.suffix.lower() or "<none>"
        by_ext[suffix] += 1
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size >= args.large_threshold:
            large_files.append((size, path))

    print(f"target: {root}")
    print(f"files_seen: {len(files)}")
    print("workflow:")
    progress = effective_progress(root)
    print(f"- current_round: {progress.get('current_round', 0)}")
    print(f"- phase: {progress.get('phase', 'idle')}")
    print(f"- last_prompt: {progress.get('last_prompt')}")
    print(f"- last_result: {progress.get('last_result')}")
    print(f"- next_prompt_id: {next_round_id(root)}")

    plan = project_plan_path(root)
    if plan is not None:
        print("project_plan:")
        print(f"- path: {rel(plan, root)}")
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

    generated_dirs = [root / name for name in sorted(GENERATED_OR_LARGE_DIRS) if (root / name).is_dir()]
    if generated_dirs:
        print("generated_or_large_dirs:")
        for path in generated_dirs[: args.max_items]:
            mode = "included" if args.include_generated else "contents not enumerated"
            print(f"- {rel(path, root)}: {mode}")

    if large_files:
        print("large_files:")
        for size, path in sorted(large_files, reverse=True)[: args.max_items]:
            print(f"- {rel(path, root)}: {format_bytes(size)}")

    prompts = numbered_files(root, PROMPT_RE)
    results = numbered_files(root, RESULT_RE)
    print("recent_round_files:")
    for round_id in sorted(set(prompts) | set(results), reverse=True)[: args.max_items]:
        prompt = rel(prompts[round_id], root) if round_id in prompts else "missing"
        result = rel(results[round_id], root) if round_id in results else "missing"
        print(f"- round {round_id}: prompt={prompt}; result={result}")

    sensitive = sensitive_paths(root)
    if sensitive:
        tracked = git_tracked_files(root)
        print("sensitive_paths_not_read:")
        for path in sensitive[: args.max_items]:
            status = "TRACKED" if rel(path, root) in tracked else "untracked_or_ignored"
            print(f"- {rel(path, root)}: {status}")
        if len(sensitive) > args.max_items:
            print(f"- ... {len(sensitive) - args.max_items} more")

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
    prompt_path = find_round_file(root, PROMPT_RE, round_id)
    if prompt_path is None:
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


def cmd_adopt(args: argparse.Namespace) -> int:
    root = target_root(args)
    profile = detected_project_profile(root, args)
    progress = inferred_progress(root)
    had_profile = profile_path(root).exists()
    had_progress = progress_path(root).exists()

    print(f"target: {root}")
    print("detected_profile:")
    for key, value in profile.items():
        print(f"- {key}: {value}")
    print("inferred_workflow:")
    print(f"- current_round: {progress['current_round']}")
    print(f"- phase: {progress['phase']}")
    print(f"- last_prompt: {progress['last_prompt']}")
    print(f"- last_result: {progress['last_result']}")
    print(f"- next_prompt_id: {next_round_id(root)}")

    problems: list[str] = []
    if not profile["project_plan"]:
        problems.append("no project plan detected; pass --plan PATH")
    if not profile["project_rules"]:
        problems.append("no project rules detected; pass --rules PATH or install PROJECT_RULES.md")
    if problems:
        print("adopt: failed")
        for problem in problems:
            print(f"- {problem}")
        return 1

    for warning in round_warnings(root):
        print(f"warning: {warning}")

    if args.dry_run:
        print("adopt: dry-run complete; no files written")
        return 0

    written: list[Path] = []
    skipped: list[Path] = []
    copy_tree(TEMPLATE_ROOT / ".research_agent", agent_dir(root), False, written, skipped)

    helper_source = TEMPLATE_ROOT / "scripts" / "research_flow.py"
    helper_target = root / "scripts" / "research_flow.py"
    if not helper_target.exists() or args.update_helper:
        helper_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(helper_source, helper_target)
        written.append(helper_target)
    else:
        skipped.append(helper_target)

    if not had_profile or args.refresh_state:
        save_profile(root, profile)
        written.append(profile_path(root))
    else:
        skipped.append(profile_path(root))

    if not had_progress or args.refresh_state:
        save_progress(root, progress)
        write_state_snapshot(root, progress)
        written.extend([progress_path(root), state_path(root)])
    else:
        skipped.extend([progress_path(root), state_path(root)])

    print("adopt: ok")
    print(f"written: {len(set(written))}")
    for path in sorted(set(written), key=lambda item: rel(item, root).lower()):
        print(f"+ {rel(path, root)}")
    if skipped:
        print(f"preserved_existing: {len(set(skipped))}")
    print("stop: review .research_agent/project_profile.json and project_state.md")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = target_root(args)
    progress = effective_progress(root)
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
    warnings = round_warnings(root)
    plan_ok, plan_warnings = plan_report(root)

    if problems:
        print("check: failed")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("check: ok")
    print(f"next_prompt_id: {next_round_id(root)}")
    for warning in warnings:
        print(f"warning: {warning}")
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
    existing = find_round_file(root, PROMPT_RE, round_id)
    title = resolve_title_arg(args, root)
    title_slug = safe_title_slug(title)
    prompt_name = f"prompt{round_id}.md" if args.plain_name else f"prompt{round_id}_{title_slug}.md"
    prompt_path = ans_dir(root) / prompt_name
    if existing is not None and not args.force:
        print(f"refusing to overwrite existing {rel(existing, root)}")
        print("use --force only if the user explicitly asked to overwrite")
        return 1

    ans_dir(root).mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(
        render_prompt(root, round_id, title, args.focus),
        encoding="utf-8",
    )
    update_state_for_prompt(root, round_id, prompt_path)
    print(f"created: {rel(prompt_path, root)}")
    print("stop: prompt_drafted; wait for user review before execution")
    return 0


def cmd_result_check(args: argparse.Namespace) -> int:
    root = target_root(args)
    round_id = args.round
    prompt_path = find_round_file(root, PROMPT_RE, round_id)
    result_path = find_round_file(root, RESULT_RE, round_id)

    problems: list[str] = []
    warnings: list[str] = []
    if prompt_path is None:
        problems.append(f"missing prompt for round {round_id}")
    if result_path is None:
        problems.append(f"missing result for round {round_id}")

    if result_path is not None:
        sections = result_sections(result_path)
        matched: set[str] = set()
        for concept, aliases in RESULT_SECTION_CONCEPTS.items():
            if has_section_alias(sections, aliases):
                matched.add(concept)
        for concept in ("summary", "work", "verification"):
            if concept not in matched:
                problems.append(f"{rel(result_path, root)} missing required concept: {concept}")
        for concept in sorted(set(RESULT_SECTION_CONCEPTS) - matched):
            warnings.append(f"{rel(result_path, root)} has no recognized section for: {concept}")
        if args.strict and warnings:
            problems.extend(warnings)

    if problems:
        print("result-check: failed")
        for problem in problems:
            print(f"- {problem}")
        return 1

    if args.mark_executed:
        assert result_path is not None
        update_state_for_result(root, round_id, result_path)
        print("state: executed")
    print("result-check: ok")
    for warning in warnings:
        print(f"warning: {warning}")
    print("stop: wait for user review; do not generate next prompt")
    return 0


def cmd_prompt_check(args: argparse.Namespace) -> int:
    root = target_root(args)
    prompt_path = find_round_file(root, PROMPT_RE, args.round)
    if prompt_path is None:
        print("prompt-check: failed")
        print(f"- missing prompt for round {args.round}")
        return 1

    text = prompt_path.read_text(encoding="utf-8")
    size = prompt_path.stat().st_size
    sections = result_sections(prompt_path)
    task_count = len(re.findall(r"^##\s+任务\s*\d+", text, re.MULTILINE))
    warnings: list[str] = []
    if size > args.max_bytes:
        warnings.append(
            f"prompt size {format_bytes(size)} exceeds {format_bytes(args.max_bytes)}; consider splitting the round"
        )
    if task_count > args.max_tasks:
        warnings.append(f"prompt contains {task_count} numbered tasks; recommended maximum is {args.max_tasks}")

    expected_groups = [
        {"任务背景", "项目背景"},
        {"任务目标", "本轮目标"},
        {"具体要求", "总体要求"},
        {"预期输出", "预期 result", "预期 result 内容"},
    ]
    for aliases in expected_groups:
        if not has_section_alias(sections, aliases):
            warnings.append(f"missing recommended section concept: {'/'.join(sorted(aliases))}")
    if not has_section_alias(sections, {"暂不执行", "执行边界"}):
        warnings.append("missing execution boundary section: 暂不执行/执行边界")

    print("prompt-check: ok" if not (args.strict and warnings) else "prompt-check: failed")
    print(f"path: {rel(prompt_path, root)}")
    print(f"size: {format_bytes(size)}")
    print(f"numbered_tasks: {task_count}")
    for warning in warnings:
        print(f"warning: {warning}")
    return 1 if args.strict and warnings else 0


def tracked_large_files(root: Path, threshold: int) -> list[tuple[int, Path]]:
    tracked = git_tracked_files(root)
    found: list[tuple[int, Path]] = []
    for relative in tracked:
        path = root / relative
        if not path.is_file():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size >= threshold:
            found.append((size, path))
    return sorted(found, reverse=True)


def cmd_preflight(args: argparse.Namespace) -> int:
    root = target_root(args)
    problems: list[str] = []
    warnings: list[str] = []
    plan = project_plan_path(root)
    rules = project_rules_path(root)
    if plan is None:
        problems.append("project plan not detected")
    if rules is None:
        problems.append("PROJECT_RULES.md not detected")
    if not (root / "AGENTS.md").exists():
        warnings.append("AGENTS.md not found")
    if not ans_dir(root).is_dir():
        warnings.append("ans_qes directory not found")
    problems.extend(check_pairs(root))
    warnings.extend(round_warnings(root))

    if args.round is not None and find_round_file(root, PROMPT_RE, args.round) is None:
        problems.append(f"prompt for round {args.round} not found")

    tracked = git_tracked_files(root)
    for path in sensitive_paths(root):
        if rel(path, root) in tracked:
            problems.append(f"sensitive-looking file is tracked by Git: {rel(path, root)}")
        else:
            warnings.append(f"sensitive-looking file found and not read: {rel(path, root)}")

    for size, path in tracked_large_files(root, args.large_threshold):
        warnings.append(f"large tracked file: {rel(path, root)} ({format_bytes(size)})")

    changed = git_changed_files(root)
    if changed:
        warnings.append(f"Git working tree has {len(changed)} changed path(s)")

    profile = load_profile(root) or detected_project_profile(root)
    if not profile.get("environment_docs"):
        warnings.append("no runtime/environment document detected")

    print("preflight: failed" if problems else "preflight: ok")
    print(f"target: {root}")
    print(f"project_plan: {rel(plan, root) if plan else None}")
    print(f"project_rules: {rel(rules, root) if rules else None}")
    print(f"next_prompt_id: {next_round_id(root)}")
    for problem in problems:
        print(f"error: {problem}")
    for warning in warnings[: args.max_items]:
        print(f"warning: {warning}")
    if len(warnings) > args.max_items:
        print(f"warning: ... {len(warnings) - args.max_items} more")
    return 1 if problems else 0


def cmd_checkpoint(args: argparse.Namespace) -> int:
    root = target_root(args)
    prompts = numbered_files(root, PROMPT_RE)
    results = numbered_files(root, RESULT_RE)
    latest = max(set(prompts) | set(results), default=0)
    end = args.end_round or latest
    start = args.start_round or max(1, end - 19)
    if end < start or end < 1:
        print("checkpoint: failed")
        print("- invalid or empty round range")
        return 1

    profile = load_profile(root) or detected_project_profile(root)
    docs_value = profile.get("docs_dir")
    output_dir = root / docs_value if docs_value else agent_dir(root) / "checkpoints"
    output_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_dir / f"workflow_checkpoint_p{start}_p{end}.md"
    if checkpoint_path.exists() and not args.force:
        print(f"refusing to overwrite existing {rel(checkpoint_path, root)}")
        return 1

    entries: list[str] = []
    for round_id in range(start, end + 1):
        prompt = prompts.get(round_id)
        result = results.get(round_id)
        entries.append(
            f"| {round_id} | {f'`{rel(prompt, root)}`' if prompt else 'missing'} | "
            f"{f'`{rel(result, root)}`' if result else 'missing'} | 待总结 |"
        )
    plan = project_plan_path(root)
    text = (
        f"# Workflow Checkpoint: Prompt {start}-{end}\n\n"
        "## 用途\n\n"
        "本文件用于压缩一段 prompt/result 历史，供后续轮次优先读取，减少重复加载旧记录。\n\n"
        "## 项目主线\n\n"
        f"- 项目计划：`{rel(plan, root) if plan else '未检测到'}`\n"
        f"- 覆盖轮次：{start}-{end}\n\n"
        "## 轮次索引\n\n"
        "| Round | Prompt | Result | 一句话结论 |\n"
        "|---:|---|---|---|\n"
        + "\n".join(entries)
        + "\n\n## 阶段目标与完成情况\n\n待根据上述 result 提炼。\n"
        "\n## 稳定结论\n\n待填写可复用、已验证的结论。\n"
        "\n## 负结果与解释边界\n\n待填写失败尝试、限制和不能过度解读的内容。\n"
        "\n## 关键产物与证据\n\n待填写代码、配置、数据、表格、图和 claim-to-evidence 映射。\n"
        "\n## 重要决策\n\n待填写技术选择、替代方案及决策原因。\n"
        "\n## 未解决问题与下一阶段\n\n待填写。\n"
    )
    checkpoint_path.write_text(text, encoding="utf-8")
    print("checkpoint: created")
    print(f"path: {rel(checkpoint_path, root)}")
    print("stop: have Codex synthesize the placeholder sections from bounded relevant results")
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

    progress = effective_progress(root)
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
    if not args.dry_run:
        save_progress(root, progress)

    print("continue-plan: ok")
    print(f"current_round: {progress.get('current_round', 0)}")
    print(f"latest_result_round: {latest_result}")
    print(f"next_round_start: {start}")
    print(f"next_round_end: {end}")
    print(f"rounds_requested: {args.rounds}")
    print("mode: bounded_continue")
    print(f"state_written: {not args.dry_run}")
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

    adopt = subparsers.add_parser("adopt", help="adopt an existing research repository without replacing its rules")
    add_target(adopt)
    adopt.add_argument("--plan", default=None, help="project plan path relative to target")
    adopt.add_argument("--rules", default=None, help="project rules path relative to target")
    adopt.add_argument("--docs-dir", default=None, help="documentation directory relative to target")
    adopt.add_argument("--dry-run", action="store_true", help="detect and report without writing files")
    adopt.add_argument("--update-helper", action="store_true", help="replace local scripts/research_flow.py")
    adopt.add_argument("--refresh-state", action="store_true", help="replace existing project profile and progress")
    adopt.set_defaults(func=cmd_adopt)

    status = subparsers.add_parser("status", help="show workflow state")
    add_target(status)
    status.set_defaults(func=cmd_status)

    context = subparsers.add_parser("context-summary", help="summarize repo context without reading large files")
    add_target(context)
    context.add_argument("--max-items", type=int, default=12, help="maximum rows per summary section")
    context.add_argument("--large-threshold", type=int, default=1024 * 1024, help="large file threshold in bytes")
    context.add_argument("--include-generated", action="store_true", help="enumerate generated/data directories too")
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
    title_group = draft.add_mutually_exclusive_group(required=True)
    title_group.add_argument("--title", help="prompt title; use --title-file for reliable non-ASCII text on Windows")
    title_group.add_argument("--title-file", help="UTF-8 file containing the prompt title")
    draft.add_argument("--focus", default=None, help="specific goal/focus text")
    draft.add_argument("--force", action="store_true", help="overwrite existing prompt")
    draft.add_argument("--plain-name", action="store_true", help="use promptN.md instead of promptN_title.md")
    draft.set_defaults(func=cmd_draft_prompt)

    prompt_check = subparsers.add_parser("prompt-check", help="check prompt scope and required concepts")
    add_target(prompt_check)
    prompt_check.add_argument("--round", type=int, required=True, help="round number")
    prompt_check.add_argument("--max-bytes", type=int, default=12_000, help="recommended maximum prompt size")
    prompt_check.add_argument("--max-tasks", type=int, default=5, help="recommended maximum numbered tasks")
    prompt_check.add_argument("--strict", action="store_true", help="fail on warnings")
    prompt_check.set_defaults(func=cmd_prompt_check)

    result = subparsers.add_parser("result-check", help="validate resultn.md structure")
    add_target(result)
    result.add_argument("--round", type=int, required=True, help="round number")
    result.add_argument("--mark-executed", action="store_true", help="update state to executed when valid")
    result.add_argument("--strict", action="store_true", help="require every recommended result concept")
    result.set_defaults(func=cmd_result_check)

    preflight = subparsers.add_parser("preflight", help="check readiness, Git, secrets, and large tracked files")
    add_target(preflight)
    preflight.add_argument("--round", type=int, default=None, help="optional prompt round to verify")
    preflight.add_argument("--large-threshold", type=int, default=10 * 1024 * 1024, help="large tracked file threshold")
    preflight.add_argument("--max-items", type=int, default=20, help="maximum warnings to print")
    preflight.set_defaults(func=cmd_preflight)

    checkpoint = subparsers.add_parser("checkpoint", help="create a bounded workflow checkpoint scaffold")
    add_target(checkpoint)
    checkpoint.add_argument("--start-round", type=int, default=None, help="first included round")
    checkpoint.add_argument("--end-round", type=int, default=None, help="last included round")
    checkpoint.add_argument("--force", action="store_true", help="overwrite existing checkpoint")
    checkpoint.set_defaults(func=cmd_checkpoint)

    commit = subparsers.add_parser("suggest-commit", help="suggest a commit message")
    add_target(commit)
    commit.add_argument("--round", type=int, required=True, help="round number")
    commit.add_argument("--summary", default=None, help="explicit summary")
    commit.set_defaults(func=cmd_suggest_commit)

    cont = subparsers.add_parser("continue-plan", help="plan a bounded N-round continuation")
    add_target(cont)
    cont.add_argument("--rounds", type=int, required=True, help="number of rounds to continue")
    cont.add_argument("--allow-large-n", action="store_true", help="allow more than the default maximum")
    cont.add_argument("--dry-run", action="store_true", help="plan rounds without writing workflow state")
    cont.set_defaults(func=cmd_continue_plan)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
