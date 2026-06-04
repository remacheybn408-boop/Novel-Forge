"""src/cli/commands_pipeline.py — Pipeline commands (pre/post/review/export) v0.6.7"""

from src.cli.shared import (PROJECT_ROOT, SCRIPTS_DIR, _load_project_config,
    _cfg_path, _get_default_slug, _get_novels_root, _resolve_post_context,
    _story_exists, _get_workspace_dir, _get_active_db_path, _check_outline_gate)
import sys
from pathlib import Path
from scripts.config_utils import resolve_path


def cmd_pre(chapter_no: str = None, slug: str = None, volume_no: str = None):
    """Run pre-write gate for a chapter."""
    cfg = PROJECT_ROOT / "config.json"
    if not chapter_no:
        print("Usage: python novel.py pre <chapter_no> [--slug <slug>] [--volume <n>]")
        return 1
    # No-outline gate
    if _check_outline_gate():
        return 1
    print(f"  Running pre-write gate for chapter {chapter_no}...")
    # v0.6.7-clean7: resolve slug from active slot
    chapters_dir, slot_db_path, resolved_slug, resolved_title = _resolve_post_context(cfg)
    slug = slug or resolved_slug
    try:
        import subprocess
        cmd = [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "pre", str(chapter_no),
               "--config", str(cfg), "--novel-slug", slug,
               "--novel-title", resolved_title]
        if volume_no: cmd.extend(["--volume-no", str(volume_no)])
        result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), timeout=120)
        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


