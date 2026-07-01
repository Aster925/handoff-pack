# Pipeline Handoff Support — 项目交接 & 防漂移工具包
> Anti-drift handoff toolkit for local projects · 让任何本地项目可移植、可复现、不漂移

把"在我电脑上明明能跑"的项目,变成**任何新 session / 另一台机器 / 另一个人接手都能精准复现**的项目。

这是一个**独立工具项目**:你不在它里面写业务代码,而是把它当作工具,指向你**其它**的本地项目,
为它们生成一套"交接包 (handoff packet)",并审计它们的漂移风险。

---

## 为什么需要它 / Why

> **漂移 (drift) 的根因不是 LLM 笨,也不是 context 太小,而是仓库缺"浓缩状态 (condensed state)"。**

代码只体现"怎么做",不体现"为什么"和"做到哪"。当一个项目因为**上下文过长、环境变更、架构描述缺失、
跨机器迁移**而交到新 session 手上时,LLM 看到的只有局部裸代码,只能逆向重建意图、用自己的假设填空 —— 于是漂移。

**解法不是扩 context,而是把「意图 / 架构 / 进度 / 运行方式」浓缩进几个仓库文件**,
让任何新 session 在 context 限制内一读就懂。详见 [`docs/methodology.md`](docs/methodology.md)。

---

## 它生成什么 / What it produces

为目标项目落地一套进 git 的交接产物(以 **AGENTS.md 为唯一真相来源**):

| 文件 | 作用 |
|---|---|
| `AGENTS.md` | 唯一真相来源:做什么 / 架构 / 怎么跑 / 边界 / 规则。跨工具可读(Cursor / Copilot / Gemini …) |
| `CLAUDE.md` | 薄指针:`@AGENTS.md` + 仅 Claude Code 特有内容 |
| `PROGRESS.md` | 持久记忆 / 结构化笔记,每 session 追加 |
| `feature_list.json` | 功能清单,agent 只能改 `passes` 字段,防过早完工 |
| `init.sh` + `init.ps1` | 一键重建环境并运行(跨平台) |
| `.gitattributes` · `.env.example` | 行尾规范 · 密钥模板 |
| `HANDOFF.md` | 按需:一次性交接报告(下一程目标 / 进行中 / 卡点 / 隐性信息) |

---

## 项目结构 / Layout

```
pipeline-handoff-support/
├── README.md                          # 你正在读的文件
├── claude-code-cloud-and-anti-drift.md  # 种子文档 / 原始学习笔记 (seed)
├── docs/
│   └── methodology.md                 # 方法论 + 参考文献 (the "why")
└── skills/
    └── handoff-pack/                  # ← 自包含的 Claude Code skill,可直接拷走
        ├── SKILL.md                   # skill 入口 (model-invoked)
        ├── scripts/drift_audit.py     # 审计 + 脚手架 (stdlib,跨平台)
        ├── templates/                 # 上述所有文件的可填充模板
        └── reference/workflows.md     # 五种模式的逐步手册
```

---

## 安装 / Install

`skills/handoff-pack/` 是自包含的,把它装到 Claude Code 能发现 skill 的位置即可。

**全局可用(推荐)/ Global:**
```bash
# macOS / Linux
cp -r skills/handoff-pack ~/.claude/skills/handoff-pack
```
```powershell
# Windows PowerShell
Copy-Item -Recurse skills\handoff-pack "$env:USERPROFILE\.claude\skills\handoff-pack"
```

**只给某个项目用 / Per-project:** 拷到该项目的 `.claude/skills/handoff-pack/`。

安装后,在任意项目里说「帮我做项目交接 / 生成 AGENTS.md / 审计漂移」即可触发该 skill。

---

## 用法 / Usage

### A. 直接用脚本(任何 agent / 手动皆可)

```bash
# 审计目标项目的漂移风险(Windows 用 python,mac/linux 用 python3)
python skills/handoff-pack/scripts/drift_audit.py audit "C:/path/to/your/project"
#   机器可读 JSON: 末尾加 --json

# 补齐缺失的交接文件(只创建不覆盖,加 --force 可覆盖)
python skills/handoff-pack/scripts/drift_audit.py scaffold "C:/path/to/your/project"
```
脚本零第三方依赖,只做**确定性检查 + 脚手架**;填充真实内容由 agent 完成。

