# AGENTS.md — <项目名 / PROJECT NAME>

> 本文件是本项目面向 AI coding agent 的**唯一真相来源 (single source of truth)**。
> 任何工具 (Claude Code / Cursor / Copilot / Gemini …) 都读最近的 AGENTS.md。
> 目标:**从干净 clone,任何新 session 读完即可精准复现项目,不漂移。**
> 占位符标 `<...>` 或 `TODO`,请用真实内容替换后删除本提示行。

## 项目概述 / Project overview
<一两句话说清:这个项目做什么、给谁用、当前阶段。>
<One or two sentences: what this does, who it's for, current stage.>

- 状态 / Status: `<planning | active | maintenance>`
- 仓库角色 / Repo role: `<app | library | service | pipeline | ...>`

## 架构 / Architecture
- 技术栈 / Stack: `<language + framework + key libs>`
- 关键目录 / Key dirs:
  - `<dir/>` — `<职责 responsibility>`
- 数据流 / Data flow: `<输入 → 处理 → 输出,一行画清>`
- 关键决策 / Key decisions: `<为什么这样设计;有意排除了什么 why this design, what was deliberately excluded>`

## 环境与运行 / Setup & run
> 详细一键脚本见 `init.sh` (macOS/Linux) 和 `init.ps1` (Windows)。
- 先决条件 / Prerequisites: `<runtime version, e.g. Python 3.12, Node 20>`
- 安装 / Install: `<command>`
- 运行 / Run: `<command>`
- 测试 / Test: `<command>`  ← 优先端到端 (e2e),别只信单元测试

## 代码规范 / Code style
- `<只写与默认不同的约定:格式化、命名、import 顺序、禁用项>`
- `<only conventions that differ from the tool's defaults>`

## 边界 / Boundaries (do NOT touch)
- 不要改 / Never edit: `<generated files, lockfiles, vendored dirs, migrations>`
- 不要删改测试断言,只允许让代码通过测试 / Don't weaken tests to pass.
- 不要把密钥写进代码或提交 `.env` / Never commit secrets.

## Agent 工作规则 / Working rules
- `feature_list.json`:agent **只能改 `passes` 字段**,不得增删功能或改描述。
- **待办只认账本**:每写「下一步/待/暂缓」必须登记 `BACKLOG.md` 的 OPEN;**宣布「完成/无缺口」前 OPEN 须清空或逐条说明**;关闭回写 commit 凭据,只增不删。
- 一次只做一个 feature;做完跑测试验证再标 `passes: true`。
- 每个 session 结束:写清晰的 git commit + 追加 `PROGRESS.md` 一条 + 同步 `BACKLOG.md`。
- 路径用相对路径 / pathlib,不写死分隔符或绝对路径。
- 不确定意图时,先读 `PROGRESS.md` 和 git log,**不要凭假设填空**。

## 每次开场必做 / Session start routine
1. 确认工作目录 (`pwd` / `Get-Location`)。
2. 读 `BACKLOG.md` **全文**(它很短,是待办唯一账本)+ `PROGRESS.md` 最近 2~3 条 + `git log --oneline -20`。**勿因 PROGRESS 长而只截开头** —— 待办以账本为准。
3. 读 `feature_list.json`,挑优先级最高且 `passes:false` 的功能。
4. 跑 `init` 脚本,做一次基础 e2e 测试,**确认能跑再动手**。
5. 若刚迁移机器/OS,先读「平台差异」节。

## 平台差异 / Platform notes
- macOS / Linux: `<差异点>`
- Windows: `<PowerShell / 路径 / MCP 等特定配置>`
- CI: `<如有>`

## 相关文件 / Related files (just-in-time, 不在此重复内容)
- `PROGRESS.md` — 历代进度日志(叙事,可以长)/ progress log
- `BACKLOG.md` — **待办唯一账本**(必须短);宣布完成前先清 OPEN / open-items ledger
- `feature_list.json` — 功能清单 / feature checklist
- `HANDOFF.md` — 跨 session/机器交接报告 / handoff report (按需创建)
- `CLAUDE.md` — Claude Code 专用指针 / Claude-specific pointer
