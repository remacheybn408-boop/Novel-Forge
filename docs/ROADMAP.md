# Roadmap

Novel Pipeline - Write Engine 开发路线图。

## Phase 1: 项目基本结构 ⚠️ (大部分完成，核心脚本待验证)

**已完成：**
- [x] README 对齐真实仓库结构，标注"早期原型"
- [x] config.example.json — 配置模板（3300 红线，4 场景）
- [x] database/schema.sql — 完整 SQLite 表结构（含 volume_plans/chapter_plans/title_history）
- [x] scripts/init_db.py — 数据库初始化
- [x] scripts/check_schema.py — Schema 完整性检查
- [x] docs/skills/long_novel_writing_SKILL.md — 长篇写作行为规范（通用版，无具体小说绑定）
- [x] docs/ROADMAP.md — 本文件

**已完成（待用户验证）：**
- [~] chapter_pipeline.py — 已重构为 argparse + config 驱动，移除硬编码路径/小说名/角色名
- [~] 字数门禁：<3300 失败，3300-3500 pass_but_low，3500-3900 最佳
- [~] 场景门禁：>=4 有效场景

**待完成：**
- [ ] 用户在实际环境中验证 chapter_pipeline.py 可正常运行
- [ ] 确认 clone 后 `python scripts/init_db.py --config config.json` 成功
- [ ] 确认 `pytest tests/ -v` 全部通过

**验证命令：**
```bash
git clone https://github.com/remacheybn408-boop/novel-pipeline-write-engine.git
cd novel-pipeline-write-engine
cp config.example.json config.json
python scripts/init_db.py --config config.json
python scripts/check_schema.py --config config.json
pytest tests/ -v
```

## Phase 2: 标题骨架与卷级连续性

规划中：

- [ ] import_outline_skeleton.py — 从 JSON 导入标题骨架
- [ ] volume_plans / chapter_plans 的写入与校验
- [ ] 卷级 post（volume_post）：生成卷级总结、状态、下一卷承接点
- [ ] chapter_brief 输出增强
- [ ] 标题骨架入库（pre 阶段从 volume_plans/chapter_plans 读取）
- [ ] 卷序强制检查（跨卷连续性验证）

**预计：** Phase 2 完成后，可以从 JSON 骨架初始化整本书结构，逐章推进时自动读取/更新计划。

## Phase 3: 工具增强

- [ ] scripts/create_novel.py — 创建新小说项目
- [ ] scripts/export_novel.py — 导出完整小说
- [ ] scripts/backup_db.py — 数据库备份
- [ ] 更多测试覆盖（pipeline 端到端测试）

**未来可考虑（backlog）：**
- Web UI
- FastAPI 后端
- 向量数据库（用于写作参考检索）
- Agent 编排增强

---

> 当前阶段：Phase 1 大部分完成，等待实际环境验证。
> 下一步：验证通过后进入 Phase 2。