### B. 让 Claude Code 全程编排(推荐)

装好 skill 后,在目标项目里直说目标即可。skill 提供五种模式:

| 模式 | 做什么 |
|---|---|
| **audit** | 审计漂移风险,列出缺失产物 + 修复建议 |
| **init** | 脚手架落地 + 阅读代码填充真实内容,生成完整交接包 |
| **handoff** | 结束 session / 迁移前,写 HANDOFF.md + 更新 PROGRESS.md |
| **verify** | 从干净状态跑 init + 端到端测试,核对 feature_list |
| **migrate** | 跨机器 / 跨 OS 迁移检查清单 |

每种模式的详细步骤见 [`skills/handoff-pack/reference/workflows.md`](skills/handoff-pack/reference/workflows.md)。

---

## 自动化(可选,强烈推荐)/ Automation

把"每次交接"变成系统自动,不用背命令:

- **`/handoff` 命令**([`commands/handoff.md`](commands/handoff.md)):一个词完成"在 `PROGRESS.md` 顶部追加一条 + 把已验证功能的 `passes` 翻 true + **确认后** commit"。
- **SessionStart 钩子**:每次开会话**自动读 `PROGRESS.md` 顶部**,告诉你上次做到哪、接下来做什么。
- **PreCompact 钩子**:上下文压缩前**自动提醒**先 `/handoff` 保存(避免进度只留在被清理的上下文里)。
- 钩子脚本 [`hooks/handoff_hook.py`](hooks/handoff_hook.py) —— **在没有交接包的项目里自动静默**,不打扰。

安装(全局,一次性):
```bash
cp commands/handoff.md   ~/.claude/commands/
cp hooks/handoff_hook.py ~/.claude/hooks/
# 再把 hooks/settings.snippet.json 里的 hooks 块合并进 ~/.claude/settings.json
# (注意:exec 的 args 不展开 ~,路径要换成绝对路径)
```
装好后**新开一个会话**即生效(hooks 在会话启动时加载)。

---

## 设计取舍 / Design choices

- **AGENTS.md 为先 (AGENTS.md-first):** 用 2025 起的跨工具开放标准做唯一真相来源,CLAUDE.md 退化为薄指针,
  避免两份内容各自漂移。
- **脚本 vs agent 职责分离:** 脚本只做机械、确定性的事(查缺、扫描、脚手架);理解意图、填内容、判断完工归 agent。
- **指针优于内容 (just-in-time):** 交接文档存路径/链接而非粘贴大段内容,契合 context engineering。
- **跨平台:** Python stdlib 脚本 + 双 init 脚本 (`.sh` / `.ps1`),Windows ↔ macOS ↔ Linux 通用。

---

## 参考 / References

- Anthropic — *Effective context engineering for AI agents* — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic — *Effective harnesses for long-running agents* — https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- *AGENTS.md* open standard — https://agents.md
- GitHub *Spec Kit*(spec-driven development)— https://github.github.com/spec-kit/

完整推导、引用与术语表见 [`docs/methodology.md`](docs/methodology.md) 和种子文档 [`claude-code-cloud-and-anti-drift.md`](claude-code-cloud-and-anti-drift.md)。
其中 [`docs/methodology.md`](docs/methodology.md) §6 给出**对照 2026 年中官方/学术实践的复核**(SKILL.md 规范、AGENTS.md 共识、与平台 memory tool / context editing 的关系)。

---

## 状态 / Status

已在两个真实本地项目上验证(HIGH→LOW):一个学习类 App + 内容管线、一个视频/课件管线。
`skills/handoff-pack/scripts/drift_audit.py` 零第三方依赖,Python 3.13 实测可用。

## 许可 / License

[MIT](LICENSE) — 自由使用、修改、再分发。欢迎拿去改造成你自己的交接规范。
