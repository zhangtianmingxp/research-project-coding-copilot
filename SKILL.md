---
name: research-project-coding-copilot
description: "Use when the user wants a publication-first, interactive Codex or Claude Code workflow for long-running research coding projects, especially bioinformatics with noisy DNA/RNA-seq, single-cell, ATAC, Hi-C, or proteomics measurements: initialize from a markdown plan, prioritize early models and decision-grade experiments, harvest minimally publishable project families before opening successor versions, calibrate criteria to matched benchmarks and assay uncertainty, avoid engineering and repeated-version rabbit holes, keep only the active decision gate detailed, internally review prompt/result drafts before publication, produce GO/PIVOT/STOP/INCONCLUSIVE decisions, and maintain compact promptn.md/resultn.md files plus one paper_map.md. Human-controlled, not a fully autonomous agent."
metadata:
  short-description: Publication-first research coding workflow
---

# Research Project Coding Copilot

This skill turns a repository into a human-controlled research project workflow for Codex / Claude Code. It provides a reusable action CLI plus an installable repository template.

It is not an autonomous agent and must not call remote LLM APIs, auto-execute newly generated prompts, or auto-generate the next round.

## Core Rule

Every formal round is split into explicit user-controlled phases:

```text
project_plan.md -> ans_qes/promptn.md -> user review -> execute -> ans_qes/resultn.md -> user review -> stop
```

Never advance to the next phase without a clear user instruction.

## Unpublished Draft Quality Gate

Never publish the first draft of a formal prompt or result directly.

1. Compose an unpublished working draft in the current working context. Do not create numbered draft files in `ans_qes/`, update workflow state, or present the draft to the user yet.
2. Perform at least two distinct review passes:
   - **scientific review**: check claim/evidence alignment, assay and label uncertainty, benchmark comparability, leakage or confounding, decision-grade scale, uncertainty, criteria, and interpretation boundaries;
   - **execution/editorial review**: check that the work is sufficient but bounded, runnable from the repository, free of unnecessary engineering, internally consistent, factually grounded in current project evidence, concise, and written in Chinese by default.
3. Revise every material issue found. If a revision changes the scientific comparison, scale, criterion, decision, or claim boundary, repeat both review passes.
4. Continue until no material issue is detected. Normally two or three focused passes are enough; do not spend iterations on cosmetic wording that cannot change execution or interpretation.
5. Only then write the single official `ans_qes/promptn.md` or `ans_qes/resultn.md`, run its structural checker, correct any reported material issue, update workflow state, and show the user the final artifact.
6. If a material ambiguity cannot be resolved from available evidence, do not publish a misleading formal artifact. Stop and report the specific blocker or assumption requiring user confirmation.

Internal drafts and detailed self-review traces are transient working material. Do not preserve them as extra registry/history files or expose private reasoning; report only the polished artifact and any unresolved explicit caveat.

## Mainline-First, Breadth-First Decision Rule

Optimize for time to a scientifically meaningful decision, not completion of the currently open subtask. Engineering quality is enabling infrastructure and must mature only as fast as the evidence requires.

Before drafting the next prompt:

1. Identify the central claim or paper-critical uncertainty advanced by the round.
2. Compare plausible next actions across data, baseline, candidate model, experiment, analysis, and engineering. Choose the action with the highest expected information gain for the paper per unit of time or compute; do not automatically continue the deepest unfinished branch.
3. Once data can support a valid target, split, and metric, prefer the shortest vertical slice that implements a simple baseline, a serious candidate model, and a decision-grade comparison. Do not wait for a general framework, complete pipeline, exhaustive tests, or polished documentation.
4. Give an engineering blocker one focused repair attempt. If it remains unresolved, explicitly choose among bypassing it, simplifying the experiment, changing the implementation, or marking the claim INCONCLUSIVE. Continue drilling into it only when it can invalidate the central evidence and no scientifically valid bypass exists.
5. Never spend two consecutive formal rounds on engineering-only work. Non-blocking defects, edge cases, refactors, interface polish, and optional validation go to a brief deferred note and do not become the next round.
6. Match code maturity to evidence maturity: exploratory routes may use a clear script or notebook; decision-grade routes need reproducible commands and direct validity checks; only GO routes being promoted to paper-grade require broader modularization, tests, interfaces, and documentation.
7. Use CNS or strong field-leading journal review standards as an ambition benchmark when requested: prioritize novelty, scientific importance, rigorous statistics, robustness, generalization, mechanism, and a coherent claim-to-figure story. Do not claim that any workflow guarantees publication.

