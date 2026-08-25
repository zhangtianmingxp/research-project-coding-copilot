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
| `项目组合审计：<目录...>` | 把指定目录内的项目族分为 WRITE_NOW / ONE_DECISIVE_EXPERIMENT / HOLD / STOP |
| `成果收割审计` | 对当前项目族及可识别的相邻版本执行同一只读 Gate |
| `新版本审计` | 先做成果收割 Gate；仅对 ONE_DECISIVE_EXPERIMENT 审计前序 blocker，不创建新版本 |
| `项目体检` | 只读检查项目结构、轮次、敏感文件和运行环境 |
| `状态` | 显示当前轮次、阶段和下一步 |
| `快速验证：...` | 围绕一个 claim 和一个决定性比较生成首轮紧凑 prompt，最多 1-3 轮 |
| `继续快速验证` | 上一轮为 INCONCLUSIVE 时生成下一轮紧凑 prompt，最多到第 3 轮 |
| `生成下一轮` | 生成下一个 `promptN`，等待审查 |
| `修改当前 prompt：...` | 按反馈修改当前 prompt，不执行 |
| `执行当前轮` | 执行当前 prompt，完成必要有效性检查并生成同轮 `resultN` |
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

`继续 N 轮` 是唯一的多轮模式。它最多执行指定轮数，并在关键有效性检查失败、科研判断不明确、数据泄漏风险、敏感文件风险、破坏性操作或外部凭据缺失时提前停止。

任何模式都不会自行无限循环。

快速验证模式只回答一个科学决策：一个 claim、一个决定性比较、一个最小决策级规模，并在 1-3 轮内给出 `GO`、`PIVOT`、`STOP` 或 `INCONCLUSIVE`。Prompt 和 Result 不再重复全局规则，只保留决策所需字段。

正式 `promptN.md` 和 `resultN.md` 不直接使用第一稿。skill 会先在工作上下文形成未发布内稿，分别检查科学逻辑与可执行性/事实证据，修改后重新检查；只有未发现实质问题时才生成单一正式文件。内稿和详细审查过程不会另存为文件，也不会增加历史文档负担。若关键歧义无法消除，skill 会停止发布并明确指出需要确认的内容。

根目录只维护一个轻量论文证据表 `paper_map.md`。它不要求每轮更新，只在出现决策级结果、claim 改变、准备升级到 paper-grade 或开始写论文时更新。

项目组合与成果收割 Gate 只在准备启动后继版本或用户主动要求时运行，不会拖慢普通轮次。它先为每个项目族定义“最小可发表单元”，再给出一个资源分配动作：`WRITE_NOW` 表示证据已足以形成边界清楚的最低可投稿论文，应冻结新实验并完成投稿；`ONE_DECISIVE_EXPERIMENT` 只允许一个能够改变投稿判断的实验；`HOLD` 暂不投入；`STOP` 关闭项目族。四类结果只在对话中用一张紧凑表报告，不新增 registry。

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

计划书中还应明确论文定位、候选核心结论和证据链，并区分“只用于跑通代码的 smoke 规模”“能够比较方法或观察效应的最低科研规模”“正式论文规模”。例如你判断至少需要 500 cells 才可能看出差异，就应把 500 cells 写成科研推断下限；skill 不应自行退回 20 cells 得出方法或生物学判断。

计划书只详细展开当前正在决策的 Gate，包括 claim、决定性比较、最低决策级规模、判据、产物和立即分支。未被上游结果解锁的后续 Gates 各写一句即可，不需要提前设计 Prompt5-Prompt11。约 300 个非空行或 20 KB 是上下文提醒，不是阻断执行的硬限制。

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

如果你同时维护多个项目族，准备启动任何后继版本前先运行：

```text
$research-project-coding-copilot 项目组合审计：E:\mycode；/home/mycode
```

skill 会去除镜像、模板和改名副本，为每个项目族定义一个最小可发表单元，并只给一个动作：`WRITE_NOW`、`ONE_DECISIVE_EXPERIMENT`、`HOLD` 或 `STOP`。输出只是一张只读表；不会生成新文件、prompt 或版本。没有提供组合根目录时，可以用“成果收割审计”只检查当前项目族和可识别的相邻版本。

只有分类为 `ONE_DECISIVE_EXPERIMENT` 时，才允许继续考虑那一个实验；应优先在当前仓库完成。若确实需要建立独立后继版本，再运行：

```text
$research-project-coding-copilot 新版本审计
```

skill 会先读前序版本的终局结果和轻量摘要，提取真正导致 STOP 的根本 blocker。仅更换模型、特征表示、阈值、seed、metric、亚组或版本号，不足以启动新版本。新版本必须带来独立数据/生物学单位、更高测量分辨率、真正不同的 estimand、正交证据或失败结果之外已有支持的新假设。

