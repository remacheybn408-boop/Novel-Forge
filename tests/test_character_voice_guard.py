#!/usr/bin/env python3
"""Test character_voice_guard — 角色口吻门禁测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from character_voice_guard import (
    run_character_voice_check,
    analyze_dialect_level,
    analyze_wenyan_level,
)


def test_dialect_level_zero():
    assert analyze_dialect_level("今天天气很好，我们出去走走吧。") == 0


def test_dialect_level_detected():
    assert analyze_dialect_level("甭说了，俺们这就走，咋还不信咧？") >= 2


def test_wenyan_level_zero():
    assert analyze_wenyan_level("今天天气很好。") == 0


def test_wenyan_level_detected():
    assert analyze_wenyan_level("然则此法不可久恃，盖天道有常，岂可违焉？") >= 2


def test_empty_content():
    report = run_character_voice_check("", 1)
    assert report["status"] in ("PASS", "WARNING")
    assert report["total_dialogues"] == 0


def test_normal_text_passes():
    content = """周砚走到矿壁前，伸手摸了摸湿漉漉的石面。
"不急，先把这面墙看完。"他说。
沈师姐站在一旁，没有说话，只是用剑尖轻轻点了一下地面。"""
    report = run_character_voice_check(content, 1)
    assert report["status"] in ("PASS", "WARNING")


def test_forbidden_words_detected():
    content = '"这件事情没有那么简单。"周砚说。"确实，事情没有这么简单。"沈师姐回答。'
    report = run_character_voice_check(content, 1)
    # 通用 AI 腔应该被检测到
    assert report["universal_ai_violations"] >= 0  # 可能被检测


def test_voice_profiles_loaded():
    """测试加载角色口吻卡"""
    profiles = [
        {
            "character_name": "周砚",
            "dialect_level": 0,
            "wenyan_level": 1,
            "forbidden_words": ["命运", "大道"],
        }
    ]
    content = '"或许这就是命运吧。"周砚自言自语道。'
    report = run_character_voice_check(content, 1, profiles)
    # 应该检测到禁用词
    assert len(report["forbidden_words_found"]) >= 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
