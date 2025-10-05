import uuid
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import (
    CompleteStoryResponse, CompleteStoryNodeResponse, CreateStoryRequest)
from schemas.job import StoryJobResponse
from core.story_generate import StoryGenerator

router = APIRouter(
    prefix="/stories",
    tags=["stories"]
)


def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@router.post(path="/create", response_model=StoryJobResponse)
async def create_story(
    request: CreateStoryRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    session_id: str = Depends(get_session_id)
):
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    job_id = str(uuid.uuid4())

    job = StoryJob(
        job_id=job_id,
        session_id=session_id,
        theme=request.theme,
        status="pending"
    )
    await job.insert()

    background_tasks.add_task(
        generate_story_task,
        job_id=job_id,
        theme=request.theme,
        session_id=session_id
    )

    return job


async def generate_story_task(job_id: str, theme: str, session_id: str):
    try:
        job = await StoryJob.find_one(StoryJob.job_id == job_id)

        if not job:
            return

        job.status = "processing"
        await job.save()

        story = await StoryGenerator.generate_story(session_id, theme)

        job.status = "completed"
        job.story_id = str(story.id)
        job.completed_at = datetime.now()
        await job.save()

    except Exception as e:
        job.status = "failed"
        job.completed_at = datetime.now()
        job.error = str(e)


@router.get(path="/{story_id}/complete", response_model=CompleteStoryResponse)
async def get_complete_story(story_id: str):
    story = await Story.find_one(Story.id == PydanticObjectId(story_id))
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    complete_story = await build_complete_story_tree(story=story)
    return complete_story


async def build_complete_story_tree(story: Story) -> CompleteStoryResponse:
    nodes = await StoryNode.find(StoryNode.story.id == story.id).to_list()

    node_dict = {}
    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            id=str(node.id),
            content=node.content,
            is_ending=node.is_ending,
            is_winning_ending=node.is_winning_ending,
            options=node.options
        )
        node_dict[str(node.id)] = node_response

    root_node = next((node for node in nodes if node.is_root), None)
    if not root_node:
        raise HTTPException(status_code=500, detail="Root node not found")

    return CompleteStoryResponse(
        id=str(story.id),
        title=story.title,
        session_id=story.session_id,
        created_at=story.created_at,
        root_node=node_dict[str(root_node.id)],
        all_nodes=node_dict
    )
