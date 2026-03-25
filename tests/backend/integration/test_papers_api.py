import pytest


pytestmark = pytest.mark.integration


def test_get_papers_excludes_candidates_by_default(api_client, seeded_papers):
    response = api_client.get(
        "/api/v1/papers",
        params={"issue_date": seeded_papers["current_issue_date"].isoformat()},
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total"] == 2
    assert {item["category"] for item in payload["items"]} == {"focus", "watching"}


def test_get_papers_include_candidates_preserves_null_narratives(api_client, seeded_papers):
    response = api_client.get(
        "/api/v1/papers",
        params={
            "issue_date": seeded_papers["current_issue_date"].isoformat(),
            "include_candidates": "true",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["total"] == 4

    candidate = next(item for item in payload["items"] if item["category"] == "candidate")
    assert candidate["candidate_reason"] in {"low_score", "capacity_overflow"}
    assert candidate["one_line_summary"] is None
    assert candidate["one_line_summary_en"] is None


def test_get_paper_detail_returns_latest_summary_and_candidate_null_fields(api_client, seeded_papers):
    response = api_client.get(f"/api/v1/papers/{seeded_papers['paper_ids']['latest_candidate']}")

    assert response.status_code == 200
    paper = response.json()["data"]
    assert paper["category"] == "candidate"
    assert paper["issue_date"] == seeded_papers["current_issue_date"].isoformat()
    assert paper["candidate_reason"] == "capacity_overflow"
    assert paper["core_highlights"] is None
    assert paper["application_scenarios"] is None


def test_get_paper_detail_returns_404_for_missing_paper(api_client):
    response = api_client.get("/api/v1/papers/999999")

    assert response.status_code == 404
    assert response.json()["msg"] == "Paper not found"
