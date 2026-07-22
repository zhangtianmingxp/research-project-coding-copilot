# Interactive Research Workflow Rules

本文件定义 Codex / Claude Code 在科研项目中逐轮推进工作的规则。

## 1. 项目定位

这是一个交互式科研项目推进模板，不是全自动 agent。

AI 的职责是：

- 阅读 `project_plan.md`、`PROJECT_RULES.md` 相关章节和项目规则。
- 在用户要求时生成 `ans_qes/promptn.md`。
- 在用户输入“执行当前轮”或指定某个 prompt 后执行该轮。
- 执行后生成 `ans_qes/resultn.md`。
- 每个阶段完成后停止，等待用户下一条明确指令。

AI 不得：

- 自动生成下一轮 prompt。
- 自动执行刚生成的 prompt。
- 执行 `git add`、`git commit` 或 `git push`。
- 调用远程 LLM API。
- 在用户未确认时覆盖已有 `resultn.md`。

例外：如果用户明确要求“继续 N 轮”或“从当前 result 继续执行 N 轮”，允许进入受限连续推进模式。该模式最多执行用户指定的 N 轮，不能无限循环，遇到测试失败、不确定下一步、大文件/密钥风险、数据泄漏风险或需要破坏性操作时必须停止。

### 1.1 短指令协议

用户不需要在每次操作后重复说明“不要执行”或“不要生成下一轮”。以下短指令具有固定边界：

| 指令 | 固定行为 |
| --- | --- |
| `初始化` | 只安装项目模板，然后停止 |
| `接管项目` | 识别并接管已有项目，保留项目自有文件，然后停止 |
| `生成项目计划书：...` | 根据用户研究想法生成或完善 `project_plan.md`，然后等待审查 |
| `整理项目计划书：...` | 结合已有仓库内容和用户理解整理计划书，然后等待审查 |
| `项目体检` | 只读检查项目状态和风险 |
| `状态` | 报告当前轮次、阶段和下一步 |
| `生成下一轮` / `下一轮` | 只生成下一轮 prompt，然后停止 |
| `执行当前轮` | 执行当前 prompt，验证并生成同轮 result，然后停止 |
| `继续 N 轮` | 最多连续生成并执行 N 轮，然后停止 |

短指令本身就是对应动作的用户授权，不得要求用户重复确认同一个动作。只有目标不明确、缺少必要信息或触发工具权限边界时才询问。

## 2. 每轮状态机

每轮只能处于以下状态之一：

```text
idle
prompt_drafted
prompt_approved
executed
result_reviewed
```

允许的转换：

```text
idle -> prompt_drafted
prompt_drafted -> prompt_drafted
prompt_drafted -> prompt_approved
prompt_approved -> executed
executed -> executed
executed -> result_reviewed
result_reviewed -> prompt_drafted
```

禁止自动执行 `result_reviewed -> prompt_drafted`。必须由用户明确要求生成下一轮 prompt。

如果用户明确要求受限连续推进 N 轮，可以在同一轮用户指令下重复执行：

```text
prompt_drafted -> prompt_approved -> executed
```

但总轮数不得超过 N，且每轮必须保留 `promptn.md` 和 `resultn.md`。

## 2.1 项目计划书前置规则

`project_plan.md` 是正式轮次的必要输入。初始化只安装模板，不代表研究计划已经完成。

新项目可以由用户自行填写，也可以由 AI 根据用户提供的研究问题、已有数据、预期方法、限制条件和最终论文或软件目标生成初稿。

已有项目可以结合仓库中的 README、docs、配置、源码结构、checkpoint 和最近结果，以及用户对项目现状和未来方向的理解，整理或更新计划书。必须区分：

- 已经实现的内容；
- 已验证的结果；
- 用户提供的理解或判断；
- AI 明确标注的假设；
- 尚未执行的未来计划。

不得仅根据文件名推断科学结论。计划书仍含模板占位内容或信息明显不足时，不得生成正式 `promptn.md`；应先请用户完善，或协助生成计划书并等待审查。

## 3. 生成 promptn.md 的规则

触发条件：用户输入“生成下一轮”“下一轮”或明确指定某轮 prompt。

操作要求：

1. 读取 `project_plan.md` 的相关章节。
2. 用 `rg` 定位并读取 `PROJECT_RULES.md` 中与本轮任务相关的章节。
3. 读取 `.research_agent/project_state.md` 和 `.research_agent/progress.json`。
4. 检查 `ans_qes/` 中已有 prompt/result 编号。
5. 明确本轮推进的论文核心 claim、关键不确定性、目标 figure/table 或具体 blocker。
6. 将实验标记为工程 smoke、科研决策级或论文级，并写明数据规模、独立样本单位、规模依据和升级/停止标准。
7. 检查最近相关轮次。若连续两轮主要是工程补强或小规模 smoke，下一轮原则上必须进入足够规模的科研分析；只有明确 blocker 才可继续工程工作。
8. 生成指定或下一个编号的 `ans_qes/promptn.md`。
9. 更新状态为 `prompt_drafted`。
10. 停止并等待用户审查。

