# AGENTS.md — handoff-pack 工具包自身

> 本文件是**本工具包项目自己**的唯一真相来源(dogfood:工具包也守自己的方法)。人向叙事见 [`README.md`](README.md);方法论见 [`docs/methodology.md`](docs/methodology.md);进度见 [`PROGRESS.md`](PROGRESS.md)。

## 这是什么 / What
一个独立工具:为**其它**本地项目生成"交接包"(AGENTS.md 唯一真相来源 + PROGRESS + feature_list + init)并审计漂移,对抗 context 过长 / 环境变更 / 架构缺失导致的项目漂移。**不在本仓库写业务代码。**
- 已发布公开仓库(MIT):https://github.com/Aster925/handoff-pack
- 已在 2 个真实本地项目验证(均 HIGH→LOW):一个学习类 App+内容管线、一个视频课件管线。

## 结构 / Layout
- `skills/handoff-pack/` — 可安装的 Claude Code skill(SKILL.md + `scripts/drift_audit.py` + `templates/` + `reference/workflows.md`)。
- `commands/` — 全局 slash 命令:`/handoff`(收尾保存)、`/toolkit-check`(自检+校对)、`/toolkit-refresh`(方法论调研)。
- `hooks/handoff_hook.py` + `hooks/settings.snippet.json` — SessionStart/PreCompact 钩子。
- `scripts/guardian.py` — 自检 + 看护脚本。
- `docs/methodology.md` — 方法论 + 2026 官方/学术对照(§6)。

## 怎么跑 / Run
- **看护自检(每次维护先跑)**:`python scripts/guardian.py` → ①工具包自检 ②校对 `watched_projects.txt` 里的项目 ③方法论是否到期。
- 单独审计某项目:`python skills/handoff-pack/scripts/drift_audit.py audit "<项目路径>"`。
- 安装到全局(供所有项目用):`cp -r skills/handoff-pack ~/.claude/skills/`;命令 `cp commands/*.md ~/.claude/commands/`;钩子见 README「自动化」。

## 自维护循环 / Self-maintenance loop
1. **稳固性优先**:`guardian.py` 的自检必须全绿,才做别的(自检失败=工具包本身坏了,先修)。
2. **校对下游**:guardian 对被看护项目跑 audit;HIGH/MED 则去**该项目自己的窗口**跑 `/handoff`(**不在这里改它们**)。
3. **定期刷新**:距 `.methodology_review` ≥30 天,跑 `/toolkit-refresh` 搜最新方案 → 提议更新 `docs/methodology.md`/skill → 更新该日期。

## 边界 / Boundaries (do NOT)
- **不碰被看护项目的文件**:English/French 的实施由它们各自的会话进行,本工具包只审计+报告。
- **公开仓库防泄露**:`watched_projects.txt`、`.claude/settings.local.json` 含个人绝对路径,**已 gitignore**;推送前对 **tracked 文件**(不是工作区)扫「个人绝对路径 / 密钥 / 内网 IP」,确认干净再 push。
- `feature_list.json` 只改 `passes` 字段。
- 不擅自 `git push`(尤其公开仓库)——除非用户明确同意。

## Session 开场 / Start routine
1. `.claude/settings.json` 的 SessionStart 钩子会**自动**跑 `scripts/guardian.py`(也可手动 `/toolkit-check`)。
2. 读 `PROGRESS.md` 顶部。
3. 自检 FAIL 先修;下游 HIGH/MED 去对应项目窗口处理;方法论到期则 `/toolkit-refresh`。

## 相关 / Related
`README.md`(叙事+安装)· `docs/methodology.md`(为什么+2026对照)· `PROGRESS.md`(进度)· `feature_list.json`(功能清单)。
