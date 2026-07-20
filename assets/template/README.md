# Research Project

本仓库使用 Research Project Coding Copilot 管理科研代码开发轮次。

## 开始

1. 填写或替换 `project_plan.md`。
2. 在 Codex 中调用 `$research-project-coding-copilot`。
3. 使用下面的短指令推进项目。

```text
生成下一轮
执行当前轮
提交当前轮
生成下一轮
```

不需要重复说明“不要执行”“不要生成下一轮”“不要 commit”或“不要 push”。skill 已经为每条指令规定了停止位置。

## 常用指令

| 指令 | 行为 |
| --- | --- |
| `状态` | 检查当前轮次和下一步 |
| `生成下一轮` | 生成下一轮 prompt，然后等待审查 |
| `执行当前轮` | 执行当前 prompt，验证并生成对应 result |
| `提交当前轮` | commit 当前轮，不 push |
| `继续 N 轮` | 连续生成并执行 N 轮，默认不 commit、不 push |
| `继续 N 轮并逐轮提交` | 连续执行并逐轮 commit，不 push |
| `推送` | push 已提交内容 |

详细科研工程规则见 `PROJECT_RULES.md`，工作流状态见 `.research_agent/project_state.md`，每轮记录保存在 `ans_qes/`。
