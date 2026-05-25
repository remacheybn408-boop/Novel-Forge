#!/usr/bin/env python3
"""
novel.py — Novel Pipeline Write Engine CLI v0.5.0

Top-level entry point wrapping chapter_pipeline, doctor, and report tools.

Usage:
  python novel.py status              Run environment diagnostics
  python novel.py demo                Run demo (pre for chapter 1)
  python novel.py report              Show most recent guard reports
  python novel.py guards              List registered guards and status
  python novel.py check <file>        Run v0.5.0 guards on a chapter file
"""

import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SRC_GUARDS_DIR = PROJECT_ROOT / "src" / "guards"

# Ensure scripts dir is importable
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(SRC_GUARDS_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_GUARDS_DIR))


def cmd_status():
    """Run doctor.py for environment diagnostics."""
    print("=" * 60)
    print("  Novel Pipeline - Write Engine v0.5.0")
    print("  Status Check")
    print("=" * 60)
    print()

    try:
        from doctor import main as doctor_main
        return doctor_main()
    except ImportError:
        # Fallback manual check
        print("  Running manual status check...")
        all_ok = True

        # Python version
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        ok = sys.version_info >= (3, 10)
        mark = "OK" if ok else "FAIL"
        print(f"  [{mark}] Python {py_ver}")
        all_ok &= ok

        # config.json
        cfg = PROJECT_ROOT / "config.json"
        ok = cfg.exists()
        mark = "OK" if ok else "MISSING"
        print(f"  [{mark}] config.json")
        all_ok &= ok

        # src/guards/
        ok = (SRC_GUARDS_DIR / "reader_pull_guard.py").exists()
        mark = "OK" if ok else "MISSING"
        print(f"  [{mark}] src/guards/reader_pull_guard.py")
        all_ok &= ok

        ok = (SRC_GUARDS_DIR / "voice_pack_guard.py").exists()
        mark = "OK" if ok else "MISSING"
        print(f"  [{mark}] src/guards/voice_pack_guard.py")
        all_ok &= ok

        ok = (SRC_GUARDS_DIR / "meme_pack_guard.py").exists()
        mark = "OK" if ok else "MISSING"
        print(f"  [{mark}] src/guards/meme_pack_guard.py")
        all_ok &= ok

        # voice_packs
        vp = PROJECT_ROOT / "voice_packs"
        ok = vp.exists()
        mark = "OK" if ok else "MISSING"
        print(f"  [{mark}] voice_packs/ directory")
        all_ok &= ok

        if all_ok:
            print("\n  All checks passed. Ready to write.")
        else:
            print("\n  Some checks failed. Run install.bat first.")

        return 0 if all_ok else 1


def cmd_demo():
    """Run a demo pipeline check."""
    print("=" * 60)
    print("  Novel Pipeline - Write Engine v0.5.0")
    print("  Demo Run")
    print("=" * 60)
    print()

    # Check config
    cfg_path = PROJECT_ROOT / "config.json"
    if not cfg_path.exists():
        print("[ERROR] config.json not found. Run install.bat first.")
        return 1

    # Try running pre for chapter 1
    print("[STEP 1] Running pre-write gate for chapter 1...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "pre", "1",
             "--config", str(cfg_path), "--novel-slug", "demo_novel", "--volume-no", "1"],
            cwd=str(PROJECT_ROOT),
            capture_output=False,
            timeout=120,
        )
        print(f"\n  Pre-write gate exit code: {result.returncode}")
    except FileNotFoundError:
        print("  [WARN] chapter_pipeline.py not found, skipping pre gate.")
    except Exception as e:
        print(f"  [WARN] Pre-write gate error: {e}")

    # Check for chapter file
    chapter_dir = PROJECT_ROOT / "novels" / "demo_novel" / "第01卷"
    chapter_files = []
    if chapter_dir.exists():
        chapter_files = list(chapter_dir.glob("第1章*.txt"))

    if chapter_files:
        print(f"\n[STEP 2] Found chapter file: {chapter_files[0].name}")
        print("  Run 'python novel.py check' to run v0.5.0 guards on it.")
    else:
        print(f"\n[STEP 2] No chapter file found in {chapter_dir}")
        print("  Create a chapter TXT and run chapter_pipeline.py post to process it.")

    # Run test suite
    print("\n[STEP 3] Running guard validation tests...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(PROJECT_ROOT / "tests"), "-q", "--tb=short"],
            cwd=str(PROJECT_ROOT),
            capture_output=False,
            timeout=180,
        )
    except Exception as e:
        print(f"  [WARN] Test run error: {e}")

    print("\n" + "=" * 60)
    print("  Demo complete.")
    print("=" * 60)
    return 0


