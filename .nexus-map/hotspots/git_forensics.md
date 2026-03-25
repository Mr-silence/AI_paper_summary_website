> generated_by: nexus-mapper v2
> verified_at: 2026-03-25
> provenance: Derived from `.nexus-map/raw/git_stats.json`; interpret cautiously because the repository currently has only 15 commits by 1 author in the analyzed window.

# Git Forensics

## History Shape

- Commits analyzed: `15`
- Authors analyzed: `1`
- Practical meaning: hotspot and coupling results are useful, but still low-sample. They show current change clusters, not long-term organizational truth.

## Top Hotspots

| File | Changes | Risk | Interpretation |
| --- | ---: | --- | --- |
| `CODEX_MEMORY.md` | 13 | medium | Product/implementation memory is still actively evolving |
| `geminicli.md` | 7 | medium | Tooling/process guidance changed repeatedly |
| `Detailed_PRD.md` | 6 | medium | Requirements are still being refined in-repo |
| `frontend/src/views/Detail.vue` | 4 | low | Detail rendering semantics are still settling |
| `frontend/src/views/Home.vue` | 4 | low | Home feed grouping and display rules evolve with detail page |
| `backend/app/api/v1/papers.py` | 3 | low | Paper payload surface is a common backend touchpoint |
| `backend/app/api/v1/subscribe.py` | 3 | low | Subscription behavior still being tuned |
| `backend/app/models/domain.py` | 3 | low | Persistence schema moves when payload/state semantics change |
| `backend/app/schemas/paper.py` | 3 | low | API schema changes ripple through the stack |
| `backend/app/services/ai_processor.py` | 3 | low | AI contract parsing remains part of active refinement |

## Strong Co-change Pairs

| Pair | Score | Why it matters |
| --- | ---: | --- |
| `CODEX_MEMORY.md` <-> `geminicli.md` | 0.857 | Internal guidance and working-memory docs are maintained together |
| `CODEX_MEMORY.md` <-> `Detailed_PRD.md` | 0.833 | Product rules and implementation memory are tightly linked |
| `Detailed_PRD.md` <-> `geminicli.md` | 0.833 | Docs are currently evolving as a set |
| `frontend/src/views/Detail.vue` <-> `frontend/src/views/Home.vue` | 1.000 | Feed/detail UX and category semantics should be treated as one edit zone |
| `backend/app/api/v1/papers.py` <-> `backend/app/api/v1/subscribe.py` | 1.000 | Backend endpoint semantics changed together in the current history |
| `backend/app/api/v1/papers.py` <-> `backend/app/models/domain.py` | 1.000 | Payload changes tend to require ORM updates |
| `backend/app/api/v1/papers.py` <-> `backend/app/schemas/paper.py` | 1.000 | API contract and schema objects move in lockstep |
| `backend/app/api/v1/papers.py` <-> `backend/app/services/ai_processor.py` | 1.000 | Narrative field semantics can ripple into serialization |
| `backend/app/api/v1/papers.py` <-> `backend/app/services/crawler.py` | 1.000 | Fetch/enrichment changes can alter what the API exposes |
| `backend/app/api/v1/papers.py` <-> `backend/app/services/pipeline.py` | 1.000 | Pipeline output shape and read API shape are coupled |

## Operational Readout

- If you change brief payload fields, candidate rules, or detail-page semantics, expect to touch `papers.py`, `schemas/paper.py`, `domain.py`, and at least one frontend view together.
- If you change narrative generation or candidate promotion/demotion semantics, inspect both `ai_processor.py` and `pipeline.py`, even when the user-facing symptom appears in the API.
- Documentation churn currently exceeds code churn, so requirement drift is a real source of regression; re-read `Detailed_PRD.md` before making rules changes.

## Notable Absences

- No single backend service file is a dominant hotspot yet; backend complexity is more distributed than the frontend and docs cluster.
- The scheduler/deployment layer does not appear in git hotspots because it is not implemented in this repository.
