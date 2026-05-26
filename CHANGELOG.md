# Changelog

## v0.6.0 - Story Contract CLI Release (2026-05-26)

- 新增 Story Contract 命令组：story init / contract / commit / health
- 新增 query / learn / board 项目记忆和只读状态看板
- 修复 nested config(paths/novel/gates) 与旧脚本顶层字段不兼容的问题
- 修复 init 建库路径与 status 检查路径不一致的问题
- 修复 demo 未先运行 pre 导致 post 必失败的问题
- 清理发布包中的旧后端残留、.vite 缓存、嵌套 write-engine 副本和乱码 README
- 修复 tests/test_agent_run_guard.py 子进程测试不稳定问题，296 tests 全绿

## v0.5.6 - Clean CLI Release (2026-05-26)

### Fixed
- chapter_pipeline.py: chapter dir path now includes novel slug (novels/<slug>/第01卷)
- agents review: path resolution now includes novel slug
- Report directory: unified from reports/ to exports/reports/
- Demo: now runs post (ingest to DB) after creating chapter
- test_agent_run_guard.py: hardened subprocess handling to prevent hangs
- tmp/ removed from git tracking

### Changed
- README updated to v0.5.6 (title, test count 296, version lines)
- novel.py header updated to v0.5.6
- cmd_init creates exports/reports instead of reports/

## v0.5.5 - Stable & Easy Mode (2026-05-25)

### Added
- 统一命令入口 novel.py（init/demo/status/pre/post/review/report/export）
- status 健康检查命令
- 增强 Voice Pack（41 个语言包，含方言/语体/梗/英语/旁白/禁用）
- 增强 Meme Pack（梗浓度控制 + 角色绑定 + 场景绑定 + 冷静期）
- 写前任务卡 Task Card（承接/推进/禁止 + Voice/Meme 提醒）
- Reader Pull Guard 追读力门禁（钩子/兑现/悬念/爽点/代价）
- 章节风险评分 risk_score.py（8 维度）
- HTML 只读报告（纯静态，无 CDN，双击即开）
- 5 种题材模板（修仙/都市异能/规则怪谈/悬疑/科幻）
- YAML Voice Pack / Meme Pack 资产格式
- Windows 一键体验脚本（install.bat → run_demo.bat → run_report.bat）
- 多 Agent 预留目录（默认关闭，不影响主流程）

### Changed
- README 全面更新到 v0.5.5（重点、快速开始、目录结构、版本历史）
- Voice Pack 核心与小说角色解耦
- 对白密度门禁（>10% WARNING, >20% SEVERE）
- 破折号密度门禁（>5/千字 WARNING, >12/千字 SEVERE）
- 无引号对白检测 fallback 模式

### Not Included (for future versions)
- 完整多 Agent 写作系统
- Web Dashboard 前端工程
- Vector / Graph Hybrid RAG
- 37 个题材模板
