from types import SimpleNamespace

import pytest

from app.models.domain import PaperSummary
from app.services.pipeline import Pipeline


def test_seed_summary_snapshots_assigns_candidate_reasons(db_session):
    pipeline = Pipeline(db_session)
    issue_date = Pipeline._resolve_issue_date("2026-03-23")
    scored_papers = [
        {
            "arxiv_id": "2503.11001",
            "title_zh": "焦点论文",
            "title_original": "Focus Paper",
            "authors": [{"name": "Alice", "affiliation": "OpenAI"}],
            "venue": "ICLR 2026",
            "abstract": "Focus abstract",
            "pdf_url": "https://arxiv.org/pdf/2503.11001.pdf",
            "upvotes": 120,
            "arxiv_publish_date": "2026-03-20",
            "score": 96,
            "score_reasons": {"hf_recommend": 30},
            "direction": "Agent",
        },
        {
            "arxiv_id": "2503.11002",
            "title_zh": "观察候补",
            "title_original": "Watching Overflow",
            "authors": [{"name": "Bob", "affiliation": "Meta"}],
            "venue": "ACL 2026",
            "abstract": "Watching abstract",
            "pdf_url": "https://arxiv.org/pdf/2503.11002.pdf",
            "upvotes": 60,
            "arxiv_publish_date": "2026-03-20",
            "score": 55,
            "score_reasons": {"community_popularity": 20},
            "direction": "RAG",
        },
        {
            "arxiv_id": "2503.11003",
            "title_zh": "低分候选",
            "title_original": "Low Score Candidate",
            "authors": [{"name": "Carol", "affiliation": "Independent"}],
            "venue": None,
            "abstract": "Candidate abstract",
            "pdf_url": "https://arxiv.org/pdf/2503.11003.pdf",
            "upvotes": 5,
            "arxiv_publish_date": "2026-03-20",
            "score": 35,
            "score_reasons": {"academic_influence": 4},
            "direction": "Benchmarking",
        },
    ]

    paper_map = pipeline._upsert_papers(scored_papers)
    pipeline._seed_summary_snapshots(
        issue_date=issue_date,
        scored_papers=scored_papers,
        paper_map=paper_map,
        focus_selected_ids={"2503.11001"},
        watching_selected_ids=set(),
    )
    db_session.commit()

    summaries = {
        summary.paper.arxiv_id: summary
        for summary in db_session.query(PaperSummary).filter(PaperSummary.issue_date == issue_date).all()
    }

    assert summaries["2503.11001"].category == "focus"
    assert summaries["2503.11001"].candidate_reason is None
    assert summaries["2503.11002"].category == "candidate"
    assert summaries["2503.11002"].candidate_reason == "capacity_overflow"
    assert summaries["2503.11003"].category == "candidate"
    assert summaries["2503.11003"].candidate_reason == "low_score"


