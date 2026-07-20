# Research Project Coding Copilot

面向 Codex 和 Claude Code 的交互式科研代码项目推进 skill。

它把长期科研项目组织为可检查、可追踪的工作链：

```text
project plan -> promptN -> 执行 -> resultN -> 审查 -> 下一轮
```

## 最短用法

安装 skill 后，在目标科研仓库中打开 Codex。新项目只需输入：

```text
$research-project-coding-copilot 初始化
```

初始化只会创建工作流模板，不会开始科研任务。正式生成 `prompt1` 前，必须先完成并审查 `project_plan.md`。

用户可以直接编辑计划书，也可以把研究想法告诉 AI：

```text
$research-project-coding-copilot 生成项目计划书：我想研究……，已有数据是……，希望最终完成……
```

确认并修改好 `project_plan.md` 后，再输入：

```text
$research-project-coding-copilot 生成下一轮
```

检查生成的 prompt。满意后，在同一个会话中依次输入：

```text
执行当前轮
生成下一轮
```

不需要反复补充“不要执行”或“不要生成下一轮”。这些阶段边界是 skill 的内置规则。

## 短指令

| 指令 | 行为 |
| --- | --- |
| `初始化` | 为新项目安装模板，然后停下等待填写计划书 |
| `接管项目` | 识别已有项目的计划书、规则、历史轮次和文档，并安装工作流状态 |
| `生成项目计划书：...` | 根据用户提供的研究想法生成或完善 `project_plan.md` |
| `整理项目计划书：...` | 结合已有仓库内容和用户补充理解整理 `project_plan.md` |
| `项目体检` | 只读检查项目结构、轮次、Git、敏感文件和运行环境 |
| `状态` | 显示当前轮次、阶段和下一步 |
| `生成下一轮` | 生成下一个 `promptN`，等待审查 |
| `修改当前 prompt：...` | 按反馈修改当前 prompt，不执行 |
| `执行当前轮` | 执行当前 prompt，测试并生成同轮 `resultN` |
| `修改当前 result：...` | 根据反馈补充工作并更新当前 result |
| `继续 N 轮` | 连续生成并执行 N 轮，完成后停止 |

新会话建议在第一条指令前写一次 `$research-project-coding-copilot`。skill 被调用后，当前会话可以直接使用表中的短指令。

## 默认边界

每条普通指令只推进一个阶段：

```text
生成下一轮 -> 等待 prompt 审查
执行当前轮 -> 等待 result 审查
生成下一轮 -> 开始下一轮
```

`继续 N 轮` 是唯一的多轮模式。它最多执行指定轮数，并在测试失败、科研判断不明确、数据泄漏风险、敏感文件风险、破坏性操作或外部凭据缺失时提前停止。

任何模式都不会自行无限循环。skill 不执行 `git add`、`git commit` 或 `git push`。

## 推荐的 GitHub 记录习惯

每轮 prompt 执行完成、`resultN` 生成并审查通过后，建议用户自行将本轮代码、prompt、result 和必要文档提交并推送到 GitHub 一次，再开始下一轮。这样可以把每轮科研问题、代码变化、验证结果和结论保存在同一条版本历史中。

Git 操作完全由用户自行完成。skill 只会在状态或结果中提醒这项建议，不生成提交环节，也不运行任何 Git 写命令。

## 让 AI 帮你安装

下载或克隆本项目后，可以在本项目目录中打开 Codex，直接输入：

```text
把当前项目安装成全局 Codex skill
```

AI 会读取本项目的安装脚本，将 skill 安装到当前用户的 Codex skills 目录，并验证安装结果。这里的“全局”表示当前用户的所有项目都可以使用，不是写入 Codex 保留的 `.system` 内置 skill 目录。

安装完成后，重新打开一个 Codex 会话，即可在任意科研项目中直接指名使用：

```text
$research-project-coding-copilot 初始化
$research-project-coding-copilot 接管项目
$research-project-coding-copilot 状态
```

使用 Claude Code 时也可以在本项目目录中输入：

```text
把当前项目安装成全局 Claude Code skill
```

AI 应运行对应的同步脚本并报告实际安装位置。下面保留手动安装方法，方便需要自行控制安装目录或排查问题时使用。

## 安装到 Codex

克隆本仓库后运行：

```bash
python scripts/sync_to_codex_skills.py
```

默认安装到：

```text
C:\Users\<YOU>\.codex\skills\research-project-coding-copilot
```

验证安装：

```bash
python C:\Users\<YOU>\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\<YOU>\.codex\skills\research-project-coding-copilot
```

## 安装到 Claude Code

运行：

```bash
python scripts/sync_to_claude_skills.py
```

默认安装到：

```text
C:\Users\<YOU>\.claude\skills\research-project-coding-copilot
```

也可以安装到单个项目：

```bash
python scripts/sync_to_claude_skills.py --target .claude/skills/research-project-coding-copilot
```

