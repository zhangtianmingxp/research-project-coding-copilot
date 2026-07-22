# Research Project

本仓库使用 Research Project Coding Copilot 管理科研代码开发轮次。

## 开始

1. 填写或替换 `project_plan.md`。
2. 在 Codex 中调用 `$research-project-coding-copilot`。
3. 使用下面的短指令推进项目。

`project_plan.md` 是正式轮次的必要输入。用户可以自己填写，也可以把研究想法告诉 AI：

```text
$research-project-coding-copilot 生成项目计划书：研究问题是……；已有数据是……；希望最终完成……
```

已有工作项目可以使用：

```text
$research-project-coding-copilot 整理项目计划书：结合当前仓库内容和我的补充理解，已经完成……，接下来希望……
```

用户审查并修正计划书后，才能生成正式的下一轮 prompt。

```text
生成下一轮
执行当前轮
生成下一轮
```

不需要重复说明“不要执行”或“不要生成下一轮”。skill 已经为每条指令规定了停止位置。

## 常用指令

| 指令 | 行为 |
| --- | --- |
| `状态` | 检查当前轮次和下一步 |
| `生成项目计划书：...` | 根据研究想法生成或完善计划书 |
| `整理项目计划书：...` | 结合已有仓库和用户理解整理计划书 |
| `快速验证：...` | 用一个决定性比较快速判断一个 claim，最多 1-3 轮 |
| `继续快速验证` | 上一轮为 INCONCLUSIVE 时继续一轮，最多到第 3 轮 |
| `生成下一轮` | 生成下一轮 prompt，然后等待审查 |
| `执行当前轮` | 执行当前 prompt，验证并生成对应 result |
| `继续 N 轮` | 连续生成并执行 N 轮，然后停止 |

## GitHub 记录建议

每轮 result 生成并审查通过后，建议用户自行把本轮代码、prompt、result 和必要文档提交并推送到 GitHub 一次，再开始下一轮。skill 不执行 `git add`、`git commit` 或 `git push`。

详细科研工程规则见 `PROJECT_RULES.md`，工作流状态见 `.research_agent/project_state.md`，每轮记录保存在 `ans_qes/`。论文 claim 的轻量证据状态只记录在 `paper_map.md`。
