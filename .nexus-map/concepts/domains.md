> generated_by: nexus-mapper v2
> verified_at: 2026-03-25
> provenance: Domain terms are grounded in `Detailed_PRD.md` and verified against the current pipeline, API, schema, and frontend code.

# Domains

## T+3 Issue Window

- `issue_date` is the brief publication date.
- `fetch_date` is `issue_date - 3 days`.
- The batch pipeline resolves `issue_date`, then asks the crawler to fetch papers from three days earlier.
- Why it matters: anything that changes date handling touches both pipeline orchestration and historical query semantics.

## Score Tiers

- `focus`: score `>= 80`
- `watching`: `50 <= score < 80`
- `candidate`: everything else, plus overflow papers pushed out by capacity limits, plus reviewer rejections
- The system enforces both capacity (`5/12`) and minimum baseline (`3/8`), which makes “category” a workflow state rather than a pure score bucket.

## Candidate Lifecycle

- Candidate is not a dead end; it is a reversible holding state.
- `capacity_overflow` can be promoted back into focus/watching when reviewer rejection causes backfill.
- `reviewer_rejected` is sticky within the same run and enters a blacklist for that issue.
- Narrative fields must be `NULL` whenever a record is in candidate state.

## Bilingual Narrative Contract

- Non-candidate briefs must provide paired CN/EN fields for summary, highlights, and application scenarios.
- Focus briefs require `3-5` highlight bullets; Watching requires `1-2`.
- Candidate detail pages intentionally show metadata without narrative sections.
- This contract is enforced partly in `AIProcessor` parsing and partly in frontend rendering rules.

## Direction / Topic Taxonomy

- Every paper receives exactly one direction from the fixed taxonomy in `backend/app/core/specs.py`.
- The frontend exposes this taxonomy through Topic pages and direction tags.
- Because the taxonomy is ordered, earlier matches win; changing keyword order changes user-visible classification behavior.

## Subscription Token Flow

- Subscribe produces `verify_token` and `unsub_token` with 24-hour expiry.
- Verify clears the verify token and activates the subscriber.
- Unsubscribe resolves by token, not by email, and is rate-limited by client IP.
- The frontend shell owns the subscribe dialog, while the unsubscribe page resolves the token result state.

## Brief Transparency

- Home shows only focus/watching by default.
- Sources explicitly reveals the candidate pool, score reasons, and candidate reason.
- Detail pages preserve the distinction between curated briefs and unpromoted candidates.
- This makes “what was selected” and “what was merely seen” first-class product concepts, not hidden backend data.
