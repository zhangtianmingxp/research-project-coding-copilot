---
name: research-project-coding-copilot
description: "Use when the user wants an interactive Codex or Claude Code workflow for long-running research coding projects: initialize a project template from a markdown research plan, generate promptn.md files, wait for user approval, execute approved prompts, write resultn.md files, and stop between rounds. This skill is for human-controlled research project progression, not a fully autonomous agent."
metadata:
  short-description: Interactive research coding workflow
---

# Research Project Coding Copilot

This skill turns a repository into a human-controlled research project workflow for Codex / Claude Code. It provides a reusable action CLI plus an installable repository template.

It is not an autonomous agent and must not call remote LLM APIs, auto-execute newly generated prompts, auto-generate the next round, or perform Git write operations.

## Core Rule

Every formal round is split into explicit user-controlled phases:

```text
project_plan.md -> ans_qes/promptn.md -> user review -> execute -> ans_qes/resultn.md -> user review -> stop
```

Never advance to the next phase without a clear user instruction.

## Short Command Contract

The user does not need to restate safety clauses such as "do not execute" or "do not create the next prompt". Treat these concise Chinese commands as complete instructions with built-in phase boundaries:

| User command | Required behavior |
| --- | --- |
| `初始化` | Initialize a new repository template, then stop |
| `接管项目` | Detect and adopt an existing repository while preserving project-owned files, then stop |
| `项目体检` | Run read-only context, structure, plan, and preflight checks |
| `状态` | Report current round, phase, and next valid action |
| `生成下一轮` or `下一轮` | Generate only the next prompt and stop for review |
| `修改当前 prompt：...` | Revise only the current prompt and stop |
| `执行当前轮` | Execute the latest current prompt, validate work, write the matching result, and stop |
| `修改当前 result：...` | Address the feedback, revalidate, update the current result, and stop |
| `继续 N 轮` | Generate and execute at most N rounds, then stop |

The short command itself is the user's authorization for the action named in that row. Do not ask the user to repeat the same authorization. Ask only when required information is missing, the target is ambiguous, or an approval boundary outside this workflow applies.

For `执行当前轮`, resolve the highest prompt round without a matching completed result unless the user names a round.

## Action CLI

Prefer the skill-level CLI for deterministic workflow actions:

```bash
python scripts/research_copilot.py init --target .
python scripts/research_copilot.py adopt --target . --dry-run
python scripts/research_copilot.py status --target .
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py check --target .
python scripts/research_copilot.py plan-check --target .
python scripts/research_copilot.py next-id --target .
python scripts/research_copilot.py draft-prompt --target . --title "..."
python scripts/research_copilot.py prompt-check --target . --round N
python scripts/research_copilot.py result-check --target . --round N --mark-executed
python scripts/research_copilot.py preflight --target . --round N
python scripts/research_copilot.py checkpoint --target . --start-round A --end-round B
python scripts/research_copilot.py continue-plan --target . --rounds N
```

The CLI is allowed to install template files, inspect state, create prompt drafts, validate result files, and update workflow state. It must not execute prompt tasks, call model APIs, or run `git add`, `git commit`, or `git push`.

On Windows, use `--title-file PATH` with a UTF-8 one-line file when a non-ASCII `--title` would be corrupted by shell argument encoding.

Recognize both plain and titled round files:

```text
prompt12.md
prompt12_任务短名.md
result12.md
result12_任务短名.md
```

Use `max(existing_rounds) + 1` for the next round. Report historical gaps but do not fill them automatically.

## Context Budget Rules

Default to low-context mode in every target repository, especially mature research projects.

Before generating prompts, executing tasks, or analyzing results:

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
8. Never read sensitive-looking files such as API-key, credential, token, `.pem`, or `.key` files. Report paths and Git tracking status only.

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
4. Stop after initialization. `初始化` alone does not include prompt generation.

## When Adopting An Existing Repository

