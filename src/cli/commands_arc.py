#!/usr/bin/env python3
"""src/cli/commands_arc.py — Story Arc 统一追踪 CLI v0.7.2

Commands:
  python novel.py story arc check             全维度弧线检测
  python novel.py story arc show <章号>       查看某章全维度状态
  python novel.py story arc character <名>   查看角色弧线
  python novel.py story arc item <物品名>     追踪物品弧线
  python novel.py story arc timeline          弧线时间线
  python novel.py story arc report            弧线健康报告
"""

import sys
import json
import sqlite3
from pathlib import Path
from src.cli.shared import (PROJECT_ROOT, _load_project_config, _get_default_slug,
    _get_active_db_path, _get_novel_id, _find_by_title,
    _get_story_dir, find_chapter_file)
from scripts.arc.arc_checker import ArcChecker, run_arc_check, SEVERITY


def _connect():
    db = _get_active_db_path()
    if not db or not db.exists():
        print("[ERROR] 未找到活跃数据库")
        sys.exit(1)
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    ArcChecker(Path(str(db)))  # ensure arc tables exist
    return conn


# ── arc show ──

def _arc_show(chapter_no: int):
    """Show full Story Arc state for a chapter."""
    conn = _connect()
    cur = conn.cursor()
    nid = _get_novel_id(cur)
    if nid is None:
        print("  当前小说未在数据库注册")
        conn.close()
        return

    # Chapter contexts
    cur.execute("""SELECT * FROM chapter_contexts
        WHERE novel_id=? AND chapter_no=?""", (nid, chapter_no))
    ctx = cur.fetchone()

    # Arc character states
    cur.execute("""SELECT c.name, a.* FROM arc_character_states a
        JOIN characters c ON c.id = a.character_id
        WHERE a.novel_id=? AND a.chapter_no=?""", (nid, chapter_no))
    char_rows = cur.fetchall()

    # Arc alignments
    cur.execute("""SELECT * FROM arc_alignments
        WHERE novel_id=? AND chapter_no=?
        ORDER BY alignment_type""", (nid, chapter_no))
    alignments = cur.fetchall()

    # Novel title
    cur.execute("SELECT title FROM novels WHERE id=?", (nid,))
    novel = cur.fetchone()
    title = novel["title"] if novel else str(nid)
    conn.close()

    print(f"\n{'='*60}")
    print(f"  Story Arc — 第{chapter_no}章 — 《{title}》")
    print(f"{'='*60}")

    if not ctx and not char_rows:
        print("  暂无数据。请先运行 post 生成上下文。")
        return

    # Arc character states table
    if char_rows:
        print(f"\n  📊 角色状态快照 ({len(char_rows)} 角色):")
        print(f"  {'角色':12s} {'身体':8s} {'情绪':10s} {'弧线进展'}")
        print(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*30}")
        for r in char_rows:
            emo_str = ""
            try:
                emo = json.loads(r["emotional_state"]) if isinstance(r["emotional_state"], str) else r["emotional_state"]
                if emo:
                    emo_str = f"{emo.get('state','')}"
                    if emo.get("intensity"):
                        emo_str += f"({emo['intensity']})"
            except Exception:
                pass
            print(f"  {r['name']:12s} {r['physical_state']:8s} {emo_str:10s} {r['arc_progress'][:30]}")
            # Show key decisions
            try:
                decisions = json.loads(r["key_decisions"]) if isinstance(r["key_decisions"], str) else (r["key_decisions"] or [])
            except Exception:
                decisions = []
            for d in decisions:
                print(f"    ↳ 决定: {d.get('decision','')[:60]}")

    # Context data (if exists)
    if ctx:
        try:
            locs = json.loads(ctx["character_locations"]) if isinstance(ctx["character_locations"], str) else ctx["character_locations"]
        except Exception:
            locs = {}
        try:
            items = json.loads(ctx["active_items"]) if isinstance(ctx["active_items"], str) else ctx["active_items"]
        except Exception:
            items = []

        if locs:
            print(f"\n  📍 人物位置:")
            for name, loc in locs.items():
                print(f"    {name}: {loc}")
        if items:
            print(f"\n  🎒 活跃物品: {', '.join(items)}")
        if ctx["world_state"]:
            print(f"\n  🌍 环境: {ctx['world_state'][:120]}")
        if ctx["ending_state"]:
            print(f"\n  🎬 结尾: {ctx['ending_state'][:120]}")

    # Arc alignments
    if alignments:
        print(f"\n  🔗 对齐记录 ({len(alignments)} 条):")
        for a in alignments:
            a_type = a["alignment_type"]
            icon = {"fulfillment": "✅", "setup": "📌", "progress": "⬆️"}.get(a_type, "•")
            print(f"    {icon} [{a_type}] {a.get('notes','')[:80]}")

    print()


