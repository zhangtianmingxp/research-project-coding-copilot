---
name: research-project-coding-copilot
description: "Use when the user wants an interactive Codex or Claude Code workflow for long-running research coding projects: initialize a project template from a markdown research plan, generate promptn.md files, wait for user approval, execute approved prompts, write resultn.md files, suggest Git commit messages, and stop between rounds. This skill is for human-controlled research project progression, not a fully autonomous agent."
metadata:
  short-description: Interactive research coding workflow
---

# Research Project Coding Copilot

This skill turns a repository into a human-controlled research project workflow for Codex / Claude Code. It provides a reusable action CLI plus an installable repository template.

It is not an autonomous agent and must not call remote LLM APIs, auto-execute newly generated prompts, auto-generate the next round, auto-commit, or auto-push.

## Core Rule

Every formal round is split into explicit user-controlled phases:

```text
project_plan.md -> ans_qes/promptn.md -> user review -> execute -> ans_qes/resultn.md -> user review -> commit suggestion/commit -> stop
```

Never advance to the next phase without a clear user instruction.

## Action CLI

Prefer the skill-level CLI for deterministic workflow actions:

```bash
python scripts/research_copilot.py init --target .
python scripts/research_copilot.py status --target .
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py check --target .
python scripts/research_copilot.py plan-check --target .
python scripts/research_copilot.py next-id --target .
python scripts/research_copilot.py draft-prompt --target . --title "..."
python scripts/research_copilot.py result-check --target . --round N --mark-executed
python scripts/research_copilot.py suggest-commit --target . --round N
python scripts/research_copilot.py continue-plan --target . --rounds N
```

The CLI is allowed to install template files, inspect state, create prompt drafts, validate result files, update workflow state, and suggest commit messages. It must not execute prompt tasks, commit, push, or call model APIs.

## Context Budget Rules

Default to low-context mode in every target repository, especially mature research projects.

Before generating prompts, executing tasks, analyzing results, or suggesting commits:

1. Run:

```bash
python scripts/research_copilot.py context-summary --target .
```

2. Search before reading:

```bash
rg -n "term|heading|function|error" .
```

3. Read bounded excerpts only. Avoid full reads of large Markdown files, TSV/CSV/JSON manifests, notebooks, generated outputs, logs, result tables, model artifacts, and long diffs.
4. Do not read log files by default. For failures, search only for `ERROR`, `WARNING`, `Traceback`, failing stage names, or relevant timestamps.
5. Do not repeatedly reload `project_plan.md`, `PROJECT_PLAN.md`, `PROJECT_RULES.md`, or many old `result*.md` files. Reuse summaries and load only the sections needed for the current round.
6. When a file is large or generated, summarize it with counts, headings, schema, columns, file size, and a few targeted rows instead of loading raw content.
7. If broader context is truly needed, state why, then expand scope gradually.

## Scientific Code Development Rules

When helping develop research code, also follow `references/scientific_project_rules.md`.

In target repositories initialized by this skill, `PROJECT_RULES.md` is the durable project-level rule file. Treat it as mandatory, but read it with low-context discipline:

- use `rg -n "section|topic|keyword" PROJECT_RULES.md` before opening it;
- read only the relevant section unless the task requires a broader audit;
- preserve project rigor even when keeping context small.

## When Initializing A Repository

Use this when the user asks to create, install, scaffold, or apply the research workflow template.

1. Run the action CLI from this skill directory, targeting the user's current research repository:

```bash
python scripts/research_copilot.py init --target .
```

2. If files already exist, do not overwrite unless the user explicitly requested it. Use `--force` only for explicit overwrite requests.
3. Tell the user to fill in `project_plan.md` or replace it with their real research plan.
4. Stop after initialization. Do not create `prompt1.md` unless the user asked for it.

If the user only wants to inspect readiness, run:

```bash
python scripts/research_copilot.py check --target .
python scripts/research_copilot.py plan-check --target .
```

## When Generating `promptn.md`

Use this when the user asks to generate a prompt, next prompt, `prompt1.md`, `prompt2.md`, or a task prompt from `project_plan.md`.

1. Run readiness checks:

```bash
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py check --target .
python scripts/research_copilot.py next-id --target .
```

2. Read `.research_agent/AGENTS.md`, relevant sections of `PROJECT_RULES.md`, `project_plan.md`, `.research_agent/project_state.md`, and recent relevant `ans_qes/result*.md` files only as needed.
3. Create or scaffold the prompt with:

```bash
python scripts/research_copilot.py draft-prompt --target . --round N --title "..." --focus "..."
```

4. Edit the generated `ans_qes/promptn.md` into a high-quality Chinese task prompt using the project plan and current progress.
5. Stop and wait for user review. Do not execute the prompt.

## When Executing `promptn.md`

Use this only when the user explicitly says to execute a specific prompt.

1. Read the specified `ans_qes/promptn.md` and relevant sections of `PROJECT_RULES.md`.
2. Execute only that round's task.
3. Run focused checks/tests appropriate to the changes.
4. Write `ans_qes/resultn.md`.
5. Validate and mark the result:

```bash
python scripts/research_copilot.py result-check --target . --round N --mark-executed
```

6. Stop and wait for user review. Do not generate `prompt{n+1}.md`.

If `resultn.md` already exists, do not overwrite it unless the user explicitly asks.

## When The User Asks To Continue N Rounds

Use this only when the user explicitly asks to continue, run, or advance a bounded number of rounds, such as "从 result5.md 继续执行 3 轮" or "继续 N 轮".

This is a bounded continuation mode, not unlimited autopilot.

1. Run:

```bash
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py continue-plan --target . --rounds N
```

2. Start from the next available round after existing prompt/result files.
3. For each round, generate `ans_qes/promptn.md`, execute it, write `ans_qes/resultn.md`, run focused checks, and validate with:

```bash
python scripts/research_copilot.py result-check --target . --round n --mark-executed
```

4. Stop immediately when any of these occurs:
   - requested N rounds are complete;
   - tests/checks fail and the fix is not obvious;
   - the next step is scientifically ambiguous;
   - a large data/model/checkpoint/secret-risk change appears;
   - the task would require push, external credentials, or destructive changes;
   - context needed becomes too broad for low-context mode.
5. Do not push. Commit during bounded continuation only if the user explicitly asked for auto-commit; otherwise suggest commit messages and stop with a summary.
6. Never continue beyond N rounds without a new user instruction.

## When Suggesting Or Making Commits

Use this only when the user explicitly asks for a commit message or commit.

1. Inspect `git status` and the current round's prompt/result.
2. Suggest a message with:

```bash
python scripts/research_copilot.py suggest-commit --target . --round N
```

3. Commit only after explicit user confirmation.
4. Do not push unless the user explicitly asks.
5. Stop after commit.

## References

For the full protocol, read `references/workflow_protocol.md` when the task involves prompt/result lifecycle details, state updates, or commit behavior.

For context-budget behavior in large projects, read `references/context_hygiene.md`.

For scientific research code quality, benchmark discipline, model development, data provenance, and publication-readiness rules, read `references/scientific_project_rules.md`.

The template copied into research repositories lives in `assets/template/`.
