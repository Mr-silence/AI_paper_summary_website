> generated_by: nexus-mapper v2
> verified_at: 2026-03-25
> provenance: Static test-surface analysis only; tests were not executed during this mapping run.

# Test Coverage

## Covered Surfaces

| Surface | Evidence | What is protected |
| --- | --- | --- |
| Scoring rules | `tests/backend/unit/test_scorer.py` | 8-signal scoring and taxonomy matching basics |
| Pipeline candidate/backfill rules | `tests/backend/unit/test_pipeline_rules.py` | candidate_reason assignment, reviewer demotion, overflow promotion, minimum-baseline failure |
| AI parsing contracts | `tests/backend/unit/test_ai_processor.py` | title localization constraints, zero-prefix parsing, reviewer ID validation, CN/EN highlight symmetry |
| Paper read APIs | `tests/backend/integration/test_papers_api.py` | candidate hiding by default, candidate null narrative semantics, latest detail snapshot, 404 behavior |
| Subscription APIs | `tests/backend/integration/test_subscribe_api.py` | pending subscriber creation, active-user token refresh, expired unsubscribe rejection, rate limiting |
| Frontend page rendering | `tests/frontend/home.spec.js`, `detail.spec.js`, `sources.spec.js`, `topic.spec.js` | feed grouping, candidate fallback UI, candidate pool rendering, topic filtering |
| External crawler health | `tests/live/test_crawler_live.py` | Hugging Face, arXiv, GitHub Trending, Semantic Scholar, merged crawler path |
| Repository smoke health | `tests/smoke/*` | backend import, `compileall`, backfill script import, frontend build |

## Coverage Interpretation

- Backend business rules are strongest around candidate lifecycle, AI output parsing, and read API envelope behavior.
- Frontend tests focus on page-level rendering with mocked API calls, which is appropriate for current thin-client architecture.
- Live tests deliberately cover the crawler against real external services, so the repository treats upstream source breakage as a first-class regression.

## Evidence Gaps

- `backend/app/api/v1/rss.py` has no direct test coverage, despite being user-facing output.
- `frontend/src/App.vue` has no dedicated test for language persistence, subscribe dialog validation, or success/error messaging.
- `frontend/src/views/Unsubscribe.vue` has no direct page test, even though it performs token-driven side effects.
- `backend/scripts/backfill_title_zh.py` only has import smoke coverage; there is no behavioral test for batch backfill semantics.
- There is no end-to-end automated test of `Pipeline.run()` across crawler -> scorer -> AI -> DB on a fully seeded environment.
- Database DDL / migration files are present, but there is no explicit schema-vs-ORM consistency test in `tests/`.

## Risk Notes

- Live tests make part of backend verification network-dependent by design; offline confidence is weaker for crawler correctness.
- The current test suite says more about contract fidelity than about deployment readiness. Scheduler behavior, email delivery, and production ops remain outside the tested repo surface.
