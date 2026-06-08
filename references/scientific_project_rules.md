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

## Engineering Principles

- Do not turn core workflows into one-off scripts.
- Keep stable logic in modular source code, not notebooks.
- Keep data loading, feature construction, modeling, training, evaluation, interpretation, and visualization decoupled.
- Avoid hard-coded paths.
- Separate configuration from code.
- Use clear module, function, and class names.
- Use logs, controllable random seeds, traceable outputs, and useful error messages.
- Add tests or validation checks for core behavior.

## Data And Benchmark Discipline

- Treat raw data as read-only.
- Write cleaned, transformed, or normalized data to separate intermediate or processed locations.
- Track data provenance: raw source, script, config, timestamp, filters, normalization, genome/annotation version when relevant.
- Avoid data leakage.
- For prediction tasks, prefer strict generalization splits over random-only splits when scientifically relevant.
- Benchmarks must use comparable splits, inputs, preprocessing, metrics, and evaluation settings.
- Mark external data, pretrained weights, or extra information clearly.

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

- Every figure, table, and reported number should be traceable to data, code, config, output file, and commit.
- Plotting scripts and result-generation scripts should be reproducible.
- Important design decisions should be written into docs, not left only in chat history.
- README files should help new contributors understand project goals, data, environment setup, minimal pipeline, reproduction, and extension.

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

- Do not commit large raw data, processed matrices, model checkpoints, large figures, caches, or generated logs unless the project explicitly allows it.
- Commits should have clear single-topic intent.
- Before changing shared interfaces, update documentation and call sites.
- Do not break existing results without explaining whether versions, configs, or downstream docs need updates.

## Development Priority

Prefer this order unless the user specifies otherwise:

1. data format standardization
2. reproducible pipelines
3. statistical baselines
4. strong machine learning baselines
5. strict benchmark and split discipline
6. interpretability
7. advanced deep learning or graph models
8. foundation model transfer
9. biological or scientific case studies
10. paper-ready figures and documentation

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
