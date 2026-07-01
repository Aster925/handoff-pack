---
name: handoff-pack
description: >-
  Make any local project portable and drift-resistant for handoff or migration.
  Use when the user wants to hand a project off to another session / machine /
  teammate, migrate it across OSes (e.g. Windows ↔ macOS), prevent "project
  drift" caused by lost context, or stop a fresh agent from guessing at intent.
  Also use to generate or refresh AGENTS.md / CLAUDE.md / a progress log /
  feature checklist / init scripts, to audit a project for drift risk and
  missing handoff artifacts, or to write a handoff report before ending a long
  session. Triggers on: "hand off this project", "项目交接", "防漂移",
  "迁移到另一台机器", "migrate to another machine", "generate AGENTS.md",
  "audit drift", "make this repo reproducible", "交接文档".
---

# Handoff Pack — 项目交接 & 防漂移工具包

让任何本地项目变得**可移植、可复现、不漂移**,适合交接 / 迁移 / 跨 session 续作。

## 核心心智模型 / Mental model（先理解再动手）

> **漂移的根因不是 LLM 笨,也不是 context 太小,而是仓库里缺"浓缩状态 (condensed state)"。**
> 代码只体现"怎么做",不体现"为什么"和"做到哪"。新 session 看不到意图,只能从裸代码逆向 +
> 用自己的假设填空 → 漂移。
> **解法不是扩 context,而是把「意图 / 架构 / 进度 / 运行方式」浓缩进几个仓库文件**,
> 让任何新 session 在 context 限制内一读就懂、精准复现。

落地成五个产物 (全部进 git):

| 文件 | 作用 | 治的漂移 |
|---|---|---|
| `AGENTS.md` | **唯一真相来源**:做什么/架构/怎么跑/边界/规则。跨工具可读 (Cursor/Copilot/Gemini)。 | 缺意图、缺架构 |
| `CLAUDE.md` | 薄指针,`@AGENTS.md` + 仅 Claude 特有内容 | 工具特定差异 |
| `PROGRESS.md` | 持久记忆 / 结构化笔记,每 session 追加 | 隐性进度丢失 |
| `feature_list.json` | 功能清单,agent 只能改 `passes` | 过早宣布完工 |
| `init.sh` + `init.ps1` | 一键重建环境并运行 (跨平台) | 换机器不知道怎么跑 |

外加 `.gitattributes`(行尾)、`.env.example`(密钥模板)、按需 `HANDOFF.md`(一次性交接报告)。

## 五种模式 / Five modes

确定 `<TARGET>` = 目标项目根目录(默认当前目录,可向用户确认)。

1. **audit** — 审计漂移风险:跑脚本,得到缺失产物 + 漂移信号 + 修复建议。
2. **init** — 生成完整交接包:脚手架落地模板 → **阅读代码填充真实内容**。
3. **handoff** — 结束 session / 迁移前,写 `HANDOFF.md` + 更新 `PROGRESS.md`。
4. **verify** — 从"干净状态"验证:跑 `init`,基础 e2e 测试,核对 `feature_list.json`。
5. **migrate** — 跨机器/OS 迁移检查清单(锁版本、行尾、绝对路径、未跟踪文件)。

**每种模式的详细步骤见 [`reference/workflows.md`](reference/workflows.md) —— 执行前按需读取该文件(progressive disclosure)。**

## 快速上手 / Quick start

```bash
# 1) 审计目标项目(脚本零依赖,Windows 用 python,mac/linux 用 python3)
python skills/handoff-pack/scripts/drift_audit.py audit "<TARGET>"
#    机器可读: 末尾加 --json

# 2) 补齐缺失的交接文件(只创建不存在的,不覆盖)
python skills/handoff-pack/scripts/drift_audit.py scaffold "<TARGET>"

# 3) 然后由 agent 阅读代码,把模板里的 <...> / TODO 换成真实内容
```

> 脚本只做**确定性检查 + 脚手架**;理解项目意图、填充内容、判断 `passes` 由 agent 完成。
> 这是有意的职责划分(tool 做机械活,agent 做判断活)。

## 不可动摇的规则 / Hard rules

- **AGENTS.md 是唯一真相来源**;通用信息只写一处,避免 AGENTS.md 与 CLAUDE.md 双份漂移。
- **`feature_list.json` 只允许改 `passes` 字段**;不得增删功能或改描述/步骤。
- 标 `passes:true` 前**必须**实际跑通验证 (优先端到端,别只信单元测试/curl)。
- 交接文档用**指针 (just-in-time)**:指向文件/路径/commit,**不要把内容粘进来**。
- 一次只推进一个 feature;每 session 结束:干净 commit + `PROGRESS.md` 追加一条。
- 填模板时,凡是不确定的事实**先去代码/历史里查证**,查不到就在 HANDOFF 标为开放问题,**不要假设**。

## 本 skill 内含文件 / Files in this skill

- `scripts/drift_audit.py` — 审计 + 脚手架脚本(stdlib,跨平台)
- `templates/` — 上述所有文件的可填充模板
- `reference/workflows.md` — 五种模式的逐步操作手册
