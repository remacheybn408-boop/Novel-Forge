# Novel Pipeline - Write Engine

AI 长篇小说工程化写作流水线：SQLite 长期记忆 + 8 步门禁 Pipeline。

> **当前阶段：早期原型。** 基础流水线和数据库已可运行，高级功能逐步落地中。

---

## 快速开始

```bash
git clone https://github.com/remacheybn408-boop/novel-pipeline-write-engine.git
cd novel-pipeline-write-engine
cp config.example.json config.json

# 初始化
python scripts/init_db.py --config config.json
python scripts/check_schema.py --config config.json

# 测试
pip install pytest && pytest tests/ -v
```

---

## 当前已完成

| 模块 | 说明 |
|------|------|
| `chapter_pipeline.py` | 8 步流水线（pre → ingest），argparse + config 驱动 |
| 字数门禁 | < 3300 失败，3500–3900 最佳 |
| 场景门禁 | ≥ 4 有效场景 |
| `schema.sql` | 26 表 + 6 FTS5 索引，含 `volume_plans`/`chapter_plans`/`title_history` |
| `init_db.py` | 一键建库 |
| `check_schema.py` | Schema 完整性检查 |
| `import_outline_skeleton.py` | 从 JSON 导入标题骨架（校验 + 写入） |
| Skill 文档 | `docs/skills/long_novel_writing_SKILL.md`（通用版，无具体小说绑定） |
| CI | GitHub Actions 自动跑 `pytest tests/ -v` |

---

## 进行中（Phase 2 重点）

- [ ] pre 阶段从 `volume_plans`/`chapter_plans` 读取标题骨架
- [ ] `volume_post` — 卷级总结与承接
- [ ] `chapter_brief` 输出增强

---

## 后续（Phase 3）

- [ ] `export_novel.py` / `backup_db.py`
- [ ] 端到端流水线测试
- Backlog：Web UI / FastAPI / 向量数据库

详见 [ROADMAP](docs/ROADMAP.md)

---

## 核心设计

```
SQLite 记住 → 门禁防偷懒 → 摘要防迷路 → 版本可回滚
```

| 步骤 | 功能 | 门禁 |
|------|------|------|
| pre | 读上章结尾 + 查 SQLite + context_pack | pipeline_state 锁 |
| task_card | 生成任务卡 | 缺失停止 |
| write | 场景展开（≥4 场景） | - |
| word_count | 字数门禁 | < 3300 红灯 |
| continuity | 上章结尾比对 | 关键词 + 人物承接 |
| scene | 场景质量 | ≥ 4 有效场景 |
| anti_ai | 反 AI 腔（10 项检测） | ≤ 2 轻微 |
| ingest | 入库 + 切片 + FTS + 版本 + 摘要 + 日志 | 失败禁止下一章 |

---

## Skills

- [长篇写作行为规范](docs/skills/long_novel_writing_SKILL.md) — 3300 红线 / 4 场景 / 章章入库 / 卷卷入库 / 标题骨架规则

## 文档

- [架构](docs/architecture.md)
- [行为规范](docs/behavior-spec.md)
- [数据库 Schema](docs/database.md)
- [流水线](docs/pipeline.md)
- [部署指南](docs/setup-guide.md)
- [路线图](docs/ROADMAP.md)

## License

MIT