# ── arc check ──

def _arc_check(min_ch=None, max_ch=None, check_types=None):
    """Run full arc break detection."""
    db = _get_active_db_path()
    if not db or not db.exists():
        print("[ERROR] 未找到活跃数据库")
        return 1

    conn = _connect()
    nid = _get_novel_id(conn.cursor())
    conn.close()
    if nid is None:
        print("  当前小说未在数据库注册")
        return 1

    types_list = None
    if check_types:
        types_list = [t.strip() for t in check_types.split(",")]

    result = run_arc_check(str(db), nid, min_ch or 1, max_ch, types_list)

    print(f"\n{'='*60}")
    print(f"  Story Arc 弧线检测报告")
    print(f"{'='*60}")
    print(f"  状态: {result['status']}")
    print(f"  发现: {result['total_findings']} 个问题 ({result['critical']}严重, {result['warnings']}警告, {result['infos']}提示)")
    print()

    if result["total_findings"] == 0:
        print("  ✅ 未检测到弧线断裂")
        print()
        return 0

    # Group by type
    by_type = {}
    for f in result["findings"]:
        by_type.setdefault(f["type"], []).append(f)

    type_names = {
        "physical_break": "角色身体状态断裂",
        "emotional_swing": "情绪弧线突变",
        "item_void": "物品弧线断裂",
        "promise_overdue": "承诺逾期未兑现",
        "promise_unaligned": "承诺无对齐记录",
        "thread_dormant": "情节线沉睡",
    }
    for ftype, findings in by_type.items():
        print(f"  ── {type_names.get(ftype, ftype)} ({len(findings)} 项) ──")
        for f in findings:
            sev = SEVERITY.get(f["severity"], "?")
            print(f"  {sev} {f['message']}")
        print()

    print(f"  ═══")
    return 0


# ── arc character ──

def _arc_character(char_name: str):
    """Show full character arc across all chapters."""
    conn = _connect()
    cur = conn.cursor()
    nid = _get_novel_id(cur)
    if nid is None:
        print("  当前小说未在数据库注册")
        conn.close()
        return

    # Find character
    cur.execute("SELECT id FROM characters WHERE novel_id=? AND name LIKE ?",
                (nid, f"%{char_name}%"))
    char_row = cur.fetchone()
    if not char_row:
        print(f"  未找到角色「{char_name}」")
        conn.close()
        return

    # Get all arc states
    cur.execute("""SELECT a.*, c.name FROM arc_character_states a
        JOIN characters c ON c.id = a.character_id
        WHERE a.novel_id=? AND a.character_id=?
        ORDER BY a.chapter_no""", (nid, char_row["id"]))
    rows = cur.fetchall()

    # Get novel title
    cur.execute("SELECT title FROM novels WHERE id=?", (nid,))
    novel = cur.fetchone()
    title = novel["title"] if novel else ""

    conn.close()

    if not rows:
        print(f"  「{char_name}」暂无弧线数据。请先运行 post 生成。")
        return

    print(f"\n{'='*60}")
    print(f"  角色弧线 — {rows[0]['name']} — 《{title}》")
    print(f"{'='*60}")
    print(f"  共 {len(rows)} 章记录\n")

    prev_phys = ""
    prev_emo = ""
    for r in rows:
        ch = r["chapter_no"]
        phys = r["physical_state"] or "—"
        try:
            emo_data = json.loads(r["emotional_state"]) if isinstance(r["emotional_state"], str) else (r["emotional_state"] or {})
        except Exception:
            emo_data = {}
        emo_str = f"{emo_data.get('state','—')}" if emo_data else "—"

        # Mark transitions
        phys_mark = ""
        if prev_phys and phys != prev_phys:
            phys_mark = f" ← {prev_phys}→{phys}"
        emo_mark = ""
        if prev_emo and emo_data.get("state") != prev_emo:
            emo_mark = f" ← {prev_emo}→{emo_data.get('state','')}"

        print(f"  第{ch:02d}章 | 身体: {phys:6s}{phys_mark}")
        print(f"         | 情绪: {emo_str:8s}{emo_mark}")
        if r["arc_progress"]:
            print(f"         | {r['arc_progress'][:60]}")

        try:
            decisions = json.loads(r["key_decisions"]) if isinstance(r["key_decisions"], str) else (r["key_decisions"] or [])
        except Exception:
            decisions = []
        for d in decisions:
            print(f"         | ↳ {d.get('decision','')[:50]}")
        print()
        prev_phys = phys
        prev_emo = emo_data.get("state", "") if emo_data else ""

    print()


# ── arc item ──

