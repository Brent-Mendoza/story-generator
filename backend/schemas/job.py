from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class StoryJobBase(BaseModel):
    theme: str


class StoryJobResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    story_id: Optional[str] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class StoryJobCreate(StoryJobBase):
    pass
