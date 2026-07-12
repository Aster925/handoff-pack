#!/usr/bin/env python3
"""
drift_audit.py — 项目漂移风险审计 & 交接文件脚手架
Project drift-risk audit & handoff-packet scaffolder.

Part of the "handoff-pack" Claude Code skill.
零依赖 (stdlib only)，跨平台 (Windows / macOS / Linux)。

用法 / Usage
-----------
    # 审计当前项目，打印可读报告 (audit current project, human report)
    python drift_audit.py audit [PROJECT_DIR]

    # 输出机器可读 JSON (给 skill / agent 解析)
    python drift_audit.py audit [PROJECT_DIR] --json

    # 把缺失的交接模板拷进目标项目 (scaffold missing handoff files)
    python drift_audit.py scaffold [PROJECT_DIR] [--force]

退出码 / Exit codes (audit): 0 = low risk, 1 = medium, 2 = high.
脚本只做"确定性"检查 (deterministic checks)；理解代码意图、填充模板内容是 agent 的工作。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path

# 尽量用 UTF-8 输出，避免 Windows 控制台中文乱码
try:  # pragma: no cover - environment dependent
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = SCRIPT_DIR.parent / "templates"

# template filename -> destination filename in the target project
SCAFFOLD_MAP = {
    "AGENTS.md": "AGENTS.md",
    "CLAUDE.md": "CLAUDE.md",
    "feature_list.json": "feature_list.json",
    "PROGRESS.md": "PROGRESS.md",
    "BACKLOG.md": "BACKLOG.md",
    "HANDOFF.md": "HANDOFF.md",
    "init.sh": "init.sh",
    "init.ps1": "init.ps1",
    "gitattributes": ".gitattributes",
    "env.example": ".env.example",
}

# directories we never descend into when scanning source
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__",
    "dist", "build", ".next", ".nuxt", "target", ".idea", ".vscode",
    "vendor", ".mypy_cache", ".pytest_cache", ".tox", "site-packages",
}
# source extensions we scan for hardcoded paths
SOURCE_EXT = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".java", ".rs",
    ".sh", ".ps1", ".env", ".cfg", ".ini", ".toml", ".yaml", ".yml",
    ".json", ".c", ".cpp", ".h", ".cs", ".php",
}

SEV_POINTS = {"high": 5, "medium": 3, "low": 1, "info": 0}


@dataclass
class Finding:
    category: str       # what area: artifacts / deps / secrets / portability / git
    severity: str       # high / medium / low / info
    title: str          # short headline
    detail: str         # what was observed
    fix: str            # concrete remediation


@dataclass
class Report:
    project: str
    findings: list = field(default_factory=list)

    def add(self, **kw):
        self.findings.append(Finding(**kw))

    @property
    def score(self) -> int:
        return sum(SEV_POINTS.get(f.severity, 0) for f in self.findings)

    @property
    def risk(self) -> str:
        s = self.score
        if s >= 10:
            return "HIGH"
        if s >= 4:
            return "MEDIUM"
        return "LOW"

    @property
    def exit_code(self) -> int:
        return {"LOW": 0, "MEDIUM": 1, "HIGH": 2}[self.risk]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def run_git(root: Path, *args: str) -> tuple[int, str]:
    """Run a git command; return (returncode, stdout). Degrade gracefully."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        return proc.returncode, (proc.stdout or "")
    except (FileNotFoundError, OSError):
        return 127, ""


def is_git_repo(root: Path) -> bool:
    code, _ = run_git(root, "rev-parse", "--is-inside-work-tree")
    return code == 0


def git_tracked(root: Path, pattern: str) -> list[str]:
    code, out = run_git(root, "ls-files", pattern)
    if code != 0:
        return []
    return [ln for ln in out.splitlines() if ln.strip()]


def iter_source_files(root: Path, limit: int = 4000):
    """Yield source files, skipping vendored/build dirs. Capped for speed."""
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git")]
        for name in filenames:
            ext = Path(name).suffix.lower()
            if ext in SOURCE_EXT:
                yield Path(dirpath) / name
                count += 1
                if count >= limit:
                    return


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