同一根本 blocker 已造成两个版本 STOP 时，默认关闭该 claim/数据项目族；同一数据/outcome 项目族连续三个版本 STOP 后，任何重启都必须先审计。审计只有 `GO` 才允许创建新版本，`PIVOT` 要求换数据或科学问题，`STOP` 关闭项目族，`INCONCLUSIVE` 只指出一个待确认的外部事实。STOP 后最多做一次失败归因，不能用 post-hoc 亚组不断挽救已关闭 claim。根本 blocker 记录在现有 `paper_map.md`，不新增 registry。

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

## 主线优先的科研推进

skill 默认目标是缩短“研究想法到有效决策”的时间：

- 每轮重新比较数据、基线、候选模型、实验、分析和工程工作的论文信息增益，不默认继续最深的未完成子任务；
- 一旦具备有效 target、split 和 metric，优先完成“简单基线 + 候选模型 + 决策级比较”的最短纵向切片；
- 探索阶段允许清晰、可追踪的脚本或 notebook，路线获得 `GO` 后再补模块化、通用接口、广泛测试和完整文档；
- 工程 blocker 先做一次聚焦修复，仍失败时优先绕过、简化、换实现或给出 `INCONCLUSIVE`，不得连续多轮钻同一问题；
- 分层验证：工程 smoke 只负责跑通，科研决策级实验必须达到计划书规定的最低有效规模，论文级实验使用完整设计；
- 已验证代码路径不重复做微型 pilot，优先推进论文核心问题和 claim-to-evidence 链；
- 用户或计划书规定的最低规模不可为了省时自行缩小，例如要求至少 500 cells 时，20 cells 只能用于工程 smoke；
- 昂贵或外部 API 任务才要求缓存、成本记录和断点恢复；
- 数据来源、配置、环境、随机种子和代码版本可追踪；
- benchmark 公平并检查数据泄漏；
- 重要结论保留不确定性、负结果和解释边界；
- 长任务有必要的阶段进度；
- 不读取密钥内容，不把大文件、日志或模型权重载入 AI 上下文。

## 大项目与低 Token 模式

项目变大后，skill 会：

- 先搜索和生成仓库摘要，再读取必要片段；
- 默认跳过 `outputs/`、大型数据、日志和生成目录的内容枚举；
- 不读取 API key、token、credential、`.pem` 或 `.key` 文件；
- 优先读取 checkpoint 和最近 1 至 3 个相关 result；
- 对表格、manifest 和日志先做程序化摘要；
- 每 10 至 20 个重要轮次建议生成 workflow checkpoint。

低 token 模式不会跳过会影响数据有效性、泄漏、指标和核心结论的必要检查。

这个 skill 的目标不是把仓库打磨成“工程上最完整”的项目，而是尽早设计模型、尽早运行具有辨别力的实验、尽早决定 GO/PIVOT/STOP/INCONCLUSIVE。工程成熟度跟随证据成熟度，只有存活下来的论文关键路径才值得系统加固。

## 生信数据与指标判定

DNA/RNA-seq、单细胞、ATAC-seq、Hi-C 和蛋白组数据默认被视为带有技术噪声、稀疏性、batch 与处理流程误差的观测，而不是无误差的真实生物状态。因此 skill 不使用通用固定的 correlation、AUROC 或 accuracy 门槛：

- 有严格可比同行 benchmark 时，在相同数据、split、输入、预处理和 metric 下，超过同行或达到实际/统计非劣即可支持路线可行；
- 只有部分条件可比的论文数字只作为背景范围；
- 新任务没有 benchmark 时，以简单基线、null/负对照、重复稳定性、不确定性和生物学或正交一致性共同判断；
- 噪声过大、区间同时包含有效与无效结果时判为 `INCONCLUSIVE`，不因没达到武断阈值直接 `STOP`；
- 与同行持平只说明模型路线可行。论文贡献还需要新任务、泛化、效率、解释性、机制或生物学发现中的至少一项。

## 高级 CLI

日常使用不需要手动运行这些命令。它们主要用于调试、自动检查或单独操作状态：

```bash
python scripts/research_copilot.py init --target .
python scripts/research_copilot.py adopt --target .
python scripts/research_copilot.py status --target .
python scripts/research_copilot.py context-summary --target .
python scripts/research_copilot.py check --target .
python scripts/research_copilot.py prompt-check --target . --round N --strict --mark-drafted
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

同步脚本会跳过版本控制元数据、`.vscode`、Python 缓存和 `.tmp*` 临时目录。