Honor scale requirements from the user and project plan. If the project states that at least 500 cells, multiple cohorts, a full chromosome set, or another minimum is needed to distinguish effects, treat that as the minimum for scientific inference. Never replace it with a convenient tiny subset.

## Portfolio And Publication-Harvest Gate

This is a project-family resource-allocation Gate, not a per-experiment scientific decision. Run it before drafting or creating any successor version, when the user says `项目组合审计：<roots>`, or when the user says `成果收割审计` for the current family. Do not run a full portfolio scan before routine prompt/result work.

Use a bounded scan of the supplied portfolio roots or the current family and identifiable siblings. State the audited roots and material exclusions; if no portfolio root is available, audit the current family but do not imply that every project on the machine was covered. Deduplicate mirrors, templates, and renamed copies; group repositories that share the same data, outcome, and central question. Read inventories and terminal evidence first: `paper_map.md`, manuscript/submission decisions, checkpoints, terminal `result*.md`, and only the relevant plan sections. Never bulk-load every historical round.

For each family, first define its **minimum publishable unit**: one bounded claim, its decisive evidence, interpretation boundary, traceable target figure/table, unresolved validity gaps, and a realistic venue range. Then assign exactly one management action:

- `WRITE_NOW`: at least one coherent bounded claim already has decision-grade support, traceable key evidence, and a defensible contribution for at least one realistic venue, with no unresolved issue that invalidates the claim. Remaining work changes manuscript completeness or venue ceiling rather than minimum publishability. Freeze new models, exploratory analyses, experiments, and successor versions; finish the manuscript, figures/tables, methods, limitations, reproducibility package, release, and submission. A pre-existing manuscript draft is not required for this classification, and a CNS aspiration must not block a defensible bounded paper.
- `ONE_DECISIVE_EXPERIMENT`: exactly one named, feasible comparison can change the submission decision to `WRITE_NOW` or close/deprioritize the family. It must have a decision-grade scale, explicit outcomes, and no hidden chain of prerequisite experiments. Run only that comparison, preferably in the current repository through Quick Validation Mode for at most 1-3 rounds, then rerun this Gate.
- `HOLD`: the family may retain scientific value, but it has more than one material evidence gap, depends on unavailable data/resources, or has lower expected publication value than the active portfolio. Do not create a prompt or successor version until a named external condition or portfolio priority changes.
- `STOP`: a fatal validity, novelty, identifiability, or feasibility problem prevents a defensible minimum publishable unit under the current data and question, or the same root blocker has survived the allowed audits. Close the family without deleting its evidence.

These four labels are portfolio actions and must not replace or be conflated with round-level `GO/PIVOT/STOP/INCONCLUSIVE`. When evidence is incomplete, do not invent certainty: use `HOLD`, name the missing fact, and state that confidence is limited.

Return one compact read-only table with `项目族 | 最小可发表单元 | 最强证据 | 关键缺口 | Gate | 理由/下一动作`. Do not create a portfolio registry or a new file. Continue to use the single existing `paper_map.md`, updating it only under its normal evidence-change rules.

The portfolio Gate precedes the cross-version audit. `WRITE_NOW`, `HOLD`, and `STOP` block successor plans and prompts. `ONE_DECISIVE_EXPERIMENT` permits only the named experiment; if repository isolation genuinely requires a successor version, the cross-version audit below must independently return `GO`. Prefer executing the experiment in the current repository, and reclassify the family after it finishes.

## Cross-Version Project-Family Stop Rule