Claude Code 中可使用同样的短指令，例如：

```text
使用 research-project-coding-copilot：接管项目
```

## 新项目与已有项目

新项目：

```text
$research-project-coding-copilot 初始化
```

它会安装：

```text
AGENTS.md
PROJECT_RULES.md
project_plan.md
ans_qes/
.research_agent/
scripts/research_flow.py
tests/
docs/
```

初始化后，用户必须准备 `project_plan.md`。它是 skill 判断项目目标、当前阶段、实验路线、验收标准和下一轮任务的主要依据。可以选择：

1. 用户自己编辑 `project_plan.md`；
2. 把研究问题、已有数据、拟采用方法、预期结果和论文目标告诉 AI，让 AI 生成初稿；
3. 用户审查并修正 AI 生成的计划书，再开始 `prompt1`。

让 AI 生成新项目计划书：

```text
$research-project-coding-copilot 生成项目计划书：研究问题是……；目前有……数据；计划使用……方法；希望产出……
```

计划书仍有模板占位内容或信息明显不足时，skill 默认不会生成正式 prompt。

已有项目：

```text
$research-project-coding-copilot 接管项目
```

接管会自动识别：

- `project_plan.md`、`PROJECT_PLAN.md` 或 `PROJECT_PLAN*.md`；
- 项目规则和上下文规则；
- `doc/` 或 `docs/`；
- runtime environment 文档；
- `prompt12.md` 或 `prompt12_任务短名.md` 命名；
- 当前最大轮次和下一轮编号。

接管不会覆盖已有计划书、项目规则和科研文档。重复接管默认保留已有画像和进度。

如果已有项目没有正式计划书，或者现有计划书已经落后，可以让 AI 结合用户理解和仓库已有内容重新整理：

```text
$research-project-coding-copilot 整理项目计划书：请结合当前代码、README、docs、配置、已有结果和我的补充理解。当前核心目标是……，已经完成……，接下来希望……
```

AI 应先用低上下文方式检查项目结构和关键文档，区分“已经实现”“已有结果”“用户判断”和“未来计划”，再生成或更新 `project_plan.md`。用户审查确认后，才能生成下一轮 prompt。

## 轮次文件

支持带任务短名或不带短名的文件：

```text
ans_qes/prompt12.md
ans_qes/prompt12_任务短名.md
ans_qes/result12.md
ans_qes/result12_任务短名.md
```

下一轮使用现有最大编号加一。历史缺号只报告，不自动回填。

说明类 Markdown 默认使用中文；代码标识、路径、配置键、模型名和标准技术术语可以保留英文。

## 科研工程约束

skill 默认要求：

- 模块化科研代码，不把一次性脚本作为正式 pipeline；
- 配置、数据、模型、评价和可解释性解耦；
- pilot-first，昂贵任务先运行小规模验证；
- 外部 API 结果缓存、成本记录和断点恢复；
- 数据来源、配置、环境、随机种子和代码版本可追踪；
- benchmark 公平并检查数据泄漏；
- 重要结论保留不确定性、负结果和解释边界；
- 长任务有日志和进度反馈；
- 大文件、密钥、模型权重和生成结果不误提交。

## 大项目与低 Token 模式

项目变大后，skill 会：

- 先搜索和生成仓库摘要，再读取必要片段；
- 默认跳过 `outputs/`、大型数据、日志和生成目录的内容枚举；
- 不读取 API key、token、credential、`.pem` 或 `.key` 文件；
- 优先读取 checkpoint 和最近 1 至 3 个相关 result；
- 对表格、manifest 和日志先做程序化摘要；
- 每 10 至 20 个重要轮次建议生成 workflow checkpoint。

低 token 模式不会跳过必要的测试、复现性检查、数据泄漏检查或科学验证。

## 高级 CLI

日常使用不需要手动运行这些命令。它们主要用于调试、自动检查或单独操作状态：

```bash
python scripts/research_copilot.py init --target .
python scripts/research_copilot.py adopt --target .
python scripts/research_copilot.py status --target .
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py check --target .
python scripts/research_copilot.py draft-prompt --target . --title "..."
python scripts/research_copilot.py prompt-check --target . --round N
python scripts/research_copilot.py result-check --target . --round N --mark-executed
python scripts/research_copilot.py preflight --target . --round N
python scripts/research_copilot.py checkpoint --target . --start-round A --end-round B
python scripts/research_copilot.py continue-plan --target . --rounds N
```

Windows 终端传递中文标题乱码时，可把标题写入 UTF-8 单行文件并使用 `--title-file title.txt`。

## 开发与同步

修改本仓库后，重新同步即可更新已安装版本：

```bash
python scripts/sync_to_codex_skills.py
python scripts/sync_to_claude_skills.py
```

同步脚本会跳过 `.git`、`.vscode`、Python 缓存和 `.tmp*` 临时目录。
