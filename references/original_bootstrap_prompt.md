# Prompt: 实现 Codex 交互式科研项目推进模板

## 一、项目目标
请实现一个适合 Codex / Claude Code 交互式使用的科研项目推进模板。

本项目不是全自动 Agent，不需要自动调用 OpenAI API、Anthropic API 或 Codex API。

本项目的目标是：
- 让用户提供 `project_plan.md` 科研项目计划书。
- Codex 在交互窗口中按照规范逐轮推进项目：
  - 生成 promptn.md
  - 等待用户确认
  - 执行本轮任务
  - 生成 resultn.md
  - 等待用户审查
  - 提交 Git commit
  - 停止，等待用户手动触发下一轮

核心特点：
1. 保留 Codex 交互式开发体验
2. 用户可随时暂停、修改意见、继续执行
3. 每轮任务必须有 promptn.md 和 resultn.md
4. 每轮结束后必须停止，不自动进入下一轮
5. 更新项目状态文件，方便恢复上下文
6. 支持规范化 Git commit
7. 支持科研代码项目长期演进

---

## 二、设计约束

### 1. 不要实现全自动循环 Agent
禁止自动生成下一轮 prompt、自动执行下一轮代码、自动 commit 或 push。每轮完成后必须等待用户指令。

### 2. 不要直接调用模型 API
第一版不要使用任何远程 LLM API。Codex / Claude Code 本身会在交互窗口操作本仓库，本项目只提供规范、模板、状态管理和辅助脚本。

### 3. 用户始终拥有控制权
- 生成 promptn.md 后，停止，等待用户确认
- 执行 promptn.md 后，生成 resultn.md，停止，等待用户审查
- commit 前提示 commit message 建议，等待用户确认
- commit 后停止，不生成下一轮 prompt

---

## 三、工作流示例

1. 用户在 Codex 交互窗口输入：  
   `请读取 .research_agent/AGENTS.md 和 project_plan.md，根据规则生成 prompt1.md，不要执行。`  
   Codex 生成 `ans_qes/prompt1.md` 并更新 `.research_agent/project_state.md`，停止。

2. 用户可修改 prompt1.md，Codex 根据反馈修改，不执行。

3. 用户确认执行：  
   Codex 执行 prompt1.md，生成 result1.md，更新状态，停止。

4. 用户审查 result1.md，可要求修改，Codex 不进入下一轮。

5. 用户确认 commit：Codex 执行 git commit，更新状态，停止。

6. 用户手动触发下一轮：  
   `生成 prompt2.md`，Codex 才生成下一轮 prompt。

---

## 四、项目结构
.
├── project_plan.md
├── README.md
├── AGENTS.md
├── ans_qes/
│ └── README.md
├── .research_agent/
│ ├── AGENTS.md
│ ├── config.yaml
│ ├── project_state.md
│ ├── progress.json
│ ├── templates/
│ │ ├── prompt_template.md
│ │ ├── result_template.md
│ │ └── commit_template.md
│ └── logs/
├── scripts/
│ ├── research_flow.py
│ └── README.md
└── tests/
└── README.md

---

## 五、核心文件要求

- 根目录 `AGENTS.md`：Codex 项目总规则，禁止自动循环
- `.research_agent/AGENTS.md`：详细 workflow 规则
- `project_plan.md`：科研项目计划书模板
- `.research_agent/project_state.md`：记录当前轮次、状态和 open issues
- `.research_agent/progress.json`：机器可读状态
- `.research_agent/config.yaml`：配置文件
- `ans_qes/`：存放 promptn.md / resultn.md 链
- `.research_agent/templates/`：
  - prompt_template.md
  - result_template.md
  - commit_template.md

---

## 六、辅助脚本

`scripts/research_flow.py`，功能：

1. `status`：显示当前轮次、last_prompt、last_result、last_commit、open_issues
2. `next-id`：扫描 ans_qes/ 找下一个 prompt 编号
3. `check`：检查文件结构、prompt/result 配对、编号跳号
4. `init-round --round N --title "..."`：生成某轮 prompt 草稿，停止
5. `suggest-commit --round N`：生成 commit message 建议

要求：
- 不调用任何模型 API
- 不自动删除文件
- 不自动 commit
- 不自动生成下一轮 prompt

---

## 七、验收标准

1. 项目结构完整
2. AGENTS.md 存在且禁止自动循环
3. `.research_agent/config.yaml` 中 auto_next: false
4. `.research_agent/progress.json` 中 auto_next: false
5. project_plan.md 模板存在
6. ans_qes/README.md 存在
7. prompt/result/commit 模板存在
8. scripts/research_flow.py 可运行
9. 命令可执行：status、check、next-id、init-round、suggest-commit
10. prompt1.md 生成后不执行
11. 不生成 prompt2.md
12. 不 commit
13. 不 push
14. 生成 result1.md，包含：
    - 本轮完成内容
    - 创建/修改文件
    - 命令记录
    - 检查结果
    - 是否满足验收标准
    - commit 建议

---

## 八、本轮执行要求

请执行本 prompt，完成项目骨架和辅助脚本，并生成：

- `ans_qes/result1.md`（记录本轮执行内容和检查）

执行完成后停止，不要生成 prompt2.md，不 commit，不 push。