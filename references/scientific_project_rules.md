# Scientific Research Code Rules

Use these rules whenever this skill helps develop research code, especially bioinformatics, AI, machine learning, statistical modeling, benchmark, or publication-oriented projects.

## Project Positioning

Treat the target repository as a formal, long-term, publishable research project, not a demo or temporary script collection.

All code, experiments, documentation, and results should support:

- reproducibility
- extensibility
- interpretability
- comparability
- reviewability
- long-term maintenance
- publication-quality evidence

## Publication-First Prioritization

- Optimize for the central scientific question, claim-to-evidence chain, and paper narrative rather than maximum engineering completeness.
- Treat engineering as enabling work. Add architecture, tests, schemas, contracts, and documentation when they protect correctness, reproducibility, data integrity, or a paper-critical analysis.
- Prefer a scientifically informative experiment over optional refactoring or another convenience-scale rerun once the relevant code path works.
- Before starting a round, state which central claim, decisive uncertainty, figure/table, or named blocker it advances.
- If two consecutive rounds are mainly engineering or smoke validation, the next round should normally produce decision-grade scientific evidence. Continue engineering only when a concrete blocker is documented.
- When aiming at CNS or strong field-leading journals, prioritize conceptual novelty, broad significance, rigorous controls, generalization, mechanistic depth, uncertainty, and a coherent story. Do not confuse codebase sophistication with scientific impact.

Triage issues before opening follow-up work:

- **claim blocker**: can change data validity, leakage, metrics, statistical inference, central figures, or reproducibility of a key result; fix before relying on the result;
- **material but non-blocking**: useful for robustness, maintenance, or reviewer response but does not invalidate the current conclusion; record and schedule against paper priorities;
- **incidental**: cosmetic, speculative, rare, or unable to affect the central evidence; note it briefly and continue without repeated experiments.

## Engineering Principles

- Do not turn core workflows into one-off scripts.
- Keep stable logic in modular source code, not notebooks.
- Keep data loading, feature construction, modeling, training, evaluation, interpretation, and visualization decoupled.
- Avoid hard-coded paths.
- Separate configuration from code.
- Use clear module, function, and class names.
- Use logs, controllable random seeds, traceable outputs, and useful error messages.
- Add tests or validation checks for core behavior.
- Avoid speculative abstractions, exhaustive edge-case handling, and broad test expansion that do not protect a current or near-term paper-critical workflow.

## Data And Benchmark Discipline

- Treat raw data as read-only.
- Write cleaned, transformed, or normalized data to separate intermediate or processed locations.
- Track data provenance: raw source, script, config, timestamp, filters, normalization, genome/annotation version when relevant.
- Avoid data leakage.
- For prediction tasks, prefer strict generalization splits over random-only splits when scientifically relevant.
- Benchmarks must use comparable splits, inputs, preprocessing, metrics, and evaluation settings.
- Mark external data, pretrained weights, or extra information clearly.

## Validation Tiers, Scale, Runtime, And External Services

Classify every data/model experiment before execution:

1. **Engineering smoke/dry-run**: use the smallest useful input to detect parsing, interface, shape, dependency, logging, and runtime failures. It provides no evidence about effect size, model ranking, biological significance, robustness, or whether a research direction works.
2. **Decision-grade experiment**: use the minimum scientifically informative scale needed to compare methods or estimate an effect with the required heterogeneity, split structure, replication, and uncertainty. Derive this scale from the project plan, user/domain knowledge, prior variance, or power analysis, not convenience.
3. **Paper-grade run**: use the planned full dataset and reviewer-relevant seeds/replicates, strict splits, uncertainty estimates, robustness checks, and external or orthogonal validation.

- Honor an explicit minimum scale from the user or project plan. For example, if 500 cells are required to distinguish effects, 20 cells may be a smoke test but cannot be a decision-grade substitute.
- Run a new smoke test only for a new or materially changed failure mode. Reuse prior smoke evidence when the code path and input contract are unchanged.
- Promote promptly after smoke QC passes. Do not accumulate a series of tiny pilots, contract-polishing rounds, or exploratory model comparisons on underpowered data.
- A small pilot may justify fixing the pipeline; it may not justify selecting the best model, rejecting a hypothesis, freezing a biological conclusion, or redirecting the paper.
- Treat unconditional `pilot-first` language in older repository templates as legacy wording governed by these tiers, not as a requirement to repeat tiny experiments.
- Estimate runtime, input scale, storage, API requests, and likely cost before a decision-grade or paper-grade run.
- Cache external API/model responses with request parameters, model/version identifiers, and timestamps.
- Make long-running jobs resumable and emit stage-level progress.
- Maintain a concise runtime environment document with the preferred environment and verified critical packages.
- Never expose or load API keys, credentials, tokens, private keys, or secret files into model context.

