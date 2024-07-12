import os
import sys
from langchain_core.messages import BaseMessage
from datetime import datetime
from langchain_openai import ChatOpenAI
from typing import List, Dict
from dotenv import load_dotenv, find_dotenv

from app.common.config import logger
from app.messages.base import CBaseMessage
from app.chatbot.agents.actions import contextualize_query, create_redirect_tools, pick_tool, \
                                        choose_appropriate_tools, execute_redirect_tool, check_user_satisfaction, \
                                        load_external_tools, get_external_tools, get_redirect_tools, \
                                        execute_external_tool

from app.chatbot.prompts.orchestration import tool_info
from app.utils.str import extract_and_remove_dict_from_string
from app.chatbot.tools.tools import external_tool_info


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


llm_answer = ChatOpenAI(model=os.environ.get("LLM_ANSWER"), api_key=OPENAI_API_KEY, temperature=0.0)
llm_observation = ChatOpenAI(model=os.environ.get("LLM_OBSERVATION"), api_key=OPENAI_API_KEY, temperature=0.0)
llm_contextualization = ChatOpenAI(model=os.environ.get("LLM_CONTEXTUALIZE"), api_key=OPENAI_API_KEY, temperature=0.0)
llm_select_tool = ChatOpenAI(model=os.environ.get("LLM_SELECT_TOOL"), api_key=OPENAI_API_KEY, temperature=0.0)

class CCache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CCache, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Prevent __init__ from running more than once
            self.initialized = True
            self.cache = {}  # Example cache storage

    def get(self, key):
        return self.cache.get(key, [])

    def set(self, key, value):
        self.cache[key] = self.get(key) + [value]

    def get_cache_from_message(self, message: CBaseMessage) -> List[Dict]:
        """
        This function gets the cache from the message object.

        Args:
            message (CBaseMessage): The message object
        
        Returns:
            List[Dict]: The cache from the message object
        """
        # If the current thread is empty, get the parent thread cache
        if len(self.get(message.thread_id)) == 0:
            parent_msg_cache = self.get(message.parent_thread_id + "_" + message.parent_message_id)
            # If the parent thread cache is not empty, set the current thread cache to the parent thread cache
            if message.thread_id and len(parent_msg_cache) > 0:
                self.set(message.thread_id, parent_msg_cache[-1])
            # Return the parent thread cache (list of dictionaries)
            return parent_msg_cache
        else:
            # Return the current thread cache (list of dictionaries)
            return self.get(message.thread_id)

    def set_cache_from_message(self, message: CBaseMessage, value):
        """
        This function sets the cache from the message object.

        Args:
            message (CBaseMessage): The message object
            value (Dict): The value to set
        
        Returns:
            None
        """
        # If the current thread is empty, set the parent thread cache
        if message.thread_id:
            self.set(message.thread_id, value)
        else:
            self.set(message.parent_thread_id + "_" + message.parent_message_id, value)

system_prompt = """
    Bạn là Opsbot, một trợ lý ảo hỗ trợ tất cả vấn đề nội bộ của công ty thời trang YODY.
    User có thể hỏi bạn về tất cả các vấn đề liên quan đến công việc, hỗ trợ hành chính, hỗ trợ khách hàng, 
    vấn đề kỹ thuật, vấn đề về sản phẩm, vấn đề về dịch vụ, vấn đề về quy trình, vấn đề về chính sách, vận hành cửa hàng, bán hàng online v.v
    Nhiệm vụ của bạn là dựa vào yêu cầu của user và cuộc trò chuyện trước đó để chọn ra một tool phù hợp để giúp user giải quyết vấn đề.
    Bạn có thể hỏi thêm thông tin nếu cần thiết và chuyển user đến tool phù hợp để giải quyết vấn đề.
    """

def generate_answer(user_message: CBaseMessage, 
                    chat_history: List[BaseMessage], 
                    chat_history_wt_image: List[BaseMessage]) -> str:
    """
    This function takes a user message and chat history and returns an answer.

    Args:
        user_message (CBaseMessage): The user message to answer
        chat_history (List[CBaseMessage]): The chat history to use for answering

    Returns:
        str: The answer
    """
    cache = CCache()
    if len(cache.cache) > 200:
        cache.cache = {}
    # Get the list of cache from the user message(every message will have a cache, so a thread can have multiple caches)
    cached_response = cache.get_cache_from_message(user_message)
    lastest_cache = cached_response[-1] if len(cached_response) > 0 else {}
    is_user_satisfied = check_user_satisfaction(user_message.text, chat_history_wt_image, llm_observation)
    last_used_tool_name = lastest_cache.get('selected_tool', {}).get('name', "unclear_issue")

    contextualized_query = None
    # If the user is satisfied with the last response and the last function is not unclear_issue or chitchat, use cache
    if last_used_tool_name not in ('unclear_issue', "chitchat") \
        and is_user_satisfied:
        # get the last selected tool from cache
        tool_names = [last_used_tool_name]
        # If the last tool is query_promotion, alway contextualize the query
        if "query_promotion" in tool_names:
            contextualized_query = contextualize_query(llm_contextualization, user_message.text, chat_history_wt_image)
    else:
        contextualized_query = contextualize_query(llm_contextualization, user_message.text, chat_history_wt_image)
        # Pick a tools for the user using senmantic route
        tool_names = choose_appropriate_tools(contextualized_query)
    
    logger.debug(f"Tool names: {tool_names}")
    logger.debug(f"Contextualized query: {contextualized_query}")
    # split tools into external tools and redirect tools
    external_tools = load_external_tools(tool_names, external_tool_info)
    redirect_tools = create_redirect_tools(tool_names, tool_info)
    # combine external tools and redirect tools and feed to llm to pick the best tool
    appropriate_tools = external_tools + redirect_tools


    # Tools selected by llm
    contextualized_query = contextualized_query if contextualized_query else user_message.text
    picked_tools = pick_tool(llm_select_tool, user_message.text, contextualized_query, 
                            chat_history_wt_image, system_prompt, appropriate_tools)
    logger.debug(f"Picked tools: {picked_tools}")
    picked_external_tools = get_external_tools(picked_tools, external_tool_info)
    picked_redirect_tools = get_redirect_tools(picked_tools, tool_info)

    if len(picked_external_tools) > 0:
        selected_tools = picked_external_tools
    elif len(picked_redirect_tools) > 0:
        selected_tools = [picked_redirect_tools[0]]
    else:
        selected_tools = [{'name': 'unclear_issue', 'args': {'query': user_message.text}}]
    
    # Save the selected tool to cache
    cache.set_cache_from_message(user_message, {'selected_tool': selected_tools[0],
                                "timestamp": datetime.now().isoformat(),
                                'contextualized_query': contextualized_query})

    # Priority to use external tools
    if len(picked_external_tools) > 0:
        answer = execute_external_tool(
            tool=picked_external_tools,
            tool_info=external_tool_info,
            llm_model=llm_answer,
            user_query=user_message.text,
            contextualized_query=contextualized_query,
            chat_history=chat_history
        )
    else:
        # For redirect tools,  only execute the first one
        answer = execute_redirect_tool(tool=selected_tools[0],
                                    tool_info=tool_info,
                                    llm_model=llm_answer,
                                    user_query=user_message.text,
                                    contextualized_query=contextualized_query,
                                    chat_history=chat_history)
    
    answer, mentions = extract_and_remove_dict_from_string(answer)
    return answer, mentions
    
