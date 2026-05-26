#!/usr/bin/env python3
"""
novel.py — Novel Pipeline Write Engine CLI v0.6.0

Top-level entry point wrapping chapter_pipeline, doctor, and report tools.

Usage:
  python novel.py status              Run environment diagnostics
  python novel.py demo                Run demo (pre for chapter 1)
  python novel.py report              Show most recent guard reports
  python novel.py guards              List registered guards and status
  python novel.py check <file>        Run v0.5.0 guards on a chapter file
"""

import sys
from version import get_version
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

from config_utils import normalize_config, load_json_config, resolve_path


def _load_project_config() -> dict:
    """Load config.json/config.example.json using the shared compatibility layer."""
    cfg_path = PROJECT_ROOT / "config.json"
    if cfg_path.exists():
        return load_json_config(cfg_path, PROJECT_ROOT)
    return load_json_config(PROJECT_ROOT / "config.example.json", PROJECT_ROOT)


def _cfg_path(key: str, default: str) -> Path:
    cfg = _load_project_config()
    return resolve_path(PROJECT_ROOT, cfg.get(key, default))


def cmd_status():
    """Run doctor.py for environment diagnostics."""
    print("=" * 60)
    v = get_version()
    print(f"  Novel Pipeline - Write Engine {v}")
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
    """Create demo_novel, run pre -> post, then show report location."""
    print("=" * 60)
    v = get_version()
    print(f"  Novel Pipeline - Write Engine {v}")
    print("  Demo Pipeline")
    print("=" * 60)
    print()

    cfg_path = PROJECT_ROOT / "config.json"
    if not cfg_path.exists():
        print("[STEP 1] Initializing project...")
        cmd_init()
        print()
    else:
        print("[STEP 1] config.json found.")

    cfg_data = _load_project_config()
    db_path = resolve_path(PROJECT_ROOT, cfg_data.get("db_path", "./data/novel_memory.db"))
    if not db_path.exists():
        print("  Database missing, initializing now...")
        cmd_init()
        cfg_data = _load_project_config()
        db_path = resolve_path(PROJECT_ROOT, cfg_data.get("db_path", "./data/novel_memory.db"))

    slug = cfg_data.get("default_novel_slug", "demo_novel")
    title = cfg_data.get("default_novel_title", "Demo Novel")
    novels_root = resolve_path(PROJECT_ROOT, cfg_data.get("novels_root", "./novels"))
    vol_dir = novels_root / slug / "第01卷"
    vol_dir.mkdir(parents=True, exist_ok=True)

    print("\n[STEP 2] Creating demo chapter...")
    paragraphs = [
        "第1章 开篇",
        "清晨的钟声从青云宗山腰传来，像一根细线，把外门弟子从浅睡里一一拽醒。李明远坐在窄床边，先没有急着穿鞋，而是低头看向掌心那枚旧玉佩。玉佩的边缘有一道细裂，裂纹像凝住的水波，三年来从未扩大，也从未消失。",
        "他来到青云宗已经第三年。三年前，他还只是海边渔村里的少年，每天跟着父亲补网、看潮、记风向。那场暴风雨把渔船掀翻时，他以为自己会沉进海底，偏偏胸口的玉佩发出一点冷光，把他推上了岸，也把他推到了修行人的门槛前。",
        "门外传来小石头的声音：\"远哥，王教习让我们提前到练功场，说今日有长老巡视。\"小石头说话总带着一点慌张，像随时准备把自己缩进墙角。他本名石磊，因为个子小，入门又晚，所有人都叫他小石头，只有李明远还会认真叫他一声师弟。",
        "李明远把玉佩塞回衣襟，推门出去。晨雾还没有散，练功场的青砖上凝着水汽，几十名外门弟子已经排成三列。有人在压腿，有人默背心法，也有人趁王教习没到，偷偷用余光打量山道尽头。今日的气氛很不对，连平日爱说笑的赵铁柱都闭着嘴，双手按在膝上，一下一下调整呼吸。",
        "王教习终于来了。他须发皆白，步子却稳，木杖点在砖面上，声声清脆。\"今日大长老巡视外门，谁若在基础功上偷奸耍滑，老夫先罚，戒律堂再罚。\"这句话不重，却让人背脊发紧。外门弟子最怕的不是挨骂，而是被记入戒律堂的黑册，一旦名字落上去，日后进内门几乎无望。",
        "赵铁柱压低声音道：\"明远，你昨晚是不是又练到后半夜？脸色不太对。\"李明远摇摇头，没有解释。他昨夜确实没睡好，但不是因为修炼，而是因为玉佩第一次在无人触碰时自己发热。那股热意顺着胸口往丹田走，像有人在他体内画了一条陌生的经脉路线。",
        "王教习开始点名。每点到一人，便让其演示三式基础剑法。轮到李明远时，周围忽然安静下来。他的修为只是炼气三层，算不上拔尖，可他的剑路总有些古怪，明明用的是最普通的青云十三式，落点却比旁人更准，像每一剑都提前知道风会往哪里吹。",
        "李明远握住木剑，第一式平平推出。剑尖划过雾气，雾线被割开，又在他身后缓慢合拢。第二式转腕时，他胸前玉佩忽然一烫，丹田里的真气不受控制地偏了半寸。只是半寸，木剑却发出一声轻鸣，练功场边的铜铃无风自响。",
        "所有人都愣住了。王教习的眼神骤然锐利，大步走到李明远面前，伸手扣住他的腕脉。李明远只觉得一股外来的灵力沿着手腕探入体内，还没碰到玉佩所在的位置，就被一层冰冷的阻力挡了回去。王教习脸色微变，随即松手，低声道：\"今日之后，你不要一个人去后山。\"",
        "这句话来得突兀，小石头吓得脸都白了。赵铁柱想问，却被王教习一个眼神压回去。李明远心里那点不安终于落成了实物：不是他多想，玉佩真的被人察觉了。更糟的是，察觉的人未必只有王教习。",
        "山道上，三名内门弟子簇拥着一位青袍老者缓缓走来。老者眉目清瘦，袖口绣着戒律堂的玄色云纹，正是外门弟子口中最不愿遇见的大长老。他的目光扫过练功场，最后停在李明远身上，停得比任何人都久。",
        "李明远低下头，手指按住衣襟里的玉佩。玉佩已经恢复冰凉，可那道裂纹里似乎多了一点极淡的金色。它像一只刚睁开的眼睛，在沉默里看着所有人。",
        "大长老没有立刻说话，只是对王教习点了点头。王教习会意，宣布今日晨练改为根骨复测。人群顿时骚动起来。根骨复测一年一次，通常只为筛选升入内门的弟子，绝不会临时提前。李明远听见身后有人倒吸冷气，也听见小石头小声念了一句：\"完了，肯定有人要倒霉。\"",
        "李明远没有回头。他知道那个人很可能就是自己。可他也清楚，若今日退缩，玉佩的秘密未必能保住，自己的路也会被别人安排。三年来，他第一次生出一个明确的念头：他不能再只做外门里那个安静听话的弟子。",
        "铜铃第二次响起时，雾气终于散开。阳光落在练功场中央，也落在大长老面前那块测灵石上。李明远向前一步，掌心贴上冰冷的石面。下一瞬，测灵石深处亮起一道从未在外门出现过的青金色细线，像雷光，也像裂开的命运。",
    ]
    demo_content = "\n\n".join(paragraphs) + "\n"
    chapter_file = vol_dir / "第1章_开篇.txt"
    chapter_file.write_text(demo_content, encoding="utf-8")
    cn_count = sum(1 for c in demo_content if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf')
    print(f"  [OK] {chapter_file.name} ({cn_count} 汉字)")

    outline_file = novels_root / slug / "outline.txt"
    outline_file.write_text(
        "# Demo Novel 大纲\n\n第一卷：初入宗门。第1章：外门晨练，玉佩异动，大长老临时复测根骨。\n",
        encoding="utf-8",
    )
    print(f"  [OK] {outline_file.name}")

    print("\n[STEP 3] Registering demo_novel in database...")
    try:
        import sqlite3
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute("INSERT OR IGNORE INTO novels (slug, title, genre, status) VALUES (?, ?, ?, ?)",
                     (slug, title, cfg_data.get("default_genre", "xianxia"), "writing"))
        novel_id = conn.execute("SELECT id FROM novels WHERE slug=?", (slug,)).fetchone()[0]
        conn.execute("INSERT OR IGNORE INTO volumes (novel_id, volume_no, title) VALUES (?, ?, ?)",
                     (novel_id, 1, "第一卷"))
        conn.commit()
        conn.close()
        print("  [OK] registered")
    except Exception as e:
        print(f"  [ERROR] database registration failed: {e}")
        return 1

    import subprocess as _sp
    print("\n[STEP 4] Running pre-write gate...")
    pre_result = _sp.run([sys.executable, str(PROJECT_ROOT / "novel.py"), "pre", "1", "--slug", slug],
                         cwd=str(PROJECT_ROOT), timeout=180)
    if pre_result.returncode != 0:
        print(f"  [FAIL] pre returned exit code {pre_result.returncode}")
        return pre_result.returncode

    print("\n[STEP 5] Running post-write guards + ingest...")
    post_result = _sp.run([sys.executable, str(PROJECT_ROOT / "novel.py"), "post", "1", "--slug", slug],
                          cwd=str(PROJECT_ROOT), timeout=300)
    if post_result.returncode != 0:
        print(f"  [FAIL] post returned exit code {post_result.returncode}")
        return post_result.returncode

    print("\n[STEP 6] Demo complete!")
    print("  Report: python novel.py report")
    print(f"  Chapter: {chapter_file}")
    print()
    print("=" * 60)
    print("  Demo pipeline passed.")
    print("=" * 60)
    return 0

def cmd_report():
    """Show most recent guard reports and exports."""
    print("=" * 60)
    v = get_version()
    print(f"  Novel Pipeline - Write Engine {v}")
    print("  Reports")
    print("=" * 60)
    print()

    cfg_data = _load_project_config()
    reports_dir = resolve_path(PROJECT_ROOT, cfg_data.get("reports_root", "./exports/reports"))
    if not reports_dir.exists():
        print("  No reports directory found.")
        print(f"  Expected: {reports_dir}")
        return 0

    all_reports = sorted(reports_dir.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not all_reports:
        print("  No report files found.")
        return 0

    print(f"  Found {len(all_reports)} report files in {reports_dir}")
    print()

    for rp in all_reports[:10]:
        mtime = datetime.fromtimestamp(rp.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        size = rp.stat().st_size
        size_str = f"{size:,}B" if size < 1024 else f"{size/1024:.1f}KB"
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
    v = get_version()
    print(f"  Novel Pipeline - Write Engine {v}")
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
        issues = len(vp_report.get("issues", [])) or len(vp_report.get("warnings", []))
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


def cmd_wc(file_path: str = None):
    """Count Chinese characters in a chapter file."""
    if not file_path:
        print("Usage: python novel.py wc <chapter_file.txt>")
        return 1
    fp = Path(file_path)
    if not fp.exists():
        print(f"[ERROR] File not found: {fp}")
        return 1
    text = fp.read_text(encoding="utf-8")
    # Count Chinese chars only (U+4E00-U+9FFF plus common CJK extensions)
    cn = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf')
    total = len(text)
    print(f"  {fp.name}")
    print(f"  汉字: {cn}  |  总字符: {total}  |  占比: {cn*100//total if total else 0}%")
    # Read word_count thresholds from config
    wc_min = 1300; wc_best_min = 1900; wc_max = 3300  # defaults
    try:
        cfg_path = PROJECT_ROOT / "config.json"
        if cfg_path.exists():
            cfg_data = _load_project_config()
            wc_cfg = cfg_data.get("word_count", {})
            normal = wc_cfg.get("normal", {})
            wc_min = normal.get("min", wc_min)
            wc_best_min = normal.get("best_min", wc_best_min)
            wc_max = normal.get("max", wc_max)
    except Exception:
        pass
    # Quick check against limits
    if cn < wc_min:
        print(f"  ⚠️  低于最低线 ({wc_min})，需补 {wc_min-cn} 字+")
    elif cn < wc_best_min:
        print(f"  ✅ 通过最低线，距最佳范围还差 {wc_best_min-cn} 字")
    elif cn <= wc_max:
        print(f"  ✅ 在正常范围内")
    else:
        print(f"  ⚠️  超过上限 ({wc_max})")
    return 0


def cmd_init():
    """Initialize project: create directories, copy config, init DB."""
    print("=" * 60)
    v = get_version()
    print(f"  Novel Pipeline - Write Engine {v}")
    print("  Initialize Project")
    print("=" * 60)
    print()

    cfg_path = PROJECT_ROOT / "config.json"
    if not cfg_path.exists():
        example = PROJECT_ROOT / "config.example.json"
        if example.exists():
            import shutil
            shutil.copy(example, cfg_path)
            print("  [OK] config.json created from config.example.json")
        else:
            print("  [WARN] config.example.json not found")
    else:
        print("  [OK] config.json already exists")

    cfg_data = _load_project_config()

    print()
    print("  Initializing database...")
    try:
        from init_db import init_db as db_init
        db_path = resolve_path(PROJECT_ROOT, cfg_data.get("db_path", "./data/novel_memory.db"))
        schema = PROJECT_ROOT / "database" / "schema.sql"
        if not schema.exists():
            print("  [WARN] schema.sql not found, skipping DB init")
        else:
            db_path.parent.mkdir(parents=True, exist_ok=True)
            db_init(str(db_path), str(schema))
            print(f"  [OK] Database initialized: {db_path}")
    except Exception as e:
        print(f"  [WARN] DB init error: {e}")

    dirs = [
        cfg_data.get("novels_root", "./novels"),
        cfg_data.get("outputs_root", "./outputs"),
        str(Path(cfg_data.get("outputs_root", "./outputs")) / "task_cards"),
        str(Path(cfg_data.get("outputs_root", "./outputs")) / "reviews"),
        cfg_data.get("exports_root", "./exports"),
        cfg_data.get("reports_root", "./exports/reports"),
        cfg_data.get("tmp_root", "./tmp"),
    ]
    for d in dirs:
        p = resolve_path(PROJECT_ROOT, d)
        p.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] Directory ready: {p.relative_to(PROJECT_ROOT) if p.is_relative_to(PROJECT_ROOT) else p}")

    print()
    print("  Project initialized. Run 'python novel.py demo' to test.")
    return 0

def _get_default_slug(cfg_path=None):
    """Resolve default novel slug from config.json."""
    try:
        return _load_project_config().get("default_novel_slug", "demo_novel")
    except Exception:
        return "demo_novel"


def cmd_pre(chapter_no: str = None, slug: str = None, volume_no: str = None):
    """Run pre-write gate for a chapter."""
    cfg = PROJECT_ROOT / "config.json"
    if not chapter_no:
        print("Usage: python novel.py pre <chapter_no> [--slug <slug>] [--volume <n>]")
        return 1
    print(f"  Running pre-write gate for chapter {chapter_no}...")
    slug = slug or _get_default_slug(cfg)
    try:
        import subprocess
        cmd = [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "pre", str(chapter_no),
               "--config", str(cfg), "--novel-slug", slug]
        if volume_no: cmd.extend(["--volume-no", str(volume_no)])
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), timeout=120)
        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