# progress-log filename candidates, in priority order (root + common doc dirs)
PROGRESS_CANDIDATES = [
    "PROGRESS.md", "claude-progress.txt", "PROGRESS.txt",
    "docs/PROGRESS.md", "docs/progress.md", ".claude/PROGRESS.md",
]


def find_progress(root: Path) -> Path | None:
    for rel in PROGRESS_CANDIDATES:
        p = root / rel
        if p.exists():
            return p
    return None


# --------------------------------------------------------------------------- #
# checks
# --------------------------------------------------------------------------- #
def check_artifacts(root: Path, rep: Report) -> None:
    """Are the condensed-state handoff files present?"""
    has_agents = (root / "AGENTS.md").exists()
    has_claude = (root / "CLAUDE.md").exists()
    progress = find_progress(root)
    has_features = (root / "feature_list.json").exists()
    has_init = (root / "init.sh").exists() or (root / "init.ps1").exists()

    if not has_agents and not has_claude:
        rep.add(category="artifacts", severity="high",
                title="无上下文文件 / No agent context file",
                detail="既没有 AGENTS.md 也没有 CLAUDE.md —— 新 session 只能从裸代码逆向意图。",
                fix="运行 `scaffold` 生成 AGENTS.md(主)+ CLAUDE.md(指针),再让 agent 填充真实内容。")
    elif not has_agents:
        rep.add(category="artifacts", severity="medium",
                title="缺 AGENTS.md / Missing portable context",
                detail="有 CLAUDE.md 但无 AGENTS.md;非 Claude 工具 (Cursor/Copilot/Gemini) 读不到上下文。",
                fix="生成 AGENTS.md 作为唯一真相来源,CLAUDE.md 改为 @AGENTS.md 指针。")

    if progress is None:
        rep.add(category="artifacts", severity="high",
                title="无进度日志 / No progress log",
                detail="没有 PROGRESS.md —— 隐性进度('做到哪了/下一步')无处落盘。",
                fix="生成 PROGRESS.md,每个 session 结束追加一条记录。")

    if not has_features:
        rep.add(category="artifacts", severity="medium",
                title="无功能清单 / No feature checklist",
                detail="没有 feature_list.json —— agent 容易过早宣布'做完了'。",
                fix="生成 feature_list.json,所有功能初始 passes:false,只能改 passes 字段。")

    if not has_init:
        rep.add(category="artifacts", severity="medium",
                title="无一键启动脚本 / No init script",
                detail="没有 init.sh / init.ps1 —— 换机器后不知道怎么重建环境、怎么跑。",
                fix="生成 init.sh + init.ps1,从干净 clone 即可一键重建。")


def check_progress_freshness(root: Path, rep: Report) -> None:
    """Is the progress log stale relative to recent commits?"""
    progress = find_progress(root)
    if progress is None or not is_git_repo(root):
        return
    rel = progress.relative_to(root).as_posix()
    # commits that touched code since progress file was last committed
    code, out = run_git(root, "log", "-1", "--format=%ct", "--", rel)
    if code != 0 or not out.strip():
        return
    try:
        progress_commit_ts = int(out.strip())
    except ValueError:
        return
    code, out = run_git(root, "log", "-1", "--format=%ct")
    if code != 0 or not out.strip():
        return
    try:
        head_ts = int(out.strip())
    except ValueError:
        return
    # count commits after the progress file was last updated
    code, out = run_git(root, "rev-list", "--count", f"--since=@{progress_commit_ts + 1}", "HEAD")
    behind = out.strip() if code == 0 else "?"
    if head_ts - progress_commit_ts > 0 and behind not in ("0", "?", ""):
        rep.add(category="artifacts", severity="medium",
                title="进度日志过期 / Stale progress log",
                detail=f"{progress.name} 之后还有约 {behind} 个 commit,日志可能落后于代码。",
                fix="结束 session 前更新 PROGRESS.md,使其反映最新进度。")


