import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Cookie
from models.job import StoryJob
from schemas.job import StoryJobResponse

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)


@router.get(path="/{job_id}", response_model=StoryJobResponse)
async def get_job_status(job_id: str):
    job = await StoryJob.find_one(StoryJob.job_id == job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job