def cmd_post(chapter_no: str = None, slug: str = None, volume_no: str = None, file_path: str = None, story: bool = False):
    """Post-write: run guards and ingest."""
    cfg = PROJECT_ROOT / "config.json"
    if not chapter_no and not file_path:
        print("Usage: python novel.py post <chapter_no> [--file <path>] [--slug <slug>] [--story]")
        return 1
    if file_path:
        print(f"  Running post-write guards for file: {file_path}")
    else:
        print(f"  Running post-write guards for chapter {chapter_no}...")
    slug = slug or _get_default_slug(cfg)
    try:
        import subprocess
        cmd = [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "post",
               str(chapter_no) if chapter_no else "1",
               "--config", str(cfg), "--novel-slug", slug]
        if volume_no: cmd.extend(["--volume-no", str(volume_no)])
        if file_path:
            cmd.extend(["--chapters-dir", str(Path(file_path).parent)])
        else:
            vol = int(volume_no or 1)
            novels_root = Path(_get_novels_root(cfg))
            cmd.extend(["--chapters-dir", str(novels_root / slug / f"第{vol:02d}卷")])
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), timeout=300)
        if result.returncode != 0:
            return result.returncode

        # Auto-generate story commit if --story flag is set and .story/ exists
        if story and _story_exists():
            print()
            print("  [story] 自动生成提交记录...")
            try:
                from scripts.story import commit_builder
                ch_no = int(chapter_no) if chapter_no else 1

                # Try to read word count from the chapter file
                wc = 0
                if file_path:
                    ch_fp = Path(file_path)
                else:
                    novels_root = _get_novels_root(cfg)
                    ch_dir = Path(novels_root) / slug / "第01卷"
                    candidates = list(ch_dir.glob(f"第{ch_no}章*.txt"))
                    ch_fp = candidates[0] if candidates else None

                if ch_fp and ch_fp.exists():
                    text = ch_fp.read_text(encoding="utf-8")
                    wc = sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf')

                # Try reading guard report for summary
                guard_summary = {}
                try:
                    import json as _json
                    cfg_data = _load_project_config()
                    reports_dir = resolve_path(PROJECT_ROOT, cfg_data.get("reports_root", "./exports/reports"))
                    if reports_dir.exists():
                        reports = sorted(reports_dir.rglob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
                        if reports:
                            rpt = _json.loads(reports[0].read_text(encoding="utf-8"))
                            guard_summary = {
                                "status": rpt.get("status", rpt.get("overall_status", "?")),
                                "issues": len(rpt.get("issues", [])),
                            }
                except Exception:
                    pass

                commit = commit_builder.build_commit(
                    PROJECT_ROOT, ch_no,
                    chapter_title=f"第{ch_no}章",
                    word_count=wc,
                    guard_summary=guard_summary,
                )
                saved = commit_builder.save_commit(PROJECT_ROOT, ch_no, commit)
                print(f"  [story] 第{ch_no}章提交记录已保存: {Path(saved).name}")
            except Exception as e:
                print(f"  [story] 提交生成失败: {e}")

        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


def _get_novels_root(cfg_path=None):
    """Read novels_root from config."""
    try:
        cfg = _load_project_config()
        return str(resolve_path(PROJECT_ROOT, cfg.get("novels_root", "./novels")))
    except Exception:
        return str(PROJECT_ROOT / "novels")


def cmd_review(chapter_no: str = None, slug: str = None, volume_no: str = None):
    """Run guard review on a chapter."""
    cfg = PROJECT_ROOT / "config.json"
    if not chapter_no:
        print("Usage: python novel.py review <chapter_no> [--slug <slug>] [--volume <n>]")
        return 1
    print(f"  Running review for chapter {chapter_no}...")
    slug = slug or _get_default_slug(cfg)
    try:
        import subprocess
        cmd = [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "review", str(chapter_no),
               "--config", str(cfg), "--novel-slug", slug]
        if volume_no: cmd.extend(["--volume-no", str(volume_no)])
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), timeout=300)
        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


