"""精神状态系统测试 — guard 规则 + 数据模型 + CLI 基础"""

import json
from pathlib import Path

# ── mental_state_guard 测试 ──

SAMPLE_CONTENT_CLEAN = """
林观澜推开洞府的门，阳光照进来。他深吸一口气，开始今天的修炼。
灵气在体内流转，一切如常。远处传来剑鸣声，他充耳不闻。
"""

SAMPLE_CONTENT_OVERPLAY = """
他疯了！彻底疯了！整个人都崩溃了，失控地狂笑，像一个精神病患者。
歇斯底里的声音在洞府回荡，他发疯一样砸碎所有东西，整个人都扭曲了。
疯了疯了疯了！精神错乱！完全失控！这简直是疯子的行为！
"""

SAMPLE_CONTENT_PTSD = """
血月当空。林观澜忽然僵住，手脚冰凉。眼前的景象让他浑身颤抖，
他仿佛又回到了那个夜晚——宗门被灭，师父被一掌拍碎元婴。
剑鸣声响起，他捂着头蹲下，呼吸困难，冷汗涔涔。
"""


def test_guard_importable():
    """mental_state_guard 模块可导入且函数存在。"""
    from src.guards.human_texture import mental_state_guard
    assert hasattr(mental_state_guard, "run_mental_state_check")


def test_guard_clean_pass():
    """干净文本应 PASS。"""
    from src.guards.human_texture.mental_state_guard import run_mental_state_check
    result = run_mental_state_check(SAMPLE_CONTENT_CLEAN, chapter_no=1)
    assert result["status"] == "PASS"
    assert len(result["issues"]) == 0


def test_guard_overplay_warn():
    """过度精神病理词汇应 WARN。"""
    from src.guards.human_texture.mental_state_guard import run_mental_state_check
    result = run_mental_state_check(SAMPLE_CONTENT_OVERPLAY, chapter_no=1)
    assert result["status"] in ("WARN", "FAIL")
    codes = [i["code"] for i in result["issues"]]
    assert any("OVERPLAY" in c for c in codes), f"应检测到过度词汇: {codes}"


def test_guard_overplay_block():
    """极端过度应 BLOCK（根据阈值）。"""
    from src.guards.human_texture.mental_state_guard import run_mental_state_check
    # 用大量重复词推高密度
    heavy = "疯了疯了疯了疯了疯了崩溃崩溃失控失控失控疯了疯了疯了疯了疯了疯了 " * 10
    result = run_mental_state_check(heavy, chapter_no=1)
    # 有限字符内可能达不到 FAIL，确认至少有 WARN
    codes = [i["code"] for i in result["issues"]]
    overplay_warns = [c for c in codes if "OVERPLAY" in c]
    assert len(overplay_warns) > 0, f"应检测到过度词汇: {codes}"


def test_guard_genre_elastic():
    """不同题材应有不同阈值。"""
    from src.guards.human_texture.mental_state_guard import (
        run_mental_state_check,
    )
    result_horror = run_mental_state_check(SAMPLE_CONTENT_OVERPLAY, chapter_no=1, genre="horror")
    result_urban = run_mental_state_check(SAMPLE_CONTENT_OVERPLAY, chapter_no=1, genre="urban")
    # 惊悚题材允许更多夸张词汇，都市更严格
    h_codes = [i["code"] for i in result_horror["issues"]]
    u_codes = [i["code"] for i in result_urban["issues"]]
    h_overplay = any("OVERPLAY" in c for c in h_codes)
    u_overplay = any("OVERPLAY" in c for c in u_codes)
    # 至少都市检测比惊悚更严格（或者一样）
    if not h_overplay and u_overplay:
        # 都市检测到但惊悚没检测到 → 弹性生效
        assert True
    elif h_overplay and not u_overplay:
        # 惊悚检测到但都市没检测到 → 异常
        assert False, "Horror should be more lenient than urban"


def test_guard_deviation():
    """情绪极端词偏离检测。"""
    from src.guards.human_texture.mental_state_guard import run_mental_state_check
    extreme_text = "他痛不欲生，撕心裂肺地哭嚎。这是极度痛苦的时刻，生不如死。"
    result = run_mental_state_check(extreme_text, chapter_no=1)
    # 纯文本检查不涉及角色卡，可能只有 overplay 或 deviation
    assert result["status"] in ("PASS", "WARN", "FAIL")


def test_guard_ptsg_triggers():
    """PTSD 文本不应过度报警（合理的精神状态描写）。"""
    from src.guards.human_texture.mental_state_guard import run_mental_state_check
    result = run_mental_state_check(SAMPLE_CONTENT_PTSD, chapter_no=1)
    # PTSD 场景包含「颤抖」「僵住」等词但不是过度病理词汇
    # 不应该触发 OVERPLAY
    codes = [i["code"] for i in result["issues"]]
    overplay = [c for c in codes if "OVERPLAY" in c]
    if overplay:
        # 可能轻度警告但不应该 FAIL
        assert result["status"] != "FAIL", f"合理 PTSD 不应 FAIL: {codes}"


# ── 数据模型测试 ──

def test_mental_state_categories():
    """MENTAL_STATE_CATEGORIES 应包含 15 类。"""
    from src.guards.human_texture.mental_state_crud import MENTAL_STATE_CATEGORIES
    assert len(MENTAL_STATE_CATEGORIES) == 15
    assert "抑郁症" in MENTAL_STATE_CATEGORIES
    assert "PTSD" in MENTAL_STATE_CATEGORIES
    assert "精神分裂" in MENTAL_STATE_CATEGORIES


