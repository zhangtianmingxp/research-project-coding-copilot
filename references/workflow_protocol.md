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
- `context-summary --target PATH`: print a bounded repository summary, file counts, large files, top directories, project plan headings, and recent round files without loading large contents.
- `check --target PATH`: check required template files, prompt/result numbering, and safety flags.
- `plan-check --target PATH`: warn when `project_plan.md` still looks like an unfilled template.
- `next-id --target PATH`: print the next prompt/result round number.
- `draft-prompt --target PATH --title TITLE`: legacy manual scaffold for debugging. It does not satisfy the unpublished-draft quality gate and is not used by the normal skill workflow.
- `prompt-check --target PATH --round N`: warn when a prompt is oversized, contains too many independent tasks, or lacks expected task concepts. Add `--strict --mark-drafted` to register an already reviewed official prompt only when no warnings remain.
- `result-check --target PATH --round N --mark-executed`: validate `resultn.md` sections and update state to `executed`.
- `preflight --target PATH --round N`: check plan/rules, round pairing, sensitive-looking paths, and runtime documentation.
- `checkpoint --target PATH --start-round A --end-round B`: create a compact workflow-checkpoint scaffold for long project history.
- `continue-plan --target PATH --rounds N`: check numbering and record a bounded continuation request for the next N rounds.

The CLI is deliberately bounded. It does not execute prompt tasks, call model APIs, or generate the next round automatically.

Round filenames may include task titles, such as `prompt12_任务短名.md`. The next round is the maximum existing round plus one; historical gaps are warnings, not slots to refill.

## Short User Commands

The user can control the workflow with concise commands. Guardrails are implicit and do not need to be repeated in every request:

- `初始化`: initialize only, then stop.
- `接管项目`: adopt an existing project while preserving its files, then stop.
- `生成项目计划书：...`: draft or improve a project plan from the user's research idea.
- `整理项目计划书：...`: synthesize a project plan from an existing repository and the user's interpretation.
- `项目组合审计：<目录...>`: classify every deduplicated project family in the supplied roots as WRITE_NOW, ONE_DECISIVE_EXPERIMENT, HOLD, or STOP; remain read-only.
- `成果收割审计`: apply the same read-only Gate to the current family and identifiable sibling versions.
- `新版本审计`: run the harvest Gate first; only for ONE_DECISIVE_EXPERIMENT audit terminal decisions and root blockers, without creating a version, plan, or prompt.
- `项目体检`: run read-only readiness checks.
- `状态`: report current state and next action.
- `快速验证：...`: draft the first compact prompt for one claim and one decisive comparison; use at most 1-3 rounds.
- `继续快速验证`: after an INCONCLUSIVE result, draft the next focused prompt if fewer than 3 rounds have been used.
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

Preserve existing rules, plans, and any existing `paper_map.md`. Install only missing workflow-control files plus the single lightweight `paper_map.md`.

## Project Plan Prerequisite

A reviewed project plan is required before formal prompt rounds. Initialization only creates the template.

For a new project, the user may write `project_plan.md` directly or ask the skill to generate it from their research question, available data, intended methods, constraints, and desired publication or software outcome.

For an existing project, combine bounded evidence from code, README files, docs, configs, checkpoints, and recent results with the user's understanding. Clearly separate implemented work, validated results, user-provided interpretation, assumptions, and future plans.

Run `plan-check` before prompt generation. If placeholders or material omissions remain, stop for plan review rather than generating a formal prompt. The CLI permits an explicit `--allow-incomplete-plan` override only for exceptional user-directed cases.

Keep only the current active Gate detailed: claim, decisive comparison, minimum decision-grade scale, criterion, artifacts, and immediate decision branches. Inactive future Gates stay one sentence each until an upstream GO unlocks them. Roughly 300 nonblank lines or 20 KB is an advisory context boundary, not a validity check; for an established longer plan, identify and read a compact active section plus necessary global context.

