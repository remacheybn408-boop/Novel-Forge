# Pipeline — v0.3.1 完整流程

`chapter_pipeline.py` 设计文档。v0.3.1 质量门禁修正版。

## 流程

```
pre
→ task_card
→ scene_plan
→ write_chunks       (Chunked Writing Mode)
→ assemble_chapter
→ chapter_word_count_gate  (只检查 assembled_chapter)
→ continuity_gate
→ hallucination_gate (硬门禁 — FAIL 禁止 ingest)
→ scene_quality_gate
→ anti_ai_style_gate
→ padding_guard      (反水文)
→ ingest             (全部门禁通过才能入库)
→ chapter_run_report
→ agent_run_guard
→ auto_pre_next_chapter
```

## Chunked Writing Mode

- chunk 是写作单位，chapter 是入库单位
- 3300 字红线只卡 assembled_chapter，不卡单个 chunk
- 单个 chunk 建议 300~900 字
- 每章建议 4~7 个 chunks
- chunk 失败只重写该 chunk，不重写整章
- assembled_chapter 字数不足时补缺失场景，禁止补水文

chunk 合格条件：
1. 有明确地点 2. 有明确人物 3. 有具体动作 4. 有冲突/信息推进
5. 推进主线/人物/伏笔/承诺/世界观/情绪之一
6. 不能只解释设定 7. 不能只心理独白 8. 不能复述前文

## Hallucination Hard Gate

- hallucination_gate 是硬门禁
- FAIL → 禁止 ingest + 禁止 pre 下一章
- agent_run_guard 必须 FAIL
- run_report: next_allowed=false, next_action=fix_hallucination

## Anti-padding Guard

- padding_detected=true → 禁止 ingest
- 检测：连续三段同义 / 空泛心理 / 设定堆砌无行动 / 尾部补独白
- 字数不足时补场景，不补废话

## 字数门禁 (V4)

3300 红线只适用于 assembled_chapter。单个 write_chunk 不要求 3300。

## 调用示例

```bash
python scripts/chapter_pipeline.py pre 1 --config config.json --novel-slug demo_novel
python scripts/chapter_pipeline.py post 1 --config config.json --novel-slug demo_novel
python scripts/chapter_pipeline.py volume --config config.json --novel-slug demo_novel --volume-no 1
python scripts/agent_run_guard.py exports/run_reports/chapter_001_run_report.json
```

## 输出文件

| 阶段 | 输出 |
|------|------|
| pre | context_pack.txt, pipeline_state.json |
| post | chapter_brief.json, chapter_run_report.json, hallucination_report.json |
| volume | volume_report.json |
