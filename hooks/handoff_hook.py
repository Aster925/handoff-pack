#!/usr/bin/env python3
"""
handoff_hook.py — handoff-pack 全局钩子 (SessionStart / PreCompact)。

在**有交接包**(存在 AGENTS.md 或 PROGRESS.md)的项目里:
  - session-start: 提醒开场例程 + 摘录 PROGRESS 顶部,让 agent 一开口就知道"上次做到哪"。
  - pre-compact:   上下文压缩前提醒"先 /handoff 保存交接",避免进度只留在被清理的上下文里;
                   并**重注入 AGENTS.md 的「边界」+「固化流程索引」小节**(constraint pinning)——
                   压缩会悄悄丢约束,丢约束后违反率显著上升(arXiv 2606.22528);丢流程索引则
                   新上下文会按"通用做法"自行分析,故把两节原文钉回上下文。
在**没有交接包**的项目里:完全静默(不打扰)。

由 ~/.claude/settings.json 的 hooks 调用:
  python <this> session-start     (SessionStart 事件)
  python <this> pre-compact       (PreCompact 事件)
钩子输入 JSON 从 stdin 传入(含 cwd);输出到 stdout 会被并入会话上下文。
"""
import sys, os, re, json
from pathlib import Path

PROGRESS_CANDIDATES = ("PROGRESS.md", "docs/PROGRESS.md", "claude-progress.txt", "PROGRESS.txt")
BOUNDARY_HEADING = re.compile(r"boundar|边界|red.?line|红线|do\s+not", re.IGNORECASE)
CANON_HEADING = re.compile(r"固化流程|固化裁定|canonical\s*workflows?|fixed\s*rulings", re.IGNORECASE)
PIN_MAX_CHARS = 2000  # 每节上限,防止把超长小节整个灌进上下文


def find_progress(cwd: Path):
    for rel in PROGRESS_CANDIDATES:
        p = cwd / rel
        if p.exists():
            return p
    return None


def extract_section(lines: list, heading_re) -> str:
    """提取第一个标题命中 heading_re 的小节原文,到下一个同级或更高级标题为止。"""
    out: list = []
    level = 0
    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if out:
            if m and len(m.group(1)) <= level:
                break
            out.append(line)
        elif m and heading_re.search(m.group(2)):
            level = len(m.group(1))
            out.append(line)
    return "\n".join(out).strip()[:PIN_MAX_CHARS]


def extract_pins(agents_md: Path) -> str:
    """constraint pinning:从 AGENTS.md 提取「边界」+「固化流程索引」小节原文。

    压缩丢约束后违反率显著上升(arXiv 2606.22528),故把这两节钉回上下文;
    固化流程索引同理——丢了它,新上下文会按"通用做法"自行分析(实案:法语项目 z15)。
    找不到 / 读不了 → 返回空串(调用方静默跳过)。
    """
    try:
        lines = agents_md.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return ""
    parts = [extract_section(lines, rx) for rx in (BOUNDARY_HEADING, CANON_HEADING)]
    return "\n\n".join(p for p in parts if p)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "session-start"

    raw = ""
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
    except Exception:
        pass
    raw = raw.lstrip("\ufeff")  # Windows PowerShell 管道会加 BOM,json.loads 会炸→cwd 静默回退错目录
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
        pins = extract_pins(cwd / "AGENTS.md") if has_agents else ""
        if pins:
            print("\n[handoff-pack] 约束重注入 / constraint pinning —— 压缩常会丢约束,"
                  "以下 AGENTS.md 边界/固化流程在压缩后**依然有效**,请继续遵守:\n" + pins)
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
        # stdin 同样重配:Windows 默认按本地编码(如 GBK)解码,会把 UTF-8 的 BOM/中文路径解成垃圾
        # → json 解析失败 → cwd 静默回退到错误目录。utf-8-sig 自动剥 BOM。
        sys.stdin.reconfigure(encoding="utf-8-sig", errors="replace")
    except Exception:
        pass
    main()
