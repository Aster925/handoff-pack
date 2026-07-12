# Progress Log / 进度日志

> 这是项目的**持久记忆 (durable memory)** —— 结构化笔记 (structured note-taking)。
> 每个 session 结束**追加**一条 (最新在最上)。不要删旧记录;它是给下一个 agent 的交接。
> 只写"裸代码看不出"的东西:意图、决策理由、卡点、下一步。
> ⚠ **本文件会随时间超过单次可读上限**(Read 单次 ~25k tokens):新 session **勿只截开头**;
> 「下一步/待办」不要只散落在这里 —— 同步登记 [`BACKLOG.md`](BACKLOG.md)(**待办唯一账本**,永远短到一口气读完)。

<!-- 复制下面这块作为新条目 / copy this block for each new entry -->

## [YYYY-MM-DD] Session N — <一句话主题>
- **做了 / Did:** <这次完成/改动了什么>
- **状态 / Status:** `done | partial | blocked`
- **为什么 / Why:** <做了哪些非显然的决策,以及理由>
- **下一步 / Next:** <下个 session 该从哪开始,最具体的入手点>
- **卡点 / Blockers:** <如有:卡在哪、试过什么、缺什么>
- **隐性信息 / Hidden context:** <环境怪癖、依赖坑、临时绕过的地方 etc.>
- **改了哪些 feature / Features touched:** <F1: false→true 等>

---

## [初始化 / Init] Session 0 — 交接产物落地
- **做了 / Did:** 用 handoff-pack 生成 AGENTS.md / CLAUDE.md / feature_list.json / init 脚本。
- **状态 / Status:** partial
- **下一步 / Next:** 把各文件中的 `<...>` / TODO 占位符替换为真实项目内容。
- **隐性信息 / Hidden context:** <迁移来源、原始环境版本、与 AI 的关键对话结论 etc.>
