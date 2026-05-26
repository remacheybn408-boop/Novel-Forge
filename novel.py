#!/usr/bin/env python3
"""
novel.py — Novel Pipeline Write Engine CLI v0.5.6

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
    """Create demo_novel with real chapter file, ingest to DB, show report."""
    print("=" * 60)
    v = get_version()
    print(f"  Novel Pipeline - Write Engine {v}")
    print("  Demo Setup")
    print("=" * 60)
    print()

    # Run init first if config is missing
    cfg_path = PROJECT_ROOT / "config.json"
    if not cfg_path.exists():
        print("[STEP 1] Initializing project...")
        cmd_init()
        print()
        step = 2
    else:
        print("[STEP 1] config.json found, project already initialized.")
        step = 2

    # Create demo_novel directories and files
    # For demo, always use project-relative novels directory
    novels_root = PROJECT_ROOT / "novels"
    demo_dir = novels_root / "demo_novel"
    vol_dir = demo_dir / "第01卷"
    vol_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[STEP {step}] Creating demo_novel chapter...")
    print(f"  novels/demo_novel/")
    print(f"  novels/demo_novel/第01卷/")

    # Write demo chapter with real Chinese content (~2000 chars)
    demo_content = (
        "第1章 开篇\n\n"
        "清晨的阳光穿过窗棂，洒在陈旧的木桌上。李明远缓缓睁开眼睛，耳边传来熟悉的鸟鸣声。窗外，几只翠鸟在枝头跳来跳去，叽叽喳喳地叫个不停。这是他最喜欢的时刻——天地初醒，万物复苏，整个世界都笼罩在一层温柔的金色光芒中。\n\n"
        "这是他来到青云宗的第三年。三年前，他还只是山下渔村里的一个普通少年，每天跟着父亲出海打鱼，过着平凡而单调的生活。那时的他从未想过，自己有朝一日会踏入修仙之路，成为一名真正的修士。命运的转折发生在一个暴风雨的夜晚——他的渔船被巨浪掀翻，他在海中挣扎求生，绝望之际，怀里那枚母亲留下的玉佩突然发出耀眼光芒，不仅救了他一命，还让他觉醒了灵根。\n\n"
        "\u201c远哥，该去练功了！\u201d门外传来师弟小石头清脆的声音。小石头本名石磊，是两年前被宗门从难民中收留的孤儿，因为年纪最小，个子也最矮，大家都叫他小石头。这孩子虽然资质平平，却比任何人都勤奋，每天天不亮就起来练功，从不偷懒。\n\n"
        "李明远翻身坐起，目光落在床头那枚已经暗淡无光的玉佩上。那是母亲留给他的唯一遗物，通体碧绿，上面刻着一些他至今无法理解的古文字。自从三年前意外激活之后，他的命运就彻底改变了——从一个平凡的渔家少年，变成了青云宗的外门弟子。但三年过去了，他始终停留在炼气期第三层，在同批入门的弟子中只能算是中游水平。\n\n"
        "\u201c来了。\u201d他应了一声，简单洗漱后推门而出。\n\n"
        "练功场上，数十名外门弟子已经开始了晨练。剑光闪烁，拳风呼啸，空气中弥漫着汗水与青草混合的气息。有些弟子在练习基础剑法，一招一式虽然生涩，却也透着一股不服输的劲头；另一些则在打坐吐纳，试图感应天地间的灵气。远处还有几个师兄在切磋对战，你来我往，打得虎虎生风。\n\n"
        "\u201c明远来了！\u201d一个身材魁梧的青年大步走来，脸上带着爽朗的笑容。此人名叫赵铁柱，是外门弟子中修为最高的几人之一，天生神力，一双铁拳在同辈中罕有对手。他修炼的是青云宗最为刚猛的《铁骨功》，据说已经快要突破炼气期第六层，距离内门只差一步之遥。\u201c昨日你那一剑可真是厉害，连王教习都夸你有天赋。\u201d\n\n"
        "李明远微微一笑，谦逊地摇了摇头：\u201c赵师兄过奖了，不过是运气好罢了。\u201d\n\n"
        "他说的是实话。每次修炼时，那枚玉佩都会在他体内引导真气，走出一条与青云宗正传心法截然不同的路径。这条路更加艰险，也更加玄妙。他不知道自己修炼的到底是什么功法，但他能感觉到，这股力量远比表面看起来要强大得多。\n\n"
        "\u201c都给我站好了！\u201d一声洪亮的嗓音打断了众人的喧闹。\n\n"
        "王教习大步走上练功场中央，目光如电，扫过在场的每一名弟子。他年过六旬，须发皆白，但腰杆挺得笔直，浑身散发着一股不怒自威的气势。作为青云宗资格最老的外门教习，他教导过的弟子没有一千也有八百。据说早年间他也曾是内门弟子，只因在一次秘境探险中伤了根基，这才退居外门担任教习。\n\n"
        "\u201c今日有大长老前来巡视，尔等务必打起十二分精神！\u201d王教习的声音低沉而威严，每一个字都像钉子一样砸在众人心头，\u201c大长老乃我青云宗三大元老之一，执掌戒律堂多年，最是眼里揉不得沙子。谁要是出了岔子，莫怪老夫不讲情面！\u201d\n\n"
        "此言一出，全场鸦雀无声。弟子们不由自主地挺直了脊背，就连平时最散漫的几个也收起了嬉皮笑脸。李明远注意到，连一向大大咧咧的赵铁柱都变得异常严肃，额头隐隐渗出了汗珠。大长老的威名，在外门弟子中无人不知。\n\n"
        "李明远心中却莫名地涌起一阵不安。他下意识地握紧了挂在胸前的玉佩，一股若有若无的凉意从掌心传来，仿佛在提醒他什么。他抬头望向远处的山峰，那里是内门所在的区域，云雾缭绕，隐隐有灵光闪烁。\n\n"
        "他有一种直觉——这场巡视，恐怕不只是例行公事那么简单。\n\n"
        "而那枚玉佩，似乎正在用它的方式告诉他：危险，正在靠近。\n"
    )
    chapter_file = vol_dir / "第1章_开篇.txt"
    chapter_file.write_text(demo_content, encoding="utf-8")
    cn_count = sum(1 for c in demo_content if '\u4e00' <= c <= '\u9fff' or '\u3400' <= c <= '\u4dbf')
    print(f"  [OK] novels/demo_novel/第01卷/第1章_开篇.txt ({cn_count} 汉字)")

    # Register demo novel in database using config's db_path
    try:
        import sqlite3, json
        db_path = PROJECT_ROOT / "data" / "novel_memory.db"
        if cfg_path.exists():
            try:
                cfg_data = json.loads(cfg_path.read_text(encoding="utf-8"))
                # Check both top-level and paths.db_path
                dp = cfg_data.get("db_path") or cfg_data.get("paths", {}).get("db_path")
                if dp:
                    db_path = Path(dp)
                    if not db_path.is_absolute():
                        db_path = PROJECT_ROOT / db_path
            except: pass
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        conn.execute("INSERT OR IGNORE INTO novels (slug, title, genre, style, status) VALUES (?, ?, ?, ?, ?)",
                    ("demo_novel", "Demo Novel", "xianxia", "webnovel", "writing"))
        conn.commit()
        conn.close()
        print("  [OK] demo_novel registered in database")
    except Exception as e:
        print(f"  [WARN] Could not register in DB: {e}")

    # Write demo outline
    outline_content = (
        "# 演示小说 大纲\n\n"
        "## 第一卷：初入宗门\n\n"
        "### 第1章 开篇\n"
        "- 主角李明远是青云宗外门弟子，身怀神秘玉佩\n"
        "- 大长老巡视在即，主角心中不安\n"
        "- 引入宗门世界和修炼体系的基本设定\n\n"
        "### 第2章 考验\n"
        "- 大长老的巡视带有深层目的\n"
        "- 主角在考验中展露异常天赋\n"
        "- 埋下后续冲突的伏笔\n\n"
        "### 第3章 暗流\n"
        "- 宗门内部势力开始关注主角\n"
        "- 主角面临选择：隐藏实力还是脱颖而出\n"
        "- 第一条支线展开\n"
    )
    outline_file = demo_dir / "outline.txt"
    outline_file.write_text(outline_content, encoding="utf-8")
    print(f"  [OK] novels/demo_novel/outline.txt")

    # Run post to ingest chapter to DB
    step += 1
    print(f"\n[STEP {step}] Running post-write guard + ingest...")
    print(f"  python novel.py post 1 --slug demo_novel")
    import subprocess as _sp
    result = _sp.run(
        [sys.executable, str(PROJECT_ROOT / "novel.py"), "post", "1", "--slug", "demo_novel"],
        cwd=str(PROJECT_ROOT), timeout=300
    )
    if result.returncode != 0:
        print(f"\n[WARN] post returned exit code {result.returncode}")
    else:
        print(f"  [OK] Chapter ingested to DB")

    step += 1
    print(f"\n[STEP {step}] Demo complete!")
    print(f"  Report: exports/reports/ (run 'python novel.py report' to view)")
    print(f"  Chapter: novels/demo_novel/第01卷/第1章_开篇.txt ({cn_count} 汉字)")
    print()
    print("=" * 60)
    print("  Demo setup complete.")
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

    # Read exports_root from config
    cfg_path = PROJECT_ROOT / "config.json"
    exports_root = None
    try:
        cfg_data = json.loads(cfg_path.read_text(encoding="utf-8"))
        exports_root = cfg_data.get("exports_root")
    except Exception:
        pass

    reports_dir = Path(exports_root) / "reports" if exports_root else PROJECT_ROOT / "exports" / "reports"
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
            cfg_data = json.loads(cfg_path.read_text(encoding="utf-8"))
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
    dirs = ["outputs/task_cards", "outputs/reviews", "exports", "exports/reports", "tmp"]
    for d in dirs:
        p = PROJECT_ROOT / d
        p.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] Directory created: {d}")

    print()
    print("  Project initialized. Run 'python novel.py demo' to test.")
    return 0


def _get_default_slug(cfg_path):
    """Resolve default novel slug from config.json."""
    try:
        import json as _json
        _cfg = _json.load(open(cfg_path, encoding="utf-8"))
        return _cfg.get("default_novel_slug", "demo_novel")
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
            from pathlib import Path
            cmd.extend(["--chapters-dir", str(Path(file_path).parent)])
        else:
            # Always pass chapters-dir using project-relative path
            cmd.extend(["--chapters-dir", str(PROJECT_ROOT / "novels" / slug / "第01卷")])
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
                    from pathlib import Path
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
                    cfg_data = _json.loads(cfg.read_text(encoding="utf-8"))
                    exports_root = cfg_data.get("exports_root", str(PROJECT_ROOT / "exports"))
                    reports_dir = Path(exports_root) / "reports"
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


def _get_novels_root(cfg_path):
    """Read novels_root from config."""
    try:
        import json as _json
        with open(cfg_path, encoding="utf-8") as f:
            c = _json.load(f)
        return c.get("novels_root", str(PROJECT_ROOT / "novels"))
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
                "--slug", slug, "--format", fmt,
                "--output", str(PROJECT_ROOT / "exports" / f"{slug}_full{ext}")]
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
            _cfg = _json.load(open(cfg_path, encoding="utf-8"))
        slug = getattr(args, "slug", None) or _cfg.get("default_novel_slug", "demo_novel")
        novels_root = _cfg.get("novels_root", str(PROJECT_ROOT / "novels"))
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
            cfg_data = _json.loads(cfg.read_text(encoding="utf-8"))
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
            cfg_data = _json.loads(cfg.read_text(encoding="utf-8"))
            slug = cfg_data.get("default_novel_slug", "demo_novel")
            novels_root = cfg_data.get("novels_root", str(PROJECT_ROOT / "novels"))
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
            cfg_data = _json.loads(db_cfg.read_text(encoding="utf-8"))
            db_path = cfg_data.get("db_path", str(PROJECT_ROOT / "data" / "novel_memory.db"))
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