def cmd_export(slug: str = None, fmt: str = "md"):
    """Export novel to a single file."""
    if not slug:
        print("Usage: python novel.py export --slug <novel_slug> [--format txt|md]")
        return 1
    fmt = fmt or "md"
    ext = ".txt" if fmt == "txt" else ".md"
    print(f"  Exporting novel '{slug}' as {fmt}...")
    try:
        import subprocess
        args = [sys.executable, str(SCRIPTS_DIR / "export_novel.py"),
                "--slug", slug, "--config", str(PROJECT_ROOT / "config.json"), "--format", fmt,
                "--output", str(resolve_path(PROJECT_ROOT, _load_project_config().get("exports_root", "./exports")) / f"{slug}_full{ext}")]
        result = subprocess.run(args, cwd=str(PROJECT_ROOT), timeout=60)
        if result.returncode == 0:
            print(f"  [OK] Exported to exports/{slug}_full{ext}")
        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


def cmd_agents(args):
    """Multi-agent review board."""
    if args.agents_action != "review":
        print("Usage: python novel.py agents review <chapter_no> [--mode light|full]")
        return 1
    chapter_no = getattr(args, "chapter_no", None)
    if not chapter_no:
        print("Usage: python novel.py agents review <chapter_no>")
        return 1
    try:
        import json as _json
        cfg_path = PROJECT_ROOT / "config.json"
        _cfg = {}
        if cfg_path.exists():
            _cfg = _load_project_config()
        slug = getattr(args, "slug", None) or _cfg.get("default_novel_slug", "demo_novel")
        novels_root = resolve_path(PROJECT_ROOT, _cfg.get("novels_root", "./novels"))
        ch_dir = Path(novels_root) / slug / "第01卷"
        candidates = list(ch_dir.glob(f"第{chapter_no}章*.txt"))
        if not candidates:
            print(f"[WARN] No chapter file found for chapter {chapter_no} in {ch_dir}")
            print(f"[INFO] Running agent review on empty context...")
            content = ""
        else:
            content = candidates[0].read_text(encoding="utf-8")
        
        mode = getattr(args, "mode", "light")
        print(f"Running {mode}-mode agent review for chapter {chapter_no}...")
        from scripts.agents.orchestrator import run_agent_review
        result = run_agent_review(content, int(chapter_no), mode=mode)
        print(f"  Score: {result.get('overall_score', 'N/A')}")
        print(f"  Status: {result.get('status', 'N/A')}")
        chief = result.get("chief_editor", {})
        for cat in ["must_fix", "should_fix", "keep"]:
            items = chief.get(cat, [])
            if items:
                print(f"  {cat}: {len(items)} items")
        return 0
    except Exception as e:
        print(f"  [ERROR] Agent review failed: {e}")
        return 1


