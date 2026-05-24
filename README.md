# Novel Pipeline - Write Engine v0.4.5

[![Test](https://github.com/remacheybn408-boop/novel-pipeline-write-engine/actions/workflows/test.yml/badge.svg)](https://github.com/remacheybn408-boop/novel-pipeline-write-engine/actions/workflows/test.yml)

AI 长篇小说工程化写作流水线：SQLite 长期记忆 + Guard Registry + 连续性证据 + 防幻觉 + 自动审稿闭环。

> **当前稳定版：v0.4.5 — Guard Truth Source Fix。** 重点修复 post / orchestrator / CI 的 Guard 结果不一致问题，并增加 FTS5 自愈、叙事化证据识别、门禁统一摘要输出。32 个测试文件，238 个测试用例通过。

---

## 它解决什么问题？

写长篇小说时，AI 很容易出现：

- 每章像真空中写出来，缺少上一章承接
- 人物状态、伤势、任务、伏笔被遗忘
- 新设定突然冒出来，造成幻觉
- 章节越写越像模板，AI 腔、总结腔、说明书腔变重
- 科学设定、修炼体系、剧情因果无法长期保持一致
- 门禁结果不统一：post 报 WARNING，orchestrator 却显示 0 WARNING
- SQLite / FTS5 索引损坏后，后续上下文召回 silently fail

这个项目的目标不是"自动水文"，而是把长篇小说写作拆成可检查、可追踪、可回滚、可审稿的工程流程。

---

## v0.4.5 重点

v0.4.5 是一次门禁可信度修复版：

| 模块 | 修复方向 |
|------|----------|
| Guard Registry | post / orchestrator / CI 使用同一套 guard 真相源 |
| WARNING 汇总 | 所有 WARNING 结构化写入 guard_summary.json |
| FTS5 Healthcheck | 检测 invalid fts5 file format，并尝试 rebuild / fallback |
| scene_delta | 从关键词推进改为叙事证据推进 |
| scene_causality | 支持身体代价、环境代价、关系代价、物件后果 |
| continuity | 从词重叠改为承接证据 |
| anti_ai | 统一正则与句式检测入口 |
| path_resolver | 降低 novels_root / slug / 卷目录强耦合 |
| title policy | 标题变化只记录，不擅自改写用户标题 |

---

## 快速开始

### Windows 一键体验

```bat
install.bat
run_demo.bat
```

### 手动运行

```bash
git clone https://github.com/remacheybn408-boop/novel-pipeline-write-engine.git
cd novel-pipeline-write-engine
cp config.example.json config.json

# 初始化数据库
python scripts/init_db.py --config config.json

# 导入 Demo 标题骨架
python scripts/import_outline_skeleton.py --config config.json --input examples/demo_novel/outline_skeleton.json

# 写作前准备
python scripts/chapter_pipeline.py pre 1 --config config.json --novel-slug demo_novel

# 写完 TXT 后入库
python scripts/chapter_pipeline.py post 1 --config config.json --novel-slug demo_novel

# 跑测试
pytest tests/ -v
```

---

## 目录结构

```
novel-pipeline-write-engine/
├── config.example.json              ← 配置模板
├── config.json                      ← 你的本地配置（gitignore）
├── install.bat / run_demo.bat       ← Windows 一键安装/运行
│
├── scripts/
│   ├── chapter_pipeline.py          ← 主流水线（pre / post / review / volume）
│   ├── guard_registry.py            ← [v0.4.5] 统一门禁注册入口
│   ├── guard_result.py              ← [v0.4.5] GuardResult / GuardSummary 数据结构
│   ├── anti_ai_patterns.py          ← [v0.4.5] AI腔统一规则库
│   ├── consequence_lexicon.py       ← [v0.4.5] 可见后果词库
│   ├── fts_health.py                ← [v0.4.5] FTS5 自愈
│   ├── bridge_evidence_guard.py     ← [v0.4.5] 章间承接证据
│   ├── path_resolver.py             ← [v0.4.5] 灵活目录模板
│   ├── guard_orchestrator.py        ← 门禁总控调度
│   ├── init_db.py / check_schema.py ← 数据库初始化
│   └── ... (20+ guards)
│
├── database/
│   └── schema.sql                   ← SQLite schema（26 表 + 6 FTS5）
│
├── examples/
│   ├── demo_novel/                  ← Demo 骨架
│   ├── demo_chapters/               ← Demo 章节样本
│   └── demo_reports/                ← Demo 报告样本
│
├── tests/                           ← 32 个测试文件，238 个测试用例
├── docs/                            ← 架构 / 规范 / 发布说明
│   ├── releases/                    ← 历史版本发布说明
│   └── skills/                      ← Agent 写作路由
│
├── .github/workflows/test.yml       ← CI（pytest 自动跑）
└── README.md
```

---

## 核心能力

| 能力 | 作用 |
|------|------|
| SQLite 长期记忆 | 记录章节、人物、设定、摘要、标题、状态 |
| Chapter Pipeline | pre / post / review / volume 分阶段处理 |
| Guard Registry | 统一所有门禁入口，避免多入口结果漂移 |
| Continuity Evidence | 检查上一章状态、钩子、任务是否被承接 |
| Hallucination Guard | 阻止无依据新设定、矛盾设定、遗忘状态 |
| Scene Delta Guard | 检查场景是否真的发生推进 |
| Scene Causality Guard | 检查行动是否带来可见后果 |
| Anti-AI / QGP | 检测模板化、重复、总结腔、异常平滑 |
| Revision Loop | 输出可审阅的改稿建议，默认不覆盖原文 |
| Backup DB | 写作前备份 SQLite，降低数据损坏风险 |

---

## 工作流

```text
outline skeleton
    ↓
chapter_pipeline pre        ← 读上章结尾 + 查 SQLite + 出 task card
    ↓
write chapter txt           ← 正文写作（必须走 novel-factory skill）
    ↓
chapter_pipeline post       ← 跑全部门禁
    ↓
guard registry              ← 统一门禁入口 → guard_summary.json
    ↓
ingest to SQLite            ← 入库 + 切片 + FTS + 版本 + 摘要
    ↓
next chapter context        ← 自动读取上章 brief，进入下章 pre
```

---

## 适合谁使用？

- 想写 50 万字以上长篇小说的人
- 想让 AI 写作有长期记忆的人
- 想降低 AI 腔、模板腔、说明书腔的人
- 想做玄幻、科幻、修仙、连续剧情工程化写作的人
- 想让 Agent 按流程写，而不是普通聊天随便续写的人

---

## 文档导航

- [架构说明](docs/architecture.md)
- [数据库 Schema](docs/database.md)
- [流水线说明](docs/pipeline.md)
- [路线图](docs/ROADMAP.md)
- [Guard Registry](docs/GUARD_REGISTRY.md)
- [FTS5 自愈](docs/README_FULL.md#fts5)
- [Hermes Agent 写作规则](docs/HERMES_AGENT_RULES.md)
- [角色口吻与动作证据系统](docs/character_voice_action_proof_system.md)
- [QGP 困惑度质量门禁](docs/PERPLEXITY_QGP.md)
- [拟人审稿质量套件](docs/HUMAN_GRADE_REVISION_SUITE.md)
- [改稿闭环](docs/REVISION_LOOP.md)
- [部署指南](docs/setup-guide.md)

### Agent Skill 文档

- [novel-factory Router](docs/skills/novel_factory_router_SKILL.md) — 正文写作前必读
- [长篇写作行为规范](docs/skills/long_novel_writing_SKILL.md)

---

## 版本历史

| 版本 | 重点 |
|------|------|
| v0.4.5 | Guard Truth Source Fix — 门禁可信度修复 |
| v0.4.0 | Human-Grade Revision Suite — 拟人审稿 + 改稿闭环 |
| v0.3.1 | Quality Guard Patch — 误判校准 + 角色口吻 + QGP |

详见 [docs/releases/](docs/releases/)

---

## License

MIT