A new version name is not new scientific evidence. Treat repositories or plans that repeatedly reuse the same dataset, outcome, and central question as one project family, even when their model, feature representation, subgroup, threshold, or directory name changes.

When the user says `新版本审计`, run the portfolio Gate first. Continue with the following scientific restart audit only when it classifies the current family as `ONE_DECISIVE_EXPERIMENT` and a separate successor repository is genuinely necessary:

1. Use a bounded scan of sibling/current versions, their terminal `result*.md`, project plans, checkpoints, and `paper_map.md`. Read summaries and final decisions first; do not bulk-load every historical round.
2. Extract the **root blocker** behind each STOP or failed claim, not merely the version label or immediate metric.
3. Permit a new version only when it adds information capable of overcoming or testing that blocker, such as new independent biological units or data, improved measurement resolution, an outcome/estimand that genuinely escapes the old limitation, orthogonal/external evidence, or a hypothesis supported independently before inspecting the failed result.
4. Changing only the model family, feature encoding, threshold, seed, metric, subgroup, post-hoc label, or version number is insufficient. A subgroup or alternative outcome is eligible only when independent evidence predicts the difference and the planned comparison can distinguish that explanation from post-hoc rescue.
5. If the same root blocker terminates two versions, default to closing that claim/data family unless new independent evidence directly removes the blocker. After three consecutive version-level STOP decisions in the same dataset/outcome family, require a project-family audit before any restart even when the immediate blockers differ. These are portfolio-governance defaults, not statistical significance thresholds; override them only at the user's explicit direction with the new evidence and rationale documented.
6. The audit must return exactly one of the existing decisions: `GO` means a new version is justified by named new information; `PIVOT` means change the data or scientific question before continuing; `STOP` closes the project family; `INCONCLUSIVE` names one external fact needed to decide. Do not create a new version, plan, or prompt unless the audit returns GO.
7. After STOP, allow at most one focused post-hoc failure audit, only to identify the root blocker and determine whether an independently motivated hypothesis exists. It cannot rescue the closed claim, trigger recursive audits, or justify a narrower version by itself.

Record a decision-grade family conclusion and its root blocker in the existing root/project-family `paper_map.md`; never create a separate version registry.

## Active-Plan Scope Rule

Keep the project plan useful for the next scientific decision rather than pre-writing an entire speculative program.

1. Detail only the current active claim/Gate: decisive comparison, minimum decision-grade scale, criterion, artifacts, and immediate GO/PIVOT/STOP/INCONCLUSIVE branch.
2. Mention downstream or inactive Gates in at most one sentence each. Expand one only after the upstream result unlocks it.
3. Do not fully pre-author distant prompt sequences such as Prompt5-Prompt11. The prompt/result loop, not a static long plan, decides later work from evidence.
4. As a context guideline, prefer at most roughly 300 nonblank lines or 20 KB. This is an advisory scope signal, never a scientific validity cutoff. If an established plan is longer, identify a compact active-plan section and read that plus only the relevant global sections; do not rewrite project-owned history unless asked.

## Bioinformatics Measurement And Criterion Calibration

Assume that common genomics and proteomics assays, including DNA/RNA sequencing, single-cell measurements, ATAC-seq, Hi-C, and mass-spectrometry proteomics, are noisy and pipeline-dependent observations of biology. Do not silently treat an observed count, peak, contact, abundance, annotation, or derived label as error-free biological ground truth.

When defining decision criteria:

