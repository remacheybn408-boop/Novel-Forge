"""menu_provider.py — 中文菜单生成器

委托 scripts.scc_menu_renderer 渲染菜单。
不暴露终端命令。
"""

from pathlib import Path
from scripts.scc_menu_renderer import load_project_status, render_main_menu as _render


def render_main_menu() -> str:
    """生成主菜单（委托 scc_menu_renderer）。"""
    status = load_project_status()
    return _render(status, style="mcp")


def render_status_text(output: str) -> str:
    """将 status 命令输出转为更友好的中文格式。"""
    return output


def render_chapter_list(chapters_output: str) -> str:
    """将 chapters 命令输出转为中文格式。"""
    if not chapters_output or chapters_output.strip() == "":
        return "当前没有章节数据。"
    return chapters_output
