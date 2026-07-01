#!/usr/bin/env python3
"""
handoff_hook.py — handoff-pack 全局钩子 (SessionStart / PreCompact)。

在**有交接包**(存在 AGENTS.md 或 PROGRESS.md)的项目里:
  - session-start: 提醒开场例程 + 摘录 PROGRESS 顶部,让 agent 一开口就知道"上次做到哪"。
  - pre-compact:   上下文压缩前提醒"先 /handoff 保存交接",避免进度只留在被清理的上下文里。
在**没有交接包**的项目里:完全静默(不打扰)。

由 ~/.claude/settings.json 的 hooks 调用:
  python <this> session-start     (SessionStart 事件)
  python <this> pre-compact       (PreCompact 事件)
钩子输入 JSON 从 stdin 传入(含 cwd);输出到 stdout 会被并入会话上下文。
"""
import sys, os, json
from pathlib import Path

PROGRESS_CANDIDATES = ("PROGRESS.md", "docs/PROGRESS.md", "claude-progress.txt", "PROGRESS.txt")


def find_progress(cwd: Path):
    for rel in PROGRESS_CANDIDATES:
        p = cwd / rel
        if p.exists():
            return p
    return None


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "session-start"

    raw = ""
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
    except Exception:
        pass
    try:
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}
    cwd = Path(data.get("cwd") or os.getcwd())

    has_agents = (cwd / "AGENTS.md").exists()
    progress = find_progress(cwd)

    # 非交接包项目 → 静默,绝不打扰其它项目/会话
    if not has_agents and progress is None:
        return

    if mode == "pre-compact":
        print("[handoff-pack] 上下文即将压缩。请**先保存交接**再继续:运行 /handoff "
              "(在 PROGRESS.md 顶部追加一条 + 更新 feature_list 的 passes + 征得用户确认后 commit)。"
              "压缩清理的是上下文窗口,不是仓库 —— 不落盘的进度会丢。")
        return

    # session-start
    out = ["[handoff-pack] 本项目已有交接包,请按防漂移例程开场:"]
    if has_agents:
        out.append("· AGENTS.md 是唯一真相来源(通常已随 CLAUDE.md 加载)。")
    if progress:
        rel = progress.relative_to(cwd).as_posix()
        out.append(f"· 先读 {rel} 顶部,向用户复述「上次做到哪 / 接下来该做什么」再动手。")
        try:
            lines = [l for l in progress.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
            snippet = lines[:12]
            if snippet:
                out.append("  —— PROGRESS 顶部摘录 ——")
                out.extend("  " + l for l in snippet)
        except Exception:
            pass
    out.append("· 结束、或发现 context 快满时,运行 /handoff 保存交接。")
    print("\n".join(out))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()
