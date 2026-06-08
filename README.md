# Research Project Coding Copilot

一个面向 Codex / Claude Code 的交互式科研代码项目推进 skill。

它适合长期、正式、可发表论文或可支撑严肃科研结论的代码项目。核心目标是把科研项目推进过程变成可追踪的链条：

```text
project_plan.md -> promptn.md -> resultn.md -> 检查/审查 -> commit 建议 -> 下一轮
```

## 它是什么

这是一个 Codex skill，提供：

- 可安装到任意科研仓库的项目模板；
- `project_plan.md` 计划书模板；
- `PROJECT_RULES.md` 科研代码开发规则；
- `promptn.md` / `resultn.md` 两阶段记录机制；
- 低 token 上下文工作规则；
- 状态检查、编号检查、prompt 草稿、result 校验、commit message 建议；
- 用户明确要求时的受限连续推进 N 轮。

## 它不是什么

它不是无限自动 agent。

默认不会：

- 自动执行刚生成的 prompt；
- 自动生成下一轮 prompt；
- 自动 commit；
- 自动 push；
- 调用远程 LLM API；
- 无限循环直到项目“完成”。

如果用户明确要求“继续 N 轮”，它只会进入受限连续推进模式，最多执行 N 轮，并在测试失败、不确定下一步、大文件/密钥风险、数据泄漏风险、需要 push 或上下文过宽时停止。

## 安装为 Codex Skill

把本仓库复制或克隆到 Codex skills 目录：

```text
C:\Users\<YOU>\.codex\skills\research-project-coding-copilot
```

或者在本仓库运行同步脚本：

```bash
python scripts/sync_to_codex_skills.py
```

验证 skill：

```bash
python C:\Users\<YOU>\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\<YOU>\.codex\skills\research-project-coding-copilot
```

在 Windows 如果遇到编码问题，可以先设置：

```powershell
$env:PYTHONUTF8='1'
```

## 初始化科研项目

在目标科研仓库中打开 Codex，然后说：

```text
使用 $research-project-coding-copilot，在当前仓库初始化科研项目推进流程。不要生成 prompt1，不要执行，不要 commit。
```

它会安装模板文件：

```text
AGENTS.md
PROJECT_RULES.md
project_plan.md
ans_qes/
.research_agent/
scripts/research_flow.py
tests/
```

然后填写或替换 `project_plan.md`。

## 基本工作流

生成第一轮 prompt，不执行：

```text
使用 $research-project-coding-copilot，读取 project_plan.md，生成 ans_qes/prompt1.md，不要执行。
```

审查 prompt 后执行：

```text
执行 ans_qes/prompt1.md，完成后生成 ans_qes/result1.md，然后停止。不要生成 prompt2，不要 commit。
```

生成 commit message 建议：

```text
根据 ans_qes/prompt1.md 和 ans_qes/result1.md 生成 commit message 建议，不要提交。
```

继续下一轮：

```text
根据当前 project_plan.md、project_state.md 和 result1.md，生成 ans_qes/prompt2.md，不要执行。
```

## 继续 N 轮

如果当前已经做到 `result5.md`，可以要求继续固定轮数：

```text
使用 $research-project-coding-copilot，从当前进度继续执行 3 轮。每轮生成 prompt/result，不 push，遇到风险就停止。
```

内部会先运行：

```bash
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py continue-plan --target . --rounds 3
```

如果已有 `result5.md`，计划范围会是：

```text
prompt6/result6
prompt7/result7
prompt8/result8
```

完成后停止。

## CLI 命令

skill 级 CLI：

```bash
python scripts/research_copilot.py init --target .
python scripts/research_copilot.py status --target .
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py check --target .
python scripts/research_copilot.py plan-check --target .
python scripts/research_copilot.py next-id --target .
python scripts/research_copilot.py draft-prompt --target . --title "..."
python scripts/research_copilot.py result-check --target . --round N --mark-executed
python scripts/research_copilot.py suggest-commit --target . --round N
python scripts/research_copilot.py continue-plan --target . --rounds N
```

安装到目标仓库后的本地辅助脚本：

```bash
python scripts/research_flow.py status
python scripts/research_flow.py check
python scripts/research_flow.py next-id
python scripts/research_flow.py init-round --round 1 --title "..."
python scripts/research_flow.py suggest-commit --round 1
```

## 低 Token 规则

默认使用低上下文模式：

- 先运行 `context-summary`；
- 先用 `rg` 搜索，再读文件；
- 只读相关片段；
- 不默认整篇读取日志、notebook、manifest、结果表、大型 Markdown、旧 `result*.md`；
- 对结构化文件优先总结行数、列名、缺失值、唯一键和少量样例；
- 必要时再逐步扩大上下文。

低 token 模式不是降低质量。必要的测试、数据泄漏检查、复现性检查和科学验证仍必须执行。

## Markdown 文档语言

新生成的说明类 Markdown 文档默认使用中文。

代码标识、命令、配置键、字段名、路径、模型名、指标名和标准英文技术术语可以保留英文。

## 目录结构

```text
SKILL.md
agents/openai.yaml
scripts/
  research_copilot.py
  install_template.py
  sync_to_codex_skills.py
references/
  workflow_protocol.md
  context_hygiene.md
  scientific_project_rules.md
assets/template/
  AGENTS.md
  PROJECT_RULES.md
  project_plan.md
  ans_qes/
  .research_agent/
  scripts/research_flow.py
```

## 开发与同步

修改本仓库后，同步到本机 Codex skills 目录：

```bash
python scripts/sync_to_codex_skills.py
```

然后新开 Codex / VS Code 窗口测试。
