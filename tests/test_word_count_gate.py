"""
test_word_count_gate.py — 字数门禁单元测试
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from chapter_pipeline import _count_chinese, App, DEFAULT_CONFIG


@pytest.fixture
def app():
    cfg = DEFAULT_CONFIG.copy()
    cfg["db_path"] = ":memory:"
    return App(cfg, "test_novel", "测试小说", 1)


class TestChineseCount:
    def test_pure_chinese(self):
        """_count_chinese counts CJK chars including fullwidth punctuation in ranges"""
        assert _count_chinese("这是一段测试文本") == 8

    def test_mixed(self):
        assert _count_chinese("ABC这是一段test文本123") == 6

    def test_punctuation(self):
        assert _count_chinese("你好，世界！") == 6


class TestWordCountGate:
    def test_below_redline_fail(self, app):
        """3299 < 3300 -> fail"""
        import chapter_pipeline as cp
        cp.app = app
        content = "测试" * 1649 + "x"  # ~3299
        result, wc = cp.word_count_gate(content, 1, "normal")
        assert result == False
        assert wc < 3300

    def test_at_redline_pass(self, app):
        """3300 -> yellow (below ideal_min of 3500)"""
        import chapter_pipeline as cp
        cp.app = app
        content = "测试" * 1650  # 3300
        result, wc = cp.word_count_gate(content, 1, "normal")
        assert result == "yellow"

    def test_ideal_range(self, app):
        """3700 -> ideal"""
        import chapter_pipeline as cp
        cp.app = app
        content = "测试" * 1850  # 3700
        result, wc = cp.word_count_gate(content, 1, "normal")
        assert result == "ideal"

    def test_normal_pass(self, app):
        """4000 -> True"""
        import chapter_pipeline as cp
        cp.app = app
        content = "测试" * 2000  # 4000
        result, wc = cp.word_count_gate(content, 1, "normal")
        assert result == True

    def test_oversize_warn(self, app):
        """4500 normal type -> oversize"""
        import chapter_pipeline as cp
        cp.app = app
        content = "测试" * 2250  # 4500
        result, wc = cp.word_count_gate(content, 1, "normal")
        assert result == "oversize"
