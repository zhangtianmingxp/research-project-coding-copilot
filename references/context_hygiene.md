# Context Hygiene For Large Research Projects

## Default Mode

Use low-context mode by default. The goal is to preserve scientific rigor while avoiding unnecessary token use.

Before reading broad project context, run:

```bash
python scripts/research_copilot.py context-summary --target .
```

Then use `rg` to locate the relevant sections, functions, config keys, or errors.

## What Not To Read By Default

Do not load these files wholesale unless the user explicitly asks or the task requires it:

- logs
- notebooks
- large Markdown plans or rules
- TSV/CSV/JSON manifests
- generated result tables
- model checkpoints
- figures or binary files
- full Git diffs
- many old `ans_qes/result*.md` files
- large `PROJECT_PLAN.md` or `PROJECT_RULES.md`

## Preferred Summaries

For structured files, summarize:

- file size
- row count
- column names
- missing-value counts
- unique key counts
- duplicate keys
- a few targeted rows

For code, use:

- `rg --files`
- `rg -n "symbol|config_key|error"`
- bounded excerpts around the matched function or block

For logs, use:

- command exit code
- stderr/stdout summary
- targeted searches for `ERROR`, `WARNING`, `Traceback`, or stage names

## Prompt Generation

When generating `promptn.md`, do not reload the entire project history. Use:

- `project_plan.md` headings and relevant sections
- `.research_agent/project_state.md`
- latest one to three relevant `result*.md` files
- targeted code/config excerpts

## Execution

When executing `promptn.md`, gather only the context needed for that prompt. If the prompt is too broad and would require reading many unrelated files, narrow the task and ask for user review instead of expanding blindly.

## Final Reporting

In `resultn.md`, record what was inspected and what was deliberately not loaded. This makes future rounds cheaper.
