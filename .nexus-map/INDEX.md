> generated_by: nexus-mapper v2
> verified_at: 2026-03-25
> provenance: AST-backed for Python and JavaScript; Vue and SQL files are module-only; backend internal dependency notes are partially inferred because module IDs are emitted as `backend.app.*` while Python imports resolve as `app.*`; git hotspot data is available from 15 commits by 1 author.

# AI_paper_summary_website

## Snapshot

- 这是一个 FastAPI + MySQL + Vue 3 的 AI 论文简报站点仓库，目标是按 PRD 规则生成双语每日简报并提供历史浏览、候选池、Topic 聚合、RSS 与订阅能力。
- 后端核心生产链是 `Crawler -> Scorer -> AIProcessor -> Pipeline -> paper/paper_summary/system_task_log`，主实现位于 `backend/app/services/`。
- 前端核心消费链是 `App.vue -> router -> Home/Detail/Sources/Topic/Unsubscribe -> api/papers.js -> /api/v1/*`，主实现位于 `frontend/src/`。
- 测试结构清晰，覆盖 unit/integration/frontend/live/smoke 五层，但 `rss.py`、`App.vue` 订阅弹窗、`Unsubscribe.vue` 与完整 `Pipeline.run()` 端到端流程仍缺直接自动化保护。
- 发现两个重要边界事实：`backend/app/services/filter.py` 没有被任何生产代码引用，属于遗留孤立模块；仓库没有内置 scheduler/worker，`Pipeline(db).run()` 只是可调用入口，日更调度应由部署环境承担。

## Systems

| System | Owns | Read Next |
| --- | --- | --- |
| Daily Brief Pipeline | 采集、评分、AI 解读、补位、快照落库 | `arch/systems.md` |
| Delivery API | 列表/详情/订阅/RSS 读写接口与 envelope | `arch/dependencies.md` |
| Data Model & Persistence | SQLAlchemy 模型、会话、MySQL schema 契约 | `concepts/domains.md` |
| Frontend Briefing UI | 简报浏览、候选池、Topic、退订、订阅 UX | `arch/dependencies.md` |
| Test & Smoke Harness | 合同回归、前端页面测试、live crawler、构建烟测 | `arch/test_coverage.md` |

## High-Signal Findings

- 前端最易一起变动的界面是 `Home.vue` 与 `Detail.vue`；Git coupling 为 `1.0`，说明 feed 与 detail 的展示规则通常同步演化。
- 后端最常见的联动中心是 `backend/app/api/v1/papers.py`，它与 `subscribe.py`、`domain.py`、`schemas/paper.py`、`ai_processor.py`、`crawler.py`、`pipeline.py` 都有共同提交记录，意味着 payload 或 candidate 规则改动会穿透多层。
- PRD 文档和记忆文件 (`Detailed_PRD.md`, `geminicli.md`, `CODEX_MEMORY.md`) 的变更热度高于代码本身，说明当前仓库的真实风险之一是“规范仍在演进”，而不是只有实现复杂度。

## Evidence Gaps

- 自动 AST `impact` 图对后端 Python 内部 import 的识别不完整，因此系统依赖图对后端部分使用了代码导入与 Git 耦合作为补证。
- 未发现生产级调度、邮件发送、任务 worker 或部署编排代码；日更、发送与运维行为大概率在仓库外完成。

## [操作指南] 强制执行步骤

> 本节是对所有读取本文件的 AI 发出的硬性操作指令，不是建议。

1. 先读 `arch/systems.md`，确认你要改动的是哪一个系统，避免把 Delivery API、Pipeline 和 Persistence 混成一个层。
2. 若任务涉及接口、候选状态、分数、订阅、字段新增或跨模块修改，必须继续读 `arch/dependencies.md` 和 `concepts/domains.md`，再决定改动面。
3. 若任务涉及风险评估、测试补强或重构优先级，必须继续读 `arch/test_coverage.md` 和 `hotspots/git_forensics.md`。
4. 若任务会改变系统边界、入口、依赖关系、候选状态机或 API payload，交付前评估是否需要更新 `.nexus-map/`。
5. 不要把 `backend/app/services/filter.py` 当成现行生产链的一部分；除非显式重启用它，否则它应视为遗留代码。
