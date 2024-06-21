from langfuse import Langfuse
from langfuse.client import ChatPromptClient
from app.common.config import logger

def get_prompt_str(*args, **kwargs) -> str | None:
    langfuse = Langfuse()
    prompt = None
    try:
        prompt = langfuse.get_prompt(*args, **kwargs).compile()
    except Exception as e:
        logger.error(f"Error in get_prompt from langfuse: {e}")
        return None
    return prompt

def get_prompt_client(*args, **kwargs) -> ChatPromptClient | None:
    langfuse = Langfuse()
    prompt = None
    try:
        prompt = langfuse.get_prompt(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in get_prompt from langfuse: {e}")
        return None
    return prompt