生成 prompt 时不得修改科研代码，不得生成 `resultn.md`。

## 4. 执行 promptn.md 的规则

触发条件：用户输入“执行当前轮”或明确指定某个 prompt。

操作要求：

1. 读取对应 `ans_qes/promptn.md`。
2. 读取 `PROJECT_RULES.md` 中与本轮任务相关的章节。
3. 按 prompt 执行本轮任务。
4. 运行与风险相称的必要检查或测试，不为与论文主线无关的问题反复扩展验证。
5. 生成或更新同编号 `ans_qes/resultn.md`，并记录是否满足相关项目规则。
6. 更新状态为 `executed`。
7. 停止并等待用户审查。

如果 `resultn.md` 已存在，除非用户明确要求覆盖或更新，否则不得直接覆盖。

## 5. GitHub 历史记录建议

skill 不执行 `git add`、`git commit` 或 `git push`，Git 操作也不是本工作流的阶段。

每轮 `resultn.md` 生成并经用户审查后，应提醒用户自行将本轮代码、prompt、result 和必要文档提交并推送到 GitHub，再开始下一轮。该建议用于保存科研工作线路，但是否以及如何执行完全由用户决定。

## 5.1 受限连续推进 N 轮

触发条件：用户明确要求继续固定轮数，例如“从 result5.md 继续执行 3 轮”。

操作要求：

1. 先运行 context summary 和编号检查。
2. 从下一个可用编号开始。
3. 每轮都必须生成 `promptn.md`、执行、生成 `resultn.md`、运行检查并更新状态。
4. 完成 N 轮后必须停止。
5. 遇到以下情况必须提前停止：
   - 测试或检查失败且不能局部修复；
   - 下一步科研或工程判断不确定；
   - 出现大文件、模型权重、密钥、数据泄漏或 benchmark 不公平风险；
   - 需要外部凭据或破坏性操作；
   - 需要读取过宽上下文才能继续。
6. 不执行任何 Git 写操作；完成后提醒用户自行同步 GitHub。

## 6. 科研项目质量原则

- 必须遵守 `PROJECT_RULES.md`。
- 论文核心问题和证据链优先于工程完整度；工程工作必须服务于可信结果或解除明确 blocker。
- 微型规模只能在适用时验证代码路径。若用户或计划书规定至少 500 cells 才能分辨效应，必须以 500 cells 作为科研推断下限。
- 已通过的 smoke 不重复做；不得用低功效结果排序模型、否定假设、冻结科学结论或改变论文方向。
- 遇到问题先判断它是否会改变数据、指标、统计推断、核心图表或关键结果复现。不会影响主线的偶发/外观问题只记录，不为其反复实验或单独占用 round。
- 不把研究项目当 demo。
- 避免一次性脚本成为核心流程。
- 数据处理、特征、模型、评估、解释和可视化应保持模块边界。
- 避免数据泄漏，尤其是 benchmark、split 和外部验证。
- 长任务应有日志或进度输出。
- 结果应可追踪到代码、配置、命令、数据版本和 Git commit。
- 文档默认中文，代码标识、文件路径、指标名和模型名保留英文。

## 7. 上下文预算规则

默认使用低上下文模式。项目变大后，AI 不得把计划书、日志、结果表、notebook、manifest、旧 result 文件和长 diff 一股脑读进上下文。

推荐顺序：

1. 先运行仓库摘要命令，例如 skill 级 `context-summary` 或本地 `scripts/research_flow.py status` / `check`。
2. 使用 `rg -n` 定位相关标题、函数、配置键、错误信息或文件路径。
3. 只读取与当前任务相关的最小片段。
4. 不默认读取完整日志；失败时优先看 stderr，再搜索日志中的 `ERROR`、`WARNING`、`Traceback` 或阶段名。
5. 不默认读取完整 TSV/CSV/JSON/manifest/notebook/result table；应先总结文件大小、行列数、列名、缺失值、唯一键和少量目标行。
6. 不重复读取大量旧 `ans_qes/result*.md`；优先读取最近 1-3 个相关 result，或使用摘要。
7. 如果必须扩大读取范围，先说明原因，再逐步扩大。

低上下文模式不是降低质量；必要的测试、数据泄漏检查、复现性检查和科学验证仍必须执行。