## Portfolio And Publication-Harvest Gate

Before any successor version, define the portfolio scope and deduplicate mirrors, templates, renamed copies, and repositories that share the same data, outcome, and central question. Use bounded terminal evidence rather than loading full histories. For each family, define one minimum publishable unit and classify exactly one action:

- `WRITE_NOW`: a bounded claim has decision-grade, traceable support, a defensible contribution for at least one realistic venue, and no unresolved validity blocker. Freeze experiments and successor versions; complete manuscript, figures/tables, methods, limitations, reproducibility materials, release, and submission.
- `ONE_DECISIVE_EXPERIMENT`: one named, feasible, decision-grade comparison can change the publication decision. Run only it, preferably in the current repository and within 1-3 quick-validation rounds, then reclassify.
- `HOLD`: multiple material gaps, unavailable dependencies, or lower current portfolio value make further work a poor resource allocation. Name the reactivation condition.
- `STOP`: fatal validity, novelty, identifiability, or feasibility prevents a defensible minimum publishable unit under the current data/question.

These are resource-allocation labels, distinct from experiment-level GO/PIVOT/STOP/INCONCLUSIVE. If evidence is too incomplete for another classification, use HOLD with limited confidence and name the missing fact. Return one compact chat table; do not create another registry. Existing `paper_map.md` remains the only evidence table.

WRITE_NOW, HOLD, and STOP block successor planning. ONE_DECISIVE_EXPERIMENT permits only the named comparison; a separate successor repository additionally requires a GO from the project-family audit below.

## Project-Family Audit And Version Restarts

Treat multiple versions that reuse the same dataset, outcome, and central question as one project family. After the portfolio Gate returns ONE_DECISIVE_EXPERIMENT, inspect bounded terminal summaries from prior versions and extract their root blockers before any separate successor plan is drafted.

A successor version requires named new identifying information: independent data or biological units, better measurement resolution, a genuinely different estimand that escapes the old limitation, orthogonal/external evidence, or an independently motivated hypothesis that predates inspection of the failed result. A changed model, feature representation, threshold, seed, metric, subgroup, post-hoc label, or version number alone is insufficient.

If the same root blocker closes two versions, default to family STOP unless independent evidence removes it. Three consecutive version-level STOP decisions in the same dataset/outcome family trigger a mandatory audit regardless of blocker labels. The audit returns only GO, PIVOT, STOP, or INCONCLUSIVE; only GO permits a new version. These counts are governance defaults rather than statistical thresholds and require an explicit, documented user override.

After STOP, allow at most one focused post-hoc failure audit to identify the root blocker and test whether an independently supported hypothesis can be formed. It cannot rescue the closed claim or lead to recursive post-hoc versions. Record the blocker and reopening evidence in the existing `paper_map.md`, not a new registry.

## Bounded Continuation

When the user explicitly asks to continue N rounds from the current progress, Codex may run a bounded continuation loop. This is not the default mode and must never be infinite.

Required setup:

```bash
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py continue-plan --target . --rounds N
```

For each round:

1. Re-rank paper-critical candidate actions by expected information gain per unit effort; do not automatically continue the deepest unfinished branch.
2. Generate `ans_qes/promptn.md`.
3. Execute only that prompt.
4. Generate `ans_qes/resultn.md`.
5. Run only checks that protect the current scientific decision.
6. Run `result-check --round n --mark-executed`.
7. Continue only if the next step is clear and within the user's requested N rounds.

Stop conditions:

- N rounds completed.
- test/check failure without an obvious local fix.
- unclear scientific or engineering next step.
- risk of data leakage, benchmark unfairness, secret exposure, large files, or destructive change.
- context needs become too broad.


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

Generate a prompt only when the user asks. Keep `promptn.md` to exactly these sections:

- `科学决策`
- `最小充分工作`
- `实验层级与规模`
- `判据`
- `产物`

