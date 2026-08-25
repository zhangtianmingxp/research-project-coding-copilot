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
- Optimize time to a scientific decision. Re-rank plausible data, baseline, candidate-model, experiment, analysis, and engineering actions after every result; do not automatically continue the deepest unfinished branch.
- Once a valid target, split, and metric exist, build the shortest vertical slice containing a simple baseline, a serious candidate model, and a decision-grade comparison.
- Treat engineering as enabling work. Before a route earns GO, use a traceable prototype and add only checks needed for valid data, leakage control, correct metrics, and a trustworthy central result.
- Before starting a round, state which central claim, decisive uncertainty, figure/table, or named blocker it advances.
- Give an engineering blocker one focused repair attempt. If it remains unresolved, bypass it, simplify the experiment, change implementation, or mark the claim INCONCLUSIVE. Do not spend two consecutive formal rounds on engineering unless the blocker can invalidate central evidence and has no valid bypass.
- Let code maturity follow evidence maturity: exploratory scripts/notebooks first, reproducible decision-grade commands next, and broader modularization/tests/docs only for surviving paper-grade paths.
- When aiming at CNS or strong field-leading journals, prioritize conceptual novelty, broad significance, rigorous controls, generalization, mechanistic depth, uncertainty, and a coherent story. Do not confuse codebase sophistication with scientific impact.

Triage issues before opening follow-up work:

- **claim blocker**: can change data validity, leakage, metrics, statistical inference, central figures, or reproducibility of a key result; fix before relying on the result;
- **material but non-blocking**: useful for robustness, maintenance, or reviewer response but does not invalidate the current conclusion; record and schedule against paper priorities;
- **incidental**: cosmetic, speculative, rare, or unable to affect the central evidence; note it briefly and continue without repeated experiments.

## Portfolio And Publication Harvest

- Before opening a successor version, classify every deduplicated project family in the defined portfolio scope as WRITE_NOW, ONE_DECISIVE_EXPERIMENT, HOLD, or STOP.
- Define a minimum publishable unit before classification: one bounded claim, decisive evidence, interpretation boundary, traceable target figure/table, unresolved validity gaps, and a realistic venue range.
- WRITE_NOW requires decision-grade evidence, a defensible contribution for at least one realistic venue, and no unresolved validity blocker. Freeze new experiments and finish the submission; an aspirational venue must not delay a valid bounded paper.
- ONE_DECISIVE_EXPERIMENT means exactly one named decision-grade comparison can change the submission decision. It must not conceal a prerequisite chain; prefer running it in the current repository, then reclassify.
- HOLD means multiple material gaps, unavailable resources, or lower portfolio priority; name the condition for reconsideration. STOP means the current data/question cannot support a defensible minimum publishable unit.
- These labels govern resource allocation and do not replace experiment-level GO/PIVOT/STOP/INCONCLUSIVE. Use HOLD with an explicit evidence caveat when the portfolio record is incomplete.
- Return one compact read-only table and keep `paper_map.md` as the only evidence registry.

## Cross-Version Portfolio Discipline

- Treat versions that reuse the same dataset, outcome, and central question as one project family. A version label is not independent evidence.
- Only after the harvest Gate returns ONE_DECISIVE_EXPERIMENT, summarize prior terminal decisions and root blockers from bounded final-result, checkpoint, plan, and `paper_map.md` evidence before proposing a separate successor repository.
- Require new identifying information before restart: independent data/biological units, improved measurement resolution, a genuinely different estimand, orthogonal/external evidence, or an independently supported hypothesis established before inspecting the failed result.
- Model, representation, threshold, seed, metric, subgroup, post-hoc label, or version changes alone do not justify another project. Do not launder a failed claim through narrower post-hoc framing.
- Two STOPs caused by the same root blocker default to closure of that claim/data family. Three consecutive version-level STOPs in the same data/outcome family require a project-family GO/PIVOT/STOP/INCONCLUSIVE audit before any restart. Treat these as portfolio controls, not statistical thresholds; an override requires explicit user direction and documented new evidence.
- Permit at most one post-STOP failure audit to identify the root blocker. It cannot rescue the closed claim or trigger recursive post-hoc versions.
- Use the existing `paper_map.md` to record family blockers and evidence required for reopening. Do not create another registry.
- Keep the plan centered on the current active Gate. Future locked Gates receive one-line placeholders and are expanded only after upstream evidence unlocks them; a roughly 300-nonblank-line/20-KB scope warning is advisory only.

## Engineering Principles

