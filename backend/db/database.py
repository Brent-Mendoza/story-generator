from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from models.story import Story, StoryNode
from models.job import StoryJob
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client: AsyncIOMotorClient | None = None


async def init():
    global client
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.get_database()

    await init_beanie(database=db, document_models=[Story, StoryNode, StoryJob])
    print("Connected to MongoDB")


async def close_db():
    global client
    if client:
        client.close()
        print("Closed MongoDB Connection")