Do not repeat global project, safety, context, or engineering rules inside each prompt.

Before choosing the task, compare plausible next actions across data, baseline, candidate model, experiment, analysis, and engineering. Once a valid target, split, and metric exist, default to the shortest vertical slice that produces a baseline-versus-candidate decision-grade result. An unfinished engineering subtask does not receive automatic priority. Read the current active Gate rather than importing every inactive future branch. If the latest decision is STOP, do not create another prompt for the same claim or silently start a new version without a project-family GO.

For bioinformatics tasks, identify the measured target and relevant assay/processing uncertainty before setting criteria. Use matched peer performance as a relative comparator when protocols are genuinely comparable. For new tasks without a benchmark, use an evidence bundle of simple baselines, null/negative controls, stability, uncertainty, and biological/orthogonal consistency rather than an arbitrary absolute score.

First create an unpublished working draft in model context. Review it at least once for scientific validity and once for execution/editorial quality. Revise material issues and repeat affected checks. Do not create numbered draft variants or expose detailed private review traces.

Only after no material issue is detected, write the reviewed text to the single official prompt and run `prompt-check --strict --mark-drafted`. Correct all checker findings before presenting it, then stop. Split unrelated scientific decisions, but keep the minimal model implementation and its decisive experiment together when separating them would only create engineering-only rounds.

## Prompt Execution

Execute only when the user explicitly says to execute a specific prompt. Keep `resultn.md` to exactly these sections:

- `完成内容`
- `关键证据`
- `决策`
- `Claim 边界`
- `产物与命令`
- `下一项最高价值工作`

The decision must be exactly GO, PIVOT, STOP, or INCONCLUSIVE.

Do not convert assay noise into a false STOP. If uncertainty still spans both useful and null effects, the decision is INCONCLUSIVE. Peer-level non-inferiority can establish route viability, but result text must not call parity a method advance without another supported contribution.

Use code maturity appropriate to the evidence stage. A traceable script or notebook is sufficient for early selection; only routes that earn GO or become paper-critical need broader interfaces, tests, modularization, and documentation. Give a blocking engineering failure one focused repair attempt, then bypass, simplify, change implementation, or declare the relevant evidence INCONCLUSIVE unless no valid alternative exists.

Before writing the official result, create an unpublished draft and review it for scientific evidence, factual support, artifact/command existence, retained negative results, criterion-to-decision consistency, benchmark comparability, and claim boundaries. Revise and repeat affected checks. Only then write the single official result, run strict `result-check --mark-executed`, correct material findings, update state, and stop.

Legacy results remain readable, but newly generated results use the compact structure above.

## Quick Validation

Quick validation uses one claim, one decisive comparison, one minimum decision-grade scale, and at most 1-3 rounds. GO, PIVOT, or STOP ends it. INCONCLUSIVE may continue only to resolve one named missing evidence item, and round 3 always ends the quick validation.

Do not create a quick-validation registry. Use only root `paper_map.md` for paper evidence, and update it only for a decision-grade result, claim change, paper-grade promotion, or manuscript writing.

## Long-Running And External Work

Before expensive data processing, model inference, or external API calls:

1. Classify the run as engineering smoke, decision-grade, or paper-grade.
2. Run a small smoke/dry-run only when the code path, input contract, environment, or failure mode is new or materially changed.
3. Treat smoke output as engineering evidence only. Do not use it to rank methods, infer an effect, reject a hypothesis, or change the paper direction.
4. Set decision-grade scale from the project plan, user/domain minimum, heterogeneity, split design, expected effect, and uncertainty. Never shrink an explicit minimum merely for convenience.
5. Reuse prior smoke QC and promote promptly to the scientifically informative or formal scale.
6. Estimate input scale, runtime, API requests, and storage; record environment and dependency versions.
7. Cache external responses, make work resumable, and keep credentials outside model context.

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