def cmd_report():
    """Show most recent guard reports and exports."""
    print("=" * 60)
    print("  Novel Pipeline - Write Engine v0.5.0")
    print("  Reports")
    print("=" * 60)
    print()

    reports_dir = PROJECT_ROOT / "exports" / "reports"
    if not reports_dir.exists():
        print("  No reports directory found.")
        print(f"  Expected: {reports_dir}")
        return 0

    # Find all report files
    all_reports = sorted(reports_dir.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not all_reports:
        print("  No report files found.")
        return 0

    print(f"  Found {len(all_reports)} report files in {reports_dir}")
    print()

    # Show the 10 most recent
    for i, rp in enumerate(all_reports[:10]):
        mtime = datetime.fromtimestamp(rp.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        size = rp.stat().st_size
        size_str = f"{size:,}B" if size < 1024 else f"{size/1024:.1f}KB"

        # Try to read the status from the report
        status = "?"
        try:
            data = json.loads(rp.read_text(encoding="utf-8"))
            status = data.get("status", data.get("overall_status", "?"))
        except Exception:
            pass

        rel_path = rp.relative_to(reports_dir)
        print(f"  [{status:5s}] {mtime}  {size_str:>8s}  {rel_path}")

    if len(all_reports) > 10:
        print(f"\n  ... and {len(all_reports) - 10} more reports.")

    print()
    return 0


def cmd_guards():
    """List registered guards and their status."""
    print("=" * 60)
    print("  Novel Pipeline - Write Engine v0.5.0")
    print("  Guard Registry")
    print("=" * 60)
    print()

    # Core guards from registry
    print("  [Core Guards — scripts/]")
    try:
        from guard_registry import GUARD_RUNNERS, GUARD_LEVELS, MODE_GUARDS
        for name in sorted(GUARD_RUNNERS):
            level = GUARD_LEVELS.get(name, "?")
            print(f"    L{level} {name}")
    except ImportError:
        print("    (guard_registry not importable)")

    print()
    print("  [v0.5.0 Guards — src/guards/]")
    v050_guards = ["reader_pull_guard", "voice_pack_guard", "meme_pack_guard"]
    for name in v050_guards:
        fp = SRC_GUARDS_DIR / f"{name}.py"
        exists = "OK" if fp.exists() else "MISSING"
        print(f"    [{exists}] {name}")

    print()
    print("  [Guard Modes]")
    try:
        from guard_registry import MODE_GUARDS
        for mode, guards in MODE_GUARDS.items():
            print(f"    {mode}: {len(guards)} guards")
    except ImportError:
        pass

    print()
    return 0


def cmd_check(file_path: str):
    """Run v0.5.0 guards on a chapter file."""
    fp = Path(file_path)
    if not fp.exists():
        print(f"[ERROR] File not found: {fp}")
        return 1

    content = fp.read_text(encoding="utf-8")
    print("=" * 60)
    print(f"  Checking: {fp.name}")
    print("=" * 60)
    print()

    # Reader pull guard
    print("--- reader_pull_guard ---")
    try:
        from src.guards.reader_pull_guard import run_reader_pull_check
        rp_report = run_reader_pull_check(content, chapter_no=1)
        status = rp_report["status"]
        issues = len(rp_report.get("issues", []))
        print(f"  Status: {status} ({issues} issues)")
        if issues:
            for iss in rp_report.get("issues", [])[:5]:
                print(f"    [{iss['code']}] {iss['message'][:80]}")
    except ImportError as e:
        print(f"  [WARN] reader_pull_guard not available: {e}")
    except Exception as e:
        print(f"  [WARN] reader_pull_guard error: {e}")

    print()

    # Voice pack guard
    print("--- voice_pack_guard ---")
    try:
        from src.guards.voice_pack_guard import run_voice_pack_check
        vp_dir = str(PROJECT_ROOT / "voice_packs")
        vp_report = run_voice_pack_check(content, chapter_no=1, voice_packs_dir=vp_dir)
        status = vp_report["status"]
        issues = len(vp_report.get("issues", []))
        print(f"  Status: {status} ({issues} issues)")
        extra = vp_report.get("extra_checks", {})
        for check_name, check_issues in extra.items():
            if check_issues:
                print(f"    {check_name}: {len(check_issues)} issues")
    except ImportError as e:
        print(f"  [WARN] voice_pack_guard not available: {e}")
    except Exception as e:
        print(f"  [WARN] voice_pack_guard error: {e}")

    print()

    # Meme pack guard
    print("--- meme_pack_guard ---")
    try:
        from src.guards.meme_pack_guard import run_meme_pack_check
        mp_dir = str(PROJECT_ROOT / "voice_packs")
        mp_report = run_meme_pack_check(content, chapter_no=1, meme_packs_dir=mp_dir)
        status = mp_report["status"]
        issues = len(mp_report.get("issues", []))
        print(f"  Status: {status} ({issues} issues)")
        for iss in mp_report.get("issues", [])[:5]:
            print(f"    [{iss['code']}] {iss['message'][:80]}")
    except ImportError as e:
        print(f"  [WARN] meme_pack_guard not available: {e}")
    except Exception as e:
        print(f"  [WARN] meme_pack_guard error: {e}")

    print()
    print("=" * 60)
    return 0


def cmd_init():
    """Initialize project: create directories, copy config, init DB."""
    print("=" * 60)
    print("  Novel Pipeline - Write Engine v0.5.0")
    print("  Initialize Project")
    print("=" * 60)
    print()

    # Check for config.json
    cfg = PROJECT_ROOT / "config.json"
    if not cfg.exists():
        example = PROJECT_ROOT / "config.example.json"
        if example.exists():
            import shutil
            shutil.copy(example, cfg)
            print("  [OK] config.json created from config.example.json")
        else:
            print("  [WARN] config.example.json not found")
    else:
        print("  [OK] config.json already exists")

    # Init DB
    print()
    print("  Initializing database...")
    try:
        from init_db import init_db as db_init
        import json as _json
        with open(cfg, encoding="utf-8") as f:
            config = _json.load(f)
        db_path = config.get("db_path", str(PROJECT_ROOT / "novel_memory.db"))
        schema = PROJECT_ROOT / "database" / "schema.sql"
        if not schema.exists():
            print("  [WARN] schema.sql not found, skipping DB init")
        else:
            # Ensure db directory exists
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            db_init(str(db_path), str(schema))
            print(f"  [OK] Database initialized: {db_path}")
    except Exception as e:
        print(f"  [WARN] DB init error: {e}")

    # Create directories
    dirs = ["outputs/task_cards", "outputs/reviews", "exports", "reports", "tmp"]
    for d in dirs:
        p = PROJECT_ROOT / d
        p.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] Directory created: {d}")

    print()
    print("  Project initialized. Run 'python novel.py demo' to test.")
    return 0


def cmd_pre(chapter_no: str = None):
    """Run pre-write gate for a chapter."""
    cfg = PROJECT_ROOT / "config.json"
    if not chapter_no:
        print("Usage: python novel.py pre <chapter_no>")
        return 1
    print(f"  Running pre-write gate for chapter {chapter_no}...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "pre", str(chapter_no),
             "--config", str(cfg)],
            cwd=str(PROJECT_ROOT), timeout=120)
        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


