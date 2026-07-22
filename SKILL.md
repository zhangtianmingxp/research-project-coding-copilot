---
name: research-project-coding-copilot
description: "Use when the user wants a publication-first, interactive Codex or Claude Code workflow for long-running research coding projects: initialize from a markdown research plan, run focused 1-3 round quick validations with GO/PIVOT/STOP/INCONCLUSIVE decisions, generate compact promptn.md/resultn.md files, and maintain a lightweight paper_map.md. Human-controlled, not a fully autonomous agent."
metadata:
  short-description: Publication-first research coding workflow
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

## Publication-First Decision Rule

Treat the paper's central question and evidence chain as the optimization target. Engineering quality is necessary infrastructure, not the default source of new rounds.

Before drafting the next prompt:

1. Identify the central claim or paper-critical uncertainty advanced by the round.
2. Prefer work that produces decision-grade evidence, unlocks a named blocker to that evidence, or strengthens a reviewer-relevant weakness.
3. Do not spend repeated rounds on contracts, schemas, refactors, documentation, extra validation, or tiny reruns unless they block correctness, reproducibility, data integrity, or the next scientifically informative experiment.
4. If two consecutive rounds are mainly engineering or smoke validation, make the next round advance a scientific analysis at an adequate scale unless a concrete blocker makes that impossible. State the blocker and the evidence needed to clear it.
5. Use CNS or strong field-leading journal review standards as an ambition benchmark when requested: prioritize novelty, scientific importance, rigorous statistics, robustness, generalization, mechanism, and a coherent claim-to-figure story. Do not claim that any workflow guarantees publication.

Honor scale requirements from the user and project plan. If the project states that at least 500 cells, multiple cohorts, a full chromosome set, or another minimum is needed to distinguish effects, treat that as the minimum for scientific inference. Never replace it with a convenient tiny subset.

For repositories initialized with an older version of this skill, interpret legacy unconditional `pilot-first` wording through the tiered rules in this file: it authorizes an engineering smoke only for a new or materially changed failure mode and never overrides an explicit scientifically informative minimum. Preserve project-owned files unless the user asks to migrate them.

## Short Command Contract

The user does not need to restate safety clauses such as "do not execute" or "do not create the next prompt". Treat these concise Chinese commands as complete instructions with built-in phase boundaries:

| User command | Required behavior |
| --- | --- |
| `初始化` | Initialize a new repository template, then stop |
| `接管项目` | Detect and adopt an existing repository while preserving project-owned files, then stop |
| `生成项目计划书：...` | Draft or improve `project_plan.md` from the user's research idea |
| `整理项目计划书：...` | Synthesize `project_plan.md` from an existing repository plus the user's interpretation |
| `项目体检` | Run read-only context, structure, plan, and preflight checks |
| `状态` | Report current round, phase, and next valid action |
| `快速验证：...` | Draft the first compact prompt for one claim and one decisive comparison; use at most 1-3 rounds |
| `继续快速验证` | Draft only the next focused prompt after an INCONCLUSIVE quick-validation result, up to round 3 |
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

Use proportionate engineering: implement and test what is needed to make the scientific result trustworthy, but do not let optional architecture polish, exhaustive defensive checks, or documentation completeness displace the paper's critical path.

## When Initializing A Repository

Use this when the user asks to create, install, scaffold, or apply the research workflow template.

1. Run the action CLI from this skill directory, targeting the user's current research repository:

```bash
python scripts/research_copilot.py init --target .
```

2. If files already exist, do not overwrite unless the user explicitly requested it. Use `--force` only for explicit overwrite requests.
3. Explain that `project_plan.md` is required before formal rounds. The user may edit it manually or ask `生成项目计划书：...` and provide their research idea, data, intended methods, constraints, and desired paper/software outcome.
4. Stop after initialization. `初始化` alone does not include prompt generation.

## When Adopting An Existing Repository

Use this when a mature project already has plans, rules, prompt/result history, or custom documentation.

1. Preview detection without writing:

```bash
python scripts/research_copilot.py adopt --target . --dry-run
```

