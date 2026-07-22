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
- `adopt --target PATH --dry-run`: detect an existing project's plan, rules, docs, environment records, naming style, and current round; remove `--dry-run` to install workflow state without replacing project-owned files. Repeated adoption preserves the profile/progress unless `--refresh-state` is explicit.
- `status --target PATH`: print current round, phase, latest prompt/result, and open issues.
- `context-summary --target PATH`: print a bounded repository summary, file counts, large files, top directories, project plan headings, recent round files, and Git status without loading large contents.
- `check --target PATH`: check required template files, prompt/result numbering, and safety flags.
- `plan-check --target PATH`: warn when `project_plan.md` still looks like an unfilled template.
- `next-id --target PATH`: print the next prompt/result round number.
- `draft-prompt --target PATH --title TITLE`: create `ans_qes/promptn.md`, update state to `prompt_drafted`, then stop. On Windows, `--title-file PATH` avoids non-ASCII shell argument corruption.
- `prompt-check --target PATH --round N`: warn when a prompt is oversized, contains too many independent tasks, or lacks expected task concepts.
- `result-check --target PATH --round N --mark-executed`: validate `resultn.md` sections and update state to `executed`.
- `preflight --target PATH --round N`: check plan/rules, round pairing, Git state, sensitive-looking paths, large tracked files, and runtime documentation.
- `checkpoint --target PATH --start-round A --end-round B`: create a compact workflow-checkpoint scaffold for long project history.
- `continue-plan --target PATH --rounds N`: check numbering and record a bounded continuation request for the next N rounds.

The CLI is deliberately bounded. It does not execute prompt tasks, call model APIs, perform Git writes, or generate the next round automatically.

Round filenames may include task titles, such as `prompt12_任务短名.md`. The next round is the maximum existing round plus one; historical gaps are warnings, not slots to refill.

## Short User Commands

The user can control the workflow with concise commands. Guardrails are implicit and do not need to be repeated in every request:

- `初始化`: initialize only, then stop.
- `接管项目`: adopt an existing project while preserving its files, then stop.
- `生成项目计划书：...`: draft or improve a project plan from the user's research idea.
- `整理项目计划书：...`: synthesize a project plan from an existing repository and the user's interpretation.
- `项目体检`: run read-only readiness checks.
- `状态`: report current state and next action.
- `生成下一轮` or `下一轮`: generate the next prompt only.
- `执行当前轮`: execute the current prompt and write the matching result only.
- `继续 N 轮`: generate and execute at most N rounds, then stop.

The named short command is sufficient authorization for its named action. Do not ask for a duplicate confirmation.

## Existing Project Adoption

Do not force mature repositories into the default template names. Detect and record project-owned paths in `.research_agent/project_profile.json`, including:

- `PROJECT_PLAN*.md` or another configured project plan;
- project and context rule files;
- `doc/` or `docs/`;
- output/generated directories;
- runtime environment documents;
- titled or plain prompt/result naming.

Preserve existing rules and plans. Install only missing workflow-control files.

## Project Plan Prerequisite

A reviewed project plan is required before formal prompt rounds. Initialization only creates the template.

For a new project, the user may write `project_plan.md` directly or ask the skill to generate it from their research question, available data, intended methods, constraints, and desired publication or software outcome.

For an existing project, combine bounded evidence from code, README files, docs, configs, checkpoints, and recent results with the user's understanding. Clearly separate implemented work, validated results, user-provided interpretation, assumptions, and future plans.

Run `plan-check` before prompt generation. If placeholders or material omissions remain, stop for plan review rather than generating a formal prompt. The CLI permits an explicit `--allow-incomplete-plan` override only for exceptional user-directed cases.

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
- risk of data leakage, benchmark unfairness, secret exposure, large files, or destructive change.
- context needs become too broad.

The bounded loop does not perform Git writes. At completion, remind the user that reviewed rounds can be manually committed and pushed to GitHub.

## State Files

`.research_agent/project_state.md` is the human-readable state record.

`.research_agent/progress.json` is the machine-readable state record. These boolean values remain false:

```json
{
  "auto_next": false,
  "auto_execute_prompt": false
}
```

## Allowed Round States

```text
idle
prompt_drafted
prompt_approved
executed
result_reviewed
```

Do not move from `result_reviewed` to a new prompt automatically.

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

Run `prompt-check` before execution. A large prompt with many independent tasks should normally be split into multiple rounds.

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
- next-step ideas without starting the next prompt

After writing the result, update state and stop.

Result validation is concept-based. Accept project-specific headings such as `本轮目的`, `核心数值`, `QC 结果`, and `解释边界` when they satisfy the same semantic requirements as the default template.

## Long-Running And External Work

Before expensive data processing, model inference, or external API calls:

1. Classify the run as engineering smoke, decision-grade, or paper-grade.
2. Run a small smoke/dry-run only when the code path, input contract, environment, or failure mode is new or materially changed.
3. Treat smoke output as engineering evidence only. Do not use it to rank methods, infer an effect, reject a hypothesis, or change the paper direction.
4. Set decision-grade scale from the project plan, user/domain minimum, heterogeneity, split design, expected effect, and uncertainty. Never shrink an explicit minimum merely for convenience.
5. Reuse prior smoke QC and promote promptly to the scientifically informative or formal scale.
6. Estimate input scale, runtime, API requests, and storage; record environment and dependency versions.
7. Cache external responses, make work resumable, and keep credentials outside tracked files and model context.

## History Compaction And Evidence

For long projects, create checkpoints every 10-20 substantial rounds. Each checkpoint should summarize:

- stage objective and completion status;
- stable conclusions and negative results;
- interpretation boundaries;
- key code/config/data/figure artifacts;
- important decisions and rejected alternatives;
- claim-to-evidence mapping;
- unresolved questions and next stage.

Maintain a `doc/README.md` or `docs/README.md` with recommended reading order and current conclusion entry points.

## GitHub History Recommendation

The skill never runs `git add`, `git commit`, or `git push`. Git operations are not workflow phases.

After each `resultn.md` is generated and reviewed, recommend that the user manually commit and push that round's code, prompt, result, and necessary documentation to GitHub before starting the next round. This keeps the research path in version history while leaving repository writes under direct user control.

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
