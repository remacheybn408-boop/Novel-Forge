#!/usr/bin/env python3
"""commands_menu.py — CLI menu commands, JSON-driven via scc_menu_renderer."""

from src.cli.shared import PROJECT_ROOT
from version import get_version
import subprocess
import sys
from pathlib import Path


# ── Helpers ────────────────────────────────────────────────────

def _run_cmd(cmd: str):
    """Run novel.py command in subprocess."""
    r = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "novel.py")] + cmd.split(),
        cwd=str(PROJECT_ROOT), timeout=120,
    )
    if r.returncode != 0:
        print(f"  ⚠️  命令返回非零: {r.returncode}")


def _menu_confirm_dangerous(prompt_text="确认执行此操作？"):
    """Require YES input for dangerous operations."""
    print()
    print(f"  ⚠️  {prompt_text}")
    answer = input("  输入 YES 确认，其他任意键取消: ").strip()
    return answer == "YES"


def _ask(prompt: str, required: bool = False) -> str:
    """Ask for input with prompt."""
    val = input(f"  {prompt}: ").strip()
    if required and not val:
        print("  ❌ 不能为空。")
    return val


def _get_section_items(section_id: str) -> list:
    """Get items for a JSON menu section."""
    try:
        from scripts.scc_menu_renderer import render_section_items
        return render_section_items(section_id)
    except Exception:
        return []


# ── Generic interactive sub-menu runner ────────────────────────

def _interactive(section_id: str, action_map: dict = None):
    """Generic interactive sub-menu driven by JSON section.

    action_map: {0-indexed-item-index: callable(item)} for items
    that need custom interactive logic. Items not in map are auto-run.
    """
    items = _get_section_items(section_id)
    if not items:
        print(f"  [ERROR] 菜单 section '{section_id}' 未找到。")
        return
    if action_map is None:
        action_map = {}

    from scripts.scc_menu_renderer import get_section
    section = get_section(section_id)
    title = section["title"] if section else section_id

    while True:
        print()
        print("  " + "─" * 50)
        print(f"  【{title}】")
        print("  " + "─" * 50)
        for i, item in enumerate(items, 1):
            prefix = "⚠ " if item.get("danger") == "dangerous" else "  "
            label = item.get("label", "")
            if len(label) > 55:
                label = label[:52] + "..."
            print(f"  [{i}] {prefix}{label}")
        print("  [0] 返回主菜单")
        print()
        choice = input(f"  请选择 [0-{len(items)}]: ").strip()

        if choice == "0":
            break
        if not choice.isdigit():
            print("  无效选择，请重试。")
            continue

        idx = int(choice) - 1
        if idx < 0 or idx >= len(items):
            print("  无效选择，请重试。")
            continue

        item = items[idx]
        if item.get("danger") == "dangerous":
            if not _menu_confirm_dangerous(f"将执行: {item['label']}"):
                continue

        if idx in action_map:
            action_map[idx](item)
        else:
            cmd = item.get("command", "")
            if cmd:
                _run_cmd(cmd)


# ── Section-specific handlers ──────────────────────────────────

def _handle_archive():
    """小说档案库 sub-menu."""
    def _new(item):
        name = _ask("新 slot 名称", required=True)
        if name:
            _run_cmd(f'db new --name "{name}"')

    def _use(item):
        sid = _ask("slot ID (如 slot_002)")
        if sid:
            _run_cmd(f"db use {sid}")

    def _delete(item):
        sid = _ask("要删除的 slot ID")
        if sid:
            _run_cmd(f"db delete {sid}")

    def _restore(item):
        sid = _ask("要恢复的 slot ID")
        if sid:
            _run_cmd(f"db restore {sid}")

    _interactive("archive", {2: _new, 3: _use, 5: _delete, 6: _restore})


