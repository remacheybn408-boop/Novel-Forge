"""
test_agent_run_guard.py — Quality Guard 测试
"""
import pytest, json, tempfile, sys, os, subprocess
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

GUARD_SCRIPT = Path(__file__).parent.parent / "scripts" / "agent_run_guard.py"


def _run_guard(report_dict):
    """Write temp report, run guard, return (exit_code, stdout)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(report_dict, f)
        tmp = f.name
    result = subprocess.run([sys.executable, str(GUARD_SCRIPT), tmp], capture_output=True, text=True)
    Path(tmp).unlink()
    return result.returncode, result.stdout


def _valid_report(**overrides):
    base = {
        "mode": "NOVEL_WRITE_MODE", "required_skill": "novel-factory", "skill_called": True,
        "write_mode": "chunked", "chunk_count": 5, "chunk_word_counts": [620,710,680,760,830],
        "chunk_gate_passed": True, "chapter_no": 1, "title": "test",
        "assembled_word_count": 3600, "word_count": 3600,
        "chapter_word_count_gate": True, "word_count_gate": True, "allow_short_chapter": False,
        "pre_done": True, "task_card_done": True, "continuity_gate": True,
        "hallucination_gate_passed": True, "unsupported_claims_count": 0,
        "contradictions_count": 0, "blocked_items_count": 0,
        "scene_quality_gate": True, "anti_ai_style_gate": True, "padding_detected": False,
        "ingest_done": True, "next_allowed": True
    }
    base.update(overrides)
    return base


class TestGuardPass:
    def test_valid_report_passes(self):
        rc, out = _run_guard(_valid_report())
        assert rc == 0
        assert "PASS" in out

    def test_chunked_default_passes(self):
        rc, out = _run_guard(_valid_report())
        assert rc == 0


class TestGuardFail:
    def test_hallucination_fail_blocks(self):
        rc, out = _run_guard(_valid_report(hallucination_gate_passed=False))
        assert rc != 0

    def test_padding_detected_blocks(self):
        rc, out = _run_guard(_valid_report(padding_detected=True))
        assert rc != 0

    def test_low_word_count_blocks(self):
        rc, out = _run_guard(_valid_report(assembled_word_count=2000, chapter_word_count_gate=False, word_count_gate=False))
        assert rc != 0

    def test_contradictions_block(self):
        rc, out = _run_guard(_valid_report(contradictions_count=1))
        assert rc != 0

    def test_blocked_items_block(self):
        rc, out = _run_guard(_valid_report(blocked_items_count=2))
        assert rc != 0

    def test_unsupported_claims_block(self):
        rc, out = _run_guard(_valid_report(unsupported_claims_count=1))
        assert rc != 0

    def test_ingest_not_done_blocks(self):
        rc, out = _run_guard(_valid_report(ingest_done=False, next_allowed=False))
        assert rc != 0

    def test_chunked_low_chunks_low_wc_blocks(self):
        rc, out = _run_guard(_valid_report(chunk_count=2, assembled_word_count=1500, chapter_word_count_gate=False, word_count_gate=False))
        assert rc != 0
