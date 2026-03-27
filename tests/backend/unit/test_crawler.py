from app.services.crawler import Crawler


def test_merge_normalized_paper_preserves_richer_arxiv_metadata():
    crawler = Crawler()
    arxiv_paper = {
        "arxiv_id": "2603.00001",
        "title_zh": None,
        "title_original": "Richer arXiv Metadata",
        "authors": [
            {"name": "Alice", "affiliation": "OpenAI"},
            {"name": "Bob", "affiliation": "Stanford University"},
        ],
        "venue": "ICLR 2026",
        "abstract": "A longer abstract from arXiv with venue context.",
        "pdf_url": "https://arxiv.org/pdf/2603.00001.pdf",
        "upvotes": 0,
        "arxiv_publish_date": "2026-03-20",
        "is_hf_daily": False,
    }
    hf_paper = {
        "arxiv_id": "2603.00001",
        "title_zh": None,
        "title_original": "Richer arXiv Metadata",
        "authors": [{"name": "Alice", "affiliation": ""}],
        "venue": None,
        "abstract": "Short HF abstract.",
        "pdf_url": "https://huggingface.co/papers/2603.00001",
        "upvotes": 128,
        "arxiv_publish_date": "2026-03-20",
        "is_hf_daily": True,
    }

    merged = crawler._merge_normalized_paper(arxiv_paper, hf_paper)

    assert merged["authors"] == arxiv_paper["authors"]
    assert merged["venue"] == "ICLR 2026"
    assert merged["abstract"] == arxiv_paper["abstract"]
    assert merged["pdf_url"] == arxiv_paper["pdf_url"]
    assert merged["upvotes"] == 128
    assert merged["is_hf_daily"] is True


def test_merge_normalized_paper_can_fill_missing_arxiv_fields_from_hf():
    crawler = Crawler()
    arxiv_paper = {
        "arxiv_id": "2603.00002",
        "title_zh": None,
        "title_original": "Sparse arXiv Metadata",
        "authors": [],
        "venue": None,
        "abstract": "",
        "pdf_url": "https://arxiv.org/pdf/2603.00002.pdf",
        "upvotes": 0,
        "arxiv_publish_date": "2026-03-20",
        "is_hf_daily": False,
    }
    hf_paper = {
        "arxiv_id": "2603.00002",
        "title_zh": None,
        "title_original": "Sparse arXiv Metadata",
        "authors": [{"name": "Carol", "affiliation": "Meta"}],
        "venue": "NeurIPS 2026 Workshop",
        "abstract": "HF recovered abstract.",
        "pdf_url": "https://huggingface.co/papers/2603.00002",
        "upvotes": 42,
        "arxiv_publish_date": "2026-03-20",
        "is_hf_daily": True,
    }

    merged = crawler._merge_normalized_paper(arxiv_paper, hf_paper)

    assert merged["authors"] == hf_paper["authors"]
    assert merged["venue"] == hf_paper["venue"]
    assert merged["abstract"] == hf_paper["abstract"]
    assert merged["upvotes"] == 42
    assert merged["is_hf_daily"] is True


def test_fetch_citations_bulk_parallelizes_and_falls_back_to_zero(monkeypatch):
    crawler = Crawler()
    calls = []

    def fake_fetch(arxiv_id):
        calls.append(arxiv_id)
        if arxiv_id == "bad":
            raise RuntimeError("boom")
        return {"a": 3, "b": 9}.get(arxiv_id, 0)

    monkeypatch.setattr(crawler, "_fetch_citation_count", fake_fetch)

    citations = crawler._fetch_citations_bulk(["a", "bad", "b"])

    assert sorted(calls) == ["a", "b", "bad"]
    assert citations == {"a": 3, "bad": 0, "b": 9}