2. Check that the detected project plan, rules, context rules, docs directory, environment docs, and current round are unambiguous.
3. When the user said `接管项目`, run `adopt` without `--dry-run` in the same turn if detection is unambiguous. The command already authorizes this non-destructive adoption, so do not ask for duplicate confirmation.
4. Add only `.research_agent` state/profile files, the local helper, and `paper_map.md` when missing. Preserve existing `AGENTS.md`, project rules, plans, documentation, and any existing `paper_map.md`. Repeated adoption also preserves the existing profile and progress unless the user explicitly requests `--refresh-state`.
5. Use `PROJECT_PLAN*.md` or a configured plan path when `project_plan.md` is not present. Stop and explain only when multiple candidates or conflicting rules make the target genuinely ambiguous.

If the user only wants to inspect readiness, run:

```bash
python scripts/research_copilot.py check --target .
python scripts/research_copilot.py plan-check --target .
```

## When Creating Or Updating The Project Plan

The project plan is the required source of truth for selecting future rounds. Initialization alone is not enough.

For a new project when the user says `生成项目计划书：...`:

1. Use the user's stated research question, available data, intended methods, constraints, desired outputs, and publication goal.
2. Ask only for genuinely blocking information. Otherwise create a clearly labeled draft with explicit assumptions.
3. Replace template placeholders with concrete content covering background, scientific questions, goals, data, task definition, methods, engineering structure, validation standards, first-stage objectives, and risks.
4. Write explanatory Markdown in Chinese by default, then run `plan-check` and stop for user review.

For an existing repository when the user says `整理项目计划书：...`:

1. Run `context-summary`, then inspect bounded relevant excerpts from README files, docs, configs, source structure, checkpoints, and recent results.
2. Combine repository evidence with the user's interpretation and intended direction.
3. Clearly distinguish implemented work, validated results, user-supplied understanding, assumptions, and future plans. Do not infer unsupported scientific conclusions from filenames alone.
4. Create or update the detected project plan without overwriting unrelated project-owned documentation.
5. Run `plan-check` and stop for user review. Do not generate `prompt1` or the next prompt in the same action unless the user explicitly requested both.

## When Generating `promptn.md`

Use this when the user asks to generate a prompt, next prompt, `prompt1.md`, `prompt2.md`, or a task prompt from `project_plan.md`.

1. Run readiness checks:

```bash
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py check --target .
python scripts/research_copilot.py next-id --target .
python scripts/research_copilot.py preflight --target .
```

If `plan-check` reports missing content, template placeholders, or an obviously underspecified plan, stop and direct the user to write the plan or use `生成项目计划书：...` / `整理项目计划书：...`. Do not draft a formal prompt unless the user explicitly chooses the exceptional `--allow-incomplete-plan` override.

2. Read `.research_agent/AGENTS.md`, relevant sections of `PROJECT_RULES.md`, `project_plan.md`, `.research_agent/project_state.md`, and recent relevant `ans_qes/result*.md` files only as needed.
3. Keep the prompt compact. It must contain only these sections: `科学决策`, `最小充分工作`, `实验层级与规模`, `判据`, and `产物`. Do not repeat global project, Git, safety, context, or engineering rules inside each prompt.
4. Define one claim, one decisive comparison, the minimum decision-grade scale, and explicit GO/PIVOT/STOP/INCONCLUSIVE criteria. Tiny smoke data may verify code paths only and cannot support a scientific decision.
5. Create or scaffold the prompt with:

```bash
python scripts/research_copilot.py draft-prompt --target . --round N --title "..." --focus "..."
```

6. Edit the generated `ans_qes/promptn.md` into a high-quality Chinese task prompt using the project plan and current progress.
7. Run `prompt-check --round N`. Split prompts that are too broad, contain too many independent tasks, or exceed the configured size guideline.
8. Stop and wait for user review. Do not execute the prompt.

## When Executing `promptn.md`

Use this when the user says `执行当前轮`, asks to execute the current prompt, or names a specific prompt to execute.

1. Read the specified `ans_qes/promptn.md` and relevant sections of `PROJECT_RULES.md`.
2. Run `preflight --round N` before expensive, external-API, data-processing, or long-running work.
3. Use tiered validation:
   - engineering smoke/dry-run: the smallest data needed to catch interface, parsing, shape, dependency, and runtime failures; make no scientific inference;
   - decision-grade experiment: the minimum scientifically informative scale defined by the plan, user, heterogeneity, split design, expected effect, and uncertainty;
   - paper-grade run: the full planned scale, replicates/seeds, strict splits, uncertainty analysis, robustness checks, and external or orthogonal validation relevant to the claim.