def _handle_outline():
    """大纲管理 sub-menu."""
    def _add(item):
        fp = _ask("大纲文件路径", required=True)
        if fp:
            title = _ask("标题（可选）")
            cmd = f'outline add "{fp}"'
            if title:
                cmd += f' --title "{title}"'
            _run_cmd(cmd)

    def _switch(item):
        oid = _ask("大纲 ID")
        if oid:
            _run_cmd(f"outline switch {oid}")

    def _diff(item):
        id1 = _ask("大纲1 ID")
        id2 = _ask("大纲2 ID")
        if id1 and id2:
            _run_cmd(f"outline diff {id1} {id2}")

    def _rollback(item):
        oid = _ask("大纲 ID")
        if oid:
            _run_cmd(f"outline rollback {oid}")

    _interactive("outline", {0: _add, 3: _switch, 4: _diff, 5: _rollback, 6: None})


def _handle_writing():
    """写作流程 sub-menu."""
    def _pre(item):
        ch = _ask("章节号", required=True)
        if ch:
            _run_cmd(f"pre {ch}")

    def _post(item):
        ch = _ask("章节号", required=True)
        if ch:
            _run_cmd(f"post {ch}")

    def _wc(item):
        fp = _ask("章节号或文件路径")
        if fp:
            _run_cmd(f"wc {fp}")

    def _review(item):
        ch = _ask("章节号", required=True)
        if ch:
            _run_cmd(f"review {ch}")

    _interactive("writing", {0: _pre, 1: _post, 2: _wc, 3: _review})


def _handle_jury():
    """Agent 陪审团 sub-menu."""
    def _review_light(item):
        ch = _ask("章节号", required=True)
        if ch:
            _run_cmd(f"agents review {ch} --mode light")

    def _review_full(item):
        ch = _ask("章节号", required=True)
        if ch:
            _run_cmd(f"agents review {ch} --mode full")

    def _review_genre(item):
        ch = _ask("章节号", required=True)
        genre = _ask("题材（如 xianxia）")
        if ch and genre:
            _run_cmd(f"agents review {ch} --genre {genre}")

    _interactive("jury", {0: _review_light, 1: _review_full, 2: _review_genre})


def _handle_character():
    """角色管理 sub-menu."""
    def _show(item):
        name = _ask("角色名", required=True)
        if name:
            _run_cmd(f"character show {name}")

    def _create(item):
        name = _ask("角色名", required=True)
        if name:
            _run_cmd(f"character create {name}")

    def _edit(item):
        name = _ask("角色名", required=True)
        field = _ask("字段 (如 core / habits / identity)")
        value = _ask("值")
        if name and field and value:
            _run_cmd(f'character edit {name} {field} "{value}"')

    def _delete(item):
        name = _ask("角色名")
        if name:
            _run_cmd(f"character delete {name}")

    def _mental(item):
        name = _ask("角色名", required=True)
        if name:
            _run_cmd(f"character mental {name}")

    _interactive("character", {1: _show, 2: _create, 3: _edit, 4: _delete, 6: _mental})


def _handle_quality():
    """质量检测 sub-menu."""
    def _texture(item):
        ch = _ask("章节号", required=True)
        if ch:
            _run_cmd(f"texture check {ch}")

    def _voice(item):
        ch = _ask("章节号", required=True)
        if ch:
            _run_cmd(f"voice check {ch}")

    def _check(item):
        fp = _ask("文件路径", required=True)
        if fp:
            _run_cmd(f'check "{fp}"')

    _interactive("quality", {0: _texture, 1: _voice, 3: _check})


def _handle_report():
    """报告与导出 sub-menu."""
    def _export_txt(item):
        slug = _ask("小说 slug（可选）")
        _run_cmd(f"export --format txt {f'--slug {slug}' if slug else ''}")

    def _export_md(item):
        slug = _ask("小说 slug（可选）")
        _run_cmd(f"export --format md {f'--slug {slug}' if slug else ''}")

    _interactive("report", {1: _export_txt, 2: _export_md})


