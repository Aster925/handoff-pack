# Claude Code 云端工作流 & 防漂移指南
> Cloud workflow & anti-drift reference for long-running agent projects

本文档整理自一次完整的学习对话,作为新 project 的"种子文档" (seed document)。
目的:让任何新的 LLM session 读完即可掌握全貌,**不漂移、不遗漏**。

**参考链接 (Reference):**
Anthropic — *Effective harnesses for long-running agents* (Nov 26, 2025)
https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

---

## 1. Claude Code 的两种运行方式

| | 本地 CLI (Local) | 云端 CC Web (GitHub-connected) |
|---|---|---|
| 代码跑在哪 | 你的 Mac / PC | Anthropic 托管的虚拟机 (managed VM) |
| 需要自己的服务器吗 | 否 | 否 |
| 远程/跨设备 | 需要 SSH | 原生支持 (手机/网页/CLI 互通) |
| 能访问本地文件/密钥吗 | 能 | **不能**(`.env`、本地 secret 被隔离) |
| 网络 | 不受限 | 默认封锁,需 whitelist 域名 |
| 权限 | 每步可能要确认 | 默认 `--dangerously-skip-permissions`(因沙箱安全) |

**机制:** CC Web 把仓库 clone 到云端沙箱 → 改代码、跑测试 → 推到**新分支** → 开 **PR** 让你审查。
它从不直接改你的 `main`,所以 agent 自主运行也安全。

**适用判断:**
- 用 CC Web → 自包含的 repo 任务、想手机发起、并行多 agent。
- 留本地 CLI → 需要本地 shell / 文件 / 密钥 / 平台特定环境(如 Windows PowerShell、MCP 配置)。
- 两者不是二选一,大多数人都保留。

**入口:** https://claude.ai/code → Connect GitHub → 在 Cloud Environment settings 里 whitelist 域名 / 粘贴 `.env`。

---

## 2. Git 核心概念串联

完整链路:
```
写代码 → commit → push → (开 PR) → review → merge
        提交     推送    合并请求   审查    合并
```

- **branch (分支)** = 独立的开发线。从 `main` "长出一根树枝",随便改不影响主干。
- **push** = 把本地 commit **上传**到 GitHub 某个分支。(本地 → 远程)
- **PR (Pull Request)** = push 之后,**申请把分支合并进 main**。展示 diff,供 review。
- **merge (合并) ≠ replace (替换)** = 把分支改动**融合**进 main;原有内容**保留**,只更新你动过的行。
- **merge conflict (合并冲突)** = 同一行被两边同时改,Git 让你手动定夺。

**为什么个人项目感觉不到 PR?**
因为你一直直接 push 到 `main`(单人项目,无需审查)。PR 在两种情况登场:① 团队协作需 review;② cloud agent 改完代码不敢直接动 main,推到新分支 + 开 PR 让你把关。

| | 你平时(个人) | CC Web(云端 agent) |
|---|---|---|
| push 到 | `main` | 新分支 |
| PR | 跳过 | 自动开 |
| 谁拍板合并 | 直接推就生效 | 你 review 后点 Merge |

---

## 3. 为什么项目会"漂移" (drift) —— 根因分析

> 现象:project 迁移后(如 Windows → macOS),LLM 读取后没按原本项目复现,会"思考漂移"或遗漏。

**核心是 context 限制,但分两层:**

**第一层 — 物理限制 (hard limit):**
LLM 一次能读的 token 有上限。几十个文件、上万行代码塞不进一个 context window。
所以 agent 是**边扫边猜**(读几个文件 → 推测结构 → 决定下一步),看到的永远是**局部**。

**第二层(真正元凶)— 没有"浓缩状态"可读:**
即使 context 再大,如果项目里没有文件告诉它"这是什么 / 做到哪 / 怎么跑",它只能从**裸代码逆向重建你的意图**。
而代码只体现"怎么做",不体现"为什么"和"原计划"。逆向时必然填入自己的假设 → **漂移**。

```
你以为 LLM 看到:  整个项目 + 原始意图 + 完整历史
LLM 实际看到:     局部代码,没意图、没计划、没进度
                            ↓
                 用自己的假设填空 → 漂移 / 遗漏
```

**为什么迁移后特别明显:**
迁移时最容易丢的恰恰是"非代码"信息 —— 你脑子里的计划、和 AI 的聊天记录、隐性环境(依赖版本、运行方式)。
这些都**没进仓库**。迁移后新 session 只剩裸代码,意图层全没了。

**关键认知:不是 LLM 笨,是缺"交接文档"。**
解法**不是扩 context,而是降低 LLM 理解项目所需的 context** —— 把意图浓缩成几个仓库文件。

---

## 4. 迁移漂移的具体技术原因(macOS 迁移清单)

