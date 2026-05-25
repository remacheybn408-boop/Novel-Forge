# v0.5.0 — Stable & Easy Mode

## 版本定位

v0.5.0 是一次**稳定易用性升级**，不做复杂多 Agent 系统，不引入 Web 前端，不依赖外部 LLM 语义判断。主打：**一个统一入口、一键 Windows 体验、跑得通、看得懂、改得动**。

---

## 要解决的 5 个问题

1. **入口碎片化**：v0.4.x 的 init / pre / post / review / report 散落在不同脚本中，需要手动传 config 和 slug。v0.5.0 统一为 `novel.py` 一个命令。
2. **环境问题排查困难**：没有健康检查，用户遇到「跑不起来」只能逐一手检 Python、config、目录。v0.5.0 提供 `python novel.py status`。
3. **写前缺少结构化引导**：pre 阶段只是一个 chapter_brief JSON，AI 拿到后仍然是自由发挥。v0.5.0 增加写前任务卡 Task Card，明确承接/推进/禁止。
4. **追读力不可度量**：v0.4.x 有场景推进、因果代价检查，但没有针对网文追读力（钩子/兑现/悬念/爽点）专门设计门禁。v0.5.0 增加 Reader Pull Guard。
5. **审稿结果不可阅读**：guard_summary.json 是裸 JSON。v0.5.0 增加 HTML 只读报告，纯静态，双击即开。

---

## v0.5.0 不做什么

1. 不做完整多 Agent 写作系统（预留目录但默认关闭）
2. 不做 Web Dashboard 前端工程
3. 不做 Vector / Graph Hybrid RAG
4. 不做 37 个题材模板（只保留 5 个核心题材）
5. 不做在线服务 / FastAPI 后端
6. 不做 LLM 语义门禁（Semantic Judge mode=off）
7. 不做新手引导 wizard
8. 不做自动发布 / CD 流水线

---

## 功能清单

### P0（核心功能，10 项）

| # | 功能 | 说明 |
|---|------|------|
| 1 | 统一命令入口 `novel.py` | init / demo / status / pre / post / review / report / export / guards / check |
| 2 | status 健康检查 | Python 版本、config.json、核心模块、voice_packs 目录一键诊断 |
| 3 | 写前任务卡 Task Card | 从 SQLite 提取上下文，输出承接项/推进项/禁止项 + Voice/Meme 提醒 |
| 4 | Reader Pull Guard | 钩子设置、钩子兑现、悬念推进、爽点落地、代价展示 5 维追读力门禁 |
| 5 | Voice Pack 增强 | 41 个语言包（方言/语体/梗/英语/旁白/禁用），YAML 格式，加载器 + 校验器 |
| 6 | Meme Pack 增强 | 梗浓度控制 + 角色绑定 + 场景绑定 + 冷静期，YAML 格式 |
| 7 | HTML 只读报告 | 纯静态 HTML，无 CDN 依赖，双击即开，汇总所有 guard 结果 |
| 8 | 5 种题材模板 | 修仙 / 都市异能 / 规则怪谈 / 悬疑 / 科幻，YAML 格式 |
| 9 | Windows 一键体验 | install.bat → run_demo.bat → run_report.bat |
| 10 | 章节风险评分 | 8 维度评分（词数、场景、钩子、AI腔、水文、对白、破折号、梗浓度） |

### P1（增强功能，5 项）

| # | 功能 | 说明 |
|---|------|------|
| 11 | 多 Agent 预留目录 | src/agents/ 目录结构预留，默认关闭 |
| 12 | 对白密度门禁 | >10% 行数为对白 → WARNING，>20% → SEVERE |
| 13 | 破折号密度门禁 | >5/千字 → WARNING，>12/千字 → SEVERE |
| 14 | 无引号对白检测 | fallback 模式，检测无引号标记的对白 |
| 15 | 导出功能 | python novel.py export 导出完整小说 |

### P2（辅助功能，4 项）

| # | 功能 | 说明 |
|---|------|------|
| 16 | Guard 列表查看 | python novel.py guards 列出所有注册门禁 |
| 17 | 单文件门禁检查 | python novel.py check <file> 对任意文件跑门禁 |
| 18 | 报告缓存 | 报告生成后缓存，避免重复计算 |
| 19 | 测试覆盖 | 48 个测试文件，268 个测试用例 |

---

## 统一入口命令表

| 命令 | 功能 |
|------|------|
| `python novel.py status` | 环境健康检查 |
| `python novel.py demo` | 跑通 Demo（pre for chapter 1） |
| `python novel.py pre <N>` | 生成第 N 章写前任务卡 |
| `python novel.py post <N>` | 入库第 N 章 + 跑全部门禁 |
| `python novel.py review <N>` | 审查第 N 章 |
| `python novel.py report` | 生成 HTML 报告 |
| `python novel.py export` | 导出完整小说 |
| `python novel.py guards` | 列出已注册门禁 |
| `python novel.py check <file>` | 对任意文件跑门禁检查 |

