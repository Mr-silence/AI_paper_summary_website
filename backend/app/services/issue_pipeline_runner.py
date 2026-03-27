from __future__ import annotations

from datetime import date
from typing import Callable, Dict, Optional, Type

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.domain import SystemTaskLog
from app.services.pipeline import Pipeline


def run_issue_pipeline(
    issue_date: date,
    *,
    session_factory: Callable[[], Session] = SessionLocal,
    pipeline_cls: Type[Pipeline] = Pipeline,
) -> Dict[str, Optional[object]]:
    """
    Shared execution entry for both daily update and historical backfill.
    Guarantees both paths call the same crawler + scorer + Editor->Writer->Reviewer pipeline.
    """
    with session_factory() as db:
        pipeline_cls(db).run(issue_date.isoformat())
        task_log = (
            db.query(SystemTaskLog)
            .filter(SystemTaskLog.issue_date == issue_date)
            .first()
        )
        if task_log is None:
            raise RuntimeError("Pipeline finished without creating a system_task_log row.")

        return {
            "issue_date": issue_date.isoformat(),
            "status": task_log.status,
            "fetched_count": int(task_log.fetched_count or 0),
            "processed_count": int(task_log.processed_count or 0),
            "finished_at": task_log.finished_at.isoformat() if task_log.finished_at else None,
        }
