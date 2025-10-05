from core.config import settings
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import logging

from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode
from core.models import StoryLLMResponse, StoryNodeLLM

logger = logging.getLogger(__name__)


class StoryGenerator:

    @classmethod
    def _get_llm(cls):
        return GoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=settings.GENAI_KEY)

    @classmethod
    async def generate_story(cls, session_id: str, theme: str = "fantasy") -> Story:
        llm = cls._get_llm()
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)
        prompt = ChatPromptTemplate.from_messages([
            (
                "human",
                STORY_PROMPT
            ),
            (
                "human",
                f"Create a story with this {theme}"
            )
        ]).partial(format_instructions=story_parser.get_format_instructions())

        logger.info("Calling LLM...")
        raw_response = llm.invoke(prompt.invoke({}))
        logger.info(f"LLM response received: {raw_response[:100]}...")

        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content

        logger.info("Parsing response...")
        story_structure = story_parser.parse(response_text)
        logger.info(f"Story structure parsed: {story_structure.title}")

        story_db = Story(title=story_structure.title, session_id=session_id)
        await story_db.save()
        logger.info(f"Story saved with ID: {story_db.id}")

        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        await cls._process_story_node(story_id=story_db.id,
                                      node_data=root_node_data, is_root=True)

        return story_db

    @classmethod
    async def _process_story_node(cls, story_id: str, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
        node = StoryNode(
            story=story_id,
            content=node_data.content if hasattr(
                node_data, "content") else node_data["content"],
            is_root=is_root,
            is_ending=node_data.isEnding if hasattr(
                node_data, "isEnding") else node_data["isEnding"],
            is_winning_ending=node_data.isWinningEnding if hasattr(
                node_data, "isWinningEnding") else node_data["isWinningEnding"],
            options=[]
        )

        if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode

                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)

                child_node = await cls._process_story_node(
                    story_id, next_node, is_root=False)

                options_list.append({
                    "text": option_data.text,
                    "node_id": str(child_node.id)
                })

            node.options = options_list

        await node.save()

        return node