- A clear one-script or notebook vertical slice is acceptable for initial scientific selection.
- Move stable, repeated, or paper-grade logic into modular source code after the route earns continued investment.
- Keep data loading, feature construction, modeling, training, evaluation, interpretation, and visualization decoupled in promoted core workflows.
- Avoid hard-coded paths.
- Separate configuration from code.
- Use clear module, function, and class names.
- Use logs, controllable random seeds, traceable outputs, and useful error messages.
- Add direct validity checks during exploration; broaden tests only for reused or paper-critical behavior.
- Avoid speculative abstractions, exhaustive edge-case handling, and broad test expansion that do not protect a current or near-term paper-critical workflow.

## Data And Benchmark Discipline

- Treat raw data as read-only.
- Write cleaned, transformed, or normalized data to separate intermediate or processed locations.
- Track data provenance: raw source, script, config, timestamp, filters, normalization, genome/annotation version when relevant.
- Avoid data leakage.
- For prediction tasks, prefer strict generalization splits over random-only splits when scientifically relevant.
- Benchmarks must use comparable splits, inputs, preprocessing, metrics, and evaluation settings.
- Mark external data, pretrained weights, or extra information clearly.

## Bioinformatics Measurement Uncertainty And Success Criteria

- Treat DNA/RNA sequencing, single-cell, ATAC-seq, Hi-C, and proteomics outputs as noisy, pipeline-dependent observations affected by depth, sparsity/dropout, batch, mapping/quantification, peak/contact calling, missingness, and dynamic range. Select only the checks relevant to the assay.
- Name whether the target is a raw observation, processed quantity, or derived label. Unless orthogonal evidence supports more, claim prediction/explanation of that measurement rather than recovery of an error-free biological state.
- Do not impose universal absolute metric cutoffs. Use a hard cutoff only when supported by the user, a domain standard, power analysis, or a genuinely comparable benchmark.
- A peer benchmark is decision-grade only when dataset/cohort, split, inputs, preprocessing, and metric are sufficiently matched. Better performance or practical/statistical non-inferiority within uncertainty supports model viability. Parity alone still needs novelty, generalization, efficiency, interpretation, mechanism, or biological discovery for a paper-level contribution.
- Treat partially comparable literature numbers as contextual ranges, not pass/fail criteria.
- For a genuinely new task, use simple baselines, null/permutation or negative controls where applicable, repeat/seed or sample stability, uncertainty intervals, sensitivity analyses, and biological/orthogonal consistency. Do not invent a state-of-the-art threshold when none exists.
- Use technical replicates, split-half reliability, cross-assay concordance, or known reproducibility to estimate/discuss a measurement ceiling when possible.
- Choose INCONCLUSIVE when noise or uncertainty prevents distinguishing useful signal from failure. Choose STOP only when adequate evidence excludes a practically useful effect or reveals fatal invalidity.
- Exploratory thresholds may change with documented reasons, but later held-out or confirmatory analysis must test the revised criterion. Never move a threshold post hoc merely to obtain GO.

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

- Every figure, table, and reported number should be traceable to data, code, config, output file, and a recorded code/version note when relevant.
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

## Change Compatibility

- Before changing shared interfaces, update documentation and call sites.
- Do not break existing results without explaining whether code/data/model versions, configs, or downstream docs need updates.

## Development Priority

Prioritize by the paper's critical path rather than a fixed engineering maturity ladder:

1. define the central question, candidate claims, decisive comparisons, and evidence thresholds;
2. perform only enough data work to define a valid target, split, metric, and comparison;
3. design a simple baseline and serious candidate model, then run them at the earliest scientifically informative scale;
4. decide GO, PIVOT, STOP, or INCONCLUSIVE immediately from the predeclared criteria;
5. strengthen GO claims with strict splits, uncertainty, ablation, controls, replication, external validation, and mechanism analysis;
6. harden, document, and package only the workflows needed for the surviving claim-to-figure story.

Do not postpone scientifically informative runs until the repository reaches an imagined state of complete engineering polish.

## Low-Token Work Mode

Use low-token mode by default:

- Search with `rg` before reading.
- Read bounded excerpts, not whole large files.
- Summarize large structured data programmatically.
- Inspect logs by targeted markers such as `ERROR`, `WARNING`, and `Traceback`.
- Inspect only targeted changed files or bounded diffs relevant to the task.
- Reuse existing summaries, results, runbooks, and checkpoints.
- Do not repeatedly reload large IDE selections, logs, notebooks, manifests, or generated outputs.
- Expand context only when necessary, and state why.

Low-token mode is not permission to skip required tests, leakage checks, reproducibility checks, or scientific validation.