---

## 目录结构（v0.5.0 新增/变更）

```
novel-pipeline-write-engine/
├── novel.py                         ← [NEW] 统一入口
├── install.bat                      ← [NEW] Windows 一键安装
├── run_demo.bat                     ← [NEW] Windows 一键运行
├── run_report.bat                   ← [NEW] 双击打开 HTML 报告
├── run_status.bat                   ← [NEW] 双击运行健康检查
├── CHANGELOG.md                     ← [NEW] 版本变更日志
├── src/                             ← [NEW] 模块化源码目录
│   ├── cli/commands_status.py       ← status 命令
│   ├── guards/                      ← 门禁模块
│   │   ├── reader_pull_guard.py     ← [NEW] 追读力门禁
│   │   ├── voice_pack_guard.py      ← [NEW] 声纹门禁
│   │   └── meme_pack_guard.py       ← [NEW] 梗浓度门禁
│   ├── task_card/task_card_builder.py ← [NEW] 写前任务卡
│   ├── voice/                       ← [NEW] Voice Pack 加载器
│   ├── meme/                        ← [NEW] Meme Pack 加载器
│   └── report/html_report_builder.py ← [NEW] HTML 报告生成
├── templates/                       ← [NEW] 模板目录
│   ├── genres/                      ← 5 种题材模板 YAML
│   ├── voice_pack/                  ← 声纹 YAML 模板
│   └── meme_pack/                   ← 梗包 YAML 模板
├── voice_packs/                     ← [UPDATED] 41 个语言包
│   ├── base/
│   ├── registers/
│   ├── dialects/
│   ├── memes/
│   ├── english/
│   ├── bindings/
│   └── samples/
├── reports/index.html               ← [NEW] HTML 只读报告
├── outputs/task_cards/              ← [NEW] 任务卡输出目录
└── docs/
    ├── V050_STABLE_EASY_MODE.md     ← [NEW] 本文档
    └── releases/v0.5.0.md           ← [NEW] 发布说明
```

---

## status 健康检查说明

`python novel.py status` 执行以下检查：

| 检查项 | 说明 |
|--------|------|
| Python 版本 | 要求 ≥ 3.10 |
| config.json | 是否存在 |
| src/guards/reader_pull_guard.py | 追读力门禁模块 |
| src/guards/voice_pack_guard.py | 声纹门禁模块 |
| src/guards/meme_pack_guard.py | 梗浓度门禁模块 |
| voice_packs/ 目录 | 语言资产目录完整性 |
| templates/ 目录 | 模板目录完整性 |
| SQLite 数据库 | 数据库文件存在性 |
| requirements.txt 依赖 | Python 依赖安装状态 |
| scripts/ 核心脚本 | 关键脚本模块可导入性 |

---

## Voice Pack / Meme Pack 增强说明

### Voice Pack（41 个语言包）

v0.5.0 将 Voice Pack 从 JSON 升级为 YAML 格式，并解耦小说角色依赖：