def _arc_item(item_name: str):
    """Track an item's full lifecycle across all chapters."""
    conn = _connect()
    cur = conn.cursor()
    nid = _get_novel_id(cur)
    if nid is None:
        print("  当前小说未在数据库注册")
        conn.close()
        return

    cur.execute("""SELECT chapter_no, active_items FROM chapter_contexts
        WHERE novel_id=? ORDER BY chapter_no""", (nid,))
    rows = cur.fetchall()
    conn.close()

    appearances = []
    for r in rows:
        ch = r["chapter_no"]
        try:
            items = json.loads(r["active_items"]) if isinstance(r["active_items"], str) else (r["active_items"] or [])
        except Exception:
            continue
        if item_name in items or any(item_name in i for i in items):
            appearances.append(ch)

    if not appearances:
        print(f"  未找到物品「{item_name}」的轨迹")
        return

    print(f"\n  物品弧线 — 「{item_name}」")
    print(f"  {'─'*40}")
    # Visual bar
    if len(appearances) >= 2:
        bar = ""
        last = appearances[0]
        for ch in range(appearances[0], appearances[-1] + 1):
            if ch in appearances:
                bar += "█"
                last = ch
            elif ch - last <= 3:
                bar += "░"
            else:
                bar += "·"
        print(f"  {bar}")

    print(f"  出现: Ch{appearances[0]} → Ch{appearances[-1]}")
    if len(appearances) >= 2:
        for i in range(len(appearances) - 1):
            gap = appearances[i + 1] - appearances[i]
            if gap > 3:
                print(f"    ⚠️  第{appearances[i]}章 → 第{appearances[i+1]}章，间隔{gap}章")
    print()


# ── arc timeline ──

def _arc_timeline():
    """Show combined timeline of all arcs."""
    conn = _connect()
    cur = conn.cursor()
    nid = _get_novel_id(cur)
    if nid is None:
        print("  当前小说未在数据库注册")
        conn.close()
        return

    # Plot threads
    cur.execute("""SELECT title, thread_type, status, introduced_chapter, resolved_chapter
        FROM plot_threads WHERE novel_id=? ORDER BY introduced_chapter""", (nid,))
    threads = cur.fetchall()

    # Promises
    cur.execute("""SELECT promise_title, status, introduced_chapter, payoff_chapter
        FROM reader_promises WHERE novel_id=? ORDER BY introduced_chapter""", (nid,))
    promises = cur.fetchall()

    # Arc alignments
    cur.execute("""SELECT alignment_type, chapter_no, notes FROM arc_alignments
        WHERE novel_id=? ORDER BY chapter_no""", (nid,))
    alignments = cur.fetchall()

    # Characters with arc states
    cur.execute("""SELECT DISTINCT c.name FROM arc_character_states a
        JOIN characters c ON c.id = a.character_id
        WHERE a.novel_id=?""", (nid,))
    arc_chars = [r[0] for r in cur.fetchall()]

    # Chapter range
    cur.execute("SELECT MIN(chapter_no), MAX(chapter_no) FROM chapter_contexts WHERE novel_id=?", (nid,))
    ch_range = cur.fetchone()
    conn.close()

    min_ch = ch_range[0] or 1
    max_ch = ch_range[1] or 1

    print(f"\n{'='*60}")
    print(f"  Story Arc 时间线 (第{min_ch}-{max_ch}章)")
    print(f"{'='*60}\n")

    # Plot threads
    if threads:
        print(f"  ── 情节线 ({len(threads)} 条) ──")
        for t in threads:
            status_icon = "✅" if t["status"] == "resolved" else "🔄"
            intro = t["introduced_chapter"] or "?"
            res = t["resolved_chapter"] or "…"
            print(f"  {status_icon} {t['title']:<20s} [Ch{intro} → Ch{res}] {t['thread_type']}")
        print()

    # Promises
    if promises:
        print(f"  ── 读者承诺 ({len(promises)} 条) ──")
        for p in promises:
            icon = "✅" if p["status"] == "fulfilled" else ("❓" if p["status"] == "open" else "📌")
            intro = p["introduced_chapter"] or "?"
            payoff = p["payoff_chapter"] or "…"
            print(f"  {icon} {p['promise_title']:<25s} [Ch{intro} → Ch{payoff}]")
        print()

    # Characters with arcs
    if arc_chars:
        print(f"  ── 角色弧线 ({len(arc_chars)} 角色) ──")
        for name in arc_chars:
            print(f"      {name}")
        print()

    # Alignment marks
    if alignments:
        print(f"  ── 对齐标记 ({len(alignments)} 条) ──")
        for a in alignments:
            icon = {"fulfillment": "✅", "setup": "📌", "progress": "⬆️"}.get(a["alignment_type"], "•")
            print(f"  {icon} 第{a['chapter_no']}章 [{a['alignment_type']}] {a.get('notes','')[:60]}")
        print()


# ── arc report ──