def _handle_memory():
    """项目记忆查询 sub-menu."""
    def _query(item):
        q = _ask("问题", required=True)
        if q:
            _run_cmd(f'query "{q}"')

    def _learn_add(item):
        rule = _ask("规则内容", required=True)
        if rule:
            _run_cmd(f'learn add "{rule}"')

    def _rag_query(item):
        q = _ask("问题", required=True)
        if q:
            _run_cmd(f'rag query "{q}"')

    _interactive("memory", {0: _query, 2: _learn_add, 3: _rag_query})


# ── Section routing ────────────────────────────────────────────

_SECTION_ROUTES = {
    "start": lambda: _interactive("start"),
    "archive": _handle_archive,
    "outline": _handle_outline,
    "writing": _handle_writing,
    "jury": _handle_jury,
    "character": _handle_character,
    "quality": _handle_quality,
    "report": _handle_report,
    "memory": _handle_memory,
}


def _route_to_section(section_id: str):
    """Route to the appropriate interactive handler for a section."""
    handler = _SECTION_ROUTES.get(section_id)
    if handler:
        handler()


# ── Header / confirm helpers (kept from original) ─────────────

def _show_header():
    """Show menu header with project status."""
    print()
    print("=" * 64)
    print(f"  小说写作引擎 Novel Forge {get_version()}")
    print("=" * 64)

    try:
        import json as _json
        ws_dir = PROJECT_ROOT / "workspace"
        reg = ws_dir / "registry.json"
        if reg.exists():
            data = _json.loads(reg.read_text(encoding="utf-8"))
            active = data.get("active_slot", "")
            slot_name = ""
            for s in data.get("slots", []):
                if s.get("id") == active:
                    slot_name = s.get("name", "")
                    break
            print(f"  DB Slot: {active} ({slot_name})" if slot_name and active else f"  DB Slot: {active or '(未初始化)'}")
        else:
            print("  DB Slot: (未初始化)")
    except Exception:
        print("  DB Slot: (读取失败)")

    try:
        from src.cli.shared import _get_outline_manager
        mgr = _get_outline_manager()
        cur = mgr.current_outline()
        if cur:
            print(f"  大纲: {cur.get('title', '')} [{cur.get('id', '')}]  "
                  f"{cur.get('chapter_count', 0)}章/{cur.get('volume_count', 1)}卷")
        else:
            print("  大纲: (未设定)")
    except Exception:
        print("  大纲: (不可用)")

    print("-" * 64)


# ── Top-level commands ─────────────────────────────────────────

def cmd_scc_help():
    """Print user guide from JSON."""
    try:
        from scripts.scc_menu_renderer import render_user_guide
        print(render_user_guide())
    except Exception as e:
        print(f"  [ERROR] 无法加载操作手册: {e}")
    return 0


def cmd_menu_show():
    """Show main menu text (from JSON)."""
    try:
        from scripts.scc_menu_renderer import render_main_menu, load_project_status
        status = load_project_status()
        print(render_main_menu(status, style="cli"))
    except Exception as e:
        print(f"  [ERROR] 无法渲染菜单: {e}")
    return 0


def cmd_menu_text():
    """Output project status JSON."""
    import json as _json
    try:
        from scripts.scc_menu_renderer import load_project_status
        status = load_project_status()
        print(_json.dumps(status, ensure_ascii=False))
    except Exception as e:
        print(_json.dumps({"error": str(e)}, ensure_ascii=False))
    return 0