def cmd_rag(args):
    """Vector RAG queries."""
    action = getattr(args, "rag_action", None)
    if action == "status":
        print("RAG Status:")
        try:
            from scripts.rag.rag_config import load_rag_config, get_rag_mode
            cfg = load_rag_config()
            mode = get_rag_mode(cfg)
            # Vector available if sentence_transformers is installed
            try:
                import sentence_transformers
                vector_ok = True
            except ImportError:
                vector_ok = False
            print(f"  Mode: {mode}")
            print(f"  Vector: {'available' if vector_ok else 'unavailable (fallback to FTS5)'}")
        except Exception as e:
            print(f"  FTS5: available (default)")
            print(f"  Vector: unavailable ({e})")
        return 0
    elif action == "query":
        question = " ".join(getattr(args, "question", []))
        if not question:
            print("Usage: python novel.py rag query <question>")
            return 1
        try:
            from scripts.rag.rag_query import rag_query
            result = rag_query(question)
            print(f"Query: {question}")
            print(f"Mode: {result.get('mode', 'fts5')}")
            for r in result.get("results", [])[:5]:
                print(f"  [{r.get('chapter_no', '?')}] {r.get('evidence', '')[:80]}")
        except Exception as e:
            print(f"  [WARN] RAG query unavailable: {e}")
        return 0
    else:
        print("Usage: python novel.py rag {status|query}")
        return 1


