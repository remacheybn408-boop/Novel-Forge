"""mental_state_crud.py — 精神状态独立文件 CRUD v0.7.1

与 voice_cards 解耦，独立存储在 mental_states/<set>/<角色>.json。
按 slot 隔离，卡组体系复用 voice_cards 的 active_set 配置。
"""
import json
from pathlib import Path


# ── 15 类精神状态维度定义 ──
MENTAL_STATE_CATEGORIES = [
    "抑郁症", "PTSD", "焦虑症", "强迫症", "PTSD（战场型）",
    "人格障碍", "进食障碍", "睡眠障碍", "物质滥用",
    "精神分裂", "双相情感障碍", "恐惧症",
    "解离性障碍", "适应障碍", "冲动控制障碍",
]


def _get_active_slot(project_root: Path) -> str | None:
    """获取当前活跃 slot 名。"""
    reg_file = project_root / "workspace" / "registry.json"
    if not reg_file.exists():
        return None
    try:
        reg = json.loads(reg_file.read_text(encoding="utf-8"))
        return reg.get("active_slot", "") or None
    except Exception:
        return None


def _get_active_card_set(project_root: Path) -> str:
    """复用 voice_cards 的卡组配置（同一本小说共享）。"""
    try:
        ws_dir = project_root / "workspace"
        slot = _get_active_slot(project_root)
        if not slot:
            return "default"
        proj_file = ws_dir / slot / "project.json"
        if proj_file.exists():
            proj = json.loads(proj_file.read_text(encoding="utf-8"))
            return proj.get("active_voice_card_set", "default")
    except Exception:
        pass
    return "default"


def _mental_states_dir(project_root: Path, card_set: str | None = None) -> Path | None:
    """获取精神状态文件目录（按 slot + 卡组隔离）。"""
    ws_dir = project_root / "workspace"
    slot = _get_active_slot(project_root)
    if not slot:
        return None
    if card_set is None:
        card_set = _get_active_card_set(project_root)
    ms_dir = ws_dir / slot / "mental_states" / card_set
    ms_dir.mkdir(parents=True, exist_ok=True)
    return ms_dir


def get_mental_state(project_root: Path, name: str,
                     card_set: str | None = None) -> dict:
    """读取角色精神状态数据。

    优先读取 mental_states/<set>/ 下的独立文件，
    不存在时 fallback 到 voice_cards/ 角色卡嵌入数据（向后兼容）。
    两者都没有时返回空 dict。
    """
    ms_dir = _mental_states_dir(project_root, card_set)
    if ms_dir:
        f = ms_dir / f"{name}.json"
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                pass

    # Fallback: 从角色卡嵌入数据读取
    try:
        from .voice_diversity_guard import get_character_card
        card = get_character_card(project_root, name)
        if card:
            ms = card.get("mental_state", {})
            if ms:
                return ms
    except Exception:
        pass

    return {}


def save_mental_state(project_root: Path, name: str, data: dict,
                      card_set: str | None = None) -> bool:
    """保存角色精神状态数据到独立文件（不碰角色卡）。"""
    ms_dir = _mental_states_dir(project_root, card_set)
    if not ms_dir:
        return False
    f = ms_dir / f"{name}.json"
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def list_mental_states(project_root: Path) -> list[dict]:
    """列出当前 slot 所有角色的精神状态数据。

    返回: [{name: str, mental_state: dict}, ...]
    仅返回存在独立文件的角色（不含 fallback 嵌入数据）。
    """
    card_set = _get_active_card_set(project_root)
    ms_dir = _mental_states_dir(project_root, card_set)
    if not ms_dir or not ms_dir.exists():
        return []
    results = []
    for f in sorted(ms_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results.append({"name": f.stem, "mental_state": data})
        except Exception:
            pass
    return results