Use this when a mature project already has plans, rules, prompt/result history, or custom documentation.

1. Preview detection without writing:

```bash
python scripts/research_copilot.py adopt --target . --dry-run
```

2. Check that the detected project plan, rules, context rules, docs directory, environment docs, and current round are unambiguous.
3. When the user said `接管项目`, run `adopt` without `--dry-run` in the same turn if detection is unambiguous. The command already authorizes this non-destructive adoption, so do not ask for duplicate confirmation.
4. Add only `.research_agent` state/profile files and the local helper. Preserve existing `AGENTS.md`, project rules, plans, and documentation. Repeated adoption also preserves the existing profile and progress unless the user explicitly requests `--refresh-state`.
5. Use `PROJECT_PLAN*.md` or a configured plan path when `project_plan.md` is not present. Stop and explain only when multiple candidates or conflicting rules make the target genuinely ambiguous.

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
python scripts/research_copilot.py preflight --target .
```

2. Read `.research_agent/AGENTS.md`, relevant sections of `PROJECT_RULES.md`, `project_plan.md`, `.research_agent/project_state.md`, and recent relevant `ans_qes/result*.md` files only as needed.
3. Create or scaffold the prompt with:

```bash
python scripts/research_copilot.py draft-prompt --target . --round N --title "..." --focus "..."
```

4. Edit the generated `ans_qes/promptn.md` into a high-quality Chinese task prompt using the project plan and current progress.
5. Run `prompt-check --round N`. Split prompts that are too broad, contain too many independent tasks, or exceed the configured size guideline.
6. Stop and wait for user review. Do not execute the prompt.

## When Executing `promptn.md`

Use this when the user says `执行当前轮`, asks to execute the current prompt, or names a specific prompt to execute.

1. Read the specified `ans_qes/promptn.md` and relevant sections of `PROJECT_RULES.md`.
2. Run `preflight --round N` before expensive, external-API, data-processing, or long-running work.
3. Use pilot-first execution. Estimate cost/scale, cache external API outputs, record the runtime environment, and make long jobs resumable when relevant.
4. Execute only that round's task.
5. Run focused checks/tests appropriate to the changes.
6. Write `ans_qes/resultn.md`.
7. Validate and mark the result:

```bash
python scripts/research_copilot.py result-check --target . --round N --mark-executed
```

8. Stop and wait for user review. Do not generate `prompt{n+1}.md`.

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
   - the task would require external credentials or destructive changes;
   - context needed becomes too broad for low-context mode.
5. Do not run Git write operations. Remind the user that each reviewed round can be manually committed and pushed to GitHub to preserve history.
6. Never continue beyond N rounds without a new user instruction.

## When History Becomes Large

After roughly 10-20 substantial rounds, or when prompt/result history becomes expensive to reload, create a checkpoint scaffold:

```bash
python scripts/research_copilot.py checkpoint --target . --start-round A --end-round B
```

Synthesize it into a compact Chinese summary containing stable conclusions, negative results, interpretation limits, key artifacts, decisions, claim-to-evidence links, and unresolved questions. Prefer this checkpoint plus the latest 1-3 results over rereading the full history.

## GitHub History Recommendation

This skill does not run `git add`, `git commit`, or `git push`, and Git operations are not workflow phases.

After a prompt has been executed, its `resultn.md` has been generated, and the user has reviewed the round, recommend that the user manually commit and push that round's code, prompt, result, and necessary documentation to GitHub before starting the next round. This preserves the research path without making the skill responsible for repository writes.

## References

For the full protocol, read `references/workflow_protocol.md` when the task involves prompt/result lifecycle details or state updates.

For context-budget behavior in large projects, read `references/context_hygiene.md`.

For scientific research code quality, benchmark discipline, model development, data provenance, and publication-readiness rules, read `references/scientific_project_rules.md`.

The template copied into research repositories lives in `assets/template/`.
