> generated_by: nexus-mapper v2
> verified_at: 2026-03-25
> provenance: AST-backed for Python and JavaScript; Vue files are module-only, so view responsibilities were verified by direct file inspection; backend dependency boundaries were cross-checked manually because AST import IDs do not fully normalize `app.*` imports.

# Systems

## 1. Daily Brief Pipeline

- Code path: `backend/app/services/`
- Primary files: `pipeline.py`, `crawler.py`, `scorer.py`, `ai_processor.py`
- Supporting assets: `backend/prompts/*.md`, `backend/scripts/backfill_title_zh.py`
- Responsibility: 抓取 Hugging Face Daily + arXiv 数据，补齐 citation/trending 信号，执行 8 信号评分、中文标题本地化、Editor/Writer/Reviewer 流程、候选补位与状态迁移，并将期号快照写回数据库。
- Key evidence:
  - `Pipeline.run()` 统一串起 fetch, score, title localization, threshold/capacity, seed snapshot, AI processing, reviewer rejection/backfill 与 task log 收尾。
  - `Crawler` 负责外部聚合与 metadata enrichment。
  - `Scorer` 将 PRD 中的 threshold、conference、institution、taxonomy 规则实体化。
  - `AIProcessor` 强制三阶段 LLM 合同与解析校验。
- Boundary note: 这是“写路径”和“选题路径”的中心系统，不负责对外 HTTP 展示。

## 2. Delivery API

- Code path: `backend/app/api/v1/`
- Primary files: `papers.py`, `subscribe.py`, `rss.py`, `backend/app/main.py`
- Responsibility: 将期号快照、订阅流程和 RSS 聚合包装成统一 JSON/XML 接口，供前端消费和浏览器跳转使用。
- Key evidence:
  - `papers.py` 提供 feed/detail 读接口，并控制 candidate 默认是否暴露。
  - `subscribe.py` 管理订阅申请、验证、退订与写接口限流。
  - `rss.py` 聚合最近 7 天 focus/watching 生成 XML。
  - `main.py` 负责 CORS、异常 envelope 与路由挂载。
- Boundary note: 该系统更多是“交付层”，不直接做采集、评分或 AI 推理。

## 3. Data Model & Persistence

- Code path: `backend/app/models/`
- Supporting paths: `backend/app/db/`, `database/`
- Primary files: `domain.py`, `session.py`, `database/schema.sql`, `database/migrate_v225.sql`
- Responsibility: 定义 `paper`、`paper_summary`、`subscriber`、`system_task_log` 的物理字段与关系，为跑批写入和 API 查询提供同一事实源。
- Key evidence:
  - `PaperSummary` 明确承载 score/category/candidate_reason/narrative 字段。
  - `Subscriber` 承载 verify/unsub token 生命周期。
  - `SessionLocal`/`get_db` 是 pipeline 与 API 的共同数据库入口。
  - `schema.sql` / migration SQL 说明仓库同时维护 ORM 与显式 DDL。
- Boundary note: 这是 Pipeline 和 Delivery API 的共享基础层。

## 4. Frontend Briefing UI

- Code path: `frontend/src/`
- Primary files: `App.vue`, `router/index.js`, `api/papers.js`, `utils/request.js`, `views/*.vue`
- Responsibility: 提供双语简报阅读体验，包括首页日期分组流、单篇详情、候选池明细、按技术方向聚合、退订结果页与订阅弹窗。
- Key evidence:
  - `App.vue` 提供全局语言状态、订阅弹窗和壳层布局。
  - `Home.vue` 将 paper list 按 `issue_date` 分组，并拆成 Focus/Watching 两段。
  - `Detail.vue` 区分 candidate 与非 candidate 的 narrative 展示。
  - `Sources.vue` / `Topic.vue` 把候选池和方向过滤显式暴露给用户。
  - `Unsubscribe.vue` 直接消费 token 参数调用退订 API。
- Boundary note: 该系统不是纯展示层，视图内部已经承载分组、分页、请求去重与 server-side filter 参数构造。

## 5. Test & Smoke Harness

- Code path: `tests/`
- Responsibility: 以 unit/integration/frontend/live/smoke 五层结构约束核心业务合同、API 行为、前端页面、外部抓取路径与仓库级健康。
- Key evidence:
  - `tests/backend/unit/` 覆盖 scorer、pipeline backfill/candidate 规则、AI 输出解析。
  - `tests/backend/integration/` 覆盖 papers/subscribe API 与 DB 行为。
  - `tests/frontend/` 以 mocked API 验证 Home/Detail/Sources/Topic 四个页面。
  - `tests/live/` 真实访问 Hugging Face、arXiv、GitHub Trending、Semantic Scholar。
  - `tests/smoke/` 覆盖 backend import/compile、frontend build、脚本 import。

## Boundary Corrections

### `filter.py` 不是当前生产系统的一部分

- 证据线索: `rg` 结果显示 `backend/app/services/filter.py` 仅在自身 `__main__` 中被引用，没有任何生产代码 import 它。
- 结论: 它更像早期按 upvotes 筛选的遗留模块，不应被画入现行选题/跑批主链。

### 日更调度不在仓库内

- 证据线索: `Pipeline(db).run()` 只在 `pipeline.py` 的 `__main__` 守卫中出现，仓库内没有 scheduler、worker、cron、Celery、Airflow、Prefect 等实现。
- 结论: “每日执行”是部署外责任；仓库提供的是可调用的批处理入口和状态机，而不是调度系统本身。