def cmd_post(chapter_no: str = None):
    """Post-write: run guards and ingest chapter."""
    cfg = PROJECT_ROOT / "config.json"
    if not chapter_no:
        print("Usage: python novel.py post <chapter_no>")
        return 1
    print(f"  Running post-write guards for chapter {chapter_no}...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "post", str(chapter_no),
             "--config", str(cfg)],
            cwd=str(PROJECT_ROOT), timeout=300)
        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


def cmd_review(chapter_no: str = None):
    """Run guard review on a chapter."""
    cfg = PROJECT_ROOT / "config.json"
    if not chapter_no:
        print("Usage: python novel.py review <chapter_no>")
        return 1
    print(f"  Running review for chapter {chapter_no}...")
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "review", str(chapter_no),
             "--config", str(cfg)],
            cwd=str(PROJECT_ROOT), timeout=300)
        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


def cmd_export(slug: str = None):
    """Export novel to a single file."""
    if not slug:
        print("Usage: python novel.py export --slug <novel_slug> [--format txt|md]")
        return 1
    print(f"  Exporting novel '{slug}'...")
    try:
        import subprocess
        args = [sys.executable, str(SCRIPTS_DIR / "export_novel.py"),
                "--slug", slug, "--format", "md",
                "--output", str(PROJECT_ROOT / "exports" / f"{slug}_full.md")]
        result = subprocess.run(args, cwd=str(PROJECT_ROOT), timeout=60)
        if result.returncode == 0:
            print(f"  [OK] Exported to exports/{slug}_full.md")
        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Novel Pipeline - Write Engine v0.5.0 CLI",
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # status
    sub.add_parser("status", help="Run environment diagnostics")
    # demo
    sub.add_parser("demo", help="Run demo pipeline")
    # init
    sub.add_parser("init", help="Initialize project directories and database")
    # pre
    p_pre = sub.add_parser("pre", help="Generate pre-write task card")
    p_pre.add_argument("chapter_no", nargs="?", help="Chapter number")
    # post
    p_post = sub.add_parser("post", help="Post-write: run guards and ingest")
    p_post.add_argument("chapter_no", nargs="?", help="Chapter number")
    # review
    p_review = sub.add_parser("review", help="Run guard review on a chapter")
    p_review.add_argument("chapter_no", nargs="?", help="Chapter number")
    # report
    sub.add_parser("report", help="Show recent guard reports")
    # guards
    sub.add_parser("guards", help="List registered guards")
    # check
    p_check = sub.add_parser("check", help="Run v0.5.0 guards on a chapter file")
    p_check.add_argument("file_path", help="Path to chapter TXT file")
    # export
    p_export = sub.add_parser("export", help="Export novel to single file")
    p_export.add_argument("--slug", help="Novel slug to export")
    p_export.add_argument("--format", default="md", choices=["txt", "md"])

    args = parser.parse_args()

    if args.command == "status":
        sys.exit(cmd_status())
    elif args.command == "demo":
        sys.exit(cmd_demo())
    elif args.command == "init":
        sys.exit(cmd_init())
    elif args.command == "pre":
        sys.exit(cmd_pre(getattr(args, "chapter_no", None)))
    elif args.command == "post":
        sys.exit(cmd_post(getattr(args, "chapter_no", None)))
    elif args.command == "review":
        sys.exit(cmd_review(getattr(args, "chapter_no", None)))
    elif args.command == "report":
        sys.exit(cmd_report())
    elif args.command == "guards":
        sys.exit(cmd_guards())
    elif args.command == "check":
        sys.exit(cmd_check(args.file_path))
    elif args.command == "export":
        sys.exit(cmd_export(args.slug))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
