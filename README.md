# Novel Forge — 小说引擎 v0.7.2

[![Test](https://github.com/remacheybn408-boop/Novel-Forge/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/remacheybn408-boop/Novel-Forge/actions/workflows/test.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT%20OR%20GPL--3.0-green)
![Version](https://img.shields.io/badge/version-v0.7.2-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

轻量小说工程化写作流水线——专注长篇小说的连续性、角色口吻一致性、AI 腔检测、防幻觉、写前任务卡和写后质量报告。

---

## v0.7.1 核心能力

| # | 能力 | 说明 |
|---|------|------|
| 1 | **多小说独立数据库** | 每本小说一个 slot，独立 `novel.db`，内容不串库 |
| 2 | **大纲版本管理** | 无大纲不开写；新小说自动建库；原小说出新版大纲只新增版本，不覆盖旧数据 |
| 3 | **Agent 陪审团** | 20 个评审 Agent，覆盖角色口吻、AI 腔、场景落地、情绪递进、伏笔、追读力 |
| 4 | **Story Contract 主链** | 写前生成章节合同，写后提交章节记录，追踪目标、人物状态、伏笔推进和世界观连续 |
| 5 | **普通用户菜单** | 终端输入 `python novel.py menu` 即可进入交互菜单，不要求记命令 |
| 6 | **三端适配** | Windows，Shell 脚本 |
| 7 | **发布稳定性检查** | `python novel.py stability-check` 一键验收，覆盖版本号、pytest、demo 全流程 |
| 8 | **人工味质量层 (Human Texture)** | 8 个子检测自动运行：水文、剧情进度、陈词滥句、冲突压力、情绪总结、生活质感、节奏、声线多样性 |
| 9 | **题材写作预设** | 25 种 genre + 19 种 style 写作预设，`python novel.py genre` / `python novel.py style` 查看 |
| 10 | **角色综合管理** | 角色卡 4 维度 30 字段（声纹/性格/做事风格/叙事层）+ 精神状态管理，`python novel.py character` 全面管理 |
| 11 | **MCP 中文菜单桥接层** | 19 个安全 MCP 工具，AI 客户端通过中文直接操作引擎，零命令暴露 |
| 13 | **角色精神状态系统** | 角色卡第五层：15 类精神状况（PTSD/抑郁/焦虑等），severity 0-5 + 诱因 + 触发词 + 章节追踪，`character mental` CLI 管理 |

---

## v0.7.2 新增能力

| # | 能力 | 说明 |
|---|------|------|
| 1 | **Guard 扩展至 27 个** | 新增 5 个 Guard：情感渲染力、开篇吸引力、感官描写浓度、节奏变化、视角一致性。覆盖从"有没有AI腔"到"读起来好不好看"的全维度 |
| 2 | **角色叙事层 (10 字段)** | 角色卡新增第5维度：动机、致命缺陷、秘密、关键创伤、短期/长期目标、特长、短板、预定弧线、弧线当前。旧卡自动补齐 |
| 3 | **Story Arc 三合一架构** | 规划 Context + Promise + Plot Threads 合并为统一故事弧线追踪系统，实现跨章跨卷的状态/物品/情绪/承诺对齐检测（见 `plans/story-arc-merge-plan.md`） |
| 4 | **都市言情 30 章 Demo 小说** | 内置完整 30 章都市言情小说「城与光之间」(71,710 汉字)，含 28 张角色卡、全流程 pipeline 验证 |
| 5 | **`.story/` 自动创建** | 修复 story commit 时目录缺失的 `[WinError 3]` 路径问题 |

---

## 规划中 (Roadmap)

| 版本 | 功能 | 说明 |
|------|------|------|
| v0.7.4 | **Guard 建议自动改稿** | revise 命令接入 Guard 输出，自动执行建议修改并生成 diff |
| v0.7.5 | **RAG 全文检索 + 综合质量评分** | 当前 FTS5 基础上升级语义搜索；同时聚合 Guard 评分、Agent 陪审团审稿分、Human Texture 质量分、故事链健康度、角色弧线完整度、承诺兑现率、情节线完结率，输出单章/全本综合质量看板 |

---

## 怎么用

### 普通用户

在终端输入以下命令，按菜单提示操作：

```bash
python novel.py menu
```

然后按数字选择：添加大纲 → 开始写作 → Agent 审稿 → 导出小说。不需要记其他命令。

### 高级用户 / CLI

```bash
# 初始化
python novel.py init
python novel.py db init

# 全流程
python novel.py demo

# 日常写作
python novel.py pre 1             # 写前任务卡
python novel.py post 1            # 入库 + 27 Guard 门禁
python novel.py agents review 1 --mode full  # 20 Agent 审稿

# 角色管理
python novel.py character list              # 列出角色
python novel.py character show <角色名>     # 查看完整角色卡（含叙事层）
python novel.py character edit <名> <字段> <值>  # 编辑声纹/性格/叙事层
python novel.py character mental <名>       # 管理精神状态

# 质量检测
python novel.py texture check 1             # 人工味质量层 (8 项)
python novel.py check <文件路径>            # 单章检查
python novel.py revise 1 --mode suggest     # 自动改稿

# 故事链
python novel.py story health                # 故事链健康检查

# 上下文 / 伏笔 / 情节线
python novel.py context show 1              # 查看某章上下文
python novel.py context gap                 # 检测物品断层
python novel.py promises list               # 读者承诺管理
python novel.py plot-threads list           # 情节线管理

# 世界观与题材
python novel.py worldbuilding list          # 世界观条目
python novel.py genre list                  # 25 种题材预设
python novel.py style list                  # 19 种风格预设

# 查询
python novel.py query "主角的玉佩在哪里"    # 自然语言查询
python novel.py rag status                  # RAG 状态

# 发布验收
python novel.py stability-check

# 查看报告 & 导出
python novel.py report
python novel.py export --slug <slug>
```

---

## 典型工作流

```text
大纲骨架
    ↓
pre（写前任务卡）      ← 读取上章结尾 + SQLite 上下文
    ↓
写作（按任务卡生成正文）
    ↓
post（27 Guard 门禁） ← 幻觉 / 连续性 / AI腔 / 口吻 / 开篇 / 感官 / 节奏 / 情感 / 视角等
    ↓
agents review（可选）  ← 20 Agent + Chief Editor 审稿
    ↓
ingest to SQLite       ← 入库 + 切片 + FTS + 摘要
    ↓
下一章 pre             ← 自动读取本章 brief
```

---

## 两套审稿体系

本项目包含两层互补的质量检查：

| 体系 | 数量 | 触发方式 | 职责 |
|------|------|---------|------|
| **Guard 门禁** | 27 个（draft=5 / standard=18 / submission=26） | post 自动运行 | 拦截：幻觉、连续性断裂、AI腔、开篇乏力、感官空白、节奏失衡、视角跳跃 |
| **Agent 陪审团** | 20 个评审 Agent | 手动 `agents review` | 评估：动作自然度、潜台词、情绪递进、场景落地、节奏呼吸 |
| **发布前审稿** | 20 Agent + 主编汇总 | 发布前运行 | 风险分级、must_fix / should_fix / keep 分类 |

Guard 和 Agent 互补不重叠。Guard 保证不写错，Agent 帮助写更好。

---

## 多小说独立数据库

每本小说有独立的 SQLite 数据库（slot 机制）：

```
workspace/
├── slot_001/          ← 小说 A 的全部数据
│   ├── novel.db
│   ├── chapters/
│   └── outlines/
├── slot_002/          ← 小说 B 的全部数据
│   ├── novel.db
│   ├── chapters/
│   └── outlines/
└── registry.json      ← 活跃 slot 记录
```

- 默认 3 个 slot，用满自动添加
- 小说之间大纲、章节、角色状态互不干扰
- 支持切换、备份、恢复

---

## 大纲管理规则

- **无大纲不开写**：没有激活大纲时，阻止 pre 写作
- **新小说自动建库**：首次添加大纲会自动创建对应 slot
- **版本管理**：同一小说新增大纲只递增版本号，不覆盖旧数据
- **相似度判断**：导入大纲时自动检测与已有大纲的相似度，提示是否为新增版本

---

## Story Contract 简介

写前和写后各生成一份结构化 JSON，作为章节质量的"审计链"：

```
写前合同：章节目标、承接上下文、活跃角色、开放伏笔、禁止变更
写后提交：实际事件、角色状态变化、新承诺、已兑现伏笔、下一章钩子
```

合同和提交数据可用于 `story health` 检查故事链完整性。

---

## 稳定性检查

```bash
python novel.py stability-check --full
```

输出示例：

```
[✓] 版本号一致性: VERSION=v0.7.2
[✓] 配置文件: config.json 可解析
[✓] workspace 初始化
[✓] 默认 slot 完整: N 个 slot
[✓] active slot DB
[✓] Agent 类: 18+
[✓] pytest: exit=0
[✓] 交叉平台: 通过
[✓] Slot FTS 完整性
[✓] 结构自检: DB✓ CFG✓ WS✓
[✓] demo 全流程: exit=0

稳定性评分: 95/100
P0 问题: 0 个
建议: 可以发布正式版
```

---

## 目录结构

```
novel.py                         ← CLI 入口
src/
├── cli/                         ← 命令实现
│   ├── shared.py                ← 共用 helpers
│   ├── commands_core.py         ← 核心命令（report/guards/check/init）
│   ├── commands_demo.py         ← demo 演示
│   ├── commands_pipeline.py     ← 流水线（pre/post/review/export）
│   ├── commands_story.py        ← Story Contract
│   ├── commands_memory.py       ← RAG 记忆查询
│   ├── commands_agents.py       ← Agent 陪审团
│   ├── commands_diagnostic.py   ← 诊断（board/stability-check）
│   ├── commands_db.py           ← DB 管理
│   ├── commands_outline.py      ← 大纲管理
│   ├── commands_menu.py         ← 菜单/帮助
│   └── commands_status.py       ← 状态诊断
├── guards/                      ← 27 个门禁规则模块
├── task_card/                   ← 写前任务卡
├── voice/                       ← Voice Pack 加载器
└── report/                      ← HTML 报告生成

scripts/
├── agents/                      ← 20 Agent 陪审团
├── guard_registry.py            ← 门禁注册中心
├── guard_result.py              ← 门禁数据结构
├── chapter_pipeline.py          ← 主流水线
└── ...其他辅助模块

configs/
├── agents.yaml                  ← Agent 陪审团配置
└── jury/agents/                 ← 陪审团配置库

tests/                           ← 300 个测试用例
voice_packs/                     ← 声纹包
genre_packs/                     ← 题材模板
style_packs/                     ← 风格模板
```

---

## 文档入口

- [架构说明](docs/architecture.md)
- [数据库 Schema](docs/database.md)
- [流水线说明](docs/pipeline.md)
- [更新日志](CHANGELOG.md)
- [Guard Registry](docs/GUARD_REGISTRY.md)
- [Agent 陪审团说明](scripts/agents/README.md)
- [部署指南](docs/setup-guide.md)

---

## Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for full list.

---

## License

**开源版**：AGPL-3.0 — 修改后以 SaaS / API 对外提供服务者，须按 AGPL-3.0 公开修改源码。详见 [LICENSE](LICENSE)。

**商业版**：如需闭源使用（含商业产品集成、SaaS 服务、企业内部部署），见 [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md) 或联系 [你的邮箱 / 微信]。