## Model Development

- Start with strong baselines before complex models.
- Use unified model interfaces when possible, such as `fit`, `predict`, `evaluate`, `save`, and `load`.
- Support ablation when claims involve multiple modalities or feature families.
- Include interpretability methods where model outputs support scientific claims.
- Do not optimize a leaderboard at the expense of biological or scientific explanation.

## Statistics And Scientific Interpretation

- Avoid reporting only global averages.
- Use stratified analysis when relevant: cell type, condition, time point, gene class, expression level, cohort, tissue, or other domain groups.
- Report uncertainty where possible: confidence intervals, standard errors, bootstrap estimates, effect sizes, statistical significance, and biological significance.
- Preserve negative results. They are often central to honest research conclusions.

## Results And Paper Readiness

- Every figure, table, and reported number should be traceable to data, code, config, output file, and repository revision.
- Plotting scripts and result-generation scripts should be reproducible.
- Important design decisions should be written into docs, not left only in chat history.
- README files should help new contributors understand project goals, data, environment setup, minimal pipeline, reproduction, and extension.
- Mature projects should maintain a current research summary, recommended reading order, workflow checkpoints, figure/table inventory, and claim-to-evidence map.
- Lock central claims only when their supporting metrics, robustness checks, figures, and interpretation boundaries are traceable.
- Label every reported result as smoke-only, decision-grade, or paper-grade. State the sample size, independent experimental units, split/replicate design, and what claims the scale does and does not support.

## Markdown Documentation Language

Default to Chinese for newly generated explanatory Markdown documents, especially README-style notes, method descriptions, runbooks, project summaries, prompt/result records, design documents, and troubleshooting guides.

Keep code identifiers, commands, config keys, field names, file paths, model names, metric names, package names, and standard English technical terms in their original form when translation would reduce clarity.

Use English only when the user explicitly requests it, when a target journal/collaborator requires English, or when preserving an English source quote/specification is necessary.

## Code Quality

- Prefer Python 3.11+, type hints, `pathlib`, structured configs, standard logging, pytest, and formatting/static checks when appropriate.
- Keep functions small and focused.
- Do not mix data cleaning, model training, evaluation, and plotting in a single function.
- Error messages should explain what was expected and how to fix missing prerequisites.
- Long-running commands must show progress or logging and should support `--log-level`.

## Version Control

The skill does not perform Git writes. After each reviewed round, recommend that the user manually commit and push the round to GitHub to preserve the research history.

- Do not commit large raw data, processed matrices, model checkpoints, large figures, caches, or generated logs unless the project explicitly allows it.
- Commits should have clear single-topic intent.
- Before changing shared interfaces, update documentation and call sites.
- Do not break existing results without explaining whether versions, configs, or downstream docs need updates.

## Development Priority

Prioritize by the paper's critical path rather than a fixed engineering maturity ladder:

1. define the central question, candidate claims, decisive comparisons, and evidence thresholds;
2. remove only the data or pipeline blockers needed for those comparisons;
3. run decision-grade baselines and analyses at a scientifically informative scale;
4. strengthen promising claims with strict splits, uncertainty, ablation, controls, replication, and external validation;
5. add advanced models only when they test a scientific hypothesis or plausibly improve a paper-critical result;
6. build mechanism/case-study analyses and the claim-to-figure story;
7. harden, document, and package the workflows needed to reproduce the final evidence.

Do not postpone scientifically informative runs until the repository reaches an imagined state of complete engineering polish.

## Low-Token Work Mode

Use low-token mode by default:

- Search with `rg` before reading.
- Read bounded excerpts, not whole large files.
- Summarize large structured data programmatically.
- Inspect logs by targeted markers such as `ERROR`, `WARNING`, and `Traceback`.
- Inspect diffs incrementally: `git status --short`, `git diff --stat`, then targeted diffs.
- Reuse existing summaries, results, runbooks, and checkpoints.
- Do not repeatedly reload large IDE selections, logs, notebooks, manifests, or generated outputs.
- Expand context only when necessary, and state why.

Low-token mode is not permission to skip required tests, leakage checks, reproducibility checks, or scientific validation.