# ============================================================
#  Story Contract system commands
# ============================================================

def _story_exists() -> bool:
    """Check if .story/ directory is initialized."""
    return (PROJECT_ROOT / ".story").exists()


def _story_missing_msg() -> str:
    return "请先运行 python novel.py story init"


def cmd_story(args):
    """Story contract system: init, contract, commit, health."""
    from scripts.story import story_init, contract_builder, commit_builder, story_health

    action = getattr(args, "story_action", None)

    if action == "init":
        if _story_exists():
            print("  .story/ 目录已存在。如需重建请先删除。")
            return 0
        result = story_init.init_story(PROJECT_ROOT)
        print(f"  [OK] .story/ 已初始化")
        for item in result.get("created", []):
            print(f"    + {item}")
        print(f"\n  目录: {result['story_dir']}")
        return 0

    elif action == "contract":
        if not _story_exists():
            print(f"  {_story_missing_msg()}")
            return 1
        chapter_no = int(getattr(args, "chapter_no", "1") or "1")
        # Try loading previous commit for context
        prev_commit = None
        if chapter_no > 1:
            prev_commit_path = PROJECT_ROOT / ".story" / "commits" / f"chapter_{chapter_no-1:03d}_commit.json"
            if prev_commit_path.exists():
                import json as _json
                prev_commit = _json.loads(prev_commit_path.read_text(encoding="utf-8"))

        contract = contract_builder.build_contract(PROJECT_ROOT, chapter_no, prev_commit=prev_commit)
        saved = contract_builder.save_contract(PROJECT_ROOT, chapter_no, contract)
        print(f"  [OK] 第{chapter_no}章合同已生成")
        print(f"  保存至: {saved}")
        print(f"  开放伏笔: {len(contract.get('open_promises_to_keep', []))} 个")
        print(f"  活跃角色: {len(contract.get('active_characters', []))} 个")
        return 0

    elif action == "commit":
        if not _story_exists():
            print(f"  {_story_missing_msg()}")
            return 1
        chapter_no = int(getattr(args, "chapter_no", "1") or "1")
        commit = commit_builder.build_commit(
            PROJECT_ROOT, chapter_no,
            chapter_title=f"第{chapter_no}章",
            word_count=0,
            guard_summary={"note": "手动生成"},
        )
        saved = commit_builder.save_commit(PROJECT_ROOT, chapter_no, commit)
        print(f"  [OK] 第{chapter_no}章提交记录已生成")
        print(f"  保存至: {saved}")
        return 0

    elif action == "health":
        if not _story_exists():
            print(f"  {_story_missing_msg()}")
            return 1
        report = story_health.check_health(PROJECT_ROOT)
        print("=" * 60)
        print("  故事链健康检查")
        print("=" * 60)
        status = "OK" if report["ok"] else "ISSUES"
        print(f"  状态: {status}")
        print(f"  合同数: {report.get('contract_count', 0)}")
        print(f"  提交数: {report.get('commit_count', 0)}")
        print(f"  事件数: {report.get('event_count', 0)}")
        issues = report.get("issues", [])
        if issues:
            print(f"\n  问题 ({len(issues)}):")
            for iss in issues:
                print(f"    - {iss}")
        else:
            print("\n  未发现问题。")
        print()
        return 0 if report["ok"] else 1

    else:
        print("Usage: python novel.py story {init|contract|commit|health}")
        return 1


