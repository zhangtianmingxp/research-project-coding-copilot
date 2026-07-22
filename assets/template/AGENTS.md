# Agent Instructions

This repository is an interactive research project progression template for Codex / Claude Code.

All coding agents and AI assistants must read and follow `.research_agent/AGENTS.md` and relevant sections of `PROJECT_RULES.md` before generating prompts, executing tasks, or writing results.

Core rules:

- This project is not a fully autonomous agent.
- Do not call OpenAI, Anthropic, Codex, Claude, or other remote LLM APIs.
- Do not automatically generate the next prompt after completing a round.
- Do not automatically execute a generated prompt.
- Do not run `git add`, `git commit`, or `git push`; Git writes remain the user's responsibility.
- Keep every formal round traceable through `ans_qes/promptn.md` and `ans_qes/resultn.md`.
- After generating a prompt, stop and wait for user review.
- After executing a prompt and writing a result, stop and wait for user review.

Scientific project principles:

- Treat downstream repositories as formal research projects, not demos.
- Put the paper's central question, claim-to-evidence chain, and scientifically informative scale ahead of optional engineering completeness.
- Prefer reproducible, modular, maintainable code.
- Keep data processing, feature construction, modeling, evaluation, interpretation, and visualization decoupled.
- Avoid hard-coded paths and one-off scripts.
- Preserve strict benchmark discipline and avoid data leakage.
- Keep results traceable to data, code, configs, environment, commands, and repository versions.
- After each reviewed result, recommend that the user manually commit and push the round to GitHub to preserve the research history.
- Favor scientific rigor and publication-quality evidence over quick completion.
- Use low-context mode by default: run context summaries, search before reading, inspect bounded excerpts, and avoid loading logs, generated outputs, large manifests, notebooks, or many old result files unless necessary.

Project-level research code rules:

- `PROJECT_RULES.md` is mandatory.
- Read it with low-context discipline: use `rg` to find relevant sections, then inspect bounded excerpts.
- Do not bypass reproducibility, leakage checks, benchmark fairness, interpretability, documentation, or logging requirements merely to finish a round quickly.
- Newly generated explanatory Markdown documents should default to Chinese unless the user, publication target, or collaborator context requires English.
- Separate engineering smoke tests from decision-grade and paper-grade experiments. Smoke tests only verify code paths and must not support scientific claims.
- Honor the minimum scientifically informative scale in `project_plan.md` or stated by the user. Reuse passed smoke checks and promote promptly instead of repeating tiny pilots.
- Keep engineering and validation proportionate to risks that can affect correctness, reproducibility, data integrity, or the paper's central conclusions.
- Cache expensive or external responses and record scale, runtime, environment, and recovery details.
- For long projects, maintain checkpoint summaries, recommended reading order, and claim-to-evidence links instead of repeatedly loading full history.
- Never read credential, API-key, token, `.pem`, or `.key` file contents; only report their presence and Git tracking risk.
