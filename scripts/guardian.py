#!/usr/bin/env python3
"""
guardian.py — handoff-pack 自检 + 项目校对 + 方法论刷新提醒。

每次运行做三件事(顺序即优先级):
  1) 工具包自检(**稳固性优先**):scaffold / 模板 / audit / 钩子 都能跑;
     且**已安装副本(~/.claude/…)与仓库一致** —— 安装方式是 cp,仓库改了副本不会跟着改,
     工具包自己也会漂移(Spec Kit "workflow as versioned dependency" 同理)。失败先修工具包。
  2) 校对被看护项目:对 watched_projects.txt 里每个项目跑 drift_audit,报风险 + 是否还守着交接包。
  3) 方法论刷新提醒:距上次复核 >= REVIEW_DAYS 天则提示跑 /toolkit-refresh 调研最新方案。

零第三方依赖(stdlib),跨平台。用法:python scripts/guardian.py
"""
from __future__ import annotations
import sys, os, json, hashlib, subprocess, tempfile, shutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "skills" / "handoff-pack" / "scripts" / "drift_audit.py"
HOOK = ROOT / "hooks" / "handoff_hook.py"
REVIEW_MARKER = ROOT / ".methodology_review"   # 内含 YYYY-MM-DD;由 /toolkit-refresh 更新
REVIEW_DAYS = 30


def _py(*args, stdin: str | None = None):
    return subprocess.run([sys.executable, *map(str, args)], input=stdin,
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


def run_audit(path: str) -> dict:
    try:
        p = _py(AUDIT, "audit", path, "--json")
        return json.loads(p.stdout)
    except Exception as e:
        return {"error": str(e)}


def selftest() -> list[tuple[str, bool, str]]:
    checks: list[tuple[str, bool, str]] = []
    tmp = Path(tempfile.mkdtemp(prefix="hp_selftest_"))
    try:
        _py(AUDIT, "scaffold", tmp)
        created = [p.name for p in tmp.iterdir()]
        checks.append(("scaffold 落地 10 文件", len(created) >= 10, f"{len(created)} files"))
        fl = tmp / "feature_list.json"
        ok = False
        if fl.exists():
            try:
                json.loads(fl.read_text(encoding="utf-8")); ok = True
            except Exception:
                ok = False
        checks.append(("feature_list.json 合法", ok, ""))
        a = run_audit(str(tmp))
        checks.append(("audit --json 可运行", "risk" in a, a.get("risk", "?")))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    try:
        h = _py(HOOK, "session-start", stdin=json.dumps({"cwd": str(ROOT)}))
        checks.append(("hook 脚本可运行", h.returncode == 0, ""))
    except Exception as e:
        checks.append(("hook 脚本可运行", False, str(e)))
    return checks


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _iter_files(root: Path):
    for f in sorted(root.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts:
            yield f


def install_drift() -> list[tuple[str, bool, str]]:
    """比对仓库源 ↔ 已安装副本(~/.claude/…)。未安装 → 跳过(OK);不同步 → FAIL 提示重装。"""
    home = Path.home() / ".claude"
    checks: list[tuple[str, bool, str]] = []

    # 目录整体比对:skill;单文件比对:hook
    targets: list[tuple[str, Path, Path]] = [
        ("skill 安装副本同步", ROOT / "skills" / "handoff-pack", home / "skills" / "handoff-pack"),
        ("hook 安装副本同步", HOOK, home / "hooks" / HOOK.name),
    ]
    for name, src, dst in targets:
        if not dst.exists():
            checks.append((name, True, "未安装(跳过)"))
            continue
        if src.is_file():
            diffs = [] if _sha(src) == _sha(dst) else [src.name]
        else:
            diffs = [f.relative_to(src).as_posix() for f in _iter_files(src)
                     if not (dst / f.relative_to(src)).exists() or _sha(f) != _sha(dst / f.relative_to(src))]
        if diffs:
            checks.append((name, False, f"{len(diffs)} 处不同步(改仓库后需重装): " + ", ".join(diffs[:3])))
        else:
            checks.append((name, True, ""))

    # commands:逐文件,只比对已安装过的
    diffs, seen = [], False
    for f in sorted((ROOT / "commands").glob("*.md")):
        g = home / "commands" / f.name
        if g.exists():
            seen = True
            if _sha(f) != _sha(g):
                diffs.append(f.name)
    if not seen:
        checks.append(("commands 安装副本同步", True, "未安装(跳过)"))
    else:
        checks.append(("commands 安装副本同步", not diffs,
                       (f"{len(diffs)} 个命令不同步: " + ", ".join(diffs)) if diffs else ""))
    return checks


def watched() -> tuple[list[str], str | None]:
    for name in ("watched_projects.txt", "watched_projects.example.txt"):
        f = ROOT / name
        if f.exists():
            paths = [l.strip() for l in f.read_text(encoding="utf-8").splitlines()
                     if l.strip() and not l.strip().startswith("#")]
            return paths, name
    return [], None


def review_due() -> tuple[bool, int | None]:
    if not REVIEW_MARKER.exists():
        return True, None
    try:
        last = datetime.strptime(REVIEW_MARKER.read_text(encoding="utf-8").strip()[:10], "%Y-%m-%d")
        days = (datetime.now() - last).days
        return days >= REVIEW_DAYS, days
    except Exception:
        return True, None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    bar = "=" * 64
    print(bar + f"\n  handoff-pack Guardian — 自检 + 项目校对\n  {datetime.now():%Y-%m-%d %H:%M}\n" + bar)

    print("\n[1] 工具包自检(稳固性优先)")
    st = selftest() + install_drift()
    all_ok = all(ok for _, ok, _ in st)
    for name, ok, note in st:
        print(f"    {'OK ' if ok else 'FAIL'} {name}{('  · ' + note) if note else ''}")
    print(f"    → {'全部通过 ✓' if all_ok else '⚠ 有失败:先修工具包再做别的!'}")

    print("\n[2] 被看护项目校对(是否仍守 handoff 交接包)")
    paths, src = watched()
    if not paths:
        print("    (无项目;复制 watched_projects.example.txt → watched_projects.txt 并填路径)")
    worst = "LOW"
    for p in paths:
        a = run_audit(p)
        if "error" in a:
            print(f"    ?  {Path(p).name}: 审计出错 {a['error']}"); continue
        risk, score, n = a.get("risk"), a.get("score"), len(a.get("findings", []))
        icon = {"LOW": "OK ", "MEDIUM": "MED", "HIGH": "HIGH"}.get(risk, "?")
        if risk == "HIGH" or (risk == "MEDIUM" and worst != "HIGH"):
            worst = risk
        print(f"    {icon} {Path(p).name}: {risk} (score={score}, {n} findings)")
        for f in a.get("findings", [])[:3]:
            print(f"          - [{f['severity']}] {f['title']}")

    print("\n[3] 方法论刷新(定期 search 新方案)")
    due, days = review_due()
    if due:
        print(f"    ⚠ 该刷新了(距上次 {days if days is not None else '从未记录'} 天 ≥ {REVIEW_DAYS})→ 跑 /toolkit-refresh")
    else:
        print(f"    OK 最近已复核(距今 {days} 天 < {REVIEW_DAYS})")

    print("\n" + bar)
    print("  下一步:自检 FAIL→先修工具包 | 项目 HIGH/MED→去该项目窗口跑 /handoff | 方法论到期→/toolkit-refresh")
    print(bar)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