BACKLOG_CANDIDATES = ["BACKLOG.md", "docs/BACKLOG.md"]
# 叙事日志超过此字符数后,"通读"开始不可靠(Read 单次 ~25k tokens),需要账本兜底
LEDGER_PROGRESS_CHARS = 30_000


def check_backlog_ledger(root: Path, rep: Report) -> None:
    """账本与日志分离:超长 PROGRESS 而无 BACKLOG 账本 = "只截开头"漂移温床。"""
    progress = find_progress(root)
    if progress is None:
        return
    try:
        size = len(progress.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return
    has_backlog = any((root / rel).exists() for rel in BACKLOG_CANDIDATES)
    if size >= LEDGER_PROGRESS_CHARS and not has_backlog:
        rep.add(category="artifacts", severity="medium",
                title="日志超长且无待办账本 / Long log, no backlog ledger",
                detail=f"{progress.name} 已 {size:,} 字符 —— 超过单次可读上限后'通读'物理不可执行,"
                       "「下一步/待办」散落正文必被截断遗漏,新 session 会只读开头就自行开工。",
                fix="账本与日志分离:scaffold 生成 BACKLOG.md(<100 行:OPEN/常设裁定/CLOSED),"
                    "待办只登记账本;宣布「完成/无缺口」前 OPEN 须清空。")


def check_dependencies(root: Path, rep: Report) -> None:
    """Lockfiles + pinned versions."""
    py_manifest = (root / "requirements.txt").exists() or (root / "pyproject.toml").exists()
    node_manifest = (root / "package.json").exists()

    if py_manifest:
        has_lock = any((root / f).exists() for f in
                       ["uv.lock", "poetry.lock", "Pipfile.lock", "requirements.lock"])
        req = root / "requirements.txt"
        if req.exists():
            lines = [l.strip() for l in read_text(req).splitlines()
                     if l.strip() and not l.strip().startswith("#")]
            pinned = [l for l in lines if "==" in l]
            if lines and len(pinned) < len(lines) and not has_lock:
                rep.add(category="deps", severity="high",
                        title="依赖未锁版本 / Unpinned dependencies",
                        detail=f"requirements.txt 中 {len(lines) - len(pinned)}/{len(lines)} 行没有 == 锁定。",
                        fix="用 `==` 锁版本,或改用 uv/poetry 生成 lockfile —— 否则两台机器装出不同版本。")
        elif not has_lock:
            rep.add(category="deps", severity="medium",
                    title="无依赖锁文件 / No lockfile",
                    detail="有 pyproject.toml 但没有 uv.lock / poetry.lock。",
                    fix="生成并提交 lockfile (uv lock / poetry lock),保证可复现。")

    if node_manifest:
        has_lock = any((root / f).exists() for f in
                       ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb"])
        if not has_lock:
            rep.add(category="deps", severity="high",
                    title="无 Node 锁文件 / No Node lockfile",
                    detail="有 package.json 但没有 package-lock / yarn.lock / pnpm-lock。",
                    fix="提交锁文件 —— 否则 `npm install` 在另一台机器拉到不同版本。")


def check_secrets_and_artifacts(root: Path, rep: Report) -> None:
    """.env safety + committed build artifacts."""
    git = is_git_repo(root)
    gitignore = read_text(root / ".gitignore") if (root / ".gitignore").exists() else ""

    if (root / ".env").exists():
        tracked = git_tracked(root, ".env") if git else []
        if tracked:
            rep.add(category="secrets", severity="high",
                    title=".env 被 git 跟踪 / Secrets tracked",
                    detail="真实 .env 进了版本控制 —— 密钥泄露风险,且迁移时易冲突。",
                    fix="`git rm --cached .env`,把 .env 加入 .gitignore,只提交 .env.example(仅键名)。")
        elif ".env" not in gitignore:
            rep.add(category="secrets", severity="medium",
                    title=".env 未被忽略 / .env not ignored",
                    detail="存在 .env 但 .gitignore 没排除它,可能被误提交。",
                    fix="在 .gitignore 加入 `.env`。")
        if not (root / ".env.example").exists():
            rep.add(category="secrets", severity="medium",
                    title="无 .env.example / No env template",
                    detail="有 .env 但没有 .env.example —— 新机器不知道需要哪些环境变量。",
                    fix="生成 .env.example,只含键名(不含真实值)并提交。")

    if git:
        for junk in [".venv", "venv", "node_modules"]:
            if git_tracked(root, junk + "/"):
                rep.add(category="portability", severity="high",
                        title=f"{junk} 被提交 / Build dir committed",
                        detail=f"{junk}/ 进了 git —— 含平台特定二进制和绝对路径,不可移植。",
                        fix=f"`git rm -r --cached {junk}` 并加入 .gitignore;用 init 脚本在新机重建。")


def check_portability(root: Path, rep: Report) -> None:
    """Line endings + hardcoded absolute paths."""
    gitattr = read_text(root / ".gitattributes") if (root / ".gitattributes").exists() else ""
    if "eol=" not in gitattr and "text=auto" not in gitattr:
        rep.add(category="portability", severity="low",
                title="无换行符规范 / No EOL policy",
                detail="缺少 .gitattributes 的 eol 设置;Windows(CRLF) ↔ macOS/Linux(LF) 会造成噪声 diff。",
                fix="提交 .gitattributes 含 `* text=auto eol=lf`。")

    # hardcoded absolute paths.
    # Windows: drive letter + >=2 path segments, so "e:\n- text" (a \n escape) won't match.
    patterns = [
        (re.compile(r"[A-Za-z]:(?:[\\/][\w .\-]+){2,}"), "Windows 绝对路径"),
        (re.compile(r"/Users/[\w.\-]+(?:/[\w .\-]+)*"), "macOS home 绝对路径"),
        (re.compile(r"/home/[\w.\-]+(?:/[\w .\-]+)*"), "Linux home 绝对路径"),
    ]
    # backslash-escape signature (\n- , \t", ...): escape letter then a non-word char.
    escape_rx = re.compile(r"\\[ntrbf0](?![\w])")
    hits: list[str] = []
    for f in iter_source_files(root):
        text = read_text(f)
        if not text:
            continue
        for rx, label in patterns:
            for m in rx.finditer(text):
                frag = m.group(0)
                # skip false positives: example placeholders and string escapes (\n, \t...)
                if len(frag) > 6 and "example" not in frag.lower() and not escape_rx.search(frag):
                    rel = f.relative_to(root)
                    hits.append(f"{rel}: {frag[:60]}")
                    break
        if len(hits) >= 12:
            break
    if hits:
        rep.add(category="portability", severity="medium",
                title=f"硬编码绝对路径 / Hardcoded paths ({len(hits)}+)",
                detail="发现写死的绝对路径,迁移到另一台机器/OS 会断:\n    - " + "\n    - ".join(hits[:8]),
                fix="改用相对路径 / pathlib / 环境变量;路径不要跨平台写死。")


def check_git_state(root: Path, rep: Report) -> None:
    if not is_git_repo(root):
        rep.add(category="git", severity="high",
                title="不是 git 仓库 / Not a git repo",
                detail="没有 git 历史 —— 无法回退到能跑的状态,迁移只能靠拷贝文件。",
                fix="`git init` 并提交;git history 是最重要的交接产物之一。")
        return
    code, out = run_git(root, "status", "--porcelain")
    if code == 0 and out.strip():
        n = len([l for l in out.splitlines() if l.strip()])
        rep.add(category="git", severity="low",
                title=f"有未提交改动 / Uncommitted changes ({n})",
                detail="工作区有未提交的修改;交接/迁移前未落盘的改动会丢。",
                fix="交接前 commit 干净状态,或在 HANDOFF.md 明确记录未提交项。")


CHECKS = [
    check_artifacts,
    check_progress_freshness,
    check_backlog_ledger,
    check_dependencies,
    check_secrets_and_artifacts,
    check_portability,
    check_git_state,
]


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def do_audit(root: Path, as_json: bool) -> int:
    rep = Report(project=str(root))
    for check in CHECKS:
        try:
            check(root, rep)
        except Exception as e:  # never let one check kill the whole run
            rep.add(category="internal", severity="info",
                    title=f"check {check.__name__} failed",
                    detail=str(e), fix="report this as a bug")

    if as_json:
        payload = {
            "project": rep.project,
            "risk": rep.risk,
            "score": rep.score,
            "exit_code": rep.exit_code,
            "findings": [asdict(f) for f in rep.findings],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return rep.exit_code

    print_report(rep)
    return rep.exit_code


def print_report(rep: Report) -> None:
    bar = "=" * 64
    print(bar)
    print(f"  漂移风险审计 / Drift-risk audit")
    print(f"  项目 / Project : {rep.project}")
    print(f"  风险 / Risk    : {rep.risk}   (score={rep.score})")
    print(bar)

    if not rep.findings:
        print("\n  ✔ 未发现明显漂移信号 —— 交接产物齐备。")
        print("    No obvious drift signals; handoff artifacts look complete.\n")
        return

    order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    findings = sorted(rep.findings, key=lambda f: order.get(f.severity, 9))
    icon = {"high": "■ HIGH ", "medium": "▲ MED  ", "low": "· LOW  ", "info": "  info "}
    for i, f in enumerate(findings, 1):
        print(f"\n[{i}] {icon.get(f.severity, '')} ({f.category})  {f.title}")
        print(f"    现象 / What: {f.detail}")
        print(f"    修复 / Fix : {f.fix}")
    print()
    print(bar)
    counts = {}
    for f in rep.findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    summary = ", ".join(f"{k}={v}" for k, v in
                        sorted(counts.items(), key=lambda kv: order.get(kv[0], 9)))
    print(f"  共 {len(rep.findings)} 条 / {summary}")
    print(f"  下一步 / Next: 让 agent 按 fix 修复,然后跑 `scaffold` 补齐缺失文件并填充内容。")
    print(bar)


def do_scaffold(root: Path, force: bool) -> int:
    if not TEMPLATES_DIR.is_dir():
        print(f"ERROR: templates dir not found: {TEMPLATES_DIR}", file=sys.stderr)
        return 2
    created, skipped = [], []
    for tpl_name, dest_name in SCAFFOLD_MAP.items():
        src = TEMPLATES_DIR / tpl_name
        dest = root / dest_name
        if not src.exists():
            continue
        if dest.exists() and not force:
            skipped.append(dest_name)
            continue
        shutil.copyfile(src, dest)
        created.append(dest_name)

    print("脚手架 / Scaffold:")
    if created:
        print("  + 已创建 / created:")
        for n in created:
            print(f"      {n}")
    if skipped:
        print("  = 已存在,跳过 / skipped (use --force to overwrite):")
        for n in skipped:
            print(f"      {n}")
    print("\n模板已就位,但内容仍是占位符 (TODO)。")
    print("下一步:让 agent 阅读代码,把 AGENTS.md / feature_list.json 等填成真实内容。")
    print("Next: have the agent read the code and replace the TODO placeholders with real content.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="项目漂移审计 & 交接脚手架 / drift audit & handoff scaffolder")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_audit = sub.add_parser("audit", help="审计漂移风险 / audit drift risk")
    p_audit.add_argument("path", nargs="?", default=".", help="项目目录 / project dir")
    p_audit.add_argument("--json", action="store_true", help="输出 JSON / machine-readable output")

    p_scaf = sub.add_parser("scaffold", help="拷贝缺失模板 / copy missing templates")
    p_scaf.add_argument("path", nargs="?", default=".", help="项目目录 / project dir")
    p_scaf.add_argument("--force", action="store_true", help="覆盖已存在文件 / overwrite existing")

    args = parser.parse_args(argv)
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    if args.cmd == "audit":
        return do_audit(root, args.json)
    if args.cmd == "scaffold":
        return do_scaffold(root, args.force)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
