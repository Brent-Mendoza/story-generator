from beanie import Document, Link, Indexed
from typing import Optional
from datetime import datetime, timezone


class StoryJob(Document):
    job_id: str = Indexed(unique=True)
    session_id: str = Indexed()
    theme: str
    status: str
    story_id: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)
    completed_at: Optional[datetime] = None
