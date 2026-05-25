# Multi-Agent Review Board (Enabled in v0.5.5)

v0.5.5 已启用多 Agent 审稿团。8 个专业 Agent + 1 个 Chief Editor 并行审稿：

- **anti_ai_agent.py** — AI腔检测
- **chief_editor.py** — 总编汇总
- **context_agent.py** — 上下文一致性
- **continuity_agent.py** — 前后连续性
- **plot_agent.py** — 剧情推进
- **reader_pull_agent.py** — 追读力
- **setting_agent.py** — 世界观设定
- **voice_agent.py** — 角色口吻
- **orchestrator.py** — 调度编排

## 使用方式

```bash
# 轻量审稿（快速扫描）
python novel.py agents review <章节号>

# 完整审稿（8 Agent 并行）
python novel.py agents review <章节号> --mode full
```

## 设计原则

- **只审稿，不覆盖正文**：所有审稿结果输出报告，作者决定是否采纳
- **默认关闭**：不影响主流水线，手动触发
- **多维度并行**：8 个视角同时审稿，避免单视角盲区
