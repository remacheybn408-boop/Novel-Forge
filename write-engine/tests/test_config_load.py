"""
test_config_load.py — 配置加载测试
"""
import pytest
import json, tempfile, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from chapter_pipeline import load_config, DEFAULT_CONFIG


class TestConfigLoad:
    def test_default_config(self):
        """No config file -> defaults"""
        cfg = load_config("/nonexistent/path.json")
        assert cfg["db_path"] == DEFAULT_CONFIG["db_path"]
        assert cfg["word_count"]["normal"]["min"] == 1900
        assert cfg["scene_quality"]["min_effective_scenes"] == 4

    def test_load_config_file(self):
        """Custom config overrides defaults"""
        custom = {
            "db_path": "/custom/path.db",
            "word_count": {"normal": {"min": 1900, "best_min": 1900, "best_max": 2800, "max": 3300}},
        }
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(custom, f)
            tmp = f.name

        try:
            cfg = load_config(tmp)
            assert cfg["db_path"] == "/custom/path.db"
            assert cfg["word_count"]["normal"]["min"] == 1900
        finally:
            os.unlink(tmp)
