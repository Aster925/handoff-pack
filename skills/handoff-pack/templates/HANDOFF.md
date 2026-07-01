# HANDOFF.md — 交接报告 / Handoff report

> 一次性、面向**下一个 session / 另一台机器 / 另一个人**的清晰交接。
> 原则:**指针优先 (just-in-time)**,不要把代码/文档内容粘进来,而是指路 + 给出意图。
> 生成日期 / Generated: `<YYYY-MM-DD>`   来源 / From: `<machine, OS, tool>`

## 1. 下一程的目标 / Purpose of next session
<下一个接手者最该先做什么、要达成什么。一两句。>

## 2. 现状快照 / Current state snapshot
- 分支 / Branch: `<branch @ short-sha>`
- 最近进展 / Recent: 见 `PROGRESS.md` 顶部 N 条
- 功能进度 / Features: `<passes=true 的数量 / 总数>`,详见 `feature_list.json`
- 能跑吗 / Runnable: `<是/否;init 脚本能否一键起>`

## 3. 完成 / 进行中 / 受阻 / Done · In-progress · Blocked
- ✅ 完成 / Done: <...>
- 🔄 进行中 / In-progress: <做到哪一步,代码在哪个文件/分支>
- ⛔ 受阻 / Blocked: <卡点 + 已尝试 + 需要的决定/资源>

## 4. 环境与复现 / Environment & reproduction
- 运行方式 / How to run: 见 `init.sh` / `init.ps1`
- 关键版本 / Pinned versions: `<runtime + 锁文件位置>`
- 必需环境变量 / Required env: 见 `.env.example`(真实值不在仓库)
- 已知平台差异 / Platform gotchas: `<Windows↔mac↔Linux 的坑>`

## 5. 未落盘的隐性信息 / Hidden context not in code
> 迁移最容易丢的就是这部分 —— 脑子里的计划、和 AI 的关键结论、临时决定。
- <意图/约束/为什么排除了某方案>
- <与 AI 对话里达成但没写进代码的结论>

## 6. 未提交改动 / Uncommitted work
- <`git status` 里未提交的内容;若已 stash 说明在哪>

## 7. 待解问题 / Open questions
- [ ] <需要人来拍板的问题>
- [ ] <...>

## 8. 接手第一步 / First action for the receiver
1. 跑 `init` 脚本 + 基础 e2e,确认能跑。
2. 读 `PROGRESS.md` + 本文件第 1、3 节。
3. 从 `feature_list.json` 最高优先级的 `passes:false` 开始。