def cmd_chapters():
    """List all chapters of current novel."""
    import json as _json
    import sqlite3 as _sql
    ws = PROJECT_ROOT / "workspace"
    reg_file = ws / "registry.json"
    if not reg_file.exists():
        print("  workspace 未初始化。")
        return 1

    reg = _json.loads(reg_file.read_text(encoding="utf-8"))
    active = reg.get("active_slot", "")
    if not active:
        print("  没有活跃 slot。")
        return 1

    slot_dir = ws / active
    db_path = slot_dir / "novel.db"
    if not db_path.exists():
        print(f"  {active} 没有 novel.db")
        return 1

    conn = _sql.connect(str(db_path))
    conn.row_factory = _sql.Row
    rows = conn.execute(
        "SELECT chapter_no, title, word_count, status, created_at FROM chapters ORDER BY chapter_no"
    ).fetchall()
    novel_row = conn.execute("SELECT title FROM novels LIMIT 1").fetchone()
    novel_title = novel_row["title"] if novel_row else active
    conn.close()

    print()
    print(f"  📖 {novel_title} ({active})")
    print(f"  " + "─" * 50)
    if not rows:
        print("  (暂无章节)")
    else:
        total_wc = 0
        for r in rows:
            total_wc += r["word_count"] or 0
            print(f"  第{r['chapter_no']:02d}章  {r['title'] or '(无标题)':20s}  {r['word_count'] or 0:>5,}字  [{r['status']}]")
        print(f"  " + "─" * 50)
        print(f"  共 {len(rows)} 章，{total_wc:,} 字")
    print()
    return 0


def cmd_setup():
    """Interactive setup — configure novel folder path."""
    import json as _json
    cfg_file = PROJECT_ROOT / "config.json"

    print()
    print("  " + "=" * 55)
    print("  📁 项目设置 — 配置小说文件夹")
    print("  " + "=" * 55)
    print()

    try:
        cfg = _json.loads(cfg_file.read_text(encoding="utf-8"))
    except Exception:
        cfg = {"novels_root": "./novels", "paths": {}}

    current = cfg.get("novels_root", "未设置")
    print(f"  当前小说文件夹: {current}")
    print()
    print("  你的小说章节文件放在哪个文件夹？")
    print("  例如: D:\\小说  或  E:\\我的小说")
    print()
    print("  提示:")
    print("  · 文件夹下会自动创建「大纲/」「导出/」子目录")
    print("  · 每部小说会有自己的子文件夹")
    print("  · 可以随时修改")
    print()

    try:
        new_path = input("  请输入路径 (回车保留当前): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return 0

    if not new_path:
        print("  已取消，保持原设置。")
        return 0

    p = Path(new_path)
    if not p.is_absolute():
        print(f"  ⚠️ 请输入完整路径（如 D:\\小说），不要用相对路径。")
        return 1

    try:
        p.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"  ⚠️ 无法创建目录: {e}")

    if "paths" not in cfg:
        cfg["paths"] = {}
    cfg["novels_root"] = str(p)
    cfg["paths"]["novels_root"] = str(p)
    cfg_file.write_text(_json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"  ✅ 小说文件夹已设置为: {p}")
    print(f"     每部小说一个子文件夹，大纲、章节、导出都在里面")
    print()
    print(f"  现在把大纲.txt放到小说文件夹（如 {p / '旧楼深处/大纲.txt'}），")
    print(f"  然后运行 python novel.py outline add")
    print()
    return 0


def cmd_menu():
    """Interactive text menu — JSON-driven, with input() loop."""
    from scripts.scc_menu_renderer import get_sections

    while True:
        _show_header()
        sections = get_sections(exclude_faq=True)

        print("  主菜单:")
        print("  " + "─" * 40)
        for i, sec in enumerate(sections, 1):
            # Strip emoji for cleaner menu
            title = sec["title"]
            print(f"  [{i}] {title}")
        print("  [C] 章节列表")
        print("  [S] 项目设置")
        print("  [0] 退出")
        choice = input("  请选择 [0-9/C/S]: ").strip()

        if choice == "0":
            print()
            print("  再见！")
            print()
            break

        if choice.upper() == "C":
            cmd_chapters()
            continue

        if choice.upper() == "S":
            cmd_setup()
            continue

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(sections):
                _route_to_section(sections[idx]["id"])
            else:
                print("  无效选择，请重试。")
        else:
            print("  无效选择，请重试。")

    return 0
