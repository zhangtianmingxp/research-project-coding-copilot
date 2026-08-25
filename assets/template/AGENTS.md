# Agent Instructions

This repository is an interactive research project progression template for Codex / Claude Code.

All coding agents and AI assistants must read and follow `.research_agent/AGENTS.md` and relevant sections of `PROJECT_RULES.md` before generating prompts, executing tasks, or writing results.

Core rules:

- This project is not a fully autonomous agent.
- Do not call OpenAI, Anthropic, Codex, Claude, or other remote LLM APIs.
- Do not automatically generate the next prompt after completing a round.
- Do not automatically execute a generated prompt.
- Keep every formal round traceable through `ans_qes/promptn.md` and `ans_qes/resultn.md`.
- Keep prompts/results compact; global rules live in these instruction files rather than being repeated every round.
- Never publish the first prompt/result draft. Review an unpublished working draft for scientific validity and execution/editorial quality, revise material issues, then write only the polished official file. Do not retain draft variants or detailed review traces.
- After generating a prompt, stop and wait for user review.
- After executing a prompt and writing a result, stop and wait for user review.

Scientific project principles:

- Treat downstream repositories as formal research projects, not demos.
- Put the paper's central question, claim-to-evidence chain, and scientifically informative scale ahead of optional engineering completeness.
- Optimize for early model design, decision-grade experiments, and explicit GO/PIVOT/STOP/INCONCLUSIVE decisions.
- Re-rank candidate next actions after every result; do not keep descending into the same unfinished engineering branch by default.
- Before any successor version, classify the portfolio's deduplicated project families as WRITE_NOW, ONE_DECISIVE_EXPERIMENT, HOLD, or STOP. WRITE_NOW freezes experiments for submission; only ONE_DECISIVE_EXPERIMENT permits one named comparison, preferably in the current repository. Do not create another registry.
- Treat repeated versions using the same data, outcome, and question as one project family. Audit prior terminal decisions and root blockers before a restart; a renamed model, threshold, subgroup, or version is not new evidence.
- Keep only the current decision Gate detailed in the project plan. Leave inactive downstream Gates as one-line branches until evidence unlocks them.
- Let code maturity follow evidence maturity. A traceable exploratory script or notebook is acceptable before a route earns GO; harden surviving paper-critical paths later.
- Preserve strict benchmark discipline and avoid data leakage.
- Treat genomics and proteomics targets as noisy, pipeline-dependent measurements rather than error-free biological truth. Calibrate criteria to assay reliability and uncertainty.
- For matched peer benchmarks, peer-level practical/statistical non-inferiority is enough for model viability, while paper novelty must come from an additional contribution. For genuinely new tasks, use baselines, null/negative controls, stability, uncertainty, and biological or orthogonal consistency instead of arbitrary absolute cutoffs.
- Keep results traceable to data, code-version notes, configs, environment, and commands.
- Favor scientific rigor and publication-quality evidence over quick completion.
- Use low-context mode by default: run context summaries, search before reading, inspect bounded excerpts, and avoid loading logs, generated outputs, large manifests, notebooks, or many old result files unless necessary.

Project-level research code rules:

- `PROJECT_RULES.md` is mandatory.
- Read it with low-context discipline: use `rg` to find relevant sections, then inspect bounded excerpts.
- Before a decision, require only the checks needed for data validity, leakage control, benchmark fairness, correct metrics, and trustworthy central results. Defer optional architecture, broad tests, documentation polish, and edge-case work.
- Newly generated explanatory Markdown documents should default to Chinese unless the user, publication target, or collaborator context requires English.
- Separate engineering smoke tests from decision-grade and paper-grade experiments. Smoke tests only verify code paths and must not support scientific claims.
- Honor the minimum scientifically informative scale in `project_plan.md` or stated by the user. Reuse passed smoke checks and promote promptly instead of repeating tiny pilots.
- Keep engineering and validation proportionate to risks that can affect correctness, reproducibility, data integrity, or the paper's central conclusions.
- Cache expensive or external responses and record scale, runtime, environment, and recovery details.
- Use root `paper_map.md` as the only paper evidence table and update it only for decision-grade results, claim changes, paper-grade promotion, or manuscript writing.
- Record project-family STOP blockers and the independent evidence required to reopen them in that same `paper_map.md`; do not create a version registry.
- For long projects, maintain checkpoint summaries, recommended reading order, and claim-to-evidence links instead of repeatedly loading full history.
- Never read credential, API-key, token, `.pem`, or `.key` file contents; only report their presence.
