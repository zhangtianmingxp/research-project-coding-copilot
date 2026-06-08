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
project_plan.md
ans_qes/
.research_agent/
scripts/research_flow.py
tests/
```

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

- Search before reading large files.
- Read bounded excerpts.
- Do not dump full logs.
- Summarize structured files programmatically.
- Preserve scientific rigor while keeping context small.
