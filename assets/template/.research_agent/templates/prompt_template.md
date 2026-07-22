# Prompt {round}

## 任务标题

{title}

## 任务背景

请读取并遵守：

- `AGENTS.md`
- `.research_agent/AGENTS.md`
- `PROJECT_RULES.md`
- `project_plan.md`
- `.research_agent/project_state.md`

本轮任务是根据项目计划书和当前进度设计下一步工作。

## 任务目标

1. 明确本轮需要完成的科研或工程目标。
2. 保持任务范围可执行、可检查、可记录。
3. 避免自动进入下一轮。

## 论文主线贡献

- 本轮推进的核心科学问题、candidate claim、目标 figure/table 或具体 blocker：待填写。
- 本轮完成后将如何改变论文证据状态：待填写。

## 实验层级与规模依据

- 层级：工程 smoke / 科研决策级 / 论文级 / 不适用。
- 数据规模与独立实验单位：待填写。
- 规模依据：引用 `project_plan.md`、用户要求、power/variance、异质性、split 或已有结果说明为什么足够。
- 解释边界：smoke 只验证代码路径，不得用于模型排名、效应判断或科学结论。
- 升级或停止标准：待填写。

## 具体要求

- 不调用远程模型 API。
- 不自动生成下一轮 prompt。
- 本轮不执行 `git add`、`git commit` 或 `git push`；GitHub 同步由用户自行完成。
- 所有新增代码、实验、文档应服务于项目计划书。
- 必须遵守 `PROJECT_RULES.md` 中与本轮任务相关的科研工程、数据、benchmark、模型、统计、文档、日志和低 token 规则。
- 新增说明类 Markdown 文档默认使用中文；代码标识、命令、配置键、字段名、路径、模型名和指标名保留英文。
- 如涉及数据、模型或 benchmark，必须注意可复现性和数据泄漏风险。
- 仅当代码路径、输入契约、环境或失败模式是新的或发生实质变化时才新增 smoke / dry-run；已有 smoke 可复用时应直接推进到科研决策级或论文级规模。
- 用户或计划书给出的最低科研规模不可自行缩小。小规模结果只能标记为工程验证，不能替代有统计辨别力的实验。
- 不读取 API key、credential、token、`.pem` 或 `.key` 文件内容。

## 预期输出

- 本轮需要创建或修改的文件。
- 本轮需要运行的检查、测试或命令。
- 执行后必须生成 `ans_qes/result{round}_{title_slug}.md`。

## 暂不执行

本文件只是任务提示词。生成后必须停止，等待用户确认后才能执行。