| 原因 | 说明 | 修复 |
|---|---|---|
| 依赖没锁版本 | `requirements.txt` 没写死 `==`,两边版本不一致 | 锁版本 / 用 `uv` / `poetry` 生成 lockfile |
| venv 不可移植 | venv 含平台编译的二进制 + 绝对路径,不能直接拷贝 | 新机重建:`python -m venv .venv` → `pip install -r requirements.txt` |
| 换行符 / 路径分隔符 | Windows `CRLF` vs macOS `LF`;`\` vs `/` | `.gitattributes` 写 `* text=auto eol=lf`;代码用 `pathlib` |
| 未跟踪文件丢失 | `.env`、`.gitignore` 排除的文件、生成产物只在原机硬盘 | 提交 `.env.example`(只有键名);真 `.env` 留本地 |
| OS 特定配置 | Windows PowerShell / MSIX MCP 配置在 macOS 不通用 | 改成跨平台,或在文档里分系统标注 |

---

## 5. 防漂移的工程模式(来自 Anthropic 文章)

**核心思路:让仓库成为唯一真相来源 (single source of truth),目标是"从干净 clone 能一键重建"。**

文章方案 = 两个 agent(同一模型,只是初始 prompt 不同):
- **Initializer agent** — 第一次运行搭好环境。
- **Coding agent** — 之后每个 session 做增量进展,并留下清晰产物。

**两个被反复观察到的失败模式:**
1. agent 想一次做太多 → 中途耗尽 context → 留半成品,下个 agent 瞎猜。
2. 后期 agent 看一眼有进展 → 直接宣布"做完了"。

**关键产物(全部进 git):**

| 文件 | 作用 | 解决的漂移问题 |
|---|---|---|
| `init.sh` | 一键启动开发服务器 | 换机器后不知道怎么跑 |
| `claude-progress.txt` | 历代 agent 做了什么的日志 | 隐性进度落盘 |
| `feature_list.json` | 完整功能清单,初始全标 `passes: false` | 防止过早宣布完工 |
| git history | 每步带描述的 commit | 可回退到能跑的状态 |

**两个实用细节:**
- 功能清单用 **JSON 而非 Markdown**(模型更不容易乱改 JSON),且规定 agent 只能改 `passes` 字段。
- 测试要用**浏览器自动化**像真人那样端到端测,别只信单元测试 / curl。

**"clean state" 定义:** 适合合并到主分支的代码 —— 无重大 bug、整洁有文档、别人能直接接手。

---

## 6. 可直接复用的模板

### 6.1 `CLAUDE.md`(放仓库根目录)

```markdown
# Project: <项目名>

## What this project does / 这个项目做什么
<一两句话说清目标和范围>

## Architecture / 架构
- 技术栈:
- 关键目录:
- 数据流:

## How to run / 怎么跑
见 `init.sh`。先决条件:<Python 版本、依赖等>

## Session start routine / 每次开场必做
1. Run `pwd` to confirm working directory.
2. Read `claude-progress.txt` and `git log --oneline -20`.
3. Read `feature_list.json`, pick the highest-priority feature with `"passes": false`.
4. Run `init.sh`, do a basic end-to-end test BEFORE starting new work.

## Rules / 规则
- 只改 `feature_list.json` 的 `passes` 字段,不准删改测试。
- 每个 session 结束:写 git commit(描述清晰)+ 更新 `claude-progress.txt`。
- 一次只做一个 feature。
- 路径用 pathlib,不写死分隔符。

## Platform notes / 平台差异
- macOS:
- Windows:(如有 PowerShell / MCP 特定配置,在此标注)
```

### 6.2 `claude-progress.txt`

```text
# Progress Log

## [YYYY-MM-DD] Session N
- Worked on: <feature>
- Status: <done / partial / blocked>
- Next: <下个 session 该做什么>
- Notes: <任何下个 agent 需要知道的隐性信息>
```

### 6.3 `feature_list.json`

```json
[
  {
    "category": "functional",
    "description": "<一句话描述某个端到端功能>",
    "steps": [
      "Step 1",
      "Step 2",
      "Verify expected result"
    ],
    "passes": false
  }
]
```

### 6.4 `init.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# Rebuild environment / 重建环境(venv 不要提交,在此重建)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start dev server / 启动开发服务器
# python app.py   # 按项目实际命令修改
```

### 6.5 `.gitattributes`

```text
* text=auto eol=lf
```

---

## 7. 术语表 (English glossary — 英语学习用)

| 英文 | 中文 | 笔记 |
|---|---|---|
| harness | 支撑框架/挽具 | 工程语境:让系统受控运行的支架 |
| failure mode | 失败模式 | |
| to one-shot something | 一次性搞定 | 口语,常带贬义(想偷懒一步到位) |
| incremental progress | 增量进展 | |
| context window | 上下文窗口 | LLM 一次能读的最大信息量 |
| to reverse-engineer intent | 逆向重建意图 | |
| condensed state | 浓缩状态 | 项目精华摘要 |
| single source of truth | 唯一真相来源 | 缩写 SSOT |
| portable | 可移植的 | venv is **not** portable |
| to pin a version | 锁定版本 | `pip install foo==1.2.3` |
| hardcoded | 写死的/硬编码的 | hardcoded path 是迁移大坑 |
| untracked (files) | (git) 未跟踪的 | 被 .gitignore 排除的 = 不会被迁移 |
| to merge / merge conflict | 合并 / 合并冲突 | merge ≠ replace |
| clean state | 干净状态 | 适合合并到主分支的代码 |

经典工程吐槽:**"But it works on my machine!"**(但在我电脑上明明能跑啊!)—— 正是描述"项目和某台机器绑死"的漂移状态。

---

## 一句话总结

> 漂移的根因不是 LLM 笨,而是项目缺"交接文档"。
> 解法不是扩 context,而是**把意图、进度、运行方式浓缩成几个仓库文件**,
> 让任何新 session 在 context 限制内一读就懂、精准复现。
> 迁移时,带走的不该只是代码,而是 **代码 + 这套交接文档**。