1. Name the observed target, its main assay/processing noise, and the claim boundary. By default claim prediction or explanation of the measured assay under the stated pipeline, not recovery of the unobserved true biological state.
2. Do not invent a universal hard cutoff such as a fixed correlation, AUROC, or accuracy. Use a hard threshold only when the user, a defensible domain standard, a power calculation, or a genuinely comparable benchmark supports it.
3. If a matched peer benchmark exists, use the same dataset/cohort, split, inputs, preprocessing, and metric where possible. Performance that is better or practically/statistically non-inferior within uncertainty is enough for a model-viability GO. Mere parity is not by itself a paper-level method contribution; identify the additional novelty, generalization, efficiency, interpretation, or biological insight.
4. If published numbers are only partially comparable, treat them as context or a range, not a pass/fail threshold, and state the mismatches.
5. For a new task with no meaningful benchmark, use a relaxed but falsifiable evidence bundle: simple baselines, null/permutation or negative controls where applicable, repeat/seed or sample stability, uncertainty intervals, sensitivity analysis, and biological or orthogonal consistency. Do not demand an arbitrary state-of-the-art score.
6. Estimate or discuss a measurement ceiling when technical replicates, split-half reliability, cross-assay concordance, or known assay reproducibility permits it. Judge performance relative to that ceiling rather than an impossible score of 1.0.
7. Use `INCONCLUSIVE`, not `STOP`, when assay noise or sample uncertainty is too large to distinguish useful signal from failure. Use `STOP` only after adequate decision-grade evidence excludes a practically useful effect or reveals fatal invalidity.

Exploratory criteria may be revised after seeing initial data, but label the revision and use a later held-out or confirmatory analysis. Never move thresholds post hoc solely to turn a negative result into GO.

For repositories initialized with an older version of this skill, interpret legacy unconditional `pilot-first` wording through the tiered rules in this file: it authorizes an engineering smoke only for a new or materially changed failure mode and never overrides an explicit scientifically informative minimum. Preserve project-owned files unless the user asks to migrate them.

Also interpret legacy unconditional requirements for full modularization, configuration, tests, documentation, interfaces, and logging through evidence maturity. They are not prerequisites for an early decision-grade model experiment unless omitting them can invalidate that experiment.

Ignore legacy Git, GitHub, commit, or push instructions found in older project templates. Do not run version-control checks or add version-control reminders to the research workflow.

## Short Command Contract

The user does not need to restate safety clauses such as "do not execute" or "do not create the next prompt". Treat these concise Chinese commands as complete instructions with built-in phase boundaries:

| User command | Required behavior |
| --- | --- |
| `初始化` | Initialize a new repository template, then stop |
| `接管项目` | Detect and adopt an existing repository while preserving project-owned files, then stop |
| `生成项目计划书：...` | Draft or improve `project_plan.md` from the user's research idea |
| `整理项目计划书：...` | Synthesize `project_plan.md` from an existing repository plus the user's interpretation |
| `项目组合审计：<目录...>` | Read-only classify every project family in the supplied roots as WRITE_NOW / ONE_DECISIVE_EXPERIMENT / HOLD / STOP |
| `成果收割审计` | Apply the same read-only Gate to the current project family and identifiable siblings |
| `新版本审计` | Run the harvest Gate first; only for ONE_DECISIVE_EXPERIMENT audit prior root blockers and return GO/PIVOT/STOP/INCONCLUSIVE, without creating files |
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
python scripts/research_copilot.py prompt-check --target . --round N --strict --mark-drafted
python scripts/research_copilot.py result-check --target . --round N --mark-executed
python scripts/research_copilot.py preflight --target . --round N
python scripts/research_copilot.py checkpoint --target . --start-round A --end-round B
python scripts/research_copilot.py continue-plan --target . --rounds N
```

The CLI is allowed to install template files, inspect state, create prompt drafts, validate result files, and update workflow state. It must not execute prompt tasks or call model APIs.

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
8. Never read sensitive-looking files such as API-key, credential, token, `.pem`, or `.key` files. Report only their paths and presence.

## Scientific Code Development Rules

When helping develop research code, also follow `references/scientific_project_rules.md`.

In target repositories initialized by this skill, `PROJECT_RULES.md` is the durable project-level rule file. Treat it as mandatory, but read it with low-context discipline:

- use `rg -n "section|topic|keyword" PROJECT_RULES.md` before opening it;
- read only the relevant section unless the task requires a broader audit;
- preserve project rigor even when keeping context small.

Use proportionate engineering. Before a claim receives GO, prefer a disposable but traceable research prototype over premature platform engineering. Harden only the code path that survives scientific selection or is required to make the current decision valid.

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
3. Replace template placeholders with concrete content covering background, scientific questions, goals, data, task definition, methods, evidence-matched implementation, validation standards, the earliest feasible model comparison, first-stage objectives, and risks. Do not design a comprehensive engineering platform before the first scientific decision.
4. Write explanatory Markdown in Chinese by default, then run `plan-check` and stop for user review.

For an existing repository when the user says `整理项目计划书：...`:

1. Run `context-summary`, then inspect bounded relevant excerpts from README files, docs, configs, source structure, checkpoints, and recent results.
2. If this is a proposed successor version, first apply the portfolio Gate. For `WRITE_NOW`, switch to manuscript/submission work; for `HOLD` or `STOP`, do not create the plan; for `ONE_DECISIVE_EXPERIMENT`, name the sole allowed comparison and then apply the cross-version stop rule if a separate repository is genuinely necessary.
3. Combine repository evidence with the user's interpretation and intended direction.
4. Clearly distinguish implemented work, validated results, user-supplied understanding, assumptions, and future plans. Do not infer unsupported scientific conclusions from filenames alone.
5. Detail only the current active Gate and its immediate conditional branches. Keep later Gates compact and locked until evidence activates them.
6. If a proposed successor version is not `ONE_DECISIVE_EXPERIMENT` at the portfolio Gate or does not receive a project-family GO at the cross-version audit, do not create or reframe its plan. Report the applicable management action or scientific decision and its reason instead.
7. Create or update the detected project plan without overwriting unrelated project-owned documentation, run `plan-check`, and stop for user review. Do not generate `prompt1` or the next prompt in the same action unless the user explicitly requested both.

## When Generating `promptn.md`

Use this when the user asks to generate a prompt, next prompt, `prompt1.md`, `prompt2.md`, or a task prompt from `project_plan.md`.

1. Run the minimum navigation checks:

```bash
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py next-id --target .
```

Run `check` only when numbering or workflow state appears inconsistent. Run `preflight` only when the planned work is expensive, uses external services, handles sensitive inputs, or starts a long data/model run. Do not turn routine prompt generation into an engineering audit.

If `plan-check` reports missing content, template placeholders, or an obviously underspecified plan, stop and direct the user to write the plan or use `生成项目计划书：...` / `整理项目计划书：...`. Do not draft a formal prompt unless the user explicitly chooses the exceptional `--allow-incomplete-plan` override.

2. Read `.research_agent/AGENTS.md`, relevant sections of `PROJECT_RULES.md`, the active Gate and only necessary global sections of `project_plan.md`, `.research_agent/project_state.md`, and recent relevant `ans_qes/result*.md` files only as needed.
3. Reassess the paper-level candidate actions instead of inheriting the previous result's suggested next step uncritically. Prefer a model or decision-grade experiment as soon as the data permit one. If the latest decision is STOP, do not generate another prompt for the same claim or silently start a successor version; apply the cross-version rule first. A user-requested one-time failure audit must remain diagnostic rather than a rescue experiment.
4. Keep the prompt compact. It must contain only these sections: `科学决策`, `最小充分工作`, `实验层级与规模`, `判据`, and `产物`. Do not repeat global project, safety, context, or engineering rules inside each prompt.
5. Define one claim, one decisive comparison, the minimum decision-grade scale, and explicit GO/PIVOT/STOP/INCONCLUSIVE criteria. Tiny smoke data may verify code paths only and cannot support a scientific decision.
6. Build and iteratively review the unpublished prompt draft using the quality gate above. In addition to the shared checks, verify that every requested task contributes directly to the one scientific decision, expected artifacts are explicit, criteria are assay/benchmark-calibrated, and no prerequisite is merely assumed.
7. Only after the draft passes review, write the reviewed text directly to the single official `ans_qes/promptn.md`. Do not publish a raw template scaffold or retain alternate draft files.
8. Validate and register the official prompt with:

```bash
python scripts/research_copilot.py prompt-check --target . --round N --strict --mark-drafted
```

9. Correct every checker finding and rerun the check before presenting the file. Split prompts that contain unrelated scientific decisions, but allow the minimal end-to-end work needed to implement a model and run its decisive comparison in the same round.
10. Stop and wait for user review. Do not execute the prompt.

## When Executing `promptn.md`

Use this when the user says `执行当前轮`, asks to execute the current prompt, or names a specific prompt to execute.

1. Read the specified `ans_qes/promptn.md` and relevant sections of `PROJECT_RULES.md`.
2. Run `preflight --round N` before expensive, external-API, data-processing, or long-running work.
3. Use tiered validation:
   - engineering smoke/dry-run: the smallest data needed to catch interface, parsing, shape, dependency, and runtime failures; make no scientific inference;
   - decision-grade experiment: the minimum scientifically informative scale defined by the plan, user, heterogeneity, split design, expected effect, and uncertainty;
   - paper-grade run: the full planned scale, replicates/seeds, strict splits, uncertainty analysis, robustness checks, and external or orthogonal validation relevant to the claim.
4. Reuse prior smoke evidence when the code path and inputs are materially unchanged. Do not require a new tiny pilot before every formal run.
5. Execute the shortest end-to-end route to the scientific result. Early implementations may stay local and simple; do not generalize them before evidence warrants it. Estimate cost/scale, cache external API outputs, record the runtime environment, and make long jobs resumable when relevant.
6. Run only checks that can detect invalid data, leakage, a broken metric, a failed code path, or an incorrect central result. Record other defects briefly and continue.
7. Build an unpublished result draft containing only: `完成内容`, `关键证据`, `决策`, `Claim 边界`, `产物与命令`, and `下一项最高价值工作`. The decision must be exactly GO, PIVOT, STOP, or INCONCLUSIVE.
8. Iteratively review it using the quality gate above. Also verify that completed work and metrics are supported by actual artifacts, failed or negative results are retained, the decision follows the prompt's criteria without post-hoc threshold movement, peer comparisons are genuinely comparable, and claim boundaries do not turn assay prediction into biological truth.
9. Only after the result draft passes review, write the official `ans_qes/resultn.md`, then validate and mark it:

```bash
python scripts/research_copilot.py result-check --target . --round N --mark-executed
```

10. Correct material checker findings before presenting the result. Then stop and wait for user review. Do not generate `prompt{n+1}.md`.

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
7. The unpublished-draft quality gate applies to every quick-validation prompt and result; internal review iterations do not count as research rounds.

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

Re-rank the paper's candidate next actions after every result. Do not use bounded continuation to spend multiple rounds descending into the same engineering problem.

Apply the unpublished-draft quality gate independently to every prompt and result. Do not preserve internal variants or count editorial review passes toward N.

4. Stop immediately when any of these occurs:
   - requested N rounds are complete;
   - tests/checks fail and the fix is not obvious;
   - the next step is scientifically ambiguous;
   - a large data/model/checkpoint/secret-risk change appears;
   - the task would require external credentials or destructive changes;
   - context needed becomes too broad for low-context mode.
   - another engineering-only or tiny-smoke round would not remove a concrete blocker or advance paper-level evidence.
   - the current claim/version reaches STOP or continuation would require inventing a successor version without a project-family GO.
5. Never continue beyond N rounds without a new user instruction.

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

Do not update it after routine engineering, smoke, documentation, or inconclusive maintenance work. Keep one row per claim with: Claim, decisive experiment, current evidence, status, target figure/table, and missing evidence. For a terminated version family, put the root blocker and the evidence required to reopen it in the same table rather than creating another registry.

## References

For the full protocol, read `references/workflow_protocol.md` when the task involves prompt/result lifecycle details or state updates.

For context-budget behavior in large projects, read `references/context_hygiene.md`.

For scientific research code quality, benchmark discipline, model development, data provenance, and publication-readiness rules, read `references/scientific_project_rules.md`.

The template copied into research repositories lives in `assets/template/`.