- **base/** — 9 个通用角色声纹包（理工型主角、接地气好兄弟、武力型对手、冷契约型反派等）
- **registers/** — 8 个语体包（学者腔、官腔、冷BOSS腔、江湖语体、古文腔等）
- **dialects/** — 6 个方言包（东北、四川、山东、河南、陕西、山西）
- **memes/** — 2 个梗包（轻度网络梗、禁用梗库）
- **english/** — 2 个英语包（物理学术英语、禁用英语）
- **旁白/禁用** — 旁白语体和全局禁用词
- **通用设计**：所有 base pack 使用通用角色类型，不绑定具体小说角色

### Meme Pack 增强

- **梗浓度控制**：可配置最大梗密度（如每千字 ≤ 2 个梗）
- **角色绑定**：梗包可以绑定到特定角色类型
- **场景绑定**：按场景类型（战斗/日常/对话/独白）控制梗使用
- **冷静期**：连续梗使用后强制冷静间隔
- **banned_memes**：内置高频网络热梗禁用库（家人们谁懂啊、尊嘟假嘟、yyds 等）

---

## 写前任务卡 Task Card 说明

`python novel.py pre <N>` 自动从 SQLite 提取以下信息并生成结构化任务卡：

| 分区 | 内容 |
|------|------|
| 承接（Carry Over） | 上一章结尾状态、未解决的钩子、进行中的任务 |
| 推进（Progress） | 本章标题、章节目标、预期推进方向 |
| 禁止（Forbidden） | 不能出现的内容、不能遗忘的状态 |
| Voice 提醒 | 本章各角色应使用的声纹包 |
| Meme 提醒 | 本章可用的梗包及浓度限制 |

任务卡输出位置：`outputs/task_cards/chapter_<N>_task_card.md`

---

## Reader Pull Guard 追读力门禁说明

Reader Pull Guard 是 v0.5.0 核心新增门禁，专门检查网文追读力：

| 维度 | 检查内容 |
|------|----------|
| 钩子设置 | 本章末尾是否设置了新的钩子（悬念/预告/未解冲突） |
| 钩子兑现 | 上一章设置的钩子是否在本章得到回应 |
| 悬念推进 | 主线悬念是否有实质性推进 |
| 爽点落地 | 本章是否有爽点落地（打脸/升级/反转/收获） |
| 代价展示 | 行动是否带来可见代价或后果 |

输出格式：每个维度给出 PASS / WARNING / FAIL，附带具体证据行号。

---

## 章节风险评分说明

`risk_score.py` 对每章进行 8 维度风险评分：

| 维度 | 权重 | 说明 |
|------|------|------|
| 词数 | 10% | 是否在合理区间 |
| 场景数 | 15% | 有效场景数量 |
| 钩子 | 20% | 钩子设置与兑现 |
| AI 腔 | 15% | 模板化/总结腔/说明书腔 |
| 水文 | 15% | 同义重复/设定堆砌 |
| 对白密度 | 10% | 对白占比合理性 |
| 破折号密度 | 5% | 破折号使用频率 |
| 梗浓度 | 10% | 梗使用的合理性 |

综合评分：A（优秀）/ B（良好）/ C（需关注）/ D（需修改）/ F（不合格）

---

## HTML 报告说明

`python novel.py report` 生成纯静态 HTML 报告，特点：

- **纯静态**：无 JavaScript CDN 依赖，无外部资源
- **双击即开**：`run_report.bat` 自动打开 `reports/index.html`
- **内容**：汇总所有 guard 结果、风险评分、任务卡状态
- **离线可用**：完全离线工作，不需要网络连接
- **可分享**：单个 HTML 文件，可以直接发送给审稿人

---

## 题材模板说明

v0.5.0 内置 5 种题材模板（`templates/genres/`），YAML 格式：

| 模板 | 文件 | 说明 |
|------|------|------|
| 修仙 | xianxia.yaml | 修炼体系、境界、丹药、法宝 |
| 都市异能 | urban_power.yaml | 现代都市 + 超能力 |
| 规则怪谈 | rule_horror.yaml | 规则系恐怖、逻辑怪谈 |
| 悬疑 | mystery.yaml | 推理、线索、反转 |
| 科幻 | sci_fi.yaml | 科技设定、未来世界 |

模板包含题材默认的 Voice Pack / Meme Pack 推荐和禁用规则。

---

## 安装和快速开始

### Windows 一键体验

```bat
install.bat              ← 创建虚拟环境 + 安装依赖
run_demo.bat             ← 运行 Demo
run_report.bat           ← 打开 HTML 报告
```

### 命令行

```bash
# 克隆
git clone https://github.com/remacheybn408-boop/novel-pipeline-write-engine.git
cd novel-pipeline-write-engine

# 配置
cp config.example.json config.json

# 健康检查
python novel.py status

# Demo
python novel.py demo

# 写前任务卡
python novel.py pre 1

# 入库 + 门禁
python novel.py post 1

# 报告
python novel.py report
```

---

## 与 Webnovel Writer 的区别

| 维度 | Novel Pipeline Write Engine | Webnovel Writer |
|------|----------------------------|-----------------|
| 定位 | 工程化写作流水线 | 聊天式 AI 写作助手 |
| 记忆 | SQLite 长期记忆（26 表 + 6 FTS5） | 聊天上下文窗口 |
| 门禁 | 15+ 规则门禁 + 风险评分 | 无 |
| 连续性 | 章间承接证据 + 因果代价 | 依赖 AI 自行记忆 |
| 格式 | TXT + YAML 模板 | 聊天消息 |
| 报告 | HTML 静态报告 | 无 |
| 依赖 | Python 3.10+，零外部服务 | 依赖 LLM API |

---

## Roadmap

### v0.5.0（当前版本）✅
- 统一入口 + 健康检查 + 写前任务卡 + Reader Pull Guard + HTML 报告

### v0.5.1（下一版本）
- 完整多 Agent 写作系统（启用预留目录）
- 更多题材模板（目标 37 个）
- Vector / Graph Hybrid RAG
- 新手引导 Wizard

### v0.6.0
- Web Dashboard 前端
- FastAPI 后端
- 自动发布流水线

---

## 验收标准

| 标准 | 状态 |
|------|------|
| `python novel.py status` 全部 PASS | ✅ |
| `python novel.py demo` 成功运行 | ✅ |
| `python novel.py pre 1` 生成任务卡 | ✅ |
| `python novel.py post 1` 入库 + 门禁 | ✅ |
| `python novel.py report` 生成 HTML | ✅ |
| `python novel.py guards` 列出所有门禁 | ✅ |
| `install.bat` → `run_demo.bat` → `run_report.bat` 一键体验 | ✅ |
| 48 个测试文件，268 个测试用例（267 通过，1 个预存 config 路径差异） | ✅ |
| README 全面更新 | ✅ |
| CHANGELOG.md 创建 | ✅ |
| docs/releases/v0.5.0.md 发布说明 | ✅ |