4. Reuse prior smoke evidence when the code path and inputs are materially unchanged. Do not require a new tiny pilot before every formal run.
5. Execute only that round's task. Estimate cost/scale, cache external API outputs, record the runtime environment, and make long jobs resumable when relevant.
6. Run focused, risk-proportionate checks. Do not add unrelated tests or repeatedly investigate issues that cannot affect the central result.
7. Write a compact `ans_qes/resultn.md` containing only: `完成内容`, `关键证据`, `决策`, `Claim 边界`, `产物与命令`, and `下一项最高价值工作`. The decision must be exactly GO, PIVOT, STOP, or INCONCLUSIVE.
8. Validate and mark the result:

```bash
python scripts/research_copilot.py result-check --target . --round N --mark-executed
```

9. Stop and wait for user review. Do not generate `prompt{n+1}.md`.

If `resultn.md` already exists, do not overwrite it unless the user explicitly asks.

## Quick Validation Mode

Use this when the user says `快速验证：<claim or question>`.

1. Select exactly one claim and one decisive comparison.
2. Use the smallest scientifically decision-grade scale, never a convenience-scale smoke substitute.
3. Plan at most 1-3 prompt/result rounds. The first command drafts only the first prompt and stops for review.
4. End each executed round with exactly one decision:
   - `GO`: the criterion is met; continue the claim or prepare paper-grade validation;
   - `PIVOT`: the claim remains valuable, but change the comparison, method, or hypothesis;
   - `STOP`: adequate decision-grade evidence fails the criterion or reveals fatal infeasibility;
   - `INCONCLUSIVE`: evidence is insufficient or ambiguous; name the single missing piece that could resolve it.
5. `GO`, `PIVOT`, and `STOP` end the quick validation. After `INCONCLUSIVE`, `继续快速验证` may draft one focused next prompt if fewer than 3 rounds have been used. At round 3, stop even if the decision remains INCONCLUSIVE.
6. Do not create a separate quick-validation registry or state file. Infer the sequence from the compact prompts/results.

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
   - another engineering-only or tiny-smoke round would not remove a concrete blocker or advance paper-level evidence.
5. Do not run Git write operations. Remind the user that each reviewed round can be manually committed and pushed to GitHub to preserve history.
6. Never continue beyond N rounds without a new user instruction.

## When History Becomes Large

After roughly 10-20 substantial rounds, or when prompt/result history becomes expensive to reload, create a checkpoint scaffold:

```bash
python scripts/research_copilot.py checkpoint --target . --start-round A --end-round B
```

Synthesize it into a compact Chinese summary containing stable conclusions, negative results, interpretation limits, key artifacts, decisions, claim-to-evidence links, and unresolved questions. Prefer this checkpoint plus the latest 1-3 results over rereading the full history.

## Paper Evidence Map

Use only the root `paper_map.md`; do not create additional claim, experiment, figure, or evidence registries.

Update it only when:

- a decision-grade result appears;
- a claim changes;
- a claim is about to move to paper-grade validation;
- manuscript writing begins.

Do not update it after routine engineering, smoke, documentation, or inconclusive maintenance work. Keep one row per claim with: Claim, decisive experiment, current evidence, status, target figure/table, and missing evidence.

## GitHub History Recommendation

This skill does not run `git add`, `git commit`, or `git push`, and Git operations are not workflow phases.

After a prompt has been executed, its `resultn.md` has been generated, and the user has reviewed the round, recommend that the user manually commit and push that round's code, prompt, result, and necessary documentation to GitHub before starting the next round. This preserves the research path without making the skill responsible for repository writes.

## References

For the full protocol, read `references/workflow_protocol.md` when the task involves prompt/result lifecycle details or state updates.

For context-budget behavior in large projects, read `references/context_hygiene.md`.

For scientific research code quality, benchmark discipline, model development, data provenance, and publication-readiness rules, read `references/scientific_project_rules.md`.

The template copied into research repositories lives in `assets/template/`.
