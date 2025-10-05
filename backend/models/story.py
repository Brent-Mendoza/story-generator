from __future__ import annotations
from beanie import Document, Indexed, Link, before_event, Insert
from datetime import datetime, timezone
from typing import Optional


class Story(Document):
    title: str = Indexed()
    session_id: str = Indexed()
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: Optional[datetime] = None

    @before_event(Insert)
    def set_created_at(self):
        self.created_at = datetime.now(timezone.utc)


class StoryNode(Document):
    content: str
    is_root: bool = False
    is_ending: bool = False
    is_winning: bool = False
    is_winning_ending: bool = False
    options: list = []
    story: Link[Story]
