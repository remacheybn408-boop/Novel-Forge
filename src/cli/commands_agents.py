"""src/cli/commands_agents.py — Agent review board commands v0.6.7"""

from src.cli.shared import (PROJECT_ROOT, SCRIPTS_DIR, _load_project_config,
    _cfg_path, _get_default_slug, _get_novels_root, _resolve_post_context)
import sys
import json
from pathlib import Path
from scripts.config_utils import resolve_path


def _cmd_agents_list(args):
    """List all available agent configurations with metadata."""
    import json as _json
    import yaml as _yaml

    agents_dir = PROJECT_ROOT / "configs" / "jury" / "agents"
    mode_filter = getattr(args, "mode", None) or ""

    if not agents_dir.exists():
        print("  No agent configurations found.")
        print(f"  Expected: {agents_dir}")
        return 1

    agent_files = sorted(agents_dir.glob("*.yaml"))
    if not agent_files:
        print("  No agent YAML files found.")
        return 0

    print("=" * 70)
    print(f"  Agent 陪审团 — {len(agent_files)} 个审查代理")
    print("=" * 70)
    print()

    # Load jury mode configs to show per-mode agents
    modes_dir = PROJECT_ROOT / "configs" / "jury"
    mode_agents = {}
    for mf in sorted(modes_dir.glob("jury.*.yaml")):
        try:
            mode_data = _yaml.safe_load(mf.read_text(encoding="utf-8"))
            mode_name = mode_data.get("mode", mf.stem.replace("jury.", ""))
            mode_agents[mode_name] = mode_data.get("agents", [])
        except Exception:
            pass

    for af in agent_files:
        try:
            data = _yaml.safe_load(af.read_text(encoding="utf-8"))
        except Exception:
            print(f"  {af.stem:30s} [无法解析]")
            continue

        agent_id = data.get("agent_id", af.stem)
        name = data.get("name", agent_id)
        category = data.get("category", "unknown")
        risk = data.get("risk_level", "medium")
        enabled = data.get("default_enabled", True)
        weight = data.get("weight", 1.0)
        desc = data.get("description", "")
        if len(desc) > 80:
            desc = desc[:77] + "..."

        # Which modes include this agent?
        in_modes = [m for m, ags in mode_agents.items() if agent_id in ags]

        status_icon = "✓" if enabled else "○"
        risk_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(risk, "⚪")

        print(f"  {status_icon} {risk_icon} {name:<24s} [{agent_id}]")
        print(f"     类别: {category:<15s} 权重: {weight:.1f}  模式: {','.join(in_modes) if in_modes else '(未分配)'}")
        print(f"     {desc}")
        print()

    print("-" * 70)
    print(f"  共 {len(agent_files)} 个代理   ✓=默认启用  ○=需手动启用")
    print(f"  🔴=高风险  🟡=中风险  🟢=低风险")
    print("=" * 70)
    return 0


def cmd_agents(args):
    """Multi-agent review board."""
    action = getattr(args, "agents_action", None)

    # agents list — show all available agents
    if action == "list":
        return _cmd_agents_list(args)

    if action != "review":
        print("Usage: python novel.py agents {list|review}")
        print("  list                     — 列出所有可用审查代理")
        print("  review <N> [--mode ...]  — 运行多Agent审稿")
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
            print(f"[ERROR] 找不到第{chapter_no}章文件 (目录: {ch_dir})")
            print(f"  请指定 --slug 参数，如: python novel.py agents review {chapter_no} --slug 格物证道")
            return 1
        else:
            content = candidates[0].read_text(encoding="utf-8")

        mode = getattr(args, "mode", "light")
        print(f"Running {mode}-mode agent review for chapter {chapter_no}...")
        from scripts.agents.orchestrator import run_agent_review
        result = run_agent_review(content, int(chapter_no), mode=mode)
        print(f"  Score: {result.get('overall_score', 'N/A')}")
        print(f"  Status: {result.get('status', 'N/A')}")
        if result.get('status') == 'FAIL':
            print(f"  💡 审稿 FAIL ≠ 程序出错，是 AI 对内容质量的建议，可忽略")
        chief = result.get("chief_editor", {})
        for cat in ["must_fix", "should_fix", "keep"]:
            items = chief.get(cat, [])
            if items:
                print(f"  {cat}: {len(items)} items")
        return 0
    except Exception as e:
        print(f"  [ERROR] Agent review failed: {e}")
        return 1
