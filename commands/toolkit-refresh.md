---
description: 搜最新防漂移/handoff/context 方案 → 提议更新方法论与 skill → 确认后提交
---
为 handoff-pack 做一次**方法论刷新调研**(对抗方案随时间过时)。稳固性优先:先确保 `python scripts/guardian.py` 自检全绿。

1. 用 WebSearch / WebFetch 搜 **2026 年至今** 的:项目漂移 / 长任务 handoff / context engineering / AGENTS.md 标准 / Claude Agent Skills(SKILL.md 规范)/ 记忆与上下文管理 的最新**官方**(Anthropic、平台文档)与成熟社区/学术实践。大块检索可派 subagent,只收结论。
2. 与现有 [`docs/methodology.md`](docs/methodology.md)(尤其 §6)+ `skills/handoff-pack/` 对照,**只挑真正新、且可落地**的差异(别为改而改)。
3. 若有值得纳入的:**提议具体编辑**(哪个文件、哪段、改成什么),每条附**来源链接**;**先给用户看,确认后**再动手改。
4. 改完:把 `.methodology_review` 更新为**今天日期**;在 `PROGRESS.md` 顶部追加一条;**经用户确认**后用**具体文件** `git add` + commit。
5. 没有实质更新就如实说"暂无需要更新",并把 `.methodology_review` 更新为今天(表示已复核过)。

红线:保守、可追溯(带引用);**不自动 `git push`**(公开仓库);push 前对 **tracked 文件**做泄露扫描(个人路径/密钥/IP)并征得同意。
