from datetime import date

from app.models.domain import SystemTaskLog
from app.services.issue_pipeline_runner import run_issue_pipeline


def test_run_issue_pipeline_uses_shared_pipeline_entry(session_factory):
    executed = []

    class RecordingPipeline:
        def __init__(self, db):
            self.db = db

        def run(self, issue_date: str):
            executed.append(issue_date)
            self.db.add(
                SystemTaskLog(
                    issue_date=date.fromisoformat(issue_date),
                    status="SUCCESS",
                    fetched_count=11,
                    processed_count=5,
                )
            )
            self.db.commit()

    result = run_issue_pipeline(
        date(2026, 3, 27),
        session_factory=session_factory,
        pipeline_cls=RecordingPipeline,
    )

    assert executed == ["2026-03-27"]
    assert result["status"] == "SUCCESS"
    assert result["fetched_count"] == 11
    assert result["processed_count"] == 5
