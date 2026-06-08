---
name: research-project-coding-copilot
description: "Use when the user wants an interactive Codex or Claude Code workflow for long-running research coding projects: initialize a project template from a markdown research plan, generate promptn.md files, wait for user approval, execute approved prompts, write resultn.md files, suggest Git commit messages, and stop between rounds. This skill is for human-controlled research project progression, not a fully autonomous agent."
metadata:
  short-description: Interactive research coding workflow
---

# Research Project Coding Copilot

This skill turns a repository into a human-controlled research project workflow for Codex / Claude Code. It is not an autonomous agent and must not call remote LLM APIs, auto-execute newly generated prompts, auto-generate the next round, auto-commit, or auto-push.

## Core Rule

Every formal round is split into explicit user-controlled phases:

```text
project_plan.md -> ans_qes/promptn.md -> user review -> execute -> ans_qes/resultn.md -> user review -> commit suggestion/commit -> stop
```

Never advance to the next phase without a clear user instruction.

## When Initializing A Repository

Use this when the user asks to create, install, scaffold, or apply the research workflow template.

1. Run the installer from this skill directory, targeting the user's current research repository:

```bash
python scripts/install_template.py --target .
```

2. If files already exist, do not overwrite unless the user explicitly requested it. Use `--force` only for explicit overwrite requests.
3. Tell the user to fill in `project_plan.md` or replace it with their real research plan.
4. Stop after initialization. Do not create `prompt1.md` unless the user asked for it.

## When Generating `promptn.md`

Use this when the user asks to generate a prompt, next prompt, `prompt1.md`, `prompt2.md`, or a task prompt from `project_plan.md`.

1. Read `.research_agent/AGENTS.md`, `project_plan.md`, `.research_agent/project_state.md`, and recent relevant `ans_qes/result*.md` files only as needed.
2. Use the next available number unless the user specified a round.
3. Write `ans_qes/promptn.md` in Chinese by default.
4. Update `.research_agent/project_state.md` and `.research_agent/progress.json` to `prompt_drafted`.
5. Stop and wait for user review. Do not execute the prompt.

The helper command may be used for a scaffold:

```bash
python scripts/research_flow.py init-round --round N --title "..."
```

## When Executing `promptn.md`

Use this only when the user explicitly says to execute a specific prompt.

1. Read the specified `ans_qes/promptn.md`.
2. Execute only that round's task.
3. Run focused checks/tests appropriate to the changes.
4. Write `ans_qes/resultn.md`.
5. Update state to `executed`.
6. Stop and wait for user review. Do not generate `prompt{n+1}.md`.

If `resultn.md` already exists, do not overwrite it unless the user explicitly asks.

## When Suggesting Or Making Commits

Use this only when the user explicitly asks for a commit message or commit.

1. Inspect `git status` and the current round's prompt/result.
2. Suggest `pN: concise summary`.
3. Commit only after explicit user confirmation.
4. Do not push unless the user explicitly asks.
5. Stop after commit.

## References

For the full protocol, read `references/workflow_protocol.md` when the task involves prompt/result lifecycle details, state updates, or commit behavior.

The template copied into research repositories lives in `assets/template/`.
