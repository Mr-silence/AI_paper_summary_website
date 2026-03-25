from datetime import datetime, timedelta
from typing import Any, Dict

from app.services.crawler import Crawler


def probe_live_dates(days: int = 14) -> Dict[str, Any]:
    crawler = Crawler()
    today = datetime.now().date()
    result: Dict[str, Any] = {
        "hf_date": None,
        "hf_sample": None,
        "arxiv_date": None,
        "arxiv_sample": None,
        "combined_date": None,
    }

    for offset in range(days):
        date_str = (today - timedelta(days=offset)).isoformat()

        hf_papers = crawler._fetch_hf_papers(date_str)
        if result["hf_date"] is None and hf_papers:
            result["hf_date"] = date_str
            result["hf_sample"] = hf_papers[0]

        arxiv_papers = crawler._fetch_arxiv_papers(date_str)
        if result["arxiv_date"] is None and arxiv_papers:
            result["arxiv_date"] = date_str
            result["arxiv_sample"] = arxiv_papers[0]

        if result["combined_date"] is None and hf_papers and arxiv_papers:
            result["combined_date"] = date_str

        if result["hf_date"] and result["arxiv_date"] and result["combined_date"]:
            break

    return result
