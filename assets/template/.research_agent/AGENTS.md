# Interactive Research Workflow Rules

本文件定义 Codex / Claude Code 在科研项目中逐轮推进工作的规则。

## 1. 项目定位

这是一个交互式科研项目推进模板，不是全自动 agent。

AI 的职责是：

- 阅读 `project_plan.md` 和项目规则。
- 在用户要求时生成 `ans_qes/promptn.md`。
- 在用户确认后执行某个 prompt。
- 执行后生成 `ans_qes/resultn.md`。
- 在用户确认后建议或执行 Git commit。
- 每个阶段完成后停止，等待用户下一条明确指令。

AI 不得：

- 自动生成下一轮 prompt。
- 自动执行刚生成的 prompt。
- 自动 commit。
- 自动 push。
- 调用远程 LLM API。
- 在用户未确认时覆盖已有 `resultn.md`。

## 2. 每轮状态机

每轮只能处于以下状态之一：

```text
idle
prompt_drafted
prompt_approved
executed
result_reviewed
commit_suggested
committed
```

允许的转换：

```text
idle -> prompt_drafted
prompt_drafted -> prompt_drafted
prompt_drafted -> prompt_approved
prompt_approved -> executed
executed -> executed
executed -> result_reviewed
result_reviewed -> commit_suggested
commit_suggested -> committed
committed -> idle
```

禁止自动执行 `committed -> prompt_drafted`。必须由用户明确要求生成下一轮 prompt。

## 3. 生成 promptn.md 的规则

触发条件：用户明确要求生成某轮 prompt，例如“生成 prompt1.md”“为下一步生成 prompt，不要执行”。

操作要求：

1. 读取 `project_plan.md`。
2. 读取 `.research_agent/project_state.md` 和 `.research_agent/progress.json`。
3. 检查 `ans_qes/` 中已有 prompt/result 编号。
4. 生成指定或下一个编号的 `ans_qes/promptn.md`。
5. 更新状态为 `prompt_drafted`。
6. 停止并等待用户审查。

生成 prompt 时不得修改科研代码，不得生成 `resultn.md`。

## 4. 执行 promptn.md 的规则

触发条件：用户明确要求执行某个 prompt，例如“执行 prompt1.md”。

操作要求：

1. 读取对应 `ans_qes/promptn.md`。
2. 按 prompt 执行本轮任务。
3. 运行必要检查或测试。
4. 生成或更新同编号 `ans_qes/resultn.md`。
5. 更新状态为 `executed`。
6. 停止并等待用户审查。

如果 `resultn.md` 已存在，除非用户明确要求覆盖或更新，否则不得直接覆盖。

## 5. 生成 commit message 的规则

触发条件：用户明确要求生成 commit message 或提交。

操作要求：

1. 检查 `git status`。
2. 读取本轮 `promptn.md` 和 `resultn.md`。
3. 建议格式为 `pN: 简短中文或英文摘要`。
4. 等待用户确认后才执行 `git commit`。
5. commit 后停止，不得 push，除非用户明确要求。

## 6. 科研项目质量原则

- 不把研究项目当 demo。
- 避免一次性脚本成为核心流程。
- 数据处理、特征、模型、评估、解释和可视化应保持模块边界。
- 避免数据泄漏，尤其是 benchmark、split 和外部验证。
- 长任务应有日志或进度输出。
- 结果应可追踪到代码、配置、命令、数据版本和 Git commit。
- 文档默认中文，代码标识、文件路径、指标名和模型名保留英文。

## 7. 上下文节约规则

- 搜索后再读取大文件。
- 只读取和当前任务相关的最小片段。
- 不默认读取完整日志。
- 成功命令用 exit code、输出路径和摘要说明即可。
- 失败时优先看 stderr，再搜索日志中的 `ERROR`、`WARNING`、`Traceback`。
