# Interactive Research Workflow Protocol

## Purpose

This skill supports long-running research coding projects where the human user remains in control of every step. The skill provides a reusable workflow and repository template, while Codex or Claude Code remains the interactive executor.

## Repository Template

The installable template is in:

```text
assets/template/
```

It contains:

```text
AGENTS.md
PROJECT_RULES.md
project_plan.md
ans_qes/
.research_agent/
scripts/research_flow.py
tests/
```

## Skill-Level CLI

Use the skill-level CLI from the skill directory when a deterministic action is needed:

```text
scripts/research_copilot.py
```

Supported commands:

- `init --target PATH`: copy `assets/template/` into a target repository without overwriting existing files unless `--force` is set.
- `status --target PATH`: print current round, phase, latest prompt/result/commit, and open issues.
- `context-summary --target PATH`: print a bounded repository summary, file counts, large files, top directories, project plan headings, recent round files, and Git status without loading large contents.
- `check --target PATH`: check required template files, prompt/result numbering, and safety flags.
- `plan-check --target PATH`: warn when `project_plan.md` still looks like an unfilled template.
- `next-id --target PATH`: print the next prompt/result round number.
- `draft-prompt --target PATH --title TITLE`: create `ans_qes/promptn.md`, update state to `prompt_drafted`, then stop.
- `result-check --target PATH --round N --mark-executed`: validate `resultn.md` sections and update state to `executed`.
- `suggest-commit --target PATH --round N`: print a `pN: ...` commit message suggestion and changed files.
- `continue-plan --target PATH --rounds N`: check numbering and record a bounded continuation request for the next N rounds.

The CLI is deliberately bounded. It does not execute prompt tasks, call model APIs, commit, push, or generate the next round automatically.

## Bounded Continuation

When the user explicitly asks to continue N rounds from the current progress, Codex may run a bounded continuation loop. This is not the default mode and must never be infinite.

Required setup:

```bash
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py continue-plan --target . --rounds N
```

For each round:

1. Generate `ans_qes/promptn.md`.
2. Execute only that prompt.
3. Generate `ans_qes/resultn.md`.
4. Run focused checks/tests.
5. Run `result-check --round n --mark-executed`.
6. Continue only if the next step is clear and within the user's requested N rounds.

Stop conditions:

- N rounds completed.
- test/check failure without an obvious local fix.
- unclear scientific or engineering next step.
- risk of data leakage, benchmark unfairness, secret exposure, large file commit, destructive change, or push.
- context needs become too broad.

Unless the user explicitly requested auto-commit, bounded continuation should not commit; it should provide commit suggestions.

## State Files

`.research_agent/project_state.md` is the human-readable state record.

`.research_agent/progress.json` is the machine-readable state record. These boolean values must remain false unless the user explicitly changes the protocol:

```json
{
  "auto_next": false,
  "auto_execute_prompt": false,
  "auto_commit": false,
  "auto_push": false
}
```

## Allowed Round States

```text
idle
prompt_drafted
prompt_approved
executed
result_reviewed
commit_suggested
committed
```

Do not move from `committed` to a new prompt automatically.

## Prompt Generation

Generate a prompt only when the user asks. A good `promptn.md` includes:

- task title
- project context
- current progress
- relevant `PROJECT_RULES.md` constraints
- concrete goals
- implementation requirements
- expected outputs
- checks/tests
- explicit instruction not to execute yet

After writing the prompt, update state and stop.

## Prompt Execution

Execute only when the user explicitly says to execute a specific prompt. The resulting `resultn.md` should include:

- corresponding prompt path
- execution summary
- completed work
- changed files
- commands run
- verification
- risks and limitations
- whether relevant `PROJECT_RULES.md` constraints were satisfied
- commit suggestion
- next-step ideas without starting the next prompt

After writing the result, update state and stop.

## Commit Behavior

Commit messages should normally be:

```text
pN: short summary
```

Never commit merely because a result was generated. Wait for user confirmation. Never push unless the user explicitly asks.

## Context Hygiene

Default to low-context mode. Large research repositories often contain logs, generated outputs, manifests, notebooks, result tables, model artifacts, and long planning documents that can waste context or distort the current task.

Required sequence:

1. Run `context-summary --target PATH`.
2. Search with `rg` before opening files.
3. Read bounded excerpts, not whole large files.
4. Summarize structured/generated files by size, schema, columns, row counts, missing values, key counts, and targeted examples.
5. Read log files only when a failure cannot be diagnosed from stderr/stdout; search logs for `ERROR`, `WARNING`, `Traceback`, or stage names first.
6. Reuse previous `resultn.md` summaries instead of rereading many old files.
7. Expand context only when necessary, and state why.

Context hygiene is not permission to skip verification, tests, leakage checks, or scientific review.
