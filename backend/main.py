from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import init, close_db
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from core.config import settings
from routes import story, job


load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init()
    try:
        yield
    finally:
        await close_db()

app = FastAPI(lifespan=lifespan, title="Choose your own Adventure API",
              description="Api to generate stories", version="0.1.0", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(story.router, prefix=settings.API_PREFIX)
app.include_router(job.router, prefix=settings.API_PREFIX)