def cmd_query(args):
    """Query project memory for matching content."""
    if not _story_exists():
        print(f"  {_story_missing_msg()}")
        return 1

    question = " ".join(getattr(args, "question", []) or [])
    if not question.strip():
        print("Usage: python novel.py query <question>")
        print("Example: python novel.py query 主角的名字是什么")
        return 1

    print(f"  查询: {question}")
    print()

    story = PROJECT_ROOT / ".story"

    # Search memory JSON files
    memory = story / "memory"
    hits = 0

    for fname, label in [("characters.json", "角色"), ("promises.json", "伏笔"),
                          ("world_facts.json", "世界观"), ("learned_rules.json", "规则")]:
        fp = memory / fname
        if not fp.exists():
            continue
        try:
            import json as _json
            data = _json.loads(fp.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    text = str(item)
                    if question.lower() in text.lower() or any(kw in text for kw in question.split()):
                        hits += 1
                        preview = text[:120].replace("\n", " ")
                        print(f"  [{label}] {preview}...")
        except Exception:
            pass

    # Search event ledger
    ledger = story / "events" / "event_ledger.jsonl"
    if ledger.exists():
        try:
            for line in ledger.read_text(encoding="utf-8").strip().split("\n"):
                if not line.strip():
                    continue
                if question.lower() in line.lower() or any(kw in line for kw in question.split()):
                    hits += 1
                    import json as _json
                    evt = _json.loads(line)
                    preview = str(evt.get("event", line))[:120]
                    print(f"  [事件 ch{evt.get('chapter', '?')}] {preview}...")
        except Exception:
            pass

    # Search contracts
    chapters_dir = story / "chapters"
    if chapters_dir.exists():
        for cf in sorted(chapters_dir.glob("chapter_*_contract.json")):
            try:
                import json as _json
                text = cf.read_text(encoding="utf-8")
                if question.lower() in text.lower() or any(kw in text for kw in question.split()):
                    hits += 1
                    data = _json.loads(text)
                    print(f"  [合同 ch{data.get('chapter_no', '?')}] {data.get('chapter_title', '')}")
            except Exception:
                pass

    if hits == 0:
        print("  未找到匹配的记忆。")
    else:
        print(f"\n  共 {hits} 条匹配。")
    return 0


def cmd_learn(args):
    """Add/list/remove learned writing rules."""
    if not _story_exists():
        print(f"  {_story_missing_msg()}")
        return 1

    import json as _json

    rules_file = PROJECT_ROOT / ".story" / "memory" / "learned_rules.json"
    rules = []
    if rules_file.exists():
        try:
            rules = _json.loads(rules_file.read_text(encoding="utf-8"))
        except Exception:
            rules = []

    action = getattr(args, "action", "list")
    rule_text = " ".join(getattr(args, "rule", []) or [])

    if action == "list":
        if not rules:
            print("  暂无已学规则。用 python novel.py learn add <规则> 添加。")
            return 0
        print(f"  已学规则 ({len(rules)}):")
        for i, r in enumerate(rules):
            rule_str = r.get("rule", str(r))
            ch = r.get("chapter", "?")
            print(f"    [{i+1}] (ch{ch}) {rule_str}")
        return 0

    elif action == "add":
        if not rule_text.strip():
            print("Usage: python novel.py learn add <规则内容>")
            print("Example: python novel.py learn add 主角李明的口头禅是'走着瞧'")
            return 1
        from datetime import datetime
        rules.append({
            "rule": rule_text,
            "chapter": "manual",
            "added_at": datetime.now().isoformat(),
        })
        rules_file.write_text(_json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [OK] 规则已添加: {rule_text}")
        return 0

    elif action == "remove":
        if not rule_text.strip():
            print("Usage: python novel.py learn remove <number>")
            return 1
        try:
            idx = int(rule_text) - 1
            if 0 <= idx < len(rules):
                removed = rules.pop(idx)
                rules_file.write_text(_json.dumps(rules, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  [OK] 规则已移除: {removed.get('rule', str(removed))}")
                return 0
            else:
                print(f"  无效编号: {idx+1} (共 {len(rules)} 条)")
                return 1
        except ValueError:
            print(f"  请输入有效编号。当前共 {len(rules)} 条规则。")
            return 1

    return 0


def cmd_board(args):
    """Print a readonly status board for the project."""
    print("=" * 60)
    print("  Novel Pipeline — 项目看板")
    print("=" * 60)
    print()

    # Version
    v = get_version()
    print(f"  引擎版本: {v}")

    # Story status
    if _story_exists():
        from scripts.story import story_health
        health = story_health.check_health(PROJECT_ROOT)
        status = "OK" if health["ok"] else "ISSUES"
        print(f"  故事链: {status}")
        print(f"    合同: {health.get('contract_count', 0)}  提交: {health.get('commit_count', 0)}  事件: {health.get('event_count', 0)}")
        issues = health.get("issues", [])
        if issues:
            for iss in issues[:3]:
                print(f"    ⚠ {iss}")
    else:
        print(f"  故事链: 未初始化 (python novel.py story init)")

    # Config
    cfg = PROJECT_ROOT / "config.json"
    if cfg.exists():
        import json as _json
        try:
            cfg_data = _load_project_config()
            slug = cfg_data.get("default_novel_slug", "?")
            genre = cfg_data.get("default_genre", "?")
            style = cfg_data.get("default_style", "?")
            print(f"  当前项目: {slug}")
            print(f"  类型/风格: {genre} / {style}")

            # Word count config
            wc = cfg_data.get("word_count", {}).get("normal", {})
            if wc:
                print(f"  字数范围: {wc.get('min', '?')}-{wc.get('max', '?')} (最佳≥{wc.get('best_min', '?')})")
        except Exception:
            print(f"  配置: 读取失败")
    else:
        print(f"  配置: 未找到 config.json")

    # Chapters in novels dir
    if cfg.exists():
        import json as _json
        try:
            cfg_data = _load_project_config()
            slug = cfg_data.get("default_novel_slug", "demo_novel")
            novels_root = resolve_path(PROJECT_ROOT, cfg_data.get("novels_root", "./novels"))
            ch_dir = Path(novels_root) / slug / "第01卷"
            if ch_dir.exists():
                chapters = sorted(ch_dir.glob("第*章*.txt"))
                print(f"  已完成章节: {len(chapters)}")
                if chapters:
                    latest = chapters[-1]
                    cn = sum(1 for c in latest.read_text(encoding="utf-8")
                             if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf')
                    print(f"    最新: {latest.name} ({cn} 汉字)")
            else:
                print(f"  章节目录: 未找到 {ch_dir}")
        except Exception:
            print(f"  章节: 读取失败")

    # DB status
    try:
        db_cfg = PROJECT_ROOT / "config.json"
        if db_cfg.exists():
            cfg_data = _load_project_config()
            db_path = cfg_data.get("db_path", "./data/novel_memory.db")
        else:
            db_path = str(PROJECT_ROOT / "data" / "novel_memory.db")
        dbp = Path(db_path)
        if not dbp.is_absolute():
            dbp = PROJECT_ROOT / dbp
        if dbp.exists():
            import sqlite3
            conn = sqlite3.connect(str(dbp))
            cur = conn.execute("SELECT COUNT(*) FROM chapters")
            ch_count = cur.fetchone()[0]
            cur = conn.execute("SELECT COUNT(*) FROM characters")
            char_count = cur.fetchone()[0]
            conn.close()
            print(f"  数据库: {dbp.name} | 章节: {ch_count} | 角色: {char_count}")
        else:
            print(f"  数据库: 未找到 ({dbp})")
    except Exception:
        print(f"  数据库: 无法读取")

    print()
    print("=" * 60)
    return 0


def cmd_genre(args):
    """Genre pack management."""
    action = getattr(args, "genre_action", None)
    if action == "list":
        from scripts.genre.genre_loader import list_genres
        genres = list_genres()
        print(f"Available genres ({len(genres)}):")
        for g in genres:
            print(f"  {g}")
    elif action == "show":
        from scripts.genre.genre_loader import load_genre_pack
        gid = getattr(args, "genre_id", "generic")
        pack = load_genre_pack(gid)
        print(f"Genre: {pack.get('name', gid)} ({pack.get('genre_id', gid)})")
        print(f"  {pack.get('description', '')[:100]}")
        for key in ["core_promises", "forbidden_patterns", "agent_focus"]:
            items = pack.get(key, [])
            if items:
                print(f"  {key}:")
                for item in items[:5]:
                    print(f"    - {item}")
    else:
        print("Usage: python novel.py genre {list|show <id>}")
    return 0


def cmd_style(args):
    """Style pack management."""
    action = getattr(args, "style_action", None)
    if action == "list":
        from scripts.genre.style_loader import list_styles
        styles = list_styles()
        print(f"Available styles ({len(styles)}):")
        for s in styles:
            print(f"  {s}")
    elif action == "show":
        from scripts.genre.style_loader import load_style_pack
        sid = getattr(args, "style_id", "generic")
        pack = load_style_pack(sid)
        print(f"Style: {pack.get('name', sid)} ({pack.get('style_id', sid)})")
        print(f"  {pack.get('description', '')[:100]}")
        for key in ["narrative_features", "forbidden_patterns", "agent_focus"]:
            items = pack.get(key, [])
            if items:
                print(f"  {key}:")
                for item in items[:5]:
                    print(f"    - {item}")
    else:
        print("Usage: python novel.py style {list|show <id>}")
    return 0


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=f"Novel Pipeline - Write Engine {get_version()} CLI",
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
    p_pre.add_argument("--slug", help="Novel slug")
    p_pre.add_argument("--volume", help="Volume number")
    # post
    p_post = sub.add_parser("post", help="Post-write: run guards and ingest")
    p_post.add_argument("chapter_no", nargs="?", help="Chapter number")
    p_post.add_argument("--slug", help="Novel slug")
    p_post.add_argument("--volume", help="Volume number")
    p_post.add_argument("--file", help="Direct chapter file path")
    p_post.add_argument("--story", action="store_true", help="Auto-generate story commit after post")
    # review
    p_review = sub.add_parser("review", help="Run guard review on a chapter")
    p_review.add_argument("chapter_no", nargs="?", help="Chapter number")
    p_review.add_argument("--slug", help="Novel slug")
    p_review.add_argument("--volume", help="Volume number")
    # report
    sub.add_parser("report", help="Show recent guard reports")
    # guards
    sub.add_parser("guards", help="List registered guards")
    # check
    p_check = sub.add_parser("check", help="Run v0.5.0 guards on a chapter file")
    p_check.add_argument("file_path", help="Path to chapter TXT file")
    # agents
    p_agents = sub.add_parser("agents", help="Multi-agent review board")
    p_agents_sub = p_agents.add_subparsers(dest="agents_action")
    p_agents_review = p_agents_sub.add_parser("review", help="Run agent review on a chapter")
    p_agents_review.add_argument("chapter_no", nargs="?", help="Chapter number")
    p_agents_review.add_argument("--mode", default="light", choices=["light", "full"])
    p_agents_review.add_argument("--slug", help="Novel slug")
    p_agents_review.add_argument("--genre", help="Genre pack ID (e.g. xianxia, mystery)")
    p_agents_review.add_argument("--style", default=None, help="Style pack ID (e.g. webnovel, black_humor)")

    # rag
    p_rag = sub.add_parser("rag", help="Vector RAG (optional)")
    p_rag_sub = p_rag.add_subparsers(dest="rag_action")
    p_rag_status = p_rag_sub.add_parser("status", help="Check RAG status")
    p_rag_query = p_rag_sub.add_parser("query", help="Query the novel database")
    p_rag_query.add_argument("question", nargs="*", help="Question to ask")

    # export
    p_export = sub.add_parser("export", help="Export novel to single file")
    p_export.add_argument("--slug", help="Novel slug to export")
    p_export.add_argument("--format", default="md", choices=["txt", "md"])
    # wc
    p_wc = sub.add_parser("wc", help="Count Chinese characters in a chapter file")
    p_wc.add_argument("file_path", nargs="?", help="Path to chapter TXT file")
    # story
    p_story = sub.add_parser("story", help="Story contract system")
    p_story_sub = p_story.add_subparsers(dest="story_action")
    p_story_sub.add_parser("init", help="Initialize .story/ directory")
    p_story_sub_contract = p_story_sub.add_parser("contract", help="Generate chapter contract")
    p_story_sub_contract.add_argument("chapter_no", nargs="?", default="1")
    p_story_sub_commit = p_story_sub.add_parser("commit", help="Generate chapter commit")
    p_story_sub_commit.add_argument("chapter_no", nargs="?", default="1")
    p_story_sub.add_parser("health", help="Check story chain health")

    # query
    p_query = sub.add_parser("query", help="Query project memory")
    p_query.add_argument("question", nargs="*", help="Natural language question")

    # learn
    p_learn = sub.add_parser("learn", help="Writing rules learned")
    p_learn.add_argument("action", nargs="?", default="list", choices=["add", "list", "remove"])
    p_learn.add_argument("rule", nargs="*", help="Rule text to add")

    # board
    sub.add_parser("board", help="Readonly status board")

    # genre
    p_genre = sub.add_parser("genre", help="Genre pack management")
    p_genre_sub = p_genre.add_subparsers(dest="genre_action")
    p_genre_sub.add_parser("list", help="List available genres")
    p_genre_show = p_genre_sub.add_parser("show", help="Show genre pack details")
    p_genre_show.add_argument("genre_id", help="Genre ID (e.g. xianxia)")
    # style
    p_style = sub.add_parser("style", help="Style pack management")
    p_style_sub = p_style.add_subparsers(dest="style_action")
    p_style_sub.add_parser("list", help="List available styles")
    p_style_show = p_style_sub.add_parser("show", help="Show style pack details")
    p_style_show.add_argument("style_id", help="Style ID (e.g. black_humor)")

    args = parser.parse_args()

    if args.command == "status":
        sys.exit(cmd_status())
    elif args.command == "demo":
        sys.exit(cmd_demo())
    elif args.command == "init":
        sys.exit(cmd_init())
    elif args.command == "pre":
        sys.exit(cmd_pre(getattr(args, "chapter_no", None),
                        getattr(args, "slug", None),
                        getattr(args, "volume", None)))
    elif args.command == "post":
        sys.exit(cmd_post(getattr(args, "chapter_no", None),
                         getattr(args, "slug", None),
                         getattr(args, "volume", None),
                         getattr(args, "file", None),
                         getattr(args, "story", False)))
    elif args.command == "review":
        sys.exit(cmd_review(getattr(args, "chapter_no", None),
                           getattr(args, "slug", None),
                           getattr(args, "volume", None)))
    elif args.command == "report":
        sys.exit(cmd_report())
    elif args.command == "guards":
        sys.exit(cmd_guards())
    elif args.command == "check":
        sys.exit(cmd_check(args.file_path))
    elif args.command == "agents":
        sys.exit(cmd_agents(args))
    elif args.command == "rag":
        sys.exit(cmd_rag(args))
    elif args.command == "export":
        sys.exit(cmd_export(args.slug, args.format))
    elif args.command == "wc":
        sys.exit(cmd_wc(args.file_path))
    elif args.command == "genre":
        sys.exit(cmd_genre(args))
    elif args.command == "style":
        sys.exit(cmd_style(args))
    elif args.command == "story":
        sys.exit(cmd_story(args))
    elif args.command == "query":
        sys.exit(cmd_query(args))
    elif args.command == "learn":
        sys.exit(cmd_learn(args))
    elif args.command == "board":
        sys.exit(cmd_board(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