def test_process_category_batch_backfills_after_rejection():
    accepted_summary = SimpleNamespace(
        category="focus",
        candidate_reason=None,
        one_line_summary=None,
        one_line_summary_en=None,
        core_highlights=None,
        core_highlights_en=None,
        application_scenarios=None,
        application_scenarios_en=None,
    )
    rejected_summary = SimpleNamespace(
        category="focus",
        candidate_reason=None,
        one_line_summary="old",
        one_line_summary_en="old",
        core_highlights=["old"],
        core_highlights_en=["old"],
        application_scenarios="old",
        application_scenarios_en="old",
    )
    overflow_summary = SimpleNamespace(
        category="candidate",
        candidate_reason="capacity_overflow",
        one_line_summary=None,
        one_line_summary_en=None,
        core_highlights=None,
        core_highlights_en=None,
        application_scenarios=None,
        application_scenarios_en=None,
    )

    initial_batch = [
        {"arxiv_id": "focus-a", "_summary": accepted_summary},
        {"arxiv_id": "focus-b", "_summary": rejected_summary},
    ]
    overflow_batch = [{"arxiv_id": "focus-c", "_summary": overflow_summary}]

    pipeline = Pipeline.__new__(Pipeline)
    calls = []

    def fake_run_ai_batch(papers, category):
        calls.append([paper["arxiv_id"] for paper in papers])
        if len(calls) == 1:
            return (
                [
                    {
                        "arxiv_id": "focus-a",
                        "one_line_summary": "中文 A",
                        "one_line_summary_en": "English A",
                        "core_highlights": ["A1", "A2", "A3"],
                        "core_highlights_en": ["A1", "A2", "A3"],
                        "application_scenarios": "场景 A",
                        "application_scenarios_en": "Scenario A",
                    }
                ],
                ["focus-b"],
            )
        return (
            [
                {
                    "arxiv_id": "focus-c",
                    "one_line_summary": "中文 C",
                    "one_line_summary_en": "English C",
                    "core_highlights": ["C1", "C2", "C3"],
                    "core_highlights_en": ["C1", "C2", "C3"],
                    "application_scenarios": "场景 C",
                    "application_scenarios_en": "Scenario C",
                }
            ],
            [],
        )

    pipeline._run_ai_batch = fake_run_ai_batch

    processed_count = pipeline._process_category_batch(
        initial_batch=initial_batch,
        overflow_batch=overflow_batch,
        category="focus",
        minimum=2,
    )

    assert processed_count == 2
    assert calls == [["focus-a", "focus-b"], ["focus-c"]]
    assert accepted_summary.category == "focus"
    assert accepted_summary.one_line_summary == "中文 A"
    assert rejected_summary.category == "candidate"
    assert rejected_summary.candidate_reason == "reviewer_rejected"
    assert rejected_summary.one_line_summary is None
    assert overflow_summary.category == "focus"
    assert overflow_summary.candidate_reason is None
    assert overflow_summary.one_line_summary == "中文 C"


def test_process_category_batch_raises_when_baseline_cannot_be_met():
    accepted_summary = SimpleNamespace(
        category="watching",
        candidate_reason=None,
        one_line_summary=None,
        one_line_summary_en=None,
        core_highlights=None,
        core_highlights_en=None,
        application_scenarios=None,
        application_scenarios_en=None,
    )

    pipeline = Pipeline.__new__(Pipeline)
    pipeline._run_ai_batch = lambda papers, category: (
        [
            {
                "arxiv_id": "watch-1",
                "one_line_summary": "中文",
                "one_line_summary_en": "English",
                "core_highlights": ["P1"],
                "core_highlights_en": ["P1"],
                "application_scenarios": "场景",
                "application_scenarios_en": "Scenario",
            }
        ],
        [],
    )

    with pytest.raises(ValueError, match="no eligible backfill candidates remained"):
        pipeline._process_category_batch(
            initial_batch=[{"arxiv_id": "watch-1", "_summary": accepted_summary}],
            overflow_batch=[],
            category="watching",
            minimum=2,
        )


def test_run_fails_before_title_localization_when_supply_is_insufficient(db_session):
    pipeline = Pipeline(db_session)
    pipeline.crawler.fetch_papers = lambda fetch_date: [
        {"arxiv_id": "paper-focus"},
        {"arxiv_id": "paper-watch"},
    ]
    pipeline.scorer.score_paper = lambda paper: {
        "arxiv_id": paper["arxiv_id"],
        "title_original": paper["arxiv_id"],
        "authors": [],
        "venue": None,
        "abstract": "",
        "pdf_url": "https://arxiv.org/pdf/example.pdf",
        "upvotes": 0,
        "arxiv_publish_date": "2026-03-20",
        "score": 90 if paper["arxiv_id"] == "paper-focus" else 60,
        "score_reasons": {},
        "direction": "Agent",
    }

    def fail_if_called(_papers):
        raise AssertionError("title localization should not run before the focus/watching supply audit")

    pipeline.ai_processor.localize_titles = fail_if_called

    with pytest.raises(ValueError, match="Supply insufficient"):
        pipeline.run("2026-03-23")
