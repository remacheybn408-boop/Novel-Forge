# Roadmap

Novel Pipeline - Write Engine 开发路线图。

## Phase 1: 项目可运行 ✅ (已完成)

- [x] README 对齐真实仓库结构，标注"早期原型"
- [x] config.example.json — 配置模板（V5 字数规则：按 chapter_type 分级）
- [x] database/schema.sql — 完整 SQLite 表结构（26 表 + 6 FTS5）
- [x] scripts/init_db.py — 一键建库
- [x] scripts/check_schema.py — Schema 完整性检查
- [x] scripts/import_outline_skeleton.py — JSON 标题骨架 → SQLite
- [x] scripts/chapter_pipeline.py — argparse + config 驱动，无硬编码
- [x] 字数门禁：按类型分级（普通1900-3300, 重点1900-4200, 高潮1900-5500）
- [x] 场景门禁：>=4 有效场景
- [x] examples/demo_novel/ — 25 章 demo 项目
- [x] docs/skills/long_novel_writing_SKILL.md — 通用写作行为规范
- [x] 14 个基础测试 + GitHub Actions CI

**验证命令：**
```bash
git clone https://github.com/remacheybn408-boop/novel-pipeline-write-engine.git
cd novel-pipeline-write-engine
cp config.example.json config.json
python scripts/init_db.py --config config.json
python scripts/check_schema.py --config config.json
python scripts/import_outline_skeleton.py --config config.json --input examples/demo_novel/outline_skeleton.json
pytest tests/ -v
```

---

## Phase 2: 标题骨架与卷级连续性 ✅ (已完成)

**全部完成：**
- [x] import_outline_skeleton.py — JSON 标题骨架导入
- [x] volume_plans / chapter_plans 基础写入与校验
- [x] pre 阶段读取标题骨架 + TASK CARD 展示
- [x] volume_post + volume_report.json
- [x] chapter_brief JSON 输出 + pre 读取上章 brief
- [x] ingest 自动更新 chapter_plans 状态 + title_history
- [x] 卷序强制检查 + 端到端测试（21 个测试）
- [x] Demo 项目 + CI

---

## Phase 2.5: Agent 路由控制 ✅ (已完成)

- [x] novel_factory_router_SKILL.md — PLAN_MODE / NOVEL_WRITE_MODE 路由器
- [x] long_novel_writing_SKILL 顶部 Section 0：优先读取 Router
- [x] README 强制规则段：NOVEL_WRITE_MODE 执行头 + 禁止聊天模式
- [x] agent_run_guard.py — chapter_run_report.json 自检脚本
- [x] ingest 自动生成 chapter_run_report.json
- [x] Skills 列表挂载 novel_factory_router 链接

---

## Phase 2.6: v0.3.1 — Quality Guard Release ✅

- [x] Hallucination Guard hard gate（FAIL 禁止 ingest）
- [x] Chunked Writing Mode（chunk 300~900 字，assembled_chapter ≥3300）
- [x] Anti-padding Guard（水文检测：同义重复/设定堆砌/尾部补独白）
- [x] assembled_chapter word count gate
- [x] chapter_run_report 质量字段（write_mode/chunk_count/hallucination/padding）
- [x] agent_run_guard 全量质量检查（17 项硬门禁）

---

## Phase 3: v0.4.x — Human-Grade Revision Suite ✅ (已完成)

- [x] 7 个拟人审稿门禁（concrete_anchor / scene_causality / dialogue_naturalness / style_variation / editor_revision / compliance_selfcheck / final_submission_report）
- [x] Guard Registry 统一调度（scripts/guard_registry.py）
- [x] Revision Loop 自动改稿闭环
- [x] Continuity Evidence Guard 连续桥证据
- [x] Bridge Evidence Guard 桥证据门禁
- [x] Character Voice Guard 角色口吻门禁
- [x] GuardResult 统一数据结构

## Phase 4: v0.5.0 — Stable & Easy Mode ✅ (已完成)

- [x] novel.py 统一入口（13个子命令）
- [x] status 健康检查
- [x] Reader Pull Guard 追读力门禁（5 维度）
- [x] Voice Pack Guard + Meme Pack Guard
- [x] 写前任务卡 Task Card
- [x] HTML 只读报告
- [x] 5 种题材模板
- [x] Windows 一键脚本（install.bat / run_demo.bat / run_report.bat）

## Phase 5: v0.5.5 — Hotfix Quality ✅ (当前版本)

- [x] 版本号统一（version.py → 全项目读 VERSION）
- [x] Release 包卫生（config.json 脱敏 / .pytest_cache 排除）
- [x] CI 修复（pip install -r requirements.txt + timeout）
- [x] test subprocess 加 timeout
- [x] meme_pack_guard type 过滤
- [x] 3 个新 guard 接入 guard_registry（21 guards）
- [x] README 测试数更新（43文件/278用例）

## Phase 6: 工具增强

- [ ] scripts/create_novel.py — 创建新小说项目
- [x] scripts/export_novel.py — 导出完整小说
- [x] scripts/backup_db.py — 极简版（v0.3.1；v0.4.0 完整工具增强）
- [ ] 端到端流水线测试

**未来可考虑（backlog）：**
- Web UI
- FastAPI 后端
- 向量数据库（写作参考检索）
- Agent 编排增强

---

> 当前：Phase 5 (v0.5.5) 已完成，下一步 Phase 6 工具增强。