def _arc_report():
    """Generate full arc health report."""
    conn = _connect()
    cur = conn.cursor()
    nid = _get_novel_id(cur)
    if nid is None:
        print("  当前小说未在数据库注册")
        conn.close()
        return 1

    cur.execute("SELECT title FROM novels WHERE id=?", (nid,))
    novel = cur.fetchone()
    title = novel["title"] if novel else ""

    # Counts
    cur.execute("SELECT COUNT(*) FROM chapter_contexts WHERE novel_id=?", (nid,))
    ctx_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT character_id) FROM arc_character_states WHERE novel_id=?", (nid,))
    row = cur.fetchone()
    arc_char_count = row[0] if row else 0

    cur.execute("SELECT COUNT(*) FROM arc_character_states WHERE novel_id=?", (nid,))
    arc_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM arc_alignments WHERE novel_id=?", (nid,))
    align_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM reader_promises WHERE novel_id=? AND status='open'", (nid,))
    open_promises = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM plot_threads WHERE novel_id=? AND status='active'", (nid,))
    active_threads = cur.fetchone()[0]

    # Latest chapter
    cur.execute("SELECT MAX(chapter_no) FROM chapter_contexts WHERE novel_id=?", (nid,))
    max_ch = cur.fetchone()[0] or 0
    conn.close()

    print(f"\n{'='*60}")
    print(f"  Story Arc 健康报告 — 《{title}》")
    print(f"{'='*60}\n")
    print(f"  总章节数:       {ctx_count}")
    print(f"  已写至:         第{max_ch}章")
    print(f"  角色弧线覆盖:   {arc_char_count} 角色, {arc_count} 记录")
    print(f"  对齐记录:       {align_count} 条")
    print(f"  开放承诺:       {open_promises} 条")
    print(f"  活跃线索:       {active_threads} 条")
    print()

    # Run quick check
    result = run_arc_check(str(_get_active_db_path()), nid)
    if result["total_findings"] > 0:
        print(f"  ── 快速检测发现 {result['total_findings']} 个问题 ──")
        by_sev = {
            "critical": [f for f in result["findings"] if f["severity"] == "critical"],
            "warning": [f for f in result["findings"] if f["severity"] == "warning"],
            "info": [f for f in result["findings"] if f["severity"] == "info"],
        }
        if by_sev["critical"]:
            print(f"\n  ❌ 严重 ({len(by_sev['critical'])}):")
            for f in by_sev["critical"][:5]:
                print(f"    {f['message']}")
        if by_sev["warning"]:
            print(f"\n  ⚠️ 警告 ({len(by_sev['warning'])}):")
            for f in by_sev["warning"][:5]:
                print(f"    {f['message']}")
        if by_sev["info"] and len(by_sev["info"]) <= 5:
            print(f"\n  ℹ️ 提示 ({len(by_sev['info'])}):")
            for f in by_sev["info"][:5]:
                print(f"    {f['message']}")
    else:
        print(f"  ✅ 弧线健康")

    print(f"\n  详细检查: python novel.py story arc check")
    print()
    return 0


# ── main dispatch ──

def cmd_arc(args):
    action = getattr(args, "arc_action", "check")

    if action == "show":
        chapter_no = getattr(args, "chapter_no", None)
        if not chapter_no:
            print("用法: python novel.py story arc show <章节号>")
            return 1
        try:
            chapter_no = int(chapter_no)
        except ValueError:
            print(f"[ERROR] 无效章节号: {chapter_no}")
            return 1
        return _arc_show(chapter_no)

    elif action == "check":
        min_ch = getattr(args, "min_chapter", None)
        max_ch = getattr(args, "max_chapter", None)
        check_types = getattr(args, "check_type", None)
        return _arc_check(min_ch, max_ch, check_types)

    elif action == "character":
        char_name = getattr(args, "character_name", "")
        if not char_name:
            print("用法: python novel.py story arc character <角色名>")
            return 1
        return _arc_character(char_name)

    elif action == "item":
        item_name = getattr(args, "item_name", "")
        if not item_name:
            print("用法: python novel.py story arc item <物品名>")
            return 1
        return _arc_item(item_name)

    elif action == "timeline":
        return _arc_timeline()

    elif action == "report":
        return _arc_report()

    else:
        print("用法: python novel.py story arc {check|show|character|item|timeline|report}")
        print()
        print("  check              全维度弧线检测")
        print("  show <章号>         查看某章全维度状态")
        print("  character <角色名>  查看角色弧线")
        print("  item <物品名>       追踪物品弧线")
        print("  timeline            弧线时间线")
        print("  report              弧线健康报告")
        print()
        print("  选项:")
        print("    --min <N>          起始章 (默认1)")
        print("    --max <N>          结束章")
        print("    --type <类型>       检测类型: physical,emotional,item,promise,thread")
        return 1