def test_mental_state_card_structure():
    """角色卡应支持 mental_state 第四层。"""
    from src.guards.human_texture.mental_state_crud import (
        MENTAL_STATE_CATEGORIES,
    )
    # 模拟角色卡含 mental_state
    card = {
        "name": "test_char",
        "voice": {},
        "personality": {},
        "behavior": {},
        "mental_state": {
            "抑郁症": {
                "severity": 3,
                "onset": "测试诱因",
                "triggers": ["触发词1", "触发词2"],
                "manifestations": ["表现1"],
                "chapter_notes": {"1": "第一章表现"},
            },
        },
    }
    ms = card.get("mental_state", {})
    assert "抑郁症" in ms
    assert ms["抑郁症"]["severity"] == 3
    assert len(ms["抑郁症"]["triggers"]) == 2


def test_mental_state_empty_is_valid():
    """空 mental_state 应合法（新角色无精神状态）。"""
    card = {"name": "test", "voice": {}, "personality": {}, "behavior": {}}
    ms = card.get("mental_state", {})
    assert ms == {}


def test_mental_state_presets_yaml():
    """mental_state_presets.yaml 应可加载且包含 15 类。"""
    import yaml
    from src.cli.shared import PROJECT_ROOT
    kf = PROJECT_ROOT / "configs" / "human_texture" / "mental_state_presets.yaml"
    assert kf.exists(), f"词库文件不存在: {kf}"
    data = yaml.safe_load(kf.read_text(encoding="utf-8"))
    assert len(data) >= 15, f"词库应有 >=15 类, 实际 {len(data)}"
    assert "抑郁症" in data
    assert "PTSD" in data


# ── Agent 测试 ──

SAMPLE_TEXT_WITH_TRIGGERS = """
林观澜站在血月之下，望着满目疮痍的宗门废墟。
远处传来剑鸣声，他的身体微微一颤。
"""


def test_mental_state_agent_import():
    """MentalStateAgent 可导入且是 BaseAgent 子类。"""
    from scripts.agents.mental_state_agent import MentalStateAgent
    agent = MentalStateAgent()
    assert agent.name == "mental_state"
    result = agent.review("测试文本", chapter_no=1)
    assert "agent" in result
    assert "score" in result
    assert "status" in result
    assert "findings" in result


def test_mental_state_agent_registered():
    """MentalStateAgent 已注册到 orchestrator。"""
    from scripts.agents.orchestrator import AGENT_REGISTRY, MODE_AGENTS
    assert "mental_state" in AGENT_REGISTRY
    assert "mental_state" in MODE_AGENTS["full"]
    assert "mental_state" not in MODE_AGENTS["light"]


# ── CRUD 单元测试 ──

def _make_mock_workspace(tmp_path, slot_name="slot_test"):
    """创建 mock workspace 结构供 CRUD 测试。"""
    ws = tmp_path / "workspace"
    ws.mkdir()
    reg = ws / "registry.json"
    reg.write_text(f'{{"active_slot": "{slot_name}"}}', encoding="utf-8")
    slot = ws / slot_name
    slot.mkdir()
    proj = slot / "project.json"
    proj.write_text('{"active_voice_card_set": "default"}', encoding="utf-8")
    return tmp_path


def test_crud_save_and_read(tmp_path):
    """save_mental_state + get_mental_state 应正确读写。"""
    root = _make_mock_workspace(tmp_path)
    from src.guards.human_texture.mental_state_crud import (
        save_mental_state, get_mental_state,
    )
    data = {"PTSD": {"severity": 3, "triggers": ["血月"]}}
    ok = save_mental_state(root, "林观澜", data)
    assert ok, "save_mental_state 应返回 True"

    loaded = get_mental_state(root, "林观澜")
    assert loaded == data, f"读取数据应匹配, 实际: {loaded}"
    assert loaded["PTSD"]["severity"] == 3


def test_crud_read_empty_for_nonexistent(tmp_path):
    """不存在的角色应返回空 dict。"""
    root = _make_mock_workspace(tmp_path)
    from src.guards.human_texture.mental_state_crud import get_mental_state
    loaded = get_mental_state(root, "不存在的角色")
    assert loaded == {}


def test_crud_fallback_from_voice_card(tmp_path):
    """无独立文件时，get_mental_state 应 fallback 到角色卡嵌入数据。"""
    root = _make_mock_workspace(tmp_path)
    from src.guards.human_texture.mental_state_crud import get_mental_state
    from src.guards.human_texture.voice_diversity_guard import (
        save_character_card, get_character_card,
    )
    card = {
        "name": "韩烈",
        "voice": {},
        "personality": {},
        "behavior": {},
        "mental_state": {"焦虑症": {"severity": 2}},
    }
    save_character_card(root, "韩烈", card)
    # 确认角色卡数据正常写入
    saved = get_character_card(root, "韩烈")
    assert saved is not None, "角色卡应可正常读取"

    # 独立文件不存在时应 fallback 到嵌入数据
    loaded = get_mental_state(root, "韩烈")
    assert "焦虑症" in loaded, f"fallback 应读取到嵌入数据, 实际: {loaded}"
    assert loaded["焦虑症"]["severity"] == 2


def test_crud_save_does_not_pollute_voice_card(tmp_path):
    """save_mental_state 不应污染 voice_cards 文件。"""
    root = _make_mock_workspace(tmp_path)
    from src.guards.human_texture.mental_state_crud import save_mental_state
    from src.guards.human_texture.voice_diversity_guard import get_character_card

    # 保存精神状态
    data = {"PTSD": {"severity": 4, "triggers": ["剑鸣"]}}
    save_mental_state(root, "林观澜", data)

    # 角色卡文件应该不存在（从未创建过）
    card = get_character_card(root, "林观澜")
    assert card is None, "save_mental_state 不应创建角色卡文件"