def cmd_post(chapter_no: str = None, slug: str = None, volume_no: str = None, file_path: str = None, story: bool = False, no_jury: bool = False):
    """Post-write: run guards and ingest."""
    cfg = PROJECT_ROOT / "config.json"
    if not chapter_no and not file_path:
        print("Usage: python novel.py post <chapter_no> [--file <path>] [--slug <slug>] [--story]")
        return 1
    # No-outline gate
    if _check_outline_gate():
        return 1
    if file_path:
        print(f"  Running post-write guards for file: {file_path}")
    else:
        print(f"  Running post-write guards for chapter {chapter_no}...")

    # v0.6.7-clean6: Resolve from active slot, fallback to config
    chapters_dir, slot_db_path, resolved_slug, resolved_title = _resolve_post_context(cfg)
    slug = slug or resolved_slug

    try:
        import subprocess
        # v0.6.7: Auto-run pre if pipeline_state missing
        ch_no_str = str(chapter_no) if chapter_no else "1"
        state_path = PROJECT_ROOT / "exports" / "pipeline_state" / f"chapter_{int(ch_no_str):03d}_state.json"
        if not state_path.exists():
            print(f"  [pre] 未检测到任务卡状态，自动运行 pre...")
            pre_cmd = [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "pre",
                       ch_no_str, "--config", str(cfg), "--novel-slug", slug]
            if volume_no: pre_cmd.extend(["--volume-no", str(volume_no)])
            pre_result = subprocess.run(pre_cmd, cwd=str(PROJECT_ROOT), timeout=120)
            if pre_result.returncode != 0:
                print(f"  [pre] 自动 pre 失败，请手动运行 python novel.py pre {ch_no_str}")
                return pre_result.returncode
            print(f"  [pre] 任务卡已生成，继续 post...\n")
        cmd = [sys.executable, str(SCRIPTS_DIR / "chapter_pipeline.py"), "post",
               str(chapter_no) if chapter_no else "1",
               "--config", str(cfg), "--novel-slug", slug]
        if volume_no: cmd.extend(["--volume-no", str(volume_no)])
        if file_path:
            cmd.extend(["--chapters-dir", str(Path(file_path).parent)])
        else:
            cmd.extend(["--chapters-dir", chapters_dir])
        if slot_db_path:
            cmd.extend(["--db-path", slot_db_path])
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

        # Auto-run agent jury after post (default ON, use --no-jury to skip)
        if not no_jury and result.returncode == 0:
            try:
                print()
                print("  [jury] 自动运行 Agent 陪审团...")
                ch_no = int(chapter_no) if chapter_no else 1
                import argparse as _ap
                from src.cli.commands_agents import cmd_agents
                _ns = _ap.Namespace(
                    agents_action="review", chapter_no=str(ch_no),
                    mode="light", slug=slug, genre=None, style=None
                )
                cmd_agents(_ns)
            except Exception as e:
                print(f"  [jury] 跳过: {e}")

        return result.returncode
    except Exception as e:
        print(f"  [ERROR] {e}")
        return 1


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
    """Export novel to a single file, v0.6.7-clean7: 用小说名建文件夹."""
    # v0.6.7-clean7: 无slug时自动从活跃slot读取
    if not slug:
        try:
            import json as _j, sqlite3 as _s
            ws = PROJECT_ROOT / "workspace"
            reg = _j.loads((ws / "registry.json").read_text(encoding="utf-8"))
            active = reg.get("active_slot", "")
            slot_db = ws / active / "novel.db"
            if slot_db.exists():
                conn = _s.connect(str(slot_db))
                row = conn.execute("SELECT slug FROM novels LIMIT 1").fetchone()
                conn.close()
                if row:
                    slug = row[0]
        except Exception:
            pass
    if not slug:
        print("用法: python novel.py export [--slug <标识>] [--format txt|md]")
        print()
        print("  示例:")
        print("    python novel.py export --slug demo_novel --format md")
        print("    python novel.py export --slug demo_novel --format txt")
        return 1
    fmt = fmt or "md"
    ext = ".txt" if fmt == "txt" else ".md"

    # v0.6.7-clean7: 从活跃 slot DB 读取标题 + DB 路径
    import sqlite3 as _sql
    title = slug
    slot_db_path = None
    try:
        ws = PROJECT_ROOT / "workspace"
        reg_file = ws / "registry.json"
        if reg_file.exists():
            import json as _json
            reg = _json.loads(reg_file.read_text(encoding="utf-8"))
            active = reg.get("active_slot", "")
            slot_db = ws / active / "novel.db"
            if slot_db.exists():
                slot_db_path = slot_db
                conn = _sql.connect(str(slot_db))
                row = conn.execute("SELECT title FROM novels WHERE slug=?", (slug,)).fetchone()
                if row:
                    title = row[0]
                conn.close()
    except Exception:
        pass

    # 输出到小说自己的文件夹：novels_root/{书名}/{书名}.txt
    cfg = _load_project_config()
    nr = Path(_get_novels_root())
    out_dir = nr / title
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{title}{ext}"

    print(f"  正在导出小说「{title}」(slug={slug})，格式: {fmt}...")
    import subprocess
    try:
        args = [sys.executable, str(SCRIPTS_DIR / "export_novel.py"),
                "--slug", slug, "--config", str(PROJECT_ROOT / "config.json"), "--format", fmt,
                "--output", str(out_path)]
        if slot_db_path:
            args.extend(["--db-path", str(slot_db_path)])
        result = subprocess.run(args, cwd=str(PROJECT_ROOT), timeout=60, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        if result.returncode == 0:
            print(f"  ✅ 已导出全书到 {out_path}")
            # v0.6.7-clean7: 同时拆分每章为独立文件
            full_text = Path(out_path).read_text(encoding="utf-8")
            # Split by chapter headers: 第N章 or ---\n第N章
            import re as _re
            parts = _re.split(r'\n(?=第\d+章\s)', full_text)
            count = 0
            seen = set()
            for part in parts:
                m = _re.match(r'第(\d+)章\s+(.+)', part.strip())
                if m:
                    ch_num = int(m.group(1))
                    if ch_num in seen:
                        continue
                    seen.add(ch_num)
                    ch_title = m.group(2).strip().split('\n')[0][:20]
                    ch_file = out_dir / f"第{ch_num}章_{ch_title}.txt"
                    ch_file.write_text(part.strip() + "\n", encoding="utf-8")
                    count += 1
            if count:
                print(f"  ✅ 已拆分 {count} 章到 {out_dir}/")
        else:
            print(f"  ⚠️ 导出未完成（退出码: {result.returncode}）")
        return result.returncode
    except subprocess.TimeoutExpired:
        print(f"  ⏱️ 导出超时，请检查章节数量是否过多。")
        return 1
    except Exception as e:
        print(f"  ❌ 导出失败: {e}")
        return 1
