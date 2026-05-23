#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Agent Run Guard — v0.3.1 Quality Guard Release

检查 chapter_run_report.json 的全部质量门禁。
所有硬门禁必须 true，否则 FAILED_NOVEL_WRITE_GUARD。

用法：
python scripts/agent_run_guard.py path/to/chapter_run_report.json
"""

import json
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"FAILED_NOVEL_WRITE_GUARD: {message}")
    sys.exit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: python scripts/agent_run_guard.py path/to/chapter_run_report.json")

    report_path = Path(sys.argv[1])
    if not report_path.exists():
        fail(f"report not found: {report_path}")

    try:
        d = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid json: {exc}")

    # ── 模式与 skill ──
    if d.get("mode") != "NOVEL_WRITE_MODE":
        fail("mode must be NOVEL_WRITE_MODE")
    if d.get("required_skill") != "novel-factory":
        fail("required_skill must be novel-factory")
    if d.get("skill_called") is not True:
        fail("skill_called must be true")

    # ── 前置 ──
    if d.get("pre_done") is not True:
        fail("pre_done must be true")
    if d.get("task_card_done") is not True:
        fail("task_card_done must be true")

    # ── 字数 ──
    chapter_wc_ok = d.get("chapter_word_count_gate", d.get("word_count_gate", False))
    if chapter_wc_ok is not True:
        fail("chapter_word_count_gate must be true")
    assembled_wc = int(d.get("assembled_word_count", d.get("word_count", 0)))
    allow_short = bool(d.get("allow_short_chapter", False))
    if assembled_wc < 3300 and not allow_short:
        fail(f"assembled_word_count {assembled_wc} below 3300 and allow_short_chapter is false")

    # ── Chunked writing ──
    write_mode = d.get("write_mode", "")
    if write_mode == "chunked":
        chunk_count = int(d.get("chunk_count", 0))
        if chunk_count < 4 and assembled_wc < 3300 and not allow_short:
            fail(f"chunk_count {chunk_count} < 4 with word_count {assembled_wc} < 3300")
        if d.get("chunk_gate_passed") is not True:
            fail("chunk_gate_passed must be true")
        chunk_wcs = d.get("chunk_word_counts", [])
        if not chunk_wcs and chunk_count > 0:
            fail("chunk_word_counts must not be empty when chunk_count > 0")

    # ── 门禁 ──
    if d.get("continuity_gate") is not True:
        fail("continuity_gate must be true")

    if d.get("hallucination_gate_passed") is not True:
        fail("hallucination_gate_passed must be true")
    allow_unsupported = bool(d.get("allow_unsupported_claims", False))
    if int(d.get("unsupported_claims_count", 0)) > 0 and not allow_unsupported:
        fail("unsupported_claims_count > 0")
    if int(d.get("contradictions_count", 0)) > 0:
        fail("contradictions_count > 0")
    if int(d.get("blocked_items_count", 0)) > 0:
        fail("blocked_items_count > 0")

    if d.get("scene_quality_gate") is not True:
        fail("scene_quality_gate must be true")
    if d.get("anti_ai_style_gate") is not True:
        fail("anti_ai_style_gate must be true")

    # ── 反水文 ──
    if d.get("padding_detected") is True:
        fail("padding_detected must be false")

    # ── 入库 ──
    if d.get("ingest_done") is not True:
        fail("ingest_done must be true")
    if d.get("next_allowed") is not True:
        fail("next_allowed must be true")

    print("PASS_NOVEL_WRITE_GUARD")


if __name__ == "__main__":
    main()
